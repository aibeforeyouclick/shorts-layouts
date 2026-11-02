"""What a script line says, for each consumer (Kokoro, Chatterbox, captions).

A line is a string (narration) or {"who", "text", "gap", "seed"} (dialogue). Its text may hold
  [word](/phonemes/)  a Kokoro pronunciation override; Chatterbox and captions get the plain word
  [laugh] [chuckle] [sigh] ...  a non-verbal cue for Chatterbox; Kokoro and captions drop it
"""
import re

OVERRIDE = re.compile(r"\[([^\]]+)\]\(/[^)]*/\)")
CUE = re.compile(r"\s*\[[a-z ]+\](?!\()")


def text_of(line):
    return line["text"] if isinstance(line, dict) else line


def for_kokoro(text):
    return CUE.sub("", text).strip()


def for_chatterbox(text):
    return OVERRIDE.sub(r"\1", text).strip()


def spoken_tokens(text):
    """Spoken words in order, punctuation kept (build_data reads sentence ends from it)."""
    plain = CUE.sub("", OVERRIDE.sub(r"\1", text))
    return [t for t in plain.split() if any(c.isalnum() for c in t)]


def caption_words(text):
    return [t.strip(".,!?;:\"()") for t in spoken_tokens(text)]
