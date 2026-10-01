# LectureBridge

LectureBridge is a local-first live-caption prototype for English, Mandarin
Chinese, Japanese, and Korean with optional Vietnamese translation. An iPhone or iPad captures audio in Safari while a
Linux or Windows x86-64 computer performs inference locally.

```text
iPhone/iPad microphone -> Tailscale HTTPS -> Faster-Whisper -> source captions
                                                   \-> optional NLLB -> Vietnamese
```

The application prefers an NVIDIA GPU and safely falls back to CPU when CUDA
is unavailable. Recordings and transcripts are not saved by default.

The Local Studio testing build is now on **`main`**. Clone `main` for new
installations. See the [acceptance report template](docs/acceptance-report-template-vi.md)
to record your results; older handoff documents may still name `ubuntu/local-studio`.

## Local studio

- A Vietnamese reading interface with light/dark themes and adjustable text size.
- Switch original-language / Vietnamese / bilingual while the microphone keeps running.
- Select the spoken language at launch with `--language en|zh|ja|ko`; the UI labels
  the original transcript accordingly. Changing source language requires a server restart.
- Enable **Lưu bản ghi** before a session to keep WAV audio and committed text on
  the laptop. Recording is off again after each session.
- A local library with playback, approximate segment seeking, rename, TXT/JSON
  export, WAV download, and delete.
- Audio is never saved when recording is off. Temporary transcripts can still
  be exported before leaving the page.
- Translation loads on demand in an isolated CPU worker; it only translates new
  committed text. An explicit UI action is required to download missing weights.
- One active microphone session per server, maximum two hours. Keep Safari in
  the foreground. Disconnects retain received audio when saving was enabled;
  automatic reconnect/resume is not included.

Recordings live outside the repository: `%LOCALAPPDATA%\LectureBridge` on Windows
and `${XDG_DATA_HOME:-~/.local/share}/lecturebridge` on Linux. Use `--data-dir` to
choose another private directory. Data remains until you delete it; dual-boot
systems do not automatically share their libraries. The laptop must stay on to
browse recordings from an iPad. Anyone with access to this trusted local/tailnet
instance can access its library; it is not a multi-account cloud service.

## What is included

- High-accuracy English transcription with locked `distil-large-v3.5` weights.
- Smaller English-only `small.en`, `base.en`, and `tiny.en` fallback models.
- Multilingual `tiny`, `base`, `small`, `medium`, `large-v3-turbo`, and `large-v3`.
- Native Ubuntu/Linux and Windows 10/11 x86-64 setup.
- NVIDIA CUDA acceleration or a slower CPU `int8` fallback.
- Optional NLLB-200 distilled 600M translation on CPU.
- Tailnet-only HTTPS through Tailscale Serve; Funnel is not supported.

## Requirements

- A 64-bit Ubuntu/Linux or Windows 10/11 computer.
- Python 3.12 managed by [`uv`](https://docs.astral.sh/uv/).
- Tailscale on the computer and viewing device.
- For GPU inference: an NVIDIA driver, CUDA 12, and cuDNN 9. Linux CUDA
  runtime libraries are installed by the project; Windows libraries must be
  available on `PATH`.
- At least 10 GB free for the environment and default ASR model. Allow about
  13 GB when optional translation is also installed; larger/multiple ASR models
  and recordings require additional space.
- Permission to capture and process the audio source.

## Quick start

Linux:

```bash
git clone --branch main https://github.com/Nguyen-Le-Tuan/lecturebridge.git
cd lecturebridge
bash scripts/bootstrap-linux.sh
```

Windows PowerShell:

```powershell
git clone --branch main https://github.com/Nguyen-Le-Tuan/lecturebridge.git
Set-Location lecturebridge
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap-windows.ps1
```

The bootstrap scripts create `.venv`, install the locked dependencies, download
the immutable default model, verify its SHA-256 checksums, and run readiness
checks. Model weights remain outside Git.

Detailed instructions:

- [Linux setup](docs/setup-linux.md)
- [Windows setup](docs/setup-windows.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Classroom runbook](docs/classroom-runbook.md)
- [Public release checklist](docs/release-checklist.md)
- [Original Vietnamese project roadmap](docs/roadmap/lecture-translation-roadmap-vi.pdf)
- [Vietnamese beginner walkthrough](docs/lecturebridge-explained-for-a-12-year-old.md)

### Khởi động nhanh bằng tiếng Việt

Clone repo, chạy script tương ứng với hệ điều hành, rồi kiểm tra dòng
`NVIDIA GPU`. Nếu dòng này là `PASS`, LectureBridge đang dùng GPU; nếu là
`WARN`, chương trình vẫn chạy bằng CPU nhưng chậm hơn. Không copy `.venv` hoặc
model từ máy khác vì các file nhị phân phụ thuộc hệ điều hành.

## Run

Start the local server:

```bash
uv run lecturebridge-live --device auto
```

Open <http://127.0.0.1:8000> for a local check. To use an iPhone or iPad,
configure Tailscale Serve as described in the classroom runbook.

Force a device or choose a smaller model:

```bash
uv run lecturebridge-live --device cuda
uv run lecturebridge-live --device cpu --model tiny.en
```

Download and verify models explicitly:

```bash
uv run lecturebridge-models list
uv run lecturebridge-models download --model small.en
uv run lecturebridge-models verify --model small.en
uv run lecturebridge-models download --translation
```

Use the on-screen language buttons for on-demand translation. To explicitly
download and prewarm the non-commercial CPU model at launch:

```bash
uv run lecturebridge-live --translation
```

## Chọn ngôn ngữ và model từ nhẹ đến lớn

Ứng dụng hỗ trợ nguồn **Anh, Trung phổ thông (Mandarin), Nhật và Hàn → tiếng Việt**.
Chọn ngôn ngữ bằng `--language` khi khởi động server; UI tự đổi nút bản gốc thành
Tiếng Anh/Trung/Nhật/Hàn. Các nút Tiếng Việt và Song ngữ chỉ đổi cách đọc/bật dịch,
không thay ngôn ngữ microphone. Dừng phiên và Ctrl+C server trước khi đổi nguồn.

| Nguồn lời nói | Tham số | Model phù hợp |
|---|---|---|
| Tiếng Anh | `--language en` (mặc định) | Model tiếng Anh hoặc đa ngôn ngữ |
| Tiếng Trung phổ thông | `--language zh` | Model đa ngôn ngữ, không có `.en` |
| Tiếng Nhật | `--language ja` | Model đa ngôn ngữ, không có `.en` |
| Tiếng Hàn | `--language ko` | Model đa ngôn ngữ, không có `.en` |

Luồng xử lý là **lời nói → transcript đúng ngôn ngữ nguồn → NLLB dịch sang Việt**.
Không dùng chức năng Whisper dịch sang tiếng Anh làm bước trung gian. `zh` dùng
mã NLLB `zho_Hans`; nếu transcript nguồn là chữ phồn thể, chọn `--language zh-Hant`
để dùng `zho_Hant`. Cả hai dùng ASR Mandarin `zh`; tùy chọn này không phải bộ
chuyển đổi giản thể/phồn thể và không cam kết hỗ trợ mọi phương ngữ Trung Quốc.

### Model đa ngôn ngữ: Trung, Nhật, Hàn và Anh

Xếp theo **số tham số tăng dần**, không phải bảng xếp hạng chất lượng hoặc độ trễ:

| Model | Tham số | File tải xấp xỉ | Gợi ý thử |
|---|---|---|---|
| `tiny` | 39 M | 78 MB | Nhẹ nhất, kiểm tra luồng; chưa dùng để kết luận chất lượng dịch/bài giảng. |
| `base` | 74 M | 148 MB | Bước tiếp theo khi tiny ổn định. |
| `small` | 244 M | 486 MB | Mức trung gian để so chất lượng và độ trễ. |
| `medium` | 769 M | 1.53 GB | Model lớn hơn; chỉ thử riêng sau khi kiểm tra tài nguyên. |
| `large-v3-turbo` | 809 M | 1.62 GB | Bản tối ưu tốc độ của large-v3; nhiều tham số hơn medium không đồng nghĩa chậm hơn. |
| `large-v3` | 1,550 M | 3.09 GB | Lớn nhất đang hỗ trợ; cần nghiệm thu riêng chất lượng và tải máy. |

Số tham số và đặc điểm turbo theo [Whisper upstream](https://github.com/openai/whisper#available-models-and-languages).
Chất lượng/tốc độ phụ thuộc ngôn ngữ, nguồn âm và máy. Dung lượng tải tính từ
`models.lock.json`, theo MB/GB thập phân; **không phải VRAM/RAM cần khi chạy**,
chưa gồm Python/NLLB. Các model được khóa revision và kiểm tra SHA-256 khi tải.

### Model chỉ tiếng Anh

| Model | File tải xấp xỉ | Khi dùng |
|---|---|---|
| `tiny.en` | 78 MB | Smoke test tiếng Anh, nhẹ nhất trong nhóm này |
| `base.en` | 148 MB | Bước tiếp theo cho tiếng Anh |
| `small.en` | 486 MB | Mức trung gian tiếng Anh |
| `distil-large-v3.5` | 1.52 GB | Mặc định tiếng Anh, ưu tiên chất lượng |

**Không dùng `.en` hoặc `distil-large-v3.5` để nhận tiếng Trung/Nhật/Hàn.** CLI
sẽ từ chối kết hợp đó trước khi tải/nạp model. Khi không truyền `--model`, mặc định
vẫn là `distil-large-v3.5`; vì vậy hãy truyền cả model đa ngôn ngữ và `--language`
cho nguồn khác tiếng Anh. `medium.en`, `large` và tên rút gọn `turbo` chưa là tên
CLI hợp lệ; dùng chính xác tên trong bảng.

### Bắt đầu thử tiếng Trung → tiếng Việt

Các lệnh dùng được trên PowerShell và Bash, tại repo sau `uv sync --locked`.
Tải model trước; bước này chưa chạy inference:

```bash
uv run lecturebridge-models download --model tiny
```

Đóng server và các ứng dụng GPU khác rồi tự chạy smoke giới hạn:

```bash
uv run python scripts/gpu-smoke.py --model tiny --language zh
```

Script chỉ cho `tiny.en` hoặc `tiny`, xử lý 1 giây im lặng, không dịch; không thể
truyền model lớn vào watchdog này. Cần thấy `tiny executed on cuda` PASS; smoke
không đánh giá khả năng nhận tiếng Trung. Nếu watchdog dừng/deep test FAIL thì dừng
và giữ output. Tailscale FAIL là mục riêng; localhost không cần Tailscale.

Khi smoke đạt và máy ổn định, thử bản gốc tiếng Trung 15–30 giây trước:

```bash
uv run lecturebridge-live --device cuda --model tiny --language zh
```

Mở <http://127.0.0.1:8000>. Sau khi xác nhận có transcript tiếng Trung, chọn
**Song ngữ** hoặc **Tiếng Việt**. Nếu thiếu NLLB, chủ động bấm **Tải bộ dịch**;
dừng mic khi chờ tải/chuẩn bị, rồi bắt đầu lượt ngắn mới khi bộ dịch sẵn sàng.
Chỉ phần mới được dịch; các đoạn trước khi bật không bị dịch bù.

Đổi model trong lượt riêng: chọn **một cặp lệnh**, không chạy tất cả cùng lúc.
Dừng phiên rồi Ctrl+C server cũ trước mỗi cặp:

```bash
uv run lecturebridge-models download --model base
uv run lecturebridge-live --device cuda --model base --language zh
```

```bash
uv run lecturebridge-models download --model small
uv run lecturebridge-live --device cuda --model small --language zh
```

```bash
uv run lecturebridge-models download --model medium
uv run lecturebridge-live --device cuda --model medium --language zh
```

```bash
uv run lecturebridge-models download --model large-v3-turbo
uv run lecturebridge-live --device cuda --model large-v3-turbo --language zh
```

```bash
uv run lecturebridge-models download --model large-v3
uv run lecturebridge-live --device cuda --model large-v3 --language zh
```

### Tiếng Nhật, Hàn, Anh và CPU fallback

Giữ cùng model đa ngôn ngữ và thay ngôn ngữ; mỗi lệnh là một lượt server riêng:

```bash
uv run lecturebridge-live --device cuda --model tiny --language ja
uv run lecturebridge-live --device cuda --model tiny --language ko
uv run lecturebridge-live --device cuda --model tiny --language en
uv run lecturebridge-live --device cpu --model tiny --language zh
```

CPU fallback có thể chậm. Không cần chạy GPU smoke nếu chủ động dùng CPU.
Với tiếng Anh, lệnh tải/chạy riêng từng model vẫn là:

```bash
uv run lecturebridge-models download --model tiny.en
uv run lecturebridge-live --device cuda --model tiny.en --language en
```

```bash
uv run lecturebridge-models download --model base.en
uv run lecturebridge-live --device cuda --model base.en --language en
```

```bash
uv run lecturebridge-models download --model small.en
uv run lecturebridge-live --device cuda --model small.en --language en
```

```bash
uv run lecturebridge-models download --model distil-large-v3.5
uv run lecturebridge-live --device cuda --model distil-large-v3.5 --language en
```

`--device cuda` yêu cầu CUDA; `--device auto` ưu tiên CUDA khi đủ điều kiện,
nếu không thì chọn CPU. `lecturebridge-models list` liệt kê ASR theo dung lượng
từ nhỏ đến lớn, rồi đến bộ dịch. Không dùng `download --all` cho lượt đầu.

### Giới hạn và cách nghiệm thu ngắn

- **Các lệnh `live` không có watchdog nhiệt độ.** Smoke tiny không bảo vệ server
  hoặc xác nhận model lớn chạy ổn. Model lớn không bắt buộc cho báo cáo đầu tiên.
- Mỗi model mới: thử bản gốc 15–30 giây trước, chưa dịch. Chỉ bật dịch trong lượt
  riêng và giữ nguyên ASR để đo ảnh hưởng; không chạy stress test hoặc nhiều server.
- NLLB vẫn chạy CPU int8, hai luồng; GPU mạnh hơn không trực tiếp tăng tốc dịch.
  Bản thử đã có báo cáo dịch trễ hàng chục giây, chưa cam kết tốc độ thời gian thực.
- NLLB tải thêm khoảng 2.5 GB, chỉ dùng phi thương mại. Mã nguồn ngôn ngữ dựa trên
  [token ngôn ngữ NLLB](https://huggingface.co/facebook/nllb-200-distilled-600M/blob/main/special_tokens_map.json).
- Hỗ trợ mới đã kiểm tra đường truyền ngôn ngữ, UI và export bằng dữ liệu giả;
  chất lượng ASR/dịch Trung/Nhật/Hàn trên máy thật vẫn cần người dùng nghiệm thu.
- Ghi commit, model, `--language`, câu gốc và transcript/bản dịch; đo riêng trễ
  bản gốc và bản Việt. JSON lưu mã ngôn ngữ trong từng đoạn; bản ghi cũ vẫn mở được.

Có thể theo dõi GPU ở terminal khác:

```bash
nvidia-smi --id=0 --query-gpu=temperature.gpu,memory.used,memory.free,utilization.gpu --format=csv -l 1
```

Dừng phiên rồi Ctrl+C nếu GPU đạt 75°C, VRAM trống dưới 1024 MiB hoặc máy phản hồi
kém. Đây là ngưỡng bảo thủ của đợt thử, không phải bảo đảm chống treo máy.

## Offline transcription and verification

Place a permitted recording under `data/private/`; the directory and common
audio formats are ignored by Git.

```bash
uv run lecturebridge-preflight --device auto
uv run lecturebridge-preflight --device cuda --deep
uv run lecturebridge-transcribe data/private/example.m4a --device auto
```

`--deep` loads and executes the model, which catches CUDA/cuDNN problems that
`nvidia-smi` alone cannot detect.

## Development

```bash
uv sync --locked
uv run ruff check .
uv run pytest -q -m "not gpu"
node --test tests/test_worklet.cjs
uv build
uv run python scripts/check_repository.py
```

GPU tests are disabled unless `--run-gpu` is supplied, even when the audio
environment variable exists. Do not run the debate stress test for the first
hardware check: start with the bounded `tiny.en` check in the Windows handoff.
The optional debate acceptance test requires a permitted audio file:

```bash
LECTUREBRIDGE_DEBATE_AUDIO=/path/to/permitted.wav \
  uv run pytest -q --run-gpu tests/test_debate_stress.py
```

GitHub-hosted CI tests both Linux and Windows CPU-compatible code paths. GPU
acceptance must run manually on trusted NVIDIA hardware.

## Privacy, licenses, and limitations

Do not commit classroom recordings, transcripts, cookies, tokens, `.env`
files, model weights, or generated output. Confirm the recording policy and
obtain permission before enabling the microphone.

One mono microphone cannot reliably recover overlapping speech. Captions may
contain errors and must not be treated as an authoritative transcript.

LectureBridge source and project-owned documentation are licensed under the
[MIT License](LICENSE). Model weights and dependencies retain their own terms;
see [third-party notices](THIRD_PARTY_NOTICES.md). In particular, the optional
NLLB weights are CC-BY-NC-4.0 and are not licensed for commercial use.
