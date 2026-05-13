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
