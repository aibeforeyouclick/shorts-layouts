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
| Chatterbox-Turbo (`chatterbox-tts` 0.1.7) and its model | Optional dialogue voice engine (`"engine": "chatterbox"`) | MIT (package); model terms on its Hugging Face card | No, separate venv |
| `resemble-perth` 1.0.1 | Watermark Chatterbox adds to its audio | MIT | No |
| PyTorch, librosa | Chatterbox runtime, resampling | BSD-3-Clause / ISC | No |
| openai-whisper 20250625 (`small.en`) | Word timings for Chatterbox lines | MIT | No, separate venv |
| Lens and Clicky characters in `tools/layouts/split-screen.js` | Built-in narrator and dialogue characters | Drawn for this repo; MIT | Yes |
| `examples/*/audio/narration.wav` | Example narration | Generated with Kokoro by us; MIT like the rest of the repo | Yes |
| `examples/layout-check-2/assets/*.svg` | Example images | Drawn for this repo; MIT | Yes |
