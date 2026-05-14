# SEO Checklist — bắt buộc bài viết phải đạt

`content_writer.py` phải sinh bài thỏa toàn bộ checklist sau. `webapp_publisher.py` validate trước khi POST.

## On-page

| # | Tiêu chí | Kiểm tra |
|---|---|---|
| 1 | Title ≤ 60 ký tự, chứa **primary keyword** ở đầu | `len(title) <= 60` và keyword index < 30 |
| 2 | Meta description (excerpt) 150-160 ký tự, có CTA | `150 <= len(excerpt) <= 160` |
| 3 | H1 duy nhất, trùng hoặc gần title | exactly 1 `# ` ở đầu |
| 4 | H2 chứa secondary keywords (≥3 H2) | count(`## `) >= 3 |
| 5 | Mỗi heading cách nhau ≤ 300 từ | tránh đoạn dài |
| 6 | Primary keyword density 1-2% | check word count |
| 7 | Slug ngắn (≤ 5 từ), có keyword | web app tự sinh từ title — title phải gọn |
| 8 | Internal link 1-2 link → category page hoặc bài liên quan | `[anchor](/blog/category/...)` |
| 9 | External link 1-2 link uy tín (vogue, elle, harpersbazaar) | optional |
| 10 | Alt text mô tả cho ảnh | `![alt mô tả keyword](url)` |
| 11 | Bullet/list để tăng readability | mỗi bài ≥ 1 list |
| 12 | Bold các từ khóa quan trọng | `**từ khóa**` rải đều |

## Cấu trúc URL

Web app tự generate slug từ title qua `slugify(title)`. Đảm bảo title:
- Không có ký tự đặc biệt
- Không quá dài (slug sẽ bị cắt)
- Có primary keyword tiếng Việt không dấu (vd: `cach-phoi-chan-vay-hoa`)

## Image SEO

- Cover image: ratio 16:9 hoặc 1200x630 (Open Graph friendly)
- Filename có keyword: `chan-vay-hoa-mua-xuan.jpg`
- Alt text mô tả cụ thể, không stuff keyword

## Content quality

- Độ dài tối thiểu: 800 từ (informational), 1200 từ (how-to/listicle), 600 từ (review/behind-scenes)
- Không trùng lặp nội dung (kiểm tra qua check title/slug đã tồn tại trên web)
- Có data/số liệu cụ thể nếu có thể (vd: "70% phụ nữ Việt sở hữu ít nhất 3 chân váy hoa")
- Tone: thân thiện, hướng đến nữ 22-40 tuổi yêu thời trang nữ tính

## Output validator

Function `validate_seo(article: str) -> list[str]` trong `utils.py` trả list error. Block publish nếu error > 0.
