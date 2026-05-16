"""
主窗口 UI —— CAN 报文格式转换工具，Notion 编辑风格。

  ┌─────────────────────────────────────┐
  │  Header   CAN 报文格式转换工具      │
  │           [Notion ▼]      ☽        │
  ├─────────────────────────────────────┤
  │  ┌ 输入文件 ─────────────────────┐  │
  │  │ [未选择文件          ][浏览] │  │
  │  └──────────────────────────────┘  │
  │  ┌ 输出格式 ─────────────────────┐  │
  │  │ [▼ .blf           ]          │  │
  │  │ 输出目录                      │  │
  │  │ [未选择目录          ][浏览] │  │
  │  └──────────────────────────────┘  │
  │  ┌ 转换 ─────────────────────────┐  │
  │  │ [  转换  ] [错误报文一键转换] │  │
  │  │ ████████████░░░░░            │  │
  │  │          就绪                  │  │
  │  └──────────────────────────────┘  │
  └─────────────────────────────────────┘

  7 套配色 × 深/浅 = 14 种外观。Notion 主题有独立样式 token
  （8px 按钮圆角、500 字重、4px 进度条），其他 6 套共享统一样式。
"""

import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QProgressBar, QFileDialog, QFrame,
)
from PySide6.QtCore import Qt
from src.converters.registry import get_output_formats
from src.worker import ConversionWorker
from src.ui.themes import FAMILY_NAMES, build_qss


VERSION = "V1.4.0"


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"CAN 报文格式转换工具 {VERSION}")
        self.setMinimumSize(520, 440)
        self.resize(580, 520)
        self._selected_files = []
        self._worker = None
        self._dark_mode = True
        self._theme_family = "Notion"
        self._setup_ui()
        self._apply_theme()

    # ── UI 构建 ──────────────────────────

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──
        header = QFrame(objectName="header")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 10, 16, 10)
        hl.addWidget(QLabel("CAN 报文格式转换工具", objectName="title"))
        hl.addStretch()

        self.theme_cycle_btn = QPushButton("", objectName="theme_cycle_btn")
        self.theme_cycle_btn.setToolTip("循环切换配色方案 (共 8 套)")
        self.theme_cycle_btn.setCursor(Qt.PointingHandCursor)
        self.theme_cycle_btn.clicked.connect(self._cycle_theme)
        hl.addWidget(self.theme_cycle_btn)

        self.theme_btn = QPushButton("☽", objectName="theme_btn")
        self.theme_btn.setFixedSize(38, 30)
        self.theme_btn.setToolTip("切换深色 / 浅色模式")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self._toggle_theme)
        hl.addWidget(self.theme_btn)
        root.addWidget(header)

        # ── Body ──
        body = QWidget(objectName="body")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(20, 16, 20, 16)
        bl.setSpacing(12)

        # ── Card: 输入文件 ──
        card1 = QFrame(objectName="card")
        c1 = QVBoxLayout(card1)
        c1.setContentsMargins(14, 12, 14, 12)
        c1.setSpacing(8)
        c1.addWidget(QLabel("输入文件", objectName="section_label"))
        fr = QHBoxLayout()
        fr.setSpacing(8)
        self.input_field = QLineEdit(readOnly=True)
        self.input_field.setPlaceholderText("选择 .blf / .mf4 / .asc / .txt 文件")
        fr.addWidget(self.input_field, 1)
        b1 = QPushButton("浏览", objectName="browse_btn")
        b1.clicked.connect(self._browse_input)
        fr.addWidget(b1)
        c1.addLayout(fr)
        bl.addWidget(card1)

        # ── Card: 输出配置 ──
        card2 = QFrame(objectName="card")
        c2 = QVBoxLayout(card2)
        c2.setContentsMargins(14, 12, 14, 12)
        c2.setSpacing(8)
        c2.addWidget(QLabel("输出格式", objectName="section_label"))
        self.format_combo = QComboBox()
        self.format_combo.addItems([".blf", ".mf4", ".asc", ".csv"])
        c2.addWidget(self.format_combo)
        c2.addWidget(QLabel("输出目录", objectName="section_label"))
        dr = QHBoxLayout()
        dr.setSpacing(8)
        self.output_field = QLineEdit(readOnly=True)
        self.output_field.setPlaceholderText("选择输出目录")
        dr.addWidget(self.output_field, 1)
        b2 = QPushButton("浏览", objectName="browse_btn")
        b2.clicked.connect(self._browse_output_dir)
        dr.addWidget(b2)
        c2.addLayout(dr)
        bl.addWidget(card2)

        # ── Card: 操作 + 进度 ──
        card3 = QFrame(objectName="card")
        c3 = QVBoxLayout(card3)
        c3.setContentsMargins(14, 12, 14, 12)
        c3.setSpacing(8)
        ab = QHBoxLayout()
        ab.setSpacing(10)
        self.convert_btn = QPushButton("转换", objectName="convert_btn")
        self.convert_btn.setCursor(Qt.PointingHandCursor)
        self.convert_btn.clicked.connect(self._convert)
        ab.addWidget(self.convert_btn, 1)
        self.xlsx_btn = QPushButton("错误报文一键转换", objectName="xlsx_btn")
        self.xlsx_btn.setEnabled(False)
        self.xlsx_btn.setCursor(Qt.PointingHandCursor)
        self.xlsx_btn.clicked.connect(self._convert_to_xlsx)
        ab.addWidget(self.xlsx_btn, 1)
        c3.addLayout(ab)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        c3.addWidget(self.progress_bar)
        self.status_label = QLabel("就绪", objectName="status")
        self.status_label.setAlignment(Qt.AlignCenter)
        c3.addWidget(self.status_label)
        bl.addWidget(card3)

        bl.addStretch()
        root.addWidget(body)

    # ── 主题 ──────────────────────────────

    def _apply_theme(self):
        qss = build_qss(self._theme_family, self._dark_mode)
        self.setStyleSheet(qss)
        self.theme_cycle_btn.setText(self._theme_family)
        self.theme_btn.setText("☽" if self._dark_mode else "☀")

    def _toggle_theme(self):
        self._dark_mode = not self._dark_mode
        self._apply_theme()

    def _cycle_theme(self):
        idx = FAMILY_NAMES.index(self._theme_family)
        self._theme_family = FAMILY_NAMES[(idx + 1) % len(FAMILY_NAMES)]
        self._apply_theme()

    # ── 文件选择 ──────────────────────────

    def _browse_input(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择输入文件", "",
            "总线报文文件 (*.blf *.asc *.mf4 *.txt);;所有文件 (*)"
        )
        if files:
            self._selected_files = files
            self.input_field.setText(files[0] if len(files) == 1 else f"已选择 {len(files)} 个文件")
            input_ext = os.path.splitext(files[0])[1].lstrip(".")
            self._update_format_combo(input_ext)

    def _browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.output_field.setText(directory)

    def _update_format_combo(self, input_ext):
        self.format_combo.clear()
        formats = get_output_formats(input_ext)
        self.format_combo.addItems([f".{f}" for f in formats])
        self.xlsx_btn.setEnabled(input_ext == "txt")

    # ── 转换 ──────────────────────────────

    def _convert(self):
        if not self._selected_files:
            self.status_label.setText("请先选择输入文件")
            return
        if not self.output_field.text():
            self.status_label.setText("请先选择输出目录")
            return
        self._start_conversion(self._selected_files)

    def _convert_to_xlsx(self):
        if not self._selected_files:
            self.status_label.setText("请先选择输入文件")
            return
        if not self.output_field.text():
            self.status_label.setText("请先选择输出目录")
            return
        self._start_conversion(self._selected_files, "xlsx")

    def _start_conversion(self, file_paths, out_fmt=None):
        out_fmt = out_fmt if out_fmt else self.format_combo.currentText().lstrip(".")
        out_dir = self.output_field.text()
        self._set_controls_enabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"转换中... (0/{len(file_paths)})")
        self._worker = ConversionWorker(file_paths, out_fmt, out_dir)
        self._worker.progress.connect(self._on_progress)
        self._worker.file_done.connect(self._on_file_done)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _set_controls_enabled(self, enabled):
        self.convert_btn.setEnabled(enabled)
        self.xlsx_btn.setEnabled(enabled)

    # ── 信号 ──────────────────────────────

    def _on_progress(self, completed, total):
        self.progress_bar.setValue(int(completed / total * 100))
        self.status_label.setText(f"转换中... ({completed}/{total})")

    def _on_file_done(self, filename):
        pass

    def _on_error(self, message):
        current = self.status_label.text()
        self.status_label.setText(f"{current} — 错误: {message}")

    def _on_finished(self, message):
        self.status_label.setText(message)
        self.convert_btn.setEnabled(True)
        if self._selected_files:
            input_ext = os.path.splitext(self._selected_files[0])[1].lstrip(".")
            self.xlsx_btn.setEnabled(input_ext == "txt")
        self._worker = None
