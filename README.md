# Tmux System Monitor

This plugin is a slight modification of the great work of [hendrikmi](https://github.com/hendrikmi/),
a simple yet flexible tool designed to display CPU and memory usage in the Tmux status bar.

<img src="img/demo.png" alt="" style="width:100%; height:100%;"/>

The functionality is mainly unchanged.  The modification is to display
* the level of battery and charging/discharging status using icons defined in [NerdFonts](https://www.nerdfonts.com/).  Depending the option given, this plugin displays the battery's percentage either in 10 or 3 levels.  See the `#{battery}` placeholder section below, and
* the utilization of GPU/VRAM in systems with nvidia GPUs.


## Installation

1. Install it with the [Tmux Plugin Manager (TPM)](https://github.com/tmux-plugins/tpm) by including the following line in your `.tmux.conf` file.

```bash
set -g @plugin 'cmookj/tmux-sys-monitor'
```

1. Then trigger the installation with `Prefix + I`.

> [!NOTE]
> Some people have encountered issues with their python environment during installation. Check out [issue #11](https://github.com/hendrikmi/tmux-cpu-mem-monitor/issues/11) for some debugging tips.

## Basic Usage

Once installed, the plugin exposes the placeholders `#{cpu}` and `#{mem}`, which can be used in `status-right` and `status-left`. By default, these placeholders display the current CPU and memory usage as a raw percentage.

You can customize the display by passing additional options. For example, `#{mem --total}` will display memory usage as used/total in GB.

## Options

### `#{cpu}` Placeholder

- `-i <num>, --interval <num>` (default `1`):
  - `0`: Compares system CPU times elapsed since last call (non-blocking).
  - `>0`: Compares system CPU times (seconds) elapsed before and after the interval (blocking).
- `--precpu`: Shows the utilization as a percentage for each CPU.

For more details, see the documentation of the underlying [psutil library](https://psutil.readthedocs.io/en/latest/#psutil.cpu_percent).

### `#{mem}` Placeholder

- `-t, --total`: Display memory usage as used/total in GB instead of a percentage.

### `#{disk}` Placeholder
- `-p <path>, --path <path>`: Specify the path to monitor. Defaults: `C:` for Windows, `/System/Volumes/Data` for Mac, and `/` for Linux.
- `-t, --total`: Display disk usage as used/total in GB instead of a percentage.
- `-f, --free`: Display free disk space in GB.

### `#{battery}` Placeholder
- `-t, --time`: Display the remaining battery life time.
- `-p, --percentage`: Display the remaining battery percentage.
- `-l, --long`: Display the remaining battery as a sentence.
- `-f, --fun`: Display the remaining battery in a fun way.
- `-c, --compact`: Display the battery's status (chargning/discharging & level in 10) using an icon.
- `-s, --simple`: Display the battery's status (chargning/discharging & level in 3) using an icon.

### `#{gpu}` Placeholder
**ONLY** for nvidia GPU.
- No option: Display the utilization of GPU in percentage.
- `-p, --mem-percent`: Display the VRAM controller % like `#{mem}`, e.g., `62%`
- `-m, --mem-total`: Display the VRAM used/total, like `#{mem -t}`, e.g., `2.0GB/8.0GB`

## Examples

```bash
set -g status-right "#{cpu} | #{mem} | #{disk}"
```

<img src="img/cpu_mem_disk.png" alt="" style="width:100%; height:100%;"/>

```bash
set -g status-right " CPU: #{cpu} |  MEM: #{mem -t} | 󱛟 DISK: #{disk -t}"
```

<img src="img/cpu_mem_t_disk_t.png" alt="" style="width:100%; height:100%;"/>

```bash
set -g status-right " CPU: #{cpu -i 3} |  MEM: #{mem} | 󱛟 DISK: #{disk -f}"
```

<img src="img/cpu_mem_disk_f.png" alt="" style="width:100%; height:100%;"/>

