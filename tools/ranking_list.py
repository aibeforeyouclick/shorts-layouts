"""Add a tier board (S to F) to one phase of a short. Cards drop into their row on the spoken word.

Reads <video>/script.json "ranking": {"phase", "title", "items": [{"name", "tier", "anchor", "n"}]}.
Needs transcript.json and data.js (tools/tts.py, tools/build_data.py).
Writes vendor/ranking-list.js and ranking-list.data.js, and adds their <script> tags to index.html.
The section #<phase> must exist in index.html; its own content is hidden while the board shows.

Usage: python -I tools/ranking_list.py videos/<slug>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I leaves the script dir off sys.path
from layoutlib import check_anchor, check_phase, fail, install, load, norm

TIERS = ("S", "A", "B", "C", "D", "F")
MAX_ITEMS, MAX_NAME = 8, 3


def main(video_dir: Path) -> int:
    script, html, words = load(video_dir)
    r = script.get("ranking")
    if not isinstance(r, dict):
        return fail(["no 'ranking' block in script.json"])
    phase, items = r.get("phase"), r.get("items") or []
    errors = check_phase(phase, html)
    if not r.get("title"):
        errors.append("ranking needs a 'title'")
    if not 1 <= len(items) <= MAX_ITEMS:
        errors.append(f"ranking needs 1 to {MAX_ITEMS} items")
    for i, it in enumerate(items, 1):
        if it.get("tier") not in TIERS:
            errors.append(f"item {i}: tier {it.get('tier')!r} not in {TIERS}")
        if not it.get("name") or len(it["name"].split()) > MAX_NAME:
            errors.append(f"item {i}: 'name' needs 1 to {MAX_NAME} words")
        errors += check_anchor(f"item {i}", it.get("anchor"), it.get("n", 1), phase, words)
    if errors:
        return fail(errors)

    data = {**r, "items": [{**it, "anchor": norm(it["anchor"]), "n": int(it.get("n", 1))} for it in items]}
    err = install(video_dir, "ranking-list", "RANKING", data, "ranking_list.py")
    if err:
        return fail([err])
    print(json.dumps({"phase": phase, "items": len(items)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
