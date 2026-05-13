# CAN Bus Message Format Converter — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a PySide6 desktop app that converts CAN/LIN bus logs between BLF/MF4/ASC formats and exports to CSV, packaged as a single .exe.

**Architecture:** All converters go through a common internal `FrameRecord` representation. Readers parse input → `list[FrameRecord]`, writers serialize `list[FrameRecord]` → output. This isolates each format to one reader/writer pair and makes adding formats trivial. Conversion runs in a QThread to keep the UI responsive.

**Tech Stack:** PySide6, python-can, asammdf, pandas, PyInstaller

---

## File Structure

| File | Responsibility |
|------|---------------|
| `src/converters/base.py` | FrameRecord dataclass, Converter ABC |
| `src/converters/blf_converter.py` | BLFReader + BLFWriter |
| `src/converters/asc_converter.py` | ASCReader + ASCWriter |
| `src/converters/mf4_converter.py` | MF4Reader + MF4Writer |
| `src/converters/csv_writer.py` | CSV write-only exporter |
| `src/converters/registry.py` | Format dispatch table, validation |
| `src/worker.py` | QThread worker for async conversion |
| `src/ui/main_window.py` | MainWindow, widget setup, signal wiring |
| `src/ui/theme.qss` | Dark theme stylesheet |
| `src/main.py` | Entry point, QApplication bootstrap |
| `tests/test_blf_converter.py` | BLF round-trip and edge case tests |
| `tests/test_asc_converter.py` | ASC round-trip and edge case tests |
| `tests/test_mf4_converter.py` | MF4 round-trip and edge case tests |
| `tests/test_csv_writer.py` | CSV export tests |
| `tests/test_registry.py` | Dispatch table tests |
| `tests/test_integration.py` | Full cross-format conversion tests |
| `requirements.txt` | Python dependencies |
| `build.spec` | PyInstaller spec file |

---

### Task 1: Project Setup and Dependencies

**Files:**
- Modify: `requirements.txt`
- Create: `src/__init__.py`, `src/converters/__init__.py`, `src/ui/__init__.py`, `tests/__init__.py`

- [ ] **Step 1: Write updated requirements.txt**

```
python-can>=4.5.0
asammdf>=8.1.0
pandas>=2.2.0
PySide6>=6.7.0
pyinstaller>=6.0.0
pytest>=8.0.0
```

- [ ] **Step 2: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: all packages install without error

- [ ] **Step 3: Create package init files**

```
src/__init__.py           # empty
src/converters/__init__.py # empty
src/ui/__init__.py         # empty
tests/__init__.py          # empty
```

- [ ] **Step 4: Commit**

```bash
git add requirements.txt src/__init__.py src/converters/__init__.py src/ui/__init__.py tests/__init__.py
git commit -m "chore: project setup with dependencies and package structure"
```

---

### Task 2: FrameRecord Data Model and Converter ABC

**Files:**
- Create: `src/converters/base.py`
- Create: `tests/test_base.py`

- [ ] **Step 1: Write tests for FrameRecord and Converter ABC**

```python
# tests/test_base.py
import pytest
from dataclasses import asdict
from src.converters.base import FrameRecord, Converter


def test_framerecord_defaults():
    fr = FrameRecord(timestamp=1.5, arbitration_id=0x123)
    assert fr.timestamp == 1.5
    assert fr.arbitration_id == 0x123
    assert fr.channel == 0
    assert fr.is_extended is False
    assert fr.is_lin is False
    assert fr.dlc == 8
    assert fr.data == b''
    assert fr.bus == ""


def test_framerecord_full():
    fr = FrameRecord(
        timestamp=2.0,
        channel=1,
        arbitration_id=0x7FF,
        is_extended=True,
        is_lin=False,
        dlc=8,
        data=b'\x01\x02\x03\x04\x05\x06\x07\x08',
        bus="CAN1",
    )
    assert fr.timestamp == 2.0
    assert fr.channel == 1
    assert fr.arbitration_id == 0x7FF
    assert fr.is_extended is True
    assert fr.dlc == 8
    assert len(fr.data) == 8
    assert fr.bus == "CAN1"


def test_framerecord_lin():
    fr = FrameRecord(
        timestamp=0.5,
        arbitration_id=0x3C,
        is_lin=True,
        dlc=4,
        data=b'\xAA\xBB\xCC\xDD',
    )
    assert fr.is_lin is True


def test_framerecord_immutable():
    fr = FrameRecord(timestamp=1.0, arbitration_id=0x100)
    with pytest.raises(Exception):
        fr.timestamp = 2.0


def test_converter_abc_enforces_contract():
    class Incomplete(Converter):
        pass
    with pytest.raises(TypeError):
        Incomplete()


def test_converter_sublass_ok():
    class Complete(Converter):
        @staticmethod
        def from_file(path): pass
        @staticmethod
        def to_file(records, path): pass
    assert Complete() is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_base.py -v`
Expected: All tests FAIL (FrameRecord/Converter not defined)

- [ ] **Step 3: Implement FrameRecord and Converter ABC**

```python
# src/converters/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class FrameRecord:
    timestamp: float
    arbitration_id: int
    channel: int = 0
    is_extended: bool = False
    is_lin: bool = False
    dlc: int = 8
    data: bytes = b""
    bus: str = ""


class Converter(ABC):
    @staticmethod
    @abstractmethod
    def from_file(path: str) -> list[FrameRecord]:
        """Read a file and return a list of FrameRecord."""

    @staticmethod
    @abstractmethod
    def to_file(records: list[FrameRecord], path: str) -> None:
        """Write a list of FrameRecord to a file."""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_base.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/converters/base.py tests/test_base.py
git commit -m "feat: add FrameRecord dataclass and Converter ABC"
```

---

### Task 3: Converter Registry

**Files:**
- Create: `src/converters/registry.py`
- Create: `tests/test_registry.py`

- [ ] **Step 1: Write tests for registry**

```python
# tests/test_registry.py
import pytest
from src.converters.registry import (
    get_reader,
    get_writer,
    get_output_formats,
    supports_extension,
    READERS,
    WRITERS,
)


def test_readers_have_all_input_formats():
    assert "blf" in READERS
    assert "asc" in READERS
    assert "mf4" in READERS


def test_writers_have_blf_mf4_asc_csv():
    assert "blf" in WRITERS
    assert "mf4" in WRITERS
    assert "asc" in WRITERS
    assert "csv" in WRITERS


def test_get_reader_returns_callable():
    reader = get_reader("blf")
    assert callable(reader)


def test_get_reader_raises_for_unknown():
    with pytest.raises(ValueError, match="Unsupported input format"):
        get_reader("xyz")


def test_get_writer_returns_callable():
    writer = get_writer("csv")
    assert callable(writer)


def test_get_writer_raises_for_unknown():
    with pytest.raises(ValueError, match="Unsupported output format"):
        get_writer("xyz")


def test_get_output_formats_excludes_input():
    formats = get_output_formats("blf")
    assert "blf" not in formats
    assert "asc" in formats
    assert "mf4" in formats
    assert "csv" in formats


def test_get_output_formats_all_for_unknown():
    formats = get_output_formats("xyz")
    assert "blf" in formats
    assert "mf4" in formats
    assert "asc" in formats
    assert "csv" in formats


def test_supports_extension():
    assert supports_extension("blf") is True
    assert supports_extension("asc") is True
    assert supports_extension("mf4") is True
    assert supports_extension("csv") is True
    assert supports_extension("txt") is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_registry.py -v`
Expected: FAIL (module not found)

- [ ] **Step 3: Implement registry**

```python
# src/converters/registry.py
from src.converters.blf_converter import BLFReader, BLFWriter
from src.converters.asc_converter import ASCReader, ASCWriter
from src.converters.mf4_converter import MF4Reader, MF4Writer
from src.converters.csv_writer import CSVWriter

READERS = {
    "blf": BLFReader.from_file,
    "asc": ASCReader.from_file,
    "mf4": MF4Reader.from_file,
}

WRITERS = {
    "blf": BLFWriter.to_file,
    "asc": ASCWriter.to_file,
    "mf4": MF4Writer.to_file,
    "csv": CSVWriter.to_file,
}

ALL_FORMATS = {"blf", "mf4", "asc", "csv"}


def get_reader(extension: str):
    ext = extension.lower().lstrip(".")
    if ext not in READERS:
        raise ValueError(f"Unsupported input format: .{ext}")
    return READERS[ext]


def get_writer(extension: str):
    ext = extension.lower().lstrip(".")
    if ext not in WRITERS:
        raise ValueError(f"Unsupported output format: .{ext}")
    return WRITERS[ext]


def get_output_formats(input_extension: str) -> list[str]:
    ext = input_extension.lower().lstrip(".")
    return sorted(f for f in ALL_FORMATS if f != ext)


def supports_extension(extension: str) -> bool:
    ext = extension.lower().lstrip(".")
    return ext in ALL_FORMATS
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_registry.py -v`
Expected: FAIL (import error — converters not created yet)

This is expected. The registry imports converters that don't exist yet. Tests for registry will pass once Tasks 4-7 are done. We'll re-run this test at that point.

- [ ] **Step 5: Commit**

```bash
git add src/converters/registry.py tests/test_registry.py
git commit -m "feat: add converter registry with dispatch table"
```

---

### Task 4: BLF Converter (Tests → Implementation)

**Files:**
- Create: `src/converters/blf_converter.py`
- Create: `tests/test_blf_converter.py`

- [ ] **Step 1: Write BLF converter tests**

```python
# tests/test_blf_converter.py
import os
import tempfile
import can
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_blf_converter.py -v`
Expected: FAIL (BLFReader/BLFWriter not defined)

- [ ] **Step 3: Implement BLFReader and BLFWriter**

```python
# src/converters/blf_converter.py
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
                    is_lin_message=r.is_lin,
                    channel=r.channel,
                    dlc=r.dlc,
                    data=r.data,
                    bus=r.bus or None,
                )
                writer.on_message_received(msg)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_blf_converter.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/converters/blf_converter.py tests/test_blf_converter.py
git commit -m "feat: add BLF reader/writer converter"
```

---

### Task 5: ASC Converter (Tests → Implementation)

**Files:**
- Create: `src/converters/asc_converter.py`
- Create: `tests/test_asc_converter.py`

- [ ] **Step 1: Write ASC converter tests**

```python
# tests/test_asc_converter.py
import os
import tempfile
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_asc_converter.py -v`
Expected: FAIL (ASCReader/ASCWriter not defined)

- [ ] **Step 3: Implement ASCReader and ASCWriter**

```python
# src/converters/asc_converter.py
import can
from src.converters.base import FrameRecord


class ASCReader:
    @staticmethod
    def from_file(path: str) -> list[FrameRecord]:
        records = []
        with can.ASCReader(path) as reader:
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
            raise ValueError("No messages found in ASC file")
        return records


class ASCWriter:
    @staticmethod
    def to_file(records: list[FrameRecord], path: str) -> None:
        if not records:
            raise ValueError("No records to write")
        with can.ASCWriter(path) as writer:
            for r in records:
                msg = can.Message(
                    timestamp=r.timestamp,
                    arbitration_id=r.arbitration_id,
                    is_extended_id=r.is_extended,
                    is_lin_message=r.is_lin,
                    channel=r.channel,
                    dlc=r.dlc,
                    data=r.data,
                )
                writer.on_message_received(msg)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_asc_converter.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/converters/asc_converter.py tests/test_asc_converter.py
git commit -m "feat: add ASC reader/writer converter"
```

---

### Task 6: MF4 Converter (Tests → Implementation)

**Files:**
- Create: `src/converters/mf4_converter.py`
- Create: `tests/test_mf4_converter.py`

- [ ] **Step 1: Write MF4 converter tests**

```python
# tests/test_mf4_converter.py
import os
import tempfile
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_mf4_converter.py -v`
Expected: FAIL (MF4Reader/MF4Writer not defined)

- [ ] **Step 3: Implement MF4Reader and MF4Writer**

```python
# src/converters/mf4_converter.py
import numpy as np
from asammdf import MDF, Signal
from src.converters.base import FrameRecord


class MF4Reader:
    @staticmethod
    def from_file(path: str) -> list[FrameRecord]:
        mdf = MDF(path)
        records = []

        for group_index in range(len(mdf.groups)):
            group = mdf.groups[group_index]
            channels = group.channels
            if not channels:
                continue

            # Try to find CAN-specific channels from asammdf's CAN logging extraction
            try:
                can_iter = mdf.iter_can_logging()
                for msg in can_iter:
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
                if records:
                    return records
            except Exception:
                pass

            # Fallback: try to extract from named channels
            timestamps = None
            ids = None
            data_bytes = None
            for ch in channels:
                ch_name = ch.name.lower() if ch.name else ""
                if "can_id" in ch_name or "arbitration_id" in ch_name or "id" in ch_name:
                    ids = ch.samples
                elif "can_data" in ch_name or "data" in ch_name:
                    data_bytes = ch.samples
                if timestamps is None:
                    timestamps = ch.timestamps

            if ids is not None and timestamps is not None:
                for i in range(len(timestamps)):
                    ts = float(timestamps[i])
                    aid = int(ids[i]) if ids is not None else 0
                    data = data_bytes[i].tobytes() if data_bytes is not None and i < len(data_bytes) else b""
                    records.append(FrameRecord(
                        timestamp=ts,
                        arbitration_id=aid,
                        dlc=len(data) if data else 0,
                        data=data,
                    ))

        if not records:
            raise ValueError("No CAN/LIN messages found in MF4 file")
        return records


class MF4Writer:
    @staticmethod
    def to_file(records: list[FrameRecord], path: str) -> None:
        if not records:
            raise ValueError("No records to write")

        timestamps = np.array([r.timestamp for r in records], dtype=np.float64)
        ids = np.array([r.arbitration_id for r in records], dtype=np.uint32)
        dlcs = np.array([r.dlc for r in records], dtype=np.uint8)

        signals = [
            Signal(
                samples=timestamps,
                timestamps=timestamps,
                name="t",
                unit="s",
            ),
            Signal(
                samples=ids,
                timestamps=timestamps,
                name="CAN_ID",
                unit="",
            ),
            Signal(
                samples=dlcs,
                timestamps=timestamps,
                name="CAN_DLC",
                unit="",
            ),
        ]

        # Add data bytes as separate signals
        for byte_idx in range(8):
            byte_samples = np.array([
                r.data[byte_idx] if byte_idx < len(r.data) else 0
                for r in records
            ], dtype=np.uint8)
            signals.append(Signal(
                samples=byte_samples,
                timestamps=timestamps,
                name=f"CAN_DataByte{byte_idx}",
                unit="",
            ))

        mdf = MDF()
        mdf.append(signals)
        mdf.save(path, overwrite=True)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_mf4_converter.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/converters/mf4_converter.py tests/test_mf4_converter.py
git commit -m "feat: add MF4 reader/writer converter"
```

---

### Task 7: CSV Writer (Tests → Implementation)

**Files:**
- Create: `src/converters/csv_writer.py`
- Create: `tests/test_csv_writer.py`

- [ ] **Step 1: Write CSV writer tests**

```python
# tests/test_csv_writer.py
import os
import tempfile
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
        # Data should be hex string without "0x" prefix
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_csv_writer.py -v`
Expected: FAIL (CSVWriter not defined)

- [ ] **Step 3: Implement CSVWriter**

```python
# src/converters/csv_writer.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_csv_writer.py -v`
Expected: All 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/converters/csv_writer.py tests/test_csv_writer.py
git commit -m "feat: add CSV writer exporter"
```

---

### Task 8: Cross-Format Integration Tests

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write integration tests**

```python
# tests/test_integration.py
import os
import tempfile
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
```

- [ ] **Step 2: Run all integration tests**

Run: `pytest tests/test_integration.py -v`
Expected: 9 tests PASS (all cross-format conversions)

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add cross-format integration tests (9 conversion paths)"
```

---

### Task 9: Registry Tests (Verify After Converters Exist)

**Files:**
- Modify: none (tests and code already exist from Task 3)

- [ ] **Step 1: Run registry tests now that converters exist**

Run: `pytest tests/test_registry.py -v`
Expected: All 9 tests PASS

- [ ] **Step 2: Run entire test suite**

Run: `pytest tests/ -v`
Expected: All tests from all files PASS

- [ ] **Step 3: Commit any fixes if needed**

```bash
git add -A
git commit -m "chore: verify all tests pass after converter implementation"
```

---

### Task 10: Conversion Worker Thread

**Files:**
- Create: `src/worker.py`

- [ ] **Step 1: Write the worker**

```python
# src/worker.py
import os
import traceback
from PySide6.QtCore import QThread, Signal
from src.converters.registry import get_reader, get_writer


class ConversionWorker(QThread):
    progress = Signal(int)        # percent 0–100
    finished = Signal(str)        # success message
    error = Signal(str)           # error message
    file_done = Signal(str)       # filename just completed

    def __init__(self, input_paths: list[str], output_format: str, output_dir: str):
        super().__init__()
        self.input_paths = input_paths
        self.output_format = output_format.lstrip(".")
        self.output_dir = output_dir

    def run(self):
        reader_fn = get_reader(self._input_ext())
        writer_fn = get_writer(self.output_format)
        total = len(self.input_paths)

        for i, input_path in enumerate(self.input_paths):
            try:
                records = reader_fn(input_path)
                base = os.path.splitext(os.path.basename(input_path))[0]
                output_path = self._unique_path(base)
                writer_fn(records, output_path)
                self.file_done.emit(os.path.basename(output_path))
                self.progress.emit(int((i + 1) / total * 100))
            except Exception as e:
                self.error.emit(f"{os.path.basename(input_path)}: {e}")
                # Continue with next file in batch mode

        if total > 0:
            self.finished.emit(f"完成 {total} 个文件转换")
        else:
            self.finished.emit("无文件需要转换")

    def _input_ext(self):
        return os.path.splitext(self.input_paths[0])[1].lstrip(".")

    def _unique_path(self, base_name: str) -> str:
        ext = self.output_format
        candidate = os.path.join(self.output_dir, f"{base_name}.{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter = 1
        while True:
            candidate = os.path.join(self.output_dir, f"{base_name}_{counter}.{ext}")
            if not os.path.exists(candidate):
                return candidate
            counter += 1
```

- [ ] **Step 2: Commit**

```bash
git add src/worker.py
git commit -m "feat: add QThread conversion worker"
```

---

### Task 11: Dark Theme Stylesheet

**Files:**
- Create: `src/ui/theme.qss`

- [ ] **Step 1: Write dark theme QSS**

```css
/* src/ui/theme.qss */
QMainWindow {
    background-color: #23272a;
}

QWidget {
    background-color: #23272a;
    color: #dcddde;
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 13px;
}

QLabel {
    background: transparent;
    color: #b9bbbe;
}

QLabel#title {
    font-size: 15px;
    font-weight: bold;
    color: #ffffff;
    padding: 6px 0;
}

QLabel#status {
    color: #72767d;
    font-size: 11px;
}

QLineEdit {
    background-color: #2c2f33;
    border: 1px solid #444950;
    border-radius: 6px;
    padding: 8px 10px;
    color: #dcddde;
    font-size: 12px;
}

QLineEdit:focus {
    border-color: #5865F2;
}

QLineEdit[readOnly="true"] {
    color: #72767d;
    background-color: #2c2f33;
}

QPushButton {
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: bold;
    border: none;
}

QPushButton#browse_btn {
    background-color: #444950;
    color: #dcddde;
}

QPushButton#browse_btn:hover {
    background-color: #555a63;
}

QPushButton#single_btn {
    background-color: #5865F2;
    color: white;
    padding: 10px 16px;
}

QPushButton#single_btn:hover {
    background-color: #4752c4;
}

QPushButton#single_btn:disabled {
    background-color: #3e4280;
    color: #888;
}

QPushButton#batch_btn {
    background-color: #3BA55C;
    color: white;
    padding: 10px 16px;
}

QPushButton#batch_btn:hover {
    background-color: #2d8a47;
}

QPushButton#batch_btn:disabled {
    background-color: #1e5c30;
    color: #888;
}

QComboBox {
    background-color: #2c2f33;
    border: 1px solid #444950;
    border-radius: 6px;
    padding: 8px 10px;
    color: #dcddde;
    font-size: 12px;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #5865F2;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox::down-arrow {
    image: none;
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #2c2f33;
    border: 1px solid #444950;
    color: #dcddde;
    selection-background-color: #5865F2;
    selection-color: white;
    outline: none;
}

QProgressBar {
    background-color: #2c2f33;
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #5865F2;
    border-radius: 3px;
}

QFrame#header {
    background-color: #1e2124;
    border-bottom: 1px solid #333;
    padding: 12px 16px;
}

QScrollArea {
    border: none;
    background: transparent;
}
```

- [ ] **Step 2: Commit**

```bash
git add src/ui/theme.qss
git commit -m "feat: add dark theme QSS stylesheet"
```

---

### Task 12: Main Window UI

**Files:**
- Create: `src/ui/main_window.py`

- [ ] **Step 1: Write the main window**

```python
# src/ui/main_window.py
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QProgressBar, QFileDialog, QFrame,
)
from PySide6.QtCore import Qt
from src.converters.registry import get_output_formats, supports_extension
from src.worker import ConversionWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAN 报文格式转换工具")
        self.setFixedSize(440, 380)
        self._selected_files = []
        self._worker = None
        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame(objectName="header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 10, 16, 10)
        title = QLabel("CAN 报文格式转换工具", objectName="title")
        header_layout.addWidget(title)
        layout.addWidget(header)

        # Body
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 16, 20, 16)
        body_layout.setSpacing(12)

        # Input file
        body_layout.addWidget(QLabel("输入文件 (.blf / .mf4 / .asc)"))
        file_row = QHBoxLayout()
        self.input_field = QLineEdit(readOnly=True)
        self.input_field.setPlaceholderText("未选择文件")
        file_row.addWidget(self.input_field, 1)
        browse_btn = QPushButton("浏览", objectName="browse_btn")
        browse_btn.clicked.connect(self._browse_input)
        file_row.addWidget(browse_btn)
        body_layout.addLayout(file_row)

        # Output format
        body_layout.addWidget(QLabel("输出格式"))
        self.format_combo = QComboBox()
        self.format_combo.addItems([".blf", ".mf4", ".asc", ".csv"])
        body_layout.addWidget(self.format_combo)

        # Output directory
        body_layout.addWidget(QLabel("输出目录"))
        dir_row = QHBoxLayout()
        self.output_field = QLineEdit(readOnly=True)
        self.output_field.setPlaceholderText("未选择目录")
        dir_row.addWidget(self.output_field, 1)
        dir_browse_btn = QPushButton("浏览", objectName="browse_btn")
        dir_browse_btn.clicked.connect(self._browse_output_dir)
        dir_row.addWidget(dir_browse_btn)
        body_layout.addLayout(dir_row)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self.single_btn = QPushButton("单文件转换", objectName="single_btn")
        self.single_btn.clicked.connect(self._convert_single)
        btn_row.addWidget(self.single_btn, 1)
        self.batch_btn = QPushButton("批量转换", objectName="batch_btn")
        self.batch_btn.clicked.connect(self._convert_batch)
        btn_row.addWidget(self.batch_btn, 1)
        body_layout.addLayout(btn_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        body_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("就绪", objectName="status")
        self.status_label.setAlignment(Qt.AlignCenter)
        body_layout.addWidget(self.status_label)

        body_layout.addStretch()
        layout.addWidget(body)

    def _apply_theme(self):
        qss_path = os.path.join(os.path.dirname(__file__), "theme.qss")
        with open(qss_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def _browse_input(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择输入文件", "",
            "总线报文文件 (*.blf *.asc *.mf4);;所有文件 (*)"
        )
        if files:
            self._selected_files = files
            if len(files) == 1:
                self.input_field.setText(files[0])
            else:
                self.input_field.setText(f"已选择 {len(files)} 个文件")
            # Update output format dropdown to exclude input extension
            input_ext = os.path.splitext(files[0])[1].lstrip(".")
            self._update_format_combo(input_ext)

    def _browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if directory:
            self.output_field.setText(directory)

    def _update_format_combo(self, input_ext):
        self.format_combo.clear()
        formats = get_output_formats(input_ext)
        display = [f".{f}" for f in formats]
        self.format_combo.addItems(display)

    def _convert_single(self):
        if not self._selected_files:
            self.status_label.setText("请先选择输入文件")
            return
        if not self.output_field.text():
            self.status_label.setText("请先选择输出目录")
            return
        self._start_conversion([self._selected_files[0]])

    def _convert_batch(self):
        if not self._selected_files:
            self.status_label.setText("请先选择输入文件")
            return
        if not self.output_field.text():
            self.status_label.setText("请先选择输出目录")
            return
        self._start_conversion(self._selected_files)

    def _start_conversion(self, file_paths):
        out_fmt = self.format_combo.currentText().lstrip(".")
        out_dir = self.output_field.text()

        self._set_controls_enabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("转换中...")

        self._worker = ConversionWorker(file_paths, out_fmt, out_dir)
        self._worker.progress.connect(self._on_progress)
        self._worker.file_done.connect(self._on_file_done)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _set_controls_enabled(self, enabled):
        self.single_btn.setEnabled(enabled)
        self.batch_btn.setEnabled(enabled)

    def _on_progress(self, value):
        self.progress_bar.setValue(value)

    def _on_file_done(self, filename):
        self.status_label.setText(f"已完成: {filename}")

    def _on_error(self, message):
        self.status_label.setText(f"错误: {message}")

    def _on_finished(self, message):
        self.status_label.setText(message)
        self._set_controls_enabled(True)
        self._worker = None
```

- [ ] **Step 2: Verify the file has no import errors**

Run: `python -c "from src.ui.main_window import MainWindow; print('OK')"`
Expected: OK (or import error about PySide6 if not installed)

- [ ] **Step 3: Commit**

```bash
git add src/ui/main_window.py
git commit -m "feat: add main window UI with all widgets and signal wiring"
```

---

### Task 13: Application Entry Point

**Files:**
- Create: `src/main.py`

- [ ] **Step 1: Write entry point**

```python
# src/main.py
import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CAN-Converter")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test launching the app**

Run: `python src/main.py`
Expected: Window appears with dark theme, all widgets visible. Close manually.

- [ ] **Step 3: Commit**

```bash
git add src/main.py
git commit -m "feat: add application entry point"
```

---

### Task 14: PyInstaller Packaging

**Files:**
- Create: `build.spec`

- [ ] **Step 1: Write PyInstaller spec**

```python
# build.spec
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/ui/theme.qss', 'src/ui'),
    ],
    hiddenimports=[
        'can',
        'can.io.blf',
        'can.io.asc',
        'asammdf',
        'pandas',
        'numpy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CAN-Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
```

- [ ] **Step 2: Build the exe**

Run: `pyinstaller build.spec`
Expected: Build succeeds, produces `dist/CAN-Converter.exe`

- [ ] **Step 3: Test the exe**

Run: `dist/CAN-Converter.exe`
Expected: Window opens, no console window, dark theme works.

- [ ] **Step 4: Commit**

```bash
git add build.spec
git commit -m "feat: add PyInstaller spec for single .exe packaging"
```

---

### Task 15: Final Verification

- [ ] **Step 1: Run full test suite one final time**

Run: `pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 2: Manual smoke test checklist**
  - [ ] Launch app → dark theme renders
  - [ ] Browse → select a .blf file → path shows in input field
  - [ ] Output format dropdown updates (excludes input extension)
  - [ ] Browse output directory → path shows
  - [ ] Single conversion with a real BLF → progress bar moves → status shows "完成"
  - [ ] Batch conversion with 2+ files → each file processed
  - [ ] Verify output files exist with correct extension
  - [ ] Verify CSV output has correct columns and hex data format
  - [ ] Close app cleanly

- [ ] **Step 3: Commit final verification**

```bash
git add -A
git commit -m "chore: final test suite verification, all tests passing"
```

---

## Spec Coverage Review

| Spec Requirement | Covered By |
|-----------------|------------|
| 9 conversion paths | Tasks 4-8 (BLF/ASC/MF4 readers + writers + integration) |
| CSV write-only (no CSV → X) | Task 7 (CSVWriter only, no CSVReader) |
| FrameRecord internal model | Task 2 |
| Converter registry + dispatch | Task 3 |
| Dark theme QSS | Task 11 |
| Vertical stack layout, all widgets | Task 12 |
| Single file conversion button | Task 12 (`_convert_single`) |
| Batch conversion button | Task 12 (`_convert_batch`) |
| Progress bar + status | Task 12 (QProgressBar + status_label) |
| QThread async conversion | Task 10 |
| Output filename collision (append _1, _2) | Task 10 (`_unique_path`) |
| CAN + LIN support | Task 2 (FrameRecord.is_lin), Tasks 4-6 |
| PyInstaller single .exe | Task 14 |
| Clean Windows deployment | Task 14 (--onefile --windowed) |

No gaps. All spec requirements have corresponding tasks.
