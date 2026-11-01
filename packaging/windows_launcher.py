"""Absolute package import for the PyInstaller script entry point."""

from renamix.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
