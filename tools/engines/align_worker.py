"""Word timings for a line we already know the text of. Runs in a venv with openai-whisper (set SHORTS_WHISPER_PY).

Reads a job file: {"items": [{"wav", "words": [script words], "out"}]} and writes "out" as
[[word, start, end], ...] for exactly the script words, in order, in seconds from the start of the wav.
Whisper (small.en, CPU) only supplies the times: its words are matched to the script words, and a script word
it missed or misheard gets a time between its matched neighbours, shared by length.

Usage: <whisper python> -I tools/engines/align_worker.py <job.json>
"""
import difflib
import json
import re
import sys
from pathlib import Path

import whisper


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def align(script, heard, total):
    a, b = [norm(w) for w in script], [norm(w) for w, _, _ in heard]
    times = [None] * len(script)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            times[blk.a + k] = heard[blk.b + k][1:]
    # Fill gaps between matched words (or the line edges) in proportion to word length.
    i = 0
    while i < len(times):
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < len(times) and times[j] is None:
            j += 1
        lo = times[i - 1][1] if i > 0 else (heard[0][1] if heard else 0.0)
        hi = times[j][0] if j < len(times) else (heard[-1][2] if heard else total)
        hi = max(hi, lo + 0.08 * (j - i))
        weights = [max(1, len(script[k])) for k in range(i, j)]
        t = lo
        for k, wgt in zip(range(i, j), weights):
            d = (hi - lo) * wgt / sum(weights)
            times[k] = (t, t + d)
            t += d
        i = j
    return [[w, round(s, 3), round(e, 3)] for w, (s, e) in zip(script, times)]


job = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
model = whisper.load_model("small.en", device="cpu")
for item in job["items"]:
    audio = whisper.load_audio(item["wav"])
    res = model.transcribe(audio, language="en", word_timestamps=True, fp16=False,
                           initial_prompt=" ".join(item["words"]), condition_on_previous_text=False)
    heard = [(w["word"].strip(), w["start"], w["end"]) for s in res["segments"] for w in s.get("words", [])]
    out = align(item["words"], heard, len(audio) / whisper.audio.SAMPLE_RATE)
    Path(item["out"]).write_text(json.dumps(out), encoding="utf-8")
    matched = sum(1 for w in item["words"] if norm(w) in {norm(h[0]) for h in heard})
    print("aligned", Path(item["out"]).name, f"{matched}/{len(item['words'])} words heard", flush=True)
