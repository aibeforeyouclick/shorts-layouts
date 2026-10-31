"""Split screen: visuals on top, the host image below, captions on the seam, over one or more consecutive phases.

Reads <video>/script.json "split": {"phases": ["p1", ...], "host": "assets/host.png",
  "top": [{"src"}, {"src", "anchor", "n", "phase"}, ...]}. The first top visual shows at the start;
each next one swaps in on its spoken word (counted inside its own phase). Paths are relative to the video folder.
Needs transcript.json and data.js. Writes vendor/split-screen.js and split-screen.data.js,
and adds their <script> tags to index.html.

Usage: python -I tools/split_screen.py videos/<slug>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I leaves the script dir off sys.path
from layoutlib import check_anchor, check_file, check_phase, fail, install, load, norm

MAX_TOP = 6


def main(video_dir: Path) -> int:
    script, html, words = load(video_dir)
    s = script.get("split")
    if not isinstance(s, dict):
        return fail(["no 'split' block in script.json"])
    phases, top = s.get("phases") or [], s.get("top") or []
    order = [p["id"] for p in script.get("phases", [])]
    errors = []
    for p in phases:
        errors += check_phase(p, html)
    idx = [order.index(p) for p in phases if p in order]
    if not phases or len(idx) != len(phases) or idx != list(range(idx[0], idx[0] + len(idx))):
        errors.append(f"'phases' must be consecutive phase ids from script.json, got {phases}")
    errors += check_file("host", s.get("host"), video_dir)
    if not 1 <= len(top) <= MAX_TOP:
        errors.append(f"'top' needs 1 to {MAX_TOP} visuals")
    for i, t in enumerate(top, 1):
        errors += check_file(f"top {i}", t.get("src"), video_dir)
        if i > 1:
            if t.get("phase") not in phases:
                errors.append(f"top {i}: 'phase' must be one of {phases}")
            else:
                errors += check_anchor(f"top {i}", t.get("anchor"), t.get("n", 1), t["phase"], words)
    if errors:
        return fail(errors)

    data = {**s, "top": [t if i == 0 else {**t, "anchor": norm(t["anchor"]), "n": int(t.get("n", 1))}
                         for i, t in enumerate(top)]}
    err = install(video_dir, "split-screen", "SPLIT", data, "split_screen.py")
    if err:
        return fail([err])
    print(json.dumps({"phases": phases, "top": len(top)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
