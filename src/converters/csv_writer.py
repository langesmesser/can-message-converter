import pandas as pd
from src.converters.base import FrameRecord


class CSVWriter:
    @staticmethod
    def to_file(records: list[FrameRecord], path: str) -> None:
        if not records:
            raise ValueError("No records to write")

        rows = []
        for r in records:
            hex_data = " ".join(f"{b:02X}" for b in r.data)
            rows.append({
                "Timestamp": r.timestamp,
                "Channel": r.channel,
                "ID": hex(r.arbitration_id),
                "Extended": int(r.is_extended),
                "Type": "LIN" if r.is_lin else "CAN",
                "DLC": r.dlc,
                "Data": hex_data,
                "Bus": r.bus,
            })

        df = pd.DataFrame(rows)
        df.to_csv(path, index=False)
