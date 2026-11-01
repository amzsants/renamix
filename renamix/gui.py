"""Tkinter interface. All filesystem work runs outside the event loop."""

from pathlib import Path
from queue import Empty, Queue
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import __version__
from .executor import execute, export_csv
from .planner import READY, build_plan
from .planner import Rule
from .themes import DEFAULT_THEME, THEMES, apply_theme, load_theme, save_theme

KINDS = {"Prefixo": "prefix", "Sufixo": "suffix", "Substituição": "replace"}


class App:
    def __init__(self, root, settings_path=None):
        self.root = root
        self.settings_path = settings_path
        self.theme_id = tk.StringVar(master=root, value=load_theme(settings_path))
        self.theme_current = tk.StringVar(master=root)
        self.theme_message = tk.StringVar(master=root)
        self.plan = None
        self.report = None
        self.busy = False
        self.pending = None
        self.queue = Queue()
        self.folder = tk.StringVar()
        self.kind = tk.StringVar(value="Prefixo")
        self.text = tk.StringVar()
        self.replacement = tk.StringVar()
        self.status = tk.StringVar(value="Selecione uma pasta e configure uma regra para começar.")
        self.summary = tk.StringVar(value="Nenhuma operação executada.")
        root.title(f"Renamix {__version__}")
        width = min(1040, root.winfo_screenwidth() - 80)
        # Reserve space for window decorations and the Windows taskbar.
        height = min(680, root.winfo_screenheight() - 108)
        root.geometry(f"{width}x{height}+40+16")
        root.minsize(900, 660)
        root.protocol("WM_DELETE_WINDOW", self.close)
        apply_theme(root, self.theme_id.get())
        self.build()
        self.refresh_theme()
        for variable in (self.folder, self.kind, self.text, self.replacement):
            variable.trace_add("write", self.changed)
        root.after(80, self.poll)

    def build(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.notebook.enable_traversal()
        main = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(main, text="Renomear", underline=0)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        # Only the preview absorbs resizing; keep room for headings and rows.
        main.rowconfigure(4, weight=1, minsize=160)
        heading = ttk.Frame(main)
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ttk.Label(heading, text="RENAMIX", style="Title.TLabel").pack(side="left")
        ttk.Label(heading, text="Safe batch file renaming for local workflows",
                  style="Muted.TLabel").pack(side="left", padx=(16, 0))
        folder = ttk.LabelFrame(main, text="01  Pasta local", padding=4)
        folder.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        folder.columnconfigure(0, weight=1)
        path = ttk.Entry(folder, textvariable=self.folder)
        path.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        choose = ttk.Button(folder, text="Selecionar pasta…", command=self.choose)
        choose.grid(row=0, column=1)
        ttk.Label(folder, text="Somente arquivos diretos • Sem subpastas, ocultos ou links",
                  style="Muted.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 0))
        rules = ttk.LabelFrame(main, text="02  Regra de renomeação", padding=4)
        rules.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        rules.columnconfigure(1, weight=1)
        rules.columnconfigure(2, weight=1)
        for col, label in enumerate(("Regra", "Texto / buscar", "Substituir por")):
            ttk.Label(rules, text=label).grid(row=0, column=col, sticky="w", pady=(0, 4))
        kind = ttk.Combobox(rules, textvariable=self.kind, values=list(KINDS), state="readonly", width=16)
        kind.grid(row=1, column=0, sticky="ew", padx=(0, 12))
        text = ttk.Entry(rules, textvariable=self.text)
        text.grid(row=1, column=1, sticky="ew", padx=(0, 12))
        self.replace_entry = ttk.Entry(rules, textvariable=self.replacement, state="disabled")
        self.replace_entry.grid(row=1, column=2, sticky="ew")
        ttk.Label(rules, text="Uma regra por vez. Todas as extensões são preservadas (ex.: .tar.gz).",
                  style="Muted.TLabel").grid(row=2, column=0, columnspan=3, sticky="w", pady=(2, 0))
        ttk.Label(main, textvariable=self.status, wraplength=930).grid(row=3, column=0, sticky="ew", pady=(0, 6))
        table = ttk.Frame(main)
        table.grid(row=4, column=0, sticky="nsew")
        table.rowconfigure(0, weight=1)
        table.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(table, columns=("old", "new", "status", "detail"),
                                 show="headings", height=4)
        for name, title, width in (("old", "Nome original", 240), ("new", "Nome proposto", 240),
                                   ("status", "Status", 110), ("detail", "Detalhes", 290)):
            self.tree.heading(name, text=title)
            self.tree.column(name, width=width, minwidth=100)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal = ttk.Scrollbar(table, orient="horizontal", command=self.tree.xview)
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        actions = ttk.Frame(main)
        actions.grid(row=5, column=0, sticky="ew", pady=(8, 8))
        actions.columnconfigure(1, weight=1)
        self.preview_button = ttk.Button(actions, text="Analisar novamente", command=self.preview)
        self.preview_button.grid(row=0, column=0, sticky="w")
        self.export_button = ttk.Button(actions, text="Exportar CSV…", command=self.export, state="disabled")
        self.export_button.grid(row=0, column=2, padx=(12, 12))
        self.apply_button = ttk.Button(actions, text="Renomear arquivos", style="Accent.TButton",
                                      command=self.apply, state="disabled")
        self.apply_button.grid(row=0, column=3)
        ttk.Label(main, textvariable=self.summary, style="Muted.TLabel", wraplength=930).grid(
            row=6, column=0, sticky="ew")
        self.controls = [(path, "normal"), (choose, "normal"), (kind, "readonly"), (text, "normal")]
        self.rule_combo = kind
        self.build_themes()

    def build_themes(self):
        page = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(page, text="Temas", underline=0)
        page.columnconfigure(0, weight=1)
        page.rowconfigure(2, weight=1)
        ttk.Label(page, text="Personalização", style="Section.TLabel").grid(
            row=0, column=0, sticky="w")
        ttk.Label(page, text="Escolha uma paleta. A aparência muda imediatamente nas duas abas.",
                  style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 10))
        catalog = ttk.Frame(page)
        catalog.grid(row=2, column=0, sticky="nsew")
        for column in range(2):
            catalog.columnconfigure(column, weight=1, uniform="themes")
        for row in range(4):
            catalog.rowconfigure(row, weight=1, uniform="themes")
        for index, (theme_id, theme) in enumerate(THEMES.items()):
            card = ttk.Frame(catalog, style="Card.TFrame", padding=8)
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=4, pady=4)
            card.columnconfigure(0, weight=1)
            ttk.Radiobutton(card, text=theme.name, value=theme_id, variable=self.theme_id,
                            style="Card.TRadiobutton", command=self.select_theme).grid(
                                row=0, column=0, sticky="w")
            description = ttk.Label(card, text=theme.description, style="Card.TLabel", wraplength=360)
            description.grid(row=1, column=0, sticky="ew", pady=(2, 4))
            card.bind("<Configure>", lambda event, label=description:
                      label.configure(wraplength=max(100, event.width - 20)))
            swatches = ttk.Frame(card, style="Card.TFrame", borderwidth=0)
            swatches.grid(row=2, column=0, sticky="w")
            for color in (theme.background, theme.surface, theme.accent, theme.secondary):
                tk.Label(swatches, bg=color, width=4, height=1, font=("Segoe UI", 4),
                         borderwidth=0).pack(side="left", padx=(0, 3))
        footer = ttk.Frame(page)
        footer.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        footer.columnconfigure(0, weight=1)
        ttk.Label(footer, textvariable=self.theme_current).grid(row=0, column=0, sticky="w")
        ttk.Button(footer, text="Restaurar tema original", command=lambda: self.select_theme(DEFAULT_THEME)).grid(
            row=0, column=1, sticky="e")
        ttk.Label(page, textvariable=self.theme_message, style="Muted.TLabel", wraplength=840).grid(
            row=4, column=0, sticky="w", pady=(6, 0))

    def refresh_theme(self):
        theme_id = self.theme_id.get()
        apply_theme(self.root, theme_id, tree=self.tree, comboboxes=(self.rule_combo,))
        self.theme_current.set(f"Tema atual: {THEMES[theme_id].name}")

    def select_theme(self, theme_id=None):
        if theme_id is not None:
            self.theme_id.set(theme_id)
        self.refresh_theme()
        try:
            save_theme(self.theme_id.get(), self.settings_path)
            self.theme_message.set("Preferência salva automaticamente para a próxima abertura.")
        except OSError:
            self.theme_message.set("Tema aplicado nesta sessão. Não foi possível salvar a preferência.")

    def choose(self):
        selected = filedialog.askdirectory(parent=self.root, title="Selecionar pasta")
        if selected:
            self.folder.set(selected)

    def changed(self, *_):
        self.plan = None
        self.apply_button.configure(state="disabled")
        self.replace_entry.configure(state="normal" if self.kind.get() == "Substituição" else "disabled")
        self.status.set("Prévia desatualizada. Aguardando uma regra válida…")
        self.tree.delete(*self.tree.get_children())
        if self.pending:
            self.root.after_cancel(self.pending)
        self.pending = self.root.after(450, self.preview)

    def start(self, task, function):
        self.busy = True
        for widget, _ in self.controls:
            widget.configure(state="disabled")
        for widget in (self.replace_entry, self.preview_button, self.apply_button, self.export_button):
            widget.configure(state="disabled")
        self.status.set("Analisando pasta…" if task == "preview" else "Renomeando arquivos… Aguarde.")

        def work():
            try:
                self.queue.put((task, function(), None))
            except Exception as exc:
                self.queue.put((task, None, exc))
        Thread(target=work, daemon=True).start()

    def preview(self):
        if self.pending:
            self.root.after_cancel(self.pending)
            self.pending = None
        if self.busy:
            return
        self.plan = None
        self.apply_button.configure(state="disabled")
        try:
            if not self.folder.get().strip():
                raise ValueError("Selecione uma pasta.")
            rule = Rule(KINDS[self.kind.get()], self.text.get(), self.replacement.get())
            rule.validate()
            folder = self.folder.get()
            self.start("preview", lambda: build_plan(folder, rule))
        except (ValueError, KeyError) as exc:
            self.status.set(str(exc))

    def poll(self):
        try:
            task, value, error = self.queue.get_nowait()
        except Empty:
            self.root.after(80, self.poll)
            return
        self.busy = False
        for widget, state in self.controls:
            widget.configure(state=state)
        self.replace_entry.configure(state="normal" if self.kind.get() == "Substituição" else "disabled")
        self.preview_button.configure(state="normal")
        if error:
            self.status.set(f"Não foi possível concluir: {error}")
            messagebox.showerror("Renamix", str(error), parent=self.root)
        else:
            self.tree.delete(*self.tree.get_children())
            if task == "preview":
                self.plan = value
                ready = sum(op.status == READY for op in value.operations)
                problems = sum(op.status in {"Conflito", "Inválido"} for op in value.operations)
                self.status.set(f"{value.eligible} arquivo(s) elegível(is) • {ready} pronto(s) • {problems} problema(s)")
                for op in value.operations:
                    self.add_row(op.original, op.proposed, op.status, op.message)
                self.apply_button.configure(state="normal" if ready else "disabled")
            else:
                self.plan = None
                self.report = value
                self.summary.set(value.summary())
                self.status.set("Operação concluída. Consulte os detalhes. Para outra operação, analise novamente.")
                for row in value.results:
                    self.add_row(row.original, row.proposed, row.outcome, row.message)
        self.export_button.configure(state="normal" if self.report else "disabled")
        self.root.after(80, self.poll)

    def add_row(self, original, proposed, status, detail):
        tag = ("error" if status in {"Inválido", "Falha"} else "warning" if status == "Conflito"
               else "success" if status in {"Pronto", "Renomeado"} else "muted")
        self.tree.insert("", "end", values=(original, proposed, status, detail), tags=(tag,))

    def apply(self):
        if self.busy or self.plan is None:
            return
        plan = self.plan
        count = sum(op.status == READY for op in plan.operations)
        if messagebox.askyesno("Confirmar renomeação", f"Renomear {count} arquivo(s) em:\n{plan.folder}\n\n"
                               "Conflitos serão recusados. Não há desfazer automático.\nContinuar?", parent=self.root):
            if self.pending:
                self.root.after_cancel(self.pending)
                self.pending = None
            self.start("execute", lambda: execute(plan))

    def export(self):
        if self.report is None:
            return
        name = filedialog.asksaveasfilename(parent=self.root, title="Exportar relatório (use um nome novo)",
                                          defaultextension=".csv", filetypes=[("CSV", "*.csv")],
                                          initialfile="renamix-relatorio.csv")
        if name:
            try:
                export_csv(self.report, Path(name))
                self.status.set(f"Relatório exportado: {name}")
            except OSError as exc:
                messagebox.showerror("Não foi possível exportar", f"{exc}\nEscolha um nome ainda não utilizado.", parent=self.root)

    def close(self):
        if self.busy:
            messagebox.showinfo("Aguarde", "Aguarde a conclusão antes de fechar o aplicativo.", parent=self.root)
            return
        self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()
