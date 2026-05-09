import tkinter as tk
from tkinter import ttk, messagebox
import math

# ── Try to import backend functions ──────────────────────────────────────────
try:
    from functions import (
        load_catalogue_to_avl,
        save_to_file,
        avl_insert,
        avl_search,
        avl_delete,
        in_order,
        Item,
        log_transaction,
    )
    def get_all_items(root):
        items = []
        def _inorder(node):
            if node is None:
                return
            _inorder(node.left)
            items.append(node.data)
            _inorder(node.right)
        _inorder(root)
        return items
    BACKEND = True
except ImportError:
    BACKEND = False
    class Item:
        def __init__(self, name="", description="", category="", price=0, quantity=0, loc_x=0, loc_y=0):
            self.name = name
            self.description = description
            self.category = category
            self.price = price
            self.quantity = quantity
            self.loc_x = loc_x
            self.loc_y = loc_y

    _DEMO = [
        Item("Dell XPS 15",       "15.6\" OLED Laptop Intel i9",        "Laptops",     450000, 12),
        Item("iPhone 15 Pro",     "256GB Space Black Titanium",          "Phones",      320000,  5),
        Item("Samsung 4K TV",     "55\" QLED Smart TV",                  "Displays",    185000,  8),
        Item("Logitech MX Keys",  "Advanced Wireless Keyboard",          "Peripherals",  18500, 22),
        Item("Sony WH-1000XM5",   "Noise Cancelling Headphones",         "Audio",        72000,  3),
        Item("iPad Air M2",       "11-inch 256GB WiFi",                  "Tablets",     145000,  9),
        Item("APC UPS 1500VA",    "Back-UPS Pro Uninterruptible",        "Power",        28000, 14),
        Item("WD Black SN850X",   "2TB NVMe SSD PCIe 4.0",              "Storage",      24000,  6),
    ]

    class _FakeNode:
        def __init__(self, item): self.data = item; self.left = None; self.right = None

    def load_catalogue_to_avl():
        root = None
        for item in _DEMO: root = avl_insert(root, item)
        return root

    def avl_insert(root, item):
        node = _FakeNode(item)
        if root is None: return node
        node.left = root; return node

    def avl_search(root, name):
        node = root
        while node:
            if node.data.name == name: return node
            node = node.left
        return None

    def avl_delete(root, name): return root
    def save_to_file(root): pass
    def log_transaction(txn_type, name, qty): pass

    def get_all_items(root):
        items = []
        node = root
        while node: items.append(node.data); node = node.left
        return sorted(items, key=lambda x: x.name)


# ─────────────────────────────────────────────────────────────────────────────
#  PALETTE  (Donezo-inspired green + clean whites)
# ─────────────────────────────────────────────────────────────────────────────
BG          = "#F0F4F0"   # very light sage canvas
SIDEBAR_BG  = "#FFFFFF"   # pure white sidebar
CARD        = "#FFFFFF"   # card background
CARD2       = "#F7FAF7"   # slightly tinted card
BORDER      = "#E8EFE8"   # subtle green-tinted border

GREEN_DARK  = "#1A3D2B"   # deep forest green (hero card bg)
GREEN_MID   = "#2D6A4F"   # mid green
GREEN       = "#40916C"   # primary green accent
GREEN_LIGHT = "#74C69D"   # light green
GREEN_PALE  = "#D8F3DC"   # pale green (highlights)
GREEN_SOFT  = "#B7E4C7"   # soft green

AMBER       = "#F59E0B"
RED         = "#EF4444"
BLUE        = "#3B82F6"

TEXT        = "#1A2E1A"   # very dark green-black
TEXT2       = "#4A6741"   # muted green-text
TEXT3       = "#8BAA88"   # dim text
WHITE       = "#FFFFFF"
WHITE_DIM   = "#F0F4F0"

LOW_STOCK   = 15

# ─────────────────────────────────────────────────────────────────────────────
#  Rounded rectangle helper (Canvas-based card)
# ─────────────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────────────
#  Modern flat card frame (uses a canvas underneath for soft shadow + rounding)
# ─────────────────────────────────────────────────────────────────────────────
class CardFrame(tk.Frame):
    """A Frame that looks like a rounded white card with a subtle shadow."""
    def __init__(self, parent, radius=14, bg=CARD, shadow_color="#D8E8D8",
                 border_color=BORDER, **kw):
        # outer wrapper holds the shadow canvas + inner content
        super().__init__(parent, bg=parent.cget("bg"), **kw)
        self._radius = radius
        self._card_bg = bg
        self._shadow = shadow_color
        self._border = border_color

        self._canvas = tk.Canvas(self, bg=parent.cget("bg"),
                                 highlightthickness=0, bd=0)
        self._canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Inner content frame sits on top
        self.inner = tk.Frame(self, bg=bg)
        pad = 1
        self.inner.pack(padx=pad+radius//2, pady=pad+radius//2, fill="both", expand=True)
        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 4 or h < 4:
            return
        c = self._canvas
        c.delete("all")
        r = self._radius
        # shadow (offset slightly)
        rounded_rect(c, 3, 4, w-1, h+1, r=r, fill=self._shadow, outline="")
        # card body
        rounded_rect(c, 1, 1, w-3, h-3, r=r, fill=self._card_bg, outline=self._border)


# ─────────────────────────────────────────────────────────────────────────────
#  Pill / Tag label
# ─────────────────────────────────────────────────────────────────────────────
class PillLabel(tk.Canvas):
    def __init__(self, parent, text, fg=WHITE, bg=GREEN, font=("Segoe UI", 9, "bold"),
                 padx=10, pady=3, radius=10, **kw):
        super().__init__(parent, bg=parent.cget("bg"),
                         highlightthickness=0, bd=0, **kw)
        self._text = text; self._fg = fg; self._pill_bg = bg
        self._font = font; self._padx = padx; self._pady = pady; self._r = radius
        # measure
        tmp = tk.Label(self, text=text, font=font)
        tw = tmp.winfo_reqwidth(); th = tmp.winfo_reqheight(); tmp.destroy()
        W = tw + padx*2 + 2; H = th + pady*2
        self.config(width=W, height=H)
        rounded_rect(self, 0, 0, W, H, r=radius, fill=bg, outline="")
        self.create_text(W//2, H//2, text=text, fill=fg, font=font)


# ─────────────────────────────────────────────────────────────────────────────
#  Modern scrollable data table (Canvas-based, no ttk.Treeview wobble)
# ─────────────────────────────────────────────────────────────────────────────
class DataTable(tk.Frame):
    ROW_H = 52
    HDR_H = 48

    def __init__(self, parent, columns, col_weights=None, **kw):
        super().__init__(parent, bg=parent.cget("bg"), **kw)

        self._columns = columns
        self._col_weights = col_weights or [1]*len(columns)

        # Card wrapper (rounded handled by CardFrame)
        self._card = CardFrame(self)
        self._card.pack(fill="both", expand=True)

        container = self._card.inner

        # Header
        self._hdr_frame = tk.Frame(container, bg=CARD2, height=self.HDR_H)
        self._hdr_frame.pack(fill="x")
        self._hdr_frame.pack_propagate(False)

        # Scrollable body
        self._body_canvas = tk.Canvas(container, bg=CARD, highlightthickness=0)
        self._scrollbar = tk.Scrollbar(container, orient="vertical",
                                       command=self._body_canvas.yview)
        self._body_canvas.configure(yscrollcommand=self._scrollbar.set)

        self._scrollbar.pack(side="right", fill="y")
        self._body_canvas.pack(side="left", fill="both", expand=True)

        self._body_frame = tk.Frame(self._body_canvas, bg=CARD)
        self._canvas_window = self._body_canvas.create_window(
            (0, 0), window=self._body_frame, anchor="nw"
        )

        self._body_frame.bind("<Configure>", self._on_frame_configure)
        self._body_canvas.bind("<Configure>", self._on_canvas_configure)

        self._rows_pool = [] # List of (row_frame, divider_frame, list_of_labels)
        self._build_header()

    def _build_header(self):
        for i, col in enumerate(self._columns):
            self._hdr_frame.columnconfigure(i, weight=self._col_weights[i], uniform="table")

            lbl = tk.Label(
                self._hdr_frame,
                text=col.upper(),
                bg=CARD2,
                fg=TEXT3,
                font=("Segoe UI", 13, "bold"),
                anchor="w",
                padx=18,
                pady=12
            )
            lbl.grid(row=0, column=i, sticky="nsew")

    def _on_frame_configure(self, e):
        self._body_canvas.configure(scrollregion=self._body_canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        # 🔥 Force body width to match header width exactly
        self._body_canvas.itemconfig(self._canvas_window, width=e.width)

    def load(self, rows, tags=None):
        # Hide all existing rows in pool
        for rf, df, lbls in self._rows_pool:
            rf.pack_forget()
            df.pack_forget()

        # Ensure we have enough widgets in the pool
        while len(self._rows_pool) < len(rows):
            bg = CARD # Will be set during pack
            rf = tk.Frame(self._body_frame, bg=bg, height=self.ROW_H)
            rf.pack_propagate(False)
            
            for i in range(len(self._columns)):
                rf.columnconfigure(i, weight=self._col_weights[i], uniform="table")
            
            lbls = []
            for i in range(len(self._columns)):
                lbl = tk.Label(
                    rf,
                    anchor="w",
                    padx=18,
                    pady=12
                )
                lbl.grid(row=0, column=i, sticky="nsew")
                lbls.append(lbl)
            
            df = tk.Frame(self._body_frame, bg=BORDER, height=1)
            self._rows_pool.append((rf, df, lbls))

        # Update and show required rows
        for idx, row in enumerate(rows):
            rf, df, lbls = self._rows_pool[idx]
            bg = CARD if idx % 2 == 0 else CARD2
            
            rf.config(bg=bg)
            rf.pack(fill="x")
            
            for i, val in enumerate(row):
                lbl = lbls[i]
                lbl.config(
                    text=str(val),
                    bg=bg,
                    fg=TEXT if i == 0 else TEXT2,
                    font=("Segoe UI", 13, "bold") if i == 0 else ("Segoe UI", 13)
                )
            
            df.pack(fill="x")

class Autocomplete:
    def __init__(self, entry, get_values_cb):
        self.entry = entry
        self.get_values_cb = get_values_cb
        self.toplevel = None
        self.listbox = None
        
        self.entry.bind("<KeyRelease>", self.on_keyrelease, add="+")
        self.entry.bind("<FocusOut>", self.on_focusout, add="+")
        self.entry.bind("<Up>", self.up, add="+")
        self.entry.bind("<Down>", self.down, add="+")
        self.entry.bind("<Return>", self.select, add="+")
        self.entry.bind("<FocusIn>", self.on_focusin, add="+")
        
    def on_focusin(self, event):
        if not self.entry.get():
            self.on_keyrelease(event)
            
    def on_keyrelease(self, event):
        if event and getattr(event, "keysym", "") in ("Up", "Down", "Return", "Escape", "Tab"):
            return
            
        typed = self.entry.get().lower()
        vals = self.get_values_cb()
        matches = [v for v in vals if typed in v.lower()]
        
        if not matches or (len(matches) == 1 and matches[0].lower() == typed):
            self.close()
            return
            
        self.show_listbox(matches)
        
    def show_listbox(self, matches):
        if not self.toplevel:
            self.toplevel = tk.Toplevel(self.entry)
            self.toplevel.wm_overrideredirect(True)
            self.toplevel.attributes("-topmost", True)
            
            f = tk.Frame(self.toplevel, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            f.pack(fill="both", expand=True)
            
            self.listbox = tk.Listbox(f, bg=CARD, fg=TEXT, font=("Segoe UI", 11),
                                      selectbackground=GREEN_PALE, selectforeground=GREEN_DARK,
                                      relief="flat", bd=0, highlightthickness=0, activestyle="none")
            self.listbox.pack(fill="both", expand=True, padx=2, pady=2)
            self.listbox.bind("<ButtonRelease-1>", self.select)
            self.listbox.bind("<FocusOut>", self.on_focusout)
            
        parent_frame = self.entry.master.master
        w = parent_frame.winfo_width()
        x = parent_frame.winfo_rootx()
        y = parent_frame.winfo_rooty() + parent_frame.winfo_height() + 2
        
        self.toplevel.geometry(f"{w}x{min(150, len(matches)*24 + 4)}+{x}+{y}")
        
        self.listbox.delete(0, tk.END)
        for m in matches:
            self.listbox.insert(tk.END, m)
            
    def close(self, event=None):
        if self.toplevel:
            self.toplevel.destroy()
            self.toplevel = None
            self.listbox = None
            
    def on_focusout(self, event):
        self.entry.after(100, self._check_focus)
        
    def _check_focus(self):
        focus = self.entry.focus_get()
        if focus != self.listbox and focus != self.entry:
            self.close()

    def up(self, event):
        if self.listbox:
            curr = self.listbox.curselection()
            if curr:
                idx = curr[0] - 1
                if idx >= 0:
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.selection_set(idx)
                    self.listbox.see(idx)
            return "break"

    def down(self, event):
        if self.listbox:
            curr = self.listbox.curselection()
            if curr:
                idx = curr[0] + 1
                if idx < self.listbox.size():
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.selection_set(idx)
                    self.listbox.see(idx)
            else:
                self.listbox.selection_set(0)
                self.listbox.see(0)
            return "break"

    def select(self, event=None):
        if self.listbox:
            curr = self.listbox.curselection()
            if curr:
                val = self.listbox.get(curr[0])
                self.entry.delete(0, tk.END)
                self.entry.insert(0, val)
                self.close()
                return "break"

# ─────────────────────────────────────────────────────────────────────────────
#  Styled Entry
# ─────────────────────────────────────────────────────────────────────────────
def make_entry(parent, var, placeholder="", width=280):
    pbg = parent.cget("bg")
    frame = CardFrame(parent, radius=12, bg=CARD2, shadow_color=pbg, border_color=BORDER)
    e = tk.Entry(frame.inner, textvariable=var, bg=CARD2, fg=TEXT,
                 insertbackground=GREEN, relief="flat", bd=0,
                 font=("Segoe UI", 12), width=32)
    e.pack(padx=12, pady=10, fill="x")
    def on_focus_in(ev):
        frame._border = GREEN
        frame._draw()
    def on_focus_out(ev):
        frame._border = BORDER
        frame._draw()
    e.bind("<FocusIn>",  on_focus_in)
    e.bind("<FocusOut>", on_focus_out)
    return frame, e


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, bg=GREEN_DARK, fg=WHITE, hover_bg=GREEN,
                 font=("Segoe UI", 11, "bold"), radius=12, pady=10, width=None, **kw):
        super().__init__(parent, bg=parent.cget("bg"), highlightthickness=0, bd=0, **kw)
        self._text = text
        self._bg_col = bg
        self._hover = hover_bg
        self._cmd = command
        self._fg = fg
        self._font = font
        self._radius = radius
        
        tmp = tk.Label(self, text=text, font=font)
        self._req_w = tmp.winfo_reqwidth() + 40 if not width else width
        self._req_h = tmp.winfo_reqheight() + pady*2
        tmp.destroy()
        
        self.config(width=self._req_w, height=self._req_h)
        
        self._rect = None
        self._text_id = None
        
        self.bind("<Configure>", self._draw)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _draw(self, event=None):
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 4 or h < 4: return
        self.delete("all")
        self._rect = rounded_rect(self, 0, 0, w, h, r=self._radius, fill=self._bg_col, outline="")
        self._text_id = self.create_text(w//2, h//2, text=self._text, fill=self._fg, font=self._font)
        
    def _on_enter(self, e):
        if self._rect: self.itemconfig(self._rect, fill=self._hover)
        self.config(cursor="hand2")
    def _on_leave(self, e):
        if self._rect: self.itemconfig(self._rect, fill=self._bg_col)
    def _on_click(self, e):
        pass
    def _on_release(self, e):
        if self.winfo_containing(e.x_root, e.y_root) == self:
            if self._rect: self.itemconfig(self._rect, fill=self._hover)
            if self._cmd: self._cmd()

def make_button(parent, text, cmd, style="primary", width=None):
    styles = {
        "primary":   (GREEN_DARK, WHITE,    GREEN),
        "success":   (GREEN,      WHITE,    GREEN_MID),
        "danger":    (RED,        WHITE,    "#C53030"),
        "warning":   (AMBER,      WHITE,    "#D97706"),
        "ghost":     (CARD2,      TEXT2,    BORDER),
    }
    bg, fg, hover = styles.get(style, styles["primary"])
    b = RoundedButton(parent, text=text, command=cmd, bg=bg, fg=fg, hover_bg=hover, width=width)
    return b


# ─────────────────────────────────────────────────────────────────────────────
#  Main Application
# ─────────────────────────────────────────────────────────────────────────────
class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("StockFlow  ·  Inventory Manager")
        self.geometry("1300x800")
        self.minsize(1100, 680)
        self.configure(bg=BG)
        self.resizable(True, True)

        # Enable crisp font rendering on Windows
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        self._avl_root   = None
        self._data_dirty = True
        self._current_page = None
        self._pages      = {}

        self._build_layout()
        self._load_data()
        self._show_page("dashboard")

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_layout(self):
        # ── Sidebar ──────────────────────────────────────────────────────────
        self.sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(self.sidebar, bg=SIDEBAR_BG, pady=28)
        logo.pack(fill="x")
        logo_icon = tk.Frame(logo, bg=GREEN_DARK, width=38, height=38)
        logo_icon.pack_propagate(False)
        logo_icon.pack(side="left", padx=(20, 10))
        tk.Label(logo_icon, text="❖", bg=GREEN_DARK, fg=WHITE,
                 font=("Segoe UI", 18, "bold")).place(relx=.5, rely=.5, anchor="center")
        txt = tk.Frame(logo, bg=SIDEBAR_BG)
        txt.pack(side="left")
        tk.Label(txt, text="StockFlow", bg=SIDEBAR_BG, fg=TEXT,
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(txt, text="Inventory Manager", bg=SIDEBAR_BG, fg=TEXT3,
                 font=("Segoe UI", 9)).pack(anchor="w")

        # Divider
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=4)

        # Section label
        tk.Label(self.sidebar, text="MENU", bg=SIDEBAR_BG, fg=TEXT3,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=22, pady=(12, 4))

        nav_main = [
            ("Dashboard",   "dashboard", "⊞"),
            ("All Items",   "catalogue", "☰"),
            ("Search",      "search",    "⌕"),
            ("Low Stock",   "lowstock",  "⚠"),
            ("Transactions","transactions","↻"),
            ("Warehouse Map", "warehouse", "🗺"),
        ]
        nav_ops = [
            ("Add Item",    "add",       "+"),
            ("Modify Item", "modify",    "✎"),
            ("Purchase",    "purchase",  "↓"),
            ("Sell",        "sell",      "↑"),
            ("Delete Item", "delete",    "✕"),
        ]

        self._nav_buttons = {}
        for label, key, icon in nav_main:
            self._nav_buttons[key] = self._nav_btn(label, key, icon)

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=16, pady=8)
        tk.Label(self.sidebar, text="OPERATIONS", bg=SIDEBAR_BG, fg=TEXT3,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=22, pady=(0, 4))

        for label, key, icon in nav_ops:
            self._nav_buttons[key] = self._nav_btn(label, key, icon)

        # Status indicator at bottom
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(side="bottom", fill="x", padx=16, pady=4)
        status_bar = tk.Frame(self.sidebar, bg=SIDEBAR_BG)
        status_bar.pack(side="bottom", fill="x", padx=16, pady=12)
        dot = tk.Label(status_bar, text="●", bg=SIDEBAR_BG, fg=GREEN,
                       font=("Segoe UI", 12))
        dot.pack(side="left")
        tk.Label(status_bar, text=" System Online", bg=SIDEBAR_BG, fg=TEXT2,
                 font=("Segoe UI", 11)).pack(side="left")
        if not BACKEND:
            tk.Label(status_bar, text=" (Demo)", bg=SIDEBAR_BG, fg=AMBER,
                     font=("Segoe UI", 9)).pack(side="left")

        # ── Main area ────────────────────────────────────────────────────────
        main_area = tk.Frame(self, bg=BG)
        main_area.pack(side="left", fill="both", expand=True)

        # Top bar
        topbar = tk.Frame(main_area, bg=SIDEBAR_BG, height=62)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        tk.Frame(topbar, bg=BORDER, height=1).pack(side="bottom", fill="x")

        self._topbar_title = tk.Label(topbar, text="Dashboard",
                                       bg=SIDEBAR_BG, fg=TEXT,
                                       font=("Segoe UI", 17, "bold"))
        self._topbar_title.pack(side="left", padx=28, pady=16)
        self._topbar_sub = tk.Label(topbar, text="",
                                     bg=SIDEBAR_BG, fg=TEXT3,
                                     font=("Segoe UI", 12))
        self._topbar_sub.pack(side="left")

        # User chip (right side)
        user_chip = tk.Frame(topbar, bg=SIDEBAR_BG)
        user_chip.pack(side="right", padx=24)
        avatar = tk.Label(user_chip, text="A", bg=GREEN_DARK, fg=WHITE,
                          font=("Segoe UI", 13, "bold"),
                          width=2, height=1)
        avatar.pack(side="right", padx=(8, 0))
        tk.Label(user_chip, text="Admin", bg=SIDEBAR_BG, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(side="right")

        # Page container
        self.page_container = tk.Frame(main_area, bg=BG)
        self.page_container.pack(fill="both", expand=True, padx=28, pady=22)

        # Build all pages
        self._build_dashboard()
        self._build_catalogue()
        self._build_add()
        self._build_modify()
        self._build_search()
        self._build_purchase()
        self._build_sell()
        self._build_lowstock()
        self._build_delete()
        self._build_transactions()
        self._build_warehouse()

    def _nav_btn(self, label, key, icon):
        f = tk.Frame(self.sidebar, bg=SIDEBAR_BG, cursor="hand2")
        f.pack(fill="x", padx=10, pady=1)

        indicator = tk.Frame(f, bg=SIDEBAR_BG, width=4)
        indicator.pack(side="left", fill="y")

        inner = CardFrame(f, radius=8, bg=SIDEBAR_BG, shadow_color=SIDEBAR_BG, border_color=SIDEBAR_BG)
        inner.pack(fill="x", side="left", expand=True)

        icon_lbl = tk.Label(inner.inner, text=icon, bg=SIDEBAR_BG, fg=TEXT3,
                            font=("Segoe UI", 14), width=2)
        icon_lbl.pack(side="left", padx=(10, 0), pady=9)
        txt_lbl = tk.Label(inner.inner, text=label, bg=SIDEBAR_BG, fg=TEXT2,
                           font=("Segoe UI", 12), anchor="w")
        txt_lbl.pack(side="left", padx=8, pady=9)

        def click(_=None): self._show_page(key)
        def enter(_=None):
            if self._current_page != key:
                inner._card_bg = GREEN_PALE
                inner._draw()
                for w in (inner.inner, icon_lbl, txt_lbl): w.config(bg=GREEN_PALE)
        def leave(_=None):
            if self._current_page != key:
                inner._card_bg = SIDEBAR_BG
                inner._draw()
                for w in (inner.inner, icon_lbl, txt_lbl): w.config(bg=SIDEBAR_BG)
                indicator.config(bg=SIDEBAR_BG)

        for w in (f, inner, inner.inner, icon_lbl, txt_lbl, indicator):
            w.bind("<Button-1>", click)
            w.bind("<Enter>",    enter)
            w.bind("<Leave>",    leave)

        return {"frame": f, "inner": inner, "icon": icon_lbl,
                "text": txt_lbl, "indicator": indicator}

    def _set_active_nav(self, key):
        for k, w in self._nav_buttons.items():
            if k == key:
                w["inner"]._card_bg = GREEN_PALE
                w["inner"]._draw()
                for widget in (w["inner"].inner, w["icon"], w["text"]):
                    widget.config(bg=GREEN_PALE)
                w["icon"].config(fg=GREEN_DARK)
                w["text"].config(fg=GREEN_DARK, font=("Segoe UI", 12, "bold"))
                w["indicator"].config(bg=GREEN_DARK)
            else:
                w["inner"]._card_bg = SIDEBAR_BG
                w["inner"]._draw()
                for widget in (w["inner"].inner, w["icon"], w["text"]):
                    widget.config(bg=SIDEBAR_BG)
                w["icon"].config(fg=TEXT3)
                w["text"].config(fg=TEXT2, font=("Segoe UI", 12))
                w["indicator"].config(bg=SIDEBAR_BG)

    def _show_page(self, key):
        TITLES = {
            "dashboard": ("Dashboard",   "Overview of your inventory"),
            "catalogue": ("All Items",   "Full catalogue sorted alphabetically"),
            "add":       ("Add Item",    "Register a new product"),
            "modify":    ("Modify Item", "Edit an existing product"),
            "search":    ("Search",      "Find a product by name"),
            "purchase":  ("Purchase",    "Restock existing items"),
            "sell":      ("Sell",        "Dispatch stock on sale"),
            "lowstock":  ("Low Stock",   f"Items at or below {LOW_STOCK} units"),
            "delete":    ("Delete Item", "Remove a product permanently"),
            "transactions":("Transactions", "History of purchases and sales"),
            "warehouse": ("Warehouse Map", "Optimized order picking paths"),
        }
        if self._current_page:
            self._pages[self._current_page].pack_forget()
        self._current_page = key
        self._pages[key].pack(fill="both", expand=True)
        self._set_active_nav(key)
        title, sub = TITLES.get(key, ("", ""))
        self._topbar_title.config(text=title)
        self._topbar_sub.config(text=f"  /  {sub}")

        if key == "dashboard": self._refresh_dashboard()
        elif key == "catalogue": self._refresh_table()
        elif key == "lowstock":  self._refresh_lowstock()
        elif key == "transactions": self._refresh_transactions()
        elif key == "warehouse": self._refresh_warehouse()

    def _load_data(self):
        if self._data_dirty or self._avl_root is None:
            self._avl_root = load_catalogue_to_avl()
            self._data_dirty = False

    # ─────────────────────────────────────────────────────────────────────────
    #  Dashboard
    # ─────────────────────────────────────────────────────────────────────────
    def _build_dashboard(self):
        page = tk.Frame(self.page_container, bg=BG)
        self._pages["dashboard"] = page

        # KPI row
        kpi_row = tk.Frame(page, bg=BG)
        kpi_row.pack(fill="x", pady=(0, 18))

        kpi_defs = [
            ("total_items",  "Total Items",   "⊞", GREEN_DARK,  WHITE),
            ("total_value",  "Total Value",   "₨", GREEN,       WHITE),
            ("low_stock",    "Low Stock",     "⚠", AMBER,       WHITE),
            ("categories",   "Categories",   "◈", BLUE,        WHITE),
        ]
        self._kpi_vals = {}
        for i, (k, lbl, icon, bg, fg) in enumerate(kpi_defs):
            card = self._kpi_card(kpi_row, icon, lbl, "—", bg, fg)
            card.pack(side="left", fill="x", expand=True,
                      padx=(0, 14) if i < 3 else 0)
            self._kpi_vals[k] = card._val

        # Two-column lower section
        lower = tk.Frame(page, bg=BG)
        lower.pack(fill="both", expand=True)
        lower.columnconfigure(0, weight=3)
        lower.columnconfigure(1, weight=2)
        lower.rowconfigure(0, weight=1)

        # Left: inventory table card
        left_card = CardFrame(lower, radius=12, bg=CARD)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        hdr = tk.Frame(left_card.inner, bg=CARD, pady=14, padx=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Inventory Overview", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        view_all = tk.Label(hdr, text="View all →", bg=CARD, fg=GREEN,
                            font=("Segoe UI", 11), cursor="hand2")
        view_all.pack(side="right")
        view_all.bind("<Button-1>", lambda e: self._show_page("catalogue"))
        tk.Frame(left_card.inner, bg=BORDER, height=1).pack(fill="x")

        self.dash_table = DataTable(
            left_card.inner,
            columns=["Name", "Category", "Price (Rs.)", "Stock", "Status"],
            col_weights=[3, 2, 2, 1, 2],
        )
        self.dash_table.pack(fill="both", expand=True)

        # Right: summary panel
        right = tk.Frame(lower, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")

        # Quick actions card
        qa_card = CardFrame(right, radius=12, bg=CARD)
        qa_card.pack(fill="x", pady=(0, 14))
        tk.Label(qa_card.inner, text="Quick Actions", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 13, "bold"), padx=18, pady=12,
                 anchor="w").pack(fill="x")
        tk.Frame(qa_card.inner, bg=BORDER, height=1).pack(fill="x", padx=16)
        btns_frame = tk.Frame(qa_card.inner, bg=CARD, padx=16, pady=14)
        btns_frame.pack(fill="x")
        actions = [
            ("+ Add Item",   "add",      "primary"),
            ("↓ Purchase",   "purchase", "success"),
            ("↑ Sell",       "sell",     "warning"),
            ("⚠ Low Stock",  "lowstock", "ghost"),
        ]
        for txt, pg, sty in actions:
            b = make_button(btns_frame, txt, lambda p=pg: self._show_page(p), style=sty)
            b.pack(fill="x", pady=3)

        # Category breakdown card
        cat_card = CardFrame(right, radius=12, bg=CARD)
        cat_card.pack(fill="both", expand=True)
        tk.Label(cat_card.inner, text="Category Breakdown", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 13, "bold"), padx=18, pady=12,
                 anchor="w").pack(fill="x")
        tk.Frame(cat_card.inner, bg=BORDER, height=1).pack(fill="x", padx=16)
        self._cat_breakdown = tk.Frame(cat_card.inner, bg=CARD, padx=16, pady=10)
        self._cat_breakdown.pack(fill="both", expand=True)

    def _kpi_card(self, parent, icon, label, value, bg, fg):
        card = CardFrame(parent, radius=16, bg=bg, shadow_color=BG, border_color=bg)
        
        body = tk.Frame(card.inner, bg=bg, padx=10, pady=10)
        body.pack(fill="both", expand=True)
        
        # Icon circle
        icon_circle = tk.Label(body, text=icon, bg=_darken(bg, 20), fg=fg,
                               font=("Segoe UI", 16), width=2, height=1,
                               padx=4, pady=4)
        icon_circle.pack(side="left")
        txt_block = tk.Frame(body, bg=bg)
        txt_block.pack(side="left", padx=12)
        val_lbl = tk.Label(txt_block, text=value, bg=bg, fg=fg,
                           font=("Segoe UI", 24, "bold"))
        val_lbl.pack(anchor="w")
        tk.Label(txt_block, text=label, bg=bg, fg=_hex_alpha(fg, 180),
                 font=("Segoe UI", 11)).pack(anchor="w")
        card._val = val_lbl
        
        return card

    def _refresh_dashboard(self):
        self._load_data()
        items = get_all_items(self._avl_root)
        total = len(items)
        value = sum(i.price * i.quantity for i in items)
        low   = sum(1 for i in items if i.quantity <= LOW_STOCK)
        cats  = set(i.category for i in items)

        self._kpi_vals["total_items"].config(text=str(total))
        self._kpi_vals["total_value"].config(text=f"{value:,}")
        self._kpi_vals["low_stock"].config(text=str(low))
        self._kpi_vals["categories"].config(text=str(len(cats)))

        # Table data
        rows = []
        tags = []
        for i in items:
            status = "● Low" if i.quantity <= LOW_STOCK else "● OK"
            rows.append((i.name, i.category, f"{i.price:,}", i.quantity, status))
            tags.append("low" if i.quantity <= LOW_STOCK else "ok")
        self.dash_table.load(rows, tags)

        # Category breakdown
        for w in self._cat_breakdown.winfo_children(): w.destroy()
        cat_counts = {}
        for i in items:
            cat_counts[i.category] = cat_counts.get(i.category, 0) + i.quantity
        total_qty = max(sum(cat_counts.values()), 1)
        COLORS = [GREEN_DARK, GREEN, GREEN_LIGHT, AMBER, BLUE, "#8B5CF6", "#EC4899"]
        for ci, (cat, qty) in enumerate(sorted(cat_counts.items(), key=lambda x:-x[1])[:6]):
            color = COLORS[ci % len(COLORS)]
            row = tk.Frame(self._cat_breakdown, bg=CARD)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=cat, bg=CARD, fg=TEXT, font=("Segoe UI", 11),
                     anchor="w", width=16).pack(side="left")
            bar_bg = tk.Frame(row, bg=BORDER, height=8)
            bar_bg.pack(side="left", fill="x", expand=True, padx=(8, 8), pady=4)
            pct = qty / total_qty
            
            # Use a canvas for the bar to avoid widget churn and layout force
            self._create_pill_bar(bar_bg, pct, color)
            
            tk.Label(row, text=str(qty), bg=CARD, fg=TEXT3,
                     font=("Segoe UI", 11), width=5, anchor="e").pack(side="right")

    def _create_pill_bar(self, parent, pct, color):
        canv = tk.Canvas(parent, bg=BORDER, height=8, highlightthickness=0, bd=0)
        canv.pack(fill="both", expand=True)
        def draw(e=None):
            canv.delete("all")
            w = canv.winfo_width()
            if w < 4: return
            fill_w = max(int(w * pct), 4)
            # Draw rounded bar on canvas
            rounded_rect(canv, 0, 0, fill_w, 8, r=4, fill=color, outline="")
        canv.bind("<Configure>", draw)

    # ─────────────────────────────────────────────────────────────────────────
    #  Catalogue
    # ─────────────────────────────────────────────────────────────────────────
    def _build_catalogue(self):
        page = tk.Frame(self.page_container, bg=BG)
        self._pages["catalogue"] = page

        top = tk.Frame(page, bg=BG)
        top.pack(fill="x", pady=(0, 12))

        # Search bar
        search_frame = CardFrame(top, radius=12, bg=CARD2, shadow_color=BG, border_color=BORDER)
        search_frame.pack(side="left")
        tk.Label(search_frame.inner, text="⌕", bg=CARD2, fg=TEXT3,
                 font=("Segoe UI", 14)).pack(side="left", padx=(10, 4))
        self._cat_filter = tk.StringVar()
        fe = tk.Entry(search_frame.inner, textvariable=self._cat_filter,
                      bg=CARD2, fg=TEXT, insertbackground=GREEN,
                      relief="flat", bd=0, font=("Segoe UI", 12), width=28)
        fe.pack(side="left", pady=9, padx=4)
        fe.bind("<KeyRelease>", lambda e: self._refresh_table())

        ref_btn = make_button(top, "⟳  Refresh", self._refresh_table, style="ghost")
        ref_btn.pack(side="left", padx=10)

        total_lbl_frame = tk.Frame(top, bg=BG)
        total_lbl_frame.pack(side="right")
        self._cat_count_lbl = tk.Label(total_lbl_frame, text="", bg=BG, fg=TEXT3,
                                        font=("Segoe UI", 11))
        self._cat_count_lbl.pack()

        # Table card
        tcard = CardFrame(page)
        tcard.pack(fill="both", expand=True)

        inner = tcard.inner
        tcard.pack(fill="both", expand=True)
        tk.Frame(tcard, bg=BORDER, height=1).pack(fill="x")
        self.cat_table = DataTable(
            inner,
            columns=["Name", "Description", "Category", "Price (Rs.)", "In Stock"],
            col_weights=[3, 5, 2, 2, 2],
        )
        self.cat_table.pack(fill="both", expand=True)

    def _refresh_table(self):
        self._load_data()
        items = get_all_items(self._avl_root)
        f = self._cat_filter.get().lower()
        rows = []; tags = []
        for i in items:
            if f and f not in i.name.lower() and f not in i.category.lower():
                continue
            rows.append((i.name, i.description, i.category,
                         f"{i.price:,}", i.quantity))
            tags.append("low" if i.quantity <= LOW_STOCK else "ok")
        self.cat_table.load(rows, tags)
        self._cat_count_lbl.config(text=f"{len(rows)} items")

    # ─────────────────────────────────────────────────────────────────────────
    #  Add Item
    # ─────────────────────────────────────────────────────────────────────────
    def _build_add(self):
        page = tk.Frame(self.page_container, bg=BG)
        self._pages["add"] = page

        outer = tk.Frame(page, bg=BG)
        outer.pack(anchor="n", fill="x")
        card = self._section_card(outer, "Register New Product", GREEN_DARK)

        fields = [("Item Name","add_name"),("Description","add_desc"),
                  ("Category","add_cat"),("Price (Rs.)","add_price"),("Quantity","add_qty"),
                  ("Shelf X (1-6)","add_x"), ("Shelf Y (1-16)","add_y")]
        self._avars = {}
        for lbl, key in fields:
            self._avars[key] = tk.StringVar()
            self._field_row(card, lbl, self._avars[key])

        tk.Frame(card, bg=BG, height=6).pack()
        btns = tk.Frame(card, bg=CARD, padx=20, pady=4)
        btns.pack(fill="x")
        make_button(btns, "+ Add Item", self._do_add, style="primary").pack(side="left")
        make_button(btns, "Clear", self._clear_add, style="ghost").pack(side="left", padx=10)

        self._add_msg = tk.Label(card, text="", bg=CARD, fg=GREEN,
                                  font=("Segoe UI", 12, "bold"), padx=20, pady=8)
        self._add_msg.pack(anchor="w")

    def _do_add(self):
        name  = self._avars["add_name"].get().strip()
        desc  = self._avars["add_desc"].get().strip()
        cat   = self._avars["add_cat"].get().strip()
        price = self._avars["add_price"].get().strip()
        qty   = self._avars["add_qty"].get().strip()
        x     = self._avars["add_x"].get().strip()
        y     = self._avars["add_y"].get().strip()
        if not all([name, desc, cat, price, qty, x, y]):
            self._add_msg.config(text="⚠  All fields, including shelf X and Y, are required.", fg=AMBER); return
        try:
            pv = int(price); qv = int(qty)
            rx = int(x); ry = int(y)
            if not (1 <= rx <= 6) or not (1 <= ry <= 16):
                self._add_msg.config(text="⚠  Shelf X must be 1-6, Y must be 1-16.", fg=AMBER); return
                
            shelf_cols = [2, 5, 8, 11, 14, 17]
            xv = shelf_cols[rx - 1]
            yv = ry + 1 # mapping Y 1-16 to grid rows 2-17
            
            # Uniqueness check
            self._load_data()
            items = get_all_items(self._avl_root)
            for it in items:
                if it.loc_x == xv and it.loc_y == yv:
                    self._add_msg.config(text=f"⚠  Shelf ({rx},{ry}) is already occupied by '{it.name}'.", fg=AMBER); return
        except ValueError:
            self._add_msg.config(text="⚠  Numeric fields must be integers.", fg=AMBER); return

        self._avl_root = avl_insert(self._avl_root, Item(name, desc, cat, pv, qv, xv, yv))
        save_to_file(self._avl_root)
        self._data_dirty = True
        self._add_msg.config(text=f"✓  '{name}' added successfully.", fg=GREEN)
        self._clear_add()

    def _clear_add(self):
        for v in self._avars.values(): v.set("")

    # ─────────────────────────────────────────────────────────────────────────
    #  Modify Item
    # ─────────────────────────────────────────────────────────────────────────
    def _build_modify(self):
        page = tk.Frame(self.page_container, bg=BG)
        self._pages["modify"] = page

        card = self._section_card(page, "Modify Existing Product", GREEN_MID)

        # Lookup row – uses _field_row for consistent alignment
        self._mod_search = tk.StringVar()
        se = self._field_row(card, "Find Item", self._mod_search)
        Autocomplete(se, self._get_item_names)
        # Add load button into the same row frame
        load_row = se.master.master.master  # entry → CardFrame.inner → CardFrame → row
        make_button(load_row, "Load", self._load_modify, style="primary").pack(side="left", padx=10)

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=20)

        fields = [("Name","mod_name"),("Description","mod_desc"),
                  ("Category","mod_cat"),("Price (Rs.)","mod_price"),("Quantity","mod_qty"),
                  ("Shelf X (1-6)","mod_x"), ("Shelf Y (1-16)","mod_y")]
        self._mvars = {}
        for lbl, key in fields:
            self._mvars[key] = tk.StringVar()
            self._field_row(card, lbl, self._mvars[key])

        btns = tk.Frame(card, bg=CARD, padx=20, pady=12)
        btns.pack(fill="x")
        make_button(btns, "✓ Save Changes", self._do_modify, style="success").pack(side="left")
        make_button(btns, "Clear", self._clear_modify, style="ghost").pack(side="left", padx=10)

        self._mod_msg = tk.Label(card, text="", bg=CARD, fg=GREEN,
                                  font=("Segoe UI", 12, "bold"), padx=20, pady=8)
        self._mod_msg.pack(anchor="w")
        self._mod_node = None

    def _load_modify(self):
        name = self._mod_search.get().strip()
        if not name:
            self._mod_msg.config(text="⚠  Enter an item name to load.", fg=AMBER); return
        self._load_data()
        node = avl_search(self._avl_root, name)
        if not node:
            self._mod_msg.config(text=f"✕  '{name}' not found.", fg=RED); return
        self._mod_node = node; i = node.data
        self._mvars["mod_name"].set(i.name)
        self._mvars["mod_desc"].set(i.description)
        self._mvars["mod_cat"].set(i.category)
        self._mvars["mod_price"].set(str(i.price))
        self._mvars["mod_qty"].set(str(i.quantity))
        shelf_cols = [2, 5, 8, 11, 14, 17]
        display_x = shelf_cols.index(i.loc_x) + 1 if i.loc_x in shelf_cols else 1
        self._mvars["mod_x"].set(str(display_x))
        display_y = i.loc_y - 1 if 2 <= i.loc_y <= 17 else i.loc_y
        self._mvars["mod_y"].set(str(display_y))
        self._mod_msg.config(text=f"✓  Loaded '{i.name}'. Edit and save.", fg=TEXT3)

    def _do_modify(self):
        if not self._mod_node:
            self._mod_msg.config(text="⚠  Load an item first.", fg=AMBER); return
        try:
            i = self._mod_node.data
            old_name = i.name
            
            new_name  = self._mvars["mod_name"].get().strip() or i.name
            new_desc  = self._mvars["mod_desc"].get().strip() or i.description
            new_cat   = self._mvars["mod_cat"].get().strip() or i.category
            new_price = int(self._mvars["mod_price"].get())
            new_qty   = int(self._mvars["mod_qty"].get())
            
            mx = self._mvars["mod_x"].get().strip()
            my = self._mvars["mod_y"].get().strip()
            if not mx or not my:
                self._mod_msg.config(text="⚠  Shelf X and Y are required.", fg=AMBER); return
                
            rx = int(mx); ry = int(my)
            if not (1 <= rx <= 6) or not (1 <= ry <= 16):
                self._mod_msg.config(text="⚠  Shelf X must be 1-6, Y must be 1-16.", fg=AMBER); return
                
            shelf_cols = [2, 5, 8, 11, 14, 17]
            nxv = shelf_cols[rx - 1]
            nyv = ry + 1
            
            # Uniqueness check (excluding current item)
            self._load_data()
            items = get_all_items(self._avl_root)
            for it in items:
                if it.name != old_name and it.loc_x == nxv and it.loc_y == nyv:
                    self._mod_msg.config(text=f"⚠  Shelf ({rx},{ry}) is occupied by '{it.name}'.", fg=AMBER); return

            i.name        = new_name
            i.description = new_desc
            i.category    = new_cat
            i.price       = new_price
            i.quantity    = new_qty
            i.loc_x       = nxv
            i.loc_y       = nyv
            
            self._mod_node.data = i
            save_to_file(self._avl_root)
            self._data_dirty = True
            self._mod_msg.config(text=f"✓  '{i.name}' updated.", fg=GREEN)
        except ValueError:
            self._mod_msg.config(text="⚠  Price, Qty, X, and Y must be integers.", fg=AMBER)

    def _clear_modify(self):
        self._mod_search.set("")
        for v in self._mvars.values(): v.set("")
        self._mod_node = None
        self._mod_msg.config(text="")

    # ─────────────────────────────────────────────────────────────────────────
    #  Search
    # ─────────────────────────────────────────────────────────────────────────
    def _build_search(self):
        page = tk.Frame(self.page_container, bg=BG)
        self._pages["search"] = page

        card = self._section_card(page, "Search Product", GREEN, expand=True)

        # Category Row
        self._srch_cat = tk.StringVar()
        ce = self._field_row(card, "Category", self._srch_cat)
        Autocomplete(ce, self._get_cat_suggestions)
        ce.bind("<Return>", lambda _: self._do_search())

        # Name Row
        self._srch_name = tk.StringVar()
        se = self._field_row(card, "Product Name", self._srch_name)
        Autocomplete(se, self._get_name_suggestions)
        se.bind("<Return>", lambda _: self._do_search())
        
        # Search Button Row
        btn_row = tk.Frame(card, bg=CARD, pady=10)
        btn_row.pack(fill="x", padx=20)
        make_button(btn_row, "Search ⌕", self._do_search, style="primary").pack(side="left")
        
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=20)
        
        self._srch_msg = tk.Label(card, text="", bg=CARD, fg=RED, font=("Segoe UI", 12))
        self._srch_msg.pack(anchor="w", padx=20, pady=5)
        self._srch_msg.pack_forget()
        
        # Scrollable area for cards
        scroll_wrapper = tk.Frame(card, bg=CARD)
        scroll_wrapper.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self._srch_canvas = tk.Canvas(scroll_wrapper, bg=CARD, highlightthickness=0)
        self._srch_scrollbar = tk.Scrollbar(scroll_wrapper, orient="vertical", command=self._srch_canvas.yview)
        self._srch_canvas.configure(yscrollcommand=self._srch_scrollbar.set)
        
        self._srch_scrollbar.pack(side="right", fill="y")
        self._srch_canvas.pack(side="left", fill="both", expand=True)
        
        self._srch_result = tk.Frame(self._srch_canvas, bg=CARD)
        self._srch_window = self._srch_canvas.create_window((0, 0), window=self._srch_result, anchor="nw")
        
        self._srch_result.bind("<Configure>", lambda e: self._srch_canvas.configure(scrollregion=self._srch_canvas.bbox("all")))
        self._srch_canvas.bind("<Configure>", lambda e: self._srch_canvas.itemconfig(self._srch_window, width=e.width))

    def _do_search(self):
        for w in self._srch_result.winfo_children(): w.destroy()
        cat_q = self._srch_cat.get().strip().lower()
        name_q = self._srch_name.get().strip().lower()
        
        if not cat_q and not name_q: return
        
        self._load_data()
        all_items = get_all_items(self._avl_root)
        
        matches = []
        for i in all_items:
            match_cat = not cat_q or cat_q in i.category.lower()
            match_name = not name_q or name_q in i.name.lower()
            if match_cat and match_name:
                matches.append(i)
                
        if not matches:
            self._srch_msg.config(text=f"✕  No items found.", fg=RED)
            self._srch_msg.pack(anchor="w", padx=20, pady=5)
            return
            
        self._srch_msg.pack_forget()
        for i in matches:
            # Result card
            res = CardFrame(self._srch_result, radius=8, bg=CARD2, shadow_color=CARD, border_color=BORDER)
            res.pack(fill="x", pady=10, padx=2)
            inner = tk.Frame(res.inner, bg=CARD2, padx=20, pady=16)
            inner.pack(side="left", fill="both", expand=True)
            tk.Label(inner, text=i.name, bg=CARD2, fg=TEXT,
                     font=("Segoe UI", 16, "bold")).pack(anchor="w")
            cat_pill = tk.Label(inner, text=f"  {i.category}  ",
                                bg=GREEN_PALE, fg=GREEN_DARK,
                                font=("Segoe UI", 9, "bold"), padx=4, pady=2)
            cat_pill.pack(anchor="w", pady=(2, 12))
            tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", pady=6)
            for k, v in [("Description", i.description),
                         ("Price", f"Rs. {i.price:,}"),
                         ("In Stock", str(i.quantity))]:
                r = tk.Frame(inner, bg=CARD2)
                r.pack(fill="x", pady=4)
                tk.Label(r, text=f"{k}:", bg=CARD2, fg=TEXT3,
                         font=("Segoe UI", 12), width=14, anchor="w").pack(side="left")
                color = AMBER if k == "In Stock" and i.quantity <= LOW_STOCK else TEXT
                tk.Label(r, text=v, bg=CARD2, fg=color,
                         font=("Segoe UI", 12, "bold")).pack(side="left")

    # ─────────────────────────────────────────────────────────────────────────
    #  Purchase
    # ─────────────────────────────────────────────────────────────────────────
    def _build_purchase(self):
        page = tk.Frame(self.page_container, bg=BG)
        self._pages["purchase"] = page

        card = self._section_card(page, "Purchase / Restock Items", GREEN)
        self._pur_name = tk.StringVar(); self._pur_qty = tk.StringVar()
        pur_ent = self._field_row(card, "Item Name",        self._pur_name)
        Autocomplete(pur_ent, self._get_item_names)
        self._field_row(card, "Quantity to Add",  self._pur_qty)

        btns = tk.Frame(card, bg=CARD, padx=20, pady=14)
        btns.pack(fill="x")
        make_button(btns, "↓ Confirm Purchase", self._do_purchase, style="success").pack(side="left")

        self._pur_msg = tk.Label(card, text="", bg=CARD, fg=GREEN,
                                  font=("Segoe UI", 12, "bold"), padx=20, pady=8)
        self._pur_msg.pack(anchor="w")

    def _do_purchase(self):
        name = self._pur_name.get().strip(); qty = self._pur_qty.get().strip()
        if not name or not qty:
            self._pur_msg.config(text="⚠  Both fields required.", fg=AMBER); return
        try: qv = int(qty)
        except ValueError:
            self._pur_msg.config(text="⚠  Quantity must be an integer.", fg=AMBER); return
        self._load_data()
        node = avl_search(self._avl_root, name)
        if not node:
            self._pur_msg.config(text=f"✕  '{name}' not found.", fg=RED); return
        node.data.quantity += qv
        save_to_file(self._avl_root)
        self._data_dirty = True
        log_transaction("BUY", name, qv)
        self._pur_msg.config(
            text=f"✓  Added {qv} units to '{name}'. New stock: {node.data.quantity}.",
            fg=GREEN)
        self._pur_name.set(""); self._pur_qty.set("")

    # ─────────────────────────────────────────────────────────────────────────
    #  Sell
    # ─────────────────────────────────────────────────────────────────────────
    def _build_sell(self):
        page = tk.Frame(self.page_container, bg=BG)
        self._pages["sell"] = page

        card = self._section_card(page, "Sell / Dispatch Items", AMBER)
        self._sell_name = tk.StringVar(); self._sell_qty = tk.StringVar()
        sell_ent = self._field_row(card, "Item Name",    self._sell_name)
        Autocomplete(sell_ent, self._get_item_names)
        self._field_row(card, "Quantity Sold", self._sell_qty)

        btns = tk.Frame(card, bg=CARD, padx=20, pady=14)
        btns.pack(fill="x")
        make_button(btns, "↑ Confirm Sale", self._do_sell, style="warning").pack(side="left")

        self._sell_msg = tk.Label(card, text="", bg=CARD, fg=GREEN,
                                   font=("Segoe UI", 12, "bold"), padx=20, pady=8)
        self._sell_msg.pack(anchor="w")

    def _do_sell(self):
        name = self._sell_name.get().strip(); qty = self._sell_qty.get().strip()
        if not name or not qty:
            self._sell_msg.config(text="⚠  Both fields required.", fg=AMBER); return
        try: qv = int(qty)
        except ValueError:
            self._sell_msg.config(text="⚠  Quantity must be an integer.", fg=AMBER); return
        self._load_data()
        node = avl_search(self._avl_root, name)
        if not node:
            self._sell_msg.config(text=f"✕  '{name}' not found.", fg=RED); return
        if qv > node.data.quantity:
            self._sell_msg.config(text=f"✕  Only {node.data.quantity} units in stock.", fg=RED); return
        node.data.quantity -= qv
        save_to_file(self._avl_root)
        self._data_dirty = True
        log_transaction("SELL", name, qv)
        self._sell_msg.config(
            text=f"✓  Sold {qv} units of '{name}'. Remaining: {node.data.quantity}.",
            fg=GREEN)
        self._sell_name.set(""); self._sell_qty.set("")

    # ─────────────────────────────────────────────────────────────────────────
    #  Low Stock
    # ─────────────────────────────────────────────────────────────────────────
    def _build_lowstock(self):
        page = tk.Frame(self.page_container, bg=BG)
        self._pages["lowstock"] = page

        hdr = tk.Frame(page, bg=BG)
        hdr.pack(fill="x", pady=(0, 12))

        alert_pill = tk.Label(hdr, text=f"  ⚠  Threshold: ≤ {LOW_STOCK} units  ",
                              bg="#FEF3C7", fg=AMBER,
                              font=("Segoe UI", 11, "bold"), padx=6, pady=4)
        alert_pill.pack(side="left")
        make_button(hdr, "⟳ Refresh", self._refresh_lowstock, style="ghost").pack(side="right")

        tcard = tk.Frame(page, bg=CARD)
        tcard.pack(fill="both", expand=True)
        tk.Frame(tcard, bg=BORDER, height=1).pack(fill="x")
        self.low_table = DataTable(
            tcard,
            columns=["Name", "Category", "Price (Rs.)", "In Stock"],
            col_weights=[3, 3, 3, 2],
        )
        self.low_table.pack(fill="both", expand=True)

    def _refresh_lowstock(self):
        self._load_data()
        items = get_all_items(self._avl_root)
        rows = []; tags = []
        for i in items:
            if i.quantity <= LOW_STOCK:
                rows.append((i.name, i.category, f"{i.price:,}", i.quantity))
                tags.append("low")
        self.low_table.load(rows, tags)

    # ─────────────────────────────────────────────────────────────────────────
    #  Delete
    # ─────────────────────────────────────────────────────────────────────────
    def _build_delete(self):
        page = tk.Frame(self.page_container, bg=BG)
        self._pages["delete"] = page

        card = self._section_card(page, "Delete Product", RED)
        self._del_name = tk.StringVar()
        del_ent = self._field_row(card, "Item Name", self._del_name)
        Autocomplete(del_ent, self._get_item_names)

        # Warning banner
        warn = tk.Frame(card, bg="#FEE2E2", padx=20, pady=10)
        warn.pack(fill="x", padx=20, pady=8)
        tk.Label(warn, text="⚠  This action is permanent and cannot be undone.",
                 bg="#FEE2E2", fg=RED, font=("Segoe UI", 11)).pack(anchor="w")

        btns = tk.Frame(card, bg=CARD, padx=20, pady=4)
        btns.pack(fill="x")
        make_button(btns, "✕ Delete Item", self._do_delete, style="danger").pack(side="left")

        self._del_msg = tk.Label(card, text="", bg=CARD, fg=GREEN,
                                  font=("Segoe UI", 12, "bold"), padx=20, pady=8)
        self._del_msg.pack(anchor="w")

    def _do_delete(self):
        name = self._del_name.get().strip()
        if not name:
            self._del_msg.config(text="⚠  Enter an item name.", fg=AMBER); return
        self._load_data()
        node = avl_search(self._avl_root, name)
        if not node:
            self._del_msg.config(text=f"✕  '{name}' not found.", fg=RED); return
        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Permanently delete '{name}'?\nThis action cannot be undone.",
            icon="warning")
        if not confirmed: return
        self._avl_root = avl_delete(self._avl_root, name)
        save_to_file(self._avl_root)
        self._data_dirty = True
        self._del_msg.config(text=f"✓  '{name}' deleted.", fg=GREEN)
        self._del_name.set("")

    # ─────────────────────────────────────────────────────────────────────────
    #  Transactions
    # ─────────────────────────────────────────────────────────────────────────
    def _build_transactions(self):
        page = tk.Frame(self.page_container, bg=BG)
        self._pages["transactions"] = page

        top = tk.Frame(page, bg=BG)
        top.pack(fill="x", pady=(0, 12))

        make_button(top, "⟳ Refresh", self._refresh_transactions, style="ghost").pack(side="right")

        tcard = tk.Frame(page, bg=CARD)
        tcard.pack(fill="both", expand=True)
        tk.Frame(tcard, bg=BORDER, height=1).pack(fill="x")
        self.txn_table = DataTable(
            tcard,
            columns=["Timestamp", "Type", "Item Name", "Quantity"],
            col_weights=[3, 2, 4, 2],
        )
        self.txn_table.pack(fill="both", expand=True)

    def _refresh_transactions(self):
        import os
        rows = []; tags = []
        if os.path.exists("transactions.txt"):
            with open("transactions.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in reversed(lines):
                    if not line.strip(): continue
                    try:
                        ts = line[1:20]
                        parts = line[22:].split("|")
                        t_type = parts[0].strip()
                        item = parts[1].strip()
                        qty = parts[2].replace("Qty:", "").strip()
                        rows.append((ts, t_type, item, qty))
                        tags.append("ok")
                    except Exception:
                        pass
        self.txn_table.load(rows, tags)

    # ─────────────────────────────────────────────────────────────────────────
    #  Warehouse Map
    # ─────────────────────────────────────────────────────────────────────────
    def _build_warehouse(self):
        page = tk.Frame(self.page_container, bg=BG)
        self._pages["warehouse"] = page

        left = tk.Frame(page, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        right = tk.Frame(page, bg=BG, width=320)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        map_card = CardFrame(left, radius=12, bg=CARD)
        map_card.pack(fill="both", expand=True)
        tk.Label(map_card.inner, text="Warehouse Floor Plan", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 14, "bold"), pady=10).pack()
        
        self.map_canvas = tk.Canvas(map_card.inner, bg=WHITE_DIM, highlightthickness=1, highlightbackground=BORDER)
        self.map_canvas.pack(fill="both", expand=True, padx=20, pady=20)
        self.map_canvas.bind("<Configure>", self._on_map_configure)
        self.map_canvas.bind("<Motion>", self._on_map_motion)
        
        ctrl_card = CardFrame(right, radius=12, bg=CARD)
        ctrl_card.pack(fill="both", expand=True)
        tk.Label(ctrl_card.inner, text="Order Pick List", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 14, "bold"), pady=10).pack()
                 
        self._pick_search = tk.StringVar()
        se = self._field_row(ctrl_card.inner, "Item", self._pick_search, label_width=8)
        Autocomplete(se, self._get_item_names)
        make_button(ctrl_card.inner, "+ Add to Pick List", self._add_to_picklist, style="primary").pack(pady=10)
        
        tk.Frame(ctrl_card.inner, bg=BORDER, height=1).pack(fill="x", pady=10)
        self.pick_listbox = tk.Listbox(ctrl_card.inner, bg=CARD2, fg=TEXT, font=("Segoe UI", 11),
                                       selectbackground=GREEN_PALE, selectforeground=GREEN_DARK,
                                       relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER)
        self.pick_listbox.pack(fill="both", expand=True, padx=20, pady=5)
        
        btns = tk.Frame(ctrl_card.inner, bg=CARD)
        btns.pack(fill="x", padx=20, pady=14)
        make_button(btns, "Generate Path", self._generate_pick_path, style="success").pack(side="left")
        make_button(btns, "Clear", lambda: self.pick_listbox.delete(0, tk.END), style="ghost").pack(side="right")
        
        self._wh_items = []
        self._path_nodes = []
        self._anim_idx = 0
        self._item_hitboxes = []
        self._tooltip_bg = None
        self._tooltip_text = None

    def _refresh_warehouse(self):
        self._load_data()
        self._wh_items = get_all_items(self._avl_root)
        self._draw_warehouse_grid()
        
    def _on_map_configure(self, event):
        self._draw_warehouse_grid()

    def _draw_warehouse_grid(self):
        c = self.map_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w <= 10 or h <= 10:
            return
            
        GRID = 20
        self.cw = w / GRID
        self.ch = h / GRID
        
        try:
            import pathfinding
        except ImportError:
            return
        
        # Batch background drawing
        for x in range(GRID):
            for y in range(GRID):
                x1, y1 = x * self.cw, y * self.ch
                x2, y2 = (x + 1) * self.cw, (y + 1) * self.ch
                if pathfinding.is_shelf(x, y):
                    c.create_rectangle(x1, y1, x2, y2, fill=TEXT3, outline=WHITE, tags="bg")
                else:
                    c.create_rectangle(x1, y1, x2, y2, fill=WHITE_DIM, outline=BORDER, tags="bg")
                    
        c.create_rectangle(0, 0, self.cw, self.ch, fill=AMBER, outline=AMBER, tags="bg")
        c.create_text(self.cw/2, self.ch/2, text="D", fill=WHITE, font=("Segoe UI", 10, "bold"), tags="bg")
                    
        self._item_hitboxes = []
        for i in self._wh_items:
            lx, ly = getattr(i, 'loc_x', 0), getattr(i, 'loc_y', 0)
            if 0 <= lx < GRID and 0 <= ly < GRID:
                cx, cy = lx * self.cw + self.cw/2, ly * self.ch + self.ch/2
                r = min(self.cw, self.ch) * 0.3
                c.create_oval(cx-r, cy-r, cx+r, cy+r, fill=BLUE, outline="", tags="item")
                self._item_hitboxes.append((cx-r, cy-r, cx+r, cy+r, i.name))
                
        self._tooltip_bg = c.create_rectangle(0, 0, 0, 0, fill=TEXT, outline="", state="hidden", tags="tooltip")
        self._tooltip_text = c.create_text(0, 0, text="", fill=WHITE, font=("Segoe UI", 10, "bold"), state="hidden", anchor="nw", tags="tooltip")

    def _on_map_motion(self, event):
        x, y = event.x, event.y
        hovered_name = None
        for x1, y1, x2, y2, name in self._item_hitboxes:
            if x1 <= x <= x2 and y1 <= y <= y2:
                hovered_name = name
                break
                
        if hovered_name:
            c = self.map_canvas
            c.itemconfig(self._tooltip_text, text=hovered_name, state="normal")
            c.coords(self._tooltip_text, x + 15, y + 15)
            bbox = c.bbox(self._tooltip_text)
            if bbox:
                c.coords(self._tooltip_bg, bbox[0]-6, bbox[1]-4, bbox[2]+6, bbox[3]+4)
                c.itemconfig(self._tooltip_bg, state="normal")
                c.tag_raise(self._tooltip_bg)
                c.tag_raise(self._tooltip_text)
        else:
            if self._tooltip_text and self._tooltip_bg:
                self.map_canvas.itemconfig(self._tooltip_text, state="hidden")
                self.map_canvas.itemconfig(self._tooltip_bg, state="hidden")
                
    def _add_to_picklist(self):
        if self.pick_listbox.size() >= 3:
            messagebox.showwarning("Limit Reached", "The pick-up list is limited to 3 items to ensure optimal pathfinding.")
            return
        name = self._pick_search.get().strip()
        if name:
            self.pick_listbox.insert(tk.END, name)
            self._pick_search.set("")
            
    def _generate_pick_path(self):
        try:
            import pathfinding
        except ImportError:
            return
            
        self._draw_warehouse_grid()
        
        pick_names = self.pick_listbox.get(0, tk.END)
        if not pick_names: return
        
        items_to_pick = []
        for name in pick_names:
            node = avl_search(self._avl_root, name)
            if node:
                items_to_pick.append(node.data)
                
        c = self.map_canvas
        for i in items_to_pick:
            lx, ly = getattr(i, 'loc_x', 0), getattr(i, 'loc_y', 0)
            cx, cy = lx * self.cw + self.cw/2, ly * self.ch + self.ch/2
            r = min(self.cw, self.ch) * 0.4
            c.create_oval(cx-r, cy-r, cx+r, cy+r, fill=RED, outline=WHITE, width=2)
            
        path, events = pathfinding.get_optimal_pick_path((0, 0), items_to_pick)
        
        if not path:
            return
            
        self._path_nodes = path
        self._anim_idx = 0
        self._animate_path()
        
    def _animate_path(self):
        if self._anim_idx >= len(self._path_nodes) - 1:
            return
            
        c = self.map_canvas
        p1 = self._path_nodes[self._anim_idx]
        p2 = self._path_nodes[self._anim_idx + 1]
        
        x1, y1 = p1[0] * self.cw + self.cw/2, p1[1] * self.ch + self.ch/2
        x2, y2 = p2[0] * self.cw + self.cw/2, p2[1] * self.ch + self.ch/2
        
        c.create_line(x1, y1, x2, y2, fill=GREEN, width=4, capstyle="round", joinstyle="round")
        
        c.delete("worker")
        r = min(self.cw, self.ch) * 0.3
        c.create_oval(x2-r, y2-r, x2+r, y2+r, fill=GREEN_DARK, outline=WHITE, tags="worker")
        
        self._anim_idx += 1
        c.after(40, self._animate_path)

    # ─────────────────────────────────────────────────────────────────────────
    #  Shared helpers
    # ─────────────────────────────────────────────────────────────────────────
    def _section_card(self, parent, title, accent, expand=False):
        wrapper = tk.Frame(parent, bg=BG)
        if expand:
            wrapper.pack(fill="both", expand=True, anchor="n")
        else:
            wrapper.pack(fill="x", anchor="n")
            
        card = CardFrame(wrapper, radius=12, bg=CARD)
        if expand:
            card.pack(fill="both", expand=True)
        else:
            card.pack(fill="x")
        # Title row
        tk.Label(card.inner, text=title, bg=CARD, fg=TEXT,
                 font=("Segoe UI", 15, "bold"),
                 pady=14, padx=20, anchor="w").pack(fill="x")
        tk.Frame(card.inner, bg=BORDER, height=1).pack(fill="x", padx=20)
        return card.inner

    def _get_item_names(self):
        self._load_data()
        return [i.name for i in get_all_items(self._avl_root)]

    def _get_cat_suggestions(self):
        self._load_data()
        items = get_all_items(self._avl_root)
        return sorted(list(set([i.category for i in items])))

    def _get_name_suggestions(self):
        self._load_data()
        items = get_all_items(self._avl_root)
        cat_filter = getattr(self, '_srch_cat', None)
        if cat_filter and cat_filter.get().strip():
            target_cat = cat_filter.get().strip().lower()
            return sorted(list(set([i.name for i in items if i.category.lower() == target_cat])))
        return sorted(list(set([i.name for i in items])))

    def _field_row(self, parent, label, var, label_width=18):
        row = tk.Frame(parent, bg=CARD, pady=4)
        row.pack(fill="x", padx=20)
        tk.Label(row, text=label, bg=CARD, fg=TEXT2,
                 font=("Segoe UI", 12), width=label_width, anchor="w").pack(side="left")
        sf, se = make_entry(row, var)
        sf.pack(side="left", fill="x", expand=True)
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=20)
        return se


# ─────────────────────────────────────────────────────────────────────────────
#  Color helpers
# ─────────────────────────────────────────────────────────────────────────────
def _darken(hex_color, amount=20):
    hex_color = hex_color.lstrip("#")
    r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    r = max(0, r - amount); g = max(0, g - amount); b = max(0, b - amount)
    return f"#{r:02x}{g:02x}{b:02x}"

def _hex_alpha(hex_color, alpha=200):
    """Blend hex color toward white at given alpha (0-255)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    a = alpha / 255
    r = int(r * a + 255 * (1-a))
    g = int(g * a + 255 * (1-a))
    b = int(b * a + 255 * (1-a))
    return f"#{r:02x}{g:02x}{b:02x}"


# ─────────────────────────────────────────────────────────────────────────────
#  End of GUI Module
# ─────────────────────────────────────────────────────────────────────────────