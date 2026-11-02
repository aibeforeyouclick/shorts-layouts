"""Narration for a short (Kokoro by default, or Chatterbox-Turbo).

Reads <video>/script.json:
  {"voice": "am_michael", "speed": 1.1, "gap": 0.35,
   "phases": [{"id": "p1", "lines": ["...", "..."]}, ...]}
Dialogue: add "cast": {"lens": {"voice": "am_michael", "speed": 1.1}, "clicky": {...}} and write a line as
  {"who": "clicky", "text": "...", "gap": 0.15}. "gap" (optional) is the pause after that line; a negative gap
  starts the next line before this one ends (an interruption, down to -0.4 s). Dialogue lines are trimmed of
  the engine's own lead and tail silence so turns can be timed to the millisecond.
Engine: "engine": "chatterbox" uses Chatterbox-Turbo (more natural, takes cues like [laugh] [sigh] [chuckle]).
  Each cast member then needs "ref": a reference clip of a voice you have the rights to (default voices/<who>.wav,
  e.g. a few seconds of Kokoro output). A line may set "seed" to get a different take. Lines are cached in audio/lines/ by text + voice + seed,
  so changing only gaps re-times the dialogue without generating again. Word times come from whisper
  (tools/engines/align_worker.py), matched to the script words.

Writes:
  <video>/audio/narration.wav   24 kHz mono
  <video>/transcript.json       [{"word", "start", "end", "phase", "who"}]
  <video>/timings.json          {"phases": [{"id", "start", "end"}], "lines": [{"who", "start", "end"}], "duration"}
  <video>/envelope.json         {"fps": 30, "<who>": [loudness 0..1 per frame]}, one track per speaker

Usage: python -I tools/tts.py videos/<slug>
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I leaves the script dir off sys.path
from script_text import caption_words, for_chatterbox, for_kokoro

SR = 24000
FPS = 30
SILENCE = 0.01  # amplitude under this counts as silence when trimming dialogue lines
LAB = Path(__file__).resolve().parent.parent
# Chatterbox and whisper each run in their own venv: set these to that venv's python (see README, "Dialogue").
CHATTERBOX_PY = os.environ.get("SHORTS_CHATTERBOX_PY", "")
WHISPER_PY = os.environ.get("SHORTS_WHISPER_PY", "")


def trim(audio, head, tail):
    """Cut the lead (head) and/or tail silence; returns (audio, seconds cut from the start)."""
    loud = np.flatnonzero(np.abs(audio) > SILENCE)
    if not len(loud):
        return audio, 0.0
    a = max(0, loud[0] - int(0.02 * SR)) if head else 0
    b = min(len(audio), loud[-1] + int(0.04 * SR)) if tail else len(audio)
    return audio[a:b], a / SR


def envelope(track, total):
    """Loudness per video frame (RMS, scaled so the loud end of speech is ~1)."""
    hop = SR // FPS
    track = np.pad(track, (0, max(0, total - len(track))))
    rms = np.array([np.sqrt(np.mean(track[i:i + hop] ** 2)) for i in range(0, total, hop)])
    top = np.percentile(rms[rms > 0], 95) if (rms > 0).any() else 1.0
    return [round(float(v), 3) for v in np.clip(rms / top, 0, 1)]


def kokoro_lines(items, cast):
    """Each item -> (audio, [[word, start, end], ...]) with times from the start of the line."""
    from kokoro import KPipeline
    pipes, out = {}, []
    for it in items:
        voice, speed = cast[it["who"]]["voice"], float(cast[it["who"]]["speed"])
        pipe = pipes.setdefault(voice[0], KPipeline(lang_code=voice[0], repo_id="hexgrad/Kokoro-82M"))
        parts, words, t = [], [], 0.0
        for result in pipe(for_kokoro(it["text"]), voice=voice, speed=speed):
            audio = result.audio.numpy() if hasattr(result.audio, "numpy") else np.asarray(result.audio)
            for tok in result.tokens:
                if tok.start_ts is None or not tok.text.strip() or not any(c.isalnum() for c in tok.text):
                    continue
                words.append([tok.text, round(t + tok.start_ts, 3), round(t + tok.end_ts, 3)])
            parts.append(audio.astype(np.float32))
            t += len(audio) / SR
        out.append((np.concatenate(parts), words))
    return out


def chatterbox_lines(items, cast, video_dir):
    cache = video_dir / "audio" / "lines"
    cache.mkdir(parents=True, exist_ok=True)
    jobs = []
    for i, it in enumerate(items):
        ref = LAB / cast[it["who"]].get("ref", f"voices/{it['who']}.wav")
        if not ref.is_file():
            raise SystemExit(f"no reference clip for {it['who']!r}: {ref}")
        text, seed = for_chatterbox(it["text"]), int(it.get("seed", 1000 + i))
        key = hashlib.sha1(json.dumps(["chatterbox-turbo", text, hashlib.sha1(ref.read_bytes()).hexdigest(), seed]).encode()).hexdigest()[:16]
        jobs.append({"text": text, "ref": str(ref), "seed": seed, "out": str(cache / f"{key}.wav"),
                     "words": caption_words(it["text"]), "align": str(cache / f"{key}.words.json")})
    run_worker(CHATTERBOX_PY, "chatterbox_worker.py", [j for j in jobs if not Path(j["out"]).exists()], video_dir)
    run_worker(WHISPER_PY, "align_worker.py", [{"wav": j["out"], "words": j["words"], "out": j["align"]}
                                               for j in jobs if not Path(j["align"]).exists()], video_dir)
    return [(sf.read(j["out"], dtype="float32")[0], json.loads(Path(j["align"]).read_text(encoding="utf-8"))) for j in jobs]


def run_worker(python, script, items, video_dir):
    if not items:
        return
    if not python:
        raise SystemExit(f"set SHORTS_CHATTERBOX_PY and SHORTS_WHISPER_PY to the python of their venvs (README, 'Dialogue'), needed for {script}")
    job = video_dir / "audio" / f".{script}.job.json"
    job.write_text(json.dumps({"items": items}), encoding="utf-8")
    env = {**os.environ, "HF_HUB_OFFLINE": "1"}  # models are already downloaded; no network
    subprocess.run([python, "-I", str(LAB / "tools" / "engines" / script), str(job)], check=True, env=env)
    job.unlink()


def main(video_dir: Path) -> None:
    script = json.loads((video_dir / "script.json").read_text(encoding="utf-8-sig"))
    narrator = {"voice": script.get("voice", "am_michael"), "speed": float(script.get("speed", 1.1)), "ref": "voices/narrator.wav"}
    cast = {"narrator": narrator, **{k: {"speed": narrator["speed"], **v} for k, v in script.get("cast", {}).items()}}
    gap = float(script.get("gap", 0.35))
    lead_in = float(script.get("lead_in", 0.3))
    engine = script.get("engine", "kokoro")

    items = []
    for phase in script["phases"]:
        for line in phase["lines"]:
            spec = line if isinstance(line, dict) else {"text": line}
            if spec.get("who", "narrator") not in cast:
                raise SystemExit(f"line by {spec['who']!r} but no such name in 'cast'")
            items.append({**spec, "who": spec.get("who", "narrator"), "phase": phase["id"], "dialogue": isinstance(line, dict)})
    if engine == "kokoro":
        made = kokoro_lines(items, cast)
    elif engine == "chatterbox":
        made = chatterbox_lines(items, cast, video_dir)
    else:
        raise SystemExit(f"unknown engine {engine!r}, use kokoro or chatterbox")

    clips, words, phases, spans = [], [], [], []
    t = lead_in
    for it, (audio, line_words) in zip(items, made):
        if not phases or phases[-1]["id"] != it["phase"]:
            if phases:
                phases[-1]["end"] = round(t, 3)
            phases.append({"id": it["phase"], "start": round(t, 3)})
        audio, cut = trim(audio, True, True) if it["dialogue"] else (audio, 0.0)
        for w, s, e in line_words:
            words.append({"word": w, "start": round(t + max(0.0, s - cut), 3), "end": round(t + max(0.0, e - cut), 3),
                          "phase": it["phase"], "who": it["who"]})
        clips.append((it["who"], int(round(t * SR)), audio))
        spans.append({"who": it["who"], "start": round(t, 3), "end": round(t + len(audio) / SR, 3)})
        t = max(t, t + len(audio) / SR + max(-0.4, float(it.get("gap", gap))))
    phases[-1]["end"] = round(t, 3)

    tail = float(script.get("tail", 1.6))  # held final frame doubles as thumbnail
    t += tail
    total = int(round(t * SR))
    tracks = {}
    for who, at, audio in clips:
        tr = tracks.setdefault(who, np.zeros(total, dtype=np.float32))
        tr[at:at + len(audio)] += audio[:max(0, total - at)]
    mix = np.clip(sum(tracks.values()), -1.0, 1.0)

    (video_dir / "audio").mkdir(exist_ok=True)
    sf.write(video_dir / "audio" / "narration.wav", mix, SR)
    (video_dir / "transcript.json").write_text(json.dumps(words, indent=1), encoding="utf-8")
    (video_dir / "timings.json").write_text(
        json.dumps({"phases": phases, "lines": spans, "duration": round(t, 3)}, indent=1), encoding="utf-8")
    env = {"fps": FPS, **{who: envelope(tr, total) for who, tr in tracks.items()}}
    (video_dir / "envelope.json").write_text(json.dumps(env, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"engine": engine, "duration": round(t, 2), "phases": phases, "words": len(words)}))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
