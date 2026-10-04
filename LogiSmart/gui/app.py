import tkinter as tk

from gui.theme import (
    BG,
    SURFACE,
    SIDEBAR,
    SIDEBAR_HOVER,
    SIDEBAR_ACTIVE,
    TEXT_MUTED,
    TEXT_SECONDARY,
    TEXT,
    PRIMARY,
    configurar_tema
)

from gui.views.dashboard_view import DashboardView
from gui.views.acceso_view import AccesoView
from gui.views.verdad_view import VerdadView
from gui.views.incidentes_view import IncidentesView
from gui.views.asistente_view import AsistenteView
from gui.views.riesgos_view import RiesgosView
from gui.views.reportes_view import ReportesView
from gui.views.configuracion_view import ConfiguracionView


class LogiSmartApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("LogiSmart | Centro de Control Inteligente")
        self.geometry("1400x850")
        self.minsize(1150, 720)

        self.configure(bg=BG)

        configurar_tema(self)

        self.contenedor = None
        self.boton_activo = None

        self.crear_interfaz()

        self.mostrar_dashboard()

    # ============================================================
    # INTERFAZ PRINCIPAL
    # ============================================================

    def crear_interfaz(self):

        sidebar = tk.Frame(
            self,
            bg=SIDEBAR,
            width=245
        )

        sidebar.pack(
            side="left",
            fill="y"
        )

        sidebar.pack_propagate(False)

        # --------------------------------------------------------
        # LOGO
        # --------------------------------------------------------

        logo = tk.Frame(
            sidebar,
            bg=SIDEBAR
        )

        logo.pack(
            fill="x",
            padx=22,
            pady=(25, 30)
        )

        tk.Label(
            logo,
            text="L",
            font=("Segoe UI", 18, "bold"),
            bg=PRIMARY,
            fg="white",
            width=2,
            height=1
        ).pack(
            side="left",
            padx=(0, 10)
        )

        textos_logo = tk.Frame(
            logo,
            bg=SIDEBAR
        )

        textos_logo.pack(
            side="left"
        )

        tk.Label(
            textos_logo,
            text="LogiSmart",
            font=("Segoe UI", 16, "bold"),
            bg=SIDEBAR,
            fg="white"
        ).pack(
            anchor="w"
        )

        tk.Label(
            textos_logo,
            text="CONTROL LOGÍSTICO",
            font=("Segoe UI", 7, "bold"),
            bg=SIDEBAR,
            fg=TEXT_MUTED
        ).pack(
            anchor="w"
        )

        # --------------------------------------------------------
        # MENÚ
        # --------------------------------------------------------

        tk.Label(
            sidebar,
            text="PRINCIPAL",
            font=("Segoe UI", 8, "bold"),
            bg=SIDEBAR,
            fg=TEXT_MUTED
        ).pack(
            anchor="w",
            padx=22,
            pady=(0, 10)
        )

        botones = [
            ("▣", "Dashboard", self.mostrar_dashboard),
            ("◉", "Control de acceso", self.mostrar_acceso),
            ("◇", "Tabla de verdad", self.mostrar_verdad),
            ("⚠", "Incidentes", self.mostrar_incidentes),
            ("✦", "Asistente LLM", self.mostrar_asistente),
            ("◆", "Riesgos éticos", self.mostrar_riesgos),
            ("▤", "Reportes", self.mostrar_reportes),
            ("⚙", "Configuración", self.mostrar_configuracion),
        ]

        self.botones_menu = []

        for icono, texto, comando in botones:

            boton = self.crear_boton_menu(
                sidebar,
                icono,
                texto,
                comando
            )

            self.botones_menu.append(boton)

        # --------------------------------------------------------
        # PIE DEL MENÚ
        # --------------------------------------------------------

        pie = tk.Frame(
            sidebar,
            bg="#0B1220"
        )

        pie.pack(
            side="bottom",
            fill="x"
        )

        tk.Label(
            pie,
            text="LogiSmart v1.0",
            font=("Segoe UI", 9, "bold"),
            bg="#0B1220",
            fg="#CBD5E1"
        ).pack(
            anchor="w",
            padx=22,
            pady=(14, 2)
        )

        tk.Label(
            pie,
            text="Sistema de apoyo a decisiones",
            font=("Segoe UI", 8),
            bg="#0B1220",
            fg=TEXT_MUTED
        ).pack(
            anchor="w",
            padx=22,
            pady=(0, 14)
        )

        # --------------------------------------------------------
        # ÁREA PRINCIPAL
        # --------------------------------------------------------

        area = tk.Frame(
            self,
            bg=BG
        )

        area.pack(
            side="left",
            fill="both",
            expand=True
        )

        # --------------------------------------------------------
        # TOPBAR
        # --------------------------------------------------------

        topbar = tk.Frame(
            area,
            bg=SURFACE,
            height=68,
            highlightthickness=1,
            highlightbackground="#E2E8F0"
        )

        topbar.pack(
            fill="x"
        )

        topbar.pack_propagate(False)

        tk.Label(
            topbar,
            text="Centro de Control Inteligente",
            font=("Segoe UI", 11, "bold"),
            bg=SURFACE,
            fg=TEXT
        ).pack(
            side="left",
            padx=28
        )

        estado = tk.Frame(
            topbar,
            bg=SURFACE
        )

        estado.pack(
            side="right",
            padx=28
        )

        tk.Label(
            estado,
            text="●",
            font=("Segoe UI", 12),
            bg=SURFACE,
            fg="#16A34A"
        ).pack(
            side="left",
            padx=(0, 6)
        )

        tk.Label(
            estado,
            text="Sistema operativo",
            font=("Segoe UI", 9, "bold"),
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack(
            side="left"
        )

        # --------------------------------------------------------
        # CONTENEDOR
        # --------------------------------------------------------

        self.contenedor = tk.Frame(
            area,
            bg=BG
        )

        self.contenedor.pack(
            fill="both",
            expand=True
        )

    # ============================================================
    # BOTONES DEL MENÚ
    # ============================================================

    def crear_boton_menu(
        self,
        parent,
        icono,
        texto,
        comando
    ):

        boton = tk.Frame(
            parent,
            bg=SIDEBAR,
            height=46,
            cursor="hand2"
        )

        boton.pack(
            fill="x",
            padx=12,
            pady=2
        )

        boton.pack_propagate(False)

        icono_label = tk.Label(
            boton,
            text=icono,
            font=("Segoe UI", 12),
            bg=SIDEBAR,
            fg="#94A3B8",
            width=3
        )

        icono_label.pack(
            side="left"
        )

        texto_label = tk.Label(
            boton,
            text=texto,
            font=("Segoe UI", 10),
            bg=SIDEBAR,
            fg="#CBD5E1"
        )

        texto_label.pack(
            side="left"
        )

        widgets = [
            boton,
            icono_label,
            texto_label
        ]

        for widget in widgets:

            widget.bind(
                "<Button-1>",
                lambda event, cmd=comando: cmd()
            )

            widget.bind(
                "<Enter>",
                lambda event, frame=boton:
                self.hover_menu(frame, True)
            )

            widget.bind(
                "<Leave>",
                lambda event, frame=boton:
                self.hover_menu(frame, False)
            )

        return boton

    # ============================================================
    # HOVER
    # ============================================================

    def hover_menu(
        self,
        boton,
        activo
    ):

        if boton == self.boton_activo:
            return

        color = (
            SIDEBAR_HOVER
            if activo
            else SIDEBAR
        )

        boton.configure(
            bg=color
        )

        for widget in boton.winfo_children():

            widget.configure(
                bg=color
            )

    # ============================================================
    # ACTIVAR BOTÓN
    # ============================================================

    def activar_menu(
        self,
        boton
    ):

        if self.boton_activo:

            self.boton_activo.configure(
                bg=SIDEBAR
            )

            for widget in self.boton_activo.winfo_children():

                widget.configure(
                    bg=SIDEBAR
                )

        self.boton_activo = boton

        boton.configure(
            bg=SIDEBAR_ACTIVE
        )

        for widget in boton.winfo_children():

            widget.configure(
                bg=SIDEBAR_ACTIVE
            )

    # ============================================================
    # LIMPIAR CONTENIDO
    # ============================================================

    def limpiar_contenido(self):

        for widget in self.contenedor.winfo_children():

            widget.destroy()

    # ============================================================
    # CAMBIO DE VISTA
    # ============================================================

    def mostrar_vista(
        self,
        vista,
        indice
    ):

        self.limpiar_contenido()

        print()
        print("======================================")
        print(" CAMBIO DE VISTA")
        print("======================================")
        print(
            f"Vista: {vista.__name__}"
        )

        try:

            print("1. Creando vista...")

            frame = vista(
                self.contenedor
            )

            print(
                "2. Vista creada correctamente."
            )

            frame.pack(
                fill="both",
                expand=True
            )

            print(
                "3. Vista mostrada correctamente."
            )

            if indice < len(
                self.botones_menu
            ):

                self.activar_menu(
                    self.botones_menu[indice]
                )

            print(
                "4. Navegación completada."
            )

        except Exception as error:

            import traceback

            print()
            print(
                "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            )
            print(
                " ERROR AL CARGAR LA VISTA"
            )
            print(
                "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            )

            print(
                f"Tipo: {type(error).__name__}"
            )

            print(
                f"Mensaje: {error}"
            )

            traceback.print_exc()

            self.limpiar_contenido()

            tk.Label(
                self.contenedor,
                text="ERROR AL CARGAR ESTA SECCIÓN",
                font=("Segoe UI", 22, "bold"),
                bg=BG,
                fg="#DC2626"
            ).pack(
                pady=(100, 10)
            )

            tk.Label(
                self.contenedor,
                text=str(error),
                font=("Segoe UI", 11),
                bg=BG,
                fg=TEXT_SECONDARY,
                wraplength=800,
                justify="center"
            ).pack(
                pady=10
            )

    # ============================================================
    # VISTAS
    # ============================================================

    def mostrar_dashboard(self):
        self.mostrar_vista(
            DashboardView,
            0
        )

    def mostrar_acceso(self):
        self.mostrar_vista(
            AccesoView,
            1
        )

    def mostrar_verdad(self):
        self.mostrar_vista(
            VerdadView,
            2
        )

    def mostrar_incidentes(self):
        self.mostrar_vista(
            IncidentesView,
            3
        )

    def mostrar_asistente(self):
        self.mostrar_vista(
            AsistenteView,
            4
        )

    def mostrar_riesgos(self):
        self.mostrar_vista(
            RiesgosView,
            5
        )

    def mostrar_reportes(self):
        self.mostrar_vista(
            ReportesView,
            6
        )

    def mostrar_configuracion(self):
        self.mostrar_vista(
            ConfiguracionView,
            7
        )


# ================================================================
# INICIO DE LA APLICACIÓN
# ================================================================

if __name__ == "__main__":

    app = LogiSmartApp()

    app.mainloop()