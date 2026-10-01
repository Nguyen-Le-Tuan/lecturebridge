# LectureBridge: Chiến lược Freemium cho Du học sinh

> Archived planning document, dated 15 September 2026. The original Vietnamese
> proposal and its assumptions are preserved below. Proposed prices, cloud
> services, and milestones are not current product features or commitments.
> For the available application, see the [README](../../README.md).

**Báo cáo gửi:** Giám đốc điều hành  
**Ngày:** 15 tháng 9 năm 2026  
**Phiên bản:** 1.0 - Quyết định cho private alpha 90 ngày  
**Phạm vi:** Chiến lược sản phẩm, cạnh tranh, mô hình doanh thu, hạ tầng, rủi ro và năng lực vận hành của người sáng lập

> **Khuyến nghị điều hành:** GO có điều kiện cho một private alpha tối đa 25 sinh viên, sau đó closed beta tối đa 100 sinh viên. Không thuê GPU cloud cố định, không phát hành App Store/Google Play và không nhận tiền trước khi hoàn thành Giai đoạn 0 về quyền làm chủ hệ thống, kiểm tra giấy phép và consent.

---

## 1. Tóm tắt điều hành

LectureBridge nên bắt đầu như một công cụ giúp du học sinh **đọc kịp bài giảng và debate bằng tiếng Anh**, không phải một ứng dụng ghi chú AI tổng quát. Sản phẩm hiện tại đã chứng minh được luồng local-first: iPad thu microphone, truyền âm thanh qua Tailscale tới laptop Ubuntu, Faster-Whisper chạy trên RTX 3050 và trả transcript tiếng Anh gần thời gian thực. Đây là một nền kỹ thuật có giá trị, nhưng chưa phải sản phẩm thương mại nhiều người dùng.

Thị trường mở đầu là sinh viên quốc tế tại Hoa Kỳ. IIE ghi nhận 1.177.766 sinh viên quốc tế trong năm học 2024-2025. Nghiên cứu Academic Listening Project của University of Leeds cũng cho thấy việc theo kịp bài giảng là một vấn đề chuyển tiếp thực tế đối với người học dùng tiếng Anh như ngôn ngữ thứ hai [1][2]. Tuy nhiên, quy mô thị trường không tự động tạo ra lợi thế: Apple và Google đã cung cấp phụ đề trực tiếp miễn phí; Otter, Ava, Notta và nhiều đối thủ có thương hiệu lớn; BBNotes đã định vị trực tiếp cho sinh viên quốc tế [3][4][5][6][7].

Khoảng trống LectureBridge có thể chiếm là tổ hợp gồm:

- Transcript tiếng Anh xuất hiện nhanh và ưu tiên khả năng theo kịp debate.
- Course glossary giúp nhận đúng tên môn học, giảng viên và thuật ngữ chuyên ngành.
- Không ép người dùng lưu recording hoặc mua tính năng tóm tắt không cần thiết.
- Community Edition chạy local, miễn phí không giới hạn và có thể kiểm tra mã nguồn.
- Cloud Edition mở bằng link, dành cho người không có laptop GPU.
- Giá và chính sách quota minh bạch, có hardship code cho sinh viên khó khăn.

Quyết định đề xuất là mô hình **local miễn phí + cloud trả phí**, PWA trước, B2C trước và campus B2B sau. Cloud beta nên mua ASR theo giờ sử dụng thay vì thuê GPU 24/7. Soniox là ứng viên thương mại đầu tiên nhờ giá niêm yết khoảng 0,12 USD/giờ, Web SDK và temporary key có thể giới hạn một phiên; AssemblyAI là đối chứng khoảng 0,15 USD/giờ [20][21][22]. Nhà cung cấp cuối cùng chỉ được chọn sau benchmark trên audio lecture/debate có consent.

NLLB hiện tại không được đưa vào sản phẩm trả phí. Model card dùng giấy phép CC-BY-NC-4.0 và nói rõ đây là model nghiên cứu, không phát hành cho production deployment [23]. MVP thương mại chỉ transcript tiếng Anh. Dịch là sản phẩm bổ sung tương lai sau khi có phương án được phép thương mại và unit economics riêng.

### Quyết định GO/NO-GO

| Quyết định | Kết luận | Điều kiện |
|---|---|---|
| Private alpha 25 người | **GO** | Không thu tiền; audio có consent; chi phí có hard cap |
| Closed beta 100 người | **GO có điều kiện** | Giai đoạn 0 hoàn tất; PWA có quota, xóa dữ liệu và monitoring |
| Thu tiền B2C | **CHƯA GO** | Kiểm tra pháp lý, license, thanh toán, support và recovery |
| App Store/Google Play | **CHƯA GO** | Chỉ làm khi PWA tạo ra rào cản chuyển đổi đã đo được |
| Thuê GPU 24/7 | **NO-GO hiện tại** | Chỉ xét lại sau khoảng 3.000 audio-hour/tháng và benchmark đa phiên |
| Dịch NLLB có trả phí | **NO-GO** | Phải thay bằng model/API được phép thương mại |

---

## 2. Khách hàng, vấn đề và lời hứa sản phẩm

### 2.1 Khách hàng mở đầu

Persona chính là một du học sinh tại Mỹ có vốn từ đủ để đọc tài liệu nhưng không nghe kịp khi:

- Giảng viên nói nhanh, nuốt âm hoặc dùng accent lạ.
- Nhiều sinh viên đổi lượt liên tục trong debate.
- Phòng học có tiếng quạt, bàn phím hoặc khoảng cách xa microphone.
- Người học phải đồng thời nghe, dịch trong đầu và ghi chú.
- Phụ đề đang thay đổi quá chậm hoặc tóm tắt làm mất câu chữ gốc.

Job-to-be-done cốt lõi: **“Khi tốc độ nói vượt quá tốc độ nghe của tôi, hãy cho tôi một dòng chữ tiếng Anh đủ nhanh để tôi bắt lại mạch nội dung, mà không buộc tôi ghi âm hoặc giao toàn bộ bài học cho một hệ thống đám mây.”**

Persona phụ trong năm đầu:

- Người học ESL trong seminar hoặc workshop.
- Teaching assistant cần glossary thuật ngữ môn học.
- International student office muốn tài trợ công cụ cho một nhóm nhỏ.

Chưa mở rộng thông điệp sang mọi người dùng khiếm thính hoặc cam kết accommodation chính thức. Đây là lĩnh vực đòi hỏi tiêu chuẩn accessibility, support và độ tin cậy cao hơn khả năng hiện tại.

### 2.2 Lời hứa có thể đo

- Người mới bắt đầu phiên đầu trong dưới 3 phút.
- Partial text đầu tiên dưới 2 giây trong điều kiện mạng bình thường.
- Committed transcript không chậm quá 5 giây.
- Không lưu audio mặc định.
- Transcript cloud tự xóa sau 7 ngày và có nút xóa ngay.
- Hiển thị rõ chữ đang thay đổi và chữ đã committed.

Không sử dụng lời quảng cáo “không bỏ sót từ nào”. Hai người nói chồng lên nhau qua một microphone mono tạo ra một tín hiệu đã trộn; model không thể đảm bảo khôi phục đầy đủ cả hai câu.

### 2.3 Lợi thế cần xây

Model ASR không phải hào kinh tế bền vững vì đối thủ có thể mua cùng API hoặc model. Lợi thế cần tích lũy là:

1. Bộ benchmark lecture/debate có consent, accent đa dạng và ground truth.
2. Course glossary và luồng nhập syllabus/thuật ngữ đơn giản.
3. Dữ liệu đo độ trễ, lỗi và độ hữu ích mà không lưu audio ngoài ý muốn.
4. Niềm tin về quyền riêng tư và một bản local thực sự dùng được.
5. Kênh phân phối qua cộng đồng sinh viên quốc tế và campus partners.
6. Tài liệu vận hành giúp dự án không phụ thuộc vào một AI coding agent.

---

## 3. Bản đồ cạnh tranh và khoảng trống thị trường

Giá và số liệu store dưới đây được ghi nhận từ nguồn công khai tại thời điểm lập báo cáo; phải kiểm tra lại trước mỗi quyết định giá.

### 3.1 Đối thủ trực tiếp và thay thế

| Sản phẩm | Kênh | Giá/tín hiệu thị trường | Điểm mạnh | Khoảng trống cho LectureBridge |
|---|---|---|---|---|
| Apple Live Captions | iPad/iPhone tích hợp | Miễn phí cùng thiết bị | Không cần cài, gần hệ điều hành | Không định vị cho course glossary hoặc workflow lecture [3] |
| Google Live Transcribe | Android/Play | Miễn phí; hơn 70 ngôn ngữ | Phổ biến, có offline trên một số thiết bị | Không phải trải nghiệm chuyên cho du học sinh [4] |
| Ava | iOS/Android/Web | Free basic; Community khoảng 9,99 USD/tháng theo năm hoặc 14,99 USD tháng | Accessibility, lớp học, custom vocabulary | Giá cao hơn mục tiêu; cloud và workflow rộng [5] |
| Otter | iOS/Android/Web | Free 300 phút; Pro 16,99 USD tháng hoặc 8,49 USD/tháng theo năm | Thương hiệu mạnh, meeting notes, 5M+ Android downloads | Tập trung meeting/AI notes hơn debate transcript [6][8] |
| Notta | iOS/Android/Web | Free 120 phút nhưng giới hạn 3 phút/cuộc; Pro từ 8,17 USD/tháng theo năm | Nhiều ngôn ngữ, translation và notes | Free session quá ngắn; sản phẩm rộng, phức tạp [9][10] |
| Transkriptor | iOS/Android/Web | Lite 9,99 USD; Pro 19,99 USD tháng hoặc 8,33 USD/tháng theo năm | File transcription, đa nền tảng, giảm giá giáo dục | Không local-first; không chuyên debate live [11] |
| Live Transcribe iOS | iOS | Từ 9,99 USD/tháng; 10 giờ Pro | Sản phẩm caption chuyên dụng, offline | Quota/giá tạo khoảng trống cho gói sinh viên [12] |
| Captio AI | iOS | Free 10 phút/ngày; paid unlimited | Caption, dịch, tóm tắt; thông điệp privacy | Định vị rộng; chưa tạo lợi thế course context [13] |
| BBNotes | iOS/iPadOS/macOS | Trial 14 ngày; gói tháng/học kỳ/năm | Đối thủ sát nhất: sinh viên quốc tế, PDF, handwriting, bilingual captions | LectureBridge phải đơn giản, nhanh và rẻ hơn thay vì sao chép “AI notebook” [7] |
| Captio.dev | Web/QR/PWA | Từ 4,99 USD/tháng | Không cần cài app, glossary, EU hosting | Xác nhận PWA là kênh khả thi; cần thắng bằng lecture UX [14] |
| Aiko | iOS/macOS | Khoảng 24 USD một lần | On-device, riêng tư | Không live trong lúc recording [15] |
| MacWhisper | Mac/direct download | Free và Pro lifetime khoảng 64 EUR | Local, private, thương hiệu Whisper mạnh | Chủ yếu desktop/file; không tối ưu iPad classroom [16] |
| FUTO Voice Input | Play/F-Droid/APK | License một lần; offline | Kênh ngoài store, local hoàn toàn | Là input method, không phải lecture caption room [17] |
| Whisper Mobile/Android forks | GitHub/APK | Miễn phí/mã nguồn mở | Offline, không cloud | UX, update, support và trust không đồng đều [18][19] |

### 3.2 Kết luận cạnh tranh

LectureBridge không nên tuyên bố lợi thế chỉ vì dùng Whisper hoặc chạy local. Những yếu tố này đã phổ biến. White space hợp lý là:

- **Fast reading layer:** giao diện chỉ tập trung vào việc đọc kịp, không đẩy người dùng vào notes, bot hoặc summary.
- **Debate mode:** kiểm thử và tối ưu cho đổi lượt nhanh, nhưng công khai giới hạn với lời nói chồng nhau.
- **Course context:** glossary theo lớp, tên riêng và thuật ngữ quan trọng.
- **Choice of trust:** local unlimited cho người có máy; cloud metered cho người cần tiện lợi.
- **Student economics:** giá thấp hơn nhóm ứng dụng meeting, không dark pattern và có hardship access.

### 3.3 Kênh phân phối

Thứ tự đề xuất:

1. PWA bằng link/QR, dùng Safari/Chrome và Add to Home Screen.
2. Community Edition trên GitHub kèm release, checksum và tài liệu cài đặt.
3. Campus landing page và invite code cho từng tổ chức.
4. iOS native chỉ khi đo thấy background/microphone/PWA làm giảm activation hoặc retention.
5. Android store/APK sau khi có signing, update và security response chuẩn.

Apple Developer Program hiện có phí 99 USD/năm; Android full distribution yêu cầu đăng ký/xác minh và Google công bố luồng limited distribution riêng. Những quy định này có thể đổi và phải được kiểm tra lại khi bước vào store [24][25][26].

---

## 4. Mô hình freemium đặt lợi ích sinh viên lên trước

### 4.1 Cấu trúc gói đề xuất

| Gói | Giá | Quota | Phiên tối đa | Đối tượng |
|---|---:|---:|---:|---|
| Community Local | 0 USD | Không giới hạn | Phụ thuộc máy cá nhân | Người có laptop đủ mạnh, privacy-first |
| Cloud Free | 0 USD | 300 phút/tháng | 60 phút | Dùng thử và các buổi học quan trọng |
| Student Plus | 6,99 USD/tháng | 900 phút/tháng | 120 phút | Người cần cloud thường xuyên |
| Semester Pass | 34,99 USD/6 tháng | 900 phút/tháng, reset hàng tháng | 120 phút | Giảm churn và khớp lịch học kỳ |
| Supporter | 9,99 USD/tháng | Như Student Plus | 120 phút | Người tự nguyện tài trợ free pool |
| Hardship | 0 USD bằng code | Theo Free hoặc Plus | Theo gói | Cấp thủ công trong beta |

Nguyên tắc:

- Không quảng cáo “unlimited” khi chi phí tăng theo phút.
- Không tự động tính tiền vượt quota. Người dùng chủ động mua thêm hoặc chờ kỳ mới.
- Hiển thị phút còn lại trước và trong phiên.
- Gửi cảnh báo ở 80%, 95% và 100% quota.
- Hủy subscription dễ như đăng ký; không dùng countdown giả hoặc nút gây nhầm lẫn.
- Free quota không bị hạ âm thầm để ép nâng cấp.

### 4.2 Unit economics tham chiếu

Giả định bảo thủ cho Student Plus:

- Giá niêm yết: 6,99 USD/tháng.
- Stripe domestic card: 2,9% + 0,30 USD, tạo doanh thu ròng khoảng 6,49 USD [27].
- Sử dụng đủ 15 giờ với Soniox 0,12 USD/giờ: 1,80 USD.
- Phân bổ auth/database/monitoring/support tooling: 0,30 USD.
- Lãi gộp tối đa: 4,39 USD, tương đương khoảng 67,6%.

Đây là contribution margin trước thuế, hoàn tiền, hỗ trợ con người, marketing và chi phí pháp lý. Nếu dùng AssemblyAI 0,15 USD/giờ, ASR thành 2,25 USD và margin giảm khoảng 7 điểm phần trăm.

Cloud Free 300 phút tạo chi phí ASR tối đa 0,60-0,75 USD/người/tháng. Với ngân sách ASR 75 USD, trường hợp xấu nhất chỉ nên nhận khoảng 100 người dùng Free sử dụng đủ quota trong beta. Paid usage và người dùng không dùng hết quota sẽ cải thiện thực tế, nhưng không được dùng breakage làm giả định sống còn.

### 4.3 Cơ chế bảo vệ biên lợi nhuận

- Hard spend cap 75 USD/tháng tại nhà cung cấp ASR nếu họ hỗ trợ; thêm soft alert tại 25/50/65 USD.
- Token chỉ dùng một lần, hết hạn nhanh và có maximum session duration.
- Quota được kiểm tra server-side trước khi cấp token và đối soát sau phiên.
- Rate limit theo account, device và IP; phát hiện nhiều phiên đồng thời bất thường.
- Invite-only trong alpha/beta.
- Không lưu audio; transcript text 7 ngày có chi phí rất nhỏ so với media.
- Không tặng translation miễn phí trong gói rẻ nếu chi phí translation chưa được đo.

---

## 5. Chiến lược server và kiến trúc cloud

### 5.1 Quyết định build-versus-buy

Trong beta, API ASR theo giờ có lợi hơn GPU cố định vì:

- Không trả tiền khi không có lớp học.
- Không phải tự vận hành autoscaling, WebSocket routing, GPU OOM và model warm-up.
- Có temporary key cho browser kết nối trực tiếp, giảm bandwidth backend.
- Dễ áp quota và tính chi phí theo session.

Soniox hỗ trợ backend cấp temporary API key ngắn hạn, `single_use`, `client_reference_id` và `max_session_duration_seconds` tới 18.000 giây; Web SDK có sẵn luồng microphone và stop/finalize [20][21]. AssemblyAI cũng hỗ trợ token ngắn hạn cho browser và WebSocket streaming, nên phù hợp làm provider thứ hai để benchmark [22].

### 5.2 Luồng dữ liệu mục tiêu

```text
iPad/điện thoại
    │ microphone PCM
    ▼
LectureBridge PWA
    │ 1. đăng nhập + xin bắt đầu session
    ▼
Control API ── kiểm tra quota ── Supabase
    │ 2. temporary key dùng một lần
    ▼
PWA ═════ audio trực tiếp ═════► ASR provider
    ◄════ partial/final text ════
    │ 3. chỉ gửi committed text
    ▼
Supabase ── tự xóa sau 7 ngày
```

Audio không đi qua database hoặc object storage của LectureBridge. Backend không proxy audio trong beta. Điều này giảm chi phí và phạm vi sự cố, nhưng phải công khai rằng nhà cung cấp ASR vẫn xử lý audio theo điều khoản và data-processing policy của họ.

### 5.3 API tối thiểu

| Endpoint | Trách nhiệm | Kiểm soát bắt buộc |
|---|---|---|
| `POST /v1/sessions` | Tạo phiên, ghi consent version | Auth, quota, idempotency |
| `POST /v1/asr/token` | Cấp key một lần | TTL ngắn, max 120 phút, client reference |
| `GET /v1/usage` | Trả phút đã dùng/còn lại | Không tin số đo từ client |
| `POST /v1/sessions/{id}/segments` | Lưu committed text | Idempotent segment ID, giới hạn kích thước |
| `GET /v1/sessions/{id}/export` | Xuất TXT/JSON | Chỉ chủ session, audit metadata |
| `DELETE /v1/sessions/{id}` | Xóa ngay | Xóa text và metadata không bắt buộc |

Một scheduled job xóa mọi committed segment quá 7 ngày. Log kỹ thuật chỉ chứa session ID giả danh, latency, duration, provider status và chi phí; không chứa audio hoặc nội dung transcript.

### 5.4 Khi nào mới self-host GPU

RunPod niêm yết L4 khoảng 0,49 USD/GPU-hour [28]. So với API 0,12 USD/audio-hour, một GPU phải phục vụ trung bình hơn 4,08 luồng đồng thời trong toàn bộ thời gian được trả tiền mới chỉ hòa chi phí ASR thô:

```text
break-even concurrency = 0,49 / 0,12 = 4,08 phiên đồng thời
```

Một GPU chạy 24/7 tốn khoảng 357,70 USD/tháng và cần khoảng 2.981 audio-hour/tháng để hòa API 0,12 USD/giờ, chưa tính idle, orchestration, egress, monitoring và nhân công. Vì vậy chỉ mở dự án self-host khi:

- Vượt khoảng 3.000 audio-hour trả phí/tháng trong hai tháng liên tiếp.
- Benchmark chứng minh một GPU giữ chất lượng/độ trễ với ít nhất 5 phiên đồng thời.
- Có autoscaling, warm pool, bounded queue, sticky session và graceful shutdown.
- Tổng cost per audio-hour thấp hơn API ít nhất 25%, tạo đủ vùng đệm vận hành.

Không chọn GPU chỉ vì giá niêm yết thấp; quyết định dựa trên cost per completed audio-hour và tỷ lệ session thành công.

---

## 6. Privacy, consent, license và an toàn kinh doanh

### 6.1 Dữ liệu

- Audio: không lưu mặc định; không có nút record trong beta.
- Partial text: chỉ tồn tại trong bộ nhớ client.
- Committed text: lưu tối đa 7 ngày nếu người dùng chọn cloud session.
- Export: TXT/JSON do người dùng chủ động tải.
- Delete now: có ở mọi session.
- Account deletion: xóa transcript, session metadata không bắt buộc và credential liên quan.
- Analytics: ưu tiên event số lượng/latency, không gửi transcript tới analytics provider.

Trước khi alpha, phải xác nhận chính sách data retention, model training, region, subprocessors và DPA của nhà cung cấp ASR. Không tuyên bố “audio không bao giờ rời thiết bị” cho Cloud Edition.

### 6.2 Consent và trường học

PWA phải hiển thị lời nhắc: người dùng chịu trách nhiệm xin phép theo quy định lớp học, trường và pháp luật địa phương. Consent version được lưu cùng session metadata. Không dùng biểu tượng hoặc câu chữ khiến người dùng tưởng LectureBridge đã được trường chính thức phê duyệt.

Trước khi thu tiền hoặc chạy campus pilot, cần luật sư Mỹ rà soát tối thiểu:

- Quy định ghi âm/consent theo bang.
- FERPA và vai trò của nhà cung cấp khi trường tài trợ.
- Privacy Policy, Terms of Service và Data Processing Addendum.
- Accessibility claims và giới hạn trách nhiệm.
- Sales tax và subscription cancellation rules.

### 6.3 Giấy phép

- Distil-Whisper v3.5: MIT [29].
- Faster-Whisper: MIT [30].
- WhisperLiveKit: Apache-2.0 [31].
- NLLB-200 distilled 600M: CC-BY-NC-4.0; loại khỏi production paid path [23].
- Mã do LectureBridge sở hữu: dự kiến AGPL-3.0-or-later cho Community Edition.

Trước khi công bố AGPL, cần hoàn tất inventory copyright, NOTICE/attribution, Software Bill of Materials và rà soát pháp lý cấu trúc dual-license. Contributor tương lai phải ký CLA hoặc DCO phù hợp nếu công ty muốn cung cấp commercial license riêng.

---

## 7. Go-to-market: B2C trước, campus sau

### 7.1 Private alpha

Tuyển 25 sinh viên qua:

- Hội sinh viên Việt Nam và international student associations.
- ESL center, writing/academic success center.
- Bạn học trong seminar/debate có thể xin consent.
- Nhóm Discord, WhatsApp, WeChat hoặc Zalo của sinh viên quốc tế.

Không trả tiền quảng cáo. Mỗi người tham gia hoàn thành onboarding 15 phút, dùng ít nhất ba session và trả lời một survey ngắn.

Thông điệp thử nghiệm:

> **Read the lecture before it disappears.** Fast English captions for international students, with a private local option.

Không dẫn đầu bằng “AI”, số model hay GPU. Dẫn đầu bằng khoảnh khắc người dùng bắt lại được mạch bài.

### 7.2 Closed beta và paid pilot

Sau alpha, mở tối đa 100 tài khoản. Thử hai landing-page messages:

- A: “Fast live transcript for lectures and debates.”
- B: “Private captions with a free local edition.”

Chỉ bật Student Plus cho người chủ động tham gia paid pilot. Không khóa transcript đã tạo sau paywall. Hardship code được cấp thủ công để học quy mô nhu cầu trước khi tự động hóa.

### 7.3 Campus motion

Chỉ bắt đầu sau khi có ít nhất:

- 50 người dùng đã hoàn thành ba session.
- 10 testimonial có consent.
- Session success trên 98%.
- Tài liệu privacy/security và quy trình support.

Gói campus đầu tiên là pilot 25-50 seat do international office hoặc academic success center tài trợ, không phải triển khai toàn trường. Mục tiêu là học procurement, privacy review và support load.

---

## 8. Giai đoạn 0: người sáng lập phải làm chủ hệ thống

Đây là rủi ro tổ chức lớn nhất hiện nay. Toàn bộ code được tạo với hỗ trợ của Codex trong khi người sáng lập chưa tự viết hoặc khôi phục hệ thống. Nếu không sửa, bất kỳ lỗi dependency, tài khoản hoặc deployment nào cũng có thể dừng sản phẩm.

### 8.1 Cổng bắt buộc trước khi nhận tiền

Người sáng lập phải tự làm, không chỉ quan sát:

- [ ] Clone repo vào thư mục sạch và dựng lại bằng tài liệu.
- [ ] Xác nhận Python trong `.venv`, chạy Ruff và toàn bộ pytest.
- [ ] Chạy offline transcription và giải thích load time, inference time, RTF.
- [ ] Chạy live từ laptop tới iPad và dừng session đúng cách.
- [ ] Vẽ lại luồng PCM16 → WebSocket → ASR → committed text.
- [ ] Tự sửa một CLI flag, viết/chỉnh test và đọc diff.
- [ ] Chẩn đoán ba lỗi giả lập: microphone bị từ chối, port bận, token hết hạn.
- [ ] Tạo release tag thử nghiệm, triển khai và rollback.
- [ ] Khôi phục hệ thống từ repo khi máy cũ không còn.
- [ ] Giải thích nơi secrets, models, transcript và logs được phép tồn tại.

### 8.2 Bộ tài liệu cần hoàn thiện

- `README`: zero-to-running trong một lần đọc.
- Architecture overview: sơ đồ local và cloud, ranh giới tin cậy.
- Operations runbook: start/stop, classroom fallback, incident và recovery.
- Dependency/license inventory và SBOM.
- `LICENSE`, `NOTICE`, `SECURITY.md`, `CONTRIBUTING.md`, CLA/DCO decision.
- CI chạy lint/test trên clean environment.
- Release/rollback checklist.
- ADR cho local/cloud split, provider ASR, retention 7 ngày và AGPL.

### 8.3 Giáo trình bốn tuần

| Tuần | Học gì | Bài thực hành phải nộp |
|---|---|---|
| 1 | Terminal, Git, GitHub, Python 3.12, uv, pytest, Ruff | Fresh clone; sửa một test nhỏ; giải thích Git diff |
| 2 | PCM, sample rate, mono, VAD, Whisper, CUDA, VRAM, WER, RTF | Chạy benchmark hai model; đọc kết quả; mô tả bottleneck |
| 3 | HTTP, WebSocket, JS/TS, `getUserMedia`, AudioWorklet, PWA | Trang demo mic; reconnect; phân biệt partial/final |
| 4 | Auth, quota, database, secrets, logs, privacy, deploy/rollback | Mô phỏng token hết hạn; xóa transcript; khôi phục release |

Nguồn chính thức đề xuất: Python Tutorial [32], Pro Git [33], uv documentation [34], MDN Web APIs/PWA [35] và OWASP Top 10 [36]. Mỗi tuần phải tạo một ghi chú “tôi đã hiểu gì” bằng lời của người sáng lập; không chấp nhận tài liệu do AI tạo mà chưa được diễn giải lại.

### 8.4 Định nghĩa đạt

Giai đoạn 0 hoàn tất khi người sáng lập có thể độc lập:

1. Dựng lại hệ thống.
2. Chạy và quan sát hệ thống.
3. Giải thích dữ liệu đi đâu.
4. Thực hiện thay đổi nhỏ có test.
5. Phát hiện lỗi phổ biến.
6. Rollback khi release hỏng.

Codex có thể tiếp tục tăng tốc, nhưng không còn là người duy nhất hiểu cách sản phẩm tồn tại.

---

## 9. Lộ trình 90 ngày và 12 tháng

### Ngày 0-30: quyền làm chủ và bằng chứng chất lượng

- Hoàn thành Giai đoạn 0 và license inventory.
- Thu audio có consent ở bốn nhóm: lecture chậm, debate nhanh lần lượt, đổi người liên tục và tiếng nói chồng nhau.
- Tạo ground truth cho một bộ nhỏ; đo WER, first-text latency, committed latency và session success.
- Benchmark local Distil-Whisper, Soniox và AssemblyAI trên cùng dữ liệu.
- Private alpha tối đa 25 sinh viên; không thu tiền.

### Ngày 31-60: cloud safety và closed beta

- PWA, auth, quota server-side và temporary key.
- Transcript 7 ngày, export, delete-now và deletion job.
- Monitoring không chứa transcript; cost dashboard và spend alerts.
- Privacy/consent draft và security review.
- Closed beta tối đa 100 sinh viên.

### Ngày 61-90: paid pilot có kiểm soát

- Stripe test mode, webhook idempotency, entitlement và cancellation.
- Bật Student Plus cho nhóm tự nguyện nhỏ.
- Hardship codes và Supporter tier thủ công.
- Báo cáo retention, paid conversion, cost per completed session và support burden.
- Tiếp cận một campus partner cho pilot 25-50 seat nếu KPI đạt.

### Tháng 4-6

- Course glossary MVP.
- Cải thiện reconnect/resume và offline/local installer.
- Campus pilot đầu tiên.
- Quyết định có cần native iOS dựa trên dữ liệu PWA.

### Tháng 7-12

- Mở rộng campus pilots nếu support và privacy review chịu được.
- Đánh giá Android/native channel.
- Đánh giá self-host GPU nếu vượt ngưỡng usage.
- Nghiên cứu translation thương mại như add-on, không gộp miễn phí.

---

## 10. KPI, cổng mở rộng và điều kiện dừng

### North-star metric

**Số session mỗi tuần mà người dùng xác nhận transcript đã giúp họ bắt lại mạch bài.** Không dùng số phút được xử lý làm north star vì có thể tăng chi phí mà không tạo kết quả học tập.

### KPI vận hành và sản phẩm

| Chỉ số | Mục tiêu beta |
|---|---:|
| Time to first session | < 3 phút |
| First partial text | < 2 giây |
| Committed latency | < 5 giây |
| Session success | > 98% |
| Crash-free session | > 99,5% |
| Người dùng đánh giá “giúp theo kịp” | >= 70% |
| D7 retention | > 35% |
| Paid conversion thử nghiệm | >= 5% |
| Cloud COGS/paid revenue | < 30-35% |
| Transcript còn sau TTL | 0 |

### Cổng mở rộng

- Chỉ tăng từ 25 lên 100 người nếu session success >98% và không có sự cố privacy nghiêm trọng.
- Chỉ thu tiền nếu Giai đoạn 0, license review, consent và recovery đã hoàn thành.
- Chỉ làm store nếu ít nhất 20% người bỏ onboarding vì giới hạn PWA hoặc người dùng hoạt động yêu cầu native.
- Chỉ thuê GPU nếu chi phí dự báo giảm ít nhất 25% sau khi tính idle và vận hành.
- Chỉ làm translation nếu có license thương mại, accuracy benchmark và gross margin riêng.

### Điều kiện dừng hoặc pivot

- Sau hai vòng alpha, transcript không được người dùng đánh giá tốt hơn built-in captions cho tình huống mục tiêu.
- D7 retention dưới 20% dù onboarding và reliability đạt.
- Chi phí mỗi người dùng giữ lại vượt khả năng định giá sinh viên.
- Consent hoặc chính sách trường làm cho use case mục tiêu không thể vận hành an toàn.

Khi đó không tăng marketing hoặc server. Pivot ưu tiên sang Community Edition, course glossary hoặc công cụ local cho nhóm nhỏ đã chứng minh nhu cầu.

---

## 11. Checklist CEO trước khi phê duyệt từng giai đoạn

### Trước private alpha

- [ ] Danh sách 25 người tham gia và consent process.
- [ ] ASR budget cap, quota và kill switch.
- [ ] Benchmark protocol; không lưu audio trái phép.
- [ ] Incident contact và cách dừng toàn hệ thống.
- [ ] Không có API key trong client/repo/log.

### Trước closed beta

- [ ] Giai đoạn 0 hoàn tất và CEO tự chạy recovery drill.
- [ ] Privacy Policy/Terms bản beta được rà soát.
- [ ] Transcript TTL 7 ngày được test bằng thời gian giả lập.
- [ ] Account/session deletion được test end-to-end.
- [ ] Provider DPA, retention và training policy được xác nhận.
- [ ] Dashboard chi phí và cảnh báo hoạt động.

### Trước nhận tiền

- [ ] License/NOTICE/SBOM và legal review hoàn tất.
- [ ] Stripe webhook idempotency, refund và cancellation được test.
- [ ] Support SLA phù hợp một người vận hành.
- [ ] Backup/restore và rollback có bằng chứng.
- [ ] Giá hiển thị đúng, quota minh bạch, hardship process tồn tại.
- [ ] NLLB bị loại khỏi mọi production paid path.

### Trước campus pilot

- [ ] Security/privacy questionnaire có câu trả lời.
- [ ] Role, retention, deletion và data export rõ ràng.
- [ ] Không tuyên bố accommodation hoặc compliance chưa được chứng minh.
- [ ] Có owner xử lý incident và yêu cầu xóa dữ liệu.

---

## 12. Rủi ro trọng yếu

| Rủi ro | Xác suất/tác động | Giảm thiểu |
|---|---|---|
| Built-in captions đủ tốt và miễn phí | Cao/Cao | Tập trung debate benchmark, glossary và local trust |
| Một microphone không xử lý lời chồng nhau | Cao/Cao | Cảnh báo rõ, đặt mic tốt, không hứa tuyệt đối |
| Founder bus factor | Cao/Cao | Giai đoạn 0, recovery drill, CI, runbook |
| Bill shock hoặc abuse | Trung/Cao | Quota server-side, token một lần, spend cap, invite-only |
| NLLB không dùng thương mại | Chắc chắn/Cao | Loại khỏi paid path; translation là dự án riêng |
| Recording consent/FERPA | Trung/Cao | Legal review, consent UX, no-audio-storage |
| Vendor lock-in | Trung/Trung | Provider adapter, benchmark hai vendor, export metrics |
| PWA bị Safari giới hạn background | Cao/Trung | Foreground UX; chỉ native khi dữ liệu chứng minh |
| Store policy/fees thay đổi | Trung/Trung | PWA-first, kiểm tra policy tại thời điểm phát hành |
| Độ chính xác khác xa audio benchmark | Cao/Cao | Bộ audio thật có consent, ground truth và cohort-by-cohort metrics |

---

## 13. Khuyến nghị cuối cùng

LectureBridge có lý do hợp lý để tiếp tục, nhưng không nên biến ngay thành một “startup AI transcription” tổng quát. Cơ hội nằm ở một lời hứa hẹp, có thể kiểm chứng: **giúp du học sinh đọc kịp lớp học tiếng Anh, đặc biệt khi tốc độ nói tăng, trong khi vẫn có lựa chọn local miễn phí và riêng tư.**

Hành động đúng trong 90 ngày tới không phải thuê server mạnh hoặc lên store. Đó là:

1. Làm cho người sáng lập thực sự sở hữu tri thức vận hành.
2. Đo accuracy/latency bằng audio thật có consent.
3. Thử private alpha nhỏ với API tính tiền theo giờ và hard cap.
4. Chỉ xây cloud payment sau khi người dùng quay lại vì transcript hữu ích.
5. Giữ Community Edition miễn phí như cam kết lâu dài với sinh viên.

Nếu bốn cổng chất lượng, retention, privacy và founder independence cùng đạt, dự án có thể chuyển từ mini project thành một sản phẩm freemium có biên lợi nhuận lành mạnh mà không hy sinh nhóm người dùng nó được tạo ra để phục vụ.

---

## Phụ lục A. Nguồn tham khảo

1. IIE Open Doors, International Students: https://opendoorsdata.org/annual-release/international-students/
2. University of Leeds, Academic Listening Project: https://teachingexcellence.leeds.ac.uk/research/fellowships/the-academic-listening-project/
3. Apple, Live Captions on iPad: https://support.apple.com/en-ie/guide/ipad/ipad0bbca12e/ipados
4. Google, Live Transcribe: https://support.google.com/accessibility/android/answer/9158064?hl=en-IE
5. Ava App Store/Pricing: https://apps.apple.com/us/app/ava-transcribe-voice-to-text/id1030067058 ; https://www.ava.me/pricing
6. Otter Pricing: https://otter.ai/pricing
7. BBNotes: https://bbnotes.app/
8. Otter Google Play: https://play.google.com/store/apps/details?id=com.aisense.otter
9. Notta Pricing: https://www.notta.ai/en/pricing
10. Notta Google Play: https://play.google.com/store/apps/details?id=com.langogo.transcribe
11. Transkriptor Pricing: https://transkriptor.com/pricing/
12. Live Transcribe plans: https://help.livetranscribe.app/hc/en-us/articles/42117309799181-Subscription-plan-options
13. Captio AI: https://captioai.app/live-captions
14. Captio.dev: https://captio.dev/
15. Aiko App Store: https://apps.apple.com/us/app/aiko/id1672085276
16. MacWhisper: https://www.macwhisper.com/
17. FUTO Voice Input: https://voiceinput.futo.org/
18. Whisper Mobile: https://github.com/hrushik98/whisper-mobile
19. Whisper Android: https://github.com/vilassn/whisper_android
20. Soniox temporary API keys: https://soniox.com/docs/guides/temporary-api-keys
21. Soniox Web SDK: https://soniox.com/docs/sdk/web-SDK
22. AssemblyAI streaming: https://www.assemblyai.com/products/streaming-speech-to-text
23. NLLB model card/license: https://huggingface.co/facebook/nllb-200-distilled-600M
24. Apple Developer Program: https://developer.apple.com/programs/enroll/
25. Google Android developer verification: https://support.google.com/android-developer-console/answer/16561738?hl=en
26. Google limited distribution: https://support.google.com/android-developer-console/answer/16640817?hl=en
27. Stripe pricing: https://stripe.com/pricing
28. RunPod pricing: https://www.runpod.io/pricing
29. Distil-Whisper v3.5: https://huggingface.co/distil-whisper/distil-large-v3.5
30. Faster-Whisper: https://github.com/SYSTRAN/faster-whisper
31. WhisperLiveKit: https://github.com/QuentinFuxa/WhisperLiveKit
32. Python Tutorial: https://docs.python.org/3/tutorial/
33. Pro Git: https://git-scm.com/book/en/v2
34. uv documentation: https://docs.astral.sh/uv/
35. MDN Web APIs: https://developer.mozilla.org/en-US/docs/Web/API
36. OWASP Top 10: https://owasp.org/www-project-top-ten/

## Phụ lục B. Giả định tài chính

- Mọi giá là USD, chưa gồm thuế, refund, chargeback, support lao động và marketing.
- Giá vendor và store có thể thay đổi; phải xác nhận lại trước launch.
- Quota là giới hạn cứng theo tháng, không rollover trong beta.
- Contribution margin không đồng nghĩa lợi nhuận ròng.
- Break-even GPU giả định công suất được sử dụng liên tục; thực tế phải cộng idle và vận hành.
- Báo cáo này là tài liệu chiến lược, không phải tư vấn pháp lý, thuế hoặc đầu tư.

