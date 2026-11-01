"""Launch with python -m renamix."""

import sys


def main():
    try:
        from .gui import main as launch
        launch()
    except ImportError as exc:
        print(f"Não foi possível carregar a interface: {exc}. Instale o suporte Tkinter do Python.", file=sys.stderr)
        return 1
    except Exception as exc:
        # Tk may be present without an available display (headless Linux).
        print(f"Não foi possível iniciar o Renamix: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
