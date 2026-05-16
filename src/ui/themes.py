"""
主题系统：8 套配色方案 — 切换主题布局零变化。

Notion: 独立样式 token（8px 圆角、500 字重、4px 进度条）。
Apple / Discord / Ocean / Forest / Sunset / Nord / Solarized: 共享统一样式。
深色 / 浅色独立切换，主题轮盘循环切换配色家族。
默认使用 Notion 配色。
"""

# ── 统一样式 token（6 套已有主题共用） ──

_STYLE = {
    "font_family": '"Segoe UI", "Microsoft YaHei", sans-serif',
    "font_size": "13px",
    "border_radius": "6px",
    "progress_height": "6px",
    "progress_radius": "3px",
    "button_font_weight": "bold",
}

# ── Notion 专属样式 token ──

_NOTION_STYLE = {
    "font_family": '"Segoe UI", "Microsoft YaHei", sans-serif',
    "font_size": "13px",
    "border_radius": "8px",
    "progress_height": "4px",
    "progress_radius": "2px",
    "button_font_weight": "500",
}

# ── QSS 模板 ──

_QSS_TEMPLATE = """QMainWindow {{
    background-color: {bg_primary};
}}

QWidget {{
    background-color: {bg_primary};
    color: {text_primary};
    font-family: {font_family};
    font-size: {font_size};
}}

QLabel {{
    background: transparent;
    color: {text_secondary};
}}

QLabel#title {{
    font-size: 15px;
    font-weight: 600;
    color: {text_primary};
    padding: 6px 0;
}}

QLabel#section_label {{
    font-size: 13px;
    font-weight: 600;
    color: {text_primary};
}}

QLabel#status {{
    color: {text_muted};
    font-size: 11px;
}}

QLineEdit {{
    background-color: {bg_secondary};
    border: 1px solid {border};
    border-radius: {border_radius};
    padding: 8px 10px;
    color: {text_primary};
    font-size: 12px;
}}

QLineEdit:focus {{
    border-color: {accent};
}}

QLineEdit[readOnly="true"] {{
    color: {text_secondary};
    background-color: {bg_secondary};
}}

QPushButton {{
    border-radius: {border_radius};
    padding: 8px 16px;
    font-size: 12px;
    font-weight: {button_font_weight};
    border: none;
}}

QPushButton#browse_btn {{
    background-color: {btn_browse};
    color: {text_primary};
}}

QPushButton#browse_btn:hover {{
    background-color: {btn_browse_hover};
}}

QPushButton#convert_btn {{
    background-color: {accent};
    color: white;
    padding: 10px 18px;
}}

QPushButton#convert_btn:hover {{
    background-color: {accent_hover};
}}

QPushButton#convert_btn:disabled {{
    background-color: {btn_disabled_bg};
    color: {btn_disabled_text};
}}

QPushButton#xlsx_btn {{
    background-color: {success};
    color: white;
    padding: 10px 18px;
}}

QPushButton#xlsx_btn:hover {{
    background-color: {success_hover};
}}

QPushButton#xlsx_btn:disabled {{
    background-color: {btn_disabled_bg};
    color: {btn_disabled_text};
}}

QPushButton#theme_cycle_btn {{
    background-color: {btn_theme_bg};
    color: {btn_theme_text};
    font-size: 12px;
    font-weight: {button_font_weight};
    padding: 6px 14px;
    border: 1px solid {border};
    border-radius: {border_radius};
}}

QPushButton#theme_cycle_btn:hover {{
    background-color: {btn_theme_hover};
}}

QPushButton#theme_btn {{
    background-color: {btn_theme_bg};
    color: {btn_theme_text};
    font-size: 16px;
    padding: 4px 10px;
    border: 1px solid {border};
    border-radius: 8px;
}}

QPushButton#theme_btn:hover {{
    background-color: {btn_theme_hover};
}}

QComboBox {{
    background-color: {bg_secondary};
    border: 1px solid {border};
    border-radius: {border_radius};
    padding: 8px 10px;
    color: {text_primary};
    font-size: 12px;
    min-height: 20px;
}}

QComboBox:hover {{
    border-color: {accent};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}

QComboBox::down-arrow {{
    image: none;
    border: none;
}}

QComboBox QAbstractItemView {{
    background-color: {bg_secondary};
    border: 1px solid {border};
    color: {text_primary};
    selection-background-color: {accent};
    selection-color: white;
    outline: none;
}}

QFrame#header {{
    background-color: {header_bg};
    border-bottom: 1px solid {header_border};
    padding: 12px 16px;
}}

QFrame#card {{
    background-color: {bg_secondary};
    border: 1px solid {border};
}}

QProgressBar {{
    background-color: {progress_bg};
    border: none;
    border-radius: {progress_radius};
    height: {progress_height};
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {accent};
    border-radius: {progress_radius};
}}

QScrollArea {{
    border: none;
    background: transparent;
}}
"""

# ── 8 套配色方案 ──
# Notion 使用独立 _NOTION_STYLE, 其余 7 套共享 _STYLE

THEME_FAMILIES = {
    # ── Notion ──
    # 浅色: canvas/surface/hairline 体系; 深色: 参考 Notion 桌面 app 暗色模式
    "Notion": {
        "dark": {
            **_NOTION_STYLE,
            "bg_primary": "#1b1b1a",
            "bg_secondary": "#252524",
            "text_primary": "#e6e5e3",
            "text_secondary": "#b4b3b1",
            "text_muted": "#797876",
            "accent": "#5645d4",
            "accent_hover": "#4534b3",
            "border": "#333331",
            "btn_browse": "#2f2f2e",
            "btn_browse_hover": "#3a3a39",
            "btn_disabled_bg": "#353540",
            "btn_disabled_text": "#666",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#b4b3b1",
            "btn_theme_hover": "#2f2f2e",
            "success": "#1aae39",
            "success_hover": "#158f2e",
            "progress_bg": "#252524",
            "header_bg": "#131312",
            "header_border": "#333331",
        },
        "light": {
            **_NOTION_STYLE,
            "bg_primary": "#ffffff",
            "bg_secondary": "#f6f5f4",
            "text_primary": "#1a1a1a",
            "text_secondary": "#5d5b54",
            "text_muted": "#a4a097",
            "accent": "#5645d4",
            "accent_hover": "#4534b3",
            "border": "#e5e3df",
            "btn_browse": "#f0eeec",
            "btn_browse_hover": "#e5e3df",
            "btn_disabled_bg": "#e5e3df",
            "btn_disabled_text": "#bbb8b1",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#5d5b54",
            "btn_theme_hover": "#f6f5f4",
            "success": "#1aae39",
            "success_hover": "#158f2e",
            "progress_bg": "#f0eeec",
            "header_bg": "#fafaf9",
            "header_border": "#e5e3df",
        },
    },
    # ── Apple ──
    # 浅色: canvas-parchment #f5f5f7 + Action Blue #0066cc
    # 深色: 纯黑表面 + 深灰卡片 + #2997ff 蓝
    "Apple": {
        "dark": {
            **_STYLE,
            "bg_primary": "#000000",
            "bg_secondary": "#1d1d1f",
            "text_primary": "#f5f5f7",
            "text_secondary": "#cccccc",
            "text_muted": "#7a7a7a",
            "accent": "#2997ff",
            "accent_hover": "#0071e3",
            "border": "#333333",
            "btn_browse": "#2a2a2c",
            "btn_browse_hover": "#3a3a3c",
            "btn_disabled_bg": "#2a2a2c",
            "btn_disabled_text": "#555",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#cccccc",
            "btn_theme_hover": "#2a2a2c",
            "success": "#30d158",
            "success_hover": "#28b84a",
            "progress_bg": "#1d1d1f",
            "header_bg": "#0a0a0a",
            "header_border": "#333333",
        },
        "light": {
            **_STYLE,
            "bg_primary": "#f5f5f7",
            "bg_secondary": "#fafafc",
            "text_primary": "#1d1d1f",
            "text_secondary": "#333333",
            "text_muted": "#7a7a7a",
            "accent": "#0066cc",
            "accent_hover": "#0071e3",
            "border": "#e0e0e0",
            "btn_browse": "#ebebed",
            "btn_browse_hover": "#e0e0e0",
            "btn_disabled_bg": "#e0e0e0",
            "btn_disabled_text": "#999",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#333333",
            "btn_theme_hover": "#ebebed",
            "success": "#30d158",
            "success_hover": "#28b84a",
            "progress_bg": "#ebebed",
            "header_bg": "#fafafc",
            "header_border": "#e0e0e0",
        },
    },
    # ── Discord ──
    "Discord": {
        "dark": {
            **_STYLE,
            "bg_primary": "#23272a",
            "bg_secondary": "#2c2f33",
            "text_primary": "#dcddde",
            "text_secondary": "#b9bbbe",
            "text_muted": "#72767d",
            "accent": "#5865F2",
            "accent_hover": "#4752c4",
            "border": "#444950",
            "btn_browse": "#444950",
            "btn_browse_hover": "#555a63",
            "btn_disabled_bg": "#3e4280",
            "btn_disabled_text": "#888",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#b9bbbe",
            "btn_theme_hover": "#3a3d42",
            "success": "#3ba55c",
            "success_hover": "#2d8a47",
            "progress_bg": "#2c2f33",
            "header_bg": "#1e2124",
            "header_border": "#333",
        },
        "light": {
            **_STYLE,
            "bg_primary": "#ede9e2",
            "bg_secondary": "#f5f2ec",
            "text_primary": "#37352f",
            "text_secondary": "#6b6358",
            "text_muted": "#9b9487",
            "accent": "#5a8db5",
            "accent_hover": "#4d7d9f",
            "border": "#d9d3c9",
            "btn_browse": "#e0dbd1",
            "btn_browse_hover": "#d4cec3",
            "btn_disabled_bg": "#c5c0b5",
            "btn_disabled_text": "#9b9487",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#6b6358",
            "btn_theme_hover": "#e0dbd1",
            "success": "#4a9c6c",
            "success_hover": "#3d8259",
            "progress_bg": "#e0dbd1",
            "header_bg": "#e5e0d7",
            "header_border": "#d9d3c9",
        },
    },
    # ── Ocean ──
    "Ocean": {
        "dark": {
            **_STYLE,
            "bg_primary": "#0d1117",
            "bg_secondary": "#161b22",
            "text_primary": "#c9d1d9",
            "text_secondary": "#8b949e",
            "text_muted": "#484f58",
            "accent": "#58a6ff",
            "accent_hover": "#1f6feb",
            "border": "#30363d",
            "btn_browse": "#21262d",
            "btn_browse_hover": "#30363d",
            "btn_disabled_bg": "#1c3350",
            "btn_disabled_text": "#666",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#8b949e",
            "btn_theme_hover": "#21262d",
            "success": "#3fb950",
            "success_hover": "#2ea043",
            "progress_bg": "#161b22",
            "header_bg": "#010409",
            "header_border": "#21262d",
        },
        "light": {
            **_STYLE,
            "bg_primary": "#ebeff3",
            "bg_secondary": "#f4f6f9",
            "text_primary": "#24292f",
            "text_secondary": "#57606a",
            "text_muted": "#8c959f",
            "accent": "#0969da",
            "accent_hover": "#0550ae",
            "border": "#c8d2dc",
            "btn_browse": "#dfe4ea",
            "btn_browse_hover": "#c8d2dc",
            "btn_disabled_bg": "#c0c9d3",
            "btn_disabled_text": "#8c959f",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#57606a",
            "btn_theme_hover": "#dfe4ea",
            "success": "#2da44e",
            "success_hover": "#238636",
            "progress_bg": "#dfe4ea",
            "header_bg": "#e3e8ee",
            "header_border": "#c8d2dc",
        },
    },
    # ── Forest ──
    "Forest": {
        "dark": {
            **_STYLE,
            "bg_primary": "#1a1e1b",
            "bg_secondary": "#232925",
            "text_primary": "#d4d9d3",
            "text_secondary": "#a0a9a0",
            "text_muted": "#5c665c",
            "accent": "#6cbe7a",
            "accent_hover": "#4da15d",
            "border": "#3a453b",
            "btn_browse": "#2d352e",
            "btn_browse_hover": "#3a453b",
            "btn_disabled_bg": "#2e4d2e",
            "btn_disabled_text": "#666",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#a0a9a0",
            "btn_theme_hover": "#2d352e",
            "success": "#57ab5f",
            "success_hover": "#448c4b",
            "progress_bg": "#232925",
            "header_bg": "#141715",
            "header_border": "#2d352e",
        },
        "light": {
            **_STYLE,
            "bg_primary": "#edf1eb",
            "bg_secondary": "#f5f7f4",
            "text_primary": "#2d3a2d",
            "text_secondary": "#5c6b5c",
            "text_muted": "#8fa08f",
            "accent": "#3d8c4a",
            "accent_hover": "#2d6e38",
            "border": "#cdd8ca",
            "btn_browse": "#dfe5dc",
            "btn_browse_hover": "#cdd8ca",
            "btn_disabled_bg": "#c4cec1",
            "btn_disabled_text": "#8fa08f",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#5c6b5c",
            "btn_theme_hover": "#dfe5dc",
            "success": "#3d8c4a",
            "success_hover": "#2d6e38",
            "progress_bg": "#dfe5dc",
            "header_bg": "#e3e9e0",
            "header_border": "#cdd8ca",
        },
    },
    # ── Sunset ──
    "Sunset": {
        "dark": {
            **_STYLE,
            "bg_primary": "#1e1a1d",
            "bg_secondary": "#282326",
            "text_primary": "#e0d7d9",
            "text_secondary": "#b8a9ae",
            "text_muted": "#6e6066",
            "accent": "#e8845e",
            "accent_hover": "#c96e4a",
            "border": "#453b3e",
            "btn_browse": "#352d30",
            "btn_browse_hover": "#453b3e",
            "btn_disabled_bg": "#4d3535",
            "btn_disabled_text": "#666",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#b8a9ae",
            "btn_theme_hover": "#352d30",
            "success": "#d4845e",
            "success_hover": "#b86e4b",
            "progress_bg": "#282326",
            "header_bg": "#171416",
            "header_border": "#352d30",
        },
        "light": {
            **_STYLE,
            "bg_primary": "#f2ece4",
            "bg_secondary": "#f9f5ef",
            "text_primary": "#3d322b",
            "text_secondary": "#7a6860",
            "text_muted": "#b0a098",
            "accent": "#d4794a",
            "accent_hover": "#b8603a",
            "border": "#dbcec2",
            "btn_browse": "#e8dbcf",
            "btn_browse_hover": "#dbcec2",
            "btn_disabled_bg": "#d4c7bb",
            "btn_disabled_text": "#b0a098",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#7a6860",
            "btn_theme_hover": "#e8dbcf",
            "success": "#c07d5a",
            "success_hover": "#a06848",
            "progress_bg": "#e8dbcf",
            "header_bg": "#ebe2d6",
            "header_border": "#dbcec2",
        },
    },
    # ── Nord ──
    "Nord": {
        "dark": {
            **_STYLE,
            "bg_primary": "#2e3440",
            "bg_secondary": "#3b4252",
            "text_primary": "#d8dee9",
            "text_secondary": "#e5e9f0",
            "text_muted": "#616e88",
            "accent": "#88c0d0",
            "accent_hover": "#8fbcbb",
            "border": "#434c5e",
            "btn_browse": "#434c5e",
            "btn_browse_hover": "#4c566a",
            "btn_disabled_bg": "#3b4658",
            "btn_disabled_text": "#616e88",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#d8dee9",
            "btn_theme_hover": "#434c5e",
            "success": "#a3be8c",
            "success_hover": "#8fbc6e",
            "progress_bg": "#3b4252",
            "header_bg": "#242933",
            "header_border": "#434c5e",
        },
        "light": {
            **_STYLE,
            "bg_primary": "#eceff4",
            "bg_secondary": "#e5e9f0",
            "text_primary": "#2e3440",
            "text_secondary": "#4c566a",
            "text_muted": "#7b88a1",
            "accent": "#5e81ac",
            "accent_hover": "#4c6f9a",
            "border": "#c8d0dc",
            "btn_browse": "#dfe4ec",
            "btn_browse_hover": "#c8d0dc",
            "btn_disabled_bg": "#c2cad6",
            "btn_disabled_text": "#7b88a1",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#4c566a",
            "btn_theme_hover": "#dfe4ec",
            "success": "#7a9f6e",
            "success_hover": "#689058",
            "progress_bg": "#dfe4ec",
            "header_bg": "#e5e9f0",
            "header_border": "#c8d0dc",
        },
    },
    # ── Solarized ──
    "Solarized": {
        "dark": {
            **_STYLE,
            "bg_primary": "#002b36",
            "bg_secondary": "#073642",
            "text_primary": "#839496",
            "text_secondary": "#93a1a1",
            "text_muted": "#586e75",
            "accent": "#268bd2",
            "accent_hover": "#1d7ab8",
            "border": "#124652",
            "btn_browse": "#073642",
            "btn_browse_hover": "#11505f",
            "btn_disabled_bg": "#0e4050",
            "btn_disabled_text": "#586e75",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#839496",
            "btn_theme_hover": "#073642",
            "success": "#859900",
            "success_hover": "#6b7a00",
            "progress_bg": "#073642",
            "header_bg": "#001f27",
            "header_border": "#124652",
        },
        "light": {
            **_STYLE,
            "bg_primary": "#fdf6e3",
            "bg_secondary": "#eee8d5",
            "text_primary": "#586e75",
            "text_secondary": "#657b83",
            "text_muted": "#93a1a1",
            "accent": "#268bd2",
            "accent_hover": "#1d7ab8",
            "border": "#d6cdb5",
            "btn_browse": "#e8e1cc",
            "btn_browse_hover": "#d6cdb5",
            "btn_disabled_bg": "#d0c8b5",
            "btn_disabled_text": "#93a1a1",
            "btn_theme_bg": "transparent",
            "btn_theme_text": "#657b83",
            "btn_theme_hover": "#e8e1cc",
            "success": "#859900",
            "success_hover": "#6b7a00",
            "progress_bg": "#e8e1cc",
            "header_bg": "#f4edda",
            "header_border": "#d6cdb5",
        },
    },
}

FAMILY_NAMES = list(THEME_FAMILIES.keys())


def build_qss(family_name: str, dark: bool) -> str:
    """根据主题家族名和深色/浅色模式生成 QSS 样式表。"""
    mode = "dark" if dark else "light"
    return _QSS_TEMPLATE.format(**THEME_FAMILIES[family_name][mode])
