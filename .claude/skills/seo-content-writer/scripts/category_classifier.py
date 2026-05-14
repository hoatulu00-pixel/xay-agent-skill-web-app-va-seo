"""Map topic + intent -> content_type -> category_id (cached in settings)."""
from __future__ import annotations

from .utils import load_settings, log

CONTENT_TYPE_KEYWORDS = {
    "care_guide": ["giặt", "bảo quản", "vệ sinh", "ủi", "treo", "gấp", "phơi"],
    "product_review": ["review", "đánh giá", "có tốt", "có nên mua"],
    "trend_report": ["xu hướng", "trend", "mùa xuân", "mùa hè", "mùa thu", "mùa đông"],
    "behind_scenes": ["câu chuyện", "behind", "thương hiệu", "hoa xuân story"],
    "how_to": ["cách", "làm sao", "hướng dẫn", "tự làm"],
    "listicle": ["top ", " mẫu", " kiểu", " loại", "must have"],
    "styling_guide": ["phối", "kết hợp", "match", "với"],
}


def classify_content_type(topic: str, keywords: list[str]) -> str:
    text = (topic + " " + " ".join(keywords)).lower()
    for ctype, kws in CONTENT_TYPE_KEYWORDS.items():
        if any(k in text for k in kws):
            log.info("Content type: %s", ctype)
            return ctype
    log.info("Content type: styling_guide (default for fashion blog)")
    return "styling_guide"


def get_category_id(content_type: str) -> int | None:
    settings = load_settings()
    cat_id = settings.get("category_map", {}).get(content_type)
    if cat_id is None:
        log.warning("category_map[%s] is null. Run: python -m scripts.seed_categories", content_type)
    return cat_id
