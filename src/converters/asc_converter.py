"""
ASC（ASCII Logging Format）转换器。

ASC 是 Vector 公司的文本格式 CAN/LIN 日志，可读性好，广泛用于调试和
数据分析。本模块基于 python-can 库实现 ASC 文件的读写。

ASC 格式特性：
  - 文本格式（纯 ASCII），可用任意文本编辑器打开
  - 时间戳精度：毫秒级（小数点后 6 位，float 秒表示时为微秒级）
  - 文件体积较大（每条约 50-150 字符），约为 BLF 的 5-10 倍
  - 支持 CAN 2.0、CAN FD、LIN 报文

读写流程：
  ASCReader:  ASC 文件 → can.Message → FrameRecord 列表
  ASCWriter:  FrameRecord 列表 → can.Message → ASC 文件
"""

import can
from src.converters.base import FrameRecord


class ASCReader:
    """ASC 文件读取器。

    使用 python-can 的 ASCReader 按行解析 ASC 文本日志，
    将每条报文映射到 FrameRecord。

    Usage:
        records = ASCReader.from_file("/path/to/data.asc")
    """

    @staticmethod
    def from_file(path: str) -> list[FrameRecord]:
        """读取 ASC 文件，返回 FrameRecord 列表。

        ASC 文件按行存储，每行一条报文或元数据。python-can 的 ASCReader
        已封装好解析逻辑，逐条返回 can.Message 对象。

        Args:
            path: ASC 文件的绝对路径（UTF-8 或 ASCII 编码）

        Returns:
            list[FrameRecord]: 按时间顺序排列的帧记录列表

        Raises:
            ValueError: ASC 文件中无有效报文记录
        """
        records = []
        with can.ASCReader(path) as reader:
            for msg in reader:
                records.append(FrameRecord(
                    timestamp=msg.timestamp,
                    arbitration_id=msg.arbitration_id,
                    channel=getattr(msg, "channel", 0),
                    is_extended=msg.is_extended_id,
                    is_lin=getattr(msg, "is_lin_message", False),
                    is_fd=msg.is_fd,
                    dlc=msg.dlc,
                    data=msg.data if msg.data else b"",
                    bus=getattr(msg, "bus", "") or "",
                ))
        if not records:
            raise ValueError("No messages found in ASC file")
        return records


class ASCWriter:
    """ASC 文件写入器。

    将 FrameRecord 列表转换为 can.Message 后写入 ASC 文本文件。

    Usage:
        ASCWriter.to_file(records, "/path/to/output.asc")
    """

    @staticmethod
    def to_file(records: list[FrameRecord], path: str) -> None:
        """将 FrameRecord 列表写入 ASC 文件。

        每个 FrameRecord 构造一个 can.Message 对象，由 ASCWriter 负责
        格式化为 ASC 文本行（时间戳 + 总线 + ID + DLC + 数据）。

        Args:
            records: 待写入的帧记录列表（非空）
            path: 输出 ASC 文件的绝对路径

        Raises:
            ValueError: records 为空时抛出
        """
        if not records:
            raise ValueError("No records to write")
        with can.ASCWriter(path) as writer:
            for r in records:
                msg = can.Message(
                    timestamp=r.timestamp,
                    arbitration_id=r.arbitration_id,
                    is_extended_id=r.is_extended,
                    is_fd=r.is_fd,
                    channel=r.channel,
                    dlc=r.dlc,
                    data=r.data,
                )
                writer.on_message_received(msg)
