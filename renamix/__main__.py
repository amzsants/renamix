"""Launch with python -m renamix."""

import sys


def report_startup_error(message):
    """Windowed builds have no stderr; keep startup failures visible."""
    if sys.stderr is not None:
        print(message, file=sys.stderr)
        return
    try:
        from tkinter import messagebox
        messagebox.showerror("Renamix — erro de inicialização", message)
    except Exception:
        if sys.platform != "win32":
            raise RuntimeError(message)
        # Also works if the bundled Tcl/Tk itself could not be loaded.
        import ctypes
        show = ctypes.WinDLL("user32", use_last_error=True).MessageBoxW
        show.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint]
        show.restype = ctypes.c_int
        if not show(None, message, "Renamix — erro de inicialização", 0x10):
            raise RuntimeError(message)


def main():
    try:
        from .gui import main as launch
        launch()
    except ImportError as exc:
        guidance = ("Obtenha uma cópia íntegra do executável." if getattr(sys, "frozen", False)
                    else "Verifique o suporte Tkinter da instalação do Python.")
        report_startup_error(f"Não foi possível carregar a interface: {exc}. {guidance}")
        return 1
    except Exception as exc:
        # Tk may be present without an available display (headless Linux).
        report_startup_error(f"Não foi possível iniciar o Renamix: {type(exc).__name__}: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
