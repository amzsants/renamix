import io
import sys
import unittest
from unittest.mock import Mock, patch

from renamix.__main__ import main, report_startup_error


class StartupTests(unittest.TestCase):
    def test_source_errors_use_stderr(self):
        stream = io.StringIO()
        with patch.object(sys, "stderr", stream):
            report_startup_error("Falha de teste")
        self.assertIn("Falha de teste", stream.getvalue())

    def test_windowed_errors_use_dialog(self):
        with patch.object(sys, "stderr", None), patch("tkinter.messagebox.showerror") as show:
            report_startup_error("Falha de teste")
        show.assert_called_once()
        self.assertIn("Falha de teste", show.call_args.args)

    def test_windowed_tk_failure_uses_native_dialog(self):
        native = Mock(return_value=1)
        with patch.object(sys, "stderr", None), patch.object(sys, "platform", "win32"), \
                patch("tkinter.messagebox.showerror", side_effect=RuntimeError("Tk failed")), \
                patch("ctypes.WinDLL", create=True) as library:
            library.return_value.MessageBoxW = native
            report_startup_error("Falha de teste")
        native.assert_called_once()

    def test_startup_exception_returns_failure(self):
        with patch("renamix.gui.main", side_effect=RuntimeError("test")), \
                patch("renamix.__main__.report_startup_error") as report:
            self.assertEqual(main(), 1)
        self.assertIn("RuntimeError", report.call_args.args[0])

    def test_successful_startup_returns_zero(self):
        with patch("renamix.gui.main") as launch:
            self.assertEqual(main(), 0)
        launch.assert_called_once()
