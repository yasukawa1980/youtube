"""設定の2層読み込み。

  genres/<ジャンル>.yaml  … 音の設計・映像の作り・サムネの型。ジャンルで固定。
  volumes/<巻>.yaml       … 素材の場所・タイトル・場面・曲順。巻ごとに変わる。

巻の側に同じキーを書けばジャンルの値を上書きできる（辞書は再帰的にマージ）。
"""
import os

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
    def tracks_dir(self):
        return os.path.join(self["dir"], self.get("tracks_subdir", "楽曲"))

    @property
    def images_dir(self):
        return os.path.join(self["dir"], self.get("images_subdir", "画像"))

    @property
    def slug(self):
        return self.get("slug") or f"vol{self['volume']}"


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
    gpath = os.path.join(GENRE_DIR, f"{genre}.yaml")
    if not os.path.exists(gpath):
        raise SystemExit(f"ジャンル設定が見つかりません: {gpath}")
    with open(gpath) as f:
        base = yaml.safe_load(f) or {}

    cfg = Config(_expand(_merge(base, vol)))
    cfg["_path"] = path
    return cfg


def save_volume(cfg, key, value):
    """巻の設定ファイルに結果を書き戻す（order コマンドが曲順を確定するときに使う）。

    コメントは保持されないので、書き戻す対象は order / tracks のような
    自動で決まるキーに限る。
    """
    path = cfg["_path"]
    with open(path) as f:
        vol = yaml.safe_load(f) or {}
    vol[key] = value
    with open(path, "w") as f:
        yaml.safe_dump(vol, f, allow_unicode=True, sort_keys=False, width=200)
