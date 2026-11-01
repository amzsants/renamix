from dataclasses import replace
from pathlib import Path
import csv
import errno
import os
import tempfile
import unittest
from unittest.mock import patch

from renamix.executor import execute, export_csv, rename_no_replace
from renamix.planner import Rule, build_plan


class ExecutorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def file(self, name, data="original"):
        path = self.folder / name
        path.write_text(data, encoding="utf-8")
        return path

    def plan(self, rule=None):
        return build_plan(self.folder, rule or Rule("prefix", "x_"))

    def test_real_native_rename(self):
        self.file("a.txt")
        report = execute(self.plan())
        self.assertEqual(report.renamed, 1, report.results)
        self.assertFalse((self.folder / "a.txt").exists())
        self.assertEqual((self.folder / "x_a.txt").read_text(), "original")

    def test_suffix_and_replacement_execute(self):
        for rule, original, proposed in (
            (Rule("suffix", "_final"), "relatorio.tar.gz", "relatorio_final.tar.gz"),
            (Rule("replace", "IMG_", "Foto_"), "IMG_001.jpg", "Foto_001.jpg"),
        ):
            with self.subTest(rule=rule), tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                (folder / original).write_bytes(b"unchanged bytes")
                report = execute(build_plan(folder, rule))
                self.assertEqual(report.renamed, 1, report.results)
                self.assertEqual((folder / proposed).read_bytes(), b"unchanged bytes")

    @unittest.skipUnless(os.name == "nt", "Bloqueio exclusivo do Windows")
    def test_windows_locked_file_is_failure(self):
        import ctypes
        source = self.file("a.txt")
        plan = self.plan()
        api = ctypes.WinDLL("kernel32", use_last_error=True)
        create = api.CreateFileW
        create.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                           ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p]
        create.restype = ctypes.c_void_p
        close = api.CloseHandle
        close.argtypes = [ctypes.c_void_p]
        close.restype = ctypes.c_int
        handle = create(str(source), 0x80000000, 0, None, 3, 0x80, None)
        if handle == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            report = execute(plan)
            self.assertEqual(report.failed, 1, report.results)
            self.assertEqual(report.renamed, 0)
        finally:
            close(handle)
        self.assertEqual(source.read_text(), "original")

    def test_native_exclusion_preserves_both_files(self):
        source = self.file("a.txt")
        target = self.file("b.txt", "target")
        with self.assertRaises(OSError):
            rename_no_replace(source, target)
        self.assertEqual(source.read_text(), "original")
        self.assertEqual(target.read_text(), "target")

    def test_existing_destination_not_overwritten(self):
        source = self.file("orig.txt")
        target = self.file("dest.txt", "target")
        report = execute(self.plan(Rule("replace", "orig", "dest")))
        self.assertEqual(report.failed, 1)
        self.assertEqual(source.read_text(), "original")
        self.assertEqual(target.read_text(), "target")

    def test_removed_after_preview(self):
        source = self.file("a.txt")
        plan = self.plan()
        source.unlink()
        report = execute(plan)
        self.assertEqual(report.failed, 1)
        self.assertFalse((self.folder / "x_a.txt").exists())

    def test_content_changed_after_preview(self):
        source = self.file("a.txt")
        plan = self.plan()
        source.write_text("changed and longer")
        self.assertEqual(execute(plan).failed, 1)
        self.assertEqual(source.read_text(), "changed and longer")

    def test_replaced_source_after_preview(self):
        source = self.file("a.txt")
        plan = self.plan()
        other = self.file("replacement", "different")
        source.unlink()
        other.rename(source)
        self.assertEqual(execute(plan).failed, 1)
        self.assertEqual(source.read_text(), "different")

    def test_destination_created_after_preview(self):
        self.file("a.txt")
        plan = self.plan()
        target = self.file("x_a.txt", "concurrent")
        report = execute(plan)
        self.assertEqual(report.failed, 1)
        self.assertEqual(target.read_text(), "concurrent")

    def test_destination_created_at_native_call(self):
        source = self.file("a.txt")
        plan = self.plan()

        def race(src, dst):
            dst.write_text("concurrent")
            rename_no_replace(src, dst)

        with patch("renamix.executor.rename_no_replace", side_effect=race):
            report = execute(plan)
        self.assertEqual(report.failed, 1)
        self.assertEqual(source.read_text(), "original")
        self.assertEqual((self.folder / "x_a.txt").read_text(), "concurrent")

    def test_partial_failure_and_continuation(self):
        self.file("a.txt")
        self.file("b.txt")

        def fail_one(src, dst):
            if src.name == "a.txt":
                raise PermissionError("Arquivo bloqueado")
            rename_no_replace(src, dst)

        with patch("renamix.executor.rename_no_replace", side_effect=fail_one):
            report = execute(self.plan())
        self.assertEqual((report.failed, report.renamed), (1, 1))
        self.assertIn("Arquivo bloqueado", report.results[0].message)
        self.assertTrue((self.folder / "a.txt").exists())
        self.assertTrue((self.folder / "x_b.txt").exists())

    def test_unexpected_exception_is_failure(self):
        self.file("a.txt")
        with patch("renamix.executor.rename_no_replace", side_effect=RuntimeError("unexpected")):
            report = execute(self.plan())
        self.assertEqual((report.failed, report.renamed), (1, 0))
        self.assertIn("RuntimeError", report.results[0].message)

    def test_scan_permission_error_is_reported(self):
        self.file("a.txt")
        plan = self.plan()
        with patch("renamix.executor.build_plan", side_effect=PermissionError("Sem permissão")):
            report = execute(plan)
        self.assertEqual(report.failed, 1)
        self.assertIn("Sem permissão", report.results[0].message)

    def test_file_removed_during_execution(self):
        source = self.file("a.txt")
        plan = self.plan()

        def remove_before_call(src, dst):
            src.unlink()
            rename_no_replace(src, dst)

        with patch("renamix.executor.rename_no_replace", side_effect=remove_before_call):
            report = execute(plan)
        self.assertEqual(report.failed, 1)
        self.assertFalse((self.folder / "x_a.txt").exists())

    def test_source_becomes_symlink_after_preview(self):
        source = self.file("a.txt")
        target = self.file("target.txt", "unrelated")
        plan = self.plan()
        link = self.folder / "temporary-link"
        try:
            link.symlink_to(target)
        except OSError:
            self.skipTest("Criação de links exige privilégios neste sistema.")
        source.unlink()
        link.rename(source)
        report = execute(plan)
        original_result = next(row for row in report.results if row.original == "a.txt")
        self.assertEqual(original_result.outcome, "Falha")
        self.assertTrue(source.is_symlink())

    def test_unavailable_safe_backend_fails_closed(self):
        self.file("a.txt")
        with patch("renamix.executor.sys.platform", "unsupported"):
            report = execute(self.plan())
        self.assertEqual(report.failed, 1)
        self.assertTrue((self.folder / "a.txt").exists())

    def test_unsupported_filesystem_is_failure(self):
        self.file("a.txt")
        with patch("renamix.executor.rename_no_replace", side_effect=OSError(errno.ENOTSUP, "unsupported")):
            self.assertEqual(execute(self.plan()).failed, 1)
        self.assertTrue((self.folder / "a.txt").exists())

    def test_changed_directory_is_rejected(self):
        self.file("a.txt")
        plan = self.plan()
        plan = replace(plan, folder_identity=(-1, -1))
        self.assertEqual(execute(plan).failed, 1)

    def test_directory_missing_at_execution(self):
        child = self.folder / "child"
        child.mkdir()
        (child / "a.txt").write_text("a")
        plan = build_plan(child, Rule("prefix", "x"))
        (child / "a.txt").unlink()
        child.rmdir()
        self.assertEqual(execute(plan).failed, 1)

    def test_tampered_plan_cannot_escape_folder(self):
        self.file("a.txt")
        plan = self.plan()
        op, = plan.operations
        for name in ("../outside", "C:\\outside", "/outside"):
            corrupted = replace(plan, operations=(replace(op, proposed=name),))
            with self.subTest(name=name):
                self.assertEqual(execute(corrupted).failed, 1)
        self.assertTrue((self.folder / "a.txt").exists())

    def test_ignored_and_unchanged_report(self):
        self.file("a.txt")
        self.file(".hidden")
        report = execute(self.plan(Rule("replace", "missing", "x")))
        self.assertEqual((report.ignored, report.failed, report.renamed), (2, 0, 0))

    def test_csv_export_exclusive_and_formula_safe(self):
        self.file("=formula.txt")
        report = execute(self.plan())
        destination = self.folder / "report.csv"
        export_csv(report, destination)
        with destination.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.reader(stream, delimiter=";"))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][0], "'=formula.txt")
        before = destination.read_bytes()
        with self.assertRaises(FileExistsError):
            export_csv(report, destination)
        self.assertEqual(before, destination.read_bytes())

    def test_execution_twice_does_not_rename_again(self):
        self.file("a.txt")
        plan = self.plan()
        self.assertEqual(execute(plan).renamed, 1)
        self.assertEqual(execute(plan).failed, 1)
        self.assertFalse((self.folder / "x_x_a.txt").exists())
