"""Build from any working directory: python path/to/scripts/build_windows.py."""

import hashlib
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    if sys.platform != "win32":
        raise SystemExit("O executável Windows deve ser construído no Windows.")
    root = Path(__file__).resolve().parents[1]
    subprocess.run([
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
        "--onefile", "--windowed", "--noupx", "--name", "Renamix",
        "--distpath", str(root / "dist"), "--workpath", str(root / "build" / "pyinstaller"),
        "--specpath", str(root / "build"), "--paths", str(root),
        "--exclude-module", "tests", "--exclude-module", "test",
        "--exclude-module", "unittest", str(root / "packaging" / "windows_launcher.py"),
    ], cwd=root, check=True)
    executable = root / "dist" / "Renamix.exe"
    if not executable.is_file() or executable.stat().st_size == 0:
        raise SystemExit("O build não gerou um executável válido.")
    digest = hashlib.sha256(executable.read_bytes()).hexdigest()
    (executable.parent / "Renamix.exe.sha256").write_text(
        f"{digest}  Renamix.exe\n", encoding="ascii")
    shutil.copyfile(root / "LICENSE", executable.parent / "LICENSE")
    print(f"Executável: {executable}\nBytes: {executable.stat().st_size}\nSHA-256: {digest}")


if __name__ == "__main__":
    main()
