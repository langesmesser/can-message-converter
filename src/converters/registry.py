"""
读写器注册表：统一管理所有支持格式的 Reader/Writer 映射。

新增格式支持时，只需在此文件中注册 Reader 和 Writer 即可，
无需修改任何其他代码。格式扩展名统一小写处理，消除大小写歧义。

====================  支持的转换路径  ======================

输入（4 种）      输出（4 种）           说明
---------------------------------------------------------
  .blf          .mf4 / .asc / .csv       BLF 可导入回系统
  .mf4          .blf / .asc / .csv       MF4 可导入回系统
  .asc          .blf / .mf4 / .csv       ASC 可导入回系统
  .txt          .asc                      TXT 文本日志（仅转 ASC）
  .csv          不支持作为输入           CSV 为只写导出格式
"""

from src.converters.blf_converter import BLFReader, BLFWriter
from src.converters.asc_converter import ASCReader, ASCWriter
from src.converters.mf4_converter import MF4Reader, MF4Writer
from src.converters.csv_writer import CSVWriter
from src.converters.txt_converter import TXTReader
from src.converters.xlsx_writer import XLSXWriter

# 读取器映射：扩展名 → 静态方法（函数指针）
READERS = {
    "blf": BLFReader.from_file,
    "asc": ASCReader.from_file,
    "mf4": MF4Reader.from_file,
    "txt": TXTReader.from_file,
}

# 写入器映射：扩展名 → 静态方法（函数指针）
# 注意：TXT 只有 Reader，不能作为输出目标
WRITERS = {
    "blf": BLFWriter.to_file,
    "asc": ASCWriter.to_file,
    "mf4": MF4Writer.to_file,
    "csv": CSVWriter.to_file,
    "xlsx": XLSXWriter.to_file,
}

# 系统支持的所有格式扩展名集合（用于验证和过滤）
ALL_FORMATS = {"blf", "mf4", "asc", "csv", "txt"}


def get_reader(extension: str):
    """根据输入文件扩展名获取对应的读取函数。

    Args:
        extension: 文件扩展名字符串，可带或不带前导点（如 "blf" 或 ".blf"）

    Returns:
        Callable[[str], list[FrameRecord]]: 接受文件路径、返回 FrameRecord 列表的函数

    Raises:
        ValueError: 扩展名不在 READERS 中（如传入 "csv" 或未知格式）
    """
    ext = extension.lower().lstrip(".")
    if ext not in READERS:
        raise ValueError(f"Unsupported input format: .{ext}")
    return READERS[ext]


def get_writer(extension: str):
    """根据输出文件扩展名获取对应的写入函数。

    Args:
        extension: 文件扩展名字符串，可带或不带前导点

    Returns:
        Callable[[list[FrameRecord], str], None]: 接受记录列表和输出路径的函数

    Raises:
        ValueError: 扩展名不在 WRITERS 中（如传入未知格式）
    """
    ext = extension.lower().lstrip(".")
    if ext not in WRITERS:
        raise ValueError(f"Unsupported output format: .{ext}")
    return WRITERS[ext]


# 部分输入格式限制可转换的输出格式（如 TXT 仅允许转为 ASC）
_RESTRICTED_OUTPUT = {
    "txt": {"asc"},
}


def get_output_formats(input_extension: str) -> list[str]:
    """根据输入格式，返回可用的输出格式列表（排除与输入相同的格式）。

    例如输入 "blf" 时返回 ["asc", "csv", "mf4"]，
    排除 "blf" 以避免无意义的同格式转换。
    TXT 格式仅允许输出 ASC（用户需求：在 CANoe 中阅读）。

    Args:
        input_extension: 输入文件的扩展名

    Returns:
        list[str]: 排序后的输出格式扩展名列表（不含前导点）
    """
    ext = input_extension.lower().lstrip(".")
    candidates = _RESTRICTED_OUTPUT.get(ext, ALL_FORMATS)
    return sorted(f for f in candidates if f != ext)


def supports_extension(extension: str) -> bool:
    """检查给定的扩展名是否为系统支持的格式（读或写均可）。

    Args:
        extension: 扩展名字符串

    Returns:
        bool: True 表示该格式可读或可写
    """
    ext = extension.lower().lstrip(".")
    return ext in ALL_FORMATS
