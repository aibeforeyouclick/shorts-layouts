---
name: split-screen
description: Split screen for a short - visuals on top, a host image below, captions on the seam - over one or more consecutive phases; the top visual swaps on spoken words. Use when the user asks for split screen, "host below", or a talking-host layout for a faceless short.
---
# /split-screen

Spec: `docs/SPEC.md`. Example: `examples/layout-check-2` (phase p1).

1. Host: one image of your character in `examples/<slug>/assets/` (1080x960 works best; it slowly zooms so the bottom never sits still). Video hosts are not supported in v1.
2. Top visuals: 1 to 6 images (1080x960; the top 75 px and bottom 75 px get cropped). The first shows from the start of the split; each next one swaps in on its word.
3. Add to `script.json`:
   `"split": {"phases": ["p1"], "host": "assets/host.svg", "top": [{"src": "assets/a.svg"}, {"src": "assets/b.svg", "anchor": "checklist", "n": 1, "phase": "p1"}]}`
4. Pipeline: check_script, tts, build_data, then `python -I tools/split_screen.py examples/<slug>`.
5. `npx --no-install hyperframes check`, snapshot at 0.05 s and after each swap; check the AI-GENERATED VOICE badge is clear of the top image and captions sit on the seam.
6. Report output paths and what was not checked. Never publish.
