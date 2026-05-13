import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QProgressBar, QFileDialog, QFrame,
)
from PySide6.QtCore import Qt
from src.converters.registry import get_output_formats
from src.worker import ConversionWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAN 报文格式转换工具")
        self.setFixedSize(440, 380)
        self._selected_files = []
        self._worker = None
        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame(objectName="header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 10, 16, 10)
        title = QLabel("CAN 报文格式转换工具", objectName="title")
        header_layout.addWidget(title)
        layout.addWidget(header)

        # Body
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 16, 20, 16)
        body_layout.setSpacing(12)

        # Input file
        body_layout.addWidget(QLabel("输入文件 (.blf / .mf4 / .asc)"))
        file_row = QHBoxLayout()
        self.input_field = QLineEdit(readOnly=True)
        self.input_field.setPlaceholderText("未选择文件")
        file_row.addWidget(self.input_field, 1)
        browse_btn = QPushButton("浏览", objectName="browse_btn")
        browse_btn.clicked.connect(self._browse_input)
        file_row.addWidget(browse_btn)
        body_layout.addLayout(file_row)

        # Output format
        body_layout.addWidget(QLabel("输出格式"))
        self.format_combo = QComboBox()
        self.format_combo.addItems([".blf", ".mf4", ".asc", ".csv"])
        body_layout.addWidget(self.format_combo)

        # Output directory
        body_layout.addWidget(QLabel("输出目录"))
        dir_row = QHBoxLayout()
        self.output_field = QLineEdit(readOnly=True)
        self.output_field.setPlaceholderText("未选择目录")
        dir_row.addWidget(self.output_field, 1)
        dir_browse_btn = QPushButton("浏览", objectName="browse_btn")
        dir_browse_btn.clicked.connect(self._browse_output_dir)
        dir_row.addWidget(dir_browse_btn)
        body_layout.addLayout(dir_row)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self.single_btn = QPushButton("单文件转换", objectName="single_btn")
        self.single_btn.clicked.connect(self._convert_single)
        btn_row.addWidget(self.single_btn, 1)
        self.batch_btn = QPushButton("批量转换", objectName="batch_btn")
        self.batch_btn.clicked.connect(self._convert_batch)
        btn_row.addWidget(self.batch_btn, 1)
        body_layout.addLayout(btn_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        body_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("就绪", objectName="status")
        self.status_label.setAlignment(Qt.AlignCenter)
        body_layout.addWidget(self.status_label)

        body_layout.addStretch()
        layout.addWidget(body)

    def _apply_theme(self):
        qss_path = os.path.join(os.path.dirname(__file__), "theme.qss")
        with open(qss_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def _browse_input(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择输入文件", "",
            "总线报文文件 (*.blf *.asc *.mf4);;所有文件 (*)"
        )
        if files:
            self._selected_files = files
            if len(files) == 1:
                self.input_field.setText(files[0])
            else:
                self.input_field.setText(f"已选择 {len(files)} 个文件")
            input_ext = os.path.splitext(files[0])[1].lstrip(".")
            self._update_format_combo(input_ext)

    def _browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.output_field.setText(directory)

    def _update_format_combo(self, input_ext):
        self.format_combo.clear()
        formats = get_output_formats(input_ext)
        display = [f".{f}" for f in formats]
        self.format_combo.addItems(display)

    def _convert_single(self):
        if not self._selected_files:
            self.status_label.setText("请先选择输入文件")
            return
        if not self.output_field.text():
            self.status_label.setText("请先选择输出目录")
            return
        self._start_conversion([self._selected_files[0]])

    def _convert_batch(self):
        if not self._selected_files:
            self.status_label.setText("请先选择输入文件")
            return
        if not self.output_field.text():
            self.status_label.setText("请先选择输出目录")
            return
        self._start_conversion(self._selected_files)

    def _start_conversion(self, file_paths):
        out_fmt = self.format_combo.currentText().lstrip(".")
        out_dir = self.output_field.text()

        self._set_controls_enabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("转换中...")

        self._worker = ConversionWorker(file_paths, out_fmt, out_dir)
        self._worker.progress.connect(self._on_progress)
        self._worker.file_done.connect(self._on_file_done)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _set_controls_enabled(self, enabled):
        self.single_btn.setEnabled(enabled)
        self.batch_btn.setEnabled(enabled)

    def _on_progress(self, value):
        self.progress_bar.setValue(value)

    def _on_file_done(self, filename):
        self.status_label.setText(f"已完成: {filename}")

    def _on_error(self, message):
        self.status_label.setText(f"错误: {message}")

    def _on_finished(self, message):
        self.status_label.setText(message)
        self._set_controls_enabled(True)
        self._worker = None
