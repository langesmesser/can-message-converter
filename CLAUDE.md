# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

```bash
# 运行全部测试（97 条，必须全过才能打包）
python -m pytest tests/ -v

# 运行单个测试文件
python -m pytest tests/test_themes.py -v

# 运行单个测试用例
python -m pytest tests/test_base.py::test_framerecord_immutable -v

# 启动 GUI（开发调试）
python src/main.py

# 打包 .exe（构建前确保 97 条测试全过）
pyinstaller build.spec --noconfirm

# 清理构建残留
rm -rf build/ .pytest_cache/ **/__pycache__/
```

## 架构总览

**核心模式：内部中间表示（IR）统一转换**

所有格式互转通过 `FrameRecord`（冻结数据类）作为中间格式。每种格式只需实现 Reader（解析为 FrameRecord 列表）和 Writer（将 FrameRecord 列表写出），即可覆盖全部 N×M 转换路径。

```
源文件 → Reader.from_file() → list[FrameRecord] → Writer.to_file() → 目标文件
```

**支持的转换路径：**

| 输入 | 输出（常规下拉框） | 一键转换 |
|------|-------------------|---------|
| .blf | .mf4 / .asc / .csv | — |
| .mf4 | .blf / .asc / .csv | — |
| .asc | .blf / .mf4 / .csv | — |
| .txt | .asc | .xlsx |

TXT 和 CSV 仅读/仅写，不能作为反向转换目标。XLSX 是只写格式，仅通过"错误报文一键转换"按钮触发（TXT 输入时可用）。

**转换器注册表（registry.py）：** 所有 Reader/Writer 以函数指针形式注册在 `READERS` / `WRITERS` 字典中，新增格式只需在此添加入口。`_RESTRICTED_OUTPUT` 控制特定输入格式的可用输出列表。

**GUI 架构：** PySide6 主窗口 → ConversionWorker(QThread) → ThreadPoolExecutor(4 线程) 并行转换。Worker 通过 Qt Signal（progress/file_done/error/finished）向 UI 线程报告状态。写入阶段重定向 stderr 到 `os.devnull`（`os.dup2`），抑制 python-can C 扩展对非标准 CAN FD DLC 的 fprintf 警告。

**主题系统（src/ui/themes.py）：** 8 套配色家族 × 深色/浅色 = 16 个变体。轮盘顺序：Notion → Apple → Discord → Ocean → Forest → Sunset → Nord → Solarized。颜色 + 样式 token 定义为 Python dict，通过 `build_qss()` 动态生成 QSS 并 `setStyleSheet()` 应用。Header 右侧轮盘按钮显示当前主题名，☽/☀ 按钮独立切换深色/浅色模式。

Notion 使用独立样式 token（`_NOTION_STYLE`：8px 圆角、500 字重、4px 进度条），其余 7 套共享 `_STYLE`（6px 圆角、bold 字重、6px 进度条）。静态 QSS 文件（theme.qss / theme_light.qss）保留在 datas 中但未被代码引用（所有样式由 `build_qss()` 动态生成）。

**布局（src/ui/main_window.py）：** Card 式 3 分区——输入文件 / 输出配置 / 操作+进度。QFrame#card 容器仅设 `background-color` + `border`，无 `border-radius` 和 `padding`（原因见下文）。内边距全部由 layout 的 `setContentsMargins` 控制。

## Qt QSS 关键限制（踩过的坑）

- **不要在 QFrame 父容器上设 `border-radius` 或 `padding`**——会导致子控件文字渲染异常（残缺、模糊或消失）。卡片视觉区分通过 `bg_secondary` + `border` 实现，间距全部用 layout 控制。
- **不要用 `QLabel.setStyleSheet()` 设局部样式**——它会完全替换全局 QSS，导致 label 失去 `color`/`font-family` 等继承属性。改字重用 `QFont.setWeight()`。
- **QSS font-family 只用 `"FontName"` 格式**（如 `"Segoe UI", "Microsoft YaHei", sans-serif`），不要用 `-apple-system`、`system-ui` 等 Web CSS 值，Qt 解析器不识别。

## 关键实现细节

**MF4 读取双策略：** 真实采集设备的 MF4 使用 `CAN_DataFrame` 复合结构体（samples 是结构化 numpy 数组），需要 `mdf.get("CAN_DataFrame", group=gi, index=1)` 方式读取；本工具写出的 MF4 使用扁平独立通道（13 个独立 Signal）。Reader 按优先级自动检测。

**CAN FD 支持：** `FrameRecord.is_fd` 字段标识 CAN FD 帧。MF4 Reader 通过 DLC > 8 判定。python-can 库对写入时的 DLC 编码做规范化验证，Worker 通过 `os.dup2` 重定向 stderr 到 `os.devnull` 抑制这些无害的 C 扩展 fprintf 警告。

**TXT 读取：** 仅读不写（输出通过 ASC 或 XLSX）。解析空格/制表符分隔的格式 A（timestamp [channel] id data_bytes...）。channel 列自动检测（值 0-15 视为通道号）。ID 可带或不带 0x 前缀。非数值开头的行视为注释跳过。CAN FD 数据长度自动映射为标准 DLC 编码（12→9, 16→10, ...）。

**XLSX 写入：** TXT → XLSX 一键转换，输出列：时间戳 / 通道 / ID(HEX) / 数据(HEX)。通过 openpyxl 写入，首行冻结 + 自动筛选。

**BLF/ASC 写入注意：** python-can 4.x 的 BLFWriter 不支持 `is_lin_message` 和 `bus` 参数。Reader 端使用 `getattr(..., default)` 安全读取可选属性。

**PyInstaller 打包：** `build.spec` 使用 `--onefile --windowed`，`strip=False`（Windows 无 strip 命令），`upx=True`。通过 `excludes` 排除 torch、transformers、scipy、matplotlib、flask、jupyter、playwright 等大型/无关库。`hiddenimports` 确保 `can.io.blf`、`can.io.asc`、`src.ui.themes` 等隐式导入被包含。QSS 文件通过 `datas` 打包。

**关键依赖保留：** asammdf 核心依赖 `numexpr`、`sympy`、`lz4`、`zstd`、`deflate`、`isal`、`snappy`、`cryptography`、`fsspec`、`canmatrix` 等不可排除。

**文件名策略：** 批量转换保持原文件名不变，仅改扩展名。
