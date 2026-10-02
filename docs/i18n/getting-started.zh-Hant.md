# LectureBridge — 新手安裝指南

**Language:** [English](../getting-started.md) | [Tiếng Việt](getting-started.vi.md) | [简体中文](getting-started.zh-Hans.md) | [繁體中文](getting-started.zh-Hant.md) | [日本語](getting-started.ja.md) | [한국어](getting-started.ko.md)

LectureBridge 在瀏覽器中顯示即時字幕，並可將字幕翻譯成越南語。本指南協助你在新的 Windows 或 Ubuntu 電腦上完成安裝並試用一段短會話，不需要自行安裝 Git、Python 或 CUDA Toolkit。

**文件語言、音訊語言與翻譯目標語言是不同的設定。** 閱讀繁體中文指南不會變更應用程式設定。目前語音辨識支援英語、中文普通話、日語及韓語，翻譯目標為越南語；越南語尚不能選作語音輸入語言。應用程式介面目前為越南語，安裝程式訊息為英語。

## 1. 安裝前準備

- Windows 10/11 x86-64 或 Ubuntu 22.04/24.04 x86-64。
- 至少 4 GB 記憶體，安裝磁碟至少有 20 GB 可用空間。
- 安裝與下載模型時需要網路。相依套件可能占用數 GB；模型快取磁碟至少保留 2 GB 空間，啟用翻譯另需約 2.5 GB。
- 麥克風，以及擷取相關音訊的許可。NVIDIA GPU 並非必要，但 CPU 模式可能較慢。

## 2. 下載並解壓縮

開啟 [Releases](https://github.com/Nguyen-Le-Tuan/lecturebridge/releases)，展開 **Assets**。Windows 下載 `*-windows-x64.zip`，Ubuntu 下載 `*-ubuntu-x64.tar.gz`。請選擇這些安裝封裝，而不是 GitHub 自動產生的 **Source code**。若已直接收到安裝檔，也可直接使用。從私有儲存庫下載需要該儲存庫的存取權限。

將整個壓縮檔解壓縮至有寫入權限、準備長期保留的資料夾。開啟其中包含 `Install.cmd` 與 `Install.sh` 的資料夾。請從解壓縮後的位置執行，不要直接在壓縮檔檢視器中執行。

## 3. 安裝並啟動

### Windows

1. 按兩下 `Install.cmd`。
2. 選擇音訊中實際使用的語言，等待 **Setup complete**。
3. 若 Windows 要求安裝 Microsoft Visual C++，允許後繼續。若安裝程式要求重新啟動，請自行重新啟動 Windows，再執行 Install。
4. 按兩下 `Start.cmd`。

### Ubuntu

在解壓縮後的資料夾中開啟終端機。先執行第一行，看到 **Setup complete** 後再執行第二行：

```bash
bash Install.sh
bash Start.sh
```

依提示選擇音訊語言。安裝缺少的系統套件時可能需要輸入 `sudo` 密碼。輸入密碼時終端機不會顯示字元，輸入完成後按 Enter 即可。

Install 會下載相依套件並選擇較小的起始模型。安裝期間只檢查硬體，不執行模型推論，也不更動 GPU 驅動程式。首次使用符合條件的 GPU 啟動時，Start 會執行有時間與資源限制的 `tiny` 檢查；失敗時，該會話改用 CPU。瀏覽器會開啟 [http://127.0.0.1:8000](http://127.0.0.1:8000)。使用期間請保持終端機開啟。

## 4. 先試用一段短會話

允許瀏覽器使用麥克風。第一次先關閉錄音儲存與翻譯，說話 15–30 秒。**Bắt đầu nghe** 表示開始聆聽，**Dừng phiên** 表示停止會話。先在應用程式中停止，再於終端機按 Ctrl+C 關閉伺服器。

另開會話測試翻譯：選擇 **Tiếng Việt**（越南語）或 **Song ngữ**（雙語），並同意下載模型。翻譯在 CPU 上執行，只處理新確認的字幕，可能延遲數十秒。

若要儲存音訊與文字，請在會話開始前開啟 **Lưu bản ghi**（儲存錄音）。結束後進入 **Thư viện**（資料庫）播放或匯出 TXT/JSON/WAV。音訊以 WAV 儲存；已確認字幕與已有翻譯存於 `library.sqlite3`，匯出後才會產生獨立文字檔。Windows 儲存位置為 `%LOCALAPPDATA%\LectureBridge`，Ubuntu 為 `${XDG_DATA_HOME:-~/.local/share}/lecturebridge`。瀏覽器匯出的檔案使用瀏覽器設定的下載位置。

## 5. 選擇音訊語言

| 音訊語言 | 代碼 |
| --- | --- |
| 英語 | `en` |
| 中文普通話 | `zh` |
| 普通話，使用繁體中文翻譯來源設定 | `zh-Hant` |
| 日語 | `ja` |
| 韓語 | `ko` |

更改語言前先關閉伺服器。例如，使用繁體中文翻譯來源設定：

```powershell
.\Start.cmd --language zh-Hant
```

```bash
bash Start.sh --language zh-Hant
```

依作業系統選擇一行指令。Start 會記住選擇。`zh-Hant` 與 `zh` 使用相同的語音辨識器，並不保證字幕一定為繁體。中文、日語和韓語需要 `tiny`、`base`、`small` 等多語言模型；`.en` 模型和 `distil-large-v3.5` 僅支援英語。

## 6. 遇到問題時

- 安裝失敗：查看 `.lecturebridge/setup.log`，處理提示的問題後重新執行 Install。安裝成功前 Start 不會啟動應用程式。
- 瀏覽器沒有開啟：等待伺服器啟動後，手動開啟 `http://127.0.0.1:8000`。
- 8000 連接埠被占用：先關閉之前的伺服器。
- 希望只使用 CPU：先關閉伺服器，在安裝資料夾執行對應系統的指令。此範例使用普通話與繁體中文翻譯來源設定。

```powershell
.\Install.cmd -Profile cpu -Language zh-Hant
```

```bash
bash Install.sh --profile cpu --language zh-Hant
```

初次測試請保持簡短。**即時伺服器沒有溫度監控自動停止功能。** 若電腦過熱或反應變差，請停止會話。受限的 GPU 檢查能縮短測試時間，但無法防止所有驅動程式或系統當機。

在同一台電腦上使用不需要 Tailscale。連接手機或 iPad 時，請參考下方 HTTPS Tailscale 指南。更新時將新版本安裝至新的資料夾，不要跨電腦或作業系統複製 `.venv`。已儲存錄音仍在使用者資料目錄中。

## 相關文件

以下參考文件目前為英語。

- [Windows 安裝](../setup-windows.md)
- [Ubuntu 安裝](../setup-linux.md)
- [安裝設定與硬體選擇](../installation.md)
- [語言、模型與執行指令](../models.md)
- [手機／平板的 Tailscale HTTPS 設定](../classroom-runbook.md)
- [疑難排解](../troubleshooting.md)
- [功能測試](../testing.md)
- [測試報告範本](../acceptance-report-template.md)
- [專案介紹](../../README.md)
