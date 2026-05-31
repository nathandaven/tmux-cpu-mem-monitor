"""GPU usage monitor for tmux status bar.

Supported platforms:
  - macOS (Apple Silicon): uses `macmon` CLI (sudoless)
  - Linux NVIDIA: uses `nvidia-smi`
  - Linux AMD: reads /sys/class/drm/card*/device/gpu_busy_percent
  - Other: prints "N/A"
"""

import argparse
import json
import os
import platform
import subprocess
import sys


def _run(cmd, timeout=3):
    """Run command and return stdout, or None on failure."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if r.returncode == 0:
            return r.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def gpu_macos_macmon(interval=1):
    """macOS Apple Silicon via macmon pipe (one JSON sample)."""
    try:
        proc = subprocess.Popen(
            ["macmon", "pipe", "-i", str(interval * 1000)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        line = proc.stdout.readline()
        proc.kill()
        proc.wait(timeout=2)
        if line:
            data = json.loads(line)
            usage_ratio = data.get("gpu_usage", [None, None])
            if isinstance(usage_ratio, (list, tuple)) and len(usage_ratio) >= 2:
                pct = usage_ratio[1] * 100
                return f"{pct:3.0f}%"
    except (FileNotFoundError, json.JSONDecodeError, TypeError, IndexError, OSError):
        pass
    return None


def gpu_linux_nvidia():
    """NVIDIA GPU via nvidia-smi."""
    out = _run(
        ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"]
    )
    if out:
        # May return multiple lines for multi-GPU; take first
        try:
            pct = int(out.splitlines()[0].strip())
            return f"{pct:3d}%"
        except ValueError:
            pass
    return None


def gpu_linux_amd():
    """AMD GPU via sysfs."""
    drm = "/sys/class/drm"
    if not os.path.isdir(drm):
        return None
    for card in sorted(os.listdir(drm)):
        busy = os.path.join(drm, card, "device", "gpu_busy_percent")
        if os.path.isfile(busy):
            try:
                pct = int(open(busy).read().strip())
                return f"{pct:3d}%"
            except (ValueError, OSError):
                pass
    return None


def get_gpu_usage(interval=1):
    """Return GPU usage string or None if no GPU / unsupported."""
    system = platform.system()
    if system == "Darwin":
        return gpu_macos_macmon(interval)
    elif system == "Linux":
        # Try NVIDIA first, then AMD
        return gpu_linux_nvidia() or gpu_linux_amd()
    return None


def main(args):
    usage = get_gpu_usage(args.interval)
    if usage is None:
        # No GPU detected or unsupported — exit silently (tmux shows nothing useful)
        # Print empty to avoid clutter
        print("")
    else:
        print(usage)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--interval", type=int, default=1, help="interval in seconds"
    )
    args = parser.parse_args()
    main(args)
