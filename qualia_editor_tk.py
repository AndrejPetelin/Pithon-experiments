"""
qualia_editor_tk.py
Qualia Editor — desktop writing tool with AI editorial feedback.
Skeleton: layout and widgets only, no AI logic yet.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext


# ── Colours ──────────────────────────────────────────────────────────────────
BG          = "#0e0e10"
SURFACE     = "#16161a"
SURFACE2    = "#1e1e24"
BORDER      = "#2a2a35"
ACCENT      = "#c9a84c"
TEXT        = "#e8e4d9"
TEXT_DIM    = "#7a7870"
TEXT_MID    = "#b0ac9f"
GREEN       = "#50b478"

FONT_BODY   = ("Georgia", 12)
FONT_MONO   = ("Courier New", 10)
FONT_SMALL  = ("Courier New", 9)
FONT_TITLE  = ("Georgia", 14, "bold")


class QualiaEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Qualia Editor")
        self.root.configure(bg=BG)
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)

        self._build_header()
        self._build_workspace()
        self._build_statusbar()

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        header = tk.Frame(self.root, bg=SURFACE, height=48)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        # Logo
        tk.Label(
            header, text="Qualia Editor",
            bg=SURFACE, fg=ACCENT,
            font=FONT_TITLE
        ).pack(side=tk.LEFT, padx=16, pady=10)

        tk.Label(
            header, text="v0.1",
            bg=SURFACE, fg=TEXT_DIM,
            font=FONT_SMALL
        ).pack(side=tk.LEFT, pady=10)

        # Right side buttons
        tk.Button(
            header, text="New",
            bg=SURFACE, fg=TEXT_MID,
            font=FONT_SMALL,
            relief=tk.FLAT,
            activebackground=SURFACE2,
            activeforeground=ACCENT,
            command=self._new_document
        ).pack(side=tk.RIGHT, padx=8, pady=10)

        tk.Button(
            header, text="Open",
            bg=SURFACE, fg=TEXT_MID,
            font=FONT_SMALL,
            relief=tk.FLAT,
            activebackground=SURFACE2,
            activeforeground=ACCENT,
            command=self._open_file
        ).pack(side=tk.RIGHT, padx=4, pady=10)

        tk.Button(
            header, text="Save",
            bg=SURFACE, fg=TEXT_MID,
            font=FONT_SMALL,
            relief=tk.FLAT,
            activebackground=SURFACE2,
            activeforeground=ACCENT,
            command=self._save_file
        ).pack(side=tk.RIGHT, padx=4, pady=10)

    # ── Main workspace ────────────────────────────────────────────────────────
    def _build_workspace(self):
        workspace = tk.Frame(self.root, bg=BG)
        workspace.pack(fill=tk.BOTH, expand=True)

        self._build_editor_pane(workspace)
        self._build_editorial_pane(workspace)

    # ── Left: manuscript editor ───────────────────────────────────────────────
    def _build_editor_pane(self, parent):
        pane = tk.Frame(parent, bg=BG)
        pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Pane header
        pane_header = tk.Frame(pane, bg=SURFACE, height=32)
        pane_header.pack(fill=tk.X)
        pane_header.pack_propagate(False)

        tk.Label(
            pane_header, text="MANUSCRIPT",
            bg=SURFACE, fg=TEXT_DIM,
            font=FONT_SMALL
        ).pack(side=tk.LEFT, padx=12, pady=8)

        self.wordcount_label = tk.Label(
            pane_header, text="0 words",
            bg=SURFACE, fg=TEXT_DIM,
            font=FONT_SMALL
        )
        self.wordcount_label.pack(side=tk.RIGHT, padx=12, pady=8)

        # Separator
        tk.Frame(pane, bg=BORDER, height=1).pack(fill=tk.X)

        # Text editor
        self.editor = tk.Text(
            pane,
            bg=BG, fg=TEXT,
            font=FONT_BODY,
            insertbackground=ACCENT,
            selectbackground=ACCENT,
            selectforeground=BG,
            relief=tk.FLAT,
            padx=40, pady=32,
            wrap=tk.WORD,
            spacing1=4, spacing3=4
        )
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.editor.bind("<KeyRelease>", self._on_editor_change)

        # Scrollbar
        scrollbar = tk.Scrollbar(self.editor, bg=SURFACE, troughcolor=BG)
        self.editor.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.editor.yview)

    # ── Right: editorial panel ────────────────────────────────────────────────
    def _build_editorial_pane(self, parent):
        # Vertical separator
        tk.Frame(parent, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

        pane = tk.Frame(parent, bg=SURFACE, width=380)
        pane.pack(side=tk.LEFT, fill=tk.Y)
        pane.pack_propagate(False)

        # Pane header
        pane_header = tk.Frame(pane, bg=SURFACE, height=32)
        pane_header.pack(fill=tk.X)
        pane_header.pack_propagate(False)

        tk.Label(
            pane_header, text="EDITORIAL",
            bg=SURFACE, fg=TEXT_DIM,
            font=FONT_SMALL
        ).pack(side=tk.LEFT, padx=12, pady=8)

        self.note_count_label = tk.Label(
            pane_header, text="0 notes",
            bg=SURFACE, fg=TEXT_DIM,
            font=FONT_SMALL
        )
        self.note_count_label.pack(side=tk.RIGHT, padx=12, pady=8)

        tk.Frame(pane, bg=BORDER, height=1).pack(fill=tk.X)

        # Controls area
        controls = tk.Frame(pane, bg=SURFACE, padx=12, pady=10)
        controls.pack(fill=tk.X)

        # Work type dropdown
        type_row = tk.Frame(controls, bg=SURFACE)
        type_row.pack(fill=tk.X, pady=3)

        tk.Label(
            type_row, text="TYPE",
            bg=SURFACE, fg=TEXT_DIM,
            font=FONT_SMALL, width=6, anchor=tk.W
        ).pack(side=tk.LEFT)

        self.work_type = ttk.Combobox(
            type_row,
            values=["Novel", "Short story", "Game dialogue",
                    "Screenplay", "Poetry", "Technical writing"],
            state="readonly",
            font=FONT_SMALL
        )
        self.work_type.set("Novel")
        self.work_type.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Model dropdown
        model_row = tk.Frame(controls, bg=SURFACE)
        model_row.pack(fill=tk.X, pady=3)

        tk.Label(
            model_row, text="MODEL",
            bg=SURFACE, fg=TEXT_DIM,
            font=FONT_SMALL, width=6, anchor=tk.W
        ).pack(side=tk.LEFT)

        self.ai_model = ttk.Combobox(
            model_row,
            values=["Claude (editorial)", "Grok (punchy)",
                    "Gemini (localisation)", "Mistral (local/offline)"],
            state="readonly",
            font=FONT_SMALL
        )
        self.ai_model.set("Claude (editorial)")
        self.ai_model.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Notes to editor
        tk.Label(
            controls, text="NOTES TO EDITOR",
            bg=SURFACE, fg=TEXT_DIM,
            font=FONT_SMALL, anchor=tk.W
        ).pack(fill=tk.X, pady=(8, 3))

        self.editor_notes = tk.Text(
            controls,
            bg=SURFACE2, fg=TEXT,
            font=FONT_BODY,
            insertbackground=ACCENT,
            relief=tk.FLAT,
            height=4,
            wrap=tk.WORD,
            padx=8, pady=6
        )
        self.editor_notes.pack(fill=tk.X)

        # Buttons
        btn_row = tk.Frame(controls, bg=SURFACE)
        btn_row.pack(fill=tk.X, pady=8)

        self.analyse_btn = tk.Button(
            btn_row, text="Analyse manuscript",
            bg=ACCENT, fg=BG,
            font=FONT_SMALL,
            relief=tk.FLAT,
            activebackground="#e0bb60",
            activeforeground=BG,
            command=self._analyse
        )
        self.analyse_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))

        self.selection_btn = tk.Button(
            btn_row, text="Selection",
            bg=SURFACE2, fg=TEXT_MID,
            font=FONT_SMALL,
            relief=tk.FLAT,
            activebackground=BORDER,
            activeforeground=ACCENT,
            command=self._analyse_selection
        )
        self.selection_btn.pack(side=tk.LEFT)

        tk.Frame(pane, bg=BORDER, height=1).pack(fill=tk.X)

        # Comments area
        self.comments_frame = tk.Frame(pane, bg=SURFACE)
        self.comments_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.no_comments_label = tk.Label(
            self.comments_frame,
            text="Editorial notes will appear here.\nWrite or paste text, then click Analyse.",
            bg=SURFACE, fg=TEXT_DIM,
            font=FONT_BODY,
            justify=tk.CENTER
        )
        self.no_comments_label.pack(expand=True)

    # ── Status bar ────────────────────────────────────────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=SURFACE, height=26)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        tk.Frame(self.root, bg=BORDER, height=1).pack(fill=tk.X, side=tk.BOTTOM)

        self.status_words  = tk.Label(bar, text="WORDS  0", bg=SURFACE, fg=TEXT_DIM, font=FONT_SMALL)
        self.status_notes  = tk.Label(bar, text="NOTES  0", bg=SURFACE, fg=TEXT_DIM, font=FONT_SMALL)
        self.status_msg    = tk.Label(bar, text="Ready",    bg=SURFACE, fg=TEXT_DIM, font=FONT_SMALL)

        self.status_words.pack(side=tk.LEFT, padx=16, pady=4)
        self.status_notes.pack(side=tk.LEFT, padx=16, pady=4)
        self.status_msg.pack(side=tk.LEFT, padx=16, pady=4)

    # ── Callbacks (stubs for now) ─────────────────────────────────────────────
    def _on_editor_change(self, event=None):
        text = self.editor.get("1.0", tk.END)
        words = len(text.split()) if text.strip() else 0
        self.wordcount_label.config(text=f"{words} words")
        self.status_words.config(text=f"WORDS  {words}")

    def _analyse(self):
        self.status_msg.config(text="Analysing… (not yet implemented)")

    def _analyse_selection(self):
        self.status_msg.config(text="Selection analysis… (not yet implemented)")

    def _new_document(self):
        self.editor.delete("1.0", tk.END)
        self.status_msg.config(text="New document")

    def _open_file(self):
        self.status_msg.config(text="Open… (not yet implemented)")

    def _save_file(self):
        self.status_msg.config(text="Save… (not yet implemented)")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = QualiaEditor(root)
    root.mainloop()
