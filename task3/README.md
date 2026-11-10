# Task 3 – Kakuro CSP

Hai bàn trong đề được lưu tại `kakuro_csp.py`: bàn mẫu 5×5 trang 4 và bàn nâng cao 9×9 trang 5.

## Mô hình và thuật toán

- **Variables (biến)**: mỗi ô trắng là một biến, nhận diện bằng tọa độ hàng và cột.
- **Domains (miền giá trị)**: mỗi biến bắt đầu với các số từ 1 đến 9.
- **Constraints (ràng buộc)**: mỗi dãy ngang hoặc dọc có tổng bằng gợi ý và các số đôi một khác nhau.
- **Backtracking Search (tìm kiếm quay lui)** thử từng giá trị của biến được chọn. **MRV** ưu tiên ô chưa cố định có ít ứng viên nhất để sớm gặp mâu thuẫn.
- **Forward Checking (kiểm tra trước)** kiểm tra các dãy chứa ô vừa gán. Solver chỉ giữ giá trị xuất hiện trong ít nhất một bộ số hợp lệ của dãy, rồi **Constraint Propagation (lan truyền ràng buộc)** áp dụng miền đã thu hẹp cho các dãy giao nhau. Miền rỗng làm nhánh thất bại. Khi quay lui, solver khôi phục miền trước lần thử. Khi mọi miền còn một số, solver kiểm tra lại tất cả ràng buộc.

## Chạy từ thư mục gốc

```sh
python -m pip install pygame
python -m task3.main --board simple
python -m task3.main --board advanced
python -m task3.main --board backtracking_demo
```

- **← (Previous Step)** lùi một bước và tạm dừng nếu đang chạy tự động.
- **→ (Next Step)** tiến một bước.
- **Space (Play/Pause)** chạy tự động hoặc tạm dừng.
- **R (Reset)** về trạng thái ban đầu.

UI phát lại nhật ký của solver. Màu xanh là gán thử, vàng là loại ứng viên, đỏ là quay lui và khôi phục miền. Ô còn một ứng viên hiện số lớn.

Bàn **Backtracking Demo 4×4** minh họa một lần gán thử thất bại. Khi miền của một ô rỗng, solver quay lui, khôi phục miền trước lần gán và thử giá trị tiếp theo. Dùng hai phím mũi tên để xem lại bước màu đỏ.

## Kiểm thử và đo thời gian

```sh
python -m unittest task3.test_kakuro -v
python -m task3.main --board simple --no-ui
python -m task3.main --board advanced --no-ui
python -m task3.main --board backtracking_demo --no-ui
```

Kết quả chạy thực tế với `--no-ui`. Cả 5 unit test đều đạt.

| Bàn | Số ô trắng | Solved | Backtracks |
| --- | ---: | --- | ---: |
| Simple 5×5 | 12 | Có | 0 |
| Advanced 9×9 | 48 | Có | 0 |
| Backtracking Demo 4×4 | 9 | Có | 1 |

Thời gian đo toàn bộ lượt giải, kể cả chuẩn bị các bộ số và ghi nhật ký. Backtracks đếm số lần hoàn tác một giá trị thử thất bại. Variables processed đếm số ô trắng khác nhau thuộc các dãy đã xét khi lan truyền hoặc được MRV chọn để gán thử. Mỗi ô chỉ được đếm một lần.
