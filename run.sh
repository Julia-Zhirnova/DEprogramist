#!/bin/bash
source venv/bin/activate
QT_PLUGINS_DIR=$(python3 -c "import os, PyQt5; print(os.path.join(os.path.dirname(PyQt5.__file__), 'Qt5', 'plugins'))")
export QT_QPA_PLATFORM_PLUGIN_PATH="$QT_PLUGINS_DIR/platforms"
export QT_PLUGIN_PATH="$QT_PLUGINS_DIR"

echo "🔌 Путь к платформам: $QT_QPA_PLATFORM_PLUGIN_PATH"
python3 -c "from PyQt5.QtGui import QImageReader; print('🖼 Поддерживаемые форматы:', [f.data().decode() for f in QImageReader.supportedImageFormats()])"

python main.py
