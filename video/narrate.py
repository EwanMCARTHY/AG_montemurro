"""
Generate the narration audio with edge-tts (Microsoft neural voices).

The text of each beat is read from build/cues/<Scene>.json (written by every
render), turned into a "spoken" form (R0 -> "R zéro", MPa -> "mégapascals",
...) and synthesised to build/audio/<Scene>_<NN>.wav, which NarratedScene.voice
then picks up. The subtitles keep the written form.

Note: edge-tts sends the text to Microsoft's online speech service.

Usage (from video/):
    ../.venv/Scripts/python narrate.py --samples          # one sentence, several voices
    ../.venv/Scripts/python narrate.py [--voice NAME] [--rate +0%] [--force]
"""

import argparse
import asyncio
import hashlib
import json
import re
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg

VIDEO_DIR = Path(__file__).resolve().parent
BUILD_DIR = VIDEO_DIR / "build"
CUES_DIR = BUILD_DIR / "cues"
AUDIO_DIR = BUILD_DIR / "audio"
SAMPLES_DIR = BUILD_DIR / "voice_samples"

DEFAULT_VOICE = "fr-FR-VivienneMultilingualNeural"
SAMPLE_VOICES = [
    "fr-FR-VivienneMultilingualNeural",
    "fr-FR-DeniseNeural",
    "fr-FR-EloiseNeural",
    "fr-FR-RemyMultilingualNeural",
    "fr-FR-HenriNeural",
]
SAMPLE_TEXT = ("Seuls R0 et R1 dépendent de l'empilement. Chaque pli est une flèche de "
               "longueur 1 : avec 0, 60 et moins 60 degrés, les flèches forment un triangle "
               "fermé, et la membrane est isotrope. R0 de A étoile vaut 44 MPa.")

# Written form -> spoken form (applied in this order)
SPOKEN = [
    (r"\bPhi(\d)", lambda m: "Fi " + "zéro un deux trois quatre cinq six sept huit neuf".split()[int(m[1])]),
    (r"\b([RT])0\b", r"\1 zéro"),
    (r"\b([RT])1\b", r"\1 un"),
    (r"\bMPa\b", "mégapascals"),
    (r"\bGPa\b", "gigapascals"),
    (r"(\d) %", r"\1 pour cent"),
    (r"\b3 par 3\b", "trois par trois"),
]


def spoken(text):
    for pat, rep in SPOKEN:
        text = re.sub(pat, rep, text)
    return text


async def synth(text, voice, rate, wav_path):
    """Synthesise `text` to a mono 48 kHz wav file."""
    mp3 = wav_path.with_suffix(".mp3")
    for attempt in range(5):          # the online service fails now and then
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(str(mp3))
            break
        except edge_tts.exceptions.NoAudioReceived:
            if attempt == 4:
                raise
            await asyncio.sleep(2 + 3 * attempt)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-loglevel", "error", "-y", "-i", str(mp3),
                    "-ac", "1", "-ar", "48000", str(wav_path)], check=True)
    mp3.unlink()


async def samples(rate):
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    for v in SAMPLE_VOICES:
        out = SAMPLES_DIR / f"{v}.wav"
        await synth(spoken(SAMPLE_TEXT), v, rate, out)
        print("sample:", out.name)


async def narrate(voice, rate, force):
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    for cue_file in sorted(CUES_DIR.glob("*.json")):
        scene = cue_file.stem
        for i, cue in enumerate(json.loads(cue_file.read_text(encoding="utf-8")), 1):
            text = spoken(cue["text"])
            wav = AUDIO_DIR / f"{scene}_{i:02d}.wav"
            stamp = wav.with_suffix(".txt")       # remembers what the wav says
            key = hashlib.sha1(f"{voice}|{rate}|{text}".encode()).hexdigest()
            if not force and wav.exists() and stamp.exists() and stamp.read_text() == key:
                continue
            await synth(text, voice, rate, wav)
            stamp.write_text(key)
            print(f"{wav.name}: {text[:70]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", action="store_true")
    ap.add_argument("--voice", default=DEFAULT_VOICE)
    ap.add_argument("--rate", default="+0%")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    asyncio.run(samples(a.rate) if a.samples else narrate(a.voice, a.rate, a.force))


if __name__ == "__main__":
    main()
