"""
Render every scene and assemble the full explainer video.

Steps
1. (unless --no-render) render each scene with Manim at the chosen quality;
   each render also writes build/cues/<Scene>.json (one cue per narration beat);
2. concatenate the scene videos in order into build/video_ag.mp4;
3. write build/video_ag.srt (French subtitles) from the cues, shifted by
   the start time of each scene, and mux them as a soft subtitle track into
   build/video_ag_subtitled.mp4.

Usage (from the video/ folder):
    ../.venv/Scripts/python build_video.py              # 1080p60 render + assembly
    ../.venv/Scripts/python build_video.py -q m         # 720p30, faster
    ../.venv/Scripts/python build_video.py --no-render  # assembly only
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# (file stem in scenes/, scene class), in video order
SCENES = [
    ("s01_hook", "S01Hook"),
    ("s02_ply", "S02Ply"),
    ("s03_stiffness", "S03Stiffness"),
    ("s04_abd", "S04ABD"),
    ("s05_polar", "S05Polar"),
    ("s06_arrows", "S06Arrows"),
    ("s07_objectives", "S07Objectives"),
    ("s08_decisions", "S08Decisions"),
    ("s09_ga", "S09GA"),
    ("s10_results", "S10Results"),
    ("s11_end", "S11End"),
]
QUALITY_DIR = {"l": "480p15", "m": "720p30", "h": "1080p60", "k": "2160p60"}


def render(stem, cls, quality):
    print(f"--- rendering {cls} ({QUALITY_DIR[quality]})", flush=True)
    subprocess.run([sys.executable, "-m", "manim", f"-q{quality}", "--disable_caching",
                    f"scenes/{stem}.py", cls], cwd=HERE, check=True,
                   stdout=subprocess.DEVNULL)


def duration(path):
    """Duration of a media file [s], read from ffmpeg's banner."""
    out = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def split_cue(start, end, text, max_chars=84):
    """Split a long beat into subtitle lines of at most ~2 x 42 characters,
    sharing the beat duration in proportion to their length."""
    words, chunks, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            chunks.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    chunks.append(cur)
    total = sum(len(c) for c in chunks)
    out, t = [], start
    for c in chunks:
        dt = (end - start) * len(c) / total
        out.append((t, t + dt, c))
        t += dt
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", "--quality", default="h", choices=list(QUALITY_DIR))
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()
    qdir = QUALITY_DIR[args.quality]

    if not args.no_render:
        for stem, cls in SCENES:
            render(stem, cls, args.quality)

    videos = [BUILD / "media" / "videos" / stem / qdir / f"{cls}.mp4" for stem, cls in SCENES]
    for v in videos:
        if not v.exists():
            sys.exit(f"missing {v}: render it first")

    # 1. Concatenation (same codec and settings for every scene: stream copy)
    listing = BUILD / "concat.txt"
    listing.write_text("".join(f"file '{v.as_posix()}'\n" for v in videos), encoding="utf-8")
    full = BUILD / "video_ag.mp4"
    subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c", "copy", str(full)], check=True)

    # 2. Subtitles from the narration cues
    entries, offset = [], 0.0
    for (stem, cls), v in zip(SCENES, videos):
        cues = json.loads((BUILD / "cues" / f"{cls}.json").read_text(encoding="utf-8"))
        for c in cues:
            entries += split_cue(offset + c["start"], offset + c["end"], c["text"])
        offset += duration(v)
    srt = BUILD / "video_ag.srt"
    srt.write_text("".join(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{t}\n\n"
                           for i, (a, b, t) in enumerate(entries, 1)), encoding="utf-8")

    # 3. Soft subtitle track (can be switched on/off in the player)
    subbed = BUILD / "video_ag_subtitled.mp4"
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(full), "-i", str(srt), "-c", "copy",
                    "-c:s", "mov_text", "-metadata:s:s:0", "language=fre", str(subbed)], check=True)

    print(f"video     : {full}  ({duration(full) / 60:.1f} min)")
    print(f"subtitles : {srt}  ({len(entries)} lines)")
    print(f"with subs : {subbed}")


if __name__ == "__main__":
    main()
