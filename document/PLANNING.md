# Ứng dụng Machine Learning trong việc phân loại sai lệch dòng tiền và dự báo rủi ro thất thoát tại điểm bán lẻ (POS).

#### 🔄 Vòng 1: Descriptive — Đối soát Doanh thu theo Ca _(giữ nguyên, hợp lý)_

Ghép `DetailsTransaction` vào từng ca trong `MainLog` theo timestamp, tính `Payment_Mismatch` và `Cash_Diff`. Đây là bước cốt lõi và data hoàn toàn hỗ trợ.

#### 🔄 Vòng 2: Diagnostic — Phân cụm Ca theo Mẫu Sai lệch _(giữ nguyên, hợp lý)_

K-Means trên `[Cash_Diff, Payment_Mismatch, Shift_Velocity, total_revenue]` để tách "nhầm loại tiền" vs "thất thoát thực".

#### 🔄 Vòng 3 (Sửa): Customer Pattern Mining — Phân tích Khách Đặc biệt

Thay PhoBERT bằng **clustering + rule-based** trên chính cột `notes`:

- **Chuẩn hoá tên** bằng fuzzy matching (vì "ngoc pt", "n9oc pt", "Ngọc pt" là cùng 1 người) → gom thành ~5–8 khách quen
- **Phân tích hành vi** từng khách: tần suất, giá trị đơn trung bình, tỷ lệ chuyển khoản vs tiền mặt
- **Phát hiện bất thường** trong các đơn có notes: đơn nào giá trị cao bất thường, đơn nào thanh toán lệch chiều so với thói quen của khách đó
- Insight thực tế khả thi: "ngoc pt xuất hiện 31 lần, 90% chuyển khoản, đơn trung bình 46k — nếu 1 đơn đột ngột ghi tiền mặt thì đáng nghi", hoặc "c trang thường xuyên trả đơn hơn 300k -> đây là người hay ủ nợ"

#### 🔄 Vòng 4 (Sửa): Prescriptive — Rule Engine + Báo cáo Tự động

Thay Gemini/RAG bằng **rule engine đơn giản** để sinh báo cáo giải thích:

- Rule 1: Nếu `Cash_Diff < 0` và `Payment_Mismatch > 0` cùng chiều → "Nhầm loại tiền"
- Rule 2: Nếu `Cash_Diff < 0` và không có mismatch → "Nghi thất thoát thực"
- Rule 3: Nếu ca có đơn của khách quen (trong notes) mà thanh toán lệch thói quen → "Kiểm tra lại đơn [X] của [tên khách]"
- Output: báo cáo text tự động, không cần LLM