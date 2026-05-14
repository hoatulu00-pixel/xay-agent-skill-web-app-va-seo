# Content Types — 7 dạng bài + mapping category

| Content Type | Category trên web | Khi dùng | Template file |
|---|---|---|---|
| `how_to` | Hướng dẫn & Mẹo | Intent: "cách", "làm sao", "hướng dẫn" | `assets/article_templates/how_to.md` |
| `listicle` | Phối đồ | Intent: "top X", "X cách", "X mẫu" | `assets/article_templates/listicle.md` |
| `trend_report` | Xu hướng thời trang | Intent: "xu hướng", "trend", "mùa X" | `assets/article_templates/trend_report.md` |
| `styling_guide` | Phối đồ | Intent: "phối với", "match", "kết hợp" | `assets/article_templates/styling_guide.md` |
| `product_review` | Review sản phẩm | Intent: "review", "đánh giá", "có tốt không" | `assets/article_templates/product_review.md` |
| `care_guide` | Bảo quản & Chăm sóc | Intent: "giặt", "bảo quản", "vệ sinh" | `assets/article_templates/care_guide.md` |
| `behind_scenes` | Câu chuyện thương hiệu | Intent: "câu chuyện", "behind", "Hoa Xuân" | `assets/article_templates/behind_scenes.md` |

## Logic phân loại (`category_classifier.py`)

```
def classify(topic: str, intent: str, keywords: list[str]) -> str:
    text = f"{topic} {' '.join(keywords)}".lower()
    if any(k in text for k in ["cách", "làm sao", "hướng dẫn", "tự làm"]): return "how_to"
    if any(k in text for k in ["giặt", "bảo quản", "vệ sinh", "ủi", "treo"]): return "care_guide"
    if any(k in text for k in ["review", "đánh giá", "có tốt", "có nên mua"]): return "product_review"
    if any(k in text for k in ["xu hướng", "trend", "mùa xuân", "mùa hè", "thu đông"]): return "trend_report"
    if any(k in text for k in ["câu chuyện", "behind", "hoa xuân", "thương hiệu"]): return "behind_scenes"
    if any(k in text for k in ["top ", " mẫu", " kiểu", " loại"]): return "listicle"
    if any(k in text for k in ["phối", "kết hợp", "match", "với"]): return "styling_guide"
    return "styling_guide"  # default cho fashion blog
```

Default fallback là `styling_guide` vì brand chuyên thời trang nữ nên đa số topic sẽ về phối đồ.

## Cấu trúc category trên web app

`scripts/seed_categories.py` tạo 7 category với:
- `name`: tên hiển thị
- `description`: mô tả ngắn cho trang category
- `slug`: tự sinh từ tên (Vietnamese-friendly)

Mapping `content_type → category_id` cache trong `config/settings.json` sau khi seed.
