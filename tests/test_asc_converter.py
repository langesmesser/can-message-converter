import os
import tempfile
import pytest
from src.converters.base import FrameRecord
from src.converters.asc_converter import ASCReader, ASCWriter


def _make_records():
    return [
        FrameRecord(
            timestamp=0.0,
            arbitration_id=0x100,
            channel=0,
            is_extended=False,
            dlc=8,
            data=b"\x01\x02\x03\x04\x05\x06\x07\x08",
        ),
        FrameRecord(
            timestamp=1.0,
            arbitration_id=0x1FFFFFFF,
            channel=1,
            is_extended=True,
            dlc=3,
            data=b"\xAA\xBB\xCC",
        ),
    ]


def test_asc_round_trip():
    original = _make_records()
    with tempfile.NamedTemporaryFile(suffix=".asc", delete=False) as f:
        path = f.name
    try:
        ASCWriter.to_file(original, path)
        result = ASCReader.from_file(path)
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


def test_asc_empty_file_raises():
    with tempfile.NamedTemporaryFile(suffix=".asc", delete=False) as f:
        path = f.name
    try:
        with pytest.raises(Exception):
            ASCReader.from_file(path)
    finally:
        os.unlink(path)


def test_asc_multiple_frames():
    records = [
        FrameRecord(timestamp=float(i), arbitration_id=0x100 + i, dlc=8, data=b"\x00" * 8)
        for i in range(10)
    ]
    with tempfile.NamedTemporaryFile(suffix=".asc", delete=False) as f:
        path = f.name
    try:
        ASCWriter.to_file(records, path)
        result = ASCReader.from_file(path)
        assert len(result) == 10
        for i, r in enumerate(result):
            assert r.arbitration_id == 0x100 + i
    finally:
        os.unlink(path)
