import tkinter as tk
from tkinter import ttk

from gui.theme import (
    BG,
    SURFACE,
    SURFACE_SOFT,
    PRIMARY,
    PRIMARY_DARK,
    PRIMARY_SOFT,
    TEXT,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BORDER,
    SUCCESS,
    SUCCESS_SOFT,
    WARNING,
    WARNING_SOFT,
    DANGER,
    DANGER_SOFT,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_SECTION,
    FONT_BODY,
    FONT_SMALL,
    FONT_BUTTON,
    boton,
    tarjeta,
    encabezado,
)


class VerdadView(tk.Frame):

    def __init__(self, parent, app=None):
        super().__init__(parent, bg=BG)

        self.app = app

        # ==========================================
        # PREMISAS
        # ==========================================

        self.vars = {
            "P": tk.BooleanVar(value=False),
            "Q": tk.BooleanVar(value=False),
            "R": tk.BooleanVar(value=False),
            "S": tk.BooleanVar(value=False),
            "T": tk.BooleanVar(value=False),
            "HR": tk.BooleanVar(value=False),
        }

        self.crear_interfaz()

    # ==========================================
    # INTERFAZ PRINCIPAL
    # ==========================================

    def crear_interfaz(self):

        # ==========================================
        # CONTENEDOR PRINCIPAL CON SCROLL
        # ==========================================

        contenedor = tk.Frame(
            self,
            bg=BG
        )

        contenedor.pack(
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            contenedor,
            bg=BG,
            highlightthickness=0,
            bd=0
        )

        scrollbar = ttk.Scrollbar(
            contenedor,
            orient="vertical",
            command=self.canvas.yview
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        # ==========================================
        # CONTENIDO INTERNO
        # ==========================================

        self.contenido = tk.Frame(
            self.canvas,
            bg=BG
        )

        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.contenido,
            anchor="nw"
        )

        self.contenido.bind(
            "<Configure>",
            self.actualizar_scroll
        )

        self.canvas.bind(
            "<Configure>",
            self.ajustar_ancho
        )

        # ==========================================
        # SCROLL CON RUEDA DEL MOUSE
        # IMPORTANTE:
        # Se usa bind(), NO bind_all().
        # ==========================================

        self.canvas.bind(
            "<MouseWheel>",
            self.scroll_mouse
        )

        self.canvas.bind(
            "<Button-4>",
            self.scroll_arriba
        )

        self.canvas.bind(
            "<Button-5>",
            self.scroll_abajo
        )

        # ==========================================
        # ENCABEZADO
        # ==========================================

        encabezado(
            self.contenido,
            "Simulador de tabla de verdad",
            "Modifica las premisas y observa cómo cambian las reglas en tiempo real."
        )

        # ==========================================
        # PANEL DE PREMISAS
        # ==========================================

        controles = tarjeta(
            self.contenido
        )

        controles.pack(
            fill="x",
            padx=32,
            pady=(0, 18)
        )

        tk.Label(
            controles,
            text="Premisas",
            font=FONT_SECTION,
            bg=SURFACE,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )

        tk.Label(
            controles,
            text="Activa o desactiva cada premisa para simular diferentes escenarios.",
            font=FONT_SMALL,
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        # ==========================================
        # GRID DE PREMISAS
        # ==========================================

        grid = tk.Frame(
            controles,
            bg=SURFACE
        )

        grid.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        for columna in range(3):
            grid.columnconfigure(
                columna,
                weight=1
            )

        self.crear_interruptor(
            grid,
            "P",
            "Autorización vigente",
            0,
            0
        )

        self.crear_interruptor(
            grid,
            "Q",
            "Restricción activa",
            0,
            1
        )

        self.crear_interruptor(
            grid,
            "R",
            "Material peligroso",
            0,
            2
        )

        self.crear_interruptor(
            grid,
            "S",
            "Documentación completa",
            1,
            0
        )

        self.crear_interruptor(
            grid,
            "T",
            "Certificación vigente",
            1,
            1
        )

        self.crear_interruptor(
            grid,
            "HR",
            "Horario restringido",
            1,
            2
        )

        # ==========================================
        # RESULTADOS EN VIVO
        # ==========================================

        resultados = tarjeta(
            self.contenido
        )

        resultados.pack(
            fill="x",
            padx=32,
            pady=(0, 18)
        )

        tk.Label(
            resultados,
            text="Resultados en vivo",
            font=FONT_SECTION,
            bg=SURFACE,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        resultados_grid = tk.Frame(
            resultados,
            bg=SURFACE
        )

        resultados_grid.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        for columna in range(4):
            resultados_grid.columnconfigure(
                columna,
                weight=1
            )

        self.resultado_A = self.crear_resultado(
            resultados_grid,
            "A",
            "Acceso estándar",
            0
        )

        self.resultado_E = self.crear_resultado(
            resultados_grid,
            "E",
            "Inspección especial",
            1
        )

        self.resultado_C = self.crear_resultado(
            resultados_grid,
            "C",
            "Certificación",
            2
        )

        self.resultado_H = self.crear_resultado(
            resultados_grid,
            "H",
            "Horario restringido",
            3
        )

        # ==========================================
        # EXPLICACIÓN DE LAS REGLAS
        # ==========================================

        explicacion = tarjeta(
            self.contenido
        )

        explicacion.pack(
            fill="x",
            padx=32,
            pady=(0, 18)
        )

        tk.Label(
            explicacion,
            text="Reglas utilizadas",
            font=FONT_SECTION,
            bg=SURFACE,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 10)
        )

        texto_reglas = (
            "A = P ∧ S ∧ ¬Q\n"
            "Acceso estándar: requiere autorización, documentación completa "
            "y ausencia de restricción.\n\n"
            "E = P ∧ (R ∨ Q)\n"
            "Inspección especial: requiere autorización y que exista material "
            "peligroso o una restricción activa.\n\n"
            "C = P ∧ T ∧ ¬Q\n"
            "Certificación: requiere autorización, certificación vigente "
            "y ausencia de restricción.\n\n"
            "H = R ∧ HR\n"
            "Horario restringido: se activa cuando existe material peligroso "
            "y el horario está restringido."
        )

        tk.Label(
            explicacion,
            text=texto_reglas,
            font=FONT_BODY,
            bg=SURFACE,
            fg=TEXT,
            justify="left",
            anchor="w"
        ).pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        # ==========================================
        # TABLA DE VERDAD
        # ==========================================

        tabla_frame = tarjeta(
            self.contenido
        )

        tabla_frame.pack(
            fill="x",
            padx=32,
            pady=(0, 32)
        )

        tk.Label(
            tabla_frame,
            text="Tabla de verdad completa",
            font=FONT_SECTION,
            bg=SURFACE,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )

        tk.Label(
            tabla_frame,
            text="Existen 64 combinaciones posibles (2⁶). Cada fila representa un escenario diferente.",
            font=FONT_SMALL,
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        # ==========================================
        # CONTENEDOR DE TABLA
        # ==========================================

        tabla_contenedor = tk.Frame(
            tabla_frame,
            bg=SURFACE
        )

        tabla_contenedor.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        columnas = (
            "#",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "HR",
            "A",
            "E",
            "C",
            "H"
        )

        self.tabla = ttk.Treeview(
            tabla_contenedor,
            columns=columnas,
            show="headings",
            height=16
        )

        # ==========================================
        # CONFIGURACIÓN DE COLUMNAS
        # ==========================================

        for columna in columnas:

            self.tabla.heading(
                columna,
                text=columna
            )

            if columna == "#":
                ancho = 55
            else:
                ancho = 65

            self.tabla.column(
                columna,
                width=ancho,
                minwidth=45,
                anchor="center"
            )

        # ==========================================
        # SCROLL DE LA TABLA
        # ==========================================

        scrollbar_tabla = ttk.Scrollbar(
            tabla_contenedor,
            orient="vertical",
            command=self.tabla.yview
        )

        self.tabla.configure(
            yscrollcommand=scrollbar_tabla.set
        )

        self.tabla.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar_tabla.pack(
            side="right",
            fill="y"
        )

        # ==========================================
        # CARGAR LAS 64 COMBINACIONES
        # ==========================================

        self.cargar_tabla()

        # ==========================================
        # PRIMERA EVALUACIÓN
        # ==========================================

        self.actualizar()

        # ==========================================
        # ACTUALIZAR SCROLL
        # ==========================================

        self.canvas.update_idletasks()

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    # ==========================================
    # CREAR INTERRUPTOR
    # ==========================================

    def crear_interruptor(
        self,
        parent,
        codigo,
        descripcion,
        fila,
        columna
    ):

        frame = tk.Frame(
            parent,
            bg=SURFACE_SOFT,
            highlightthickness=1,
            highlightbackground=BORDER
        )

        frame.grid(
            row=fila,
            column=columna,
            padx=6,
            pady=6,
            sticky="nsew"
        )

        contenido = tk.Frame(
            frame,
            bg=SURFACE_SOFT
        )

        contenido.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=10
        )

        # ==========================================
        # LETRA
        # ==========================================

        tk.Label(
            contenido,
            text=codigo,
            font=("Segoe UI", 16, "bold"),
            bg=SURFACE_SOFT,
            fg=PRIMARY
        ).pack(
            side="left",
            padx=(0, 10)
        )

        # ==========================================
        # DESCRIPCIÓN
        # ==========================================

        textos = tk.Frame(
            contenido,
            bg=SURFACE_SOFT
        )

        textos.pack(
            side="left",
            fill="x",
            expand=True
        )

        tk.Label(
            textos,
            text=descripcion,
            font=FONT_BODY,
            bg=SURFACE_SOFT,
            fg=TEXT,
            anchor="w"
        ).pack(
            anchor="w"
        )

        # ==========================================
        # ESTADO
        # ==========================================

        estado = tk.Label(
            textos,
            text="FALSO",
            font=("Segoe UI", 8, "bold"),
            bg=SURFACE_SOFT,
            fg=TEXT_MUTED
        )

        estado.pack(
            anchor="w",
            pady=(2, 0)
        )

        # ==========================================
        # CHECKBOX
        # ==========================================

        ttk.Checkbutton(
            contenido,
            variable=self.vars[codigo],
            command=lambda: self.actualizar_interruptor(
                codigo,
                estado
            )
        ).pack(
            side="right"
        )

    # ==========================================
    # ACTUALIZAR INTERRUPTOR
    # ==========================================

    def actualizar_interruptor(
        self,
        codigo,
        etiqueta
    ):

        if self.vars[codigo].get():

            etiqueta.config(
                text="VERDADERO",
                fg=SUCCESS
            )

        else:

            etiqueta.config(
                text="FALSO",
                fg=TEXT_MUTED
            )

        self.actualizar()

    # ==========================================
    # CREAR RESULTADO
    # ==========================================

    def crear_resultado(
        self,
        parent,
        codigo,
        descripcion,
        columna
    ):

        frame = tk.Frame(
            parent,
            bg=SURFACE_SOFT,
            highlightthickness=1,
            highlightbackground=BORDER
        )

        frame.grid(
            row=0,
            column=columna,
            padx=5,
            sticky="nsew"
        )

        tk.Label(
            frame,
            text=codigo,
            font=("Segoe UI", 18, "bold"),
            bg=SURFACE_SOFT,
            fg=PRIMARY
        ).pack(
            pady=(12, 3)
        )

        tk.Label(
            frame,
            text=descripcion,
            font=FONT_SMALL,
            bg=SURFACE_SOFT,
            fg=TEXT_SECONDARY
        ).pack()

        resultado = tk.Label(
            frame,
            text="FALSO",
            font=("Segoe UI", 11, "bold"),
            bg=DANGER_SOFT,
            fg=DANGER,
            padx=10,
            pady=8
        )

        resultado.pack(
            fill="x",
            padx=10,
            pady=10
        )

        return resultado

    # ==========================================
    # CÁLCULO DE LAS REGLAS
    # ==========================================

    def calcular(
        self,
        P,
        Q,
        R,
        S,
        T,
        HR
    ):

        # Regla principal A
        # A = P ∧ S ∧ ¬Q

        A = P and S and (not Q)

        # Regla principal E
        # E = P ∧ (R ∨ Q)

        E = P and (R or Q)

        # Regla adicional C
        # C = P ∧ T ∧ ¬Q

        C = P and T and (not Q)

        # Regla adicional H
        # H = R ∧ HR

        H = R and HR

        return A, E, C, H

    # ==========================================
    # ACTUALIZAR RESULTADOS
    # ==========================================

    def actualizar(self):

        P = self.vars["P"].get()
        Q = self.vars["Q"].get()
        R = self.vars["R"].get()
        S = self.vars["S"].get()
        T = self.vars["T"].get()
        HR = self.vars["HR"].get()

        A, E, C, H = self.calcular(
            P,
            Q,
            R,
            S,
            T,
            HR
        )

        self.actualizar_resultado(
            self.resultado_A,
            A
        )

        self.actualizar_resultado(
            self.resultado_E,
            E
        )

        self.actualizar_resultado(
            self.resultado_C,
            C
        )

        self.actualizar_resultado(
            self.resultado_H,
            H
        )

    # ==========================================
    # ACTUALIZAR COLOR DEL RESULTADO
    # ==========================================

    def actualizar_resultado(
        self,
        etiqueta,
        valor
    ):

        if valor:

            etiqueta.config(
                text="VERDADERO",
                bg=SUCCESS_SOFT,
                fg=SUCCESS
            )

        else:

            etiqueta.config(
                text="FALSO",
                bg=DANGER_SOFT,
                fg=DANGER
            )

    # ==========================================
    # CARGAR TABLA DE VERDAD
    # ==========================================

    def cargar_tabla(self):

        valores = [
            False,
            True
        ]

        numero = 1

        # ==========================================
        # 2⁶ = 64 COMBINACIONES
        # ==========================================

        for P in valores:

            for Q in valores:

                for R in valores:

                    for S in valores:

                        for T in valores:

                            for HR in valores:

                                A, E, C, H = self.calcular(
                                    P,
                                    Q,
                                    R,
                                    S,
                                    T,
                                    HR
                                )

                                self.tabla.insert(
                                    "",
                                    "end",
                                    values=(
                                        numero,
                                        "V" if P else "F",
                                        "V" if Q else "F",
                                        "V" if R else "F",
                                        "V" if S else "F",
                                        "V" if T else "F",
                                        "V" if HR else "F",
                                        "V" if A else "F",
                                        "V" if E else "F",
                                        "V" if C else "F",
                                        "V" if H else "F"
                                    )
                                )

                                numero += 1

    # ==========================================
    # SCROLL PRINCIPAL
    # ==========================================

    def actualizar_scroll(
        self,
        event=None
    ):

        try:

            if not self.winfo_exists():
                return

            if not hasattr(self, "canvas"):
                return

            if not self.canvas.winfo_exists():
                return

            self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )

        except (
            tk.TclError,
            AttributeError
        ):
            pass

    def ajustar_ancho(
        self,
        event
    ):

        try:

            if not self.winfo_exists():
                return

            if not hasattr(self, "canvas"):
                return

            if not self.canvas.winfo_exists():
                return

            self.canvas.itemconfig(
                self.window_id,
                width=event.width
            )

        except (
            tk.TclError,
            AttributeError
        ):
            pass

    # ==========================================
    # RUEDA DEL MOUSE
    # ==========================================

    def scroll_mouse(
        self,
        event
    ):

        try:

            if not self.winfo_exists():
                return

            if not hasattr(self, "canvas"):
                return

            if not self.canvas.winfo_exists():
                return

            delta = event.delta

            if delta == 0:
                return

            self.canvas.yview_scroll(
                int(-1 * (delta / 120)),
                "units"
            )

        except (
            tk.TclError,
            AttributeError
        ):
            pass

    # ==========================================
    # SCROLL HACIA ARRIBA
    # ==========================================

    def scroll_arriba(
        self,
        event
    ):

        try:

            if not self.winfo_exists():
                return

            if not hasattr(self, "canvas"):
                return

            if not self.canvas.winfo_exists():
                return

            self.canvas.yview_scroll(
                -1,
                "units"
            )

        except (
            tk.TclError,
            AttributeError
        ):
            pass

    # ==========================================
    # SCROLL HACIA ABAJO
    # ==========================================

    def scroll_abajo(
        self,
        event
    ):

        try:

            if not self.winfo_exists():
                return

            if not hasattr(self, "canvas"):
                return

            if not self.canvas.winfo_exists():
                return

            self.canvas.yview_scroll(
                1,
                "units"
            )

        except (
            tk.TclError,
            AttributeError
        ):
            pass