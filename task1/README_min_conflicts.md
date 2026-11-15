# Task 1 — Min-Conflicts

Mỗi hàng có một hậu. Standard chọn ngẫu nhiên một hàng có xung đột. Heuristic chọn ngẫu nhiên trong các hàng có nhiều xung đột nhất. Cả hai chấm mọi cột khác cột ban đầu và chọn ngẫu nhiên trong các cột có điểm thấp nhất.

Chạy notebook từ thư mục gốc hoặc task1. Kết quả đã lưu trong notebook và results/. Nếu chạy lại, sao lưu results/ trước vì notebook ghi lại tên file cố định. Chạy test bằng `python -B -m unittest task1.test_nqueens_min_conflicts`.

## Kết quả trên Windows, Python 3.10.6

Mỗi cặp N và phương pháp dùng 20 seed từ 2026 đến 2045, tối đa 2.000 bước. Các lần thất bại vẫn được tính vào thời gian và số bước trung bình.

| N | Phương pháp | Thành công | TB ms | TB bước | TB đỉnh KiB |
|---:|---|---:|---:|---:|---:|
| 4 | Standard | 100% | 0.164 | 12.65 | 1.35 |
| 4 | Improved | 100% | 0.165 | 12.10 | 1.43 |
| 8 | Standard | 100% | 1.189 | 39.40 | 2.07 |
| 8 | Improved | 85% | 10.406 | 345.05 | 2.03 |
| 10 | Standard | 100% | 3.203 | 74.45 | 3.22 |
| 10 | Improved | 100% | 5.014 | 117.65 | 3.33 |
| 20 | Standard | 100% | 10.303 | 72.00 | 6.62 |
| 20 | Improved | 100% | 7.094 | 46.05 | 6.70 |
| 50 | Standard | 100% | 78.080 | 95.15 | 25.93 |
| 50 | Improved | 100% | 69.221 | 84.40 | 26.02 |

Ở N=8, Heuristic thành công 17/20 lượt và mất nhiều bước hơn. Ở N=20 và N=50, Heuristic giảm số bước trung bình. Kết quả chỉ áp dụng cho các kích thước và seed đã đo.

## Phạm vi đo và độ phức tạp

perf_counter đo lời gọi giải, gồm khởi tạo trạng thái, tìm kiếm và dựng kết quả. tracemalloc đo một lượt riêng trên cùng seed, lấy đỉnh cấp phát Python trong lời gọi giải. Cả hai phép đo loại constructor, xác thực, xuất CSV và vẽ biểu đồ. KiB là 1.024 byte. Bộ nhớ theo dõi được khác với RSS của tiến trình.

Mỗi lần đếm xung đột của một hậu quét O(N) hàng. Kiểm tra nghiệm, tìm hàng xung đột và chấm N−1 cột đều tốn tối đa O(N²) mỗi bước. Với giới hạn S bước, thời gian là O((S + 1)N²), gồm kiểm tra cuối và dựng bàn. Không gian làm việc là O(N) cho trạng thái và danh sách ứng viên. Ma trận nghiệm trả về cần O(N²); lượt thành công tính cả ma trận có đỉnh O(N²). Đây là cận theo mã, còn bảng là số đo trên một môi trường cụ thể.
