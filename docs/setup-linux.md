# Ubuntu setup

Download the Ubuntu archive from
[Releases](https://github.com/Nguyen-Le-Tuan/lecturebridge/releases), or use the
archive shared with you. On Ubuntu 22.04/24.04 x86-64, extract it into a permanent
writable directory and open a terminal there:

```bash
bash Install.sh
bash Start.sh
```

No Git or system Python installation is needed. Setup downloads private
uv/Python and locked application dependencies. It installs missing `curl`,
`ca-certificates`, and `libgomp1` through apt; `sudo` may request your password.
GPU drivers are not installed or modified. Private Linux CUDA runtime packages
are included in the locked dependencies even on a CPU-only installation.

The [installation reference](installation.md) covers profiles and automatic
model selection; the [model guide](models.md) lists languages and launch commands.
Ubuntu derivatives may work. Other Linux distributions require their own
prerequisite setup.

To force CPU and choose Japanese:

```bash
bash Install.sh --profile cpu --language ja
bash Start.sh
```

To change source language later, close the server, then run:

```bash
bash Start.sh --language zh
```

## Recovery

- Read `.lecturebridge/setup.log` if setup fails. Rerun `bash Install.sh` after
  fixing the reported problem; valid downloads are reused.
- A failed or interrupted setup blocks Start until Install completes.
- Run as your ordinary user; let sudo handle only system packages.
- Keep the extracted folder in place. Do not share its `.venv` with Windows.
- Close any existing server on port 8000 before starting another.
- A missing, warm, or unavailable NVIDIA GPU selects CPU. Use `--profile cpu`
  to avoid GPU inference completely.
- Install updates in a separate extracted folder. Recordings remain under
  `${XDG_DATA_HOME:-~/.local/share}/lecturebridge` until explicitly deleted.

Tailscale is optional for localhost use. Follow the classroom runbook only if
connecting a phone/tablet.
