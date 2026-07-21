#!/usr/bin/env bash

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Checks if Python3 is installed
check_python_installation() {
    if ! command -v python3 >/dev/null; then
        tmux display-message "Python3 is required but not installed. Please install Python3."
        exit 1 # Exit the script if Python3 is not installed
    fi
}

# Sets up the virtual environment and install dependencies
setup_virtual_env() {
    if [ ! -d "$CURRENT_DIR/venv" ]; then
        tmux display-message "tmux-cpu-memory: Setting up virtual environment..."
        if python3 -m venv "$CURRENT_DIR/venv"; then
            if "$CURRENT_DIR/venv/bin/pip" install -r "$CURRENT_DIR/requirements.txt"; then
                tmux display-message "tmux-cpu-memory plugin installed successfully."
            else
                tmux display-message "tmux-cpu-memory: Failed to install dependencies."
                exit 1 # Exit if pip fails to install dependencies
            fi
        else
            tmux display-message "tmux-cpu-memory: Failed to create virtual environment."
            exit 1 # Exit if virtual environment creation fails
        fi
    else
        tmux display-message "tmux-cpu-memory: Virtual environment already exists."
    fi
}

# Updates tmux option with the cpu or mem script command.
# Handles multiple occurrences of the same placeholder with different flags,
# e.g., both #{gpu} and #{gpu -p} in the same status string.
update_placeholder() {
    local placeholder="$1"
    local option="$2"
    local script="$3"
    local option_value
    option_value="$(tmux show-option -gqv "$option")"

    # Collect all distinct #{placeholder...} variants present in the string,
    # sorted longest-first so that e.g., "#{gpu -p}" is replaced before "#{gpu}".
    local variants
    variants=$(printf '%s' "$option_value" \
        | grep -oE "#\\{${placeholder}[^}]*\\}" \
        | awk '{print length, $0}' | sort -rn | cut -d' ' -f2- \
        | uniq)

    [ -z "$variants" ] && return

    local new_value="$option_value"
    while IFS= read -r variant; do
        # Extract flags: the part between "#{placeholder" and the closing "}"
        local flags="${variant#"#{${placeholder}"}"
        flags="${flags%\}}"

        local cmd="#($CURRENT_DIR/venv/bin/python $CURRENT_DIR/src/$script$flags)"

        # Escape the variant and command for use as a sed BRE expression (| delimiter).
        # Note: { and } are NOT metacharacters in sed BRE so are excluded here.
        local esc_variant
        esc_variant=$(printf '%s' "$variant" | sed 's/[][\\.*^$|+?()]/\\&/g')
        local esc_cmd
        esc_cmd=$(printf '%s' "$cmd" | sed 's/[&\\|]/\\&/g')

        new_value=$(printf '%s' "$new_value" | sed "s|${esc_variant}|${esc_cmd}|g")
    done <<< "$variants"

    tmux set-option -g "$option" "$new_value"
}

main() {
    check_python_installation
    setup_virtual_env
    update_placeholder "cpu" "status-right" "cpu.py"
    update_placeholder "mem" "status-right" "mem.py"
    update_placeholder "disk" "status-right" "disk.py"
    update_placeholder "battery" "status-right" "battery.py"
    update_placeholder "gpu" "status-right" "gpu.py"
    update_placeholder "cpu" "status-left" "cpu.py"
    update_placeholder "mem" "status-left" "mem.py"
    update_placeholder "disk" "status-left" "disk.py"
    update_placeholder "battery" "status-left" "battery.py"
    update_placeholder "gpu" "status-left" "gpu.py"
}
main
