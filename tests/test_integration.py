import os
import tempfile
import pytest
from src.converters.base import FrameRecord
from src.converters.blf_converter import BLFReader, BLFWriter
from src.converters.asc_converter import ASCReader, ASCWriter
from src.converters.mf4_converter import MF4Reader, MF4Writer
from src.converters.csv_writer import CSVWriter


_SAMPLE = [
    FrameRecord(timestamp=0.0, channel=0, arbitration_id=0x100, is_extended=False,
                dlc=8, data=b"\x01\x02\x03\x04\x05\x06\x07\x08", bus="CAN0"),
    FrameRecord(timestamp=0.5, channel=0, arbitration_id=0x200, is_extended=True,
                dlc=4, data=b"\xAA\xBB\xCC\xDD", bus="CAN0"),
    FrameRecord(timestamp=1.0, channel=1, arbitration_id=0x300, is_extended=False,
                dlc=3, data=b"\x11\x22\x33", bus="CAN1"),
]


def _assert_records_equal(actual, expected):
    assert len(actual) == len(expected)
    for a, e in zip(actual, expected):
        assert a.timestamp == pytest.approx(e.timestamp, rel=1e-3)
        assert a.arbitration_id == e.arbitration_id
        assert a.channel == e.channel
        assert a.is_extended == e.is_extended
        assert a.dlc == e.dlc
        assert a.data == e.data
        assert a.bus == e.bus


class TestBLFtoX:
    def test_blf_to_asc(self):
        with tempfile.NamedTemporaryFile(suffix=".blf", delete=False) as f:
            blf_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".asc", delete=False) as f:
            asc_path = f.name
        try:
            BLFWriter.to_file(_SAMPLE, blf_path)
            records = BLFReader.from_file(blf_path)
            ASCWriter.to_file(records, asc_path)
            result = ASCReader.from_file(asc_path)
            _assert_records_equal(result, records)
        finally:
            os.unlink(blf_path)
            os.unlink(asc_path)

    def test_blf_to_mf4(self):
        with tempfile.NamedTemporaryFile(suffix=".blf", delete=False) as f:
            blf_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".mf4", delete=False) as f:
            mf4_path = f.name
        try:
            BLFWriter.to_file(_SAMPLE, blf_path)
            records = BLFReader.from_file(blf_path)
            MF4Writer.to_file(records, mf4_path)
            result = MF4Reader.from_file(mf4_path)
            _assert_records_equal(result, records)
        finally:
            os.unlink(blf_path)
            os.unlink(mf4_path)

    def test_blf_to_csv(self):
        with tempfile.NamedTemporaryFile(suffix=".blf", delete=False) as f:
            blf_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            csv_path = f.name
        try:
            BLFWriter.to_file(_SAMPLE, blf_path)
            records = BLFReader.from_file(blf_path)
            CSVWriter.to_file(records, csv_path)
            assert os.path.getsize(csv_path) > 0
        finally:
            os.unlink(blf_path)
            os.unlink(csv_path)


class TestASCtoX:
    def test_asc_to_blf(self):
        with tempfile.NamedTemporaryFile(suffix=".asc", delete=False) as f:
            asc_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".blf", delete=False) as f:
            blf_path = f.name
        try:
            ASCWriter.to_file(_SAMPLE, asc_path)
            records = ASCReader.from_file(asc_path)
            BLFWriter.to_file(records, blf_path)
            result = BLFReader.from_file(blf_path)
            _assert_records_equal(result, records)
        finally:
            os.unlink(asc_path)
            os.unlink(blf_path)

    def test_asc_to_mf4(self):
        with tempfile.NamedTemporaryFile(suffix=".asc", delete=False) as f:
            asc_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".mf4", delete=False) as f:
            mf4_path = f.name
        try:
            ASCWriter.to_file(_SAMPLE, asc_path)
            records = ASCReader.from_file(asc_path)
            MF4Writer.to_file(records, mf4_path)
            result = MF4Reader.from_file(mf4_path)
            _assert_records_equal(result, records)
        finally:
            os.unlink(asc_path)
            os.unlink(mf4_path)

    def test_asc_to_csv(self):
        with tempfile.NamedTemporaryFile(suffix=".asc", delete=False) as f:
            asc_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            csv_path = f.name
        try:
            ASCWriter.to_file(_SAMPLE, asc_path)
            records = ASCReader.from_file(asc_path)
            CSVWriter.to_file(records, csv_path)
            assert os.path.getsize(csv_path) > 0
        finally:
            os.unlink(asc_path)
            os.unlink(csv_path)


class TestMF4toX:
    def test_mf4_to_blf(self):
        with tempfile.NamedTemporaryFile(suffix=".mf4", delete=False) as f:
            mf4_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".blf", delete=False) as f:
            blf_path = f.name
        try:
            MF4Writer.to_file(_SAMPLE, mf4_path)
            records = MF4Reader.from_file(mf4_path)
            BLFWriter.to_file(records, blf_path)
            result = BLFReader.from_file(blf_path)
            _assert_records_equal(result, records)
        finally:
            os.unlink(mf4_path)
            os.unlink(blf_path)

    def test_mf4_to_asc(self):
        with tempfile.NamedTemporaryFile(suffix=".mf4", delete=False) as f:
            mf4_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".asc", delete=False) as f:
            asc_path = f.name
        try:
            MF4Writer.to_file(_SAMPLE, mf4_path)
            records = MF4Reader.from_file(mf4_path)
            ASCWriter.to_file(records, asc_path)
            result = ASCReader.from_file(asc_path)
            _assert_records_equal(result, records)
        finally:
            os.unlink(mf4_path)
            os.unlink(asc_path)

    def test_mf4_to_csv(self):
        with tempfile.NamedTemporaryFile(suffix=".mf4", delete=False) as f:
            mf4_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            csv_path = f.name
        try:
            MF4Writer.to_file(_SAMPLE, mf4_path)
            records = MF4Reader.from_file(mf4_path)
            CSVWriter.to_file(records, csv_path)
            assert os.path.getsize(csv_path) > 0
        finally:
            os.unlink(mf4_path)
            os.unlink(csv_path)
