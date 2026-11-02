"""Chatterbox-Turbo worker for tools/tts.py. Runs in its own venv (set SHORTS_CHATTERBOX_PY).

Reads a job file: {"items": [{"text", "ref", "seed", "out"}]} and writes each item's wav (24 kHz mono) to "out".
The voice comes from "ref", a short reference clip of a voice you have the rights to (do not clone a real person without consent).
Chatterbox adds Resemble's inaudible Perth watermark to everything it makes.

Usage: <chatterbox python> -I tools/engines/chatterbox_worker.py <job.json>
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
import torch
from chatterbox.tts_turbo import ChatterboxTurboTTS

SR = 24000

job = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
model = ChatterboxTurboTTS.from_pretrained(device="cuda" if torch.cuda.is_available() else "cpu")
for item in job["items"]:
    torch.manual_seed(int(item["seed"]))
    wav = model.generate(item["text"], audio_prompt_path=item["ref"])
    audio = wav.squeeze().detach().cpu().numpy().astype(np.float32)
    if model.sr != SR:
        audio = librosa.resample(audio, orig_sr=model.sr, target_sr=SR)
    sf.write(item["out"], audio, SR)
    print("made", Path(item["out"]).name, round(len(audio) / SR, 2), flush=True)
