Dưới đây là tổng quan về 2 file dữ liệu:

📋 DetailsTransaction.csv — Chi tiết từng giao dịch
Quy mô: 5.412 giao dịch | Thời gian: 1/1/2026 → 9/4/2026 (~3,5 tháng)
Cột dữ liệu:

transaction_at — Thời điểm giao dịch
total_revenue — Tổng giá trị đơn
transfer_payment — Thanh toán chuyển khoản
cash_payment — Thanh toán tiền mặt
notes — Ghi chú (chỉ có 101/5412 dòng có dữ liệu)

Số liệu nổi bật:

Tổng doanh thu: 191,495,000 VND
Tiền mặt: 100,548,000 VND (~52%) | Chuyển khoản: 90,939,000 VND (~48%)
Giá trị trung bình/đơn: ~35,400 VND | Min: 10,000 | Max: 625,000
75% giao dịch ≤ 43,000 VND → đây là các đơn nhỏ, có vẻ là quán ăn/cafe


📋 MainLog.csv — Nhật ký theo ca làm việc
Quy mô: 242 bản ghi | Thời gian: 1/1/2026 → 9/4/2026
Cột dữ liệu:

timestamp — Thời điểm chốt ca
total_revenue — Tổng doanh thu ca đó
transfer_amount / cash_amount — Doanh thu theo phương thức thanh toán
is_morning_shift — Ca sáng (True) hay ca chiều (False)
actual_cash_in_drawer — Tiền mặt thực tế trong két

Số liệu nổi bật:

114 ca sáng, 128 ca chiều (~4 tháng, mỗi ngày 2 ca)
Doanh thu trung bình/ca: ~791,000 VND | Max: 2,061,000 VND
Tiền trong két trung bình: ~1,210,000 VND


🔗 Mối liên hệ giữa 2 file
DetailsTransaction ghi từng giao dịch lẻ, còn MainLog là bản tổng hợp theo ca (có thể là dữ liệu chốt sổ cuối ca). Hai file có thể join theo thời gian để kiểm tra tính khớp giữa tổng giao dịch thực tế và số liệu báo cáo ca.