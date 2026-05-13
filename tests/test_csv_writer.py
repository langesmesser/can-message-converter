import os
import tempfile
import pytest
import pandas as pd
from src.converters.base import FrameRecord
from src.converters.csv_writer import CSVWriter


def _make_records():
    return [
        FrameRecord(
            timestamp=0.0,
            channel=0,
            arbitration_id=0x100,
            is_extended=False,
            is_lin=False,
            dlc=8,
            data=b"\x01\x02\x03\x04\x05\x06\x07\x08",
            bus="CAN0",
        ),
        FrameRecord(
            timestamp=0.5,
            channel=1,
            arbitration_id=0x1FFFFFFF,
            is_extended=True,
            is_lin=False,
            dlc=4,
            data=b"\xAA\xBB\xCC\xDD",
            bus="CAN1",
        ),
        FrameRecord(
            timestamp=1.0,
            channel=0,
            arbitration_id=0x3C,
            is_extended=False,
            is_lin=True,
            dlc=4,
            data=b"\x11\x22\x33\x44",
            bus="LIN1",
        ),
    ]


def test_csv_write_and_readable():
    records = _make_records()
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = f.name
    try:
        CSVWriter.to_file(records, path)
        assert os.path.exists(path)
        df = pd.read_csv(path)
        assert len(df) == 3
        assert list(df.columns) == [
            "Timestamp", "Channel", "ID", "Extended",
            "Type", "DLC", "Data", "Bus"
        ]
    finally:
        os.unlink(path)


def test_csv_timestamp_column():
    records = _make_records()
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = f.name
    try:
        CSVWriter.to_file(records, path)
        df = pd.read_csv(path)
        assert df["Timestamp"].iloc[0] == 0.0
        assert df["Timestamp"].iloc[1] == 0.5
        assert df["Timestamp"].iloc[2] == 1.0
    finally:
        os.unlink(path)


def test_csv_data_column_hex_format():
    records = _make_records()
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = f.name
    try:
        CSVWriter.to_file(records, path)
        df = pd.read_csv(path)
        assert df["Data"].iloc[0] == "01 02 03 04 05 06 07 08"
        assert df["Data"].iloc[1] == "AA BB CC DD"
    finally:
        os.unlink(path)


def test_csv_type_column():
    records = _make_records()
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = f.name
    try:
        CSVWriter.to_file(records, path)
        df = pd.read_csv(path)
        assert df["Type"].iloc[0] == "CAN"
        assert df["Type"].iloc[2] == "LIN"
    finally:
        os.unlink(path)


def test_csv_empty_records_raises():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        path = f.name
    try:
        with pytest.raises(ValueError, match="No records"):
            CSVWriter.to_file([], path)
    finally:
        os.unlink(path)
