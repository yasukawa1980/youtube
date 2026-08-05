"""画像をAPIで生成する。旧「ChatGPTにプロンプトを貼って1枚ずつ保存」の置き換え。

APIキーは ~/.config/bgmkit/env（600）か環境変数から読む。
このリポジトリにキーを書かないこと。読み込み順は 環境変数 → 設定ファイル。

生成サイズは 1536x1024（3:2）しか選べないので、16:9 に切り出してから保存する。
既存の巻の素材は 1672x941 だったので、横幅はわずかに落ちる（1536）。
本編は 2880x1620 に拡大してから 1920 に縮めるため、実用上の差は小さい。
"""
import base64
import json
import os
import time
import urllib.error
import urllib.request

from PIL import Image

ENV_FILE = os.path.expanduser("~/.config/bgmkit/env")
ENDPOINT = "https://api.openai.com/v1/images/generations"


def api_key():
    k = os.environ.get("OPENAI_API_KEY")
    if k:
        return k.strip()
    if os.path.exists(ENV_FILE):
        for line in open(ENV_FILE):
            line = line.strip()
            if line.startswith("OPENAI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(
        "APIキーが見つかりません。以下をご自身で実行してください（キーは私に見せないでください）:\n"
        "  mkdir -p ~/.config/bgmkit && "
        "printf 'OPENAI_API_KEY=キー\\n' > ~/.config/bgmkit/env && chmod 600 ~/.config/bgmkit/env")


def _post(payload, key, timeout=300):
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def _generate_one(prompt, cfg, key):
    icfg = cfg["images_api"]
    payload = {"model": icfg["model"], "prompt": prompt,
               "size": icfg["size"], "n": 1}
    for opt in ("quality", "background", "output_format"):
        if opt in icfg:
            payload[opt] = icfg[opt]

    last = None
    for attempt in range(icfg.get("retries", 3)):
        try:
            res = _post(payload, key)
            d = res["data"][0]
            if "b64_json" in d:
                return base64.b64decode(d["b64_json"])
            with urllib.request.urlopen(d["url"], timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:500]
            last = f"HTTP {e.code}: {body}"
            # 400番台は投げ直しても同じなので、レート制限以外は即座に諦める
            if e.code != 429 and 400 <= e.code < 500:
                raise SystemExit(f"APIがリクエストを拒否しました。\n{last}")
            time.sleep(5 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError) as e:
            last = str(e)
            time.sleep(5 * (attempt + 1))
    raise SystemExit(f"生成に失敗しました: {last}")


def _crop_169(data, path, anchor=0.5):
    """3:2 で返ってくる画像を 16:9 に切り出す。anchor は縦の取り位置（0=上）。"""
    import io
    im = Image.open(io.BytesIO(data)).convert("RGB")
    w, h = im.size
    want = int(round(w * 9 / 16))
    if h > want:
        top = int((h - want) * anchor)
        im = im.crop((0, top, w, top + want))
    im.save(path)
    return im.size


def run(cfg, only=None):
    prompts = cfg.get("image_prompts")
    if not prompts:
        raise SystemExit(
            "巻のYAMLに image_prompts がありません。場面と同じ数だけ並べてください。")
    scenes = cfg.get("scenes") or [""] * len(prompts)
    style = cfg.get("image_style", "")
    anchors = cfg.get("image_anchor") or [0.5] * len(prompts)

    key = api_key()
    out_dir = cfg.images_dir
    os.makedirs(out_dir, exist_ok=True)

    targets = range(len(prompts)) if only is None else [i - 1 for i in only]
    for i in targets:
        path = os.path.join(out_dir, f"{cfg.slug}_{i + 1:02d}.png")
        if os.path.exists(path) and not cfg.get("overwrite_images"):
            print(f"  {i + 1:02d} 既にあるので飛ばします: {os.path.basename(path)}")
            continue
        prompt = prompts[i]
        if style:
            prompt = f"{prompt}\n\n{style}"
        sc = scenes[i] if i < len(scenes) else ""
        print(f"  {i + 1:02d} 生成中 {sc}...", flush=True)
        data = _generate_one(prompt, cfg, key)
        size = _crop_169(data, path, anchors[i] if i < len(anchors) else 0.5)
        print(f"     → {os.path.basename(path)} {size[0]}x{size[1]}")

    print(f"\n書き出し先: {out_dir}")
    print("※ 看板・扁額・提灯の文字はAI特有の崩れ字になります。"
          "本編画像・エンドカード・サムネ背景の3つを必ず目で確認してください。")
