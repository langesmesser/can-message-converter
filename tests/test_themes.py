"""主题系统数据完整性测试 —— 验证 8 套配色方案 × 2 模式的 token 和 QSS 生成。"""

from src.ui.themes import THEME_FAMILIES, FAMILY_NAMES, build_qss

ALL_FAMILIES = list(THEME_FAMILIES.keys())

REQUIRED_TOKENS = [
    "bg_primary", "bg_secondary", "text_primary", "text_secondary", "text_muted",
    "accent", "accent_hover", "border", "btn_browse", "btn_browse_hover",
    "btn_disabled_bg", "btn_disabled_text", "btn_theme_bg", "btn_theme_text",
    "btn_theme_hover", "success", "success_hover", "progress_bg", "header_bg",
    "header_border",
    "font_family", "font_size", "border_radius",
    "progress_height", "progress_radius", "button_font_weight",
]

# ── 结构完整性 ──

def test_all_families_have_both_modes():
    for family in ALL_FAMILIES:
        assert "dark" in THEME_FAMILIES[family], f"{family}: missing dark mode"
        assert "light" in THEME_FAMILIES[family], f"{family}: missing light mode"


def test_required_tokens_present():
    for family in ALL_FAMILIES:
        for mode in ("dark", "light"):
            tokens = THEME_FAMILIES[family][mode]
            for token in REQUIRED_TOKENS:
                assert token in tokens, f"{family}/{mode}: missing token '{token}'"


def test_family_names_length():
    assert len(FAMILY_NAMES) == 8, f"expected 8 families, got {len(FAMILY_NAMES)}"


# ── Notion 是默认主题 ──

def test_notion_family_exists():
    assert "Notion" in THEME_FAMILIES


def test_notion_is_default():
    assert FAMILY_NAMES[0] == "Notion", f"expected Notion first, got {FAMILY_NAMES[0]}"


# ── Notion 有独立样式 token，其他 6 套共享统一样式 ──

def test_notion_has_distinct_style_tokens():
    """Notion 主题有不同于其他主题的样式参数。"""
    notion = THEME_FAMILIES["Notion"]["dark"]
    discord = THEME_FAMILIES["Discord"]["dark"]
    assert notion["border_radius"] == "8px"
    assert discord["border_radius"] == "6px"
    assert notion["button_font_weight"] == "500"
    assert discord["button_font_weight"] == "bold"
    assert notion["progress_height"] == "4px"
    assert discord["progress_height"] == "6px"


def test_existing_seven_families_share_style_tokens():
    """Apple/Discord/Ocean/Forest/Sunset/Nord/Solarized 共享相同的样式 token。"""
    others = ["Apple", "Discord", "Ocean", "Forest", "Sunset", "Nord", "Solarized"]
    for key in ["font_family", "font_size", "border_radius",
                "progress_height", "progress_radius", "button_font_weight"]:
        values = {THEME_FAMILIES[f]["dark"][key] for f in others}
        assert len(values) == 1, f"'{key}' differs across existing themes: {values}"


# ── QSS 生成 ──

def test_build_qss_notion_dark_returns_string():
    qss = build_qss("Notion", True)
    assert isinstance(qss, str)
    assert len(qss) > 0


def test_build_qss_notion_light_returns_string():
    qss = build_qss("Notion", False)
    assert isinstance(qss, str)
    assert len(qss) > 0


def test_build_qss_all_families_no_exception():
    for family in ALL_FAMILIES:
        for dark in (True, False):
            qss = build_qss(family, dark)
            assert isinstance(qss, str)
            assert len(qss) > 0


# ── Notion 配色特征 ──

def test_notion_accent_is_purple():
    assert THEME_FAMILIES["Notion"]["dark"]["accent"] == "#5645d4"
    assert THEME_FAMILIES["Notion"]["light"]["accent"] == "#5645d4"


def test_notion_success_is_green():
    assert THEME_FAMILIES["Notion"]["dark"]["success"] == "#1aae39"
    assert THEME_FAMILIES["Notion"]["light"]["success"] == "#1aae39"


def test_notion_light_uses_canvas_white():
    assert THEME_FAMILIES["Notion"]["light"]["bg_primary"] == "#ffffff"


def test_notion_light_surface():
    assert THEME_FAMILIES["Notion"]["light"]["bg_secondary"] == "#f6f5f4"


def test_notion_light_hairline_border():
    assert THEME_FAMILIES["Notion"]["light"]["border"] == "#e5e3df"


def test_build_qss_contains_notion_purple():
    qss = build_qss("Notion", True)
    assert "#5645d4" in qss


def test_all_qss_has_section_label_rule():
    """确保 section_label QSS 规则用于卡片标题。"""
    qss = build_qss("Notion", True)
    assert "QLabel#section_label" in qss


def test_all_qss_has_card_rule():
    """确保 QFrame#card 规则存在。"""
    qss = build_qss("Notion", True)
    assert "QFrame#card" in qss


def test_notion_border_radius_is_8px():
    qss = build_qss("Notion", False)
    assert "border-radius: 8px;" in qss


def test_notion_font_weight_is_500():
    qss = build_qss("Notion", True)
    assert "font-weight: 500;" in qss


def test_existing_themes_keep_bold_weight():
    for family in ["Apple", "Discord", "Ocean", "Forest", "Sunset", "Nord", "Solarized"]:
        qss = build_qss(family, True)
        assert "bold" in qss, f"{family}: lost bold weight"


# ── Apple 配色特征 ──

def test_apple_family_exists():
    assert "Apple" in THEME_FAMILIES


def test_apple_accent_is_action_blue():
    assert THEME_FAMILIES["Apple"]["light"]["accent"] == "#0066cc"


def test_apple_dark_accent_is_bright_blue():
    assert THEME_FAMILIES["Apple"]["dark"]["accent"] == "#2997ff"


def test_apple_light_uses_parchment():
    assert THEME_FAMILIES["Apple"]["light"]["bg_primary"] == "#f5f5f7"


def test_apple_dark_uses_black():
    assert THEME_FAMILIES["Apple"]["dark"]["bg_primary"] == "#000000"
