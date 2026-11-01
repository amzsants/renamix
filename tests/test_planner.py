from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

from renamix.planner import (CONFLICT, IGNORED, INVALID, READY, UNCHANGED,
                             Rule, build_plan, invalid_name)


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def file(self, name, data="conteúdo"):
        path = self.folder / name
        path.write_text(data, encoding="utf-8")
        return path

    def plan(self, rule):
        return build_plan(self.folder, rule)

    def test_prefix(self):
        self.file("documento.pdf")
        op, = self.plan(Rule("prefix", "2026_")).operations
        self.assertEqual((op.proposed, op.status), ("2026_documento.pdf", READY))

    def test_suffix(self):
        self.assertEqual(Rule("suffix", "_final").apply("relatorio.xlsx"), "relatorio_final.xlsx")

    def test_replacement(self):
        self.assertEqual(Rule("replace", "IMG_", "Foto_").apply("IMG_001.jpg"), "Foto_001.jpg")

    def test_all_extensions_preserved(self):
        self.assertEqual(Rule("suffix", "_novo").apply("backup.tar.gz"), "backup_novo.tar.gz")
        self.assertEqual(Rule("replace", "gz", "zip").apply("backup.tar.gz"), "backup.tar.gz")
        self.assertEqual(Rule("prefix", "x_").apply("report.v1.csv"), "x_report.v1.csv")

    def test_no_extension_and_unicode(self):
        self.file("ação_日本語")
        op, = self.plan(Rule("suffix", "_✓")).operations
        self.assertEqual(op.proposed, "ação_日本語_✓")
        self.assertEqual(op.status, READY)

    def test_empty_folder(self):
        plan = self.plan(Rule("prefix", "x"))
        self.assertEqual(plan.operations, ())
        self.assertEqual(plan.eligible, 0)

    def test_permission_denied_during_scan(self):
        with patch.object(Path, "iterdir", side_effect=PermissionError("Sem acesso")):
            with self.assertRaises(PermissionError):
                self.plan(Rule("prefix", "x"))

    def test_permission_denied_on_one_entry(self):
        self.file("a.txt")
        original = Path.lstat

        def deny(path, *args, **kwargs):
            if path.name == "a.txt":
                raise PermissionError("Sem acesso ao arquivo")
            return original(path, *args, **kwargs)

        with patch.object(Path, "lstat", deny):
            op, = self.plan(Rule("prefix", "x")).operations
        self.assertEqual(op.status, INVALID)
        self.assertIn("Sem acesso", op.message)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "Arquivos especiais POSIX")
    def test_fifo_is_ignored(self):
        os.mkfifo(self.folder / "pipe")
        op, = self.plan(Rule("prefix", "x")).operations
        self.assertEqual(op.status, IGNORED)

    def test_ignored_entries(self):
        self.file(".oculto")
        (self.folder / "subpasta").mkdir()
        self.file("normal.txt")
        plan = self.plan(Rule("prefix", "x"))
        self.assertEqual(plan.eligible, 1)
        self.assertEqual(sum(op.status == IGNORED for op in plan.operations), 2)

    def test_symlink_ignored_even_when_dangling(self):
        link = self.folder / "link.txt"
        try:
            link.symlink_to(self.folder / "missing.txt")
        except OSError:
            self.skipTest("Criação de links exige privilégios neste sistema.")
        op, = self.plan(Rule("prefix", "x")).operations
        self.assertEqual(op.status, IGNORED)

    @unittest.skipUnless(os.name == "nt", "Atributo oculto do Windows")
    def test_windows_hidden_attribute(self):
        import ctypes
        path = self.file("oculto.txt")
        api = ctypes.windll.kernel32.SetFileAttributesW
        self.assertTrue(api(str(path), 2))
        self.addCleanup(api, str(path), 128)
        op, = self.plan(Rule("prefix", "x")).operations
        self.assertEqual(op.status, IGNORED)

    def test_invalid_rules(self):
        for rule in (Rule("other", "x"), Rule("prefix", ""), Rule("replace", "", "x"),
                     Rule("prefix", "../"), Rule("suffix", "\\x"), Rule("prefix", "\0")):
            with self.subTest(rule=rule), self.assertRaises(ValueError):
                self.plan(rule)

    def test_invalid_proposed_names(self):
        self.file("good.txt")
        for replacement in ("CON", "LPT1", "NUL", "", ".secret", "x" * 256):
            with self.subTest(replacement=replacement):
                op, = self.plan(Rule("replace", "good", replacement)).operations
                self.assertEqual(op.status, INVALID)
        for name in ("../escape", "file ", "file.", "AUX.txt", "COM¹.txt", "x:y", "CONIN$"):
            self.assertTrue(invalid_name(name, self.folder))

    def test_unchanged(self):
        self.file("a.txt")
        op, = self.plan(Rule("replace", "missing", "x")).operations
        self.assertEqual(op.status, UNCHANGED)

    def test_planned_collisions(self):
        self.file("a.txt")
        self.file("aa.txt")
        ops = self.plan(Rule("replace", "a", "b")).operations
        self.assertTrue(all(op.status == READY for op in ops))
        # Both names lose their distinguishing characters.
        self.file("ab.txt")
        self.file("b.txt")
        ops = {op.original: op for op in self.plan(Rule("replace", "a", "")).operations}
        self.assertEqual(ops["ab.txt"].status, CONFLICT)

    def test_two_new_targets_collide(self):
        self.file("ab.txt")
        self.file("aab.txt")
        ops = self.plan(Rule("replace", "a", "")).operations
        self.assertTrue(all(op.status == CONFLICT for op in ops))

    def test_existing_targets_include_directories_and_case(self):
        self.file("a.txt")
        (self.folder / "X_A.TXT").mkdir()
        op = next(op for op in self.plan(Rule("prefix", "x_")).operations if op.original == "a.txt")
        self.assertEqual(op.status, CONFLICT)

    def test_unicode_equivalent_conflict(self):
        self.file("a.txt")
        self.file("é_a.txt")
        op = next(op for op in self.plan(Rule("prefix", "e\u0301_")).operations if op.original == "a.txt")
        self.assertEqual(op.status, CONFLICT)

    def test_case_only_rename_is_blocked(self):
        self.file("a.txt")
        op, = self.plan(Rule("replace", "a", "A")).operations
        self.assertEqual(op.status, CONFLICT)

    def test_preview_has_no_side_effects(self):
        source = self.file("a.txt")
        before = source.stat()
        self.plan(Rule("prefix", "x"))
        self.assertEqual([p.name for p in self.folder.iterdir()], ["a.txt"])
        self.assertEqual(source.read_text(encoding="utf-8"), "conteúdo")
        after = source.stat()
        self.assertEqual((before.st_mtime_ns, before.st_ctime_ns), (after.st_mtime_ns, after.st_ctime_ns))

    def test_missing_folder_and_regular_file(self):
        with self.assertRaises(FileNotFoundError):
            build_plan(self.folder / "missing", Rule("prefix", "x"))
        with self.assertRaises(NotADirectoryError):
            build_plan(self.file("a"), Rule("prefix", "x"))
