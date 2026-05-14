"""Generate article outline from template + research brief.

This module returns a populated outline as Markdown. Real generation is delegated
to the LLM caller (Claude orchestrates by reading prompts/outline_prompt.txt).
This module's job is to load the right template + return the prompt string ready
for the LLM, OR to produce a fallback skeleton when used standalone.
"""
from __future__ import annotations

from pathlib import Path

from .utils import SKILL_ROOT, log

TEMPLATES_DIR = SKILL_ROOT / "assets" / "article_templates"
PROMPTS_DIR = SKILL_ROOT / "assets" / "prompts"


def load_template(content_type: str) -> str:
    fp = TEMPLATES_DIR / f"{content_type}.md"
    if not fp.exists():
        fp = TEMPLATES_DIR / "styling_guide.md"
    return fp.read_text(encoding="utf-8")


def build_outline_prompt(brief: dict, template_content: str) -> str:
    prompt = (PROMPTS_DIR / "outline_prompt.txt").read_text(encoding="utf-8")
    return prompt.format(
        template_content=template_content,
        primary_keyword=brief["primary_keyword"],
        secondary_keywords=", ".join(brief.get("secondary_keywords", [])),
        intent=brief.get("intent", "informational"),
        persona=brief.get("persona", ""),
        core_questions="\n- " + "\n- ".join(brief.get("questions", [])),
        word_count=brief.get("target_word_count", 1200),
    )


def fallback_outline(brief: dict) -> str:
    """Used when LLM not available — produces a minimal usable outline."""
    pk = brief["primary_keyword"]
    questions = brief.get("questions", [f"{pk} là gì?", f"Cách chọn {pk}?", f"Phối {pk} thế nào?"])
    return f"""# {pk.title()}: Hướng dẫn chi tiết và mẹo từ Hoa Xuân

> **Tóm tắt nhanh:** Bài viết tổng hợp những điều cần biết về {pk}, từ cách chọn đến mẹo phối đồ chuẩn xu hướng dành cho phụ nữ Việt 22-40 tuổi.

## {pk.title()} là gì?

(Định nghĩa và ý nghĩa)

## Tại sao {pk} đáng để đầu tư?

(Phân tích lợi ích)

## Cách chọn {pk} phù hợp với từng dáng người

(3-5 gợi ý theo dáng)

## Công thức phối đồ với {pk}

(3-5 công thức)

## Câu hỏi thường gặp

### {questions[0] if questions else pk}
(...)

### {questions[1] if len(questions) > 1 else f"Cách bảo quản {pk}?"}
(...)

### {questions[2] if len(questions) > 2 else f"{pk} hợp với mùa nào?"}
(...)

## Lời kết
"""
