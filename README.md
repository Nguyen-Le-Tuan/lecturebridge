# LectureBridge

LectureBridge is a local-first English live-caption prototype with optional
Vietnamese translation. An iPhone or iPad captures audio in Safari while a
Linux or Windows x86-64 computer performs inference locally.

```text
iPhone/iPad microphone -> Tailscale HTTPS -> Faster-Whisper -> English captions
                                                   \-> optional NLLB -> Vietnamese
```

The application prefers an NVIDIA GPU and safely falls back to CPU when CUDA
is unavailable. Recordings and transcripts are not saved by default.

The Local Studio testing build is now on **`main`**. Clone `main` for new
installations. See the [acceptance report template](docs/acceptance-report-template-vi.md)
to record your results; older handoff documents may still name `ubuntu/local-studio`.

## Local studio

- A Vietnamese reading interface with light/dark themes and adjustable text size.
- Switch English / Vietnamese / bilingual while the microphone keeps running.
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
- Smaller `small.en`, `base.en`, and `tiny.en` fallback models.
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
  13 GB when optional translation is also installed.
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

## Chọn model từ nhẹ đến lớn

Bản hiện tại hỗ trợ **4 model ASR**, theo thứ tự kích thước bên dưới.
`distil-large-v3.5` là model lớn nhất **được LectureBridge hỗ trợ hiện tại** và
là mặc định khi không truyền `--model`. Các tên như `medium.en`, `large-v3`
hoặc `large-v3-turbo` chưa nằm trong danh sách CLI/manifest, nên chưa chạy được
bằng cách thay tên trong lệnh.

| Model | Tổng dung lượng file model xấp xỉ | Gợi ý lựa chọn |
|---|---|---|
| `tiny.en` | 78 MB | Bắt đầu ở đây: kiểm tra cài đặt, GPU, mic và luồng UI; chưa dùng để kết luận chất lượng bài giảng. |
| `base.en` | 148 MB | Bước thử tiếp theo khi tiny chạy ổn và muốn thử model lớn hơn nhưng vẫn gọn. |
| `small.en` | 486 MB | Lựa chọn trung gian để đối chiếu chất lượng transcript và độ trễ trước khi thử model mặc định. |
| `distil-large-v3.5` | 1.52 GB | Model mặc định ưu tiên chất lượng tiếng Anh; thử sau khi các lượt nhỏ ổn định và đã xem tài nguyên còn trống. |

Dung lượng trên được tính từ `models.lock.json`, theo MB/GB thập phân; **không
phải lượng VRAM/RAM cần khi chạy** và chưa gồm môi trường Python hoặc NLLB.
Model lớn hơn không bảo đảm tốt hơn trên mọi nguồn âm; hãy so cùng một đoạn nói,
ghi model, độ chính xác quan sát được và độ trễ. Cấu hình máy mạnh hơn vẫn cần
kiểm tra thực tế, không suy ra mức VRAM tối thiểu chỉ từ kích thước file.

### Tải và chạy từng model trên Windows hoặc Ubuntu

Các lệnh dưới dùng được trong PowerShell và Bash, tại thư mục repo sau
`uv sync --locked`. **Chỉ chọn một model mỗi lượt**, không chạy tất cả server
đồng thời. Lệnh `download` tải và kiểm tra file; lệnh `live` nạp model và chạy
inference khi nhận audio. Dừng phiên trên UI rồi Ctrl+C server trước khi đổi model.

**1. tiny.en — lượt đầu:**

```bash
uv run lecturebridge-models download --model tiny.en
uv run python scripts/gpu-smoke.py
```

Chỉ tiếp tục nếu dòng deep test xác nhận `tiny.en executed on cuda` PASS và
máy ổn định. Nếu watchdog dừng hoặc deep test FAIL, giữ output để chẩn đoán;
không chuyển sang model lớn. Tailscale FAIL là mục riêng, không đồng nghĩa
CUDA FAIL; localhost không cần Tailscale. Chạy smoke khi server đã dừng.

```bash
uv run lecturebridge-live --device cuda --model tiny.en
```

**2. base.en — lượt riêng sau tiny:**

```bash
uv run lecturebridge-models download --model base.en
uv run lecturebridge-live --device cuda --model base.en
```

**3. small.en — lượt riêng khi muốn thử mức trung gian:**

```bash
uv run lecturebridge-models download --model small.en
uv run lecturebridge-live --device cuda --model small.en
```

**4. distil-large-v3.5 — lớn nhất trong bản hiện tại:**

```bash
uv run lecturebridge-models download --model distil-large-v3.5
uv run lecturebridge-live --device cuda --model distil-large-v3.5
```

Mở <http://127.0.0.1:8000>. Lượt đầu với mỗi model chỉ thử tiếng Anh trong
15–30 giây, chưa bật dịch, rồi Dừng để quan sát kết quả. **Các lệnh `live`
không có watchdog nhiệt độ**; `gpu-smoke.py` chỉ bảo vệ lượt smoke tiny,
không bảo vệ server hoặc xác nhận model lớn chạy ổn. Có thể theo dõi ở terminal khác:

```bash
nvidia-smi --id=0 --query-gpu=temperature.gpu,memory.used,memory.free,utilization.gpu --format=csv -l 1
```

Dừng phiên rồi Ctrl+C nếu GPU đạt 75°C, VRAM trống dưới 1024 MiB hoặc máy
phản hồi kém. Đây là ngưỡng bảo thủ cho đợt thử, không phải bảo đảm chống treo máy.
Không cần thử đủ bốn model hoặc chạy benchmark để gửi báo cáo đầu tiên.

### CPU fallback và dịch tiếng Việt

Nếu không dùng NVIDIA CUDA, bắt đầu bằng CPU với tiny; bỏ qua bài GPU smoke:

```bash
uv run lecturebridge-live --device cpu --model tiny.en
```

`--device cuda` yêu cầu CUDA và báo lỗi nếu không khả dụng; `--device auto`
ưu tiên CUDA khi đủ điều kiện, nếu không thì chọn CPU. CPU fallback có thể chậm,
đặc biệt với model lớn.

Bốn lựa chọn trên dùng cho **transcript tiếng Anh**. Dịch Anh → Việt dùng
model NLLB riêng, bật bằng nút Tiếng Việt/Song ngữ trên UI; nó vẫn chạy CPU
với hai luồng dù GPU mạnh hơn. Bản thử hiện có báo cáo dịch trễ hàng chục giây:
hãy thử dịch trong lượt riêng, giữ nguyên model ASR và đo độ trễ Anh/Việt riêng.
NLLB chỉ dùng phi thương mại; tải bộ dịch có thể cần thêm khoảng 2.5 GB.

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
