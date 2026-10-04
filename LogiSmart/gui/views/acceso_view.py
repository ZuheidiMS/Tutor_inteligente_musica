import tkinter as tk
from tkinter import ttk, messagebox

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
    INFO,
    INFO_SOFT,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_SECTION,
    FONT_BODY,
    FONT_SMALL,
    FONT_BUTTON,
    boton,
    tarjeta,
    encabezado,
    badge,
)

from logiuncodigo import (
    evaluar_camion,
    evaluar_certificacion,
    evaluar_horario_restringido,
)


class AccesoView(tk.Frame):

    def __init__(self, parent, app=None):
        super().__init__(parent, bg=BG)
        self.app = app

        # ==========================================
        # VARIABLES
        # ==========================================

        self.var_placa = tk.StringVar()
        self.var_camion_id = tk.StringVar()
        self.var_empresa = tk.StringVar()

        self.var_P = tk.BooleanVar(value=True)
        self.var_Q = tk.BooleanVar(value=False)
        self.var_R = tk.BooleanVar(value=False)
        self.var_S = tk.BooleanVar(value=True)
        self.var_T = tk.BooleanVar(value=True)
        self.var_HR = tk.BooleanVar(value=False)

        self.crear_interfaz()

    # ==========================================
    # INTERFAZ PRINCIPAL
    # ==========================================

    def crear_interfaz(self):

        # ------------------------------------------
        # CONTENEDOR PRINCIPAL CON SCROLL
        # ------------------------------------------

        contenedor = tk.Frame(self, bg=BG)
        contenedor.pack(fill="both", expand=True)

        # Canvas
        self.canvas = tk.Canvas(
            contenedor,
            bg=BG,
            highlightthickness=0,
            bd=0
        )

        # Scrollbar vertical
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

        # ------------------------------------------
        # FRAME INTERNO
        # ------------------------------------------

        self.contenido = tk.Frame(
            self.canvas,
            bg=BG
        )

        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.contenido,
            anchor="nw"
        )

        # Ajustar scroll al contenido
        self.contenido.bind(
            "<Configure>",
            self.actualizar_scroll
        )

        # Hacer que el contenido ocupe todo el ancho
        self.canvas.bind(
            "<Configure>",
            self.ajustar_ancho
        )

        # Mouse wheel
        self.canvas.bind_all(
            "<MouseWheel>",
            self.scroll_mouse
        )

        # Linux / otros sistemas
        self.canvas.bind_all(
            "<Button-4>",
            self.scroll_arriba
        )

        self.canvas.bind_all(
            "<Button-5>",
            self.scroll_abajo
        )

        # ------------------------------------------
        # ENCABEZADO
        # ------------------------------------------

        encabezado(
            self.contenido,
            "Control de acceso",
            "Evalúa las condiciones de un camión mediante lógica proposicional."
        )

        # ------------------------------------------
        # IDENTIFICACIÓN DEL CAMIÓN
        # ------------------------------------------

        identificacion = tarjeta(self.contenido)

        identificacion.pack(
            fill="x",
            padx=32,
            pady=(0, 18)
        )

        tk.Label(
            identificacion,
            text="Identificación del camión",
            font=FONT_SECTION,
            bg=SURFACE,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        campos = tk.Frame(
            identificacion,
            bg=SURFACE
        )

        campos.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        self.crear_campo(
            campos,
            "Placa",
            self.var_placa,
            0
        )

        self.crear_campo(
            campos,
            "Camión ID",
            self.var_camion_id,
            1
        )

        self.crear_campo(
            campos,
            "Empresa",
            self.var_empresa,
            2
        )

        # ------------------------------------------
        # PREMISAS
        # ------------------------------------------

        condiciones = tarjeta(self.contenido)

        condiciones.pack(
            fill="x",
            padx=32,
            pady=(0, 18)
        )

        tk.Label(
            condiciones,
            text="Condiciones de acceso",
            font=FONT_SECTION,
            bg=SURFACE,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )

        tk.Label(
            condiciones,
            text="Activa o desactiva las premisas para simular diferentes escenarios.",
            font=FONT_SMALL,
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        # ------------------------------------------
        # GRID DE CONDICIONES
        # ------------------------------------------

        grid = tk.Frame(
            condiciones,
            bg=SURFACE
        )

        grid.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        for columna in range(2):
            grid.columnconfigure(
                columna,
                weight=1
            )

        self.crear_condicion(
            grid,
            "P",
            "Autorización vigente",
            self.var_P,
            0,
            0
        )

        self.crear_condicion(
            grid,
            "Q",
            "Restricción activa",
            self.var_Q,
            0,
            1
        )

        self.crear_condicion(
            grid,
            "R",
            "Material peligroso",
            self.var_R,
            1,
            0
        )

        self.crear_condicion(
            grid,
            "S",
            "Documentación completa",
            self.var_S,
            1,
            1
        )

        self.crear_condicion(
            grid,
            "T",
            "Certificación vigente",
            self.var_T,
            2,
            0
        )

        self.crear_condicion(
            grid,
            "HR",
            "Horario restringido",
            self.var_HR,
            2,
            1
        )

        # ------------------------------------------
        # BOTÓN EVALUAR
        # ------------------------------------------

        zona_boton = tk.Frame(
            self.contenido,
            bg=BG
        )

        zona_boton.pack(
            fill="x",
            padx=32,
            pady=(0, 18)
        )

        boton(
            zona_boton,
            "Evaluar acceso",
            self.evaluar,
            tipo="primary"
        ).pack(
            anchor="e"
        )

        # ------------------------------------------
        # RESULTADO
        # ------------------------------------------

        self.resultado_frame = tarjeta(
            self.contenido
        )

        self.resultado_frame.pack(
            fill="x",
            padx=32,
            pady=(0, 32)
        )

        tk.Label(
            self.resultado_frame,
            text="Resultado de la evaluación",
            font=FONT_SECTION,
            bg=SURFACE,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        self.resultado_label = tk.Label(
            self.resultado_frame,
            text="Configura las condiciones y presiona «Evaluar acceso».",
            font=("Segoe UI", 12, "bold"),
            bg=SURFACE_SOFT,
            fg=TEXT_SECONDARY,
            padx=18,
            pady=16
        )

        self.resultado_label.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        self.explicacion_label = tk.Label(
            self.resultado_frame,
            text="",
            font=FONT_BODY,
            bg=SURFACE,
            fg=TEXT,
            justify="left",
            anchor="w"
        )

        self.explicacion_label.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        # Iniciar arriba
        self.canvas.update_idletasks()
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    # ==========================================
    # CAMPO DE TEXTO
    # ==========================================

    def crear_campo(
        self,
        parent,
        etiqueta,
        variable,
        columna
    ):

        frame = tk.Frame(
            parent,
            bg=SURFACE
        )

        frame.grid(
            row=0,
            column=columna,
            padx=8,
            sticky="ew"
        )

        parent.columnconfigure(
            columna,
            weight=1
        )

        tk.Label(
            frame,
            text=etiqueta,
            font=FONT_SMALL,
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack(
            anchor="w",
            pady=(0, 5)
        )

        ttk.Entry(
            frame,
            textvariable=variable
        ).pack(
            fill="x"
        )

    # ==========================================
    # TARJETA DE CONDICIÓN
    # ==========================================

    def crear_condicion(
        self,
        parent,
        codigo,
        descripcion,
        variable,
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

        parent.rowconfigure(
            fila,
            weight=1
        )

        contenido = tk.Frame(
            frame,
            bg=SURFACE_SOFT
        )

        contenido.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=12
        )

        # Código
        tk.Label(
            contenido,
            text=codigo,
            font=("Segoe UI", 16, "bold"),
            bg=SURFACE_SOFT,
            fg=PRIMARY
        ).pack(
            side="left",
            padx=(0, 12)
        )

        # Descripción
        texto = tk.Frame(
            contenido,
            bg=SURFACE_SOFT
        )

        texto.pack(
            side="left",
            fill="x",
            expand=True
        )

        tk.Label(
            texto,
            text=descripcion,
            font=FONT_BODY,
            bg=SURFACE_SOFT,
            fg=TEXT,
            anchor="w"
        ).pack(
            anchor="w"
        )

        estado = tk.Label(
            texto,
            text="ACTIVA" if variable.get() else "INACTIVA",
            font=("Segoe UI", 8, "bold"),
            bg=SURFACE_SOFT,
            fg=SUCCESS if variable.get() else TEXT_MUTED
        )

        estado.pack(
            anchor="w",
            pady=(3, 0)
        )

        # Checkbutton
        check = ttk.Checkbutton(
            contenido,
            variable=variable,
            command=lambda: self.actualizar_estado(
                variable,
                estado
            )
        )

        check.pack(
            side="right"
        )

    # ==========================================
    # ACTUALIZAR ESTADO
    # ==========================================

    def actualizar_estado(
        self,
        variable,
        etiqueta
    ):

        if variable.get():
            etiqueta.config(
                text="ACTIVA",
                fg=SUCCESS
            )
        else:
            etiqueta.config(
                text="INACTIVA",
                fg=TEXT_MUTED
            )

    # ==========================================
    # SCROLL
    # ==========================================

    def actualizar_scroll(self, event=None):

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def ajustar_ancho(self, event):

        self.canvas.itemconfig(
            self.window_id,
            width=event.width
        )

    def scroll_mouse(self, event):

        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    def scroll_arriba(self, event):

        self.canvas.yview_scroll(
            -1,
            "units"
        )

    def scroll_abajo(self, event):

        self.canvas.yview_scroll(
            1,
            "units"
        )

    # ==========================================
    # EVALUAR
    # ==========================================

    def evaluar(self):

        try:

            P = self.var_P.get()
            Q = self.var_Q.get()
            R = self.var_R.get()
            S = self.var_S.get()
            T = self.var_T.get()
            HR = self.var_HR.get()

            resultado = evaluar_camion(
                P,
                Q,
                R,
                S,
                guardar=True,
                operador="GUI"
            )

            certificacion = evaluar_certificacion(
                P,
                T,
                Q
            )

            horario = evaluar_horario_restringido(
                R,
                HR
            )

            A = resultado["acceso_estandar"]
            E = resultado["inspeccion_especial"]

            # --------------------------------------
            # DETERMINAR RESULTADO VISUAL
            # --------------------------------------

            if E:

                titulo = "⚠ INSPECCIÓN ESPECIAL"

                self.resultado_label.config(
                    text=titulo,
                    bg=WARNING_SOFT,
                    fg=WARNING
                )

            elif A and certificacion:

                titulo = "✓ ACCESO PERMITIDO"

                self.resultado_label.config(
                    text=titulo,
                    bg=SUCCESS_SOFT,
                    fg=SUCCESS
                )

            else:

                titulo = "✕ ACCESO NO PERMITIDO"

                self.resultado_label.config(
                    text=titulo,
                    bg=DANGER_SOFT,
                    fg=DANGER
                )

            # --------------------------------------
            # EXPLICACIÓN
            # --------------------------------------

            explicacion = (
                f"Premisas utilizadas:\n\n"
                f"P = {'Verdadero' if P else 'Falso'}\n"
                f"Q = {'Verdadero' if Q else 'Falso'}\n"
                f"R = {'Verdadero' if R else 'Falso'}\n"
                f"S = {'Verdadero' if S else 'Falso'}\n"
                f"T = {'Verdadero' if T else 'Falso'}\n"
                f"HR = {'Verdadero' if HR else 'Falso'}\n\n"
                f"Regla A = P ∧ S ∧ ¬Q → "
                f"{'Verdadero' if A else 'Falso'}\n"
                f"Regla E = P ∧ (R ∨ Q) → "
                f"{'Verdadero' if E else 'Falso'}\n"
                f"Regla C = P ∧ T ∧ ¬Q → "
                f"{'Verdadero' if certificacion else 'Falso'}\n"
                f"Regla H = R ∧ HR → "
                f"{'Verdadero' if horario else 'Falso'}"
            )

            self.explicacion_label.config(
                text=explicacion
            )

            # Volver a calcular scroll por si cambió contenido
            self.canvas.update_idletasks()

            self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )

        except Exception as error:

            messagebox.showerror(
                "Error en la evaluación",
                str(error)
            )