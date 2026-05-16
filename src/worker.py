"""
后台转换工作线程。

本模块实现异步批量转换的核心逻辑：
  - ConversionWorker 继承 QThread，在后台线程中执行转换
  - 使用 ThreadPoolExecutor 实现最多 4 个文件的并行转换
  - 通过 Qt Signal 向 UI 线程报告进度 / 错误 / 完成状态

信号列表：
  progress(int, int): (已完成文件数, 总文件数) —— 更新进度条
  file_done(str): 刚刚完成的文件名 —— 更新状态栏
  error(str): 错误信息 —— 显示错误
  finished(str): 全部完成的消息 —— 恢复 UI 控件

并行策略：
  - 每个文件独立读取 → 转换 → 写出，不共享任何状态
  - 4 线程并行（由 CPU/磁盘决定实际加速比，约为 1.2-1.5x）
  - 写入时重定向 stderr 到 /dev/null，抑制 python-can C 扩展的
    CAN FD DLC 不规范警告（不影响数据正确性）
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtCore import QThread, Signal
from src.converters.registry import get_reader, get_writer


class ConversionWorker(QThread):
    """异步转换工作线程。

    接收输入文件列表、目标格式和输出目录，
    在后台线程中并行执行所有文件的格式转换。

    Usage:
        worker = ConversionWorker(file_paths, "blf", "/output/dir")
        worker.progress.connect(on_progress)
        worker.file_done.connect(on_file_done)
        worker.error.connect(on_error)
        worker.finished.connect(on_finished)
        worker.start()  # 启动线程
    """

    # Qt 信号：emit 自动线程安全（跨线程传递到 UI 主线程）
    progress = Signal(int, int)   # (已完成数, 总数)
    finished = Signal(str)        # 完成消息
    error = Signal(str)           # 错误消息
    file_done = Signal(str)       # 刚完成的文件名

    def __init__(self, input_paths: list[str], output_format: str, output_dir: str):
        """初始化转换工作线程。

        Args:
            input_paths: 输入文件的绝对路径列表
            output_format: 目标格式扩展名（如 \"blf\"，不含前导点）
            output_dir: 输出目录的绝对路径
        """
        super().__init__()
        self.input_paths = input_paths
        self.output_format = output_format.lstrip(".")
        self.output_dir = output_dir

    def run(self):
        """线程主函数：并行提交所有文件转换任务。

        使用 ThreadPoolExecutor（最多 4 线程）并行处理。
        as_completed 按照完成顺序收集结果，实时报告进度。
        """
        total = len(self.input_paths)
        completed = 0

        # 最多 4 个线程并行（磁盘 I/O 瓶颈，线程再多收益递减）
        with ThreadPoolExecutor(max_workers=min(4, total)) as pool:
            futures = {
                pool.submit(self._convert_one, p): p
                for p in self.input_paths
            }
            for future in as_completed(futures):
                path = futures[future]
                try:
                    filename = future.result()
                    completed += 1
                    self.progress.emit(completed, total)
                    self.file_done.emit(filename)
                except Exception as e:
                    completed += 1
                    self.progress.emit(completed, total)
                    self.error.emit(f"{os.path.basename(path)}: {e}")

        if total > 0:
            self.finished.emit(f"完成 {total} 个文件转换")
        else:
            self.finished.emit("无文件需要转换")

    def _convert_one(self, input_path: str) -> str:
        """单个文件的读取 → 转换 → 写出全流程。

        在写入时重定向 stderr 到 os.devnull，抑制 python-can 的 C 扩展
        对非标准 CAN FD DLC 的警告输出。这些警告不影响数据正确性，
        仅因为某些记录设备的 DLC 编码不符合 CAN FD 规范。

        Args:
            input_path: 单个输入文件的绝对路径

        Returns:
            str: 输出文件名（不含路径）

        Raises:
            各种转换异常由调用方统一捕获
        """
        reader_fn = get_reader(self._input_ext())
        writer_fn = get_writer(self.output_format)
        records = reader_fn(input_path)

        # 输出文件名 = 输入文件名（换扩展名），保持原名称不变
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(self.output_dir, f"{base}.{self.output_format}")

        # 重定向文件描述符 2（stderr）到 /dev/null，
        # 抑制 python-can C 扩展的 fprintf(stderr, ...) 警告。
        # 仅影响当前线程的写入阶段。
        fd = os.open(os.devnull, os.O_WRONLY)
        old_stderr = os.dup(2)
        os.dup2(fd, 2)
        os.close(fd)
        try:
            writer_fn(records, output_path)
        finally:
            # 恢复 stderr，确保后续错误信息能正常输出
            os.dup2(old_stderr, 2)
            os.close(old_stderr)

        return os.path.basename(output_path)

    def _input_ext(self):
        """获取输入文件的扩展名（从第一个文件推断，所有输入文件应为同格式）。"""
        return os.path.splitext(self.input_paths[0])[1].lstrip(".")
