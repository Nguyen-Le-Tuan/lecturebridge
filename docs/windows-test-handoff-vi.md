# Lấy bản Local Studio và kiểm thử Windows

Nhánh cần lấy: **`ubuntu/local-studio`**. Đây là bản để nghiệm thu local,
chưa phải bản phát hành công khai/classroom-ready. `main` chưa có các tính năng này.
Không copy `.venv` từ Ubuntu sang Windows; model GPU/CPU chưa được chạy lại trong
đợt triển khai này theo yêu cầu tránh làm quá tải máy.

Dùng [hướng dẫn Windows fresh từng bước và F01–F20](windows-fresh-acceptance-vi.md)
khi cài máy mới; hướng dẫn đó chỉ tải tiny trước lượt GPU đầu tiên.
Dùng [mẫu báo cáo nghiệm thu](acceptance-report-template-vi.md) để ghi kết quả.
Mục chưa thử ghi `CHƯA TEST`; không cần chạy bài nặng để điền đủ mẫu.

## 1. Lấy đúng code

Nếu chưa có repo trên Windows, dùng PowerShell:

```powershell
git clone --branch ubuntu/local-studio https://github.com/Nguyen-Le-Tuan/lecturebridge.git
Set-Location lecturebridge
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap-windows.ps1
```

Nếu đã clone:

```powershell
Set-Location <thu-muc-repo-cua-ban>
git status --short
git fetch origin
git switch ubuntu/local-studio
git pull --ff-only origin ubuntu/local-studio
uv sync --locked
```

Giữ lại/commit thay đổi riêng trước khi switch nếu Git báo xung đột. Không dùng
`reset --hard`. Bộ cài tải model mặc định nhưng không chạy inference/deep preflight.
CUDA 12, cuDNN 9 và Visual C++ x64 vẫn cần cài riêng: xem [Windows setup](setup-windows.md).

## 2. Kiểm tra nhẹ, không GPU và không nạp model

```powershell
uv run ruff check .
uv run pytest -q -m "not gpu"
uv build
```

Nếu có Node.js, kiểm tra resampler bằng dữ liệu số giả:

```powershell
node --test tests/test_worklet.cjs
```

Xem UI với backend dữ liệu giả (không nạp model hoặc nhận diện giọng nói thật):

```powershell
$env:PYTHONPATH = "src"
uv run python tests/ui_server.py
```

Mở `http://127.0.0.1:8765`. Server fixture này chỉ dành cho test, trả câu ví dụ
khi nhận audio. Nếu tự mở fixture trong trình duyệt, microphone vẫn là microphone
thật của bạn; chỉ bài kiểm thử Playwright tự động mới cấp microphone giả. Thư viện
nằm trong thư mục tạm và bị xóa khi đóng fixture bình thường.
Dừng bằng `Ctrl+C`. Phiên thật dùng lệnh ở mục 4.

## 3. Bài GPU đầu tiên: nhỏ, có watchdog, chạy thủ công

Đóng server LectureBridge và các ứng dụng GPU khác, cắm nguồn, đặt máy thông thoáng.
Không chạy stress test hoặc bộ dịch trong bài kiểm tra đầu tiên.

```powershell
uv run lecturebridge-models download --model tiny.en
uv run python scripts/gpu-smoke.py
```

Script chỉ chạy `tiny.en` với **1 giây im lặng**, không bật NLLB và không lặp benchmark.
Nó giám sát GPU số 0, từ chối bắt đầu nếu nhiệt độ trên 65°C; dừng tiến trình test
nếu đạt 75°C, VRAM trống dưới 1024 MiB, quá 60 giây hoặc không đọc được cảm biến.
`Ctrl+C` cũng dừng tiến trình test. Các ngưỡng được chọn bảo thủ, không phải giới hạn
phần cứng của nhà sản xuất. Watchdog chỉ giảm rủi ro, không bảo đảm tránh được lỗi
driver, nguồn điện hoặc treo toàn hệ điều hành.

Muốn quan sát riêng ở cửa sổ PowerShell thứ hai:

```powershell
nvidia-smi --query-gpu=temperature.gpu,memory.used,memory.total,utilization.gpu --format=csv -l 1
```

Yêu cầu thấy `[PASS] Deep model smoke test` và chi tiết `tiny.en executed on cuda`.
Nếu fail hoặc watchdog dừng, dừng tại đây; giữ thông báo lỗi để chẩn đoán, không
chuyển ngay sang model lớn. Một số kiểm tra preflight khác như Tailscale có thể
fail riêng; đọc từng dòng thay vì coi đó là lỗi CUDA.

## 4. Thử ứng dụng thật sau khi smoke test đạt

```powershell
uv run lecturebridge-live --device cuda --model tiny.en
```

Mở `http://127.0.0.1:8000`, thử **15–30 giây**, rồi bấm **Dừng phiên**.
Lệnh server này không có watchdog nhiệt độ; quan sát cửa sổ `nvidia-smi`, dừng
bằng nút UI rồi `Ctrl+C` nếu máy nóng hoặc phản hồi kém. Giữ chế độ Tiếng Anh
trong lượt đầu. `tiny.en` chỉ để xác nhận luồng hoạt động, chất lượng thấp hơn
model mặc định. Chưa chạy phiên 20 phút hoặc stress/debate ở bước này.

Khi bạn đã xác nhận máy ổn định, có thể tự chọn kiểm thử model mặc định và dịch
CPU trong lượt riêng. Không có bước tự động nào nâng từ tiny lên model lớn.

Kiểm tra chức năng:

1. Không bật lưu: transcript hiện nhưng Thư viện không thêm bản ghi.
2. Phiên tiếp theo bật **Lưu bản ghi**: thấy chỉ báo lưu, dừng và nghe lại được.
3. Thử tải WAV/TXT/JSON, đổi tên, tua theo đoạn và xóa.
4. Trong một lượt riêng, chọn **Song ngữ**: model dịch thiếu thì UI đề nghị tải
   khoảng 2,5 GB; khi sẵn sàng chỉ dịch phần mới, tiếng Anh vẫn hoạt động.
5. Chọn **Tiếng Anh**: ngừng gửi việc dịch mới, không mất nội dung đã có.
6. iPad dùng HTTPS Tailscale riêng và giữ Safari ở foreground; không dùng Funnel.

## Dữ liệu và giới hạn

- Windows: `%LOCALAPPDATA%\LectureBridge`; Linux: `~/.local/share/lecturebridge`
  (hoặc theo `XDG_DATA_HOME`). Tùy chọn `--data-dir` đổi vị trí lưu.
- WAV mono 16 kHz/16-bit khoảng 115 MB/giờ; transcript và metadata trong SQLite.
- Lưu do người dùng bật trước từng phiên; dữ liệu giữ tới khi xóa. Tắt lưu thì
  nội dung chỉ nằm trong bộ nhớ của phiên, export vẫn có sẵn trước khi đóng trang.
- Ubuntu và Windows có thư viện riêng; Git chỉ mang code, không mang bản ghi.
- Mất kết nối: bản ghi chỉ có phần laptop đã nhận. Không tự reconnect/ghép phiên.
- Một phiên đang nghe cho mỗi server, tối đa 2 giờ. Timestamp căn theo đoạn, chưa
  phải căn chính xác từng từ. Chưa có tài khoản/cloud hoặc đồng bộ đa thiết bị.
- Ai truy cập được instance trên local/tailnet tin cậy đều có quyền đọc/xóa thư viện.
