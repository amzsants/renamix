"""Final validation and native exclusive rename; never fall back to os.replace."""

import csv
import ctypes
import errno
import os
from pathlib import Path
import sys

from dataclasses import dataclass
from .planner import (CONFLICT, INVALID, READY, Fingerprint, Plan, build_plan,
                      identity, ignored_reason, invalid_name, name_key)


def rename_no_replace(source: Path, target: Path):
    """Rename once, with kernel-enforced destination exclusion or fail closed."""
    if source.parent != target.parent or source.name == target.name:
        raise ValueError("A operação deve permanecer na mesma pasta e alterar o nome.")
    if sys.platform == "win32":
        api = ctypes.WinDLL("kernel32", use_last_error=True).MoveFileExW
        api.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
        api.restype = ctypes.c_int
        if not api(str(source), str(target), 0):
            raise ctypes.WinError(ctypes.get_last_error())
        return
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        api = libc.renameat2
        api.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p,
                        ctypes.c_uint]
        api.restype = ctypes.c_int
        # Directory descriptors keep this call anchored to one directory.
        fd = os.open(source.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            result = api(fd, os.fsencode(source.name), fd, os.fsencode(target.name), 1)
            code = ctypes.get_errno()
        finally:
            os.close(fd)
    elif sys.platform == "darwin" and hasattr(libc, "renamex_np"):
        api = libc.renamex_np
        api.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        api.restype = ctypes.c_int
        result = api(os.fsencode(source), os.fsencode(target), 0x4)  # RENAME_EXCL
        code = ctypes.get_errno()
    else:
        raise OSError(errno.ENOTSUP, "Sistema sem renomeação exclusiva disponível; operação recusada.")
    if result != 0:
        raise OSError(code, os.strerror(code), str(target))


@dataclass(frozen=True)
class Result:
    original: str
    proposed: str
    outcome: str
    message: str = ""


@dataclass(frozen=True)
class Report:
    results: tuple[Result, ...]

    @property
    def renamed(self):
        return sum(row.outcome == "Renomeado" for row in self.results)

    @property
    def failed(self):
        return sum(row.outcome == "Falha" for row in self.results)

    @property
    def ignored(self):
        return len(self.results) - self.renamed - self.failed

    def summary(self):
        return (f"Analisados: {len(self.results)}  •  Renomeados: {self.renamed}  •  "
                f"Ignorados: {self.ignored}  •  Falhas: {self.failed}")


def execute(plan: Plan) -> Report:
    """Execute an already confirmed plan, rejecting stale or malformed entries."""
    plan.rule.validate()
    try:
        if identity(plan.folder.stat()) != plan.folder_identity:
            raise ValueError("A pasta foi substituída após a prévia.")
        fresh = build_plan(plan.folder, plan.rule)
        current = {op.original: op for op in fresh.operations}
        setup_error = ""
    except (OSError, ValueError) as exc:
        current, setup_error = {}, str(exc)
    results = []
    for op in plan.operations:
        if op.status != READY:
            outcome = "Falha" if op.status in {CONFLICT, INVALID} else "Ignorado"
            results.append(Result(op.original, op.proposed, outcome, op.message or op.status))
            continue
        try:
            if setup_error:
                raise ValueError(setup_error)
            if (Path(op.original).name != op.original or invalid_name(op.proposed, plan.folder)
                    or op.proposed != plan.rule.apply(op.original)):
                raise ValueError("Planejamento inválido; gere uma nova prévia.")
            latest = current.get(op.original)
            if latest is None or latest.fingerprint != op.fingerprint:
                raise ValueError("Arquivo removido ou alterado após a prévia.")
            if latest.status != READY or latest.proposed != op.proposed:
                raise ValueError(latest.message or "O planejamento mudou; gere uma nova prévia.")
            if identity(plan.folder.stat()) != plan.folder_identity:
                raise ValueError("A pasta foi substituída durante a execução.")
            source, target = plan.folder / op.original, plan.folder / op.proposed
            info = source.lstat()
            if ignored_reason(source, info) or Fingerprint.of(info) != op.fingerprint:
                raise ValueError("Arquivo alterado durante a execução.")
            # Includes hidden entries, directories and dangling links. Native API
            # closes the remaining exact-destination creation race.
            if any(name_key(p.name) == name_key(op.proposed) for p in plan.folder.iterdir()):
                raise FileExistsError("Destino ocupado; nenhum arquivo foi sobrescrito.")
            rename_no_replace(source, target)
            results.append(Result(op.original, op.proposed, "Renomeado"))
        except Exception as exc:
            # A failed row is always visible; partial success is not rolled back.
            results.append(Result(op.original, op.proposed, "Falha", f"{type(exc).__name__}: {exc}"))
    return Report(tuple(results))


def export_csv(report: Report, destination: str | Path):
    # Exclusive creation also protects files selected in the save dialog.
    with Path(destination).open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream, delimiter=";")
        writer.writerow(["Nome anterior", "Nome proposto", "Resultado", "Mensagem de erro"])
        for row in report.results:
            # Prevent spreadsheet formula execution when opening untrusted names.
            writer.writerow(["'" + value if value.startswith(("=", "+", "-", "@", "\t", "\r", "\n"))
                             else value for value in (row.original, row.proposed, row.outcome, row.message)])
