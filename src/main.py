"""
CAN 报文格式自由转换工具 —— 应用程序入口。

本脚本是 PySide6 GUI 桌面应用的主入口，负责：
  1. 初始化 QApplication 和主窗口
  2. 修复项目根目录到 sys.path（兼容直接运行和 PyInstaller 打包）
  3. 进入 Qt 事件循环

直接运行：
    python src/main.py

PyInstaller 打包后：
    CAN-Converter.exe（双击运行，无需 Python 环境）
"""

import sys
import os

# 确保项目根目录在 sys.path 中，使 `from src.xxx import yyy` 能正常工作。
# PyInstaller 打包后 sys.path 已包含，此操作无副作用。
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    """应用程序主函数：创建 Qt 应用 → 显示主窗口 → 进入事件循环。"""
    app = QApplication(sys.argv)
    app.setApplicationName("CAN-Converter")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
