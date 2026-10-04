import tkinter as tk
from tkinter import messagebox

from database.mongodb import MongoDB
from database.riesgos_repository import RiesgosRepository

from gui.theme import (
    BG,
    SURFACE,
    SURFACE_SOFT,
    TEXT,
    TEXT_SECONDARY,
    PRIMARY,
    DANGER,
    WARNING,
    SUCCESS,
    BORDER,
    FONT_TITLE,
    FONT_SUBTITLE,
    FONT_BODY,
    FONT_SMALL,
)


class RiesgosView(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=BG)

        self.mongo = MongoDB()
        self.db = None
        self.repository = None

        self.crear_interfaz()
        self.cargar_riesgos()

    # =========================================================
    # INTERFAZ
    # =========================================================

    def crear_interfaz(self):

        encabezado = tk.Frame(
            self,
            bg=BG
        )
        encabezado.pack(
            fill="x",
            padx=30,
            pady=(25, 10)
        )

        tk.Label(
            encabezado,
            text="Riesgos éticos",
            font=FONT_TITLE,
            bg=BG,
            fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            encabezado,
            text="Identificación y gestión de riesgos asociados al uso de Inteligencia Artificial.",
            font=FONT_SUBTITLE,
            bg=BG,
            fg=TEXT_SECONDARY
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        # -----------------------------------------------------
        # RESUMEN
        # -----------------------------------------------------

        resumen = tk.Frame(
            self,
            bg=BG
        )
        resumen.pack(
            fill="x",
            padx=30,
            pady=10
        )

        self.crear_tarjeta_resumen(
            resumen,
            "Riesgos registrados",
            "0",
            0
        )

        self.crear_tarjeta_resumen(
            resumen,
            "Riesgos críticos",
            "0",
            1
        )

        self.crear_tarjeta_resumen(
            resumen,
            "Riesgos mitigados",
            "0",
            2
        )

        # -----------------------------------------------------
        # CONTENEDOR PRINCIPAL
        # -----------------------------------------------------

        contenedor = tk.Frame(
            self,
            bg=BG
        )
        contenedor.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(5, 25)
        )

        # Scroll
        self.canvas = tk.Canvas(
            contenedor,
            bg=BG,
            highlightthickness=0
        )

        scrollbar = tk.Scrollbar(
            contenedor,
            orient="vertical",
            command=self.canvas.yview
        )

        self.lista = tk.Frame(
            self.canvas,
            bg=BG
        )

        self.lista.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window(
            (0, 0),
            window=self.lista,
            anchor="nw"
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    # =========================================================
    # TARJETAS RESUMEN
    # =========================================================

    def crear_tarjeta_resumen(
        self,
        parent,
        titulo,
        valor,
        columna
    ):

        tarjeta = tk.Frame(
            parent,
            bg=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        tarjeta.grid(
            row=0,
            column=columna,
            sticky="nsew",
            padx=5
        )

        parent.grid_columnconfigure(
            columna,
            weight=1
        )

        tk.Label(
            tarjeta,
            text=titulo,
            font=FONT_SMALL,
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=18,
            pady=(15, 3)
        )

        etiqueta = tk.Label(
            tarjeta,
            text=valor,
            font=("Segoe UI", 22, "bold"),
            bg=SURFACE,
            fg=PRIMARY
        )

        etiqueta.pack(
            anchor="w",
            padx=18,
            pady=(0, 15)
        )

        if titulo == "Riesgos registrados":
            self.lbl_total = etiqueta

        elif titulo == "Riesgos críticos":
            self.lbl_criticos = etiqueta

        elif titulo == "Riesgos mitigados":
            self.lbl_mitigados = etiqueta

    # =========================================================
    # CONEXIÓN
    # =========================================================

    def conectar(self):

        try:

            self.db = self.mongo.conectar()

            if self.db is None:
                messagebox.showerror(
                    "Error de conexión",
                    "No fue posible conectar con MongoDB."
                )
                return False

            self.repository = RiesgosRepository(
                self.db
            )

            return True

        except Exception as error:

            messagebox.showerror(
                "Error",
                f"No fue posible acceder a los riesgos.\n\n{error}"
            )

            return False

    # =========================================================
    # CARGAR RIESGOS
    # =========================================================

    def cargar_riesgos(self):

        if not self.conectar():
            self.mostrar_riesgos_base()
            return

        try:

            riesgos = self.repository.obtener_todos()

            self.mostrar_riesgos(
                riesgos
            )

        except Exception as error:

            print(
                "Error al cargar riesgos:",
                error
            )

            self.mostrar_riesgos_base()

    # =========================================================
    # MOSTRAR RIESGOS
    # =========================================================

    def mostrar_riesgos(
        self,
        riesgos
    ):

        for widget in self.lista.winfo_children():
            widget.destroy()

        if not riesgos:

            self.mostrar_riesgos_base()

            return

        total = len(riesgos)
        criticos = 0
        mitigados = 0

        for riesgo in riesgos:

            impacto = str(
                riesgo.get(
                    "impacto",
                    ""
                )
            ).lower()

            estado = str(
                riesgo.get(
                    "estado",
                    ""
                )
            ).lower()

            if impacto in (
                "alto",
                "crítico",
                "critico"
            ):
                criticos += 1

            if estado in (
                "mitigado",
                "controlado"
            ):
                mitigados += 1

            self.crear_tarjeta_riesgo(
                riesgo
            )

        self.lbl_total.config(
            text=str(total)
        )

        self.lbl_criticos.config(
            text=str(criticos)
        )

        self.lbl_mitigados.config(
            text=str(mitigados)
        )

    # =========================================================
    # RIESGOS BASE
    # =========================================================

    def mostrar_riesgos_base(self):

        riesgos = [

            {
                "modulo": "Asistente LLM",
                "descripcion": "El modelo puede generar información incorrecta o inventada.",
                "categoria": "Alucinación",
                "probabilidad": "Media",
                "impacto": "Alto",
                "mitigacion": "Validar las respuestas contra información almacenada en MongoDB y solicitar revisión humana cuando exista discrepancia.",
                "estado": "Mitigado"
            },

            {
                "modulo": "Clasificador de correos",
                "descripcion": "El sistema puede clasificar incorrectamente mensajes debido a errores de escritura o diferentes formas de expresar una situación.",
                "categoria": "Sesgo de clasificación",
                "probabilidad": "Media",
                "impacto": "Medio",
                "mitigacion": "Combinar reglas deterministas con LLM y permitir revisión humana.",
                "estado": "Mitigado"
            },

            {
                "modulo": "Información de conductores",
                "descripcion": "El sistema procesa información relacionada con operadores y actividades logísticas.",
                "categoria": "Privacidad",
                "probabilidad": "Media",
                "impacto": "Alto",
                "mitigacion": "Aplicar controles de acceso y almacenar únicamente la información necesaria.",
                "estado": "Mitigado"
            },

            {
                "modulo": "Automatización",
                "descripcion": "Los usuarios pueden depender demasiado de las decisiones generadas automáticamente por el sistema.",
                "categoria": "Sobredependencia",
                "probabilidad": "Media",
                "impacto": "Alto",
                "mitigacion": "Mantener intervención humana en decisiones críticas y mostrar claramente cuándo una decisión requiere revisión.",
                "estado": "Mitigado"
            }
        ]

        self.mostrar_riesgos(
            riesgos
        )

    # =========================================================
    # TARJETA DE RIESGO
    # =========================================================

    def crear_tarjeta_riesgo(
        self,
        riesgo
    ):

        tarjeta = tk.Frame(
            self.lista,
            bg=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        tarjeta.pack(
            fill="x",
            pady=7
        )

        contenido = tk.Frame(
            tarjeta,
            bg=SURFACE
        )

        contenido.pack(
            fill="x",
            padx=20,
            pady=18
        )

        # -----------------------------------------------------
        # ENCABEZADO
        # -----------------------------------------------------

        fila_titulo = tk.Frame(
            contenido,
            bg=SURFACE
        )

        fila_titulo.pack(
            fill="x"
        )

        categoria = riesgo.get(
            "categoria",
            "Sin categoría"
        )

        modulo = riesgo.get(
            "modulo",
            "Sin módulo"
        )

        tk.Label(
            fila_titulo,
            text=categoria,
            font=("Segoe UI", 14, "bold"),
            bg=SURFACE,
            fg=TEXT
        ).pack(
            side="left"
        )

        tk.Label(
            fila_titulo,
            text=modulo,
            font=FONT_SMALL,
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack(
            side="right"
        )

        # -----------------------------------------------------
        # DESCRIPCIÓN
        # -----------------------------------------------------

        tk.Label(
            contenido,
            text=riesgo.get(
                "descripcion",
                "Sin descripción"
            ),
            font=FONT_BODY,
            bg=SURFACE,
            fg=TEXT_SECONDARY,
            justify="left",
            wraplength=850
        ).pack(
            fill="x",
            anchor="w",
            pady=(10, 15)
        )

        # -----------------------------------------------------
        # DATOS
        # -----------------------------------------------------

        datos = tk.Frame(
            contenido,
            bg=SURFACE
        )

        datos.pack(
            fill="x"
        )

        self.crear_dato(
            datos,
            "Probabilidad",
            riesgo.get(
                "probabilidad",
                "No definida"
            ),
            0
        )

        self.crear_dato(
            datos,
            "Impacto",
            riesgo.get(
                "impacto",
                "No definido"
            ),
            1
        )

        self.crear_dato(
            datos,
            "Estado",
            riesgo.get(
                "estado",
                "No definido"
            ),
            2
        )

        # -----------------------------------------------------
        # MITIGACIÓN
        # -----------------------------------------------------

        mitigacion_frame = tk.Frame(
            contenido,
            bg=SURFACE_SOFT
        )

        mitigacion_frame.pack(
            fill="x",
            pady=(15, 0)
        )

        tk.Label(
            mitigacion_frame,
            text="MITIGACIÓN",
            font=("Segoe UI", 9, "bold"),
            bg=SURFACE_SOFT,
            fg=PRIMARY
        ).pack(
            anchor="w",
            padx=12,
            pady=(10, 2)
        )

        tk.Label(
            mitigacion_frame,
            text=riesgo.get(
                "mitigacion",
                "No definida"
            ),
            font=FONT_SMALL,
            bg=SURFACE_SOFT,
            fg=TEXT,
            justify="left",
            wraplength=800
        ).pack(
            anchor="w",
            padx=12,
            pady=(0, 10)
        )

    # =========================================================
    # DATO
    # =========================================================

    def crear_dato(
        self,
        parent,
        titulo,
        valor,
        columna
    ):

        bloque = tk.Frame(
            parent,
            bg=SURFACE
        )

        bloque.grid(
            row=0,
            column=columna,
            sticky="w",
            padx=(0, 35)
        )

        tk.Label(
            bloque,
            text=titulo,
            font=FONT_SMALL,
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack(
            anchor="w"
        )

        valor_label = tk.Label(
            bloque,
            text=valor,
            font=("Segoe UI", 10, "bold"),
            bg=SURFACE,
            fg=self.color_valor(
                titulo,
                valor
            )
        )

        valor_label.pack(
            anchor="w",
            pady=(2, 0)
        )

    # =========================================================
    # COLOR
    # =========================================================

    def color_valor(
        self,
        titulo,
        valor
    ):

        valor = str(valor).lower()

        if titulo == "Impacto":

            if valor in (
                "alto",
                "crítico",
                "critico"
            ):
                return DANGER

            if valor == "medio":
                return WARNING

            return SUCCESS

        if titulo == "Estado":

            if valor in (
                "mitigado",
                "controlado"
            ):
                return SUCCESS

        return TEXT

    # =========================================================
    # CERRAR
    # =========================================================

    def destruir(self):

        try:
            self.mongo.cerrar()
        except Exception:
            pass

        self.destroy()