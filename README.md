# CAN Message Converter

- [Usage](#usage)
- [Getting Started](#getting-started--documentation)
- [Developing](#developing)
- [License](#license)

---

CAN Message Converter is a free desktop tool for converting CAN bus log files across 6 formats — no commercial software required.

The key features of CAN Message Converter are:

- **Infrastructure as IR**: All format conversion passes through a unified `FrameRecord` intermediate representation. Each format only needs a Reader and a Writer — 4 inputs × 5 outputs covered by 9 modules instead of 20 point-to-point adapters.
- **Execution Plans**: Batch conversion runs on a 4-thread parallel engine (`QThread` + `ThreadPoolExecutor`) with real-time progress reporting via Qt signals, keeping the UI responsive.
- **Resource Graph**: Supported input formats are BLF (Vector binary), MF4/MDF4 (ASAM standard), ASC (Vector ASCII), and TXT (raw text dumps). Output targets include BLF, MF4, ASC, CSV, and XLSX — covering the full matrix of 12+ conversion paths.
- **State Management**: 8 theme families × light/dark mode = 16 visual variants, with QSS generated dynamically from Python token dictionaries. All state is local — no cloud dependencies, no telemetry.

For more information, refer to the [architecture overview](CLAUDE.md).

---

## Usage

### GUI

```bash
python src/main.py
```

Drag and drop input files into the top card, select the desired output format from the dropdown, and click **Convert**. Progress is shown per file in real time.

**Quick workflow:**

1. Drop `.blf`, `.mf4`, `.asc`, or `.txt` files into the input area
2. Choose the output format (`.blf` / `.mf4` / `.asc` / `.csv`)
3. Click **Convert** — output files land alongside the originals

**One-click TXT → XLSX:** When the input is `.txt`, the **Convert to XLSX** button is available, producing a spreadsheet with columns: timestamp, channel, ID (hex), and data (hex).

### Build .exe

```bash
python -m pytest tests/ -v    # all 97 tests must pass
pyinstaller build.spec --noconfirm
```

### Supported formats

| Input | Output |
|-------|--------|
| `.blf` | `.mf4` / `.asc` / `.csv` |
| `.mf4` | `.blf` / `.asc` / `.csv` |
| `.asc` | `.blf` / `.mf4` / `.csv` |
| `.txt` | `.asc` / `.xlsx` |

---

## Getting Started & Documentation

Documentation is available in the [CLAUDE.md](CLAUDE.md) file, which covers:

- [Common commands](CLAUDE.md) — run tests, launch the GUI, build the `.exe`
- [Architecture overview](CLAUDE.md) — IR pattern, converter registry, supported paths
- [Qt QSS pitfalls](CLAUDE.md) — documented anti-patterns discovered during development

If you're new to CAN bus data, the tool handles protocol details automatically — CAN FD DLC encoding, MF4 dual-strategy reading (composite struct vs. flat channels), and python-can C extension warnings are all managed internally.

## Developing

This repository contains the full source for the CAN Message Converter GUI application.

- [CLAUDE.md](CLAUDE.md) for build commands and architecture
- [GitHub Issues](https://github.com/langesmesser/can-message-converter/issues) for bug reports and feature requests

## License

[MIT](LICENSE)
