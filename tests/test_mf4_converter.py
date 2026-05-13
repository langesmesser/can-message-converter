import os
import tempfile
import pytest
from src.converters.base import FrameRecord
from src.converters.mf4_converter import MF4Reader, MF4Writer


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
            timestamp=0.5,
            arbitration_id=0x1FFFFFFF,
            channel=1,
            is_extended=True,
            dlc=4,
            data=b"\xAA\xBB\xCC\xDD",
        ),
    ]


def test_mf4_round_trip():
    original = _make_records()
    with tempfile.NamedTemporaryFile(suffix=".mf4", delete=False) as f:
        path = f.name
    try:
        MF4Writer.to_file(original, path)
        result = MF4Reader.from_file(path)
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


def test_mf4_empty_file_raises():
    with tempfile.NamedTemporaryFile(suffix=".mf4", delete=False) as f:
        path = f.name
    try:
        with pytest.raises(Exception):
            MF4Reader.from_file(path)
    finally:
        os.unlink(path)


def test_mf4_single_frame():
    record = FrameRecord(
        timestamp=2.0,
        arbitration_id=0x7FF,
        is_extended=True,
        dlc=8,
        data=b"\xFF" * 8,
        channel=0,
    )
    with tempfile.NamedTemporaryFile(suffix=".mf4", delete=False) as f:
        path = f.name
    try:
        MF4Writer.to_file([record], path)
        result = MF4Reader.from_file(path)
        assert len(result) == 1
        r = result[0]
        assert r.arbitration_id == 0x7FF
    finally:
        os.unlink(path)
