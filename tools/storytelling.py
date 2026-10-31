"""Three images, a title and a small subtitle in one phase. Each image pops in on its spoken word.

Reads <video>/script.json "story": {"phase", "title", "sub", "sub_anchor"?, "sub_n"?,
  "images": [{"src", "label"?, "anchor", "n"}] x3}. Image paths are relative to the video folder.
Needs transcript.json and data.js. Writes vendor/storytelling.js and storytelling.data.js,
and adds their <script> tags to index.html.

Usage: python -I tools/storytelling.py videos/<slug>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I leaves the script dir off sys.path
from layoutlib import check_anchor, check_file, check_phase, fail, install, load, norm

MAX_TITLE, MAX_SUB, MAX_LABEL = 7, 10, 3


def main(video_dir: Path) -> int:
    script, html, words = load(video_dir)
    s = script.get("story")
    if not isinstance(s, dict):
        return fail(["no 'story' block in script.json"])
    phase, images = s.get("phase"), s.get("images") or []
    errors = check_phase(phase, html)
    if not s.get("title") or len(s["title"].split()) > MAX_TITLE:
        errors.append(f"'title' needs 1 to {MAX_TITLE} words")
    if not s.get("sub") or len(s["sub"].split()) > MAX_SUB:
        errors.append(f"'sub' needs 1 to {MAX_SUB} words")
    if s.get("sub_anchor"):
        errors += check_anchor("sub", s["sub_anchor"], s.get("sub_n", 1), phase, words)
    if len(images) != 3:
        errors.append("'images' needs exactly 3 entries")
    for i, im in enumerate(images, 1):
        errors += check_file(f"image {i}", im.get("src"), video_dir)
        if len((im.get("label") or "").split()) > MAX_LABEL:
            errors.append(f"image {i}: label over {MAX_LABEL} words")
        errors += check_anchor(f"image {i}", im.get("anchor"), im.get("n", 1), phase, words)
    if errors:
        return fail(errors)

    data = {**s, "sub_anchor": norm(s.get("sub_anchor") or ""), "sub_n": int(s.get("sub_n", 1)),
            "images": [{**im, "anchor": norm(im["anchor"]), "n": int(im.get("n", 1))} for im in images]}
    err = install(video_dir, "storytelling", "STORY", data, "storytelling.py")
    if err:
        return fail([err])
    print(json.dumps({"phase": phase, "images": [im["src"] for im in images]}))
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
