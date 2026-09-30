# Troubleshooting

## `nvidia-smi` is not found

Install or repair the NVIDIA display driver, then open a new terminal. Use
`--device cpu --model tiny.en` if the computer has no NVIDIA GPU.

## Windows reports a missing CUDA DLL

LectureBridge requires `cublas64_12.dll`, `cudnn64_9.dll`, and
`cudnn_ops64_9.dll` on `PATH`. Install CUDA Toolkit 12 and cuDNN 9 from NVIDIA,
then restart PowerShell. `nvidia-smi` showing a GPU is not sufficient by itself.

## Linux reports missing CUDA runtime packages

Run:

```bash
uv sync --locked
uv run lecturebridge-preflight --device cuda --deep
```

The project adds its pip-installed cuBLAS/cuDNN directories to
`LD_LIBRARY_PATH` exactly once before starting Python.

## Model verification fails

Do not edit a cached model. Remove only the named corrupted Hugging Face
snapshot, then download it again:

```bash
uv run lecturebridge-models download --model distil-large-v3.5
uv run lecturebridge-models verify --model distil-large-v3.5
```

The repository, revision, size, and SHA-256 values are defined in
`models.lock.json`.

## GPU runs out of memory

Stop the server and retry models in this order:

```bash
uv run lecturebridge-live --model small.en
uv run lecturebridge-live --model base.en
uv run lecturebridge-live --model tiny.en
```

Translation is forced to CPU to reserve VRAM for English ASR. Disable
translation first when diagnosing memory pressure.

## Preflight fails only on Tailscale

Confirm that Tailscale is installed, signed in, and online on both devices.
On Windows, run `tailscale serve` from an Administrator terminal. On Linux,
the first Serve configuration may require administrative approval.

## CPU fallback is too slow

Use `tiny.en` or `base.en`, connect power, close other CPU-heavy programs, and
measure with a permitted recording. CPU fallback provides compatibility, not a
guaranteed real-time classroom target.
