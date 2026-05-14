"""Design SEO-optimized OG thumbnail (1200x630) — keyword badge + title overlay."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OG_W, OG_H = 1200, 630

WIN_FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"
WIN_FONT_REG = "C:/Windows/Fonts/arial.ttf"

ROSE_PINK = (220, 38, 80)
WHITE = (255, 255, 255)
SHADOW = (0, 0, 0)


def _load_font(path: str, size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _wrap_lines(text: str, font, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip() if cur else w
        bbox = font.getbbox(test)
        if (bbox[2] - bbox[0]) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _cover_resize_crop(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    src_ratio = img.width / img.height
    dst_ratio = target_w / target_h
    if src_ratio > dst_ratio:
        new_h = target_h
        new_w = int(new_h * src_ratio)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def _gradient_overlay(w: int, h: int, start_y_frac: float = 0.30, max_alpha: int = 200) -> Image.Image:
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    start_y = int(h * start_y_frac)
    span = h - start_y
    for y in range(h):
        if y < start_y:
            a = 0
        else:
            t = (y - start_y) / span
            a = int(20 + (max_alpha - 20) * t)
        draw.line([(0, y), (w, y)], fill=(0, 0, 0, a))
    return overlay


def design(
    base_image: Path,
    title: str,
    primary_keyword: str,
    out_path: Path,
    brand: str = "Hoa Xuân Fashion",
) -> Path:
    """Generate 1200x630 OG-card with keyword badge + wrapped title + brand."""
    img = Image.open(base_image).convert("RGB")
    img = _cover_resize_crop(img, OG_W, OG_H)
    img = img.filter(ImageFilter.GaussianBlur(radius=1.2))

    img = Image.alpha_composite(
        img.convert("RGBA"),
        _gradient_overlay(OG_W, OG_H, start_y_frac=0.28, max_alpha=205),
    ).convert("RGB")

    draw = ImageDraw.Draw(img)

    badge_font = _load_font(WIN_FONT_BOLD, 28)
    kw_text = primary_keyword.upper()
    bbox = badge_font.getbbox(kw_text)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 22, 12
    bx, by = 40, 40
    draw.rounded_rectangle(
        [bx, by, bx + bw + pad_x * 2, by + bh + pad_y * 2 + 6],
        radius=10,
        fill=ROSE_PINK,
    )
    draw.text((bx + pad_x, by + pad_y), kw_text, font=badge_font, fill=WHITE)

    title_font = _load_font(WIN_FONT_BOLD, 58)
    max_w = OG_W - 80
    lines = _wrap_lines(title, title_font, max_w)
    if len(lines) > 4:
        lines = lines[:4]
        last = lines[-1].rstrip(".")
        lines[-1] = last + "..."
    line_h = title_font.getbbox("Ag")[3] + 14
    block_h = line_h * len(lines)
    start_y = OG_H - block_h - 90

    for i, line in enumerate(lines):
        y = start_y + i * line_h
        draw.text((42, y + 3), line, font=title_font, fill=SHADOW)
        draw.text((42, y + 2), line, font=title_font, fill=SHADOW)
        draw.text((40, y), line, font=title_font, fill=WHITE)

    brand_font = _load_font(WIN_FONT_BOLD, 24)
    bbox = brand_font.getbbox(brand)
    bw2 = bbox[2] - bbox[0]
    draw.text((OG_W - bw2 - 40, OG_H - 48), brand, font=brand_font, fill=WHITE)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "JPEG", quality=88, optimize=True)
    return out_path
