# Windows fresh: lấy toàn bộ code và nghiệm thu từng tiêu chí

Toàn bộ mã nguồn nằm trên nhánh **`ubuntu/local-studio`** của
[LectureBridge](https://github.com/Nguyen-Le-Tuan/lecturebridge/tree/ubuntu/local-studio).
Tên nhánh có chữ Ubuntu nhưng ứng dụng hỗ trợ Windows native. `main` chưa có
bản Local Studio này. Clone sẽ lấy code, giao diện, scripts, tests và tài liệu;
model, môi trường Python và bản ghi riêng được tạo/tải lại trên Windows.

Làm lần lượt từng chặng bằng **PowerShell**, không dán tất cả thành một lần chạy.
Lỗi ở chặng nào thì ghi báo cáo tại đó. Bài đầu chỉ dùng `tiny.en`; không cần
test dịch, iPad hoặc model lớn để gửi báo cáo đầu tiên. Hướng dẫn này không tự
thực thi GPU và không yêu cầu stress test.

## 1. Cài các thành phần trên Windows

Dùng Windows 10/11 x64 trực tiếp, không chạy các lệnh này trong WSL.

### Git và uv

Cài Git theo [hướng dẫn chính thức](https://git-scm.com/install/windows):

```powershell
winget install --id Git.Git -e --source winget
```

Nếu không có `winget`, tải bộ cài x64 từ trang Git trên. Cài uv theo
[hướng dẫn chính thức](https://docs.astral.sh/uv/getting-started/installation/):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Đóng PowerShell rồi mở cửa sổ mới để nhận PATH. Kiểm tra:

```powershell
git --version
uv --version
```

### Điều kiện để chạy NVIDIA GPU

- Cài [NVIDIA driver](https://www.nvidia.com/drivers) phù hợp GPU.
- Chọn **CUDA Toolkit 12.x** trong [CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive).
- Cài **cuDNN 9 dành cho CUDA 12**, theo
  [hướng dẫn cuDNN trên Windows](https://docs.nvidia.com/deeplearning/cudnn/installation/latest/windows.html).
- Cài [Microsoft Visual C++ Redistributable x64](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170).
- Cài [Tailscale Windows](https://tailscale.com/download/windows) và đăng nhập
  tài khoản tailnet của bạn. Preflight kiểm tra thành phần này; iPad cũng dùng
  cùng tailnet ở bước tùy chọn sau.

CUDA/cuDNN ở đây là yêu cầu của phiên bản dự án, không phải yêu cầu cài mọi bản
mới nhất. Không cần cài toàn bộ Visual Studio chỉ để chạy app Python này.
Nếu bộ cài yêu cầu restart Windows thì hoàn thành trước khi test.

Mở PowerShell mới và kiểm tra — các lệnh này **không chạy inference**:

```powershell
nvidia-smi
where.exe cublas64_12.dll
where.exe cudnn64_9.dll
where.exe cudnn_ops64_9.dll
```

Mỗi lệnh `where.exe` phải tìm thấy DLL. Nếu thiếu, kiểm tra cài đặt rồi thêm
thư mục **thực sự chứa DLL** vào Windows Environment Variables → Path → New;
không thay thế toàn bộ PATH. Mở lại PowerShell và kiểm tra lại. Không đoán đường
dẫn cuDNN vì bố cục thư mục có thể khác giữa các bộ cài. Dòng “CUDA Version” của
`nvidia-smi` không chứng minh Toolkit/cuDNN đã được cài đủ. Nếu chưa đủ DLL,
vẫn có thể làm kiểm tra nhẹ; chưa chuyển sang chặng GPU.

## 2. Clone đầy đủ source và cài môi trường Python riêng

Chọn thư mục mới; không copy `.venv` từ Ubuntu:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\source" | Out-Null
Set-Location "$env:USERPROFILE\source"
git clone --branch ubuntu/local-studio https://github.com/Nguyen-Le-Tuan/lecturebridge.git
Set-Location lecturebridge
git branch --show-current
git rev-parse --short HEAD
git status --short
uv python install 3.12
uv sync --locked
uv run python --version
```

Nhánh phải là `ubuntu/local-studio`, Python là 3.12.x; ghi commit thực tế vào
mục 1 của báo cáo. Nếu GitHub yêu cầu đăng nhập, dùng tài khoản có quyền truy cập
repo. Nếu thư mục `lecturebridge` đã tồn tại, không clone đè hoặc xóa dữ liệu:
dùng quy trình cập nhật trong [handoff](windows-test-handoff-vi.md).

Quy trình này chủ động cài từng bước. **Không cần chạy thêm
`bootstrap-windows.ps1`**: script đó còn tải model mặc định
`distil-large-v3.5`; lượt đầu bên dưới chỉ cần `tiny.en`.

Tạo bản báo cáo để điền, giữ nguyên mẫu gốc:

```powershell
New-Item -ItemType Directory -Force .\data\private | Out-Null
$reportPath = ".\data\private\acceptance-report-$(Get-Date -Format yyyyMMdd-HHmmss).md"
Copy-Item .\docs\acceptance-report-template-vi.md $reportPath
notepad $reportPath
```

`data/private/` đã được Git ignore. Báo cáo chỉ ở máy của bạn cho tới khi bạn
chủ động gửi. Mở lại hướng dẫn này bất kỳ lúc nào bằng:

```powershell
notepad .\docs\windows-fresh-acceptance-vi.md
```

## 3. Điền môi trường và chạy kiểm tra nhẹ

Trong mục 2 báo cáo: dùng `winver` lấy Windows build; Task Manager → Performance
lấy CPU, RAM, GPU; Settings/trình duyệt lấy phiên bản browser và microphone.
Dung lượng trống xem trong File Explorer. Lấy thông tin còn lại bằng:

```powershell
uv --version
uv run python --version
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
```

Chạy **từng lệnh** sau, ghi kết quả vào mục 3 báo cáo. Có thể xem
`$LASTEXITCODE` ngay sau mỗi lệnh; 0 nghĩa là lệnh hoàn thành thành công.

```powershell
uv run ruff check .
uv run pytest -q -m "not gpu"
uv build
uv run python scripts/check_repository.py
```

Các bài này không nạp model ASR/dịch thật hoặc chạy GPU. Ghi đúng số tests mà
máy Windows báo, kể cả skipped/deselected. Repo guard không có hàng riêng trong
mẫu thì ghi vào phần kết quả bổ sung. Nếu đã có Node.js, chạy thêm:

```powershell
node --test tests/test_worklet.cjs
```

Không có Node thì ghi `CHƯA TEST — chưa cài Node`; không cần cài chỉ để điền đủ.

Muốn xem UI trước khi thử GPU, có thể dùng fixture tùy chọn:

```powershell
$env:PYTHONPATH = "src"
uv run python tests/ui_server.py
```

Mở `http://127.0.0.1:8765`. Fixture trả transcript giả; tự mở browser vẫn dùng
mic thật nếu bạn bấm Bắt đầu. Ghi rõ `fixture` khi báo cáo, không coi đây là
bằng chứng ASR/dịch thật. Thư viện fixture là tạm. Dừng bằng Ctrl+C trước khi
sang bước sau, rồi xóa biến tạm trong cửa sổ này:

```powershell
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
```

## 4. Bài GPU đầu tiên — chỉ chạy khi bạn sẵn sàng

Đóng server LectureBridge và ứng dụng GPU khác. Cắm sạc, để máy thông thoáng.
Mở cửa sổ PowerShell thứ hai để quan sát; lệnh này chỉ đọc thông số:

```powershell
nvidia-smi --id=0 --query-gpu=temperature.gpu,memory.used,memory.free,utilization.gpu --format=csv -l 1
```

Ở cửa sổ chính, tải tiny trước — tải model không chạy inference:

```powershell
uv run lecturebridge-models download --model tiny.en
```

Khi tải thành công, chạy bài có watchdog:

```powershell
uv run python scripts/gpu-smoke.py
$LASTEXITCODE
```

Bài này nạp `tiny.en`, xử lý **1 giây im lặng**, không bật dịch. GPU số 0 phải
không quá 65°C và còn ít nhất 1024 MiB VRAM để bắt đầu. Watchdog dừng khi nhiệt
độ đạt 75°C, VRAM trống dưới 1024 MiB, hết 60 giây hoặc mất telemetry. Ctrl+C
cũng dừng bài. Watchdog giảm rủi ro, không bảo đảm chống mọi lỗi driver/nguồn/OS.

Điền **mục 4 báo cáo**: toàn bộ output, exit code, thời gian, nhiệt độ và VRAM
quan sát được. Tìm dòng `[PASS] Deep model smoke test` có chi tiết
`tiny.en executed on cuda`. Không lấy PASS của phần tải model làm PASS GPU.
Nếu watchdog dừng hoặc deep test FAIL/không xuất hiện, dừng tại đây và gửi lỗi.
Nếu chỉ Tailscale FAIL nhưng deep CUDA PASS và các điều kiện runtime khác PASS,
ghi lỗi Tailscale riêng: có thể thử localhost, chưa xác nhận iPad.

## 5. S01 — tiếng Anh, không lưu, 15–30 giây

Chỉ tiếp tục khi smoke đạt và máy ổn định. Chạy tại thư mục repo:

```powershell
uv run lecturebridge-live --device cuda --model tiny.en
```

Đợi server ready, mở `http://127.0.0.1:8000`. Lệnh server này **không có watchdog
nhiệt độ**. Giữ cửa sổ theo dõi GPU; dừng phiên rồi Ctrl+C nếu đạt 75°C, VRAM
trống dưới 1024 MiB hoặc máy phản hồi kém. Không chạy đồng thời nhiều server.

Chọn **Tiếng Anh**, để **Lưu bản ghi tắt**, nhìn số bản ghi hiện có trong Thư viện,
rồi trở lại màn hình phiên học. Bắt đầu và cho phép mic. Có thể tự đọc mẫu này
trong khoảng 15–30 giây, nghỉ nhẹ giữa các câu:

> Today we are testing LectureBridge on Windows. The microphone should capture
> my voice clearly. The transcript should remain visible after I stop the session.
> This recording is only for my own software test.

Nếu đọc sai, ghi lời bạn thực sự nói để đối chiếu. Bấm **Dừng phiên**, chờ hoàn
tất; tải TXT trước khi rời trang. Ghi S01 trong mục 5 báo cáo và F01–F05 bên dưới.

| ID | Thao tác cụ thể | PASS khi / bằng chứng cần ghi |
|---|---|---|
| F01 | Xem màn hình phiên học và Thư viện; thu nhỏ cửa sổ, rồi mở rộng lại. | Không chồng chữ, mất nút hoặc tràn ngang. Ghi browser/kích thước ước lượng; chụp ảnh nếu lỗi. |
| F02 | Bắt đầu, cấp quyền mic, nói, Dừng. | Có thu âm; sau Dừng chỉ báo mic đang hoạt động của browser/Windows tắt. Biểu tượng quyền đã cấp có thể vẫn còn. Ghi lỗi quyền hoặc thời gian dừng bất thường. |
| F03 | Đọc mẫu, đợi chữ rồi Dừng. | Có tiếng Anh và transcript còn sau hoàn tất. Dán lời thực tế + transcript vào phần chất lượng; không yêu cầu tiny nhận đúng tuyệt đối để xác nhận luồng. |
| F04 | So sánh Thư viện trước/sau S01 khi lưu tắt. | Không có bản ghi mới. Ghi số lượng trước/sau. |
| F05 | Sau Dừng, tải TXT trước khi reload/rời trang. | TXT mở được và có transcript S01. Giữ file; ghi tên file vào báo cáo. |
| F14 | Thử sáng/tối, tăng/giảm cỡ chữ; làm khi chưa bắt đầu hoặc sau Dừng cũng được. | Giao diện đổi đúng, nút vẫn dùng được; ghi chế độ/cỡ chữ gặp lỗi nếu có. |
| F15 | Khi đang có text mới, cuộn lên đọc phần cũ; sau đó bấm “Về nội dung mới”. | Không tự kéo xuống khi đang đọc cũ; nút đưa về đoạn mới. Nếu chưa đủ chữ để cuộn, tăng cỡ chữ/thu chiều cao cửa sổ; vẫn chưa đủ thì ghi CHƯA TEST, không kéo dài bài chỉ vì tiêu chí này. |

Đo độ trễ bằng đồng hồ hoặc ước lượng có ghi rõ cách đo: bắt đầu nói → chữ đầu;
kết thúc câu → đoạn chốt; bấm Dừng → hoàn tất. Ghi riêng số “Độ trễ xử lý” của UI.
Không suy ra p95 từ vài câu hoặc coi số UI là độ trễ toàn bộ luồng. Không đo được
thì ghi `CHƯA ĐO`.

## 6. S02 — lưu audio, 15–30 giây; kiểm tra thư viện sau Dừng

Đợi máy ổn định rồi bắt đầu lượt riêng, vẫn **tiny.en + Tiếng Anh**. Bật
**Lưu bản ghi trước khi Bắt đầu**. Đọc 2–4 câu tự tạo, đánh dấu thời điểm bắt đầu
capture và Dừng để đối chiếu audio. Điền khối S02 riêng trong mục 5 báo cáo.
Các thao tác nghe lại/tải/đổi tên/xóa thực hiện sau khi phiên kết thúc.

| ID | Thao tác cụ thể | PASS khi / bằng chứng cần ghi |
|---|---|---|
| F06 | Bật lưu trước phiên; quan sát lúc thu; Dừng rồi mở Thư viện. | Có chỉ báo lưu và bản ghi S02 xuất hiện. Ghi tên bản ghi/thời gian. |
| F07 | Mở S02 và nghe toàn bộ đoạn ngắn bằng player. | Đúng giọng/nội dung, không méo hay mất đoạn bất thường. Nếu lỗi, ghi giây xảy ra và thiết bị mic/loa. |
| F08 | So thời lượng player/WAV với thời gian từ lúc capture bắt đầu tới Dừng, gồm cả khoảng lặng. | Hai thời lượng gần nhau. Ghi cụ thể, ví dụ capture 24 s / WAV 23.8 s / lệch −0.2 s; không so với riêng thời gian có tiếng nói. Nếu lệch đáng kể, báo số đo để đánh giá. |
| F09 | Tua player tới giữa file; bấm timestamp một đoạn transcript đã lưu. | Player đến gần vị trí tương ứng và phát đúng phần lân cận. Ghi đoạn/giây lệch; timestamp theo đoạn, không chính xác từng từ. |
| F10 | Tải WAV, TXT, JSON trước khi xóa; mở WAV bằng player và TXT/JSON bằng editor UTF-8. | Audio mở được; transcript/metadata đúng. Nếu S02 chỉ có tiếng Anh, ghi “export PASS; dấu Việt CHƯA TEST”; bổ sung file phiên dịch S03 sau để xác nhận dấu Việt, không đánh dấu toàn bộ tiêu chí đã đủ. |
| F11 | Đổi tên thành “Nghiệm thu Windows S02”; reload trang, mở lại Thư viện. | Tên mới và bản ghi vẫn còn. Ghi tên trước/sau. |
| F12 | Sau khi tải file bằng chứng, xóa đúng bản ghi thử S02 và xác nhận. | Không còn mở audio/transcript S02 qua UI sau reload. File đã tải trong Downloads vẫn tồn tại là bình thường. Không xóa bản ghi quan trọng để test. |
| F13 | Sau khi kết thúc S02, quay lại phần tạo phiên; chưa bấm Bắt đầu. | “Lưu bản ghi” đã trở về tắt. Chụp ảnh nếu vẫn bật. |

Windows lưu thư viện mặc định ở `%LOCALAPPDATA%\LectureBridge`. Đây là dữ liệu
riêng trên Windows; clone Git không chuyển bản ghi từ Ubuntu sang. Không cần
mở hoặc sửa SQLite để đánh giá các tiêu chí trên.

## 7. S03 tùy chọn — đổi chế độ ngay trên transcript và dịch CPU

Chỉ thử sau khi các lượt trên ổn định; có thể để F16–F19 `CHƯA TEST`. NLLB chạy
CPU nhưng vẫn dùng RAM/CPU đáng kể. Giữ ASR `tiny.en` trong lượt này để quan sát
riêng phần dịch. Không thêm `--translation` vào lệnh server khi muốn kiểm tra
hành vi xin tải model F16.

| ID | Thao tác cụ thể | PASS khi / bằng chứng cần ghi |
|---|---|---|
| F16 | Khi bộ dịch chưa có, chọn Song ngữ; nếu cần Bắt đầu một phiên ngắn để kích hoạt chuẩn bị. Chưa bấm tải ngay. | UI đề nghị tải bộ dịch và chỉ tải sau khi bạn bấm “Tải bộ dịch”. Nếu model đã có thì ghi CHƯA TEST — model đã cache; không cần xóa model. |
| F17 | Khi bộ dịch sẵn sàng, mở phiên Anh; đọc câu A, đợi chốt, đổi sang Song ngữ ngay trên màn hình. | Câu A giữ nguyên, phiên/mic không bị reset hoặc ngắt. Ghi thời điểm đổi và thời gian chờ trạng thái sẵn sàng. |
| F18 | Sau trạng thái dịch sẵn sàng, nói câu B và đợi chốt/dịch. | Câu B có bản Việt; câu A đã chốt trước lúc bật vẫn không được dịch bù. Lưu cả câu A/B và bản dịch để đối chiếu. |
| F19 | Chuyển về Tiếng Anh, nói câu C, đợi chốt rồi Dừng. | Không gửi dịch mới cho C. Transcript cũ vẫn còn; bản Việt cũ được ẩn ở chế độ Anh, không bị xóa. Chọn lại Song ngữ sau Dừng để xem bản dịch đã có của B. Việc dịch đã gửi trước khi tắt có thể hoàn tất muộn. |

Tải bộ dịch khoảng 2.5 GB có thể lâu: sau khi chủ động bấm tải, **Dừng phiên mic**
trong lúc chờ, giữ server hoạt động. Không để mic chạy nhiều phút chỉ để đợi tải.
Khi bộ dịch sẵn sàng, bắt đầu S03 mới và làm A → B → C ở trên. Dùng câu ngắn:

- A, trước bật dịch: “This sentence is spoken before translation is enabled.”
- B, sau bật dịch: “Students can review their notes after the lecture.”
- C, sau tắt dịch: “We are now reading English captions again.”

Nếu muốn bổ sung kiểm tra dấu Việt F10, bật lưu trước S03 rồi export TXT/JSON
sau Dừng. Thử thêm nút **Tiếng Việt**: đoạn đã dịch hiển thị bản Việt; đoạn chưa
có bản dịch có thể giữ tiếng Anh để không mất nội dung. Ghi quan sát này cạnh
F17/F18. Đây là dịch **lời nói tiếng Anh sang tiếng Việt**, không phải chuyển
`tiny.en` sang nhận diện lời nói tiếng Việt.

Điền thêm phần dịch trong mục 6 báo cáo: thời gian chuẩn bị, Anh chốt → Việt xuất
hiện, độ trễ Anh trước/sau, RAM/CPU quan sát được, lỗi hoặc nhãn “Chưa dịch”. Nếu
máy chậm/nóng thì Dừng và Ctrl+C; không cố tăng model hay thử đi thử lại.

## 8. S04 tùy chọn — iPad/Safari qua Tailscale

Cài Tailscale trên iPad, đăng nhập cùng tailnet với Windows. Server Windows
vẫn chạy ở `127.0.0.1:8000`. Trong PowerShell có quyền Administrator:

```powershell
tailscale serve --bg --yes http://127.0.0.1:8000
tailscale serve status
```

Nếu Tailscale yêu cầu bật HTTPS/Serve, làm theo đường dẫn cấu hình nó hiển thị.
Mở **URL HTTPS `https://...ts.net` đúng do lệnh trả về** trên Safari iPad.
`127.0.0.1` trên iPad không trỏ tới laptop. Không dùng Funnel hoặc mở public port.

F20: thử dọc/ngang, cho phép mic iPad, đọc vài câu tiếng Anh trong 15–30 giây,
Dừng. Xác nhận transcript và thao tác cảm ứng; giữ Safari ở foreground, màn
hình bật. Không mở thêm phiên mic trên laptop cùng lúc. Ghi model iPad/iPadOS,
Safari, mạng, URL loại HTTPS, mic đang dùng, lỗi bố cục; direct/relay chưa xác
nhận thì ghi `CHƯA XÁC NHẬN`. Ghi S04 riêng, không gộp kết quả mic iPad vào S01.

## 9. Model mặc định — lượt nghiệm thu chất lượng sau, không bắt buộc lần đầu

`tiny.en` xác nhận cài đặt GPU và luồng chức năng. Nó không đại diện cho độ chính
xác của model mặc định `distil-large-v3.5`. Chỉ khi tiny ổn định và bạn chủ động
muốn thử model mặc định: Dừng phiên, Ctrl+C server cũ, chờ GPU hạ nhiệt.

Tải model trước; bước tải không inference:

```powershell
uv run lecturebridge-models download --model distil-large-v3.5
```

Lệnh dưới **nạp model lớn hơn thật và không có watchdog**. Có thể hoãn hoàn toàn;
không suy ra model lớn an toàn chỉ từ tiny PASS. Nếu tự quyết định thử, vẫn giữ
cửa sổ theo dõi, chỉ EN, không dịch, 15–30 giây rồi Dừng/Ctrl+C:

```powershell
uv run lecturebridge-live --device cuda --model distil-large-v3.5
```

Ghi S05 riêng và dùng lại lời đọc để so chất lượng. `gpu-smoke.py` chỉ kiểm tra
tiny, không tự bảo vệ lệnh server này. Nếu chưa thử thì mục 8 báo cáo ghi
`Model mặc định: CHƯA TEST`; không cần phiên dài hoặc stress test.

## 10. Điền kết quả và gửi lại

- Mục 1–2: commit, cấu hình, điều kiện test và kết luận quan sát.
- Mục 3–4: output kiểm tra nhẹ và GPU smoke; phân biệt lỗi Tailscale với lỗi CUDA.
- Mục 5: một khối Sxx cho mỗi phiên thật; giữ cả phiên gặp lỗi.
- Mục 6: từng Fxx ghi trạng thái, ID phiên, số đo/file/ảnh. Chưa đủ các phần của
  một tiêu chí thì ghi rõ phần PASS và phần CHƯA TEST, không tự đánh dấu toàn bộ PASS.
- Mục 7: lỗi Bxx gồm thao tác, mong đợi, thực tế, log; không cần tái hiện máy sập.
- Mục 8–9: các phần chưa thử và danh sách tệp đính kèm.

Ví dụ một ô bằng chứng: `S02 | WAV 23.8 s, capture ~24 s; nghe rõ; file S02.wav`.
`FAIL` là đã thực hiện và sai; `BLOCKED` là không bắt đầu được vì điều kiện thiếu;
`CHƯA TEST` là chưa thử; số chưa đo ghi `CHƯA ĐO`, không ghi 0.

Gửi lại file Markdown đã điền, output smoke, lỗi liên quan và 2–4 câu gốc kèm
transcript/bản dịch nếu có. Chỉ cần audio ngắn tự tạo khi cần chẩn đoán ghi âm,
không cần toàn bộ bản ghi lớp học. Khi hoàn tất, Ctrl+C server và cửa sổ theo dõi.
Không cần bật phiên dài để đạt đủ mọi ô; báo cáo một phần vẫn đủ để xác định
bước tiếp theo nhỏ nhất.
