"""
Qualia Editor - AI-assisted text editor with editorial comments
Qualia Software

Two-panel layout:
  Left  — original text with highlights linked to comments
  Right — editorial comment threads with pushback dialog

AI backends: Claude, Grok, Gemini, Mistral (local via Ollama)
Offline-capable via local Mistral.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from collections import Counter
import json
import os
import re

# ── Placeholder AI call (wire up real APIs later) ─────────────────────────────

def call_ai(provider, system_prompt, user_prompt):
    """
    Placeholder for AI API calls.
    Replace each branch with real API integration.
    """
    if provider == "Local Mistral (Ollama)":
        try:
            import requests
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "mistral", "prompt": f"{system_prompt}\n\n{user_prompt}", "stream": False},
                timeout=60
            )
            return response.json().get("response", "No response from Ollama.")
        except Exception as e:
            return f"[Ollama not available: {e}]"
    else:
        # Placeholder for Claude / Grok / Gemini
        return (
            f"[{provider} response placeholder]\n\n"
            f"This is where {provider} would provide editorial notes.\n"
            f"Wire up the real API key to activate."
        )

# ── Comment data model ────────────────────────────────────────────────────────

class Comment:
    _id_counter = 0

    def __init__(self, text_snippet, ai_note, tag):
        Comment._id_counter += 1
        self.id = Comment._id_counter
        self.text_snippet = text_snippet
        self.ai_note = ai_note
        self.tag = tag  # tkinter tag name for the highlight
        self.thread = [("Editor", ai_note)]  # list of (speaker, message)
        self.resolved = False

# ── Main Application ──────────────────────────────────────────────────────────

class QualiaEditor:

    WORK_TYPES = [
        "Novel (literary fiction)",
        "Novel (genre fiction)",
        "Short story",
        "Game dialogue (.frank)",
        "Screenplay",
        "Technical writing",
        "Poetry",
        "Non-fiction / memoir",
    ]

    PROVIDERS = [
        "Local Mistral (Ollama)",
        "Claude (Anthropic)",
        "Grok (xAI)",
        "Gemini (Google)",
        "Le Chat (Mistral cloud)",
    ]

    HIGHLIGHT_COLOR  = "#FFD700"   # gold — unresolved
    RESOLVED_COLOR   = "#C8F7C5"   # pale green — resolved
    SELECTED_COLOR   = "#FFB347"   # orange — currently selected

    def __init__(self, root):
        self.root = root
        self.root.title("Qualia Editor")
        self.root.geometry("1200x750")
        self.root.configure(bg="#1E1E2E")

        self.comments = {}       # tag -> Comment
        self.selected_tag = None
        self.current_file = None

        self._build_menu()
        self._build_toolbar()
        self._build_main_panels()
        self._build_status_bar()

    # ── Menu ──────────────────────────────────────────────────────────────────

    def _build_menu(self):
        menubar = tk.Menu(self.root, bg="#2E2E4E", fg="white")

        file_menu = tk.Menu(menubar, tearoff=0, bg="#2E2E4E", fg="white")
        file_menu.add_command(label="New",        command=self.new_file)
        file_menu.add_command(label="Open...",    command=self.open_file)
        file_menu.add_command(label="Save",       command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit",       command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0, bg="#2E2E4E", fg="white")
        edit_menu.add_command(label="Word Frequency", command=self.show_word_frequency)
        edit_menu.add_command(label="Clear All Comments", command=self.clear_all_comments)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        self.root.config(menu=menubar)

    # ── Toolbar ───────────────────────────────────────────────────────────────

    def _build_toolbar(self):
        toolbar = tk.Frame(self.root, bg="#2E2E4E", pady=6)
        toolbar.pack(fill="x", side="top")

        tk.Label(toolbar, text="Work type:", bg="#2E2E4E", fg="#AAAACC",
                 font=("Arial", 10)).pack(side="left", padx=(12, 4))

        self.work_type_var = tk.StringVar(value=self.WORK_TYPES[0])
        work_dropdown = ttk.Combobox(toolbar, textvariable=self.work_type_var,
                                     values=self.WORK_TYPES, width=26, state="readonly")
        work_dropdown.pack(side="left", padx=4)

        tk.Label(toolbar, text="AI provider:", bg="#2E2E4E", fg="#AAAACC",
                 font=("Arial", 10)).pack(side="left", padx=(16, 4))

        self.provider_var = tk.StringVar(value=self.PROVIDERS[0])
        provider_dropdown = ttk.Combobox(toolbar, textvariable=self.provider_var,
                                          values=self.PROVIDERS, width=26, state="readonly")
        provider_dropdown.pack(side="left", padx=4)

        tk.Button(toolbar, text="▶  Analyse", command=self.run_analysis,
                  bg="#5B4FCF", fg="white", relief="flat", padx=12, pady=3,
                  font=("Arial", 10, "bold")).pack(side="right", padx=12)

    # ── Main panels ───────────────────────────────────────────────────────────

    def _build_main_panels(self):
        paned = tk.PanedWindow(self.root, orient="horizontal",
                               bg="#1E1E2E", sashwidth=6, sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=8, pady=4)

        # ── Left: text editor ─────────────────────────────────────────────────
        left_frame = tk.Frame(paned, bg="#1E1E2E")
        paned.add(left_frame, minsize=400)

        tk.Label(left_frame, text="Document", bg="#1E1E2E", fg="#AAAACC",
                 font=("Arial", 10, "bold")).pack(anchor="w", padx=4, pady=(4, 0))

        self.text_editor = tk.Text(
            left_frame,
            wrap="word",
            font=("Georgia", 12),
            bg="#12121E",
            fg="#E0E0F0",
            insertbackground="white",
            selectbackground="#5B4FCF",
            relief="flat",
            padx=12,
            pady=12,
            undo=True,
        )
        self.text_editor.pack(fill="both", expand=True, padx=4, pady=4)
        self.text_editor.bind("<Button-1>", self._on_text_click)

        # ── Right: editorial panel ────────────────────────────────────────────
        right_frame = tk.Frame(paned, bg="#1E1E2E")
        paned.add(right_frame, minsize=340)

        tk.Label(right_frame, text="Editorial Notes", bg="#1E1E2E", fg="#AAAACC",
                 font=("Arial", 10, "bold")).pack(anchor="w", padx=4, pady=(4, 0))

        # Notes to editor
        tk.Label(right_frame, text="Notes to editor:", bg="#1E1E2E", fg="#888899",
                 font=("Arial", 9)).pack(anchor="w", padx=4)

        self.notes_text = tk.Text(right_frame, height=4, wrap="word",
                                   font=("Arial", 10), bg="#12121E", fg="#E0E0F0",
                                   insertbackground="white", relief="flat",
                                   padx=8, pady=6)
        self.notes_text.pack(fill="x", padx=4, pady=(0, 6))
        self.notes_text.insert("1.0", "e.g. The protagonist speaks in clipped sentences deliberately.")

        # Comment thread display
        tk.Label(right_frame, text="Comment thread:", bg="#1E1E2E", fg="#888899",
                 font=("Arial", 9)).pack(anchor="w", padx=4)

        self.thread_display = scrolledtext.ScrolledText(
            right_frame, height=12, wrap="word",
            font=("Arial", 10), bg="#12121E", fg="#E0E0F0",
            relief="flat", padx=8, pady=6, state="disabled"
        )
        self.thread_display.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        # Pushback input
        tk.Label(right_frame, text="Your response to editor:", bg="#1E1E2E", fg="#888899",
                 font=("Arial", 9)).pack(anchor="w", padx=4)

        self.pushback_text = tk.Text(right_frame, height=3, wrap="word",
                                      font=("Arial", 10), bg="#12121E", fg="#E0E0F0",
                                      insertbackground="white", relief="flat",
                                      padx=8, pady=6)
        self.pushback_text.pack(fill="x", padx=4, pady=(0, 4))

        btn_frame = tk.Frame(right_frame, bg="#1E1E2E")
        btn_frame.pack(fill="x", padx=4, pady=(0, 6))

        tk.Button(btn_frame, text="Push back", command=self.push_back,
                  bg="#2E4E7E", fg="white", relief="flat", padx=10, pady=3,
                  font=("Arial", 9)).pack(side="left", padx=(0, 6))

        tk.Button(btn_frame, text="✓ Resolve", command=self.resolve_comment,
                  bg="#2E6E3E", fg="white", relief="flat", padx=10, pady=3,
                  font=("Arial", 9)).pack(side="left")

        tk.Button(btn_frame, text="All comments", command=self.show_all_comments,
                  bg="#3E3E5E", fg="white", relief="flat", padx=10, pady=3,
                  font=("Arial", 9)).pack(side="right")

    # ── Status bar ────────────────────────────────────────────────────────────

    def _build_status_bar(self):
        status_frame = tk.Frame(self.root, bg="#2E2E4E", pady=3)
        status_frame.pack(fill="x", side="bottom")

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(status_frame, textvariable=self.status_var,
                 bg="#2E2E4E", fg="#888899", font=("Arial", 9),
                 anchor="w").pack(side="left", padx=12)

        self.wordcount_var = tk.StringVar(value="Words: 0")
        tk.Label(status_frame, textvariable=self.wordcount_var,
                 bg="#2E2E4E", fg="#888899", font=("Arial", 9)).pack(side="right", padx=12)

        self.text_editor.bind("<KeyRelease>", self._update_word_count)

    # ── File operations ───────────────────────────────────────────────────────

    def new_file(self):
        self.text_editor.delete("1.0", tk.END)
        self.clear_all_comments()
        self.current_file = None
        self.root.title("Qualia Editor")

    def open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt *.frank *.md"), ("All files", "*.*")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert("1.0", f.read())
            self.current_file = path
            self.root.title(f"Qualia Editor — {os.path.basename(path)}")
            self._update_word_count()

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.text_editor.get("1.0", tk.END))
            self.status_var.set(f"Saved: {os.path.basename(self.current_file)}")
        else:
            self.save_file_as()

    def save_file_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("Frank files", "*.frank"), ("All files", "*.*")])
        if path:
            self.current_file = path
            self.save_file()
            self.root.title(f"Qualia Editor — {os.path.basename(path)}")

    # ── Analysis ──────────────────────────────────────────────────────────────

    def run_analysis(self):
        text = self.text_editor.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Empty", "Nothing to analyse.")
            return

        notes      = self.notes_text.get("1.0", tk.END).strip()
        work_type  = self.work_type_var.get()
        provider   = self.provider_var.get()

        words      = re.findall(r'\b\w+\b', text.lower())
        freq       = Counter(words)
        top_words  = freq.most_common(20)
        freq_str   = ", ".join(f"{w}({c})" for w, c in top_words if c > 2)

        system_prompt = (
            f"You are a professional literary editor reviewing a {work_type}.\n"
            f"Writer's notes: {notes if notes else 'None provided.'}\n"
            f"Top word frequencies (word/count): {freq_str}\n\n"
            f"Provide 3-5 specific editorial comments. For each:\n"
            f"- Quote the relevant passage (max 10 words)\n"
            f"- Give a concise note\n"
            f"- Be direct, respect deliberate stylistic choices mentioned in the writer's notes.\n"
            f"Format each comment as:\n"
            f"COMMENT: [quoted passage]\nNOTE: [your note]\n"
        )

        self.status_var.set(f"Asking {provider}...")
        self.root.update()

        response = call_ai(provider, system_prompt, text[:4000])

        self._parse_and_highlight(response)
        self.status_var.set(f"Analysis complete — {provider}")

    def _parse_and_highlight(self, response):
        """Parse AI response and highlight matching passages in the editor."""
        text = self.text_editor.get("1.0", tk.END)

        pattern = re.compile(
            r'COMMENT:\s*["\']?(.+?)["\']?\s*\nNOTE:\s*(.+?)(?=\nCOMMENT:|\Z)',
            re.DOTALL | re.IGNORECASE
        )

        matches = list(pattern.finditer(response))

        if not matches:
            # Fallback — show raw response as a single comment
            self._add_comment_manual("Full document", response.strip())
            return

        for match in matches:
            snippet  = match.group(1).strip().strip('"\'')
            note     = match.group(2).strip()
            self._add_comment_manual(snippet, note)

    def _add_comment_manual(self, snippet, note):
        """Find snippet in editor and add a highlight + comment."""
        text = self.text_editor.get("1.0", tk.END)
        idx = text.lower().find(snippet.lower()[:30])

        tag = f"comment_{Comment._id_counter + 1}"
        comment = Comment(snippet, note, tag)
        self.comments[tag] = comment

        if idx >= 0:
            start = self.text_editor.index(f"1.0 + {idx} chars")
            end   = self.text_editor.index(f"1.0 + {idx + len(snippet)} chars")
            self.text_editor.tag_add(tag, start, end)
            self.text_editor.tag_config(tag,
                background=self.HIGHLIGHT_COLOR,
                foreground="#1E1E2E")
            self.text_editor.tag_bind(tag, "<Button-1>",
                lambda e, t=tag: self._select_comment(t))

    # ── Comment interaction ───────────────────────────────────────────────────

    def _on_text_click(self, event):
        index = self.text_editor.index(f"@{event.x},{event.y}")
        for tag in self.text_editor.tag_names(index):
            if tag in self.comments:
                self._select_comment(tag)
                return

    def _select_comment(self, tag):
        # Deselect previous
        if self.selected_tag and self.selected_tag in self.comments:
            c = self.comments[self.selected_tag]
            color = self.RESOLVED_COLOR if c.resolved else self.HIGHLIGHT_COLOR
            self.text_editor.tag_config(self.selected_tag,
                background=color, foreground="#1E1E2E")

        self.selected_tag = tag
        self.text_editor.tag_config(tag,
            background=self.SELECTED_COLOR, foreground="#1E1E2E")

        self._refresh_thread_display()

    def _refresh_thread_display(self):
        self.thread_display.config(state="normal")
        self.thread_display.delete("1.0", tk.END)

        if not self.selected_tag or self.selected_tag not in self.comments:
            self.thread_display.insert("1.0", "Click a highlighted passage to see comments.")
            self.thread_display.config(state="disabled")
            return

        comment = self.comments[self.selected_tag]

        header = f'Passage: "{comment.text_snippet[:60]}"\n'
        header += "─" * 40 + "\n\n"
        self.thread_display.insert("1.0", header)

        for speaker, message in comment.thread:
            label = "🖊 Editor:" if speaker == "Editor" else "✍ You:"
            self.thread_display.insert(tk.END, f"{label}\n{message}\n\n")

        if comment.resolved:
            self.thread_display.insert(tk.END, "✓ Resolved\n")

        self.thread_display.config(state="disabled")

    def push_back(self):
        if not self.selected_tag or self.selected_tag not in self.comments:
            messagebox.showinfo("No selection", "Click a highlighted passage first.")
            return

        user_message = self.pushback_text.get("1.0", tk.END).strip()
        if not user_message:
            messagebox.showinfo("Empty", "Write your response to the editor first.")
            return

        comment  = self.comments[self.selected_tag]
        provider = self.provider_var.get()

        comment.thread.append(("User", user_message))

        # Build context for the AI
        thread_str = "\n".join(
            f"{'Editor' if s == 'Editor' else 'Writer'}: {m}"
            for s, m in comment.thread
        )

        system_prompt = (
            f"You are a professional literary editor.\n"
            f"Passage in question: \"{comment.text_snippet}\"\n"
            f"Conversation so far:\n{thread_str}\n\n"
            f"The writer has just responded. Engage thoughtfully — "
            f"if their explanation is valid, acknowledge it and update your note. "
            f"If you still have concerns, explain why respectfully."
        )

        self.status_var.set("Editor is responding...")
        self.root.update()

        response = call_ai(provider, system_prompt, user_message)
        comment.thread.append(("Editor", response.strip()))

        self.pushback_text.delete("1.0", tk.END)
        self._refresh_thread_display()
        self.status_var.set("Ready")

    def resolve_comment(self):
        if not self.selected_tag or self.selected_tag not in self.comments:
            messagebox.showinfo("No selection", "Click a highlighted passage first.")
            return

        comment = self.comments[self.selected_tag]
        comment.resolved = True
        self.text_editor.tag_config(self.selected_tag,
            background=self.RESOLVED_COLOR, foreground="#1E1E2E")

        comment.thread.append(("Editor", "Marked as resolved."))
        self._refresh_thread_display()
        self.status_var.set("Comment resolved.")

    def clear_all_comments(self):
        for tag in list(self.comments.keys()):
            self.text_editor.tag_delete(tag)
        self.comments.clear()
        self.selected_tag = None
        self._refresh_thread_display()

    # ── Word frequency ────────────────────────────────────────────────────────

    def show_word_frequency(self):
        text = self.text_editor.get("1.0", tk.END)
        words = re.findall(r'\b\w+\b', text.lower())
        freq  = Counter(words)

        win = tk.Toplevel(self.root)
        win.title("Word Frequency")
        win.geometry("320x480")
        win.configure(bg="#1E1E2E")

        tk.Label(win, text="Top words", bg="#1E1E2E", fg="#AAAACC",
                 font=("Arial", 11, "bold")).pack(pady=8)

        listbox = tk.Listbox(win, bg="#12121E", fg="#E0E0F0",
                             font=("Courier", 10), relief="flat")
        listbox.pack(fill="both", expand=True, padx=12, pady=8)

        for word, count in freq.most_common(50):
            if len(word) > 2:
                listbox.insert(tk.END, f"{count:>5}  {word}")

    def show_all_comments(self):
        win = tk.Toplevel(self.root)
        win.title("All Comments")
        win.geometry("480x520")
        win.configure(bg="#1E1E2E")

        tk.Label(win, text="Comments", bg="#1E1E2E", fg="#AAAACC",
                 font=("Arial", 11, "bold")).pack(pady=8)

        display = scrolledtext.ScrolledText(win, bg="#12121E", fg="#E0E0F0",
                                             font=("Arial", 10), relief="flat",
                                             padx=10, pady=8)
        display.pack(fill="both", expand=True, padx=12, pady=8)

        if not self.comments:
            display.insert("1.0", "No comments yet. Run an analysis first.")
        else:
            for tag, comment in self.comments.items():
                status = "✓ Resolved" if comment.resolved else "○ Open"
                display.insert(tk.END,
                    f"{status}  \"{comment.text_snippet[:50]}\"\n"
                    f"{comment.thread[-1][1][:120]}...\n"
                    f"{'─' * 40}\n\n"
                )
        display.config(state="disabled")

    # ── Utilities ─────────────────────────────────────────────────────────────

    def _update_word_count(self, event=None):
        text  = self.text_editor.get("1.0", tk.END)
        count = len(re.findall(r'\b\w+\b', text))
        self.wordcount_var.set(f"Words: {count}")

    def show_all_comments(self):
        win = tk.Toplevel(self.root)
        win.title("All Comments")
        win.geometry("480x520")
        win.configure(bg="#1E1E2E")

        tk.Label(win, text="Comments", bg="#1E1E2E", fg="#AAAACC",
                 font=("Arial", 11, "bold")).pack(pady=8)

        display = scrolledtext.ScrolledText(win, bg="#12121E", fg="#E0E0F0",
                                             font=("Arial", 10), relief="flat",
                                             padx=10, pady=8)
        display.pack(fill="both", expand=True, padx=12, pady=8)

        if not self.comments:
            display.insert("1.0", "No comments yet. Run an analysis first.")
        else:
            for tag, comment in self.comments.items():
                status = "✓ Resolved" if comment.resolved else "○ Open"
                display.insert(tk.END,
                    f"{status}  \"{comment.text_snippet[:50]}\"\n"
                    f"{comment.thread[-1][1][:120]}\n"
                    f"{'─' * 40}\n\n"
                )
        display.config(state="disabled")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()

    # Style the ttk comboboxes
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TCombobox",
        fieldbackground="#12121E",
        background="#2E2E4E",
        foreground="#E0E0F0",
        selectbackground="#5B4FCF",
        selectforeground="white"
    )

    app = QualiaEditor(root)
    root.mainloop()
