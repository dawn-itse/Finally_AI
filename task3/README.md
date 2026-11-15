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

## Benchmark độc lập

Chạy `python -B -m task3.benchmark` từ thư mục gốc. Mỗi bàn được giải 20 lần và mọi nghiệm đều được kiểm tra. CSV lưu số đo từng lượt. Kết quả dưới đây đo trên Windows với Python 3.10.6.

| Bàn | Lượt | TB ms | SD mẫu ms | TB Backtracks | TB ô đã xử lý | TB đỉnh KiB |
|---|---:|---:|---:|---:|---:|---:|
| Simple 5×5 | 20 | 1,619 | 0,266 | 0 | 12 | 24,73 |
| Advanced 9×9 | 20 | 357,981 | 40,049 | 0 | 48 | 10.212,16 |
| Backtracking Demo 4×4 | 20 | 0,982 | 0,063 | 1 | 9 | 20,56 |

`perf_counter()` đo toàn bộ `solve()`, gồm tạo bộ ứng viên, tìm nghiệm và ghi bước. `tracemalloc` đo đỉnh cấp phát Python ở lượt giải độc lập trên cùng bàn, gồm `solver.steps`. Cả hai phép đo loại bước tạo CSP, xác thực nghiệm, xuất CSV và UI. Đỉnh cấp phát này khác với RSS và không tách riêng số byte của nhật ký. Hai bàn trong đề giải được bằng lan truyền ban đầu. Bàn demo đi qua một nhánh thất bại để kiểm tra quay lui.

## Độ phức tạp theo mã

Gọi V là số ô trắng, D là kích thước miền tối đa (9), R là số dãy, K là chiều dài dãy tối đa và P là số bộ số hợp lệ tối đa của một dãy.

- **Tạo bộ ứng viên.** Mỗi dãy dài k thử tổ hợp và sinh hoán vị khi đúng tổng. Cận thời gian cho cả bàn là O(R × (K × C(D,K) + K × P)) nếu các dãy cùng dài K. Với độ dài khác nhau, cộng chi phí theo từng dãy với k và số bộ thực tế của dãy đó. Bộ nhớ bảng bộ số tối đa O(RKP).
- **Lan truyền.** Mỗi lần lấy một dãy từ hàng đợi quét các bộ ứng viên cho dãy, tốn O(K(P + D)) gồm lọc và cập nhật miền. Nếu lượt lan truyền bắt đầu với tối đa R dãy, mỗi lần giảm miền chỉ có thể thêm dãy giao nhau. Có tối đa VD giá trị bị loại. Do kiểm tra trùng trong hàng đợi tuyến tính, cận thời gian mỗi lượt là O((R + VD)K(P + D) + VDR) với mỗi ô thuộc tối đa hai dãy. Bộ đệm xử lý một dãy cần O(KD) và hàng đợi cần O(R).
- **MRV và Backtracking.** MRV quét V miền trong O(V) thời gian và O(V) bộ nhớ cho danh sách ô chưa cố định. Cây tìm kiếm có tối đa O(D^V) nút. Mỗi nhánh sao chép bảng miền O(V) và lan truyền tiếp. Vì vậy thời gian tìm kiếm có cận O(D^V × (V + chi phí một lượt lan truyền)), ngoài bước tạo bộ ứng viên. Đây là cận xấu nhất, còn hai bàn trong đề không cần mở nhánh.
- **Không gian solver và nhật ký.** Bảng bộ ứng viên cần O(RKP). Ngăn xếp tìm kiếm sâu tối đa V, với tối đa O(V²) mục trong các bản sao dictionary. Các bản sao chia sẻ tập giá trị cho đến khi thay miền. Cận bảo thủ cho miền và các bản sao là O(V²D), ngoài hàng đợi và bộ đệm lan truyền. Riêng nhật ký giữ một mục cho mỗi lần gán, loại ứng viên hoặc hoàn tác. Một mục thông thường giữ một miền, còn mục hoàn tác có thể giữ tới V miền. Với E mục, O(EVD) là cận bảo thủ, có tính đến việc nhật ký giữ tham chiếu tới các miền cũ. Số mục E có thể tăng theo số nhánh đã thử, kể cả khi độ sâu ngăn xếp nhỏ.
