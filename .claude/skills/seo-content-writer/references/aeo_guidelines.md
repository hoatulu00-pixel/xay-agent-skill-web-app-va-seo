# AEO Guidelines — Answer Engine Optimization

Tối ưu cho Google SGE, ChatGPT Search, Perplexity, Bing Copilot. Mục tiêu: bài viết được AI trích dẫn / tóm tắt khi user hỏi.

## Nguyên tắc cốt lõi

1. **TL;DR đầu bài (40-60 từ)**: ngay sau H1, trước phần intro dài. Trả lời thẳng câu hỏi chính trong 1-2 câu. Đây là phần AI engines copy nhiều nhất.

   Ví dụ:
   > **Tóm tắt nhanh:** Chân váy hoa mùa xuân phối đẹp nhất với áo blouse trắng, sweater pastel hoặc áo sơ mi linen. Chọn pattern hoa nhỏ cho dáng người mảnh, hoa lớn cho dáng đầy đặn.

2. **Cấu trúc câu hỏi → câu trả lời**: H2 là câu hỏi user thực sự gõ. Dưới H2 là 1 đoạn 40-80 từ trả lời trực tiếp, sau đó mới mở rộng.

3. **FAQ section bắt buộc**: cuối bài, ≥3 câu hỏi. Mỗi câu trả lời 30-60 từ. Format:
   ```markdown
   ## Câu hỏi thường gặp
   
   ### Chân váy hoa nên phối với giày gì?
   
   Chân váy hoa hợp nhất với giày sandal quai mảnh, ankle boot da bò, hoặc sneakers trắng tối giản.
   ```
   Web app sẽ tự convert sang FAQ schema khi render.

4. **Định nghĩa rõ trong 1 câu**: nếu bài có thuật ngữ chuyên ngành, định nghĩa ngay câu đầu tiên đoạn đó.

   > Pattern hoa **liberty** là họa tiết hoa nhỏ li ti có nguồn gốc từ Anh quốc, đặc trưng bởi nét vẽ tinh tế.

5. **List rõ ràng cho query so sánh / liệt kê**: nếu H2 là "Top X..." hoặc "X cách..." → bullet list ngay, không viết dạng văn xuôi.

6. **Số liệu cụ thể, có nguồn**: AI engines ưu tiên trích bài có data citation.

## Checklist AEO cho mỗi bài

- [ ] TL;DR 40-60 từ ngay sau H1
- [ ] Mỗi H2 có 1 paragraph trả lời trực tiếp (≤80 từ) trước khi mở rộng
- [ ] FAQ section ≥3 Q&A
- [ ] Có ít nhất 1 list bullet/số
- [ ] Có ít nhất 1 định nghĩa trong câu đầu đoạn
- [ ] Title dạng câu hỏi hoặc statement có data (vd: "5 cách phối...", "Cách phối X cho người Y")

## Schema markup (handled by web app)

Web app render bài tự động sinh:
- Article schema (headline, datePublished, author, image)
- BreadcrumbList
- FAQPage (nếu detect FAQ section)

Skill không cần inject schema thủ công, nhưng phải đảm bảo cấu trúc FAQ đúng pattern `## Câu hỏi thường gặp` để web app detect.
