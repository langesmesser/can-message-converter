import numpy as np
from asammdf import MDF, Signal
from src.converters.base import FrameRecord


class MF4Reader:
    """Read CAN/LIN frame records from an MF4 file."""

    @staticmethod
    def from_file(path: str) -> list[FrameRecord]:
        mdf = MDF(path)
        records: list[FrameRecord] = []
        try:
            # Collect all signals by name using iter_channels
            channels_by_name: dict[str, Signal] = {}
            for sig in mdf.iter_channels():
                channels_by_name[sig.name] = sig

            # Try CAN logging extraction first (requires database)
            bus_map = mdf.bus_logging_map
            if bus_map and any(v for v in bus_map.values()):
                try:
                    # Look for CAN bus logging channels directly
                    for bus_type, channels in bus_map.items():
                        if bus_type not in ("CAN", "LIN"):
                            continue
                        for ch_name, ch_info in channels.items():
                            if ch_name in channels_by_name:
                                sig = channels_by_name[ch_name]
                                # This is a CAN/LIN bus signal, extract frames
                                # For now, fall through to named-channel parsing
                                pass
                except Exception:
                    pass

            # Fallback: extract from named channels written by MF4Writer
            if "CAN_ID" in channels_by_name:
                can_id_sig = channels_by_name["CAN_ID"]
                n = len(can_id_sig.samples)
                timestamps = can_id_sig.timestamps

                can_dlc_sig = channels_by_name.get("CAN_DLC")
                can_chan_sig = channels_by_name.get("CAN_Channel")
                can_flags_sig = channels_by_name.get("CAN_Flags")
                can_bus_sig = channels_by_name.get("CAN_Bus")

                # Collect data bytes
                data_byte_sigs: dict[int, Signal] = {}
                for bi in range(8):
                    name = f"CAN_DataByte{bi}"
                    if name in channels_by_name:
                        data_byte_sigs[bi] = channels_by_name[name]

                for i in range(n):
                    ts = float(timestamps[i])
                    aid = int(can_id_sig.samples[i])
                    dlc = int(can_dlc_sig.samples[i]) if can_dlc_sig is not None else 8
                    channel = int(can_chan_sig.samples[i]) if can_chan_sig is not None else 0

                    flags = int(can_flags_sig.samples[i]) if can_flags_sig is not None else 0
                    is_extended = bool(flags & 1)
                    is_lin = bool(flags & 2)

                    # Reconstruct data bytes and trim to DLC
                    data = bytearray()
                    for bi in range(8):
                        if bi in data_byte_sigs and i < len(data_byte_sigs[bi].samples):
                            data.append(int(data_byte_sigs[bi].samples[i]))
                        else:
                            break
                    data_bytes = bytes(data[:dlc])

                    bus = ""
                    if can_bus_sig is not None and i < len(can_bus_sig.samples):
                        bus_val = can_bus_sig.samples[i]
                        if isinstance(bus_val, bytes):
                            bus = bus_val.decode("utf-8", errors="replace").rstrip("\x00")
                        elif isinstance(bus_val, str):
                            bus = bus_val

                    records.append(FrameRecord(
                        timestamp=ts,
                        arbitration_id=aid,
                        channel=channel,
                        is_extended=is_extended,
                        is_lin=is_lin,
                        dlc=dlc,
                        data=data_bytes,
                        bus=bus,
                    ))

            if not records:
                raise ValueError("No CAN/LIN messages found in MF4 file")
            return records
        finally:
            mdf.close()


class MF4Writer:
    """Write CAN/LIN frame records to an MF4 file."""

    @staticmethod
    def to_file(records: list[FrameRecord], path: str) -> None:
        if not records:
            raise ValueError("No records to write")

        n = len(records)
        timestamps = np.array([r.timestamp for r in records], dtype=np.float64)
        ids = np.array([r.arbitration_id for r in records], dtype=np.uint32)
        dlcs = np.array([r.dlc for r in records], dtype=np.uint8)
        channels = np.array([r.channel for r in records], dtype=np.uint8)

        # Encode flags: bit 0 = is_extended, bit 1 = is_lin
        flags = np.array([
            (1 if r.is_extended else 0) | (2 if r.is_lin else 0)
            for r in records
        ], dtype=np.uint8)

        # Prepare data byte arrays (pad short data with zeros)
        data_byte_arrays = []
        for bi in range(8):
            byte_samples = np.array([
                r.data[bi] if bi < len(r.data) else 0
                for r in records
            ], dtype=np.uint8)
            data_byte_arrays.append(byte_samples)

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
            mdf.close()
