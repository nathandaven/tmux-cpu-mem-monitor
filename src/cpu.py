import argparse

import psutil


def get_cpu_temperature() -> str:
    core_temps = psutil.sensors_temperatures()["coretemp"]
    total_temp = 0
    num_cores = 0
    for ct in core_temps:
        if "Core" in ct.label:
            total_temp += ct[1]
            num_cores += 1
    temp_avg = round(total_temp / num_cores, 1)
    return f"{temp_avg}"


def get_cpu_usage(interval: int, percpu: bool) -> str:
    """Display CPU usage as a percentage"""
    cpu_usage = psutil.cpu_percent(interval=interval, percpu=percpu)

    if percpu:
        percpu_str = ", ".join(map(str, cpu_usage))
        return percpu_str
    return f"{cpu_usage}%"


def get_cpu_stats(interval: int, percpu: bool) -> str:
    cpu_usage = get_cpu_usage(interval, percpu)
    cpu_temp = get_cpu_temperature()
    return f"{cpu_usage}, T:{cpu_temp}C"


def main(args):
    # cpu_usage = get_cpu_usage(args.interval, args.percpu)
    # print(cpu_usage)
    cpu_stats = get_cpu_stats(args.interval, args.percpu)
    print(cpu_stats)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--interval", type=int, default=1, help="interval in seconds"
    )
    parser.add_argument(
        "--percpu", action="store_true", default=False, help="display per cpu usage"
    )
    args = parser.parse_args()
    main(args)
