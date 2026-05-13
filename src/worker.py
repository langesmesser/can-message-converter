import os
from PySide6.QtCore import QThread, Signal
from src.converters.registry import get_reader, get_writer


class ConversionWorker(QThread):
    progress = Signal(int)        # percent 0-100
    finished = Signal(str)        # success message
    error = Signal(str)           # error message
    file_done = Signal(str)       # filename just completed

    def __init__(self, input_paths: list[str], output_format: str, output_dir: str):
        super().__init__()
        self.input_paths = input_paths
        self.output_format = output_format.lstrip(".")
        self.output_dir = output_dir

    def run(self):
        reader_fn = get_reader(self._input_ext())
        writer_fn = get_writer(self.output_format)
        total = len(self.input_paths)

        for i, input_path in enumerate(self.input_paths):
            try:
                records = reader_fn(input_path)
                base = os.path.splitext(os.path.basename(input_path))[0]
                output_path = self._unique_path(base)
                writer_fn(records, output_path)
                self.file_done.emit(os.path.basename(output_path))
                self.progress.emit(int((i + 1) / total * 100))
            except Exception as e:
                self.error.emit(f"{os.path.basename(input_path)}: {e}")

        if total > 0:
            self.finished.emit(f"完成 {total} 个文件转换")
        else:
            self.finished.emit("无文件需要转换")

    def _input_ext(self):
        return os.path.splitext(self.input_paths[0])[1].lstrip(".")

    def _unique_path(self, base_name: str) -> str:
        ext = self.output_format
        candidate = os.path.join(self.output_dir, f"{base_name}.{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter = 1
        while True:
            candidate = os.path.join(self.output_dir, f"{base_name}_{counter}.{ext}")
            if not os.path.exists(candidate):
                return candidate
            counter += 1
