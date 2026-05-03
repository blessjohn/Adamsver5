"""
Server-side membership ID card as PNG (reliable for bulk-imported users and when
browser canvas export fails).
"""

from __future__ import annotations

import os
import re
from io import BytesIO

from django.conf import settings
from PIL import Image, ImageDraw, ImageFont

from .utils import generate_qr_code_live, stored_file_is_missing

_FONT_CACHE: dict[int, ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}


def _sans_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]
    candidates = [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            try:
                f = ImageFont.truetype(path, size)
                _FONT_CACHE[size] = f
                return f
            except OSError:
                continue
    f = ImageFont.load_default()
    _FONT_CACHE[size] = f
    return f


def _text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _wrap_lines(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    words = (text or "").split()
    if not words:
        return [""]
    lines: list[str] = []
    cur: list[str] = []
    for w in words:
        trial = " ".join(cur + [w])
        if _text_width(draw, trial, font) <= max_width:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines or [""]


def _safe_photo_path(user) -> str | None:
    if stored_file_is_missing(user.photo):
        return None
    raw = str(user.photo).strip()
    if not raw or raw == "None":
        return None
    rel = raw if raw.startswith("media/") else f"media/{raw}"
    full = os.path.normpath(os.path.join(str(settings.BASE_DIR), rel.replace("/", os.sep)))
    media_root = os.path.normpath(str(settings.MEDIA_ROOT))
    if not full.startswith(media_root) or not os.path.isfile(full):
        return None
    return full


def build_id_card_png_bytes(user) -> bytes:
    """Build a PNG image (RGB) for the membership card; returns raw bytes."""
    W, H = 420, 560
    im = Image.new("RGB", (W, H), "#f0f4fb")
    draw = ImageDraw.Draw(im)
    draw.rectangle([0, 0, W, 96], fill="#0d6efd")

    font_title = _sans_font(15)
    font_sub = _sans_font(12)
    font_body = _sans_font(16)
    font_small = _sans_font(13)
    font_id = _sans_font(18)

    title = "Association of Doctors and Medical Students"
    sub = "(ADAMS) — Membership identification"
    y = 8
    for line in _wrap_lines(title, font_title, W - 24, draw):
        tw = _text_width(draw, line, font_title)
        draw.text((W // 2 - tw // 2, y), line, fill="white", font=font_title)
        y += 18
    tws = _text_width(draw, sub, font_sub)
    draw.text((W // 2 - tws // 2, y + 2), sub, fill="#e7f1ff", font=font_sub)

    y0 = 112
    cx = W // 2
    photo_path = _safe_photo_path(user)
    ph = 108
    if photo_path:
        try:
            pimg = Image.open(photo_path).convert("RGBA")
            pimg = pimg.resize((ph, ph), Image.Resampling.LANCZOS)
            mask = Image.new("L", (ph, ph), 0)
            mdraw = ImageDraw.Draw(mask)
            mdraw.ellipse([0, 0, ph - 1, ph - 1], fill=255)
            rim = Image.new("RGBA", (ph + 8, ph + 8), (0, 0, 0, 0))
            rim.paste(pimg, (4, 4), mask)
            draw.ellipse([cx - ph // 2 - 4, y0 - 4, cx + ph // 2 + 4, y0 + ph + 4], outline="#0d6efd", width=3)
            im.paste(rim, (cx - (ph + 8) // 2, y0 - 0), rim)
        except Exception:
            draw.ellipse([cx - ph // 2, y0, cx + ph // 2, y0 + ph], fill="#dee2e6", outline="#0d6efd", width=3)
            tw = _text_width(draw, "No photo", font_small)
            draw.text((cx - tw // 2, y0 + ph // 2 - 6), "No photo", fill="#6c757d", font=font_small)
    else:
        draw.ellipse([cx - ph // 2, y0, cx + ph // 2, y0 + ph], fill="#e9ecef", outline="#0d6efd", width=3)
        msg = "Photo pending"
        tw = _text_width(draw, msg, font_small)
        draw.text((cx - tw // 2, y0 + ph // 2 - 6), msg, fill="#6c757d", font=font_small)

    name_parts = [
        (user.first_name or "").strip(),
        (user.middle_name or "").strip(),
        (user.last_name or "").strip(),
    ]
    display_name = " ".join(p for p in name_parts if p) or user.username
    twn = _text_width(draw, display_name, font_body)
    draw.text((cx - twn // 2, y0 + ph + 18), display_name, fill="#212529", font=font_body)

    y2 = y0 + ph + 52
    draw.line([24, y2, W - 24, y2], fill="#ced4da", width=1)
    y2 += 14
    draw.text((24, y2), "CATEGORY", fill="#6c757d", font=font_small)
    y2 += 20
    cat = user.get_category_display()
    for line in _wrap_lines(cat, font_body, W - 48, draw):
        draw.text((24, y2), line, fill="#212529", font=font_body)
        y2 += 22

    y2 += 8
    draw.line([24, y2, W - 24, y2], fill="#ced4da", width=1)
    y2 += 14
    draw.text((24, y2), "MEMBERSHIP ID NO.", fill="#6c757d", font=font_small)
    y2 += 22
    mid = user.display_membership_id or ""
    draw.text((24, y2), mid, fill="#0d6efd", font=font_id)

    try:
        qr_buf = generate_qr_code_live(user)
        qr_im = Image.open(qr_buf).convert("RGBA").resize((112, 112), Image.Resampling.LANCZOS)
        qx, qy = W - 112 - 20, H - 112 - 20
        im.paste(qr_im, (qx, qy), qr_im)
        cap = "Verification QR"
        twc = _text_width(draw, cap, font_small)
        draw.text((qx + 56 - twc // 2, H - 22), cap, fill="#6c757d", font=font_small)
    except Exception:
        pass

    out = BytesIO()
    im.save(out, format="PNG", optimize=True)
    return out.getvalue()


def id_card_png_filename(user) -> str:
    base = user.display_membership_id or f"ADAMS_user_{user.pk}"
    safe = re.sub(r"[^\w\-.]+", "_", base, flags=re.ASCII)
    return f"{safe}.png"
