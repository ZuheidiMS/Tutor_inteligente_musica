import tkinter as tk
from tkinter import ttk


# ============================================================
# PALETA LOGISMART
# ============================================================

BG = "#F5F7FA"
SURFACE = "#FFFFFF"
SURFACE_SOFT = "#F8FAFC"

PRIMARY = "#2563EB"
PRIMARY_DARK = "#1D4ED8"
PRIMARY_SOFT = "#EFF6FF"

TEXT = "#111827"
TEXT_SECONDARY = "#64748B"
TEXT_MUTED = "#94A3B8"

BORDER = "#E2E8F0"

SIDEBAR = "#0F172A"
SIDEBAR_HOVER = "#1E293B"
SIDEBAR_ACTIVE = "#2563EB"

SUCCESS = "#16A34A"
SUCCESS_SOFT = "#F0FDF4"

WARNING = "#D97706"
WARNING_SOFT = "#FFFBEB"

DANGER = "#DC2626"
DANGER_SOFT = "#FEF2F2"

INFO = "#0891B2"
INFO_SOFT = "#ECFEFF"


# ============================================================
# FUENTES
# ============================================================

FONT_TITLE = ("Segoe UI", 26, "bold")
FONT_SUBTITLE = ("Segoe UI", 11)
FONT_SECTION = ("Segoe UI", 15, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_BUTTON = ("Segoe UI", 10, "bold")
FONT_NUMBER = ("Segoe UI", 24, "bold")


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

def configurar_tema(root):

    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        ".",
        font=FONT_BODY
    )

    style.configure(
        "TEntry",
        padding=9,
        fieldbackground=SURFACE,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER
    )

    style.configure(
        "TCombobox",
        padding=8,
        fieldbackground=SURFACE,
        background=SURFACE
    )

    style.configure(
        "Treeview",
        background=SURFACE,
        fieldbackground=SURFACE,
        foreground=TEXT,
        rowheight=38,
        borderwidth=0,
        font=FONT_BODY
    )

    style.configure(
        "Treeview.Heading",
        background="#F8FAFC",
        foreground=TEXT_SECONDARY,
        font=("Segoe UI", 9, "bold"),
        padding=10,
        relief="flat"
    )

    style.map(
        "Treeview",
        background=[
            ("selected", PRIMARY_SOFT)
        ],
        foreground=[
            ("selected", TEXT)
        ]
    )

    style.configure(
        "TScrollbar",
        background="#CBD5E1",
        troughcolor="#F8FAFC",
        borderwidth=0
    )

    style.configure(
        "Horizontal.TProgressbar",
        troughcolor="#E2E8F0",
        background=PRIMARY,
        thickness=8
    )

    return style


# ============================================================
# BOTONES
# ============================================================

def boton(
    parent,
    texto,
    comando,
    tipo="primary",
    width=None
):

    colores = {
        "primary": (PRIMARY, PRIMARY_DARK, "white"),
        "success": (SUCCESS, "#15803D", "white"),
        "warning": (WARNING, "#B45309", "white"),
        "danger": (DANGER, "#B91C1C", "white"),
        "secondary": ("#E2E8F0", "#CBD5E1", TEXT)
    }

    normal, hover, foreground = colores.get(
        tipo,
        colores["primary"]
    )

    button = tk.Button(
        parent,
        text=texto,
        command=comando,
        font=FONT_BUTTON,
        bg=normal,
        fg=foreground,
        activebackground=hover,
        activeforeground=foreground,
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=18,
        pady=10
    )

    if width:
        button.config(width=width)

    def entrar(event):
        button.config(bg=hover)

    def salir(event):
        button.config(bg=normal)

    button.bind("<Enter>", entrar)
    button.bind("<Leave>", salir)

    return button


# ============================================================
# TARJETAS
# ============================================================

def tarjeta(parent):

    return tk.Frame(
        parent,
        bg=SURFACE,
        bd=0,
        highlightthickness=1,
        highlightbackground=BORDER
    )


def etiqueta_titulo(parent, texto):

    return tk.Label(
        parent,
        text=texto,
        font=FONT_SECTION,
        bg=SURFACE,
        fg=TEXT
    )


def etiqueta_secundaria(parent, texto):

    return tk.Label(
        parent,
        text=texto,
        font=FONT_SMALL,
        bg=SURFACE,
        fg=TEXT_SECONDARY
    )


# ============================================================
# BADGES
# ============================================================

def badge(parent, texto, tipo="info"):

    configuraciones = {
        "success": (SUCCESS_SOFT, SUCCESS),
        "warning": (WARNING_SOFT, WARNING),
        "danger": (DANGER_SOFT, DANGER),
        "info": (INFO_SOFT, INFO),
        "primary": (PRIMARY_SOFT, PRIMARY),
        "neutral": ("#F1F5F9", TEXT_SECONDARY)
    }

    fondo, color = configuraciones.get(
        tipo,
        configuraciones["neutral"]
    )

    return tk.Label(
        parent,
        text=texto,
        font=("Segoe UI", 9, "bold"),
        bg=fondo,
        fg=color,
        padx=10,
        pady=5
    )


# ============================================================
# ENCABEZADO DE VISTA
# ============================================================

def encabezado(parent, titulo, descripcion):

    frame = tk.Frame(
        parent,
        bg=BG
    )

    frame.pack(
        fill="x",
        padx=32,
        pady=(28, 20)
    )

    tk.Label(
        frame,
        text=titulo,
        font=FONT_TITLE,
        bg=BG,
        fg=TEXT
    ).pack(anchor="w")

    tk.Label(
        frame,
        text=descripcion,
        font=FONT_SUBTITLE,
        bg=BG,
        fg=TEXT_SECONDARY
    ).pack(
        anchor="w",
        pady=(5, 0)
    )

    return frame


# ============================================================
# SEPARADOR
# ============================================================

def separador(parent):

    return tk.Frame(
        parent,
        bg=BORDER,
        height=1
    )