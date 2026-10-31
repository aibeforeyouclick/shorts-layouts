"""Check a video's script.json against the channel rules before TTS (and after, if timings exist).

Rules (README, 'Channel rules'):
  - a non-empty "sources" block (every claim needs a source)
  - a "privacy" line that is actually spoken in one of the phases
  - numbers spelled out in spoken lines (TTS reads digits badly)
  - after TTS: speaking rate per phase <= 3.0 words/s (warn above 2.5)
  - index.html shows the AI label

Usage: python -I tools/check_script.py videos/<slug>
Exit code 1 if any ERROR.
"""
import json
import re
import sys
from pathlib import Path


def main(video_dir: Path) -> int:
    errors, warnings = [], []
    script = json.loads((video_dir / "script.json").read_text(encoding="utf-8-sig"))
    lines = [(p["id"], line) for p in script.get("phases", []) for line in p.get("lines", [])]

    if not script.get("sources"):
        errors.append("no 'sources' block: every claim needs a source")

    privacy = (script.get("privacy") or "").strip()
    if not privacy:
        errors.append("no 'privacy' line (say what the tool does with your data)")
    elif not any(privacy in line for _, line in lines):
        errors.append(f"privacy line is not spoken in any phase: {privacy!r}")

    for pid, line in lines:
        if re.search(r"\d", line):
            warnings.append(f"{pid}: digits in spoken line, spell them out: {line!r}")

    timings = video_dir / "timings.json"
    transcript = video_dir / "transcript.json"
    if timings.exists() and transcript.exists():
        phases = json.loads(timings.read_text(encoding="utf-8-sig"))["phases"]
        words = json.loads(transcript.read_text(encoding="utf-8-sig"))
        for ph in phases:
            n = sum(1 for w in words if w["phase"] == ph["id"])
            dur = ph["end"] - ph["start"]
            rate = n / dur if dur else 0
            if rate > 3.0:
                errors.append(f"{ph['id']}: {rate:.2f} words/s is too fast")
            elif rate > 2.5:
                warnings.append(f"{ph['id']}: {rate:.2f} words/s is fast")

    index = video_dir / "index.html"
    if index.exists() and "AI-GENERATED" not in index.read_text(encoding="utf-8-sig").upper():
        errors.append("index.html has no AI-GENERATED label")

    for e in errors:
        print("ERROR  ", e)
    for w in warnings:
        print("WARN   ", w)
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
