"""Rebuild the external SRTs from the measured narration timelines, without media.

Run from anywhere with WOM_EPISODE_ROOT pointing at the episode folder (the
repository copy under new-channel/episodes/EP001_Anubis works). Audio and video
are untouched because the subtitles are not burned in.
"""
import json
import os
from pathlib import Path

from wom01_subtitles import sentence_cues, to_srt

root = Path(os.environ["WOM_EPISODE_ROOT"])
for lang in ("en", "ja"):
    timeline = json.loads((root / f"records/narration_timeline_{lang}.json").read_text())
    cues = [p for seg in timeline["segments"] for c in seg["cues"] for p in sentence_cues(c, lang)]
    prev = 0
    for c in cues:
        assert 0 <= prev <= c["start"] < c["end"] <= timeline["duration_seconds"]
        assert len(c["text"].splitlines()) <= 2
        prev = c["end"]
    (root / f"deliverables/EP001_字幕_{lang}.srt").write_text(to_srt(cues))
    (root / f"records/subtitle_cues_{lang}.json").write_text(json.dumps({
        "timing": "measured sentence boundaries; within-sentence page changes proportional to text length",
        "count": len(cues), "cues": cues}, ensure_ascii=False, indent=2)+"\n")
    print(lang, len(cues), "cues")
