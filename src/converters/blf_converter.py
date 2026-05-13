import can
from src.converters.base import FrameRecord


class BLFReader:
    @staticmethod
    def from_file(path: str) -> list[FrameRecord]:
        records = []
        with can.BLFReader(path) as reader:
            for msg in reader:
                records.append(FrameRecord(
                    timestamp=msg.timestamp,
                    arbitration_id=msg.arbitration_id,
                    channel=getattr(msg, "channel", 0),
                    is_extended=msg.is_extended_id,
                    is_lin=getattr(msg, "is_lin_message", False),
                    dlc=msg.dlc,
                    data=msg.data if msg.data else b"",
                    bus=getattr(msg, "bus", "") or "",
                ))
        if not records:
            raise ValueError("No messages found in BLF file")
        return records


class BLFWriter:
    @staticmethod
    def to_file(records: list[FrameRecord], path: str) -> None:
        if not records:
            raise ValueError("No records to write")
        with can.BLFWriter(path) as writer:
            for r in records:
                msg = can.Message(
                    timestamp=r.timestamp,
                    arbitration_id=r.arbitration_id,
                    is_extended_id=r.is_extended,
                    channel=r.channel,
                    dlc=r.dlc,
                    data=r.data,
                )
                writer.on_message_received(msg)
