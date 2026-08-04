"""Genera assets/logo.png y assets/icon.ico para PhishScope (uso puntual)."""

import os

from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")
ICONS = os.path.join(ASSETS, "icons")

SIZE = 512
ACCENT = (56, 189, 248, 255)       # #38bdf8
ACCENT_SOFT = (125, 211, 252, 255) # #7dd3fc
GRAD_TOP = (13, 20, 32)            # #0d1420
GRAD_BOTTOM = (22, 36, 62)         # #16243e
RING = (56, 189, 248, 120)


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def gradient_bg(size, top, bottom):
    img = Image.new("RGBA", (size, size))
    px = img.load()
    for y in range(size):
        t = y / (size - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(size):
            px[x, y] = (r, g, b, 255)
    return img


def rounded_mask(size, radius):
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return mask


def draw_logo():
    img = gradient_bg(SIZE, GRAD_TOP, GRAD_BOTTOM)
    mask = rounded_mask(SIZE, radius=110)
    img.putalpha(mask)

    d = ImageDraw.Draw(img)

    # Anillo interior sutil
    d.rounded_rectangle([14, 14, SIZE - 15, SIZE - 15], radius=100,
                        outline=RING, width=4)

    # ---- Símbolo: lupa con check ----
    lens_cx, lens_cy, lens_r = 246, 224, 108

    # Cristal de la lupa (relleno translúcido)
    fill_lens = (56, 189, 248, 40)
    d.ellipse([lens_cx - lens_r, lens_cy - lens_r,
               lens_cx + lens_r, lens_cy + lens_r], outline=ACCENT,
              width=22, fill=fill_lens)

    # Mango de la lupa (hacia abajo-derecha)
    d.line([lens_cx + lens_r - 28, lens_cy + lens_r - 28,
            362, 400], fill=ACCENT, width=38, joint="curve")
    d.ellipse([350, 388, 374, 412], fill=ACCENT)

    # Check dentro del cristal
    d.line([202, 232, 240, 270], fill=ACCENT_SOFT, width=30, joint="curve")
    d.line([240, 270, 302, 196], fill=ACCENT_SOFT, width=30, joint="curve")

    # Punto de mira central (subtle crosshair)
    d.line([lens_cx, lens_cy - 12, lens_cx, lens_cy + 12],
           fill=(255, 255, 255, 140), width=5)
    d.line([lens_cx - 12, lens_cy, lens_cx + 12, lens_cy],
           fill=(255, 255, 255, 140), width=5)

    return img


def main():
    os.makedirs(ASSETS, exist_ok=True)
    os.makedirs(ICONS, exist_ok=True)

    logo = draw_logo()

    logo_png = os.path.join(ASSETS, "logo.png")
    logo.resize((256, 256), Image.LANCZOS).save(logo_png)

    icon_png = os.path.join(ICONS, "logo.png")
    logo.save(icon_png)

    ico_path = os.path.join(ASSETS, "icon.ico")
    logo.save(ico_path, format="ICO", sizes=[(16, 16), (24, 24), (32, 32),
                                             (48, 48), (64, 64), (128, 128),
                                             (256, 256)])
    print("OK:", logo_png, icon_png, ico_path)


if __name__ == "__main__":
    main()
