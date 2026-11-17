"""
Shared style and helpers for every scene of the explainer video.

- Colours: one fixed colour per tensor, as in "Claude Momon's/plots.py"
  (ply Q blue, A* green, B* purple, D* red), lightened for a dark background.
- NarratedScene.voice(): a context manager that times one narration beat.
  The animations played inside the block start with the beat; if they are
  shorter than the narration, the scene waits for the rest. Each beat is
  recorded as a subtitle cue in build/cues/<SceneName>.json.
- The project code in "Claude Momon's/" is imported read-only, never edited.
"""

import json
import sys
import wave
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP, Line, MathTex, Scene, Tex, TexTemplate, VGroup,
)

# ---------------------------------------------------------------------------
# Paths and project code
# ---------------------------------------------------------------------------
VIDEO_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = VIDEO_DIR.parent
PROJECT_DIR = REPO_DIR / "Claude Momon's"
BUILD_DIR = VIDEO_DIR / "build"
AUDIO_DIR = BUILD_DIR / "audio"
CUES_DIR = BUILD_DIR / "cues"

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import config  # noqa: E402  (project input data)

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
BG = "#11151c"
FG = "#e8e6e1"          # main text
MUTED = "#8a93a3"       # secondary text, axes
ACCENT = "#f2b134"      # highlights, warnings
COL_Q = "#5aa9e6"       # ply Q (plots.py: tab:blue)
COL_A = "#5cc46a"       # A* (tab:green)
COL_B = "#b48ee0"       # B* (tab:purple)
COL_D = "#ef6461"       # D* (tab:red)
COL_FIBRE = "#2b2f36"   # carbon fibres
COL_RESIN = "#c89b5a"   # epoxy resin

# ---------------------------------------------------------------------------
# LaTeX: default template + amssymb, French text typed with explicit
# non-breaking spaces before ':' (babel-french is avoided because it makes
# ':' active, which breaks some math).
# ---------------------------------------------------------------------------
TEMPLATE = TexTemplate()
TEMPLATE.add_to_preamble(r"\usepackage{amssymb}")


def tex(text, size=36, color=FG, **kw):
    """French text (LaTeX), inline math allowed with $...$."""
    return Tex(text, tex_template=TEMPLATE, font_size=size, color=color, **kw)


def math(text, size=40, color=FG, **kw):
    """Display math."""
    return MathTex(text, tex_template=TEMPLATE, font_size=size, color=color, **kw)


# ---------------------------------------------------------------------------
# Narration timing
# ---------------------------------------------------------------------------
WORDS_PER_SECOND = 160 / 60   # usual voice-over pace (see scenario.md)
BEAT_PAD = 0.4                # breathing time after each beat [s]


def estimated_duration(text):
    """Estimated speaking time of a narration beat [s]."""
    return len(text.split()) / WORDS_PER_SECOND + BEAT_PAD


def wav_duration(path):
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


class NarratedScene(Scene):
    """Scene whose timing is driven by narration beats."""

    def setup(self):
        self.cues = []

    @contextmanager
    def voice(self, text):
        """
        Time one narration beat. If build/audio/<Scene>_<NN>.wav exists, it
        is added to the soundtrack and its length sets the beat duration;
        otherwise the duration is estimated from the word count.
        """
        index = len(self.cues) + 1
        audio = AUDIO_DIR / f"{type(self).__name__}_{index:02d}.wav"
        start = self.time
        if audio.exists():
            self.add_sound(str(audio))
            target = wav_duration(audio) + BEAT_PAD
        else:
            target = estimated_duration(text)
        yield
        elapsed = self.time - start
        if elapsed < target:
            self.wait(target - elapsed)
        self.cues.append({"start": start, "end": self.time, "text": " ".join(text.split())})

    def tear_down(self):
        CUES_DIR.mkdir(parents=True, exist_ok=True)
        out = CUES_DIR / f"{type(self).__name__}.json"
        out.write_text(json.dumps(self.cues, ensure_ascii=False, indent=1), encoding="utf-8")


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def clip_line_to_rect(p, d, xmin, xmax, ymin, ymax):
    """
    Segment of the infinite line p + t d inside an axis-aligned rectangle
    (Liang-Barsky). Returns (start, end) as 2D arrays, or None.
    """
    t0, t1 = -np.inf, np.inf
    for pi, di, lo, hi in ((p[0], d[0], xmin, xmax), (p[1], d[1], ymin, ymax)):
        if abs(di) < 1e-12:
            if pi < lo or pi > hi:
                return None
            continue
        a, b = (lo - pi) / di, (hi - pi) / di
        t0, t1 = max(t0, min(a, b)), min(t1, max(a, b))
    if t0 >= t1:
        return None
    return p + t0 * d, p + t1 * d


def fibre_hatch(center, width, height, angle_deg, spacing=0.14, color=COL_FIBRE,
                stroke=1.6):
    """
    Parallel lines at angle_deg (fibre direction seen from above) clipped to
    a width x height rectangle centred on `center`.
    """
    cx, cy = center[0], center[1]
    xmin, xmax = cx - width / 2, cx + width / 2
    ymin, ymax = cy - height / 2, cy + height / 2
    a = np.radians(angle_deg)
    d = np.array([np.cos(a), np.sin(a)])
    n = np.array([-np.sin(a), np.cos(a)])
    reach = np.hypot(width, height) / 2
    lines = VGroup()
    for off in np.arange(-reach, reach + spacing, spacing):
        seg = clip_line_to_rect(np.array([cx, cy]) + off * n, d, xmin, xmax, ymin, ymax)
        if seg is None:
            continue
        s, e = seg
        if np.hypot(*(e - s)) < 1e-3:
            continue
        lines.add(Line([s[0], s[1], 0], [e[0], e[1], 0], color=color, stroke_width=stroke))
    return lines


__all__ = [
    "np", "config", "NarratedScene", "tex", "math", "fibre_hatch",
    "BG", "FG", "MUTED", "ACCENT", "COL_Q", "COL_A", "COL_B", "COL_D",
    "COL_FIBRE", "COL_RESIN", "UP", "DOWN", "LEFT", "RIGHT", "PROJECT_DIR",
]
