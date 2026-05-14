"""Expand 1 seed topic into N diverse sub-topics for batch publishing."""
from __future__ import annotations

from . import keyword_research
from .utils import log

# Templates spread across 7 content_types so batch produces variety
TOPIC_TEMPLATES = [
    "cách phối {seed} đẹp",                    # styling_guide
    "top kiểu {seed} hot trend 2026",          # listicle
    "xu hướng {seed} mới nhất",                # trend_report
    "cách chọn {seed} phù hợp dáng người",     # how_to
    "{seed} mặc với áo gì đẹp",                # styling_guide
    "{seed} cho người tròn trịa",              # how_to
    "review chất liệu {seed}",                 # product_review
    "cách bảo quản {seed} bền đẹp",            # care_guide
    "{seed} đi đám cưới sang trọng",           # styling_guide
    "{seed} đi làm công sở",                   # styling_guide
    "{seed} mùa hè mát mẻ",                    # trend_report
    "phong cách vintage với {seed}",           # trend_report
    "câu chuyện thiết kế {seed}",              # behind_scenes
]


def expand(seed: str, n: int = 10) -> list[str]:
    """Generate N diverse sub-topics from a single seed."""
    seed = seed.strip()
    if not seed:
        return []

    seen: set[str] = set()
    out: list[str] = []

    def _add(t: str) -> None:
        norm = t.strip().lower()
        if norm and norm not in seen and len(norm) > 5 and norm != seed.lower():
            seen.add(norm)
            out.append(t.strip())

    try:
        research = keyword_research.research(seed)
        for s in research.get("all_suggestions", [])[:8]:
            _add(s)
    except Exception as e:  # noqa: BLE001
        log.warning("topic_expander research fallback: %s", e)

    real_count = len(out)
    log.info("Got %d real autocomplete topics, filling rest with templates", real_count)

    for tpl in TOPIC_TEMPLATES:
        if len(out) >= n:
            break
        _add(tpl.format(seed=seed))

    return out[:n]


if __name__ == "__main__":
    import json
    import sys

    seed = sys.argv[1] if len(sys.argv) > 1 else "chân váy hoa"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    print(json.dumps(expand(seed, n), ensure_ascii=False, indent=2))
