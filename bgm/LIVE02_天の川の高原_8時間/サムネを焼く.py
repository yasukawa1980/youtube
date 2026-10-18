"""2026/10/11 LIVE02（8時間ライブ・天の川の高原）のサムネ。WAVE09_v2 の設定を読み、絵と題字だけ替える。
★絵はWAVE09の本編第1場面「宵の天の川」（WAVE09のサムネ専用画と別にして、168pxで見分けがつくように）。
★焼き方は _ABテスト_20261008/焼く.py の variant（太い明朝W6）をそのまま使う。bgmkit は触らない。
"""
import importlib.util, os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
BGM = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("ab", os.path.join(BGM, "_ABテスト_20261008", "焼く.py"))
ab = importlib.util.module_from_spec(spec); spec.loader.exec_module(ab)

cfg = ab.load("wave09_v2")
cfg["background"] = os.path.join(BGM, "WAVE09_天の川の高原", "画像", "wave09_01_宵の天の川.png")
cfg["thumb_sub"] = "8時間ライブ｜1Hz デルタ波 バイノーラルビート"
plan = dict(lines=["朝まで8時間", "天の川の高原"], family="jp", index=ab.W6)
out = os.path.join(HERE, "live02_サムネ.png")
ab.variant(cfg, plan, out)
ab.variant(cfg, plan, os.path.join(HERE, "_空白版.png"), blank=True)
print("168px 題字と地の差:", round(ab.contrast168(out, os.path.join(HERE, "_空白版.png"))))
os.remove(os.path.join(HERE, "_空白版.png"))
im = Image.open(out).convert("RGB"); im.save(os.path.join(HERE, "live02_サムネ.jpg"), quality=92)
im.resize((168, 95), Image.LANCZOS).save(os.path.join(HERE, "live02_サムネ_168px.png"))
print(os.path.getsize(os.path.join(HERE, "live02_サムネ.jpg")))
