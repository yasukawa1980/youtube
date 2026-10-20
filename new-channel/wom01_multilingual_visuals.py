"""English-only picture compositions for the common EP001 picture track."""
import json
import os
import textwrap
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1920, 1080
BG, IVORY, GOLD, MUTED = "#0c1820", "#f4efdf", "#d8b575", "#b0bfc3"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
TITLE = "/System/Library/Fonts/Supplemental/Georgia.ttf"


def font(size, serif=False):
    return ImageFont.truetype(TITLE if serif else FONT, size)


def put(draw, xy, value, size=42, color=IVORY, serif=False):
    assert not any("\u3040" <= c <= "\u30ff" or "\u4e00" <= c <= "\u9fff" for c in value), value
    draw.text(xy, value, font=font(size, serif), fill=color)


def fit_text(draw, xy, value, width, size=50, color=IVORY, serif=False):
    while draw.textlength(value, font=font(size, serif)) > width and size > 30:
        size -= 1
    assert draw.textlength(value, font=font(size, serif)) <= width, value
    put(draw, xy, value, size, color, serif)


def bars(im, heading, label, footer):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 164), fill=BG)
    d.rectangle((0, 970, W, H), fill=BG)
    put(d, (100, 32), "WORLDS OF MYSTERY  /  EP001", 28, GOLD)
    fit_text(d, (100, 87), heading, 1720, 54, serif=True)
    width = d.textlength(label, font=font(34)) + 40
    d.rounded_rectangle((1820-width, 25, 1820, 77), 10, fill="#243942")
    put(d, (1840-width, 30), label, 34, GOLD)
    fit_text(d, (100, 996), footer, 1720, 31, MUTED)
    return im


def card_image(seg, key):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    data = {
        "roles": [("Anubis", "Reads the scale"), ("Thoth", "Records the result"), ("Osiris", "Receives the dead")],
        "journey": [("Prepare the body", "Preservation and ritual"),
                    ("Support the journey", "Spells and images"), ("Pass the test", "The weighing of the heart")],
        "timeline": [("Middle Kingdom", "Royal relief: c. 1981–1952 BCE"),
                     ("Third Intermediate Period", "Nauny's papyrus: c. 1050 BCE"),
                     ("Roman period", "Cartonnage fragment: 100–300 CE")],
        "evidence": [("Museum objects", "Photographs of surviving evidence"),
                     ("Interpretation", "What the sources explain"),
                     ("Reconstructions", "Images that help us picture the past")],
        "human_work": [("Human hands", "Preparing the dead for burial"),
                       ("Divine protection", "Stories that gave the rites meaning")],
        "passage": [("A frightening test", "The possibility of failure"),
                    ("A protective purpose", "The hope of completing the journey")],
        "protect": [("Guard", "Watching over tombs"), ("Protect", "Taking part in funerary rites"),
                    ("Weigh", "Overseeing the scale")],
        "maat": [("Maat", "Order and right conduct"),
                 ("In Nauny's papyrus", "A small goddess wearing a feather")],
        "credits": [("Museum images", "The Metropolitan Museum of Art / Open Access (CC0)"),
                    ("English narration", "Kokoro / Heart (af_heart) / synthetic speech"),
                    ("Reconstructions and music", "AI-generated images / original ambient score")],
    }
    if key == "balance":
        d.line((960, 280, 960, 790), fill=GOLD, width=8)
        d.line((510, 420, 1410, 420), fill=GOLD, width=8)
        d.line((820, 790, 1100, 790), fill=GOLD, width=8)
        for x in (540, 1380):
            d.line((x, 420, x-140, 660), fill=GOLD, width=4)
            d.line((x, 420, x+140, 660), fill=GOLD, width=4)
            d.arc((x-150, 590, x+150, 770), 0, 180, fill=GOLD, width=6)
        d.ellipse((475, 560, 550, 635), fill="#b66061")
        d.ellipse((530, 560, 605, 635), fill="#b66061")
        d.polygon([(475, 610), (605, 610), (540, 695)], fill="#b66061")
        d.line((1350, 690, 1415, 535), fill=IVORY, width=5)
        for i in range(10):
            x, y = 1357+i*5, 669-i*12
            d.line((x-28, y-8, x+28, y-18), fill=IVORY, width=4)
        put(d, (435, 835), "The heart", 48)
        put(d, (1180, 835), "A symbol of Maat", 48)
    else:
        rows = data[key]
        for i, (title, subtitle) in enumerate(rows):
            y = 215 + i * (705 // len(rows))
            height = min(195, 640 // len(rows))
            d.rounded_rectangle((130, y, 1790, y+height), 22, fill="#1a303a", outline="#42535b", width=2)
            put(d, (175, y+50), f"{i+1:02}", 60, GOLD)
            fit_text(d, (320, y+28), title, 1400, 51, serif=True)
            fit_text(d, (320, y+103), subtitle, 1400, 40, MUTED)
    footer = ("Full credits, sources and terms in the description" if key == "credits"
              else seg["caption"])
    return bars(im, seg["heading"], "Production credits" if key == "credits" else "Concept diagram", footer)


def main():
    root, source = Path(os.environ["WOM_EPISODE_ROOT"]), Path(os.environ["WOM_SOURCE_ROOT"])
    content = json.loads((root / "records/content_en.json").read_text())
    museum = {str(m["object_id"]): m for m in json.loads((source / "records/museum_assets.json").read_text())}
    out = root / "assets/composed_en"
    out.mkdir(parents=True, exist_ok=True)
    # Keep diagrams to at most two appearances, show the referred object more often.
    overrides = {
        "N10": ["linen", "human_work"], "N11": ["met_545547", "met_545547_detail"],
        "N14": ["balance", "met_557657_scale"], "N15": ["maat", "met_548344_maat"],
        "N19": ["met_557657_scale", "met_557657_osiris"],
        "N20": ["passage", "hero"], "N23": ["met_552247", "met_552247_detail"],
        "N24": ["met_547871", "met_547871_detail"], "N27": ["protect", "hero"],
    }
    generated = {"hero": "01_anubis_chamber.png", "nile": "02_nile.png",
                 "linen": "03_linen.png", "archive": "04_archive.png"}
    # Pixel rectangles were visually checked against original source JPGs.
    crops = {
        "met_557657_scale": (2000, 1250, 3020, 2220),
        "met_557657_osiris": (950, 1300, 2130, 2990),
        "met_548344_detail": (.10, .37, .97, .90),
        "met_548344_maat": (.24, .46, .63, .89),
        "met_544075_detail": (.20, .03, .97, .92),
        "met_552247": (.04, .18, .96, .84),
        "met_552247_detail": (.35, .20, .94, .85),
        "met_570223": (.30, .24, .68, .77),
        "met_547871_detail": (0, 0, 1, .70),
        "met_544206_detail": (.34, .05, .93, .96),
        "met_557830_detail": (.08, .25, .91, .91),
    }
    manifest, uses = [], Counter()
    for seg in content["segments"]:
        for j, key in enumerate(overrides.get(seg["id"], seg["visuals"])):
            name = f'{seg["id"]}_{j:02}_{key}'
            record = {"segment_id": seg["id"], "key": key, "file": f"assets/composed_en/{name}.png"}
            if key.startswith("met_") or key in generated:
                im = Image.new("RGB", (W, H), BG)
                if key in generated:
                    src = Image.open(source / "assets/generated" / generated[key]).convert("RGB")
                    label, footer = "AI reconstruction", seg["caption"]
                    record["source"] = f"assets/generated/{generated[key]}"
                else:
                    oid = key.split("_")[1]
                    src = Image.open(source / "assets/museum" / f"met_{oid}.jpg").convert("RGB")
                    crop = crops.get(key)
                    if crop is None and key.endswith("_detail"):
                        crop = (.12, .06, .90, .94)
                    if crop:
                        box = (tuple(round(v*(src.width if i % 2 == 0 else src.height)) for i, v in enumerate(crop))
                               if max(crop) <= 1 else crop)
                        record["crop_pixels"] = box
                        src = src.crop(box)
                    label = "Facsimile (copy on paper)" if oid == "557830" else "Museum object"
                    footer = f'The Metropolitan Museum of Art / {museum[oid]["object_number"]} / Open Access (CC0)'
                    record["source"] = f"assets/museum/met_{oid}.jpg"
                art = ImageOps.contain(src, (1720, 800), Image.Resampling.LANCZOS)
                im.paste(art, ((W-art.width)//2, 166+(800-art.height)//2))
                bars(im, seg["heading"], label, footer)
                record["display_size"] = art.size
                record["label"] = label
            else:
                uses[key] += 1
                im = card_image(seg, key)
                record["label"] = "Concept diagram" if key != "credits" else "Production credits"
            im.save(out / f"{name}.png")
            preview = im.copy()
            preview.thumbnail((1280, 720))
            preview_dir = root / "review"
            preview_dir.mkdir(exist_ok=True)
            preview.save(preview_dir / f"{name}.jpg", quality=85)
            manifest.append(record)
    assert max(uses.values()) <= 2, uses
    (root / "records/visual_manifest.json").write_text(json.dumps({
        "language": "en", "subtitles_burned_in": False,
        "diagram_use_counts": dict(uses), "shots": manifest,
        "papyrus_557657_review": "Native source checked. Scale crop includes balance beam, pans and kneeling Anubis; second crop shows Osiris.",
    }, ensure_ascii=False, indent=2)+"\n")
    # Native type and existing AI artwork; no new image generation.
    im = ImageOps.fit(Image.open(source / "assets/generated/01_anubis_chamber.png").convert("RGB"), (W, H))
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shade).rectangle((0, 0, 1100, H), fill=(5, 13, 23, 190))
    im = Image.alpha_composite(im.convert("RGBA"), shade).convert("RGB")
    d = ImageDraw.Draw(im)
    put(d, (110, 165), "ANUBIS", 165, IVORY, True)
    put(d, (115, 410), "Judge or Protector?", 88, GOLD, True)
    put(d, (120, 575), "Who decides at the scale?", 49)
    put(d, (120, 920), "WORLDS OF MYSTERY", 32, GOLD)
    im.save(root / "deliverables/EP001_thumbnail_en.jpg", quality=94)
    im.thumbnail((1280, 720))
    im.save(root / "review/wom01_サムネ.jpg", quality=88)
    print(f"{len(manifest)} English compositions ready; diagrams {dict(uses)}", flush=True)


if __name__ == "__main__":
    main()
