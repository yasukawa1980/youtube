"""EP001 local narration; language-specific sentence caches and measured timings.

WOM_EPISODE_ROOT: new production folder (records/content*.json must exist).
WOM_SOURCE_ROOT: old episode, used only to read Japanese cached sentences.
WOM_LANG=en|ja; WOM_KOKORO_MODELS; WOM_VOICEVOX_RUNTIME.
No network, paid services, or publication operations.
"""
import hashlib
import json
import os
import re
import shutil
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 24000


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def spoken_ja(text):
    for a, b in {
        '七・七': 'ななてんなな', 'エーアイ': 'エーアイ',
        'ナクトアメン': 'ナクトアメン', 'アメンエムハト一世': 'アメンエムハト、いっせい',
        '紀元前千五十年頃': 'きげんぜん、せんごじゅうねんごろ',
        '紀元前二千年頃': 'きげんぜん、にせんねんごろ',
        '死者の書': 'ししゃのしょ', '棺材': 'かんざい', '秤量': 'ひょうりょう',
        '祭具': 'さいぐ', 'アンク': 'アンク', 'ナウニ': 'ナウニ',
        '紀元前千九百八十年頃': 'きげんぜん、せんきゅうひゃくはちじゅうねんごろ',
        '二〇一九年': 'にせんじゅうきゅうねん', '銅合金': 'どうごうきん',
        '何柱': 'なんはしら', 'AI': 'エーアイ',
    }.items():
        text = text.replace(a, b)
    return text


def spoken_en(text):
    # Only unambiguous written numbers/initials; proper names remain in the script.
    for a, b in {
        "1050 BCE": "ten fifty B C E",
        "1980 BCE": "nineteen eighty B C E",
        "Amenemhat I": "Amenemhat the First",
        "7.7 centimeters": "seven point seven centimeters",
        "AI-generated": "A I generated",
    }.items():
        text = text.replace(a, b)
    return text


def main():
    root = Path(os.environ["WOM_EPISODE_ROOT"]).resolve()
    source = Path(os.environ["WOM_SOURCE_ROOT"]).resolve()
    lang = os.environ["WOM_LANG"]
    assert lang in ("en", "ja")
    content = json.loads((root / "records" / ("content_en.json" if lang == "en" else "content.json")).read_text())
    folder = root / "audio" / lang / "sentences"
    folder.mkdir(parents=True, exist_ok=True)
    synth = None
    counts = {"new": 0, "reused_legacy": 0, "reused_current": 0}
    pacing_file = root / "records/english_pacing.json"
    pacing = json.loads(pacing_file.read_text()) if pacing_file.exists() else {}
    if lang == "en":
        import onnxruntime as ort
        from kokoro_onnx import Kokoro
        ort.disable_telemetry_events()
        models = Path(os.environ["WOM_KOKORO_MODELS"])
        options = ort.SessionOptions()
        options.intra_op_num_threads = 4
        options.inter_op_num_threads = 1
        tts = Kokoro.from_session(
            ort.InferenceSession(str(models / "kokoro-v1.0.onnx"), options, providers=["CPUExecutionProvider"]),
            str(models / "voices-v1.0.bin"),
        )
        model_hash = hashlib.sha256((models / "kokoro-v1.0.onnx").read_bytes()).hexdigest()
        voice_hash = hashlib.sha256((models / "voices-v1.0.bin").read_bytes()).hexdigest()
    records = []
    for seg in content["segments"]:
        speed = pacing.get(seg["id"], .82)
        sentences = (re.split(r"(?<=[.!?])\s+", seg["text"]) if lang == "en"
                     else re.findall(r"[^。！？]+[。！？]?", seg["text"]))
        pieces, cues, cursor = [], [], 0
        for j, text in enumerate(sentences, 1):
            spoken = spoken_en(text) if lang == "en" else spoken_ja(text)
            if lang == "ja":
                config = {"style_id": 52, "speed_scale": 1.03, "intonation_scale": 0.88,
                          "pre_phoneme_length": 0.08, "post_phoneme_length": 0.17,
                          "output_sampling_rate": SR, "spoken_text": spoken}
            else:
                config = {"voice": "af_heart", "language": "en-us", "speed": speed,
                          "sentence_pause": .3, "clause_pause": .12,
                          "model_sha256": model_hash, "voices_sha256": voice_hash,
                          "engine": "kokoro-onnx 0.6.1", "spoken_text": spoken}
            key = digest(config)
            path = folder / f'{seg["id"]}_{j:02}_{key[:12]}.wav'
            if path.exists() and json.loads(path.with_suffix(".json").read_text()) == config:
                counts["reused_current"] += 1
            else:
                legacy = list((source / "audio/segments").glob(f"*_{key[:8]}.wav")) if lang == "ja" else []
                # Check full config as well as the old short filename hash.
                legacy = [p for p in legacy if p.with_suffix(".json").exists()
                          and json.loads(p.with_suffix(".json").read_text()) == config]
                if legacy:
                    shutil.copy2(legacy[0], path)
                    counts["reused_legacy"] += 1
                elif lang == "ja":
                    if synth is None:
                        from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
                        runtime = Path(os.environ["WOM_VOICEVOX_RUNTIME"])
                        ort = Onnxruntime.load_once(filename=str(next((runtime / "onnxruntime/lib").glob("*.dylib"))))
                        synth = Synthesizer(ort, OpenJtalk(str(runtime / "dict/open_jtalk_dic_utf_8-1.11")),
                                            acceleration_mode="CPU", cpu_num_threads=2)
                        with VoiceModelFile.open(str(runtime / "models/vvms/12.vvm")) as model:
                            synth.load_voice_model(model)
                    q = synth.create_audio_query(spoken, 52)
                    for field, val in config.items():
                        if field not in ("style_id", "spoken_text"):
                            setattr(q, field, val)
                    path.write_bytes(synth.synthesis(q, 52))
                    counts["new"] += 1
                else:
                    audio, rate = tts.create(spoken, voice="af_heart", lang="en-us", speed=speed,
                                             sentence_pause=.3, clause_pause=.12)
                    assert rate == SR
                    sf.write(path, audio, SR, subtype="PCM_16")
                    counts["new"] += 1
                write_json(path.with_suffix(".json"), config)
            audio, rate = sf.read(path, dtype="float32")
            assert rate == SR and audio.ndim == 1 and len(audio) > 0
            cues.append({"id": f'{seg["id"]}-{j:02}', "text": text, "spoken_text": spoken,
                         "start": cursor / SR, "end": (cursor + len(audio)) / SR,
                         "audio_file": str(path.relative_to(root)), "input_hash": key})
            pieces.append(audio)
            cursor += len(audio)
            if j != len(sentences):
                gap = np.zeros(round((.22 if lang == "en" else .16) * SR), np.float32)
                pieces.append(gap)
                cursor += len(gap)
        assembled = np.concatenate(pieces)
        path = root / "audio" / lang / f'{seg["id"]}.wav'
        sf.write(path, assembled, SR, subtype="PCM_16")
        records.append({**seg, "duration_seconds": len(assembled) / SR, "native_speed": speed if lang == "en" else 1.03,
                        "audio_file": str(path.relative_to(root)), "cues": cues})
        print(lang, seg["id"], f"{len(assembled)/SR:.3f}s", counts, flush=True)
    report = {"language": lang, "sample_rate": SR, "voice": "Kokoro: af_heart" if lang == "en" else "VOICEVOX:雀松朱司",
              "sentence_boundary_timing": "measured individual synthesis; relative to segment",
              "human_auditory_review_completed": False, "cache_counts": counts, "segments": records}
    write_json(root / "records" / f"narration_segments_{lang}.json", report)


if __name__ == "__main__":
    main()
