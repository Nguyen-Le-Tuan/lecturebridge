# LectureBridge — Hướng dẫn bắt đầu

**Language:** [English](../getting-started.md) | [Tiếng Việt](getting-started.vi.md) | [简体中文](getting-started.zh-Hans.md) | [繁體中文](getting-started.zh-Hant.md) | [日本語](getting-started.ja.md) | [한국어](getting-started.ko.md)

LectureBridge hiển thị phụ đề trực tiếp trong trình duyệt và có thể dịch sang tiếng Việt. Hướng dẫn này giúp bạn cài trên máy Windows hoặc Ubuntu mới rồi thử một phiên ngắn. Bạn không cần tự cài Git, Python hay CUDA Toolkit.

**Ngôn ngữ tài liệu, ngôn ngữ được nói và ngôn ngữ bản dịch là ba lựa chọn khác nhau.** Đọc hướng dẫn tiếng Việt không đổi cấu hình ứng dụng. Hiện ứng dụng nhận dạng tiếng Anh, Trung phổ thông, Nhật và Hàn; bản dịch đầu ra là tiếng Việt. Tiếng Việt chưa có trong danh sách ngôn ngữ nguồn. Giao diện studio dùng tiếng Việt, thông báo bộ cài dùng tiếng Anh.

## 1. Chuẩn bị

- Windows 10/11 x86-64 hoặc Ubuntu 22.04/24.04 x86-64.
- RAM tối thiểu 4 GB và ổ cài đặt còn ít nhất 20 GB.
- Internet để tải thư viện và model. Bộ cài có thể tải vài GB; ổ chứa cache model cần ít nhất 2 GB trống và thêm khoảng 2,5 GB nếu bật dịch.
- Microphone và sự cho phép để thu âm. GPU NVIDIA là tùy chọn; chạy CPU có thể chậm hơn.

## 2. Tải và giải nén

Mở [Releases](https://github.com/Nguyen-Le-Tuan/lecturebridge/releases), bung mục **Assets**. Chọn file `*-windows-x64.zip` cho Windows hoặc `*-ubuntu-x64.tar.gz` cho Ubuntu. Chọn gói cài này thay vì **Source code** do GitHub tự tạo. Nếu đã được gửi trực tiếp gói cài, dùng file đó. Repo private yêu cầu quyền truy cập để tải từ GitHub.

Giải nén toàn bộ vào một thư mục bạn có quyền ghi và muốn giữ lâu dài. Mở thư mục bên trong có `Install.cmd` và `Install.sh`. Chạy từ thư mục đã giải nén, không chạy ngay trong cửa sổ xem file nén.

## 3. Cài đặt và mở ứng dụng

### Windows

1. Bấm đúp `Install.cmd`.
2. Chọn ngôn ngữ được nói trong audio. Chờ dòng **Setup complete**.
3. Nếu Windows hỏi quyền cài Microsoft Visual C++, chấp nhận để tiếp tục. Nếu bộ cài báo cần khởi động lại, tự khởi động lại Windows rồi chạy Install lần nữa.
4. Bấm đúp `Start.cmd`.

### Ubuntu

Mở terminal trong thư mục đã giải nén. Chạy lệnh đầu, chờ **Setup complete**, rồi mới chạy lệnh thứ hai:

```bash
bash Install.sh
bash Start.sh
```

Chọn ngôn ngữ được nói khi được hỏi. Nhập mật khẩu `sudo` nếu cần cài gói hệ thống còn thiếu. Terminal không hiện ký tự lúc nhập mật khẩu; nhập xong rồi nhấn Enter.

Install tải thư viện và chọn model nhỏ để bắt đầu. Bước này chỉ kiểm tra cấu hình, không chạy inference và không thay driver GPU. Lần đầu khởi chạy với GPU đủ điều kiện, Start chạy bài kiểm tra `tiny` có giới hạn; nếu không đạt, phiên đó dùng CPU. Trình duyệt sẽ mở [http://127.0.0.1:8000](http://127.0.0.1:8000). Giữ terminal mở trong khi dùng ứng dụng.

## 4. Thử một phiên ngắn

Cho phép trình duyệt dùng microphone. Lượt đầu tắt lưu và tắt dịch, nói trong 15–30 giây. Bấm **Bắt đầu nghe** để bắt đầu và **Dừng phiên** để kết thúc. Dừng trong ứng dụng trước, sau đó nhấn Ctrl+C ở terminal nếu muốn tắt server.

Để thử dịch trong một lượt riêng, chọn **Tiếng Việt** hoặc **Song ngữ** rồi đồng ý tải model. Bộ dịch chạy CPU, chỉ dịch phần mới đã được chốt và có thể trễ hàng chục giây.

Bật **Lưu bản ghi** trước phiên nếu muốn giữ audio và nội dung. Sau đó mở **Thư viện** để nghe lại, tải TXT/JSON/WAV. Audio lưu dạng WAV; transcript đã chốt và bản dịch đã có nằm trong `library.sqlite3`. Dùng chức năng xuất TXT hoặc JSON để tạo file văn bản riêng. Thư viện ở `%LOCALAPPDATA%\LectureBridge` trên Windows hoặc `${XDG_DATA_HOME:-~/.local/share}/lecturebridge` trên Ubuntu. File xuất qua trình duyệt nằm ở thư mục tải xuống của trình duyệt.

## 5. Chọn ngôn ngữ được nói

| Ngôn ngữ audio | Mã |
| --- | --- |
| Tiếng Anh | `en` |
| Tiếng Trung phổ thông | `zh` |
| Tiếng Trung với thiết lập nguồn dịch phồn thể | `zh-Hant` |
| Tiếng Nhật | `ja` |
| Tiếng Hàn | `ko` |

Tắt server trước khi đổi ngôn ngữ. Ví dụ chuyển sang tiếng Trung:

```powershell
.\Start.cmd --language zh
```

```bash
bash Start.sh --language zh
```

Chọn lệnh đúng với hệ điều hành. Start nhớ lựa chọn này. `zh-Hant` dùng cùng bộ nhận dạng với `zh`, không bảo đảm transcript sẽ viết bằng chữ phồn thể. Tiếng Trung/Nhật/Hàn cần model đa ngôn ngữ như `tiny`, `base`, `small`; model `.en` và `distil-large-v3.5` chỉ hỗ trợ tiếng Anh.

## 6. Khi gặp lỗi

- Cài chưa xong: đọc `.lecturebridge/setup.log`, xử lý lỗi được báo rồi chạy lại Install. Start bị chặn tới khi cài thành công.
- Trình duyệt không tự mở: chờ server khởi động rồi tự mở `http://127.0.0.1:8000`.
- Cổng 8000 đang được dùng: tắt server cũ trước.
- Muốn chỉ dùng CPU: tắt server, chạy một lệnh dưới đây trong thư mục cài. `en` là audio tiếng Anh; thay bằng mã nguồn bạn cần.

```powershell
.\Install.cmd -Profile cpu -Language en
```

```bash
bash Install.sh --profile cpu --language en
```

Giữ các phiên đầu ngắn. **Server chạy trực tiếp không có watchdog nhiệt độ.** Dừng nếu máy nóng hoặc phản hồi kém. Bài kiểm tra GPU có giới hạn giúp giảm thời gian thử, nhưng không thể ngăn mọi lỗi driver hoặc sập máy.

Dùng ngay trên máy không cần Tailscale. Nếu dùng điện thoại/iPad, xem hướng dẫn HTTPS Tailscale bên dưới. Khi cập nhật, cài bản mới vào thư mục mới; không chuyển `.venv` giữa các máy hay hệ điều hành. Bản ghi đã lưu vẫn nằm trong thư mục dữ liệu người dùng.

## Tài liệu liên quan

Các tài liệu tham khảo bên dưới hiện dùng tiếng Anh.

- [Cài đặt Windows](../setup-windows.md)
- [Cài đặt Ubuntu](../setup-linux.md)
- [Profile cài đặt và chọn cấu hình](../installation.md)
- [Ngôn ngữ, model và lệnh chạy](../models.md)
- [Điện thoại/iPad qua Tailscale HTTPS](../classroom-runbook.md)
- [Xử lý lỗi](../troubleshooting.md)
- [Kiểm thử tính năng](../testing.md)
- [Mẫu báo cáo test](../acceptance-report-template.md)
- [Giới thiệu dự án](../../README.md)
