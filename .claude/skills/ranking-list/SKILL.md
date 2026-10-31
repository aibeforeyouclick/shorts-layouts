---
name: ranking-list
description: Turn one phase of a short into an S-to-F tier board where each card drops into its row on the spoken word that names it. Use when the user asks for a ranking, tier list, or "best to worst" short.
---
# /ranking-list

Spec: `docs/SPEC.md`. Example: `examples/layout-check`.

1. Script first. In the ranking phase, speak each item once with a clear word to anchor on ("Word by word highlight goes in S."). Every ranking is either sourced in `sources` or said out loud as an opinion.
2. Add to `script.json`:
   `"ranking": {"phase": "p2", "title": "CAPTION STYLES", "items": [{"name": "Word by word", "tier": "S", "anchor": "word", "n": 1}]}`
   Tiers S A B C D F; max 8 items; `name` max 3 words; `n` counts occurrences of `anchor` inside that phase only.
3. Run the pipeline: check_script.py, tts.py, build_data.py, then `python -I tools/ranking_list.py examples/<slug>`. It refuses anchors that are not spoken in the phase.
4. In `index.html` the section `#<phase>` must exist; its own content is hidden while the board shows, so leave a simple placeholder there.
5. `npx --no-install hyperframes check`, render draft, pull a frame after the last anchor and check every card sits in its row.
6. Report the board, output path, what was not checked. Never publish.
