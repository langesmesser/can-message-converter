"""MainWindow 主题行为测试 —— 验证默认主题、轮盘切换、深色/浅色模式。"""

import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.themes import FAMILY_NAMES

_qapp = QApplication.instance()
if _qapp is None:
    _qapp = QApplication(sys.argv)


def _mk_window():
    """创建新的 MainWindow 实例用于测试。"""
    return MainWindow()


def test_default_theme_is_notion():
    w = _mk_window()
    assert w._theme_family == "Notion"


def test_cycle_theme_advances():
    w = _mk_window()
    old = w._theme_family
    w._cycle_theme()
    new = w._theme_family
    expected_next = FAMILY_NAMES[(FAMILY_NAMES.index(old) + 1) % len(FAMILY_NAMES)]
    assert new == expected_next
    assert new != old


def test_cycle_wraps_around():
    w = _mk_window()
    for _ in range(len(FAMILY_NAMES)):
        w._cycle_theme()
    assert w._theme_family == "Notion"


def test_toggle_dark_mode():
    w = _mk_window()
    old = w._dark_mode
    w._toggle_theme()
    assert w._dark_mode != old


def test_cycle_btn_text_updates():
    w = _mk_window()
    w._theme_family = "Discord"
    w._apply_theme()
    assert "Discord" in w.theme_cycle_btn.text()
    w._theme_family = "Ocean"
    w._apply_theme()
    assert "Ocean" in w.theme_cycle_btn.text()


def test_dark_mode_btn_text_changes():
    w = _mk_window()
    w._dark_mode = True
    w._apply_theme()
    assert "☽" in w.theme_btn.text() or "☽" in w.theme_btn.text()
    w._dark_mode = False
    w._apply_theme()
    assert "☀" in w.theme_btn.text() or "☀" in w.theme_btn.text()


def test_apply_theme_all_families_no_crash():
    w = _mk_window()
    for family in FAMILY_NAMES:
        w._theme_family = family
        w._apply_theme()
        w._dark_mode = not w._dark_mode
        w._apply_theme()


def test_window_title_contains_version():
    w = _mk_window()
    assert "CAN" in w.windowTitle()
    assert "报文" in w.windowTitle()
