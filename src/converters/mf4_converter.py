"""
MF4（MDF4 Measurement Data Format v4）转换器。

MF4 是 ASAM 标准的测量数据文件格式，广泛应用于汽车标定和总线数据记录。
本模块基于 asammdf 库实现 MF4 文件的读写。

MF4 格式特性：
  - 二进制 HDF5 容器，适合大规模数据存储
  - 时间戳精度：float64 双精度浮点（纳秒级）
  - 使用复合信号（composite channels）存储 CAN 报文，而非简单数组
  - 支持多数据组（groups），每个组可包含多个通道（channels）

实际 MF4 文件的 CAN 报文存在两种常见布局：
  策略1（真实采集文件）：CAN_DataFrame 复合结构体，包含 ID/BusChannel/IDE/DLC/
                       DataLength/DataBytes 等子字段
  策略2（本工具写出）：扁平独立通道，CAN_ID / CAN_DLC / CAN_Channel / CAN_Flags
                     / CAN_DataByte0~7，每个通道为独立信号

读写流程：
  MF4Reader:  检测数据结构 → 按对应策略解析 → FrameRecord 列表
  MF4Writer:  FrameRecord 列表 → 扁平独立通道 → MF4 文件
"""

import numpy as np
from asammdf import MDF, Signal
from src.converters.base import FrameRecord


class MF4Reader:
    """MF4/MDF 文件读取器。

    支持两种常见的 CAN 报文数据布局，按优先级自动检测：
      1. CAN_DataFrame 复合结构体（高优先级，真实采集设备常用）
      2. 扁平独立通道（本工具 MF4Writer 输出的格式）

    Usage:
        records = MF4Reader.from_file("/path/to/data.mf4")
    """

    @staticmethod
    def from_file(path: str) -> list[FrameRecord]:
        """读取 MF4 文件，自动检测数据结构并解析 CAN/LIN 报文。

        先尝试策略1（CAN_DataFrame 复合通道），如果找到有效数据则直接返回；
        否则回退到策略2（扁平独立通道）。两种策略均失败时抛出 ValueError。

        Args:
            path: MF4 文件的绝对路径

        Returns:
            list[FrameRecord]: 按时间顺序排列的帧记录列表

        Raises:
            ValueError: 文件中未找到任何 CAN/LIN 报文数据
        """
        mdf = MDF(path)
        records = []
        try:
            # ============================================================
            # 策略1：CAN_DataFrame 复合结构体（真实采集设备输出的 MF4）
            # ============================================================
            # 真实 MF4 文件中，CAN 报文通常存储为单个复合通道 CAN_DataFrame，
            # 其 samples 是结构化 numpy 数组，包含 ID/BusChannel/IDE/DLC/
            # DataLength/DataBytes 等命名子字段。
            for gi in range(len(mdf.groups)):
                try:
                    t_sig = mdf.get("t", group=gi, index=0)
                    df_sig = mdf.get("CAN_DataFrame", group=gi, index=1)
                except Exception:
                    continue

                if t_sig is None or df_sig is None:
                    continue

                samples = df_sig.samples
                timestamps = t_sig.samples
                n = min(len(timestamps), len(samples))

                # 从结构化数组的命名字段中提取各列数据
                ids = samples["CAN_DataFrame.ID"]
                bus_channels = samples["CAN_DataFrame.BusChannel"]
                ides = samples["CAN_DataFrame.IDE"]
                dlcs = samples["CAN_DataFrame.DLC"]
                data_lengths = samples["CAN_DataFrame.DataLength"]
                data_bytes_array = samples["CAN_DataFrame.DataBytes"]

                for i in range(n):
                    dlc = int(dlcs[i])
                    data_len = int(data_lengths[i])
                    # 按 DataLength 截取有效数据字节（DataBytes 数组可能包含填充零）
                    raw = bytes(data_bytes_array[i][:data_len])

                    records.append(FrameRecord(
                        timestamp=float(timestamps[i]),
                        arbitration_id=int(ids[i]),
                        channel=int(bus_channels[i]),
                        is_extended=bool(ides[i]),
                        # CAN FD 判定：DLC > 8 即视为 CAN FD 帧
                        is_fd=bool(dlc > 8),
                        dlc=dlc,
                        data=raw,
                    ))

            if records:
                return records

            # ============================================================
            # 策略2：扁平独立通道（本工具 MF4Writer 输出的格式）
            # ============================================================
            # 本工具写出的 MF4 使用扁平布局：每条 CAN 帧的属性拆分为
            # 13 个独立 Signal（t + CAN_ID + CAN_Channel + CAN_Flags +
            # CAN_DLC + CAN_DataByte0~7），按时间戳对齐。
            sigs = {}
            for sig in mdf.iter_channels():
                sigs[sig.name] = sig

            if "CAN_ID" in sigs:
                can_id_sig = sigs["CAN_ID"]
                n = len(can_id_sig.samples)
                timestamps = can_id_sig.timestamps
                can_dlc_sig = sigs.get("CAN_DLC")
                can_chan_sig = sigs.get("CAN_Channel")
                can_flags_sig = sigs.get("CAN_Flags")

                # 收集 CAN_DataByte0 到 CAN_DataByte7 信号
                data_byte_sigs = {}
                for bi in range(8):
                    name = f"CAN_DataByte{bi}"
                    if name in sigs:
                        data_byte_sigs[bi] = sigs[name]

                for i in range(n):
                    ts = float(timestamps[i])
                    aid = int(can_id_sig.samples[i])
                    # 可选字段使用默认值，兼容只有部分通道的 MF4 文件
                    dlc = int(can_dlc_sig.samples[i]) if can_dlc_sig else 8
                    channel = int(can_chan_sig.samples[i]) if can_chan_sig else 0
                    flags = int(can_flags_sig.samples[i]) if can_flags_sig else 0
                    # CAN_Flags 位定义：bit0 = is_extended, bit1 = is_lin
                    is_extended = bool(flags & 1)
                    is_lin = bool(flags & 2)

                    # 从独立字节通道重建数据载荷
                    data = bytearray()
                    for bi in range(8):
                        if bi in data_byte_sigs and i < len(data_byte_sigs[bi].samples):
                            data.append(int(data_byte_sigs[bi].samples[i]))
                        else:
                            break
                    data_bytes = bytes(data[:dlc])

                    records.append(FrameRecord(
                        timestamp=ts,
                        arbitration_id=aid,
                        channel=channel,
                        is_extended=is_extended,
                        is_lin=is_lin,
                        is_fd=bool(dlc > 8),
                        dlc=dlc,
                        data=data_bytes,
                    ))

            if not records:
                raise ValueError("No CAN/LIN messages found in MF4 file")
            return records
        finally:
            # 确保 MDF 文件句柄关闭，防止资源泄漏
            mdf.close()


class MF4Writer:
    """MF4/MDF 文件写入器。

    使用扁平独立通道布局写出 MF4 文件。每条 CAN 帧的属性拆分为 13 个
    独立 Signal，以 numpy 数组形式存储，通过 asammdf 库写入 .mf4 文件。

    Usage:
        MF4Writer.to_file(records, "/path/to/output.mf4")
    """

    @staticmethod
    def to_file(records: list[FrameRecord], path: str) -> None:
        """将 FrameRecord 列表写入 MF4 文件（扁平独立通道布局）。

        每条帧的属性被拆分为独立的 numpy 数组 Signal：
          t（时间戳）、CAN_ID（仲裁 ID）、CAN_Channel（通道号）、
          CAN_Flags（标志位合并）、CAN_DLC（数据长度码）、
          CAN_DataByte0~7（8 个字节通道）

        这种扁平布局兼容性好，但注意与真实采集设备的 MF4 格式不同
        （后者使用 CAN_DataFrame 复合结构体）。

        Args:
            records: 待写入的帧记录列表（非空，按时间顺序排列）
            path: 输出 MF4 文件的绝对路径

        Raises:
            ValueError: records 为空时抛出
        """
        if not records:
            raise ValueError("No records to write")

        n = len(records)

        # 从 FrameRecord 列表中提取各属性为 numpy 数组（asammdf 要求）
        timestamps = np.array([r.timestamp for r in records], dtype=np.float64)
        ids = np.array([r.arbitration_id for r in records], dtype=np.uint32)
        dlcs = np.array([r.dlc for r in records], dtype=np.uint8)
        channels = np.array([r.channel for r in records], dtype=np.uint8)

        # 标志位编码为单字节：bit0 = is_extended, bit1 = is_lin
        flags = np.array([
            (1 if r.is_extended else 0) | (2 if r.is_lin else 0)
            for r in records
        ], dtype=np.uint8)

        # 将每条帧的数据载荷拆分为 8 个独立字节通道
        # 数据不足 8 字节的帧，缺失字节填充为 0
        data_byte_arrays = []
        for bi in range(8):
            byte_samples = np.array([
                r.data[bi] if bi < len(r.data) else 0
                for r in records
            ], dtype=np.uint8)
            data_byte_arrays.append(byte_samples)

        # 组装 asammdf Signal 列表（所有信号共享同一时间轴）
        signals = [
            Signal(samples=timestamps, timestamps=timestamps, name="t", unit="s"),
            Signal(samples=ids, timestamps=timestamps, name="CAN_ID", unit=""),
            Signal(samples=channels, timestamps=timestamps, name="CAN_Channel", unit=""),
            Signal(samples=flags, timestamps=timestamps, name="CAN_Flags", unit=""),
            Signal(samples=dlcs, timestamps=timestamps, name="CAN_DLC", unit=""),
        ]

        for bi in range(8):
            signals.append(Signal(
                samples=data_byte_arrays[bi],
                timestamps=timestamps,
                name=f"CAN_DataByte{bi}",
                unit="",
            ))

        mdf = MDF()
        try:
            mdf.append(signals)
            mdf.save(path, overwrite=True)
        finally:
            # 确保 MDF 文件句柄关闭
            mdf.close()
