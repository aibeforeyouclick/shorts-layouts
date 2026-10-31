"""Kokoro narration for a shorts-lab video.

Reads <video>/script.json:
  {"voice": "am_michael", "speed": 1.1, "gap": 0.35,
   "phases": [{"id": "p1", "lines": ["...", "..."]}, ...]}

Writes:
  <video>/audio/narration.wav   24 kHz mono
  <video>/transcript.json       [{"word", "start", "end", "phase"}]
  <video>/timings.json          {"phases": [{"id", "start", "end"}], "duration"}

Usage: python -I tools/tts.py videos/<slug>
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

SR = 24000


def main(video_dir: Path) -> None:
    script = json.loads((video_dir / "script.json").read_text(encoding="utf-8-sig"))
    voice = script.get("voice", "am_michael")
    speed = float(script.get("speed", 1.1))
    gap = float(script.get("gap", 0.35))
    lead_in = float(script.get("lead_in", 0.3))

    pipe = KPipeline(lang_code=voice[0], repo_id="hexgrad/Kokoro-82M")
    pieces = [np.zeros(int(lead_in * SR), dtype=np.float32)]
    t = lead_in
    words, phases = [], []

    for phase in script["phases"]:
        p_start = t
        for line in phase["lines"]:
            for result in pipe(line, voice=voice, speed=speed):
                audio = result.audio.numpy() if hasattr(result.audio, "numpy") else np.asarray(result.audio)
                for tok in result.tokens:
                    if tok.start_ts is None or not tok.text.strip() or not any(c.isalnum() for c in tok.text):
                        continue
                    words.append({"word": tok.text, "start": round(t + tok.start_ts, 3),
                                  "end": round(t + tok.end_ts, 3), "phase": phase["id"]})
                pieces.append(audio.astype(np.float32))
                t += len(audio) / SR
            pieces.append(np.zeros(int(gap * SR), dtype=np.float32))
            t += gap
        phases.append({"id": phase["id"], "start": round(p_start, 3), "end": round(t, 3)})

    tail = float(script.get("tail", 1.6))  # held final frame doubles as thumbnail
    pieces.append(np.zeros(int(tail * SR), dtype=np.float32))
    t += tail

    (video_dir / "audio").mkdir(exist_ok=True)
    sf.write(video_dir / "audio" / "narration.wav", np.concatenate(pieces), SR)
    (video_dir / "transcript.json").write_text(json.dumps(words, indent=1), encoding="utf-8")
    (video_dir / "timings.json").write_text(
        json.dumps({"phases": phases, "duration": round(t, 3)}, indent=1), encoding="utf-8")
    print(json.dumps({"duration": round(t, 2), "phases": phases, "words": len(words)}))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
