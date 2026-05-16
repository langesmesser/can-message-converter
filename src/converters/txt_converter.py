"""
TXT（文本日志）转换器 —— 仅读取，不写入。

支持解析空格/制表符分隔的 CAN 报文文本日志（格式 A）：
    <timestamp>  [channel]  <id>  [data_bytes...]

特性：
  - 自动检测可选 channel 列（第 2 列为 0-15 的整数时识别为通道号）
  - ID 支持十六进制，可带或不带 0x 前缀
  - 自动判定扩展帧（ID > 0x7FF）和 CAN FD（数据 > 8 字节）
  - 跳过注释行/标题行（首列非数值的行）
  - CAN FD DLC 自动从数据长度映射为标准 DLC 编码

Usage:
    records = TXTReader.from_file("/path/to/can_log.txt")
"""

from src.converters.base import FrameRecord


# CAN FD 数据长度 → DLC 编码映射（ISO 11898-1:2015）
_DATA_LEN_TO_DLC = {
    0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8,
    12: 9, 16: 10, 20: 11, 24: 12, 32: 13, 48: 14, 64: 15,
}


class TXTReader:
    """TXT 文件读取器。

    解析空格/制表符分隔的 CAN 报文文本日志，将每条报文映射到 FrameRecord。

    Usage:
        records = TXTReader.from_file("/path/to/can_log.txt")
    """

    @staticmethod
    def from_file(path: str) -> list[FrameRecord]:
        """读取 TXT 文件，返回 FrameRecord 列表。

        每行格式：timestamp [channel] id [byte1 byte2 ...]
        - channel 列为可选，自动检测（值为 0-15 的整数时识别为通道号）
        - 首列非数值的行视为注释/标题，自动跳过

        Args:
            path: TXT 文件的绝对路径

        Returns:
            list[FrameRecord]: 按文件顺序排列的帧记录列表

        Raises:
            ValueError: TXT 文件中无有效报文记录
        """
        records = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) < 2:
                    continue

                # 首列必须是有效浮点数（时间戳），否则视为标题/注释行跳过
                try:
                    timestamp = float(parts[0])
                except ValueError:
                    continue

                # 自动检测 channel 列：
                #   如果 parts[1] 是 0-15 的整数 → 视为 channel，ID 在 parts[2]
                #   否则 → parts[1] 就是 ID
                offset = 0
                channel = 0
                try:
                    candidate = int(parts[1])
                    if 0 <= candidate <= 15 and "." not in parts[1]:
                        channel = candidate
                        offset = 1
                except ValueError:
                    pass

                # 解析 CAN ID（十六进制，可带 0x 前缀）
                id_str = parts[1 + offset].lower().replace("0x", "")
                arbitration_id = int(id_str, 16)

                is_extended = arbitration_id > 0x7FF

                # 剩余字段为数据字节（十六进制）
                data_bytes = []
                raw_data_parts = parts[2 + offset:]
                for byte_str in raw_data_parts:
                    # 如果该字段本身就是完整的 hex 数据串（如 "55005500400c0009"），
                    # 按每 2 个字符拆分为独立字节
                    if len(byte_str) > 2 and len(byte_str) % 2 == 0:
                        try:
                            for i in range(0, len(byte_str), 2):
                                data_bytes.append(int(byte_str[i:i+2], 16))
                        except ValueError:
                            break
                    else:
                        try:
                            data_bytes.append(int(byte_str, 16))
                        except ValueError:
                            break

                data = bytes(data_bytes)
                data_len = len(data_bytes)
                is_fd = data_len > 8
                dlc = _DATA_LEN_TO_DLC.get(data_len, data_len)

                records.append(FrameRecord(
                    timestamp=timestamp,
                    arbitration_id=arbitration_id,
                    channel=channel,
                    is_extended=is_extended,
                    is_fd=is_fd,
                    dlc=dlc,
                    data=data,
                ))

        if not records:
            raise ValueError("No valid CAN messages found in TXT file")
        return records
