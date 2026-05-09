import tkinter as tk

# ── Color Palette (matching the StockFlow green theme) ───────────────────────
BG          = "#E2F0E0"
BG_FADE     = "#D6EACD"
TEXT_DARK   = "#1A3D2B"
TEXT_GREEN  = "#2D6A4F"
TEXT_MUTED  = "#4A6741"
TEXT_DIM    = "#6B8F65"
BTN_BG      = "#2D6A4F"
BTN_HOVER   = "#1A3D2B"
BTN_FG      = "#FFFFFF"

def rounded_rect(canvas, x1, y1, x2, y2, r=14, **kwargs):
    pts = [
        x1+r, y1,  x2-r, y1,
        x2,   y1,  x2,   y1+r,
        x2,   y2-r,x2,   y2,
        x2-r, y2,  x1+r, y2,
        x1,   y2,  x1,   y2-r,
        x1,   y1+r,x1,   y1,
        x1+r, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


class HoverButton(tk.Canvas):
    def __init__(self, parent, text, command=None, bg_color=BTN_BG, fg_color=BTN_FG,
                 hover_color=BTN_HOVER, width=200, height=50,
                 font=("Segoe UI", 11, "bold"), radius=10, **kwargs):
        super().__init__(parent, bg=parent.cget("bg"), highlightthickness=0,
                         bd=0, width=width, height=height, **kwargs)
        self._text = text
        self._bg = bg_color
        self._fg = fg_color
        self._hover = hover_color
        self._cmd = command
        self._font = font
        self._radius = radius
        self._rect = None

        self.bind("<Configure>", self._draw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _draw(self, event=None):
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 4 or h < 4:
            return
        self.delete("all")
        self._rect = rounded_rect(self, 0, 0, w, h, r=self._radius,
                                   fill=self._bg, outline="")
        self._text_id = self.create_text(w // 2, h // 2, text=self._text,
                                          fill=self._fg, font=self._font)

    def _on_enter(self, e):
        self.config(cursor="hand2")
        if self._rect:
            self.itemconfig(self._rect, fill=self._hover)

    def _on_leave(self, e):
        if self._rect:
            self.itemconfig(self._rect, fill=self._bg)

    def _on_click(self, e):
        if self._cmd:
            self._cmd()


class HeroScreen(tk.Toplevel):
    def __init__(self, master, on_launch=None):
        super().__init__(master)
        self.title("StockFlow  ·  Welcome")
        self.geometry("1300x800")
        self.configure(bg=BG)
        self.resizable(True, True)
        self._on_launch = on_launch
        self.state("zoomed")

        self._build_hero()

        # If user closes this window with X, quit the whole app
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self.master.destroy()

    def _do_launch(self):
        if self._on_launch:
            self._on_launch()
        self.destroy()

    def _build_hero(self):
        # ── Top Header Bar ───────────────────────────────────────────────────
        header = tk.Frame(self, bg=BG, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Logo + Title on the LEFT
        logo_frame = tk.Frame(header, bg=BG)
        logo_frame.pack(side="left", padx=44, pady=14)

        logo_box = tk.Frame(logo_frame, bg=TEXT_DARK, width=36, height=36)
        logo_box.pack_propagate(False)
        logo_box.pack(side="left", padx=(0, 12))
        tk.Label(logo_box, text="❖", bg=TEXT_DARK, fg="#FFFFFF",
                 font=("Segoe UI", 17, "bold")).place(relx=.5, rely=.5, anchor="center")

        tk.Label(logo_frame, text="StockFlow", bg=BG, fg=TEXT_DARK,
                 font=("Segoe UI", 16, "bold")).pack(side="left")

        # ── Full-screen centered container ───────────────────────────────────
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True)

        # Vertical centering
        container.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=0)
        container.rowconfigure(2, weight=2)
        container.columnconfigure(0, weight=1)

        center = tk.Frame(container, bg=BG)
        center.grid(row=0, column=0, sticky="s")

        content = tk.Frame(container, bg=BG)
        content.grid(row=1, column=0)

        # ── Headline Line 1 ─────────────────────────────────────────────────
        h1_frame = tk.Frame(content, bg=BG)
        h1_frame.pack(pady=(0, 0))

        tk.Label(h1_frame, text="Smart Inventory, ", bg=BG, fg=TEXT_DARK,
                 font=("Segoe UI", 58, "bold")).pack(side="left")
        tk.Label(h1_frame, text="Effortless", bg=BG, fg=TEXT_GREEN,
                 font=("Segoe UI", 58, "bold")).pack(side="left")

        # ── Headline Line 2 ─────────────────────────────────────────────────
        tk.Label(content, text="Stock Management", bg=BG, fg=TEXT_DARK,
                 font=("Segoe UI", 58, "bold")).pack(pady=(0, 20))

        # ── Sub-tagline ─────────────────────────────────────────────────────
        tk.Label(content, text="Your complete inventory ecosystem — powered by intelligent data structures",
                 bg=BG, fg=TEXT_MUTED, font=("Segoe UI", 13, "italic")).pack(pady=(0, 24))

        # ── Description ─────────────────────────────────────────────────────
        desc = ("Track, restock, and organize your entire product catalogue from one powerful dashboard.\n"
                "Monitor stock levels in real time, receive low-stock alerts, manage purchases and sales,\n"
                "and keep your supply chain running smoothly — all in one place.")
        tk.Label(content, text=desc, bg=BG, fg=TEXT_DIM,
                 font=("Segoe UI", 15), justify="center").pack(pady=(0, 50))

        # ── CTA Button ──────────────────────────────────────────────────────
        btn = HoverButton(content, "Launch Dashboard  →", width=280, height=60,
                          font=("Segoe UI", 14, "bold"), radius=14,
                          command=self._do_launch)
        btn.pack()

        # ── Bottom footer — pinned to bottom of window ────────────────────────
        footer = tk.Frame(self, bg=BG)
        footer.pack(side="bottom", fill="x", pady=(0, 30))

        # Wide divider line (60% of window width)
        line_canvas = tk.Canvas(footer, bg=BG, highlightthickness=0, height=2)
        line_canvas.pack(fill="x", padx=250, pady=(0, 16))
        def _draw_line(e):
            line_canvas.delete("all")
            line_canvas.create_line(0, 1, e.width, 1, fill="#C2D8BC", width=1)
        line_canvas.bind("<Configure>", _draw_line)

        tag_frame = tk.Frame(footer, bg=BG)
        tag_frame.pack()
        tags = ["Python", "Tkinter", "AVL Trees", "Data Structures"]
        for i, tag in enumerate(tags):
            if i > 0:
                tk.Label(tag_frame, text="  ·  ", bg=BG, fg="#A8C8A0",
                         font=("Segoe UI", 11)).pack(side="left")
            tk.Label(tag_frame, text=tag, bg=BG, fg="#7FA878",
                     font=("Segoe UI", 11, "bold")).pack(side="left")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    def launch():
        root.deiconify()
        root.state("zoomed")
    hero = HeroScreen(root, on_launch=launch)
    root.mainloop()