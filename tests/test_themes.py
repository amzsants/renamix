"""Theme data and persistence tests, without opening a graphical window."""

from dataclasses import fields
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from renamix.themes import (DEFAULT_THEME, THEMES, apply_theme, contrast, get_theme,
                            load_theme, readable_on, save_theme, settings_path)


class ThemeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.config = self.folder / "preferences" / "settings.json"

    def test_exactly_eight_named_themes(self):
        self.assertEqual({theme.name for theme in THEMES.values()}, {
            "Renamix Original", "ChatGPT Dark", "ChatGPT Light", "Codex Dark",
            "Codex Light", "Sakura", "Dark Beach", "Vampire"})
        self.assertEqual(len(THEMES), 8)
        self.assertEqual(get_theme(DEFAULT_THEME).name, "Renamix Original")

    def test_required_palette_colors(self):
        expected = {
            "original": ("#0D1117", "#161B22", "#E63946", "#E6EDF3"),
            "chatgpt-dark": ("#151719", "#24282B", "#10A37F", "#F0F0F0"),
            "chatgpt-light": ("#F7F7F5", "#FFFFFF", "#087F62", "#202123"),
            "codex-dark": ("#101820", "#1B2935", "#64C8BE", "#E8F0F4"),
            "codex-light": ("#F1F5F7", "#FFFFFF", "#187E85", "#1C303A"),
            "sakura": ("#281C30", "#39283F", "#F0A7C6", "#FFF0F7"),
            "dark-beach": ("#161430", "#252348", "#9D82DB", "#F0ECFF"),
            "vampire": ("#090709", "#1B1015", "#B10F2E", "#F5E8EB"),
        }
        for theme_id, colors in expected.items():
            with self.subTest(theme=theme_id):
                theme = get_theme(theme_id)
                self.assertEqual((theme.background, theme.surface, theme.accent, theme.text), colors)
        self.assertEqual(THEMES["sakura"].secondary, "#A77AAB")
        self.assertEqual(THEMES["dark-beach"].secondary, "#68C8D9")
        self.assertEqual(THEMES["vampire"].secondary, "#541221")

    def test_palette_integrity(self):
        for theme_id, theme in THEMES.items():
            with self.subTest(theme=theme_id):
                self.assertTrue(theme.description)
                colors = [getattr(theme, field.name) for field in fields(theme)
                          if field.name not in {"name", "description"}]
                colors += [theme.border, theme.muted, theme.selection, theme.error,
                           theme.warning, theme.success]
                for color in colors:
                    self.assertRegex(color, r"^#[0-9A-F]{6}$")
                self.assertEqual(len({theme.error, theme.warning, theme.success}), 3)

    def test_readable_text_and_semantic_colors(self):
        for theme_id, theme in THEMES.items():
            with self.subTest(theme=theme_id):
                self.assertGreaterEqual(contrast(theme.text, theme.background), 4.5)
                self.assertGreaterEqual(contrast(theme.text, theme.surface), 4.5)
                for color in (theme.muted, theme.error, theme.warning, theme.success):
                    self.assertGreaterEqual(contrast(color, theme.surface), 4.5)
                for background in (theme.accent, theme.border, theme.selection):
                    self.assertGreaterEqual(contrast(readable_on(background), background), 4.5)

    def test_select_valid_theme(self):
        for theme_id in THEMES:
            self.assertIs(get_theme(theme_id), THEMES[theme_id])

    def test_unknown_theme_is_rejected(self):
        for theme_id in ("unknown", "", None, [], {}):
            with self.subTest(theme=theme_id), self.assertRaises(ValueError):
                get_theme(theme_id)
        with self.assertRaises(ValueError):
            save_theme("unknown", self.config)
        self.assertFalse(self.config.exists())

    def test_missing_config_uses_original_without_writing(self):
        self.assertEqual(load_theme(self.config), DEFAULT_THEME)
        self.assertFalse(self.config.parent.exists())

    def test_save_and_restore_each_theme(self):
        for theme_id in THEMES:
            with self.subTest(theme=theme_id):
                save_theme(theme_id, self.config)
                self.assertEqual(load_theme(self.config), theme_id)
                self.assertEqual(json.loads(self.config.read_text(encoding="utf-8")), {"theme": theme_id})

    def test_restore_original_is_persisted(self):
        save_theme("sakura", self.config)
        save_theme(DEFAULT_THEME, self.config)
        self.assertEqual(load_theme(self.config), DEFAULT_THEME)

    def test_invalid_config_recovers_original(self):
        self.config.parent.mkdir()
        for content in ("", "{", "null", "[]", "3", '"sakura"', '{}',
                        '{"theme":"unknown"}', '{"theme":[]}', '{"theme":true}',
                        '{"theme":null}', '[' * 1500):
            with self.subTest(content=content[:40]):
                self.config.write_text(content, encoding="utf-8")
                self.assertEqual(load_theme(self.config), DEFAULT_THEME)
        self.config.write_bytes(b"\xff\xfe\x80")
        self.assertEqual(load_theme(self.config), DEFAULT_THEME)

    def test_oversized_config_recovers_original(self):
        self.config.parent.mkdir()
        self.config.write_text(" " * 4097)
        self.assertEqual(load_theme(self.config), DEFAULT_THEME)

    def test_unreadable_config_does_not_block_startup(self):
        with patch.object(Path, "stat", side_effect=PermissionError("no access")):
            self.assertEqual(load_theme(self.config), DEFAULT_THEME)

    def test_failed_save_keeps_previous_config_and_cleans_temp(self):
        save_theme("sakura", self.config)
        with patch("renamix.themes.os.replace", side_effect=PermissionError("read only")):
            with self.assertRaises(PermissionError):
                save_theme("vampire", self.config)
        self.assertEqual(load_theme(self.config), "sakura")
        self.assertEqual(list(self.config.parent.iterdir()), [self.config])

    def test_windows_config_location(self):
        with patch("renamix.themes.sys.platform", "win32"), patch.dict(os.environ, {"APPDATA": str(self.folder)}):
            self.assertEqual(settings_path(), self.folder / "Renamix" / "settings.json")

    def test_macos_config_location(self):
        with patch("renamix.themes.sys.platform", "darwin"), patch.object(Path, "home", return_value=self.folder):
            self.assertEqual(settings_path(), self.folder / "Library" / "Application Support" / "Renamix" / "settings.json")

    def test_linux_config_location_and_relative_fallback(self):
        with patch("renamix.themes.sys.platform", "linux"), patch.object(Path, "home", return_value=self.folder):
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.folder / "config")}):
                self.assertEqual(settings_path(), self.folder / "config" / "renamix" / "settings.json")
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": "relative"}):
                self.assertEqual(settings_path(), self.folder / ".config" / "renamix" / "settings.json")

    def test_styles_update_all_themes_without_modifying_table_data(self):
        root, tree, style = Mock(), Mock(), Mock()
        style.theme_use.return_value = "clam"
        with patch("renamix.themes.ttk.Style", return_value=style):
            for theme_id in THEMES:
                apply_theme(root, theme_id, tree=tree)
                root.configure.assert_called_with(bg=THEMES[theme_id].background)
                tree.tag_configure.assert_any_call("error", foreground=THEMES[theme_id].error)
                tree.tag_configure.assert_any_call("warning", foreground=THEMES[theme_id].warning)
                tree.tag_configure.assert_any_call("success", foreground=THEMES[theme_id].success)
        tree.delete.assert_not_called()
        tree.insert.assert_not_called()
