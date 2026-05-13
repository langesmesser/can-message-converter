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
