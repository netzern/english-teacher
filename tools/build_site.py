"""Build the standalone website (GitHub Pages) into docs/.

    python tools/build_site.py

docs/ gets: index.html (the page wrapped in a full document + app manifest),
content.json, agents.json, audio/, manifest.webmanifest and app icons.
"""
import re
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"
NAME = "המורה שלי לאנגלית"


def icon(size, maskable=False):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = 0 if maskable else int(size * 0.04)
    d.rounded_rectangle([pad, pad, size - pad, size - pad], radius=int(size * (0 if maskable else 0.22)), fill="#2D5A4E")
    edge = int(size * 0.06)
    d.rounded_rectangle([pad + edge, pad + edge, size - pad - edge, size - pad - edge], radius=int(size * 0.14), outline="#A8784E", width=int(size * 0.035))
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", int(size * 0.30))
    except OSError:
        font = ImageFont.load_default()
    text = "ABC"
    box = d.textbbox((0, 0), text, font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    d.text(((size - w) / 2 - box[0], size * 0.50 - h / 2 - box[1]), text, font=font, fill="#F4F8F2")
    r = size * 0.075
    cx, cy = size * 0.72, size * 0.27
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#FF7A3D")
    return img


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "audio").mkdir(parents=True)
    page = (ROOT / "english-teacher.html").read_text(encoding="utf-8")
    page = re.sub(r"^<title>.*?</title>\s*", "", page, count=1)
    head = f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{NAME}</title>
<meta name="description" content="מורה לאנגלית לילדים: בונים דמות, לומדים מילים ודקדוק, ומדברים עם המורה.">
<meta name="theme-color" content="#2D5A4E">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="apple-touch-icon" href="icon-192.png">
<style>:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
</head>
<body>
"""
    (OUT / "index.html").write_text(head + page + "\n</body>\n</html>\n", encoding="utf-8")
    for f in ("content.json", "agents.json"):
        shutil.copy(ROOT / f, OUT / f)
    for f in (ROOT / "audio").iterdir():
        if f.suffix in (".mp3", ".json"):
            shutil.copy(f, OUT / "audio" / f.name)
    icon(192).save(OUT / "icon-192.png")
    icon(512).save(OUT / "icon-512.png")
    icon(512, maskable=True).save(OUT / "icon-maskable.png")
    (OUT / "manifest.webmanifest").write_text("""{
  "name": "%s",
  "short_name": "המורה שלי",
  "lang": "he",
  "dir": "rtl",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "background_color": "#E7F3EF",
  "theme_color": "#2D5A4E",
  "icons": [
    {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
    {"src": "icon-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}
""" % NAME, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print("built", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
