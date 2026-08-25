"""コマンド入口。

  python3 -m bgmkit images  vol11    場面ごとの画像をAPIで生成（--only 3 5 で一部だけ）
  python3 -m bgmkit analyze vol11    候補曲の計測と重複検出 → _work/analysis.json
  python3 -m bgmkit select  vol11    本採用の選抜（--write でYAMLに書き戻し）
  python3 -m bgmkit order   vol11    曲順の決定（--write でYAMLに書き戻し）
  python3 -m bgmkit audio   vol11    トリム→-14LUFS→連結 → _work/music_bed.wav
  python3 -m bgmkit video   vol11    ケンバーンズ＋クロスフェード → _work/video.mp4
  python3 -m bgmkit mux     vol11    音と映像を合わせて完成MP4
  python3 -m bgmkit thumb   vol11    サムネイル
  python3 -m bgmkit build   vol11    audio→video→mux→thumb を通しで
  python3 -m bgmkit short   vol11    縦型ショートを作る（--only A B で一部だけ）
  python3 -m bgmkit vet     <file…>  環境音の素材を検品（巻ではなくファイル/フォルダを渡す）
  python3 -m bgmkit vet --insect <file…>  虫・蝉向けの検品（音程で落とさず種の指紋を出す）
"""
import argparse
import sys

from . import analyze, audio, config, images, select, short, thumb, vet, video


def _need_order(cfg):
    order = cfg.get("order_tracks")
    if not order:
        raise SystemExit(
            "曲順が未確定です。`order` を --write 付きで実行してから続けてください。")
    return order


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bgmkit", description="BGM動画の制作パイプライン")
    ap.add_argument("command", choices=["images", "analyze", "select", "order", "audio",
                                        "video", "mux", "thumb", "build", "vet", "short"])
    ap.add_argument("target", nargs="+",
                    help="volumes/ の設定ファイル名（拡張子は省略可）。"
                         "vet のときだけ検品するファイルかフォルダを並べる")
    ap.add_argument("--write", action="store_true",
                    help="select / order の結果を巻のYAMLに書き戻す")
    ap.add_argument("--insect", action="store_true",
                    help="vet を虫・蝉向けに切り替える（音程で落とさず、種の指紋を出す）")
    ap.add_argument("--only", nargs="+", metavar="N",
                    help="images は番号（1始まり）、short は札（A B）で絞る")
    args = ap.parse_args(argv)
    c = args.command

    # vet は巻に属さない。素材を仕入れた時点で回すので設定ファイルがまだ無い。
    if c == "vet":
        vet.run_vet(args.target, insect=args.insect)
        return 0

    if len(args.target) > 1:
        raise SystemExit(f"{c} は巻を1つだけ取ります: {' '.join(args.target)}")
    cfg = config.load(args.target[0])

    if c == "images":
        images.run(cfg, only=[int(x) for x in args.only] if args.only else None)

    elif c == "short":
        short.build(cfg, only=args.only)

    elif c == "analyze":
        analyze.run(cfg)

    elif c == "select":
        chosen = select.select(cfg)
        if args.write:
            config.save_volume(cfg, "picked", chosen)
            print("\npicked を書き戻しました。次は `order` です。")

    elif c == "order":
        picked = cfg.get("picked") or select.select(cfg)
        seq = select.order(cfg, picked)
        if args.write:
            config.save_volume(cfg, "order_tracks", seq)
            print("\norder_tracks を書き戻しました。次は `audio` です。")

    elif c == "audio":
        audio.build(cfg, _need_order(cfg))

    elif c == "video":
        video.build(cfg)

    elif c == "mux":
        video.mux(cfg)

    elif c == "thumb":
        thumb.check_runtime(cfg)
        thumb.build(cfg)

    elif c == "build":
        audio.build(cfg, _need_order(cfg))
        video.build(cfg)
        video.mux(cfg)
        thumb.check_runtime(cfg)
        thumb.build(cfg)

    return 0


if __name__ == "__main__":
    sys.exit(main())
