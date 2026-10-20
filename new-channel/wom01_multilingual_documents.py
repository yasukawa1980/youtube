"""Package measured v02 timings, bilingual scripts, draft metadata and claims."""
import csv
import json
import os
from pathlib import Path


def clock(seconds):
    n = int(seconds)
    return f"{n//60:02}:{n%60:02}"


def main():
    root = Path(os.environ["WOM_EPISODE_ROOT"])
    source = Path(os.environ["WOM_SOURCE_ROOT"])
    read = lambda p: json.loads(p.read_text())
    master = read(root / "records/master_timeline.json")
    qc = read(root / "records/qc.json")
    times = {s["id"]: s for s in master["segments"]}
    museum = read(source / "records/museum_assets.json")
    deliver = root / "deliverables"
    bilingual = master["common_bilingual_timeline_finalized"]
    scope = ("英語・日本語の共通尺確定。" if bilingual else
             "英語のみの先行確認版。日本語修正音声と共通尺は未確定。現在の時刻は英語確認版用。")
    for lang in master["languages"]:
        content = read(root / "records" / ("content_en.json" if lang == "en" else "content.json"))
        sources = {s["id"]: s for s in content["sources"]}
        title = content["title"]
        lines = [f"# EP001 出典付き台本 / {lang}", "",
                 f'{title} — {clock(master["duration_seconds"])}（{master["duration_seconds"]:.6f}秒）', "",
                 scope + "字幕焼き込みなし。文単位は生成音声の実測境界。人による全編試聴は未実施。", ""]
        for s in content["segments"]:
            lines += [f'## {clock(times[s["id"]]["start"])} {s["id"]} {s["heading"]}', "",
                      f'区分：{s["classification"]}', "", s["text"], ""]
            for sid in s["sources"]:
                src = sources[sid]
                lines += [f'- [{sid} {src["title"]}]({src["url"]}) — {src["locator"]}']
            lines += [""]
        lines += ["## 制作上の留保", "",
                  "- 宗教的信仰・図像の説明であり、死後世界の実在を主張しない。",
                  "- MET 557830はNina de Garis Daviesによる紙上の模写。MET 590939と547871の同定は不確実。",
                  "- N09の棺は2019年にエジプトへ返還。棺の写真は使用せず、解説と明示した再現画を使用。",
                  "- N26はv02で削除。N13・N16・N19・N21を含む固有名詞の読みは本人の確認待ち。",
                  "- 画面の実際の使用素材・切り出しは records/visual_manifest.json を参照。", ""]
        (deliver / f"EP001_出典付き台本_{lang}.md").write_text("\n".join(lines))
        with (root / "records" / f"claims_{lang}.csv").open("w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["segment_id", "start_seconds", "classification", "sources", "source_locations", "claim_text", "review_status"])
            for s in content["segments"]:
                w.writerow([s["id"], f'{times[s["id"]]["start"]:.6f}', s["classification"], ";".join(s["sources"]),
                            ";".join(sources[x]["locator"] for x in s["sources"]), s["text"],
                            "source-linked; human full listening pending"])
        intro = (
            "Anubis, the canine-headed god of ancient Egypt, is famous for weighing the heart of the dead. "
            "But did he really judge alone? Using public collections and curatorial notes from The Metropolitan "
            "Museum of Art, this episode follows what Anubis does in the sources: guarding tombs, protecting the "
            "body, and overseeing the scale."
            if lang == "en" else
            "犬科の頭を持つ古代エジプトの神アヌビス。心臓を量る姿だけでなく、墓や身体を守る役割を、"
            "メトロポリタン美術館の公開資料から読み解きます。")
        disclosure = (
            "Museum photographs, modern facsimiles, explanatory diagrams, and AI-generated reconstructions "
            "are labeled separately. Religious beliefs are presented as beliefs, not historical events. "
            "Music: an original ambient score, not a reconstruction of ancient music."
            if lang == "en" else
            "博物館の資料写真、現代の壁画模写、図解、AI再現画を区別して表示しています。"
            "神話・信仰を現実に起きた出来事として断定しません。音楽は本作品用のオリジナル合成音です。")
        post = [f"# EP001 投稿情報 / {lang}（下書き・未投稿）", "", scope, "", "## Title", "",
                title + (" | What Museum Objects Reveal" if lang == "en" else ""), "",
                "## Description", "", intro, "", disclosure, "",
                "English narration: Kokoro / Heart (af_heart), synthetic speech.",
                "Japanese narration: VOICEVOX:雀松朱司", "",
                "Chapters"]
        for i, ch in enumerate(content["chapters"]):
            first = next(s for s in master["segments"] if s["chapter"] == ch["id"])
            post += [f'{clock(0 if i == 0 else first["start"])} {ch["title"]}']
        post += ["", "Sources: The Metropolitan Museum of Art"]
        for s in content["sources"]:
            post += [f'{s["id"]} {s["title"]}', s["url"]]
        post += ["", "Images: The Metropolitan Museum of Art / Open Access (CC0)",
                 "https://www.metmuseum.org/hubs/open-access"]
        for m in museum:
            post += [f'{m["object_id"]} / {m["object_number"]} — {m["credit_line"]}']
        post += ["", "MET 557830: a facsimile on paper by Nina de Garis Davies. "
                 "MET 590939 and 547871: identification uncertain. "
                 "Nedjemankh's coffin was returned to Egypt in 2019; no photograph of the coffin is used.", "",
                 "Kokoro model: https://huggingface.co/hexgrad/Kokoro-82M (Apache-2.0)",
                 "VOICEVOX: https://voicevox.hiroshiba.jp/term/", "",
                 "## 公開前の確認", "",
                 "人による英語・日本語の全編試聴、固有名詞の読み、BGM、章の間を確認する。"
                 "投稿は未承認。Studioの多言語音声機能・AI使用開示は投稿前に画面で確認する。"
                 "字幕は言語別SRT。焼き込みなし。新チャンネル・契約・購入・投稿操作は行っていない。", ""]
        (deliver / f"EP001_投稿用情報_{lang}.md").write_text("\n".join(post))
    rights = ["# EP001 v02 素材・音声と利用条件", "", scope, "",
              "英語は2026-10-20に本人がB（Heart / af_heart）を選択。日本語はVOICEVOX:雀松朱司。",
              "音声条件の詳細・確認URL・モデルハッシュは records/voice_license.json。", "",
              "## 既存画像の再利用", "",
              "The Metropolitan Museum of Art / Open Access (CC0)。既存10点を使用し、原画像の移動・改変は行わず、切り出しと英語の画面組版を別ファイルに保存。", ""]
    for m in museum:
        rights += [f'- [{m["object_id"]} {m["title"]}]({m["url"]}) / {m["object_number"]} / {m["credit_line"]}']
    rights += ["", "AI再現画は既存4枚を再利用し、新たな画像生成の支出はなし。"
               "図解は制作コードで作成。BGMは既存と同じ合成式を共通尺に延長したオリジナル音。"
               "古代音楽の復元ではない。フォントファイルの配布はしない。", "",
               "英語モデル：Kokoro-82M v1、Apache-2.0。kokoro-onnxはMIT。"
               "既に試聴版で確認したモデル・声と同一ファイルを使用。"
               "日本語音声の使用時はVOICEVOX:雀松朱司のクレジットを保持。", "",
               "人による全編試聴・公開判断は残る。専門家の査読済みとは表示しない。", ""]
    (deliver / "EP001_素材と権利台帳_v02.md").write_text("\n".join(rights))
    print(f"Scripts ({', '.join(master['languages'])}), timed claims, credits and draft metadata ready.", flush=True)


if __name__ == "__main__":
    main()
