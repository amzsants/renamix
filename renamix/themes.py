"""Small, offline theme catalog, ttk styling and user preference storage."""

from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
import tempfile
from tkinter import ttk

DEFAULT_THEME = "original"


def blend(first, second, amount):
    channels = [round(int(first[i:i + 2], 16) * (1 - amount)
                      + int(second[i:i + 2], 16) * amount) for i in (1, 3, 5)]
    return "#" + "".join(f"{channel:02X}" for channel in channels)


def luminance(color):
    values = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    values = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in values]
    return sum(v * weight for v, weight in zip(values, (.2126, .7152, .0722)))


def contrast(first, second):
    bright, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (bright + .05) / (dark + .05)


def readable_on(color):
    return max(("#FFFFFF", "#000000"), key=lambda text: contrast(color, text))


@dataclass(frozen=True)
class Theme:
    name: str
    description: str
    background: str
    surface: str
    accent: str
    text: str
    secondary: str

    @property
    def light(self):
        return luminance(self.background) > .5

    @property
    def border(self):
        return "#30363D" if self.name == "Renamix Original" else blend(self.surface, self.text, .24)

    @property
    def muted(self):
        return "#8B949E" if self.name == "Renamix Original" else blend(self.surface, self.text, .74)

    @property
    def selection(self):
        return blend(self.surface, self.accent, .3)

    @property
    def error(self):
        return "#A11935" if self.light else "#FF8993"

    @property
    def warning(self):
        return "#805000" if self.light else "#F2C36B"

    @property
    def success(self):
        return "#146447" if self.light else "#84D8AE"


THEMES = {
    "original": Theme("Renamix Original", "Escuro, minimalista e com destaque vermelho.",
                      "#0D1117", "#161B22", "#E63946", "#E6EDF3", "#30363D"),
    "chatgpt-dark": Theme("ChatGPT Dark", "Cinza profundo e verde discreto.",
                          "#151719", "#24282B", "#10A37F", "#F0F0F0", "#42645B"),
    "chatgpt-light": Theme("ChatGPT Light", "Claro, simples e com destaque verde.",
                           "#F7F7F5", "#FFFFFF", "#087F62", "#202123", "#C8DED7"),
    "codex-dark": Theme("Codex Dark", "Azul tecnológico com detalhes em turquesa.",
                        "#101820", "#1B2935", "#64C8BE", "#E8F0F4", "#345663"),
    "codex-light": Theme("Codex Light", "Claro, profissional e discreto.",
                         "#F1F5F7", "#FFFFFF", "#187E85", "#1C303A", "#C3DCDF"),
    "sakura": Theme("Sakura", "Rosa suave e lilás em uma noite tranquila.",
                    "#281C30", "#39283F", "#F0A7C6", "#FFF0F7", "#A77AAB"),
    "dark-beach": Theme("Dark Beach", "Lavanda, mar noturno e atmosfera dreamwave.",
                        "#161430", "#252348", "#9D82DB", "#F0ECFF", "#68C8D9"),
    "vampire": Theme("Vampire", "Preto, vinho e vermelho em um visual gótico.",
                     "#090709", "#1B1015", "#B10F2E", "#F5E8EB", "#541221"),
}


def get_theme(theme_id):
    if not isinstance(theme_id, str) or theme_id not in THEMES:
        raise ValueError("Tema desconhecido.")
    return THEMES[theme_id]


def settings_path():
    home = Path.home()
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or home / "AppData" / "Roaming")
        if not base.is_absolute():
            base = home / "AppData" / "Roaming"
        return base / "Renamix" / "settings.json"
    if sys.platform == "darwin":
        return home / "Library" / "Application Support" / "Renamix" / "settings.json"
    base = Path(os.environ.get("XDG_CONFIG_HOME") or home / ".config")
    if not base.is_absolute():
        base = home / ".config"
    return base / "renamix" / "settings.json"


def load_theme(path=None):
    try:
        path = Path(path) if path is not None else settings_path()
        if path.stat().st_size > 4096:
            return DEFAULT_THEME
        data = json.loads(path.read_text(encoding="utf-8"))
        theme_id = data.get("theme") if isinstance(data, dict) else None
        get_theme(theme_id)
        return theme_id
    except (OSError, ValueError, UnicodeError, RecursionError):
        return DEFAULT_THEME


def save_theme(theme_id, path=None):
    get_theme(theme_id)
    path = Path(path) if path is not None else settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".settings-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump({"theme": theme_id}, stream, ensure_ascii=False)
            stream.write("\n")
        # Only this application's configuration is replaced, never user files.
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def apply_theme(root, theme_id, tree=None, comboboxes=()):
    theme = get_theme(theme_id)
    style = ttk.Style(root)
    if style.theme_use() != "clam":
        style.theme_use("clam")
    bg, panel, text = theme.background, theme.surface, theme.text
    border, muted = theme.border, theme.muted
    active = blend(panel, theme.secondary, .35)
    root.configure(bg=bg)
    style.configure(".", background=bg, foreground=text, font=("Segoe UI", 10),
                    bordercolor=border, lightcolor=border, darkcolor=border,
                    focuscolor=theme.accent, troughcolor=bg)
    style.configure("TFrame", background=bg)
    style.configure("TLabel", background=bg, foreground=text)
    style.configure("Muted.TLabel", foreground=muted)
    style.configure("Title.TLabel", font=("Segoe UI", 25, "bold"))
    style.configure("Section.TLabel", font=("Segoe UI", 18, "bold"))
    style.configure("TButton", background=panel, foreground=text, padding=(14, 6), borderwidth=1)
    style.map("TButton", background=[("disabled", panel), ("pressed", active), ("active", active)],
              foreground=[("disabled", muted), ("!disabled", text)])
    style.configure("Accent.TButton", background=theme.accent, foreground=readable_on(theme.accent))
    style.map("Accent.TButton", background=[("disabled", border), ("pressed", theme.accent),
                                            ("active", theme.accent)],
              foreground=[("disabled", readable_on(border)), ("!disabled", readable_on(theme.accent))])
    for control in ("TEntry", "TCombobox"):
        style.configure(control, fieldbackground=panel, foreground=text, insertcolor=text,
                        padding=5, arrowcolor=text, selectbackground=theme.selection,
                        selectforeground=readable_on(theme.selection))
        style.map(control, fieldbackground=[("disabled", bg), ("readonly", panel)],
                  foreground=[("disabled", muted), ("readonly", text)],
                  bordercolor=[("focus", theme.accent)])
    style.configure("Treeview", background=panel, fieldbackground=panel,
                    foreground=text, rowheight=30, borderwidth=0)
    style.configure("Treeview.Heading", background=border, foreground=readable_on(border), padding=8)
    style.map("Treeview.Heading", background=[("active", active)], foreground=[("active", text)])
    style.map("Treeview", background=[("selected", theme.selection)],
              foreground=[("selected", readable_on(theme.selection))])
    style.configure("TLabelframe", background=bg)
    style.configure("TLabelframe.Label", background=bg, foreground=muted)
    style.configure("TNotebook", background=bg, borderwidth=0, tabmargins=(0, 0, 0, 0))
    style.configure("TNotebook.Tab", background=panel, foreground=muted, padding=(16, 5))
    style.map("TNotebook.Tab", background=[("selected", bg), ("active", active)],
              foreground=[("selected", text), ("active", text)],
              lightcolor=[("selected", theme.accent)])
    for orientation in ("Vertical", "Horizontal"):
        control = f"{orientation}.TScrollbar"
        style.configure(control, background=border, troughcolor=bg, arrowcolor=text,
                        bordercolor=border, lightcolor=border, darkcolor=border)
        style.map(control, background=[("pressed", theme.accent), ("active", active)])
    style.configure("Card.TFrame", background=panel, borderwidth=1, relief="solid")
    style.configure("Card.TLabel", background=panel, foreground=muted, font=("Segoe UI", 9))
    style.configure("Card.TRadiobutton", background=panel, foreground=text, padding=(0, 2),
                    indicatorbackground=bg, indicatorforeground=theme.accent)
    style.map("Card.TRadiobutton", background=[("active", panel)],
              foreground=[("active", text)], indicatorbackground=[("selected", theme.accent)])
    for option, color in (("background", panel), ("foreground", text),
                          ("selectBackground", theme.selection),
                          ("selectForeground", readable_on(theme.selection))):
        root.option_add(f"*TCombobox*Listbox.{option}", color)
    for combo in comboboxes:
        # Refresh a popdown that may already have been created in the old theme.
        popdown = root.tk.call("ttk::combobox::PopdownWindow", str(combo))
        root.tk.call(f"{popdown}.f.l", "configure", "-background", panel, "-foreground", text,
                     "-selectbackground", theme.selection, "-selectforeground", readable_on(theme.selection))
    if tree is not None:
        for tag, color in (("error", theme.error), ("warning", theme.warning),
                           ("success", theme.success), ("muted", muted)):
            tree.tag_configure(tag, foreground=color)
