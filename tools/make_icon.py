# -*- coding: utf-8 -*-
"""Generate a desktop icon for the 408 shortcuts: dark badge with a serif "408"."""

import os

from PIL import Image, ImageDraw, ImageFont

ROOT = r"E:\CST\408"
DEST = os.path.join(ROOT, "408.ico")

INK = (26, 22, 19, 255)
PAPER = (246, 242, 233, 255)
ACC = (31, 95, 168, 255)

S = 512
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# 圆角深色底
pad = int(S * 0.045)
d.rounded_rectangle([pad, pad, S - pad, S - pad], radius=int(S * 0.19), fill=INK)

# 顶部细横线（呼应"档案/年鉴"的排版语言）
d.rounded_rectangle([int(S * 0.20), int(S * 0.205), int(S * 0.80), int(S * 0.235)],
                    radius=int(S * 0.015), fill=ACC)

# "408" 用衬线体
font = None
for fp, idx in ((r"C:\Windows\Fonts\simsun.ttc", 0), (r"C:\Windows\Fonts\georgia.ttf", None)):
    if not os.path.exists(fp):
        continue
    try:
        font = ImageFont.truetype(fp, int(S * 0.42), index=idx) if idx is not None \
            else ImageFont.truetype(fp, int(S * 0.42))
        break
    except Exception:
        continue
if font is None:
    font = ImageFont.load_default()

text = "408"
bbox = d.textbbox((0, 0), text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
d.text(((S - tw) / 2 - bbox[0], S * 0.53 - th / 2 - bbox[1]), text, font=font, fill=PAPER)

# 底部小字提示
try:
    small = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", int(S * 0.105), index=0)
except Exception:
    small = font
label = "真题 · 刷题"
bb = d.textbbox((0, 0), label, small)
d.text(((S - (bb[2] - bb[0])) / 2 - bb[0], S * 0.845 - bb[3] / 2), label,
       font=small, fill=(138, 127, 114, 255))

sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
img.save(DEST, format="ICO", sizes=sizes)
print("wrote", DEST, f"{os.path.getsize(DEST)/1024:.1f} KB")

# 同时留一张 PNG 便于预览/文档引用
png = os.path.join(ROOT, "408_icon.png")
img.resize((256, 256), Image.LANCZOS).save(png)
print("wrote", png)
