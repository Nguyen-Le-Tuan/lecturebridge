# LectureBridge — 처음 시작하기

**Language:** [English](../getting-started.md) | [Tiếng Việt](getting-started.vi.md) | [简体中文](getting-started.zh-Hans.md) | [繁體中文](getting-started.zh-Hant.md) | [日本語](getting-started.ja.md) | [한국어](getting-started.ko.md)

LectureBridge는 브라우저에서 실시간 자막을 보여 주고, 필요할 때 베트남어로 번역합니다. 이 가이드는 새 Windows 또는 Ubuntu 컴퓨터에 설치한 뒤 짧은 세션을 시작하는 방법을 설명합니다. Git, Python, CUDA Toolkit을 직접 설치할 필요는 없습니다.

**문서 언어, 음성 입력 언어, 번역 결과 언어는 서로 다릅니다.** 한국어 가이드를 읽어도 앱 설정은 바뀌지 않습니다. 현재 음성 인식은 영어, 중국어 보통화, 일본어, 한국어를 지원하며 번역 결과는 베트남어입니다. 베트남어는 아직 음성 입력 언어로 선택할 수 없습니다. 앱 화면은 베트남어, 설치 프로그램 메시지는 영어입니다.

## 1. 준비 사항

- Windows 10/11 x86-64 또는 Ubuntu 22.04/24.04 x86-64.
- RAM 4 GB 이상, 설치 드라이브의 여유 공간 20 GB 이상.
- 설치 및 모델 다운로드용 인터넷 연결. 라이브러리 다운로드는 수 GB가 될 수 있습니다. 모델 캐시 드라이브에도 최소 2 GB가 필요하며, 번역을 사용하려면 약 2.5 GB가 추가로 필요합니다.
- 마이크와 해당 음성을 수집할 수 있는 허가. NVIDIA GPU는 필수가 아니지만 CPU 모드는 느릴 수 있습니다.

## 2. 다운로드하고 압축 풀기

[Releases](https://github.com/Nguyen-Le-Tuan/lecturebridge/releases)에서 **Assets**를 펼칩니다. Windows는 `*-windows-x64.zip`, Ubuntu는 `*-ubuntu-x64.tar.gz`를 받으세요. GitHub가 자동으로 만드는 **Source code** 대신 이 설치용 압축 파일을 선택합니다. 직접 전달받은 설치 파일도 사용할 수 있습니다. 비공개 저장소에서 다운로드하려면 저장소 접근 권한이 필요합니다.

전체 압축 파일을 쓰기 권한이 있고 계속 사용할 폴더에 풉니다. 그 안에서 `Install.cmd`와 `Install.sh`가 있는 폴더를 여세요. 압축 파일 뷰어 안에서 바로 실행하지 말고, 압축을 푼 폴더에서 실행하세요.

## 3. 설치하고 실행하기

### Windows

1. `Install.cmd`를 두 번 클릭합니다.
2. 오디오에서 실제로 말하는 언어를 선택하고 **Setup complete**가 나올 때까지 기다립니다.
3. Microsoft Visual C++ 설치 권한을 요청하면 승인합니다. 다시 시작해야 한다는 메시지가 나오면 Windows를 직접 다시 시작한 뒤 Install을 다시 실행합니다.
4. `Start.cmd`를 두 번 클릭합니다.

### Ubuntu

압축을 푼 폴더에서 터미널을 엽니다. 첫 번째 명령을 실행하고 **Setup complete**를 확인한 뒤 두 번째 명령을 실행하세요.

```bash
bash Install.sh
bash Start.sh
```

안내에 따라 음성 언어를 선택합니다. 누락된 시스템 패키지를 설치할 때 `sudo` 암호를 요청할 수 있습니다. 암호를 입력하는 동안 문자가 표시되지 않는 것은 정상입니다. 입력을 마치고 Enter를 누르세요.

Install은 라이브러리를 다운로드하고 작은 시작 모델을 선택합니다. 설치 중에는 하드웨어만 확인하며 모델 추론을 실행하거나 GPU 드라이버를 변경하지 않습니다. 조건에 맞는 GPU로 처음 시작하면 Start가 시간과 자원 사용을 제한한 `tiny` 검사를 실행합니다. 실패하면 해당 세션은 CPU로 시작합니다. 브라우저에서 [http://127.0.0.1:8000](http://127.0.0.1:8000)이 열립니다. 앱을 사용하는 동안 터미널을 열어 두세요.

## 4. 짧은 세션으로 확인하기

브라우저의 마이크 사용을 허용합니다. 처음에는 녹음 저장과 번역을 끄고 15–30초 동안 말해 보세요. **Bắt đầu nghe**는 듣기 시작, **Dừng phiên**은 세션 중지입니다. 먼저 앱에서 세션을 중지한 뒤, 터미널에서 Ctrl+C를 누르면 서버가 종료됩니다.

번역은 별도의 세션에서 확인하세요. **Tiếng Việt**(베트남어) 또는 **Song ngữ**(이중 언어)를 선택하고 모델 다운로드를 승인합니다. 번역은 CPU에서 실행되며 새로 확정된 자막만 처리합니다. 수십 초 지연될 수 있습니다.

오디오와 텍스트를 보관하려면 세션 시작 전에 **Lưu bản ghi**(녹음 저장)를 켭니다. 종료 후 **Thư viện**(라이브러리)에서 재생하거나 TXT/JSON/WAV로 내보낼 수 있습니다. 오디오는 WAV로, 확정된 자막과 완료된 번역은 `library.sqlite3`에 저장됩니다. 별도 텍스트 파일이 필요하면 내보내기를 사용하세요. Windows 저장 위치는 `%LOCALAPPDATA%\LectureBridge`, Ubuntu는 `${XDG_DATA_HOME:-~/.local/share}/lecturebridge`입니다. 브라우저로 내보낸 파일은 브라우저의 다운로드 설정에 따라 저장됩니다.

## 5. 음성 언어 선택하기

| 음성 언어 | 코드 |
| --- | --- |
| 영어 | `en` |
| 중국어 보통화 | `zh` |
| 보통화, 번역 원문을 번체 중국어로 처리하는 설정 | `zh-Hant` |
| 일본어 | `ja` |
| 한국어 | `ko` |

언어를 바꾸기 전에 서버를 종료하세요. 한국어로 바꾸는 예입니다.

```powershell
.\Start.cmd --language ko
```

```bash
bash Start.sh --language ko
```

운영체제에 맞는 명령 하나를 실행합니다. Start는 선택을 기억합니다. `zh-Hant`는 `zh`와 같은 음성 인식기를 사용하므로 자막이 반드시 번체자로 나오지는 않습니다. 중국어·일본어·한국어는 `tiny`, `base`, `small` 같은 다국어 모델이 필요합니다. `.en` 모델과 `distil-large-v3.5`는 영어만 지원합니다.

## 6. 문제가 생겼을 때

- 설치 실패: `.lecturebridge/setup.log`를 읽고 표시된 문제를 해결한 뒤 Install을 다시 실행합니다. 설치가 끝나기 전에는 Start가 앱을 실행하지 않습니다.
- 브라우저가 열리지 않음: 서버가 시작될 때까지 기다린 뒤 `http://127.0.0.1:8000`을 직접 엽니다.
- 포트 8000이 사용 중: 이전 서버를 먼저 종료합니다.
- CPU만 사용하고 싶음: 서버를 종료한 뒤 설치 폴더에서 운영체제에 맞는 아래 명령을 실행합니다. 예시는 한국어 음성용입니다.

```powershell
.\Install.cmd -Profile cpu -Language ko
```

```bash
bash Install.sh --profile cpu --language ko
```

첫 세션은 짧게 진행하세요. **실시간 서버에는 온도에 따른 자동 중지 기능이 없습니다.** 컴퓨터가 뜨거워지거나 반응이 느려지면 중지하세요. 제한된 GPU 검사는 테스트 시간을 줄이지만 모든 드라이버 또는 시스템 충돌을 막을 수는 없습니다.

같은 컴퓨터에서 사용할 때는 Tailscale이 필요 없습니다. 휴대폰이나 iPad를 연결하려면 아래 Tailscale HTTPS 안내를 참고하세요. 업데이트는 새 폴더에 설치하고, `.venv`를 다른 컴퓨터나 운영체제로 복사하지 마세요. 저장된 녹음은 사용자 데이터 폴더에 남습니다.

## 관련 문서

아래 참고 문서는 현재 영어로 제공됩니다.

- [Windows 설치](../setup-windows.md)
- [Ubuntu 설치](../setup-linux.md)
- [설치 프로필 및 하드웨어 선택](../installation.md)
- [언어·모델·실행 명령](../models.md)
- [휴대폰/태블릿 Tailscale HTTPS 설정](../classroom-runbook.md)
- [문제 해결](../troubleshooting.md)
- [기능 테스트](../testing.md)
- [테스트 보고서 양식](../acceptance-report-template.md)
- [프로젝트 소개](../../README.md)
