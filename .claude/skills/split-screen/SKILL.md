---
name: split-screen
description: Split screen for a short - visuals on top, a host image below, captions on the seam - over one or more consecutive phases; the top visual swaps on spoken words. Use when the user asks for split screen, "host below", or a talking-host layout for a faceless short.
---
# /split-screen

Spec: `docs/SPEC.md`. Example: `examples/layout-check-2` (phase p1).

1. Host: one image of your character in `examples/<slug>/assets/` (1080x960 works best; it slowly zooms so the bottom never sits still), or a built-in character: `"mascot": "lens"` (a lens drawn inline and driven by the word timings: idle = the eye floats, glances and blinks; speaking = 5 bars jump on every word with a pulse ring). Video hosts are not supported.
   Dialogue: `"mascot": "lens+clicky"` puts Lens (left) and Clicky, a cursor character (right), in the bottom half. The script needs `"cast": {"lens": {"voice": "am_michael", "speed": 1.0}, "clicky": {"voice": "af_heart", "speed": 1.0}}` and lines written as `{"who": "clicky", "text": "...", "gap": 0.2}` (gap = pause after the line in seconds; negative = interruption). tools/tts.py trims each line's own silence and writes envelope.json, so the mouth and bars follow the real loudness frame by frame; the listener looks at the speaker; captions take the speaker's colour. Tune the comic timing with the per-line gaps, then run tools/sync_index.py before build_data. Voice engine: add `"engine": "chatterbox"` for Chatterbox-Turbo (more natural; cues `[laugh]` `[sigh]` `[chuckle]` inside a line's text; voices from voices/lens.wav and voices/clicky.wav, short clips of voices you have the rights to). Lines are cached in audio/lines/, so changing gaps re-times instantly; a bad take gets a new `"seed"` on that line. Word times come from whisper. Kokoro `[word](/phonemes/)` overrides are ignored by Chatterbox (it reads the plain word), so listen to heteronyms. Setup: README, "Dialogue".
2. Top visuals: 1 to 6 images (1080x960; the top 75 px and bottom 75 px get cropped). The first shows from the start of the split; each next one swaps in on its word.
3. Add to `script.json`:
   `"split": {"phases": ["p1"], "host": "assets/host.svg", "top": [{"src": "assets/a.svg"}, {"src": "assets/b.svg", "anchor": "checklist", "n": 1, "phase": "p1"}]}`
4. Pipeline: check_script, tts, build_data, then `python -I tools/split_screen.py examples/<slug>`.
5. `npx --no-install hyperframes check`, snapshot at 0.05 s and after each swap; check the AI-GENERATED VOICE badge is clear of the top image and captions sit on the seam.
6. Report output paths and what was not checked. Never publish.
