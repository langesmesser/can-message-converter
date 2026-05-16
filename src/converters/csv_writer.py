"""
CSV（Comma-Separated Values）导出器。

CSV 是只写格式（用户需求：可导出为 CSV 查看，但 CSV 不能作为输入源回导）。
本模块使用 pandas 将 FrameRecord 列表导出为 UTF-8 编码的 CSV 文件。

CSV 列结构（8 列）：
  Timestamp  时间戳（float，秒）
  Channel    总线通道号（int）
  ID         仲裁 ID（hex 字符串，如 \"0x7FF\"）
  Extended   是否扩展帧（0/1）
  Type       报文类型（\"CAN\" / \"CAN FD\" / \"LIN\"）
  DLC        数据长度码（int，CAN FD 为 9-15）
  Data       数据载荷（十六进制字符串，空格分隔，如 \"01 02 FF AE\"）
  Bus        总线名称（string，空字符串表示未指定）

CSV 文件的用途：方便在 Excel/WPS/Python 中查看和分析报文数据，
不用于格式回导（CSV → BLF/MF4/ASC 不支持）。
"""

import pandas as pd
from src.converters.base import FrameRecord


class CSVWriter:
    """CSV 文件写入器（仅写，不支持读取）。

    每个 FrameRecord 展开为 CSV 的一行 8 列数据。
    数据载荷（bytes）转换为空格分隔的十六进制大写字符串以便人类阅读。

    Usage:
        CSVWriter.to_file(records, "/path/to/output.csv")
    """

    @staticmethod
    def to_file(records: list[FrameRecord], path: str) -> None:
        """将 FrameRecord 列表导出为 CSV 文件。

        内部逐条转换为字典列表，再由 pandas.DataFrame.to_csv 写出。
        编码为 UTF-8，不含行索引列。

        Args:
            records: 待导出的帧记录列表（非空）
            path: 输出 CSV 文件的绝对路径（建议以 .csv 结尾）

        Raises:
            ValueError: records 为空时抛出
        """
        if not records:
            raise ValueError("No records to write")

        rows = []
        for r in records:
            # 将 bytes 数据转换为空格分隔的大写十六进制字符串
            # 例如 b\"\\x01\\xFF\\xAE\" → \"01 FF AE\"
            hex_data = " ".join(f"{b:02X}" for b in r.data)
            rows.append({
                "Timestamp": r.timestamp,
                "Channel": r.channel,
                "ID": hex(r.arbitration_id),
                "Extended": int(r.is_extended),
                # 类型按优先级判定：CAN FD > LIN > CAN
                "Type": "CAN FD" if r.is_fd else ("LIN" if r.is_lin else "CAN"),
                "DLC": r.dlc,
                "Data": hex_data,
                "Bus": r.bus,
            })

        # 使用 pandas 写出 CSV，index=False 避免额外的行号列
        df = pd.DataFrame(rows)
        df.to_csv(path, index=False)
