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

Kết quả chạy thực tế với `--no-ui`. Cả 6 unit test Task 3 đều đạt.

| Bàn | Số ô trắng | Solved | Backtracks |
| --- | ---: | --- | ---: |
| Simple 5×5 | 12 | Có | 0 |
| Advanced 9×9 | 48 | Có | 0 |
| Backtracking Demo 4×4 | 9 | Có | 1 |

Thời gian đo toàn bộ lượt giải, kể cả chuẩn bị các bộ số và ghi nhật ký. Backtracks đếm số lần hoàn tác một giá trị thử thất bại. Variables processed đếm số ô trắng khác nhau thuộc các dãy đã xét khi lan truyền hoặc được MRV chọn để gán thử. Mỗi ô chỉ được đếm một lần.

## Benchmark độc lập

Chạy `python -B -m task3.benchmark` từ thư mục gốc. Mỗi bàn được giải 20 lần và mọi nghiệm đều được kiểm tra. CSV lưu số đo từng lượt. Kết quả dưới đây đo trên Windows với Python 3.10.6.

| Bàn | Lượt | TB ± SD mẫu (ms), trước → sau | TB đỉnh KiB, trước → sau | TB Backtracks | TB ô xử lý | Nodes Expanded (TB) | Max Search Depth | Peak Active Nodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Simple 5×5 | 20 | 1,619 ± 0,266 → 1,588 ± 0,094 | 24,73 → 24,65 | 0 | 12 | 0 | 0 | 1 |
| Advanced 9×9 | 20 | 357,981 ± 40,049 → 357,410 ± 25,258 | 10.212,16 → 10.212,16 | 0 | 48 | 0 | 0 | 1 |
| Backtracking Demo 4×4 | 20 | 0,982 ± 0,063 → 0,962 ± 0,050 | 20,56 → 20,56 | 1 | 9 | 3 | 3 | 4 |

Mốc trước lấy từ [CSV gốc](benchmark_results.csv). Mốc sau lấy từ [CSV có bộ đếm](benchmark_results_20261115_130722.csv). Hai cột độ sâu và số node đồng thời lấy giá trị lớn nhất qua 20 lượt. Backtracks và số ô xử lý giống nhau ở hai mốc. CSV gốc chưa đo ba chỉ số tìm kiếm.

`perf_counter()` đo toàn bộ `solve()`, gồm tạo bộ ứng viên, tìm nghiệm và ghi bước. `tracemalloc` đo đỉnh cấp phát Python ở lượt giải độc lập trên cùng bàn, gồm `solver.steps`. Cả hai phép đo loại bước tạo CSP, xác thực nghiệm, xuất CSV và UI. Đỉnh cấp phát này khác với RSS và không tách riêng số byte của nhật ký. Hai bàn trong đề giải được bằng lan truyền ban đầu. Bàn demo đi qua một nhánh thất bại để kiểm tra quay lui.

## Chỉ số tìm kiếm

- **Nodes Expanded** đếm mỗi lần `_search` gặp ít nhất một miền có nhiều giá trị và chọn ô bằng MRV để thử các nhánh. Lá chỉ kiểm tra nghiệm, nhánh bị lan truyền loại trước khi gọi đệ quy và các sự kiện `assign`/`prune` đều không cộng vào chỉ số này.
- **Max Search Depth** là độ sâu lớn nhất của lời gọi `_search`, tính gốc ở độ sâu 0 và tính cả lá. Giá trị là 0 nếu lan truyền ban đầu phát hiện vô nghiệm trước khi vào `_search`.
- **Peak Active Nodes** là số frame `_search` đồng thời nhiều nhất, tính cả gốc và lá nếu có. Chỉ số bằng độ sâu lớn nhất cộng 1 khi tìm kiếm được gọi, và bằng 0 nếu tìm kiếm chưa bắt đầu. Đây là số trạng thái trên một đường đi, trong khi Nodes Expanded cộng các lần sinh nhánh trên toàn bộ lượt giải. Nó không đo byte, frame của hàm lan truyền hoặc trạng thái được giữ bởi nhật ký.

Mỗi lượt giải đặt lại ba bộ đếm. Benchmark ghi từng lượt vào CSV mới để giữ nguyên các file cũ. Giá trị đo phụ thuộc bàn và thứ tự duyệt. Chênh lệch giữa hai lần chạy thời gian hoặc bộ nhớ không cô lập chi phí của bộ đếm.

## Độ phức tạp theo mã

Gọi V là số ô trắng, D là kích thước miền tối đa (9), R là số dãy, K là chiều dài dãy tối đa và P là số bộ số hợp lệ tối đa của một dãy.

- **Tạo bộ ứng viên.** Mỗi dãy dài k thử tổ hợp và sinh hoán vị khi đúng tổng. Cận thời gian cho cả bàn là O(R × (K × C(D,K) + K × P)) nếu các dãy cùng dài K. Với độ dài khác nhau, cộng chi phí theo từng dãy với k và số bộ thực tế của dãy đó. Bộ nhớ bảng bộ số tối đa O(RKP).
- **Lan truyền.** Mỗi lần lấy một dãy từ hàng đợi quét các bộ ứng viên cho dãy, tốn O(K(P + D)) gồm lọc và cập nhật miền. Nếu lượt lan truyền bắt đầu với tối đa R dãy, mỗi lần giảm miền chỉ có thể thêm dãy giao nhau. Có tối đa VD giá trị bị loại. Do kiểm tra trùng trong hàng đợi tuyến tính, cận thời gian mỗi lượt là O((R + VD)K(P + D) + VDR) với mỗi ô thuộc tối đa hai dãy. Bộ đệm xử lý một dãy cần O(KD) và hàng đợi cần O(R).
- **MRV và Backtracking.** MRV quét V miền trong O(V) thời gian và O(V) bộ nhớ cho danh sách ô chưa cố định. Cây tìm kiếm có tối đa O(D^V) nút. Mỗi nhánh sao chép bảng miền O(V) và lan truyền tiếp. Vì vậy thời gian tìm kiếm có cận O(D^V × (V + chi phí một lượt lan truyền)), ngoài bước tạo bộ ứng viên. Đây là cận xấu nhất, còn hai bàn trong đề không cần mở nhánh.
- **Không gian solver và nhật ký.** Bảng bộ ứng viên cần O(RKP). Độ sâu tính từ gốc tối đa V, tương ứng tối đa V + 1 frame tìm kiếm. Mỗi frame có thể giữ bản sao dictionary O(V) và danh sách ô chưa cố định O(V). Các bản sao chia sẻ tập giá trị cho đến khi thay miền. Cận bảo thủ cho miền và các bản sao là O(V²D), ngoài hàng đợi và bộ đệm lan truyền. Riêng nhật ký giữ một mục cho mỗi lần gán, loại ứng viên hoặc hoàn tác. Một mục thông thường giữ một miền, còn mục hoàn tác có thể giữ tới V miền. Với E mục, O(EVD) là cận bảo thủ, có tính đến việc nhật ký giữ tham chiếu tới các miền cũ. Số mục E có thể tăng theo số nhánh đã thử, kể cả khi độ sâu ngăn xếp nhỏ.
- **Chi phí bộ đếm.** Các số tổng hợp dùng O(1) ô nhớ. Mỗi frame có thêm một giá trị độ sâu, được truyền xuống và cập nhật trong O(1) thời gian mỗi lời gọi. Các bộ đếm này giữ nguyên cận Big-O của solver.
