import customtkinter as ctk

from gui.theme import (
    APP_NAME,
    APP_SUBTITLE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
    COLOR_BACKGROUND,
    COLOR_SIDEBAR,
    COLOR_SIDEBAR_HOVER,
    COLOR_SIDEBAR_ACTIVE,
    COLOR_CARD,
    COLOR_BORDER,
    COLOR_TEXT,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_LIGHT,
    COLOR_SUCCESS,
    COLOR_INFO,
    COLOR_WARNING,
    COLOR_DANGER,
    configurar_apariencia,
)

from database.mongodb import MongoDB
from database.dashboard_repository import DashboardRepository


class LogiSmartApp(ctk.CTk):
    """Ventana principal de la aplicación LogiSmart."""

    def __init__(self):
        super().__init__()

        configurar_apariencia()

        self.title(f"{APP_NAME} | {APP_SUBTITLE}")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self.configure(fg_color=COLOR_BACKGROUND)

        # ----------------------------------------------------
        # CONEXIÓN CON MONGODB
        # ----------------------------------------------------

        self.mongodb = MongoDB()
        self.db = self.mongodb.conectar()

        if self.db is not None:
            self.dashboard_repository = DashboardRepository(self.db)
        else:
            self.dashboard_repository = None

        # ----------------------------------------------------
        # CREAR INTERFAZ
        # ----------------------------------------------------

        self.crear_interfaz()

        # Cargar datos reales
        self.cargar_dashboard()

        # ----------------------------------------------------
        # CERRAR MONGODB AL CERRAR LA APLICACIÓN
        # ----------------------------------------------------

        self.protocol(
            "WM_DELETE_WINDOW",
            self.cerrar_aplicacion
        )

    # ========================================================
    # INTERFAZ PRINCIPAL
    # ========================================================

    def crear_interfaz(self):

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ====================================================
        # BARRA LATERAL
        # ====================================================

        self.sidebar = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0,
            fg_color=COLOR_SIDEBAR
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(False)

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        logo_frame.pack(
            fill="x",
            padx=22,
            pady=(28, 35)
        )

        ctk.CTkLabel(
            logo_frame,
            text="LS",
            width=48,
            height=48,
            corner_radius=12,
            fg_color=COLOR_SIDEBAR_ACTIVE,
            text_color=COLOR_TEXT_LIGHT,
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        ).pack(side="left")

        logo_text = ctk.CTkFrame(
            logo_frame,
            fg_color="transparent"
        )

        logo_text.pack(
            side="left",
            padx=(12, 0)
        )

        ctk.CTkLabel(
            logo_text,
            text="LogiSmart",
            text_color=COLOR_TEXT_LIGHT,
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_text,
            text="CONTROL LOGÍSTICO",
            text_color="#AAB7C4",
            font=ctk.CTkFont(
                size=9,
                weight="bold"
            )
        ).pack(anchor="w")

        # ----------------------------------------------------
        # MENÚ
        # ----------------------------------------------------

        ctk.CTkLabel(
            self.sidebar,
            text="MENÚ PRINCIPAL",
            text_color="#82909D",
            font=ctk.CTkFont(
                size=10,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=24,
            pady=(0, 10)
        )

        self.botones_menu = []

        opciones = [
            ("▣", "Dashboard"),
            ("▤", "Control de acceso"),
            ("⊞", "Tabla de verdad"),
            ("✉", "Incidentes"),
            ("◉", "Asistente LLM"),
            ("⚠", "Riesgos éticos"),
            ("▥", "Reportes"),
            ("⚙", "Configuración"),
        ]

        for icono, texto in opciones:

            boton = ctk.CTkButton(
                self.sidebar,
                text=f"  {icono}    {texto}",
                anchor="w",
                height=44,
                corner_radius=8,
                fg_color=(
                    COLOR_SIDEBAR_ACTIVE
                    if texto == "Dashboard"
                    else "transparent"
                ),
                hover_color=COLOR_SIDEBAR_HOVER,
                text_color=COLOR_TEXT_LIGHT,
                font=ctk.CTkFont(
                    size=13
                ),
                command=lambda nombre=texto:
                self.seleccionar_modulo(nombre)
            )

            boton.pack(
                fill="x",
                padx=14,
                pady=3
            )

            self.botones_menu.append(
                (texto, boton)
            )

        # ----------------------------------------------------
        # ESPACIO
        # ----------------------------------------------------

        ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        ).pack(
            expand=True,
            fill="both"
        )

        # ----------------------------------------------------
        # OPERADOR
        # ----------------------------------------------------

        operador_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=COLOR_SIDEBAR_HOVER,
            corner_radius=10
        )

        operador_frame.pack(
            fill="x",
            padx=14,
            pady=18
        )

        ctk.CTkLabel(
            operador_frame,
            text="A",
            width=36,
            height=36,
            corner_radius=18,
            fg_color=COLOR_SIDEBAR_ACTIVE,
            text_color=COLOR_TEXT_LIGHT,
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        ).pack(
            side="left",
            padx=10,
            pady=10
        )

        operador_texto = ctk.CTkFrame(
            operador_frame,
            fg_color="transparent"
        )

        operador_texto.pack(
            side="left",
            pady=8
        )

        ctk.CTkLabel(
            operador_texto,
            text="Operador",
            text_color="#AAB7C4",
            font=ctk.CTkFont(
                size=10
            )
        ).pack(anchor="w")

        ctk.CTkLabel(
            operador_texto,
            text="Administrador",
            text_color=COLOR_TEXT_LIGHT,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            )
        ).pack(anchor="w")

        # ====================================================
        # ÁREA PRINCIPAL
        # ====================================================

        self.main = ctk.CTkFrame(
            self,
            fg_color=COLOR_BACKGROUND,
            corner_radius=0
        )

        self.main.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.main.grid_columnconfigure(
            0,
            weight=1
        )

        self.main.grid_rowconfigure(
            1,
            weight=1
        )

        # ----------------------------------------------------
        # ENCABEZADO
        # ----------------------------------------------------

        self.header = ctk.CTkFrame(
            self.main,
            height=80,
            fg_color=COLOR_CARD,
            corner_radius=0,
            border_width=1,
            border_color=COLOR_BORDER
        )

        self.header.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        self.header.grid_columnconfigure(
            0,
            weight=1
        )

        self.titulo_header = ctk.CTkLabel(
            self.header,
            text="Dashboard",
            text_color=COLOR_TEXT,
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        self.titulo_header.grid(
            row=0,
            column=0,
            sticky="w",
            padx=28,
            pady=(15, 0)
        )

        self.subtitulo_header = ctk.CTkLabel(
            self.header,
            text="Vista general del sistema",
            text_color=COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont(
                size=12
            )
        )

        self.subtitulo_header.grid(
            row=1,
            column=0,
            sticky="w",
            padx=28,
            pady=(0, 15)
        )

        self.estado_frame = ctk.CTkFrame(
            self.header,
            fg_color="#EAF7EF",
            corner_radius=18
        )

        self.estado_frame.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=28
        )

        ctk.CTkLabel(
            self.estado_frame,
            text="●  MongoDB conectado",
            text_color=COLOR_SUCCESS,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            )
        ).pack(
            padx=15,
            pady=9
        )

        # ====================================================
        # CONTENIDO
        # ====================================================

        self.contenido = ctk.CTkFrame(
            self.main,
            fg_color=COLOR_BACKGROUND,
            corner_radius=0
        )

        self.contenido.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=28,
            pady=28
        )

        self.contenido.grid_columnconfigure(
            0,
            weight=1
        )

        self.contenido.grid_columnconfigure(
            1,
            weight=1
        )

        self.contenido.grid_columnconfigure(
            2,
            weight=1
        )

    # ========================================================
    # DASHBOARD
    # ========================================================

    def cargar_dashboard(self):

        for widget in self.contenido.winfo_children():
            widget.destroy()

        if self.dashboard_repository is None:

            self.mostrar_error(
                "No fue posible conectar con MongoDB."
            )

            return

        try:

            indicadores = (
                self.dashboard_repository
                .obtener_indicadores()
            )

        except Exception as error:

            self.mostrar_error(
                f"Error al obtener indicadores:\n{error}"
            )

            return

        datos = [
            (
                "Camiones atendidos",
                indicadores["camiones_atendidos"],
                "Total registrados",
                COLOR_INFO
            ),
            (
                "Incidentes abiertos",
                indicadores["incidentes_abiertos"],
                "Requieren atención",
                COLOR_WARNING
            ),
            (
                "Riesgos críticos",
                indicadores["riesgos_criticos"],
                "Revisión prioritaria",
                COLOR_DANGER
            ),
        ]

        # ----------------------------------------------------
        # TARJETAS
        # ----------------------------------------------------

        for columna, (
            titulo,
            valor,
            detalle,
            color
        ) in enumerate(datos):

            tarjeta = ctk.CTkFrame(
                self.contenido,
                fg_color=COLOR_CARD,
                corner_radius=12,
                border_width=1,
                border_color=COLOR_BORDER
            )

            tarjeta.grid(
                row=0,
                column=columna,
                sticky="nsew",
                padx=7
            )

            ctk.CTkLabel(
                tarjeta,
                text=titulo,
                text_color=COLOR_TEXT_SECONDARY,
                font=ctk.CTkFont(
                    size=12
                )
            ).pack(
                anchor="w",
                padx=20,
                pady=(18, 3)
            )

            ctk.CTkLabel(
                tarjeta,
                text=str(valor),
                text_color=COLOR_TEXT,
                font=ctk.CTkFont(
                    size=30,
                    weight="bold"
                )
            ).pack(
                anchor="w",
                padx=20
            )

            ctk.CTkLabel(
                tarjeta,
                text=detalle,
                text_color=color,
                font=ctk.CTkFont(
                    size=11,
                    weight="bold"
                )
            ).pack(
                anchor="w",
                padx=20,
                pady=(3, 18)
            )

        # ----------------------------------------------------
        # INFORMACIÓN
        # ----------------------------------------------------

        panel = ctk.CTkFrame(
            self.contenido,
            fg_color=COLOR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER
        )

        panel.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="nsew",
            padx=7,
            pady=(20, 0)
        )

        ctk.CTkLabel(
            panel,
            text="Resumen del sistema",
            text_color=COLOR_TEXT,
            font=ctk.CTkFont(
                size=21,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 5)
        )

        ctk.CTkLabel(
            panel,
            text=(
                "Los indicadores mostrados se consultan "
                "directamente desde la base de datos MongoDB."
            ),
            text_color=COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont(
                size=13
            )
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 20)
        )

        # ----------------------------------------------------
        # ESTADO DE SERVICIOS
        # ----------------------------------------------------

        servicios = ctk.CTkFrame(
            panel,
            fg_color="#F8FAFC",
            corner_radius=10
        )

        servicios.pack(
            fill="x",
            padx=25,
            pady=(0, 25)
        )

        lista_servicios = [
            ("MongoDB", "Persistencia de datos", True),
            ("Motor de reglas", "Lógica proposicional", True),
            ("Ollama", "Modelo LLM local", True),
        ]

        for fila, (
            nombre,
            descripcion,
            activo
        ) in enumerate(lista_servicios):

            estado = "●" if activo else "●"

            ctk.CTkLabel(
                servicios,
                text=estado,
                text_color=COLOR_SUCCESS,
                font=ctk.CTkFont(
                    size=15
                )
            ).grid(
                row=fila,
                column=0,
                padx=(18, 8),
                pady=9
            )

            ctk.CTkLabel(
                servicios,
                text=nombre,
                text_color=COLOR_TEXT,
                font=ctk.CTkFont(
                    size=12,
                    weight="bold"
                )
            ).grid(
                row=fila,
                column=1,
                sticky="w",
                pady=9
            )

            ctk.CTkLabel(
                servicios,
                text=descripcion,
                text_color=COLOR_TEXT_SECONDARY,
                font=ctk.CTkFont(
                    size=11
                )
            ).grid(
                row=fila,
                column=2,
                padx=20,
                pady=9
            )

        # ----------------------------------------------------
        # EVALUACIONES LLM
        # ----------------------------------------------------

        evaluaciones = indicadores["evaluaciones_llm"]

        ctk.CTkLabel(
            panel,
            text=f"Evaluaciones realizadas por Ollama: {evaluaciones}",
            text_color=COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            )
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 20)
        )

    # ========================================================
    # NAVEGACIÓN
    # ========================================================

    def seleccionar_modulo(self, nombre):

        self.titulo_header.configure(
            text=nombre
        )

        self.subtitulo_header.configure(
            text=f"Módulo: {nombre}"
        )

        for texto, boton in self.botones_menu:

            if texto == nombre:

                boton.configure(
                    fg_color=COLOR_SIDEBAR_ACTIVE
                )

            else:

                boton.configure(
                    fg_color="transparent"
                )

        if nombre == "Dashboard":

            self.cargar_dashboard()

        else:

            self.mostrar_modulo_pendiente(nombre)

    # ========================================================
    # MÓDULOS TEMPORALES
    # ========================================================

    def mostrar_modulo_pendiente(self, nombre):

        for widget in self.contenido.winfo_children():
            widget.destroy()

        panel = ctk.CTkFrame(
            self.contenido,
            fg_color=COLOR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=7,
            pady=7
        )

        ctk.CTkLabel(
            panel,
            text=nombre,
            text_color=COLOR_TEXT,
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            )
        ).pack(
            pady=(100, 10)
        )

        ctk.CTkLabel(
            panel,
            text="Módulo preparado para integrar.",
            text_color=COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont(
                size=14
            )
        ).pack()

    # ========================================================
    # ERROR
    # ========================================================

    def mostrar_error(self, mensaje):

        panel = ctk.CTkFrame(
            self.contenido,
            fg_color=COLOR_CARD,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_BORDER
        )

        panel.pack(
            fill="both",
            expand=True,
            padx=7,
            pady=7
        )

        ctk.CTkLabel(
            panel,
            text="Error",
            text_color=COLOR_DANGER,
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        ).pack(
            pady=(100, 15)
        )

        ctk.CTkLabel(
            panel,
            text=mensaje,
            text_color=COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont(
                size=13
            ),
            justify="center"
        ).pack()

    # ========================================================
    # CERRAR APLICACIÓN
    # ========================================================

    def cerrar_aplicacion(self):

        if self.mongodb is not None:

            self.mongodb.cerrar()

        self.destroy()


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":

    app = LogiSmartApp()

    app.mainloop()