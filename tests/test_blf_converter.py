import os
import tempfile
import pytest
from src.converters.base import FrameRecord
from src.converters.blf_converter import BLFReader, BLFWriter


def _make_records():
    return [
        FrameRecord(
            timestamp=0.0,
            arbitration_id=0x100,
            channel=0,
            is_extended=False,
            is_lin=False,
            dlc=8,
            data=b"\x01\x02\x03\x04\x05\x06\x07\x08",
        ),
        FrameRecord(
            timestamp=0.5,
            arbitration_id=0x1FFFFFFF,
            channel=1,
            is_extended=True,
            is_lin=False,
            dlc=4,
            data=b"\xAA\xBB\xCC\xDD",
        ),
    ]


def test_blf_round_trip():
    original = _make_records()
    with tempfile.NamedTemporaryFile(suffix=".blf", delete=False) as f:
        path = f.name
    try:
        BLFWriter.to_file(original, path)
        result = BLFReader.from_file(path)
        assert len(result) == len(original)
        for r, o in zip(result, original):
            assert r.timestamp == pytest.approx(o.timestamp, rel=1e-4)
            assert r.arbitration_id == o.arbitration_id
            assert r.channel == o.channel
            assert r.is_extended == o.is_extended
            assert r.dlc == o.dlc
            assert r.data == o.data
    finally:
        os.unlink(path)


def test_blf_read_empty_file_raises():
    with tempfile.NamedTemporaryFile(suffix=".blf", delete=False) as f:
        path = f.name
    try:
        with pytest.raises(Exception):
            BLFReader.from_file(path)
    finally:
        os.unlink(path)


def test_blf_writer_creates_file():
    records = [FrameRecord(timestamp=0.0, arbitration_id=0x200, dlc=3, data=b"\x01\x02\x03")]
    with tempfile.NamedTemporaryFile(suffix=".blf", delete=False) as f:
        path = f.name
    try:
        BLFWriter.to_file(records, path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_blf_single_frame():
    record = FrameRecord(
        timestamp=1.0,
        arbitration_id=0x7FF,
        is_extended=True,
        dlc=8,
        data=b"\xFF" * 8,
        channel=2,
    )
    with tempfile.NamedTemporaryFile(suffix=".blf", delete=False) as f:
        path = f.name
    try:
        BLFWriter.to_file([record], path)
        result = BLFReader.from_file(path)
        assert len(result) == 1
        r = result[0]
        assert r.arbitration_id == 0x7FF
        assert r.is_extended is True
        assert r.data == b"\xFF" * 8
    finally:
        os.unlink(path)
