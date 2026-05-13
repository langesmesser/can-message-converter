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
