"""Copy timings.json into index.html after a TTS run: root and audio data-duration, and each phase section's
data-start/data-duration (the first section starts at 0, the last one runs to the end of the video).

Usage: python -I tools/sync_index.py videos/<slug>
"""
import json
import re
import sys
from pathlib import Path


def main(video_dir: Path) -> int:
    tm = json.loads((video_dir / "timings.json").read_text(encoding="utf-8-sig"))
    index = video_dir / "index.html"
    html = index.read_text(encoding="utf-8")
    d = tm["duration"]
    html, n_root = re.subn(r'(id="root"[^>]*data-duration=")[^"]*"', rf'\g<1>{d}"', html)
    html, n_vo = re.subn(r'(<audio id="vo"[^>]*data-duration=")[^"]*"', rf'\g<1>{d}"', html)
    missing = [] if n_root and n_vo else ["root or audio#vo"]
    phases = tm["phases"]
    for i, p in enumerate(phases):
        s = 0 if i == 0 else p["start"]
        e = d if i == len(phases) - 1 else p["end"]
        html, n = re.subn(rf'(<section id="{p["id"]}"[^>]*data-start=")[^"]*(" data-duration=")[^"]*"',
                          rf'\g<1>{round(s, 3)}\g<2>{round(e - s, 3)}"', html)
        if not n:
            missing.append(p["id"])
    if missing:
        print("ERROR   index.html has no data-start/data-duration for:", ", ".join(missing))
        return 1
    index.write_text(html, encoding="utf-8")
    print(json.dumps({"duration": d, "phases": [p["id"] for p in phases]}))
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
