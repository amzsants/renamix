"""Read-only planning and deliberately conservative, portable filenames."""

from dataclasses import dataclass, replace
from pathlib import Path
import os
import re
import stat
import unicodedata

READY = "Pronto"
UNCHANGED = "Sem alterações"
IGNORED = "Ignorado"
CONFLICT = "Conflito"
INVALID = "Inválido"


@dataclass(frozen=True)
class Rule:
    kind: str
    text: str
    replacement: str = ""

    def validate(self):
        if self.kind not in {"prefix", "suffix", "replace"}:
            raise ValueError("Escolha uma regra válida.")
        if not self.text:
            raise ValueError("Informe o texto da regra; a busca não pode ser vazia.")
        for value in (self.text, self.replacement):
            if any(c in '<>:"/\\|?*' or unicodedata.category(c) == "Cc" for c in value):
                raise ValueError("A regra contém separadores ou caracteres não permitidos.")

    def apply(self, name: str) -> str:
        # All suffixes are preserved: archive.tar.gz -> archive + .tar.gz.
        extension = "".join(Path(name).suffixes)
        stem = name[:-len(extension)] if extension else name
        if self.kind == "prefix":
            stem = self.text + stem
        elif self.kind == "suffix":
            stem += self.text
        else:
            stem = stem.replace(self.text, self.replacement)
        return stem + extension


@dataclass(frozen=True)
class Fingerprint:
    device: int
    inode: int
    mode: int
    size: int
    modified: int
    changed: int

    @classmethod
    def of(cls, info):
        return cls(info.st_dev, info.st_ino, info.st_mode, info.st_size,
                   info.st_mtime_ns, info.st_ctime_ns)


def identity(info):
    return info.st_dev, info.st_ino


def name_key(name: str) -> str:
    return unicodedata.normalize("NFC", name).casefold()


def invalid_name(name: str, folder: Path) -> str:
    if not name or name in {".", ".."} or name.startswith("."):
        return "O nome ficou vazio, oculto ou inválido."
    if any(c in '<>:"/\\|?*' or unicodedata.category(c) == "Cc" for c in name):
        return "O nome contém caracteres não permitidos."
    if name.endswith((" ", ".")):
        return "O nome não pode terminar em espaço ou ponto."
    base = name.split(".")[0].rstrip(" ").upper()
    if re.fullmatch(r"CON|PRN|AUX|NUL|(?:COM|LPT)[1-9¹²³]|CONIN\$|CONOUT\$", base):
        return "Nome reservado pelo Windows."
    try:
        if len(name.encode("utf-8")) > 255 or len(name.encode("utf-16-le")) // 2 > 255:
            return "Nome excessivamente longo."
        # Conservative Win32 limit; no long-path opt-in required.
        if os.name == "nt" and len(str(folder / name).encode("utf-16-le")) // 2 >= 260:
            return "Caminho excede o limite conservador de 259 caracteres."
    except UnicodeError:
        return "O nome contém uma sequência Unicode inválida."
    return ""


def ignored_reason(path: Path, info) -> str:
    if path.name.startswith(".") or getattr(info, "st_file_attributes", 0) & 2:
        return "Arquivo oculto."
    if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
        return "Link simbólico ou ponto de nova análise."
    if not stat.S_ISREG(info.st_mode):
        return "Não é um arquivo regular (subpastas não são percorridas)."
    return ""


@dataclass(frozen=True)
class Operation:
    original: str
    proposed: str
    status: str
    message: str = ""
    fingerprint: Fingerprint | None = None


@dataclass(frozen=True)
class Plan:
    folder: Path
    folder_identity: tuple[int, int]
    rule: Rule
    operations: tuple[Operation, ...]

    @property
    def eligible(self):
        return sum(op.fingerprint is not None for op in self.operations)


def build_plan(folder: str | Path, rule: Rule) -> Plan:
    rule.validate()
    folder = Path(folder).expanduser().resolve(strict=True)
    folder_info = folder.stat()
    if not stat.S_ISDIR(folder_info.st_mode):
        raise NotADirectoryError("Selecione uma pasta.")
    entries = sorted(folder.iterdir(), key=lambda p: (name_key(p.name), p.name))
    occupied = {}
    for entry in entries:
        occupied.setdefault(name_key(entry.name), []).append(entry.name)
    operations = []
    for entry in entries:
        try:
            info = entry.lstat()
            reason = ignored_reason(entry, info)
            if reason:
                operations.append(Operation(entry.name, entry.name, IGNORED, reason))
                continue
            proposed = rule.apply(entry.name)
            reason = invalid_name(proposed, folder)
            status = INVALID if reason else UNCHANGED if proposed == entry.name else READY
            if status == READY and name_key(proposed) in occupied:
                status, reason = CONFLICT, "Destino já ocupado ou equivalente por caixa/Unicode."
            operations.append(Operation(entry.name, proposed, status, reason, Fingerprint.of(info)))
        except OSError as exc:
            operations.append(Operation(entry.name, entry.name, INVALID, str(exc)))
    counts = {}
    for op in operations:
        if op.fingerprint is not None:
            counts[name_key(op.proposed)] = counts.get(name_key(op.proposed), 0) + 1
    operations = [replace(op, status=CONFLICT, message="Mais de um arquivo propõe o mesmo destino.")
                  if op.status == READY and counts[name_key(op.proposed)] > 1 else op
                  for op in operations]
    return Plan(folder, identity(folder_info), rule, tuple(operations))
