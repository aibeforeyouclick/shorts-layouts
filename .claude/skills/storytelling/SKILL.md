---
name: storytelling
description: Fill one phase of a short with three images, a title and a small subtitle; each image pops in on the spoken word that names it. Use when the user asks for a 3-image story, "three things" beat, or a storytelling layout.
---
# /storytelling

Spec: `docs/SPEC.md`. Example: `examples/layout-check-2` (phase p2).

1. Script: in the phase, name each image once with a clear word ("look at the first frame", "on a real phone", "three openings").
2. Put 3 images in `examples/<slug>/assets/` (your own only: generated, drawn, or your own screenshots; no one else's media). Center the subject; tiles crop to 300x380.
3. Add to `script.json`:
   `"story": {"phase": "p2", "title": "max 7 words", "sub": "max 10 words", "sub_anchor": "wins", "images": [{"src": "assets/a.svg", "label": "max 3 words", "anchor": "frame", "n": 1}, ...]}` (exactly 3 images).
4. Pipeline: check_script, tts, build_data, then `python -I tools/storytelling.py examples/<slug>`.
5. `npx --no-install hyperframes check`, then `npx --no-install hyperframes snapshot --at <times>` after each anchor; look at the frames.
6. Report output paths and what was not checked. Never publish.
