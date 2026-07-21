import argparse
import shutil
import subprocess


# nvidia-smi query fields (csv, no header, no units):
#   index, name, utilization.gpu, utilization.memory,
#   memory.used, memory.total, temperature.gpu
_QUERY = (
    "index,name,utilization.gpu,utilization.memory,"
    "memory.used,memory.total,temperature.gpu"
)
_SMI_CMD = [
    "nvidia-smi",
    f"--query-gpu={_QUERY}",
    "--format=csv,noheader,nounits",
]


def _nvidia_smi_available() -> bool:
    """Return True if nvidia-smi is present on PATH."""
    return shutil.which("nvidia-smi") is not None


def _query_gpus() -> list[dict]:
    """Run nvidia-smi and return a list of per-GPU dicts.

    Returns an empty list if the command fails or no GPUs are found.
    """
    try:
        result = subprocess.run(
            _SMI_CMD,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []

    if result.returncode != 0:
        return []

    gpus = []
    for line in result.stdout.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 7:
            continue
        try:
            gpus.append(
                {
                    "index": int(parts[0]),
                    "name": parts[1],
                    "gpu_util": int(parts[2]),       # %
                    "mem_util": int(parts[3]),        # %
                    "mem_used_mib": int(parts[4]),    # MiB
                    "mem_total_mib": int(parts[5]),   # MiB
                    "temperature": int(parts[6]),     # °C
                }
            )
        except ValueError:
            continue

    return gpus


# ---------------------------------------------------------------------------
# Display helpers (each returns a compact string per GPU, joined by " | ")
# ---------------------------------------------------------------------------

def get_gpu_util() -> str:
    """GPU compute utilisation as a percentage — mirrors #{cpu}."""
    gpus = _query_gpus()
    if not gpus:
        return ""
    return " | ".join(f"{g['gpu_util']}%" for g in gpus)


def get_gpu_mem_percent() -> str:
    """GPU memory controller utilisation as a percentage — mirrors #{mem}."""
    gpus = _query_gpus()
    if not gpus:
        return ""
    return " | ".join(f"{g['mem_util']}%" for g in gpus)


def get_gpu_mem_total() -> str:
    """GPU VRAM as used/total in GB — mirrors #{mem -t}."""
    gpus = _query_gpus()
    if not gpus:
        return ""

    parts = []
    for g in gpus:
        used_gb = g["mem_used_mib"] / 1024
        total_gb = g["mem_total_mib"] / 1024
        parts.append(f"{used_gb:.1f}GB/{total_gb:.1f}GB")
    return " | ".join(parts)


def main(args):
    if not _nvidia_smi_available():
        print("")
        return

    if args.mem_total:
        output = get_gpu_mem_total()
    elif args.mem_percent:
        output = get_gpu_mem_percent()
    else:
        output = get_gpu_util()

    print(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Display NVIDIA GPU utilisation for the tmux status bar."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-m",
        "--mem-total",
        action="store_true",
        default=False,
        help="display VRAM usage as used/total in GB  (e.g., 2.0GB/8.0GB)",
    )
    group.add_argument(
        "-p",
        "--mem-percent",
        action="store_true",
        default=False,
        help="display VRAM memory-controller utilisation as a percentage",
    )
    args = parser.parse_args()
    main(args)
