#!/bin/bash
source venv/bin/activate
export QT_QPA_PLATFORM_PLUGIN_PATH=$(find venv -path "*/plugins/platforms" -type d | head -n 1)
python main.py
