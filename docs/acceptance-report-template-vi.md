# Báo cáo nghiệm thu LectureBridge Local Studio

> Sao chép mẫu này rồi điền vào các dấu `...`. Mục chưa đo ghi `CHƯA ĐO`, mục
> chưa thử ghi `CHƯA TEST`; không điền 0 hoặc PASS thay cho phần chưa kiểm tra.
> Không cần chạy thêm bài nặng để điền đủ. Dừng ở bất kỳ bước nào nếu máy phản hồi kém.
> Dùng câu nói do bạn tự tạo hoặc audio được phép sử dụng. Không gửi token, toàn bộ
> biến môi trường hoặc bản ghi lớp học riêng tư. Có thể che tên máy/địa chỉ tailnet.

## 1. Tóm tắt để đánh giá nhanh

- Ngày, giờ và múi giờ test: ...
- Nhánh Git: ...
- Commit thực tế (`git rev-parse --short HEAD`): ...
- Có sửa code/config tại máy Windows không? Không / Có: ...
- Tôi đang test: ứng dụng thật / fixture giả lập / cả hai, ghi riêng từng lượt.
- Kết quả chung tự quan sát: Dùng được / Có lỗi / Bị chặn / Chưa đủ dữ liệu.
- Vấn đề nghiêm trọng nhất: ...
- Máy có treo, tắt nguồn, khởi động lại hoặc mất driver không? ...
- Tôi đã dừng tại bước nào và vì sao? ...
- Tôi muốn bạn đánh giá hoặc sửa gì trước? ...

## 2. Môi trường thực tế

| Thông số | Giá trị |
|---|---|
| Máy chạy server | ... |
| Windows phiên bản + OS build | ... |
| CPU | ... |
| RAM tổng (GB) | ... |
| RAM đang dùng trước test (GB, nếu quan sát được) | ... |
| GPU | ... |
| VRAM tổng (MiB) | ... |
| NVIDIA driver | ... |
| CUDA Toolkit / cuDNN, nếu biết | ... |
| Python trong môi trường `uv` | ... |
| Phiên bản `uv` | ... |
| Trình duyệt trên laptop + phiên bản | ... |
| Microphone dùng thực tế | Laptop / Tai nghe / USB / iPad / Khác: ... |
| Ổ lưu thư viện còn trống (GB) | ... |
| Có dùng `--data-dir` không? | Không / Có: ... |
| Nguồn điện | Cắm sạc / Pin |
| Máy đặt ở đâu, thông gió thế nào? | ... |
| Ứng dụng khác đang mở, nhất là ứng dụng GPU | ... |

Lệnh lấy thông tin, không chạy inference:

```powershell
git branch --show-current
git rev-parse --short HEAD
git status --short
uv --version
uv run python --version
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
```

Nếu lỗi CUDA, bổ sung kết quả dưới đây; che tên thư mục cá nhân nếu muốn:

```powershell
where.exe cublas64_12.dll
where.exe cudnn64_9.dll
where.exe cudnn_ops64_9.dll
```

```text
Dán kết quả môi trường/lỗi DLL cần thiết ở đây.
```

## 3. Cài đặt và kiểm tra nhẹ

Quy ước: `PASS` = đã thử và đúng; `FAIL` = đã thử nhưng sai;
`BLOCKED` = không thể bắt đầu vì điều kiện bên ngoài;
`CHƯA TEST` = chưa thực hiện. Điền lý do khi không PASS.

| Kiểm tra | Trạng thái | Kết quả hoặc lỗi |
|---|---|---|
| Lấy đúng nhánh `codex/local-studio` | ... | ... |
| `uv sync --locked` | ... | ... |
| `uv run ruff check .` | ... | ... |
| `uv run pytest -q -m "not gpu"` | ... | ... passed / ... skipped hoặc deselected |
| `uv build` | ... | ... |
| `node --test tests/test_worklet.cjs` — tùy chọn nếu có Node | ... | ... |

```text
Dán lỗi cài đặt/test nếu có, gồm lệnh đã chạy và phần traceback liên quan.
```

## 4. GPU smoke test — chỉ tiny.en

Chỉ thực hiện khi bạn sẵn sàng test GPU. Đóng server và ứng dụng GPU khác trước.
Không bật dịch hoặc chạy thêm benchmark cùng lúc.

```powershell
uv run lecturebridge-models download --model tiny.en
uv run python scripts/gpu-smoke.py
```

Script chỉ nạp `tiny.en` và xử lý 1 giây im lặng. Nó từ chối bắt đầu nếu nhiệt độ
trên 65°C; dừng nếu đạt 75°C, VRAM trống dưới 1024 MiB, quá 60 giây hoặc không
đọc được cảm biến. Đây là ngưỡng bảo thủ của bài test, không phải bảo đảm máy
không thể treo. Nếu script dừng hoặc có lỗi, ghi lại rồi **dừng tại đây**.

- Tải/kiểm tra model tiny.en: PASS / FAIL / CHƯA TEST.
- Watchdog có cho bắt đầu inference không? Có / Không / Không rõ.
- Dòng `Deep model smoke test`: PASS / FAIL / Không xuất hiện.
- Dòng kết quả có ghi `tiny.en executed on cuda` không? ...
- Các dòng preflight khác bị WARN/FAIL (ví dụ Tailscale), tách khỏi lỗi GPU: ...
- Kết thúc bằng: bình thường / watchdog / Ctrl+C / crash / khác: ...
- Exit code ngay sau lệnh (`$LASTEXITCODE`): ...
- Tổng thời gian lệnh, ước lượng giây: ...

| Chỉ số | Trước test | Giá trị cao nhất/thấp nhất tôi quan sát được | Sau test |
|---|---|---|---|
| Nhiệt độ GPU (°C) | ... | Cao nhất: ... | ... |
| VRAM đã dùng (MiB) | ... | Cao nhất: ... | ... |
| VRAM còn trống (MiB) | ... | Thấp nhất: ... | ... |
| RAM hệ thống đang dùng (GB), nếu có | ... | Cao nhất: ... | ... |

Các giá trị quan sát thủ công không phải peak được đo liên tục chính xác.
Nếu không quan sát được, ghi `CHƯA ĐO`.

```text
Dán toàn bộ output của gpu-smoke.py ở đây, gồm thông báo watchdog nếu có.
```

## 5. Nhật ký từng phiên thật

Chỉ tiếp tục nếu bài smoke test đã đạt và máy vẫn ổn định. Lượt đầu dùng tiếng Anh,
không lưu audio, không bật dịch; nói trong 15–30 giây rồi bấm Dừng phiên.

```powershell
uv run lecturebridge-live --device cuda --model tiny.en
```

Mở `http://127.0.0.1:8000`. Server thật này **không có watchdog nhiệt độ**.
Quan sát máy, dừng phiên rồi Ctrl+C nếu nóng hoặc phản hồi kém. Không tăng sang
model lớn, chạy stress test hoặc kéo dài phiên chỉ để hoàn thành mẫu.

Cửa sổ PowerShell thứ hai, nếu muốn theo dõi GPU:

```powershell
nvidia-smi --id=0 --query-gpu=temperature.gpu,memory.used,memory.free,utilization.gpu --format=csv -l 1
```

Dừng cửa sổ theo dõi bằng Ctrl+C sau test. Đơn vị VRAM là MiB, không phải GB.

**Lặp khối dưới đây cho mỗi phiên đã thực sự thử. Không gộp nhiều phiên thành một.**

### Phiên S01

- Ngày/giờ bắt đầu: ...
- Lệnh khởi động server chính xác: `...`
- Model và device đã yêu cầu: ...
- Device thực tế xác nhận từ output: CUDA / CPU / CHƯA XÁC NHẬN.
- Ứng dụng thật hay fixture? ...
- Thiết bị mở UI và trình duyệt: ...
- Kết nối: localhost / Tailscale HTTPS trực tiếp / Tailscale relay / Không rõ.
- Chế độ: Anh / Việt / Song ngữ; đổi chế độ ở thời điểm nào: ...
- Lưu bản ghi: Bật / Tắt.
- Nguồn âm: Tôi tự nói / File của tôi / Nguồn được cho phép khác: ...
- Accent, tốc độ nói, khoảng cách tới mic, tiếng ồn: ...
- Thời lượng thực tế: ... giây.
- Model đã được tải trước và server đã ready chưa? ...
- Thời gian chờ server ready, nếu đã quan sát: ... giây / CHƯA ĐO.
- Kết thúc: Dừng phiên / Mất mạng / Đóng trang / Ctrl+C / Lỗi khác: ...

| Chỉ số của riêng phiên này | Giá trị | Cách đo |
|---|---|---|
| Từ lúc bắt đầu nói đến chữ đầu tiên | ... giây / CHƯA ĐO | Ước lượng / Đồng hồ / Video |
| Từ lúc kết thúc một câu đến khi đoạn cuối được chốt | ... giây / CHƯA ĐO | ... |
| Độ trễ xử lý lớn nhất UI hiển thị | ... giây / CHƯA ĐO | Quan sát nhãn độ trễ |
| Từ lúc bấm Dừng đến “Phiên học đã hoàn tất” | ... giây / CHƯA ĐO | ... |
| GPU nóng nhất quan sát được | ... °C / CHƯA ĐO | ... |
| VRAM dùng cao nhất / còn trống thấp nhất | ... / ... MiB / CHƯA ĐO | ... |
| RAM hệ thống đang dùng cao nhất | ... GB / CHƯA ĐO | Task Manager / Khác |

Không coi nhãn “Độ trễ xử lý” trên UI là độ trễ end-to-end. Một phiên ngắn không đủ
để tính p95, tỷ lệ session success, độ ổn định dài hạn hoặc hiệu năng lớp học.

## 6. Kết quả chức năng

Điền ID phiên liên quan để đối chiếu với mục 5. Các mục chưa thử để nguyên CHƯA TEST.
Dịch và iPad là các lượt **tùy chọn sau**, không phải điều kiện để gửi báo cáo đầu tiên.

| ID | Thao tác và kết quả mong đợi | Trạng thái | Phiên / Thực tế / Bằng chứng |
|---|---|---|---|
| F01 | Mở UI, chữ và nút không chồng/tràn màn hình | CHƯA TEST | ... |
| F02 | Xin quyền mic, Bắt đầu/Dừng hoạt động, Stop tắt mic | CHƯA TEST | ... |
| F03 | Tiếng Anh xuất hiện và được giữ sau khi Dừng | CHƯA TEST | ... |
| F04 | Tắt lưu: không có bản ghi mới trong Thư viện | CHƯA TEST | ... |
| F05 | Không lưu vẫn tải được TXT của phiên trước khi rời trang | CHƯA TEST | ... |
| F06 | Lượt riêng bật lưu: có chỉ báo đang lưu và xuất hiện bản ghi khi Dừng | CHƯA TEST | ... |
| F07 | Nghe lại: audio nghe được, đúng giọng/nội dung, không méo hoặc mất đoạn bất thường | CHƯA TEST | ... |
| F08 | Thời lượng file audio gần bằng thời lượng capture; ghi chênh lệch cụ thể | CHƯA TEST | ... |
| F09 | Tua audio và bấm timestamp của transcript tới gần đoạn tương ứng | CHƯA TEST | ... |
| F10 | WAV/TXT/JSON tải được; mở file thấy đúng nội dung và dấu tiếng Việt | CHƯA TEST | ... |
| F11 | Đổi tên; tải lại trang vẫn thấy tên và bản ghi | CHƯA TEST | ... |
| F12 | Xóa bản ghi thử nghiệm; audio/transcript không còn truy cập được qua UI | CHƯA TEST | ... |
| F13 | Kết thúc phiên: “Lưu bản ghi” tự trở về tắt cho phiên kế tiếp | CHƯA TEST | ... |
| F14 | Sáng/tối và tăng/giảm cỡ chữ hoạt động | CHƯA TEST | ... |
| F15 | Cuộn lên đọc lại không bị kéo xuống; nút “Về nội dung mới” hoạt động | CHƯA TEST | ... |
| F16 | Dịch tùy chọn: thiếu model thì đề nghị tải, không tự tải trước khi đồng ý | CHƯA TEST | ... |
| F17 | Dịch tùy chọn: đổi Anh → Song ngữ không reset transcript/ngắt mic | CHƯA TEST | ... |
| F18 | Dịch tùy chọn: phần mới có bản Việt; phần trước khi bật không bị dịch bù | CHƯA TEST | ... |
| F19 | Dịch tùy chọn: về Anh ngừng gửi việc dịch mới, giữ nội dung đã có | CHƯA TEST | ... |
| F20 | iPad tùy chọn: mic hoạt động qua HTTPS Tailscale và UI dùng được dọc/ngang | CHƯA TEST | ... |

### Chất lượng nội dung — nếu có mẫu ngắn được phép chia sẻ

Không cần đính kèm toàn bộ audio. Với tiny.en, đây là kiểm tra luồng và lỗi thô;
không suy ra chất lượng của model mặc định từ kết quả tiny.en.

- Mẫu thuộc phiên: ...
- Loại nội dung: Câu tự đọc / Bài giảng / Hội thoại / Khác: ...
- Những gì tôi thực sự đã nói, gồm cả chỗ đọc sai nếu có:

```text
Dán 2–4 câu đối chiếu ở đây.
```

- Transcript đã chốt ứng dụng trả về:

```text
Dán transcript tương ứng ở đây.
```

- Bản dịch tương ứng, nếu đã bật và test:

```text
Dán bản dịch hoặc ghi CHƯA TEST.
```

- Từ/tên riêng bị nhận sai hoặc ý bị dịch sai: ...
- Có mất câu, lặp câu, hoặc đổi chữ sau khi đã chốt không? ...
- Tôi có đọc kịp hơn nhờ transcript không? Có / Một phần / Không; vì sao: ...

### Chỉ điền nếu đã thử dịch thật

Bộ dịch chạy CPU nhưng vẫn dùng RAM/CPU đáng kể; có thể hoãn lượt này.

- Phiên: ...
- Bộ dịch: có sẵn / tôi đã chủ động bấm tải / chưa tải.
- Từ lúc bật dịch tới trạng thái sẵn sàng: ... giây / CHƯA ĐO.
- Từ lúc câu Anh được chốt tới lúc có bản Việt: ... giây / CHƯA ĐO.
- Độ trễ transcript Anh trước và sau bật dịch: ... / ... giây / CHƯA ĐO.
- RAM trước và sau bật dịch: ... / ... GB / CHƯA ĐO.
- CPU % quan sát được, nếu có: ...
- Model ASR dùng trong lượt dịch này: ...
- Tình trạng hàng đợi hoặc thông báo “Chưa dịch”/lỗi: ...

### Chỉ điền nếu đã thử iPad thật

- iPad model / iPadOS / Safari: ...
- Host chạy Ubuntu hay Windows: ...
- Cùng Wi-Fi hay khác mạng: ...
- Tailscale direct / relay / CHƯA XÁC NHẬN: ...
- Truy cập bằng HTTPS: Có / Không.
- Mic đang dùng là mic iPad hay thiết bị khác: ...
- Để Safari ở foreground và màn hình bật suốt phiên: Có / Không.
- Lỗi bố cục, thao tác cảm ứng hoặc quyền mic: ...
- Nếu vô tình khóa màn hình/chuyển app: mô tả điều đã xảy ra, không cần cố tái hiện: ...

## 7. Báo lỗi — lặp khối cho từng lỗi

### Lỗi B01: [Tên ngắn]

- Mức độ: Máy sập/treo / Mất dữ liệu / Chặn sử dụng / Sai nội dung / Lỗi giao diện.
- Phiên và thời điểm xảy ra: ...
- Model/device/chế độ đọc/lưu bản ghi lúc đó: ...
- Các bước tôi vừa làm:
  1. ...
  2. ...
  3. ...
- Tôi mong đợi: ...
- Thực tế xảy ra: ...
- Số lần đã gặp / số lần thực sự đã thử: ... / ...
- File/bản ghi còn giữ được không? ...
- Cách tôi dừng hoặc khôi phục: ...
- Tên ảnh/log đính kèm: ...

```text
Dán thông báo lỗi và traceback liên quan ở đây.
Không gửi token, toàn bộ env, transcript hoặc audio riêng tư ngoài ý muốn.
```

Nếu máy sập, không cần lặp lại để quay video: ghi dấu hiệu trước khi sập,
thời điểm gần đúng, model đang chạy và thông tin Windows Reliability Monitor
hoặc Event Viewer nếu bạn đã có. Để trống nếu chưa biết cách lấy.

## 8. Những gì chưa được nghiệm thu

- Windows GPU: ...
- Dịch NLLB thật: ...
- Safari/iPad thật: ...
- Model mặc định `distil-large-v3.5`: ...
- Chất lượng lớp học/đối chiếu transcript chuẩn: ...
- Phiên dài, mất mạng/khôi phục: ...
- Khác: ...

Tôi chỉ xác nhận những lượt đã ghi trong báo cáo này, không coi test UI giả lập,
CI hoặc một lần smoke test là bằng chứng mọi tính năng đã chạy ổn ngoài thực tế.

## 9. Các file gửi kèm và yêu cầu đánh giá

- Báo cáo này: ...
- Log đã chọn lọc: ...
- Ảnh/video ngắn nếu có: ...
- TXT/JSON của câu thử do tôi tự tạo, nếu có: ...

Nhờ bạn dựa trên commit, cấu hình và bằng chứng ở trên để:

1. Phân biệt lỗi cài đặt/runtime, kết nối, UI, ghi âm, ASR và dịch.
2. Xác định phần nào PASS, phần nào cần sửa và phần nào vẫn chưa có bằng chứng.
3. Đề xuất bản sửa hoặc bài kiểm tra tiếp theo nhỏ nhất; không tự chạy GPU,
   benchmark, stress test hoặc model lớn.
4. Cập nhật mức độ sẵn sàng của MVP local; không đồng nhất với MVP cloud/freemium.
