"""設定の2層読み込み。

  genres/<ジャンル>.yaml  … 音の設計・映像の作り・サムネの型。ジャンルで固定。
  volumes/<巻>.yaml       … 素材の場所・タイトル・場面・曲順。巻ごとに変わる。

巻の側に同じキーを書けばジャンルの値を上書きできる（辞書は再帰的にマージ）。
"""
import io
import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENRE_DIR = os.path.join(ROOT, "genres")
VOLUME_DIR = os.path.join(ROOT, "volumes")


def _merge(base, over):
    out = dict(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def _expand(v):
    """文字列の ~ と $VAR を展開する。辞書・リストは再帰。"""
    if isinstance(v, str):
        return os.path.expandvars(os.path.expanduser(v))
    if isinstance(v, dict):
        return {k: _expand(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_expand(x) for x in v]
    return v


class Config(dict):
    """設定 + 巻ごとの派生パス。"""

    @property
    def work(self):
        """中間生成物の置き場。素材フォルダの隣に置く。

        セッション用の一時領域には置かない（セッションが終わると消えるため、
        Vol10 では manifest10.json を作り直す羽目になった）。
        """
        d = os.path.join(self["dir"], "_work")
        os.makedirs(d, exist_ok=True)
        return d

    def wpath(self, *parts):
        return os.path.join(self.work, *parts)

    @property
    def music_bed(self):
        """Read local regenerated audio first, then the retained archive copy.

        Output writers still use wpath(), so rebuilding never overwrites the
        archive merely because the local duplicate was removed.
        """
        local = os.path.join(self["dir"], "_work", "music_bed.wav")
        return local if os.path.isfile(local) else self.get("music_bed_source", local)

    @property
    def tracks_dir(self):
        return os.path.join(self["dir"], self.get("tracks_subdir", "楽曲"))

    @property
    def images_dir(self):
        return os.path.join(self["dir"], self.get("images_subdir", "画像"))

    @property
    def slug(self):
        return self.get("slug") or f"vol{self['volume']}"


def _load_genre(name, seen=None):
    """ジャンル設定を読む。`extends:` があれば親に重ねて返す。

    ★★2026年8月26日に足した。 3本目のシリーズ（Days of Old Japan）は
      Whispers と音の設計がほぼ同じで、違うのは環境音の濃さ・曲数・画風・帯だけ。
      継承が無いと**200行の調整済みの値を複製する**ことになり、しかも
      yaml で写すとコメント（＝なぜその値なのかの根拠）が全部落ちる。
      **差分だけ書けるほうが、後から読む人に正しく伝わる。**
    """
    seen = seen or []
    if name in seen:
        raise SystemExit("ジャンルの extends が循環しています: "
                         + " → ".join(seen + [name]))
    p = os.path.join(GENRE_DIR, f"{name}.yaml")
    if not os.path.exists(p):
        raise SystemExit(f"ジャンル設定が見つかりません: {p}")
    with open(p) as f:
        g = yaml.safe_load(f) or {}
    parent = g.pop("extends", None)
    if parent:
        return _merge(_load_genre(parent, seen + [name]), g)
    return g


def load(volume_file):
    """巻の設定ファイルを読み、genre: で指定されたジャンル設定に重ねて返す。"""
    path = volume_file
    if not os.path.exists(path):
        cand = os.path.join(VOLUME_DIR, volume_file)
        if not cand.endswith((".yaml", ".yml")):
            cand += ".yaml"
        path = cand
    if not os.path.exists(path):
        raise SystemExit(f"設定が見つかりません: {volume_file}")

    with open(path) as f:
        vol = yaml.safe_load(f) or {}

    genre = vol.get("genre")
    if not genre:
        raise SystemExit(f"{path} に genre: がありません")
    base = _load_genre(genre)

    cfg = Config(_expand(_merge(base, vol)))
    cfg["_path"] = path
    return cfg


def save_volume(cfg, key, value):
    """巻の設定ファイルに結果を書き戻す（select / order が確定した結果を入れる）。

    ★★2026年8月26日に作法を変えた。 それまでは `yaml.safe_dump` で**丸ごと書き直して**
      いたので、**巻のYAMLのコメントが全部消えていた**（＝なぜその値なのかの根拠が消える）。
      DOJ01 で実際に失った。長らく「既知だが未対応」だった不具合。

      直し方は、丸ごと書き直すのをやめて**該当キーの行だけ差し替える**こと。
      本文はテキストとして扱い、書き戻すキーのブロックを取り除いてから末尾に足す。
      これで人が書いた行は1文字も動かない。
    """
    path = cfg["_path"]
    src = io.open(path, encoding="utf-8").read()
    lines = src.splitlines(True)

    out, i = [], 0
    while i < len(lines):
        if re.match(rf"^{re.escape(key)}\s*:", lines[i]):
            i += 1
            # そのキーに属する行（字下げ・リスト・空行）を読み飛ばす。
            # 行頭が `#` や別のキーなら止まるので、後ろのコメントは残る。
            while i < len(lines) and (lines[i][:1] in " \t-" or not lines[i].strip()):
                i += 1
            continue
        out.append(lines[i])
        i += 1

    body = "".join(out).rstrip("\n")
    block = yaml.safe_dump({key: value}, allow_unicode=True, sort_keys=False, width=200)
    io.open(path, "w", encoding="utf-8").write(body + "\n\n" + block)
