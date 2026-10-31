# Layout skills: spec (v2)

Idea: package each recurring edit layout as a Claude Code skill with a one-line description, so an edit becomes "script + /layout-name". This repo implements four layouts for faceless shorts.

Scope: four layouts that need no new installs and no face on camera (v1: trial-reels, ranking-list; v2 adds storytelling, split-screen).

| Skill | What it makes | Input | Output |
|---|---|---|---|
| `/trial-reels` | 3 visually distinct openings of the same short, for Instagram trial reels / A-B tests. Same voice, same body; only the hook screen (phase p1) changes. | `trials` block in `script.json` (3 entries) | `trials.js`; a `trial` variable declared on `<html>` (default `off` = control); render each with `--variables '{"trial":"A"}'`. One `index.html` only (HyperFrames lint allows one root file). |
| `/ranking-list` | A tier board S to F. Cards drop into their row on the spoken word that names them. | `ranking` block in `script.json` | `ranking-list.data.js` + a board inside the chosen phase section |
| `/storytelling` | Three images, a title and a subtitle; each image pops in on its word. | `story` block | `storytelling.data.js` + the layout inside the phase |
| `/split-screen` | Visuals on top, a host image below (slow zoom), captions on the seam; top visual swaps on words. | `split` block | `split-screen.data.js` + a full-frame layer over the listed phases |

Later: video (not image) hosts for split-screen; a person-cutout layout would need an extra segmentation tool and is out of scope.

## Shared design
- One Python tool per skill in `tools/` validates the block, copies the runtime from `tools/layouts/` into `<video>/vendor/`, writes `<name>.data.js`, and adds the two `<script>` tags before `</body>` (idempotent). Shared code: `tools/layoutlib.py`. Image files must exist in the video folder.
- The runtime runs after the composition script, finds `window.__timelines.main`, builds its DOM inside `#root` and adds its tweens to that timeline. Timing anchors to spoken words (`window.WORDS`), never fixed seconds, like the rest of the pipeline.
- Channel rules stay on: the AI-GENERATED VOICE badge stays visible above every layout (z-index 5); captions stay on top (z-index 6); no new claim may appear on screen that is not in `sources`; no screen sits still for more than 5 s.
- Nothing publishes. Output is local files.

## `/trial-reels`
`script.json`:
```json
"trials": [
  {"style": "headline", "text": "Which captions get read", "sub": "four styles, ranked"},
  {"style": "post",     "text": "Four ways to caption a Short, ranked by how easy they read.", "sub": "our opinion, not a study",
   "name": "Your Brand", "handle": "@yourbrand", "avatar": "YB"},
  {"style": "minimal",  "text": "captions, ranked", "sub": "four styles, one phone"}
]
```
- Exactly 3 entries, 3 different styles from: `headline` (huge black-on-yellow words), `post` (a social-post card from our brand, no platform logo), `minimal` (light background, small lowercase text).
- `text` max 12 words, `sub` max 8 words. Both must restate what phase p1 already says (no new claim).
- The hook screen covers p1. `text` is on screen from frame 0 (the frame a feed shows first); `sub` enters halfway through p1; the screen fades out at the end of p1 and the original body plays.
- The tool refuses: missing p1 in timings, wrong count, duplicate styles, too-long text.

## `/ranking-list`
`script.json`:
```json
"ranking": {
  "phase": "p2",
  "title": "CAPTION STYLES",
  "items": [
    {"name": "Word by word", "tier": "S", "anchor": "word", "n": 1},
    {"name": "No captions",  "tier": "F", "anchor": "none", "n": 1}
  ]
}
```
- `phase`: the section id the board fills (the section must exist in `index.html`; its other content is hidden).
- Tiers S, A, B, C, D, F. All six rows are drawn; empty rows stay empty.
- Each card drops at `at(anchor, n)`: the n-th spoken occurrence of `anchor` (lowercase, letters only, as in `index.html`'s `at()`). The tool checks every anchor against `transcript.json` when it exists.
- Max 8 items, `name` max 3 words.

## Acceptance (v1)
1. `python -I tools/trial_reels.py examples/<slug>` writes trials.js and the variable; `hyperframes check` passes; frames from the 3 renders at t=0.1 show 3 different openings plus the control.
2. A test short with a ranking (`examples/layout-check`) runs the whole pipeline: check_script, TTS, build_data, ranking_list, check; a snapshot shows every card in its row.
3. Both skills are invocable in Claude Code from the repo root (`.claude/skills/*`).

## `/storytelling` and `/split-screen` (v2)
Blocks and limits are in each tool's docstring (`tools/storytelling.py`, `tools/split_screen.py`) and skill file. Rules: images are your own only (drawn, generated, or your own screenshots); the first frame of a split that opens the video is fully visible; anchors count inside their own phase.
Acceptance: `examples/layout-check-2` (split in p1, story in p2) passes `hyperframes check`; snapshots at 0.05 s, 5.5 s and after each story anchor show every element in place.
