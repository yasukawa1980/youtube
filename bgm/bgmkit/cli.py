"""コマンド入口。

  python3 -m bgmkit analyze vol11    候補曲の計測と重複検出 → _work/analysis.json
  python3 -m bgmkit select  vol11    本採用の選抜（--write でYAMLに書き戻し）
  python3 -m bgmkit order   vol11    曲順の決定（--write でYAMLに書き戻し）
  python3 -m bgmkit audio   vol11    トリム→-14LUFS→連結 → _work/music_bed.wav
  python3 -m bgmkit video   vol11    ケンバーンズ＋クロスフェード → _work/video.mp4
  python3 -m bgmkit mux     vol11    音と映像を合わせて完成MP4
  python3 -m bgmkit thumb   vol11    サムネイル
  python3 -m bgmkit build   vol11    audio→video→mux→thumb を通しで
"""
import argparse
import sys

from . import analyze, audio, config, select, thumb, video


def _need_order(cfg):
    order = cfg.get("order_tracks")
    if not order:
        raise SystemExit(
            "曲順が未確定です。`order` を --write 付きで実行してから続けてください。")
    return order


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bgmkit", description="BGM動画の制作パイプライン")
    ap.add_argument("command", choices=["analyze", "select", "order", "audio",
                                        "video", "mux", "thumb", "build"])
    ap.add_argument("volume", help="volumes/ の設定ファイル名（拡張子は省略可）")
    ap.add_argument("--write", action="store_true",
                    help="select / order の結果を巻のYAMLに書き戻す")
    args = ap.parse_args(argv)

    cfg = config.load(args.volume)
    c = args.command

    if c == "analyze":
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
