"""
BLF（Binary Logging Format）转换器。

BLF 是 Vector 公司的二进制 CAN/LIN 日志格式，广泛应用于汽车电子领域。
本模块基于 python-can 库实现 BLF 文件的读写，将原始 Message 对象
映射到中间表示 FrameRecord。

BLF 格式特性：
  - 二进制存储，体积小、解析快
  - 时间戳精度：64 位整型纳秒（python-can 以 float 秒表示）
  - 原生支持 CAN 2.0、CAN FD、LIN 多种帧类型
  - 单文件可包含多路总线数据（通过 channel 字段区分）

读写流程：
  BLFReader:  BLF 文件 → can.Message → FrameRecord 列表
  BLFWriter:  FrameRecord 列表 → can.Message → BLF 文件
"""

import can
from src.converters.base import FrameRecord


class BLFReader:
    """BLF 文件读取器。

    使用 python-can 的 BLFReader 逐条读取 Message 对象，
    将所有字段映射到 FrameRecord 冻结数据类中。

    Usage:
        records = BLFReader.from_file("/path/to/data.blf")
    """

    @staticmethod
    def from_file(path: str) -> list[FrameRecord]:
        """读取 BLF 文件，返回 FrameRecord 列表。

        遍历 BLF 文件中的每条 CAN/LIN Message，提取时间戳、仲裁 ID、
        通道号、扩展帧标志、CAN FD 标志、DLC、数据载荷和总线名称。

        Args:
            path: BLF 文件的绝对路径

        Returns:
            list[FrameRecord]: 按时间顺序排列的帧记录列表

        Raises:
            ValueError: BLF 文件中未读取到任何报文（文件为空或格式错误）
        """
        records = []
        with can.BLFReader(path) as reader:
            for msg in reader:
                # can.Message 的 channel/bus/is_lin_message 属性并非总是存在，
                # 使用 getattr 安全读取，缺失时回退到默认值
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
            raise ValueError("No messages found in BLF file")
        return records


class BLFWriter:
    """BLF 文件写入器。

    将 FrameRecord 列表逐条转换为 can.Message 对象，
    通过 python-can 的 BLFWriter 写入 .blf 二进制文件。

    Usage:
        BLFWriter.to_file(records, "/path/to/output.blf")
    """

    @staticmethod
    def to_file(records: list[FrameRecord], path: str) -> None:
        """将 FrameRecord 列表写入 BLF 文件。

        每个 FrameRecord 构造一个 can.Message 对象，包含时间戳、
        仲裁 ID、扩展帧标志、CAN FD 标志、通道号、DLC 和数据载荷。
        注意：python-can 4.x 的 BLFWriter 不支持 is_lin_message 和 bus 参数。

        Args:
            records: 待写入的帧记录列表（非空，按时间顺序排列）
            path: 输出 BLF 文件的绝对路径

        Raises:
            ValueError: records 为空时抛出
        """
        if not records:
            raise ValueError("No records to write")
        with can.BLFWriter(path) as writer:
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
