#!/bin/bash

# Output file
LOGFILE="run_output.txt"

# Clear the log file at start
> "$LOGFILE"

# -----------------------------
# Read Python path from file
# -----------------------------
PYTHON_PATH_FILE="python_path.txt"

if [ ! -f "$PYTHON_PATH_FILE" ]; then
    echo "ERROR: $PYTHON_PATH_FILE not found!" >> "$LOGFILE"
    exit 1
fi

# Read the path (first line of file)
PYTHON_PATH=$(head -n 1 "$PYTHON_PATH_FILE")

# Prepend Python folder to PATH
export PATH="$PYTHON_PATH:$PATH"

# Optional: alias python3 to python
alias python3='python'

# Verify Python version (for logging)
python --version >> "$LOGFILE" 2>&1

# -----------------------------
# Run caption scripts
# -----------------------------
#python caption_nograph.py ../output/action_caption_gemini-2.5-pro-preview-06-05_2024.json >> "$LOGFILE" 2>&1
#python caption_nograph.py ../output/action_caption_gemini-2.5-pro-preview-06-05_2025.json >> "$LOGFILE" 2>&1
#python caption_nograph.py ../output/action_caption_Qwen2.5-VL-3B-BARD_only2024.json       >> "$LOGFILE" 2>&1
#python caption_nograph.py ../output/action_caption_Qwen2.5-VL-3B-BARD_only2025.json       >> "$LOGFILE" 2>&1
#python caption_nograph.py ../output/action_caption_Qwen2.5-VL-3B-Instruct2024.json        >> "$LOGFILE" 2>&1
python caption_nograph.py ../output/action_caption_Qwen2.5-VL-3B-Instruct2025.json         >> "$LOGFILE" 2>&1
python caption_nograph.py ../output/action_caption_Qwen3-VL-4B-Instruct_prompt_2025.json   >> "$LOGFILE" 2>&1
#python caption_nograph.py ../output/action_caption_Qwen2.5-VL-3B-Instruct_ft52024.json    >> "$LOGFILE" 2>&1
#python caption_nograph.py ../output/action_caption_Qwen2.5-VL-3B-Instruct_ft52025.json    >> "$LOGFILE" 2>&1
#python caption_nograph.py ../output/action_caption_Qwen2.5-VL-7B-Instruct2024.json        >> "$LOGFILE" 2>&1
#python caption_nograph.py ../output/action_caption_Qwen2.5-VL-7B-Instruct2025.json        >> "$LOGFILE" 2>&1