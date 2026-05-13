import pytest
from dataclasses import FrozenInstanceError
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
    with pytest.raises(FrozenInstanceError):
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
