[English](README.md)

# CAN Message Converter

- [使用说明](#使用说明)
- [开发](#开发)
- [许可证](#许可证)

---

CAN Message Converter 是一款免费的 CAN 总线报文格式转换桌面工具，覆盖 6 种格式 — 无需商业软件。

核心特性：

- **IR 中间表示架构**：所有格式转换通过统一的 `FrameRecord` 中间表示进行。每种格式只需实现 Reader 和 Writer — 4 种输入 × 5 种输出仅需 9 个模块，而非 20 个端到端适配器。
- **并行执行引擎**：批量转换运行在 4 线程并行引擎上（`QThread` + `ThreadPoolExecutor`），通过 Qt 信号实时上报进度，UI 始终保持响应。
- **全格式覆盖**：支持输入格式 BLF（Vector 二进制）、MF4/MDF4（ASAM 标准）、ASC（Vector ASCII）和 TXT（原始文本 dump）。输出格式包括 BLF、MF4、ASC、CSV 和 XLSX — 覆盖 12+ 条转换路径。
- **本地优先**：8 套主题 × 深色/浅色模式 = 16 种视觉变体，QSS 由 Python token 字典动态生成。完全本地运行 — 无云端依赖，无遥测。

---

## 使用说明

### 图形界面

```bash
python src/main.py
```

将输入文件拖入上方卡片区域，在下拉框中选择目标格式，点击 **Convert** 即可。进度按文件实时显示。

**快速流程：**

1. 将 `.blf`、`.mf4`、`.asc` 或 `.txt` 文件拖入输入区域
2. 选择输出格式（`.blf` / `.mf4` / `.asc` / `.csv`）
3. 点击 **Convert** — 输出文件生成在原文件同目录

**一键 TXT → XLSX：** 输入为 `.txt` 时，**Convert to XLSX** 按钮可用，产出包含时间戳、通道、ID(HEX)、数据(HEX) 列的电子表格。

### 打包 .exe

```bash
python -m pytest tests/ -v    # 97 条测试必须全过
pyinstaller build.spec --noconfirm
```

### 格式支持矩阵

| 输入 | 输出 |
|------|------|
| `.blf` | `.mf4` / `.asc` / `.csv` |
| `.mf4` | `.blf` / `.asc` / `.csv` |
| `.asc` | `.blf` / `.mf4` / `.csv` |
| `.txt` | `.asc` / `.xlsx` |

---

## 开发

本仓库包含 CAN Message Converter 的完整源代码。

- 运行 `python -m pytest tests/ -v` 执行 97 条测试
- 运行 `python src/main.py` 启动 GUI
- 运行 `pyinstaller build.spec --noconfirm` 构建单文件 .exe
- [GitHub Issues](https://github.com/langesmesser/can-message-converter/issues) 用于缺陷报告和功能请求

## 许可证

[MIT](LICENSE)
