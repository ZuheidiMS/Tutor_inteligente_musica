import tkinter as tk
from tkinter import messagebox

from database.mongodb import MongoDB
from database.dashboard_repository import DashboardRepository

from gui.theme import (
    BG,
    SURFACE,
    SURFACE_SOFT,
    TEXT,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BORDER,
    PRIMARY,
    PRIMARY_SOFT,
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
    FONT_NUMBER,
    tarjeta,
    badge,
    encabezado,
    separador,
)


class DashboardView(tk.Frame):

    def __init__(self, parent):
        super().__init__(
            parent,
            bg=BG
        )

        self.db_manager = None
        self.db = None

        self.crear_interfaz()
        self.cargar_datos()

    # ============================================================
    # INTERFAZ
    # ============================================================

    def crear_interfaz(self):

        # --------------------------------------------------------
        # CONTENEDOR SCROLL
        # --------------------------------------------------------

        canvas = tk.Canvas(
            self,
            bg=BG,
            highlightthickness=0
        )

        scrollbar = tk.Scrollbar(
            self,
            orient="vertical",
            command=canvas.yview
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.contenido = tk.Frame(
            canvas,
            bg=BG
        )

        ventana = canvas.create_window(
            (0, 0),
            window=self.contenido,
            anchor="nw"
        )

        def actualizar_scroll(event):
            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        def ajustar_ancho(event):
            canvas.itemconfig(
                ventana,
                width=event.width
            )

        self.contenido.bind(
            "<Configure>",
            actualizar_scroll
        )

        canvas.bind(
            "<Configure>",
            ajustar_ancho
        )

        # --------------------------------------------------------
        # ENCABEZADO
        # --------------------------------------------------------

        encabezado(
            self.contenido,
            "Dashboard",
            "Resumen operativo del sistema inteligente de logística"
        )

        # --------------------------------------------------------
        # ESTADO GENERAL
        # --------------------------------------------------------

        estado = tk.Frame(
            self.contenido,
            bg=BG
        )

        estado.pack(
            fill="x",
            padx=32,
            pady=(0, 20)
        )

        indicador = tk.Frame(
            estado,
            bg=SUCCESS_SOFT,
            highlightthickness=1,
            highlightbackground="#DCFCE7"
        )

        indicador.pack(
            side="left"
        )

        tk.Label(
            indicador,
            text="●",
            font=("Segoe UI", 14),
            bg=SUCCESS_SOFT,
            fg=SUCCESS
        ).pack(
            side="left",
            padx=(12, 5),
            pady=8
        )

        tk.Label(
            indicador,
            text="Todos los servicios operativos",
            font=("Segoe UI", 9, "bold"),
            bg=SUCCESS_SOFT,
            fg=SUCCESS
        ).pack(
            side="left",
            padx=(0, 12),
            pady=8
        )

        # --------------------------------------------------------
        # TARJETAS KPI
        # --------------------------------------------------------

        self.cards_frame = tk.Frame(
            self.contenido,
            bg=BG
        )

        self.cards_frame.pack(
            fill="x",
            padx=32,
            pady=(0, 25)
        )

        self.card_camiones = self.crear_kpi(
            self.cards_frame,
            "Camiones atendidos",
            "—",
            "Vehículos registrados",
            "🚛"
        )

        self.card_incidentes = self.crear_kpi(
            self.cards_frame,
            "Incidentes abiertos",
            "—",
            "Casos pendientes",
            "⚠"
        )

        self.card_riesgos = self.crear_kpi(
            self.cards_frame,
            "Riesgos críticos",
            "—",
            "Requieren atención",
            "◆"
        )

        self.card_evaluaciones = self.crear_kpi(
            self.cards_frame,
            "Evaluaciones LLM",
            "—",
            "Procesamientos realizados",
            "✦"
        )

        # --------------------------------------------------------
        # SEGUNDA FILA
        # --------------------------------------------------------

        segunda_fila = tk.Frame(
            self.contenido,
            bg=BG
        )

        segunda_fila.pack(
            fill="both",
            expand=True,
            padx=32,
            pady=(0, 25)
        )

        # --------------------------------------------------------
        # ACTIVIDAD POR CATEGORÍA
        # --------------------------------------------------------

        panel_categorias = tarjeta(
            segunda_fila
        )

        panel_categorias.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        tk.Label(
            panel_categorias,
            text="Incidentes por categoría",
            font=FONT_SECTION,
            bg=SURFACE,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=22,
            pady=(20, 3)
        )

        tk.Label(
            panel_categorias,
            text="Distribución de los incidentes registrados",
            font=("Segoe UI", 9),
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=22,
            pady=(0, 15)
        )

        separador(
            panel_categorias
        ).pack(
            fill="x"
        )

        self.categorias_contenedor = tk.Frame(
            panel_categorias,
            bg=SURFACE
        )

        self.categorias_contenedor.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=15
        )

        # --------------------------------------------------------
        # ESTADO DE SERVICIOS
        # --------------------------------------------------------

        panel_servicios = tarjeta(
            segunda_fila
        )

        panel_servicios.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0)
        )

        tk.Label(
            panel_servicios,
            text="Estado de servicios",
            font=FONT_SECTION,
            bg=SURFACE,
            fg=TEXT
        ).pack(
            anchor="w",
            padx=22,
            pady=(20, 3)
        )

        tk.Label(
            panel_servicios,
            text="Componentes principales de LogiSmart",
            font=("Segoe UI", 9),
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=22,
            pady=(0, 15)
        )

        separador(
            panel_servicios
        ).pack(
            fill="x"
        )

        servicios = [
            ("MongoDB", "Persistencia de datos", SUCCESS),
            ("Motor de reglas", "Inferencia lógica", SUCCESS),
            ("Ollama", "Modelo LLM local", SUCCESS),
            ("Clasificador híbrido", "Reglas + IA", SUCCESS),
        ]

        for nombre, descripcion, color in servicios:

            fila = tk.Frame(
                panel_servicios,
                bg=SURFACE
            )

            fila.pack(
                fill="x",
                padx=22,
                pady=10
            )

            tk.Label(
                fila,
                text="●",
                font=("Segoe UI", 12),
                bg=SURFACE,
                fg=color
            ).pack(
                side="left",
                padx=(0, 10)
            )

            textos = tk.Frame(
                fila,
                bg=SURFACE
            )

            textos.pack(
                side="left",
                fill="x",
                expand=True
            )

            tk.Label(
                textos,
                text=nombre,
                font=("Segoe UI", 10, "bold"),
                bg=SURFACE,
                fg=TEXT
            ).pack(
                anchor="w"
            )

            tk.Label(
                textos,
                text=descripcion,
                font=("Segoe UI", 8),
                bg=SURFACE,
                fg=TEXT_SECONDARY
            ).pack(
                anchor="w"
            )

            badge(
                fila,
                "OPERATIVO",
                "success"
            ).pack(
                side="right"
            )

        # --------------------------------------------------------
        # INFORMACIÓN DEL SISTEMA
        # --------------------------------------------------------

        info = tk.Frame(
            self.contenido,
            bg=SURFACE,
            highlightthickness=1,
            highlightbackground=BORDER
        )

        info.pack(
            fill="x",
            padx=32,
            pady=(0, 35)
        )

        tk.Label(
            info,
            text="LogiSmart",
            font=("Segoe UI", 11, "bold"),
            bg=SURFACE,
            fg=TEXT
        ).pack(
            side="left",
            padx=22,
            pady=14
        )

        tk.Label(
            info,
            text="Sistema de apoyo a decisiones logísticas mediante reglas, MongoDB e inteligencia artificial.",
            font=("Segoe UI", 9),
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack(
            side="left",
            pady=14
        )

        tk.Label(
            info,
            text="v1.0",
            font=("Segoe UI", 9, "bold"),
            bg=SURFACE,
            fg=TEXT_MUTED
        ).pack(
            side="right",
            padx=22
        )

    # ============================================================
    # TARJETA KPI
    # ============================================================

    def crear_kpi(
        self,
        parent,
        titulo,
        numero,
        descripcion,
        icono
    ):

        card = tarjeta(
            parent
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        # Icono
        icono_frame = tk.Frame(
            card,
            bg=PRIMARY_SOFT,
            width=46,
            height=46
        )

        icono_frame.pack(
            anchor="w",
            padx=18,
            pady=(18, 12)
        )

        icono_frame.pack_propagate(False)

        tk.Label(
            icono_frame,
            text=icono,
            font=("Segoe UI", 17),
            bg=PRIMARY_SOFT,
            fg=PRIMARY
        ).pack(
            expand=True
        )

        # Título
        tk.Label(
            card,
            text=titulo,
            font=("Segoe UI", 9, "bold"),
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack(
            anchor="w",
            padx=18
        )

        # Número
        numero_label = tk.Label(
            card,
            text=numero,
            font=FONT_NUMBER,
            bg=SURFACE,
            fg=TEXT
        )

        numero_label.pack(
            anchor="w",
            padx=18,
            pady=(3, 0)
        )

        # Descripción
        tk.Label(
            card,
            text=descripcion,
            font=("Segoe UI", 8),
            bg=SURFACE,
            fg=TEXT_MUTED
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 18)
        )

        return numero_label

    # ============================================================
    # CARGAR DATOS
    # ============================================================

    def cargar_datos(self):

        try:

            self.db_manager = MongoDB()

            self.db = self.db_manager.conectar()

            if self.db is None:

                self.mostrar_error_conexion()

                return

            repository = DashboardRepository(
                self.db
            )

            indicadores = repository.obtener_indicadores()

            # ----------------------------------------------------
            # KPI
            # ----------------------------------------------------

            self.card_camiones.config(
                text=str(
                    indicadores.get(
                        "camiones_atendidos",
                        0
                    )
                )
            )

            self.card_incidentes.config(
                text=str(
                    indicadores.get(
                        "incidentes_abiertos",
                        0
                    )
                )

            )

            self.card_riesgos.config(
                text=str(
                    indicadores.get(
                        "riesgos_criticos",
                        0
                    )
                )

            )

            self.card_evaluaciones.config(
                text=str(
                    indicadores.get(
                        "evaluaciones_llm",
                        0
                    )
                )

            )

            # ----------------------------------------------------
            # CATEGORÍAS
            # ----------------------------------------------------

            categorias = repository.incidentes_por_categoria()

            self.mostrar_categorias(
                categorias
            )

        except Exception as error:

            self.mostrar_error(
                str(error)
            )

        finally:

            if self.db_manager:

                self.db_manager.cerrar()

                self.db_manager = None
                self.db = None

    # ============================================================
    # CATEGORÍAS
    # ============================================================

    def mostrar_categorias(
        self,
        categorias
    ):

        for widget in self.categorias_contenedor.winfo_children():
            widget.destroy()

        if not categorias:

            tk.Label(
                self.categorias_contenedor,
                text="No existen incidentes registrados.",
                font=("Segoe UI", 10),
                bg=SURFACE,
                fg=TEXT_MUTED
            ).pack(
                pady=30
            )

            return

        maximo = max(
            item.get("total", 0)
            for item in categorias
        )

        for item in categorias:

            categoria = item.get(
                "_id",
                "Sin categoría"
            )

            total = item.get(
                "total",
                0
            )

            fila = tk.Frame(
                self.categorias_contenedor,
                bg=SURFACE
            )

            fila.pack(
                fill="x",
                pady=8
            )

            nombre = tk.Label(
                fila,
                text=categoria.replace(
                    "_",
                    " "
                ).title(),
                font=("Segoe UI", 9, "bold"),
                bg=SURFACE,
                fg=TEXT
            )

            nombre.pack(
                side="left"
            )

            cantidad = tk.Label(
                fila,
                text=str(total),
                font=("Segoe UI", 9, "bold"),
                bg=SURFACE,
                fg=PRIMARY
            )

            cantidad.pack(
                side="right"
            )

            barra_fondo = tk.Frame(
                fila,
                bg="#E2E8F0",
                height=7
            )

            barra_fondo.pack(
                fill="x",
                pady=(7, 0)
            )

            if maximo > 0:

                porcentaje = total / maximo

                barra = tk.Frame(
                    barra_fondo,
                    bg=PRIMARY,
                    height=7
                )

                barra.place(
                    relwidth=porcentaje,
                    relheight=1
                )

    # ============================================================
    # ERRORES
    # ============================================================

    def mostrar_error_conexion(self):

        for widget in self.categorias_contenedor.winfo_children():
            widget.destroy()

        tk.Label(
            self.categorias_contenedor,
            text="MongoDB no está disponible.",
            font=("Segoe UI", 11, "bold"),
            bg=SURFACE,
            fg=DANGER
        ).pack(
            pady=(30, 5)
        )

        tk.Label(
            self.categorias_contenedor,
            text="Verifica que el servicio de MongoDB esté ejecutándose.",
            font=("Segoe UI", 9),
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack()

    def mostrar_error(self, mensaje):

        messagebox.showerror(
            "Error del Dashboard",
            f"No fue posible cargar los indicadores.\n\n{mensaje}"
        )

    # ============================================================
    # CIERRE
    # ============================================================

    def destroy(self):

        if self.db_manager:

            self.db_manager.cerrar()

            self.db_manager = None

        super().destroy()