"""XLSX 写入器测试。"""

import os
import tempfile
import pandas as pd
import pytest
from openpyxl import load_workbook
from src.converters.base import FrameRecord
from src.converters.xlsx_writer import XLSXWriter


def _make_records():
    return [
        FrameRecord(
            timestamp=0.123456,
            arbitration_id=0x100,
            channel=0,
            is_extended=False,
            is_fd=False,
            dlc=8,
            data=bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]),
        ),
        FrameRecord(
            timestamp=1.0,
            arbitration_id=0x7FF,
            channel=1,
            is_extended=False,
            is_fd=False,
            dlc=3,
            data=bytes([0xAA, 0xBB, 0xCC]),
        ),
        FrameRecord(
            timestamp=2.5,
            arbitration_id=0x18FEF100,
            channel=0,
            is_extended=True,
            is_fd=True,
            dlc=9,
            data=bytes([0xFF] * 12),
        ),
    ]


class TestXLSXWriter:
    """XLSX 写入器单元测试。"""

    def test_basic(self):
        records = _make_records()
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            XLSXWriter.to_file(records, path)
            df = pd.read_excel(path)
            assert list(df.columns) == ["timestamp", "id", "data"]
            assert len(df) == 3
        finally:
            os.unlink(path)

    def test_timestamp_column(self):
        records = _make_records()
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            XLSXWriter.to_file(records, path)
            df = pd.read_excel(path, dtype=str)
            assert df["timestamp"].iloc[0] == "0.123"
            assert df["timestamp"].iloc[2] == "2.500"
        finally:
            os.unlink(path)

    def test_all_columns_are_text_format(self):
        records = _make_records()
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            XLSXWriter.to_file(records, path)
            wb = load_workbook(path)
            ws = wb.active
            for row in ws.iter_rows(min_row=2, max_row=4, min_col=1, max_col=3):
                for cell in row:
                    assert cell.number_format == "@"
        finally:
            os.unlink(path)

    def test_data_hex_format(self):
        records = _make_records()
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            XLSXWriter.to_file(records, path)
            df = pd.read_excel(path)
            assert df["data"].iloc[0] == "01 02 03 04 05 06 07 08"
            assert df["data"].iloc[1] == "AA BB CC"
            assert df["data"].iloc[2] == " ".join(["FF"] * 12)
        finally:
            os.unlink(path)

    def test_id_format(self):
        records = [
            FrameRecord(
                timestamp=0.1, arbitration_id=0x100, channel=0,
                is_extended=False, is_fd=False, dlc=0, data=b"",
            ),
        ]
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            XLSXWriter.to_file(records, path)
            df = pd.read_excel(path)
            assert df["id"].iloc[0] == "0x100"
        finally:
            os.unlink(path)

    def test_empty_records_raises(self):
        with pytest.raises(ValueError, match="No records"):
            XLSXWriter.to_file([], "/nonexistent/output.xlsx")

    def test_freeze_and_filter(self):
        records = _make_records()
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            XLSXWriter.to_file(records, path)
            wb = load_workbook(path)
            ws = wb.active
            assert ws.freeze_panes == "A2"
            assert ws.auto_filter.ref == "A1:C3"
            assert ws.column_dimensions["A"].width > 0
            assert ws.column_dimensions["B"].width > 0
            assert ws.column_dimensions["C"].width > 0
            for cell in ws[1]:
                assert cell.font.bold is True
            for row in ws.iter_rows(min_row=1, max_row=4, min_col=1, max_col=3):
                for cell in row:
                    assert cell.alignment.horizontal == "center"
        finally:
            os.unlink(path)
