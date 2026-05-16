import os
import tempfile
import pytest
from src.converters.txt_converter import TXTReader


def _write_txt(lines: list[str]) -> str:
    """Helper: write lines to a temp .txt file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


# ── basic format: timestamp id data_bytes ──

def test_basic_format():
    path = _write_txt([
        "0.000000    7FF    01 02 03 04 05 06 07 08",
        "1.000000    100    AA BB CC",
    ])
    try:
        records = TXTReader.from_file(path)
        assert len(records) == 2
        r0, r1 = records
        assert r0.timestamp == 0.0
        assert r0.arbitration_id == 0x7FF
        assert r0.channel == 0
        assert not r0.is_extended
        assert r0.dlc == 8
        assert r0.data == b"\x01\x02\x03\x04\x05\x06\x07\x08"
        assert r1.timestamp == 1.0
        assert r1.arbitration_id == 0x100
        assert r1.dlc == 3
        assert r1.data == b"\xAA\xBB\xCC"
    finally:
        os.unlink(path)


# ── with 0x prefix on ID ──

def test_id_with_0x_prefix():
    path = _write_txt([
        "0.5    0x7FF    01 02 03",
        "1.5    0x1A2B3C4D    FF",
    ])
    try:
        records = TXTReader.from_file(path)
        assert len(records) == 2
        assert records[0].arbitration_id == 0x7FF
        assert records[0].data == b"\x01\x02\x03"
        assert records[1].arbitration_id == 0x1A2B3C4D
        assert records[1].is_extended
    finally:
        os.unlink(path)


# ── with channel column ──

def test_with_channel():
    path = _write_txt([
        "0.0    1    7FF    01 02 03",
        "1.0    0    100    FF EE",
    ])
    try:
        records = TXTReader.from_file(path)
        assert len(records) == 2
        assert records[0].channel == 1
        assert records[0].arbitration_id == 0x7FF
        assert records[1].channel == 0
        assert records[1].arbitration_id == 0x100
    finally:
        os.unlink(path)


# ── tabs as separator ──

def test_tab_separated():
    path = _write_txt([
        "0.0\t7FF\t01\t02\t03",
    ])
    try:
        records = TXTReader.from_file(path)
        assert len(records) == 1
        assert records[0].arbitration_id == 0x7FF
        assert records[0].data == b"\x01\x02\x03"
    finally:
        os.unlink(path)


# ── mixed whitespace ──

def test_mixed_whitespace():
    path = _write_txt([
        "  0.0    7FF     01   02\t03  ",
    ])
    try:
        records = TXTReader.from_file(path)
        assert len(records) == 1
        assert records[0].arbitration_id == 0x7FF
        assert records[0].data == b"\x01\x02\x03"
    finally:
        os.unlink(path)


# ── header / comment lines skipped ──

def test_skip_header_lines():
    path = _write_txt([
        "Time        ID      Data",
        "========    ====    ====",
        "0.0    7FF    01 02",
        "1.0    100    AA",
    ])
    try:
        records = TXTReader.from_file(path)
        assert len(records) == 2
    finally:
        os.unlink(path)


# ── empty lines skipped ──

def test_skip_empty_lines():
    path = _write_txt([
        "",
        "0.0    7FF    01",
        "",
        "1.0    100    AA",
        "",
    ])
    try:
        records = TXTReader.from_file(path)
        assert len(records) == 2
    finally:
        os.unlink(path)


# ── CAN FD (data > 8 bytes) ──

def test_can_fd():
    path = _write_txt([
        "0.0    7FF    01 02 03 04 05 06 07 08 09 0A 0B 0C",
    ])
    try:
        records = TXTReader.from_file(path)
        assert len(records) == 1
        r = records[0]
        assert r.is_fd
        assert r.dlc == 9  # 12 bytes → DLC 9
        assert len(r.data) == 12
    finally:
        os.unlink(path)


# ── extended ID detection ──

def test_extended_id():
    path = _write_txt([
        "0.0    1FFF    01",
        "0.1    7FF     02",
    ])
    try:
        records = TXTReader.from_file(path)
        assert records[0].is_extended
        assert not records[1].is_extended
    finally:
        os.unlink(path)


# ── empty data ──

def test_empty_data():
    path = _write_txt([
        "0.0    7FF",
    ])
    try:
        records = TXTReader.from_file(path)
        assert len(records) == 1
        assert records[0].data == b""
        assert records[0].dlc == 0
    finally:
        os.unlink(path)


# ── empty file raises ──

def test_empty_file_raises():
    path = _write_txt([])
    try:
        with pytest.raises(ValueError):
            TXTReader.from_file(path)
    finally:
        os.unlink(path)


# ── file with only headers raises ──

def test_only_headers_raises():
    path = _write_txt([
        "Header line",
        "===========",
    ])
    try:
        with pytest.raises(ValueError):
            TXTReader.from_file(path)
    finally:
        os.unlink(path)


# ── timestamp with decimal ──

def test_fractional_timestamp():
    path = _write_txt([
        "1234.567890    7FF    01 02",
    ])
    try:
        records = TXTReader.from_file(path)
        assert records[0].timestamp == 1234.567890
    finally:
        os.unlink(path)
