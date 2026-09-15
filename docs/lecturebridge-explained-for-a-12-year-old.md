# LectureBridge hoạt động thế nào? Bản giải thích cho bạn 12 tuổi

## 1. LectureBridge là gì?

Hãy tưởng tượng em đang ngồi trong lớp. Mọi người nói tiếng Anh rất nhanh, nhưng
em muốn đọc phụ đề tiếng Anh trên iPad. Khi cần, em cũng có thể bật bản dịch
tiếng Việt.

LectureBridge là một “cây cầu” làm việc đó:

```text
Giọng nói tiếng Anh
        ↓
Microphone của iPad
        ↓
Đường hầm riêng Tailscale
        ↓
Laptop nghe và viết lại thành chữ tiếng Anh
        ├──→ Safari trên iPad hiển thị tiếng Anh
        └──→ Nếu bật dịch: laptop dịch sang tiếng Việt
```

Điểm đặc biệt là phần AI chính chạy trên laptop của mình. Âm thanh không cần
được gửi tới một dịch vụ nhận dạng giọng nói trên Internet. Đó là ý nghĩa của
**local-first**: ưu tiên xử lý trên máy của mình.

LectureBridge hiện là một **MVP**. MVP là phiên bản nhỏ nhất có đủ chức năng để
thử trong đời thật. Nó chưa phải sản phẩm hoàn hảo, nhưng đã có thể giúp kiểm
tra xem ý tưởng có hữu ích trong lớp hay không.

## 2. Các “nhân vật” trong hệ thống

### iPad và Safari

iPad làm hai việc:

1. Dùng microphone để nghe âm thanh.
2. Dùng Safari để hiển thị phụ đề.

iPad không chạy model AI nặng. Nó giống như tai và màn hình của hệ thống.

### Tailscale

Tailscale tạo một mạng riêng giữa iPad và laptop. Có thể tưởng tượng nó là một
đường hầm chỉ những thiết bị đã đăng nhập đúng tài khoản mới đi vào được.

**Tailscale Serve** tạo một địa chỉ HTTPS riêng và chuyển yêu cầu tới chương
trình đang chạy trên laptop. Hệ thống chỉ dùng Serve trong `tailnet` cá nhân,
không dùng **Funnel** để mở trang ra Internet công cộng.

### Laptop Ubuntu

Laptop là bộ não và làm phần việc nặng:

- nhận các mẩu âm thanh từ iPad;
- dùng GPU để biến tiếng nói thành chữ tiếng Anh;
- nếu người dùng bật dịch, dùng CPU để dịch tiếng Anh sang tiếng Việt;
- gửi kết quả về Safari.

Máy hiện tại có CPU Intel Core i5-12500H, GPU RTX 3050 với 4 GB VRAM và 16 GB
RAM. VRAM là vùng nhớ riêng của GPU. Nó giống chiếc bàn làm việc của GPU: model
càng lớn thì cần mặt bàn càng rộng.

### Faster-Whisper và model `distil-large-v3.5`

Whisper là một loại AI đã học cách nghe tiếng nói. Faster-Whisper là cách chạy
Whisper nhanh và tiết kiệm tài nguyên hơn.

LectureBridge hiện dùng model `distil-large-v3.5`:

- `distil` nghĩa là model lớn đã được “chưng cất” để chạy gọn và nhanh hơn;
- model được huấn luyện cho nhận dạng tiếng Anh;
- model chạy trên GPU để có tốc độ gần thời gian thực.

Các model nhỏ hơn vẫn còn để dự phòng:

- `small.en`: dự phòng đầu tiên nếu model chính bị chậm;
- `base.en`: nhẹ hơn và nhanh hơn;
- `tiny.en`: nhẹ nhất, dùng khi máy bị chậm hoặc thiếu bộ nhớ.

### NLLB và CTranslate2

Khi người dùng chạy với cờ `--translation`, model NLLB-200 distilled 600M dịch
chữ tiếng Anh sang tiếng Việt. CTranslate2 là bộ máy giúp chạy model dịch gọn
hơn. Bình thường NLLB không được nạp để ưu tiên transcript tiếng Anh.

NLLB được buộc chạy trên CPU. Lý do là GPU chỉ có 4 GB VRAM và cần dành chỗ cho
model nghe tiếng Anh.

### WhisperLiveKit

WhisperLiveKit, viết tắt là WLK, ghép nhiều phần lại với nhau:

- trang web;
- thu microphone;
- WebSocket truyền âm thanh;
- nhận dạng giọng nói liên tục;
- dịch khi người dùng chủ động bật;
- gửi phụ đề về trình duyệt.

LectureBridge khóa WLK ở phiên bản `0.2.26`. “Khóa phiên bản” nghĩa là không tự
ý đổi sang bản mới hơn, vì bản mới có thể thay đổi hành vi ngay trước buổi học.

## 3. Hành trình chi tiết của một mẩu âm thanh

### Bước 1: Safari xin quyền microphone

Khi người dùng bấm nút ghi âm, Safari hỏi có cho trang web dùng microphone hay
không. Người dùng phải tự bấm **Allow/Cho phép**.

Safari yêu cầu trang thu microphone phải là một **secure context**, thường là
HTTPS. Vì thế Tailscale Serve HTTPS là cần thiết trên iPad.

### Bước 2: Âm thanh được đổi thành các con số

Âm thanh ngoài đời là sóng. Máy tính biến sóng này thành một dãy số gọi là
**PCM**.

Cấu hình hiện tại là:

- 16.000 mẫu mỗi giây, còn gọi là 16 kHz;
- một kênh âm thanh, còn gọi là mono;
- mỗi mẫu là số nguyên 16 bit, còn gọi là PCM16.

**AudioWorklet** là một phần của trình duyệt chuyên xử lý âm thanh đều đặn mà
không làm trang web bị giật. Nó gửi các mẩu PCM nhỏ thay vì chờ ghi xong cả file.

### Bước 3: WebSocket giữ một “cuộc điện thoại” mở

HTTP thông thường giống gửi thư: hỏi một lần rồi nhận một lần. **WebSocket**
giống một cuộc điện thoại được giữ mở, nên iPad có thể gửi liên tục nhiều mẩu
âm thanh và laptop có thể trả phụ đề liên tục.

WebSocket của WLK nằm tại đường dẫn `/asr`.

### Bước 4: Tailscale chuyển dữ liệu tới laptop

Tailscale Serve nhận kết nối HTTPS từ iPad rồi chuyển nó tới:

```text
http://127.0.0.1:8000
```

`127.0.0.1` có nghĩa là “chính laptop này”. Backend chỉ nghe ở địa chỉ đó, nên
không tự mở cổng cho cả mạng Wi-Fi. Tailscale là cánh cửa riêng ở phía trước.

### Bước 5: VAD và VAC tìm phần có giọng nói

**VAD** là Voice Activity Detection: bộ phát hiện đoạn nào có người nói và đoạn
nào chỉ là im lặng.

**VAC** là Voice Activity Controller: bộ điều phối các mẩu âm thanh dựa trên
việc có tiếng nói hay không.

Hai phần này giúp hệ thống không cố “nghe ra từ” trong một đoạn im lặng dài.

### Bước 6: Faster-Whisper tạo chữ tiếng Anh

Faster-Whisper đưa các con số âm thanh vào model `distil-large-v3.5`. Model đoán
các từ tiếng Anh có khả năng đã được nói.

LectureBridge nói rõ ngôn ngữ nguồn là `en`. Việc này giúp model không mất thời
gian đoán ngôn ngữ và không dễ nhầm tiếng Anh thành ngôn ngữ khác.

### Bước 7: LocalAgreement quyết định chữ nào đã ổn định

Trong lúc một người còn đang nói, model có thể đổi ý. Ví dụ:

```text
Tạm thời:  The cell has a wall...
Sau đó:    The cell has a membrane...
```

**LocalAgreement** chạy nhận dạng lặp lại và chỉ “chốt” phần mà nhiều lượt liên
tiếp đồng ý với nhau.

Vì thế giao diện có hai loại chữ:

- **buffer/partial**: chữ tạm thời, có thể thay đổi;
- **committed/final**: chữ đã được chốt, đáng tin hơn.

Khi có khoảng ngừng nói dài hơn khoảng 1,2 giây, hệ thống có thể tạo ranh giới
ổn định cho câu. Đây là lý do nên chờ một chút trước khi đánh giá kết quả cuối.

### Bước 8: NLLB dịch sang tiếng Việt nếu được bật

Ở chế độ mặc định, bước này được bỏ qua. Nếu chạy `lecturebridge-live
--translation`, chữ tiếng Anh được gửi cho NLLB trên CPU. Kết quả tiếng Việt
được ghép cùng phụ đề tiếng Anh rồi gửi về iPad.

Bản dịch thường chậm hơn chữ tiếng Anh một chút. Nếu câu tiếng Anh ban đầu sai,
bản dịch cũng có thể sai theo. Vì vậy cần quan sát cả hai dòng để biết lỗi nằm ở
khâu nghe hay khâu dịch.

### Bước 9: Nút Stop kết thúc đúng cách

Khi bấm Stop, trình duyệt gửi một mẩu rỗng làm dấu **EOF**. EOF có thể hiểu là
“hết âm thanh rồi”. Laptop xử lý nốt phần còn lại và gửi trạng thái
`ready_to_stop`.

Chỉ sau tín hiệu này giao diện mới báo:

```text
Finished processing audio! Ready to record again.
```

Nếu đóng Safari quá sớm, vài từ cuối có thể chưa được xử lý.

## 4. Vì sao phải làm baseline offline trước?

Trước khi xây đường truyền trực tiếp, dự án đã thử quy trình đơn giản hơn:

```text
File audio có sẵn → Faster-Whisper → transcript tiếng Anh
```

Đây gọi là **baseline**, tức mốc chuẩn ban đầu. Nếu bước đơn giản này còn lỗi,
việc thêm Safari, mạng, WebSocket và dịch sẽ làm rất khó biết lỗi nằm ở đâu.

Chương trình offline có lệnh:

```bash
uv run lecturebridge-transcribe data/private/english_test_30s.m4a
```

Nó đo:

- thời gian nạp model;
- thời gian xử lý;
- độ dài audio;
- RTF;
- transcript có rỗng hay không.

**RTF**, hay Real-Time Factor, được tính như sau:

```text
RTF = thời gian máy xử lý / độ dài audio
```

Ví dụ audio dài 100 giây mà máy xử lý trong 10 giây thì RTF là `0,1`. RTF nhỏ
hơn `1` nghĩa là máy xử lý nhanh hơn thời gian thật. Cổng của dự án là RTF nhỏ
hơn `0,7`.

Kết quả đã đo với file riêng tư dài 83,84 giây:

| Model | Xử lý | RTF | Kết quả |
| --- | ---: | ---: | --- |
| `tiny.en` | 0,89 giây | 0,011 | Đạt, không OOM |
| `base.en` | 1,37 giây | 0,016 | Đạt, không OOM |
| `small.en` | 2,61 giây | 0,031 | Đạt, dự phòng cấp 1 |
| `distil-large-v3.5` | 2,55 giây | 0,030 | Đạt, model mặc định mới |

Các số này là bài kiểm tra file offline. Độ trễ live còn phụ thuộc vào cách chia
âm thanh, LocalAgreement, mạng và bản dịch nếu được bật.

## 5. Những thứ đã được chuẩn bị và cài đặt

### Python riêng cho dự án

Ubuntu có Python hệ thống 3.14, nhưng dự án cần Python 3.12. Không thay hoặc xóa
Python hệ thống. `uv` đã tải Python 3.12.14 riêng và tạo môi trường tại:

```text
.venv/
```

Môi trường ảo, hay **venv**, giống một hộp đồ riêng của dự án. Gói của
LectureBridge không làm lộn xộn Python của Ubuntu hoặc dự án khác.

### `uv` và `uv.lock`

`uv` quản lý Python và các gói phụ thuộc. `pyproject.toml` mô tả dự án muốn gì;
`uv.lock` ghi chính xác các phiên bản đã chọn để lần cài sau có kết quả giống
nhau hơn.

Các nhóm quan trọng đã cài:

- Faster-Whisper cho ASR;
- WhisperLiveKit `0.2.26` và phần translation;
- thư viện CUDA 12 cần cho cuBLAS và cuDNN;
- `pytest` để chạy test;
- `ruff` để kiểm tra chất lượng mã.

### Ba lệnh chính của LectureBridge

```bash
uv run lecturebridge-transcribe AUDIO
uv run lecturebridge-live
uv run lecturebridge-preflight
```

- `transcribe`: thử một file audio offline;
- `live`: chạy trang phụ đề trực tiếp;
- `preflight`: kiểm tra máy đã sẵn sàng trước giờ học chưa.

## 6. Những vấn đề đã gặp và cách suy nghĩ để sửa

### Vấn đề 1: dự án bị dính vào một uv workspace bên ngoài

Thư mục cha vô tình khai báo LectureBridge là một thành viên workspace. Điều
này có thể khiến `uv` dùng sai cấu hình hoặc môi trường.

Cách sửa là gỡ riêng LectureBridge khỏi danh sách đó, không đụng đến thành viên
khác, rồi xác nhận mọi lệnh dùng đúng `.venv/bin/python3` trong repository.

Bài học: trước khi sửa AI, phải chắc mình đang chạy đúng Python và đúng dự án.

### Vấn đề 2: import được Faster-Whisper nhưng chạy GPU còn thiếu thư viện

Driver NVIDIA và GPU hoạt động không có nghĩa mọi thư viện AI đã có đủ. Khi
chạy inference, Faster-Whisper còn cần cuBLAS và cuDNN tương thích.

Dự án đã thêm các gói CUDA 12 vào dependency. Hàm runtime tìm thư mục chứa các
thư viện đó, thêm chúng vào `LD_LIBRARY_PATH`, rồi khởi động lại đúng chương
trình một lần.

Bài học: “GPU được nhìn thấy” và “model chạy thật trên GPU” là hai phép kiểm tra
khác nhau.

### Vấn đề 3: `base.en` nghe chưa đủ tốt

`base.en` rất nhanh nhưng có thể nhầm nhiều hơn trong phòng ồn, giọng lạ hoặc
bài giảng có thuật ngữ. Model được nâng lên `small.en` và benchmark trước khi
đặt làm mặc định.

Bài học: nâng model chỉ sau khi đã đo rằng máy đủ nhanh và đủ bộ nhớ.

Sau khi lớp học cho thấy `small.en` vẫn sai nhiều, dự án tiếp tục thử
`distil-large-v3.5`. Model mới xử lý file 83,84 giây trong 2,55 giây, dùng khoảng
1,08 GB VRAM sau inference và theo kịp bài stress khoảng 184 từ/phút. Vì vậy nó
trở thành mặc định cho debate; `small.en` trở thành đường lui.

### Vấn đề 4: `small.en` cộng model dịch làm GPU hết chỗ

Lần chạy đầu tiên với `small.en` và NLLB báo **CUDA out of memory**, viết tắt là
OOM. Nguyên nhân không phải `small.en` tự nó quá lớn. Nguyên nhân là NLLB tự
chọn GPU, khiến hai model tranh nhau 4 GB VRAM.

Cách sửa:

```text
GPU: chỉ chạy Faster-Whisper
CPU: chạy NLLB dịch EN → VI
```

Sau khi tách việc như vậy, server khởi động và dịch được mà không OOM.

Bài học: khi tài nguyên có hạn, không nhất thiết phải hạ chất lượng ngay. Có thể
chia công việc cho GPU và CPU hợp lý hơn.

### Vấn đề 5: tham số `--beams 1` không làm điều tưởng tượng

Ban đầu launcher truyền `--beams 1`. Khi đọc mã của đúng WLK 0.2.26, phát hiện
backend Faster-Whisper với LocalAgreement đang dùng beam size 5 cố định; cờ
`--beams` thuộc đường chạy khác và không điều khiển trường hợp này.

Cờ gây hiểu nhầm đã được bỏ khỏi live launcher. Công cụ offline có
`--beam-size 1-5` để làm thí nghiệm có kiểm soát.

Bài học: đừng tin tên một tùy chọn chỉ vì nó nghe hợp lý; phải kiểm tra nó có
thật sự đi tới đoạn mã mình đang chạy hay không.

### Vấn đề 6: iPad không thể dùng `127.0.0.1`

Trên iPad, `127.0.0.1` có nghĩa là chính iPad, không phải laptop. Vì vậy iPad
phải mở URL HTTPS do Tailscale Serve cung cấp.

Ubuntu cũng yêu cầu quyền quản trị khi cấu hình Serve lần đầu. Sau khi bật,
`tailscale serve status` cho biết URL và nơi nó chuyển tiếp tới.

Bài học: một địa chỉ có thể mang ý nghĩa khác nhau tùy thiết bị đang mở nó.

## 7. Đã kiểm thử những gì?

### Kiểm tra mã tự động

```bash
uv run ruff check .
uv run pytest -q
```

Kết quả gần nhất:

```text
Ruff: đạt
Pytest: 20 test đạt, 1 test GPU opt-in được bỏ qua mặc định
```

Test kiểm tra những việc như:

- tính RTF đúng;
- timestamp đúng;
- không in đường dẫn thư mục riêng tư;
- CLI chỉ nhận model được hỗ trợ;
- live server chỉ bind vào `127.0.0.1`;
- chế độ EN-only không bật model dịch;
- NLLB được ép chọn CPU;
- môi trường Python đúng.

### Preflight trước giờ học

```bash
uv run lecturebridge-preflight --peer ipad153
```

Preflight giống danh sách kiểm tra trước khi máy bay cất cánh. Nó kiểm tra:

1. Python có đúng `.venv` không;
2. WLK có đúng phiên bản không;
3. GPU NVIDIA có hoạt động không;
4. FFmpeg có sẵn không;
5. Tailscale có online không;
6. model ASR đã tải chưa và chỉ kiểm tra NLLB khi bật dịch;
7. iPad có kết nối direct hay relay nếu truyền `--peer`;
8. cổng 8000 trống hoặc đúng model LectureBridge đang chạy.

Kết quả gần nhất là mọi mục đều PASS và đường tới iPad là direct.

### Kiểm tra live không cần microphone

Một test client đã giả làm trình duyệt:

- đổi file audio riêng tư thành PCM16 mono 16 kHz;
- gửi 168 mẩu âm thanh qua WebSocket ở tốc độ 4 lần thời gian thật;
- nhận 222 phản hồi;
- có 213 phản hồi chứa cập nhật chữ;
- nhận 9 dòng tiếng Anh đã chốt;
- thấy bản dịch tiếng Việt;
- nhận `ready_to_stop` ở cuối;
- không OOM.

Sau đó một bài test EN-only mới đã chạy `distil-large-v3.5` với audio được tăng
tốc tới khoảng 184 từ/phút. Chữ đầu xuất hiện sau 0,56 giây, backlog xử lý cao
nhất 1,8 giây và backlog chốt chữ cao nhất 2,7 giây. Test này chứng minh máy theo
kịp về tốc độ, chưa chứng minh mọi từ trong debate thật đều chính xác.

Nội dung transcript không được đưa vào repository.

### Kiểm tra vẫn cần con người

Máy có thể kiểm tra “có chữ”, nhưng chưa thể tự biết chữ đó có đủ hữu ích với
bài giảng thật hay không. Vẫn cần:

- thử microphone Safari trên iPad qua URL HTTPS;
- nói hoặc dùng nguồn hợp lệ trong hai phút;
- quan sát độ chính xác của câu tiếng Anh đã chốt;
- kiểm tra transcript không trễ liên tục quá 5 giây;
- chạy 20 phút với nguồn điện thật để xem có nóng, treo hoặc backlog không.

**Backlog** là hàng âm thanh chờ xử lý. Nếu người nói tạo âm thanh nhanh hơn máy
xử lý, hàng chờ sẽ dài dần và phụ đề ngày càng trễ.

## 8. Dữ liệu riêng tư được bảo vệ thế nào?

`.gitignore` bảo Git bỏ qua:

- `data/private/`;
- file WAV, MP3, M4A, WebM và MP4;
- `outputs/` và kết quả benchmark riêng tư;
- model đã tải;
- `.env`, nơi sau này có thể chứa token hoặc bí mật.

Roadmap PDF, audio và transcript không nằm trong các commit đã tạo.

Hệ thống hiện không tự lưu audio hoặc transcript live. Tuy vậy, người dùng vẫn
cần tuân thủ quy định của lớp và xin phép nếu việc thu âm là bắt buộc phải xin.

## 9. Trạng thái hiện tại của dự án

Tại thời điểm viết tài liệu này:

- branch Git là `chore/bootstrap`;
- live mặc định dùng `distil-large-v3.5` và chỉ hiện tiếng Anh;
- nguồn là tiếng Anh `en`;
- Faster-Whisper chạy trên GPU;
- NLLB CTranslate2 chỉ được nạp trên CPU khi bật `--translation`;
- server chỉ bind `127.0.0.1:8000`;
- Tailscale Serve chỉ mở trong tailnet;
- health endpoint trả về `ready: true`;
- chưa push các commit mới lên GitHub.

Các commit kể lại lịch sử công việc theo thứ tự:

1. `fa26a28` — tách môi trường dự án và bảo vệ dữ liệu riêng tư;
2. `a19f60e` — thêm baseline transcription GPU offline;
3. `4996c77` — bổ sung CUDA 12 runtime;
4. `2784f8b` — thêm phụ đề live EN→VI;
5. `d25fe5a` — thêm preflight;
6. `6a00088` — thêm runbook và bằng chứng test;
7. `51f8643` — nâng ASR mặc định lên `small.en` và giải quyết OOM.
8. `8a1a0ed` — thêm chế độ debate EN-only với `distil-large-v3.5`;
9. `b5c17c3` — thêm test model, preflight và stress GPU cho debate.

## 10. Cách chạy ngắn nhất

Trong thư mục repository trên laptop:

```bash
uv run lecturebridge-preflight --peer ipad153
uv run lecturebridge-live
```

Khi thấy server sẵn sàng:

1. bật Tailscale trên iPad;
2. mở URL HTTPS được in bởi `tailscale serve status` trong Safari;
3. cho phép microphone;
4. bấm nút ghi âm;
5. khi xong, bấm Stop và chờ thông báo xử lý hoàn tất.

Nếu máy chậm, thử theo thứ tự:

```bash
uv run lecturebridge-live --model small.en
uv run lecturebridge-live --model base.en
uv run lecturebridge-live --model tiny.en
```

Muốn thử lại bản dịch tiếng Việt, chủ động chạy
`uv run lecturebridge-live --translation`. EN-only vẫn là mặc định.

## 11. Cách tư duy đã dùng khi xây MVP

### Chia bài toán lớn thành những cổng nhỏ

Không xây mọi thứ cùng lúc. Thứ tự là:

```text
Python đúng
  → GPU chạy model
  → file audio thành chữ
  → âm thanh live thành chữ
  → iPad kết nối riêng tư
  → tùy chọn: dịch sang tiếng Việt
```

Chỉ qua cổng tiếp theo khi cổng trước có bằng chứng hoạt động.

### Đo trước khi đoán

Thay vì nói “chắc model này đủ nhanh”, dự án đo thời gian, RTF, VRAM, health và
số phản hồi WebSocket.

### Chỉ thay đổi một nguyên nhân quan trọng mỗi lần

Khi OOM, không đồng thời đổi model, framework và mạng. Trước tiên xác định model
dịch đang lấy GPU, sau đó chuyển riêng nó sang CPU và chạy lại đúng bài test.

### Luôn có đường lui

`distil-large-v3.5` là mặc định nhưng `small.en`, `base.en` và `tiny.en` vẫn còn.
Trong lớp, một hệ thống hơi kém hơn nhưng chạy liên tục tốt hơn một hệ thống
thông minh hơn mà bị treo.

### Bảo vệ dữ liệu ngay từ đầu

Audio riêng tư được ignore trước khi chạy thử. Không đợi tới lúc sắp push Git
mới nghĩ về quyền riêng tư.

## 12. Những giới hạn hiện tại

- Chỉ hỗ trợ một thiết bị microphone và một phiên chính.
- Safari phải ở foreground; chuyển sang ứng dụng khác có thể làm iOS/iPadOS
  giảm hoặc dừng hoạt động của trang.
- Chưa có tự động reconnect hoàn chỉnh.
- Chưa có iPad thứ hai chỉ để xem.
- Chưa có PWA cài như ứng dụng.
- Chưa lưu hoặc xuất transcript.
- Chưa có từ điển thuật ngữ theo môn.
- Chưa đo độ chính xác bằng một transcript chuẩn do con người viết.
- Chưa chạy soak test 20 phút trong điều kiện giống lớp thật.
- Chất lượng giảm khi iPad ở xa, phòng ồn, nhiều người nói cùng lúc hoặc có từ
  chuyên ngành lạ.

## 13. Ý tưởng phát triển mới

Sau khi hiểu luồng trên, một bạn 12 tuổi có thể đặt các câu hỏi sau:

### Làm sao biết lỗi nằm ở nghe hay dịch?

Cho phép chạm vào một dòng để xem cạnh nhau:

```text
Âm thanh → tiếng Anh đã nghe → tiếng Việt đã dịch
```

Nếu tiếng Anh sai thì lỗi ASR. Nếu tiếng Anh đúng nhưng tiếng Việt sai thì lỗi
dịch.

### Làm sao giúp AI biết từ chuyên ngành?

Tạo “ba lô từ vựng” cho từng môn: Sinh học, Toán, Lập trình… Trước buổi học,
người dùng nhập các từ như `mitochondria`, `polynomial` hoặc `recursion`.

Cần thử nghiệm cẩn thận vì WLK 0.2.26 xử lý prompt khác nhau tùy streaming
policy; không nên chỉ thêm một cờ rồi giả định nó hoạt động.

### Làm sao biết microphone có nghe rõ không?

Thêm đồng hồ mức âm thanh với ba vùng:

- quá nhỏ;
- vừa đủ;
- quá to và bị vỡ tiếng.

Đây có thể cải thiện ASR nhiều mà không cần model lớn hơn.

### Làm sao đánh giá model công bằng?

Viết transcript chuẩn bằng tay cho một đoạn audio được phép dùng, rồi tính WER.

**WER**, hay Word Error Rate, là tỉ lệ từ bị sai, thiếu hoặc thừa. WER càng thấp
càng tốt. Khi đó có thể so `distil-large-v3.5`, `small.en` và các model dự phòng
bằng con số thay vì cảm giác.

### Làm sao phục hồi khi Wi-Fi chập chờn?

Thêm biểu tượng trạng thái kết nối, tự reconnect và một buffer ngắn trên iPad.
Khi mất mạng vài giây, âm thanh chưa gửi có thể được gửi tiếp thay vì mất hẳn.

### Làm sao có màn hình xem riêng?

Tách vai trò:

- một iPad gần giảng viên để thu microphone;
- một iPhone hoặc iPad khác chỉ xem phụ đề.

Muốn làm vậy cần thiết kế cách một phiên phát kết quả cho nhiều người xem.

### Làm sao giữ riêng tư mà vẫn lưu bài?

Thêm nút lưu **tắt theo mặc định**. Khi người dùng bật và có quyền, transcript
có thể được mã hóa và lưu cục bộ, kèm nút xóa rõ ràng. Không nên âm thầm lưu.

### Làm sao nhận ra hệ thống đang bị trễ?

Hiển thị backlog và độ trễ bằng màu:

- xanh: đang theo kịp;
- vàng: bắt đầu chậm;
- đỏ: nên chuyển lần lượt sang `small.en`, `base.en`, rồi `tiny.en`.

### Làm sao làm giao diện dễ đọc trong lớp?

Có thể thêm chữ lớn, tương phản cao, khóa màn hình không ngủ, chọn chỉ xem EN,
chỉ xem VI hoặc cả hai, và giữ vài câu gần nhất thay vì cuộn quá nhanh.

## 14. Điều quan trọng nhất cần nhớ

LectureBridge không phải một “AI duy nhất”. Nó là một đội nhỏ:

```text
iPad nghe
Tailscale chuyển
WebSocket giữ liên lạc
VAD/VAC tìm giọng nói
Faster-Whisper viết tiếng Anh
LocalAgreement chốt từ ổn định
NLLB dịch tiếng Việt nếu được bật
Safari hiển thị kết quả
```

Muốn cải thiện hệ thống, hãy hỏi từng thành viên trong đội:

1. Đầu vào có nghe rõ không?
2. Mạng có gửi đều không?
3. ASR có nghe đúng không?
4. Dịch có dịch đúng không?
5. Giao diện có giúp người học đọc kịp không?

Khi biết chính xác mắt xích nào yếu, ta có thể sửa đúng chỗ thay vì thay toàn bộ
hệ thống.
