# Third-party components

Nothing below is copied into this repository except where noted. Each keeps its own license.

| Component | Used for | License | In this repo? |
|---|---|---|---|
| HyperFrames 0.8.147 (npm) | HTML composition check and render | Apache-2.0 | No, installed with `npm install` |
| GSAP 3.14.2 (npm) | Animation timeline | GreenSock Standard "no charge" license (not open source) | No. Copy `node_modules/gsap/dist/gsap.min.js` into each video's `vendor/` yourself |
| Kokoro 0.9.4 and the Kokoro-82M model | Narration (text to speech) | Apache-2.0 | No, installed with pip; model downloaded on first run |
| misaki, spaCy, `en_core_web_sm` | English phonemizer used by Kokoro | Apache-2.0 / MIT | No |
| espeak-ng (loaded by `espeakng-loader`, a Kokoro dependency) | Fallback phonemizer | espeak-ng: GPL-3.0 (the loader states no license in its metadata) | No, runtime dependency only |
| numpy, soundfile | Audio | BSD-3-Clause | No |
| `examples/*/audio/narration.wav` | Example narration | Generated with Kokoro by us; MIT like the rest of the repo | Yes |
| `examples/layout-check-2/assets/*.svg` | Example images | Drawn for this repo; MIT | Yes |
