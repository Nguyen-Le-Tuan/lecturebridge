# LectureBridge — 新手安装指南

**Language:** [English](../getting-started.md) | [Tiếng Việt](getting-started.vi.md) | [简体中文](getting-started.zh-Hans.md) | [繁體中文](getting-started.zh-Hant.md) | [日本語](getting-started.ja.md) | [한국어](getting-started.ko.md)

LectureBridge 在浏览器中显示实时字幕，并可将字幕翻译成越南语。本指南帮助你在新的 Windows 或 Ubuntu 电脑上完成安装并试用一个短会话，无需自行安装 Git、Python 或 CUDA Toolkit。

**文档语言、音频语言和翻译目标语言是不同的设置。** 阅读中文版指南不会更改应用配置。目前语音识别支持英语、普通话、日语和韩语，翻译目标为越南语；越南语尚不能选作语音输入语言。应用界面目前为越南语，安装程序提示为英语。

## 1. 安装前准备

- Windows 10/11 x86-64 或 Ubuntu 22.04/24.04 x86-64。
- 至少 4 GB 内存，安装盘至少有 20 GB 可用空间。
- 安装和下载模型时需要网络。依赖库可能占用数 GB；模型缓存盘至少保留 2 GB 空间，启用翻译还需约 2.5 GB。
- 麦克风，以及采集相关音频的许可。NVIDIA GPU 不是必需的，但 CPU 模式可能较慢。

## 2. 下载并解压

打开 [Releases](https://github.com/Nguyen-Le-Tuan/lecturebridge/releases)，展开 **Assets**。Windows 下载 `*-windows-x64.zip`，Ubuntu 下载 `*-ubuntu-x64.tar.gz`。请选择这些安装包，不要选择 GitHub 自动生成的 **Source code**。如果已收到他人直接发来的安装包，可直接使用。私有仓库的 GitHub 下载需要仓库访问权限。

将整个压缩包解压到有写入权限、准备长期保留的文件夹。打开其中包含 `Install.cmd` 和 `Install.sh` 的文件夹。请从解压后的目录运行安装程序，不要直接在压缩包查看器中运行。

## 3. 安装并启动

### Windows

1. 双击 `Install.cmd`。
2. 选择音频中实际使用的语言，等待 **Setup complete**。
3. 如果 Windows 请求安装 Microsoft Visual C++，批准后继续。如果提示必须重启，请自行重启 Windows，再运行 Install。
4. 双击 `Start.cmd`。

### Ubuntu

在解压后的文件夹中打开终端。先运行第一条命令，看到 **Setup complete** 后再运行第二条：

```bash
bash Install.sh
bash Start.sh
```

按提示选择音频语言。安装缺少的系统软件包时可能需要输入 `sudo` 密码。输入密码时终端不会显示字符，输入完成后按 Enter 即可。

Install 会下载依赖并选择较小的起始模型。安装期间仅检查硬件，不执行模型推理，也不更改 GPU 驱动。首次使用符合条件的 GPU 启动时，Start 会运行有时间和资源限制的 `tiny` 检查；检查失败则在该会话中使用 CPU。浏览器会打开 [http://127.0.0.1:8000](http://127.0.0.1:8000)。使用期间请保持终端开启。

## 4. 先试用一个短会话

允许浏览器使用麦克风。第一次先关闭录音保存和翻译，说话 15–30 秒。**Bắt đầu nghe** 表示开始监听，**Dừng phiên** 表示停止会话。先在应用中停止，再按终端中的 Ctrl+C 关闭服务器。

另开一个会话测试翻译：选择 **Tiếng Việt**（越南语）或 **Song ngữ**（双语），并同意下载模型。翻译在 CPU 上运行，只处理新确认的字幕，可能延迟数十秒。

如需保存音频和文字，请在会话开始前打开 **Lưu bản ghi**（保存录音）。结束后进入 **Thư viện**（资料库）播放或导出 TXT/JSON/WAV。音频保存为 WAV；已确认字幕和已有翻译保存在 `library.sqlite3` 中，导出后才会得到独立文本文件。Windows 资料库位于 `%LOCALAPPDATA%\LectureBridge`，Ubuntu 位于 `${XDG_DATA_HOME:-~/.local/share}/lecturebridge`。浏览器导出的文件保存到浏览器设置的下载位置。

## 5. 选择音频语言

| 音频语言 | 代码 |
| --- | --- |
| 英语 | `en` |
| 普通话 | `zh` |
| 普通话，使用繁体中文翻译源设置 | `zh-Hant` |
| 日语 | `ja` |
| 韩语 | `ko` |

更改语言前先关闭服务器。例如，切换为普通话：

```powershell
.\Start.cmd --language zh
```

```bash
bash Start.sh --language zh
```

按操作系统选择一条命令。Start 会记住选择。`zh-Hant` 与 `zh` 使用相同的语音识别器，不保证字幕一定为繁体。中文、日语和韩语需要 `tiny`、`base`、`small` 等多语言模型；`.en` 模型和 `distil-large-v3.5` 仅支持英语。

## 6. 遇到问题时

- 安装失败：查看 `.lecturebridge/setup.log`，处理提示的问题后重跑 Install。安装成功前 Start 不会启动应用。
- 浏览器未打开：等待服务器启动后，手动打开 `http://127.0.0.1:8000`。
- 8000 端口被占用：先关闭之前的服务器。
- 希望只使用 CPU：先关闭服务器，在安装目录运行以下对应系统的命令。示例使用普通话音频。

```powershell
.\Install.cmd -Profile cpu -Language zh
```

```bash
bash Install.sh --profile cpu --language zh
```

初次测试请保持简短。**实时服务器没有温度监控自动停止功能。** 如果电脑过热或响应变差，请停止会话。受限的 GPU 检查可以缩短测试时间，但不能防止所有驱动或系统崩溃。

在同一电脑上使用不需要 Tailscale。连接手机或 iPad 时，请查看下方 HTTPS Tailscale 指南。更新时将新版本安装到新文件夹，不要跨电脑或操作系统复制 `.venv`。已保存的录音仍在用户数据目录中。

## 相关文档

以下参考文档目前为英语。

- [Windows 安装](../setup-windows.md)
- [Ubuntu 安装](../setup-linux.md)
- [安装配置与硬件选择](../installation.md)
- [语言、模型和运行命令](../models.md)
- [手机／平板的 Tailscale HTTPS 设置](../classroom-runbook.md)
- [故障排查](../troubleshooting.md)
- [功能测试](../testing.md)
- [测试报告模板](../acceptance-report-template.md)
- [项目介绍](../../README.md)
