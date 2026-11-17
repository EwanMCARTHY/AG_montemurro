# Explainer video (French)

A video of about 9 minutes 30 that explains the group 1 project from scratch:
ply, laminate, A/B/D matrices, polar method, objectives, the GA and the results.
The storyboard and the narration are in [scenario.md](scenario.md).

## Layout

| Path | Content |
|---|---|
| `scenario.md` | validated storyboard: narration, on-screen plan, durations |
| `scenes/common.py` | colours, LaTeX helpers, `NarratedScene` (narration timing and subtitle cues) |
| `scenes/sNN_*.py` | one Manim scene per storyboard scene |
| `record_population.py` | re-runs the GA (seed 1) and records the whole population for scene 10 |
| `narrate.py` | narration audio with edge-tts (voice Vivienne), one wav per beat |
| `build_video.py` | renders every scene, concatenates them, writes the subtitles |
| `sheet.sh` | quick check: low-quality render of one scene and a contact sheet of frames |
| `manim.cfg` | Manim settings (dark background, outputs in `build/`) |
| `build/` | renders, data, final videos (ignored by git) |

The project code in `Claude Momon's/` is only imported, never modified.

## Rebuild

From this folder, with the Python of the repository (`manim` and `imageio-ffmpeg` installed in `.venv`):

```bash
../.venv/Scripts/python record_population.py
../.venv/Scripts/python build_video.py
```

`build_video.py -q m` renders in 720p (faster), `--no-render` only reassembles.

Outputs: `build/video_ag.mp4`, `build/video_ag.srt` and `build/video_ag_subtitled.mp4` (soft subtitles).

## Narration

Each narration beat is a `with self.voice("..."):` block in the scenes. Without audio, its
length is estimated from the word count (160 words per minute). When a file
`build/audio/<SceneClass>_<NN>.wav` exists (NN = beat number from 01), it is added to the
soundtrack and its length sets the beat duration, so the animations stay in sync with the voice.

The audio is made with [edge-tts](https://github.com/rany2/edge-tts) (Microsoft neural voice
`fr-FR-VivienneMultilingualNeural`; the text is sent to Microsoft's online service).
`narrate.py` reads the beats from `build/cues/*.json`, so render once first, then:

    ../.venv/Scripts/python narrate.py            # only (re)generates beats whose text changed
    ../.venv/Scripts/python build_video.py -q h   # render again with the audio

A beat's text changes its audio only after the next render rewrites the cues, so after editing
narration run: render, `narrate.py`, render. Spoken forms (R0 -> "R zéro", MPa -> "mégapascals")
are listed in `SPOKEN` in `narrate.py`; the subtitles keep the written form.
