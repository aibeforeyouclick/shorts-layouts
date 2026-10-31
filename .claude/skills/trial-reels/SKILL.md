---
name: trial-reels
description: Make 3 visually distinct openings (headline / post card / minimal) of an existing short for Instagram trial reels or A/B tests. Same voice and body; only the hook screen over phase p1 changes. Use when the user asks for trial reels, hook variants, or A/B versions of a short.
---
# /trial-reels

Spec: `docs/SPEC.md`. Works on a short that already went through tts.py and build_data.py.

1. Read `examples/<slug>/script.json`, phase p1 and `sources`. Write a `trials` block with exactly 3 entries, one per style:
   - `headline`: 2-5 punchy words, black on yellow
   - `post`: one sentence as a post card from your brand (set `name`, `handle`, `avatar` on the entry) (max 12 words)
   - `minimal`: 2-5 lowercase words on a light background
   Each has `text` (max 12 words) and `sub` (max 8 words). Both must restate p1; no new claim, no number that is not in `sources`. Edit script.json by hand (keep its compact formatting).
2. `python -I tools/trial_reels.py examples/<slug>`. Fix any ERROR it prints and rerun (it is idempotent).
3. `cd examples/<slug>` then `npx --no-install hyperframes check` (set `HYPERFRAMES_NO_TELEMETRY=1`, `DO_NOT_TRACK=1`).
4. Render each version: `npx --no-install hyperframes render -q draft --variables "{\"trial\":\"A\"}" -o out/<slug>-A.mp4` (B, C the same). No `--variables` = the control.
5. Look before reporting: pull frames at 0.1 s and halfway through p1 with ffmpeg and check that the text is readable, the AI-GENERATED VOICE badge shows, and captions do not cover the hook text.
6. Report: the 3 texts, the output paths, what was not checked. Never publish anything; the user decides what goes up.
