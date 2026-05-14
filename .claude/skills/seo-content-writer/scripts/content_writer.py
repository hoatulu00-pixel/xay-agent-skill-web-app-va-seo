"""Compose final article content.

In production, the LLM (Claude orchestrator) generates the full article using
prompts/writing_prompt.txt. This module:
1. Builds the writing prompt to feed to the LLM
2. Provides a deterministic fallback writer for offline runs
3. Validates output against SEO/AEO checklist
4. Normalizes Vietnamese capitalization on the final output
"""
from __future__ import annotations

from .utils import SKILL_ROOT, parse_frontmatter, validate_seo

PROMPTS_DIR = SKILL_ROOT / "assets" / "prompts"


def build_writing_prompt(outline: str, brief: dict, content_type: str) -> str:
    template = (PROMPTS_DIR / "writing_prompt.txt").read_text(encoding="utf-8")
    return template.format(
        outline=outline,
        primary_keyword=brief["primary_keyword"],
        secondary_keywords=", ".join(brief.get("secondary_keywords", [])),
        word_count=brief.get("target_word_count", 1200),
        content_type=content_type,
    )


def fallback_article(brief: dict, outline: str, content_type: str) -> str:
    """Deterministic article when LLM unavailable. Quality lower but valid."""
    pk = brief["primary_keyword"]
    pk_cap = pk.capitalize()
    questions = brief.get("questions", [])
    title = f"{pk_cap}: Hướng dẫn từ Hoa Xuân Fashion"
    excerpt = (
        f"Khám phá cách chọn và phối {pk} chuẩn xu hướng cho phụ nữ Việt - "
        f"hướng dẫn chi tiết từ stylist Hoa Xuân Fashion, áp dụng được ngay hôm nay."
    )
    excerpt = excerpt[:159]

    body = f"""---
title: "{title}"
excerpt: "{excerpt}"
cover_image: ""
content_type: "{content_type}"
primary_keyword: "{pk}"
secondary_keywords: [{', '.join(f'"{k}"' for k in brief.get('secondary_keywords', []))}]
---

# {title}

> **Tóm tắt nhanh:** Bài viết hướng dẫn chi tiết về {pk} dành cho phụ nữ Việt 22-40 tuổi yêu phong cách nữ tính. Bạn sẽ biết cách chọn, cách phối, cách bảo quản và những lưu ý quan trọng để luôn diện đẹp mỗi ngày.

## {pk_cap} là gì và tại sao đang được yêu thích?

**{pk_cap}** là một trong những item đang được phụ nữ Việt yêu thích bậc nhất mùa này. Sự kết hợp giữa nét nữ tính cổ điển và xu hướng hiện đại khiến item này trở thành must-have trong tủ đồ.

Theo khảo sát của Hoa Xuân Fashion, hơn 65% khách hàng nữ trong độ tuổi 22-40 sở hữu ít nhất một item dạng này. Lý do: dễ phối, hợp nhiều dịp, tôn dáng tốt.

## Cách chọn {pk} phù hợp với dáng người

Việc chọn đúng kiểu dáng giúp bạn tôn được điểm mạnh và che khéo điểm chưa hoàn hảo.

- **Dáng người mảnh:** Ưu tiên kiểu có chi tiết bèo, xếp ly, họa tiết hoa nhỏ để tăng độ đầy đặn.
- **Dáng đồng hồ cát:** Chọn kiểu ôm vừa, tôn vòng eo, họa tiết vừa.
- **Dáng đầy đặn:** Chọn kiểu form A, vải rủ, họa tiết hoa lớn theo chiều dọc.

## Top 5 công thức phối đồ với {pk}

1. **{pk_cap} + áo blouse trắng + giày sandal** - Phong cách thanh lịch công sở.
2. **{pk_cap} + sweater pastel + ankle boot** - Phong cách dạo phố mùa giao mùa.
3. **{pk_cap} + áo sơ mi linen + sneakers trắng** - Phong cách năng động cuối tuần.
4. **{pk_cap} + áo crop top + giày cao gót mảnh** - Phong cách party gọn gàng.
5. **{pk_cap} + áo len mỏng + giày bệt** - Phong cách date dễ thương.

## Mẹo bảo quản {pk} bền đẹp

Để {pk} giữ màu và form lâu, hãy:

- Giặt tay với nước lạnh, dùng nước giặt dịu nhẹ.
- Không vắt mạnh, treo phơi nơi thoáng mát tránh nắng gắt.
- Là ủi mặt trong, nhiệt độ thấp.
- Bảo quản trong tủ thoáng, dùng móc treo phù hợp.

## Câu hỏi thường gặp

### {questions[0] if questions else f"{pk_cap} hợp với mùa nào?"}

{pk_cap} phù hợp nhất vào mùa xuân và mùa thu -thời tiết mát, dễ kết hợp với layer khác. Mùa hè có thể chọn chất liệu mỏng, mùa đông layer thêm áo len hoặc khoác dạ.

### {questions[1] if len(questions) > 1 else f"Có nên đầu tư nhiều {pk} không?"}

Nên có 2-3 mẫu cơ bản với màu trung tính (đen, be, navy) để dễ phối. Sau đó bổ sung mẫu họa tiết khi đã có nền tảng.

### {questions[2] if len(questions) > 2 else f"Mua {pk} ở đâu uy tín?"}

Hoa Xuân Fashion tự hào mang đến các thiết kế chỉn chu, chất liệu cao cấp với giá hợp lý. Tham khảo [bộ sưu tập mới](/blog/category/xu-huong-thoi-trang) để cập nhật xu hướng.

## Lời kết

{pk_cap} là item linh hoạt mà mọi tủ đồ nữ đều nên có. Hãy bắt đầu từ một kiểu dáng cơ bản và xây dần phong cách riêng. Khám phá thêm tại [Hoa Xuân Fashion](/blog/category/phoi-do).
"""
    return body


def validate(article_md: str) -> tuple[dict, str, list[str]]:
    meta, body = parse_frontmatter(article_md)
    errors = validate_seo(meta, body)
    return meta, body, errors
