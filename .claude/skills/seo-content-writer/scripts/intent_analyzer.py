"""Heuristic intent + persona analysis (no LLM call required)."""
from __future__ import annotations

from .utils import log

INFORMATIONAL = ["là gì", "tại sao", "cách", "làm sao", "hướng dẫn", "lịch sử", "ý nghĩa"]
COMMERCIAL = ["review", "đánh giá", "có tốt", "có nên", "so sánh", "tốt nhất", "top "]
TRANSACTIONAL = ["mua", "giá", "khuyến mãi", "shop", "nơi bán", "ở đâu", "đặt"]
NAVIGATIONAL = ["hoa xuân", "fanpage", "website", "store"]


def analyze(topic: str, keywords: list[str], questions: list[str]) -> dict:
    text = " ".join([topic, *keywords, *questions]).lower()

    if any(t in text for t in NAVIGATIONAL):
        intent = "navigational"
    elif any(t in text for t in TRANSACTIONAL):
        intent = "transactional"
    elif any(t in text for t in COMMERCIAL):
        intent = "commercial"
    elif any(t in text for t in INFORMATIONAL):
        intent = "informational"
    else:
        intent = "informational"

    persona_map = {
        "informational": "Phụ nữ 22-40 tuổi đang tìm thông tin/hướng dẫn để tự tin diện đẹp.",
        "commercial": "Phụ nữ đang cân nhắc mua sản phẩm, tìm review/so sánh để ra quyết định.",
        "transactional": "Phụ nữ đã sẵn sàng mua, tìm shop/giá/khuyến mãi.",
        "navigational": "Khách quen của Hoa Xuân, tìm thông tin trực tiếp về thương hiệu.",
    }

    result = {
        "intent": intent,
        "persona": persona_map[intent],
    }
    log.info("Intent: %s", intent)
    return result
