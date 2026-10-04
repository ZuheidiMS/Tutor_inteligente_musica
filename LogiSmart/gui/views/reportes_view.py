
import tkinter as tk
from tkinter import filedialog, messagebox

from database.mongodb import MongoDB
from reports.report_generator import ReportGenerator


class ReportesView(tk.Frame):

    def __init__(self, parent):
        super().__init__(
            parent,
            bg="#f4f6f8"
        )

        self.db_connection = MongoDB()

        # CORRECCIÓN:
        # No se debe evaluar directamente self.db_connection.conectar()
        self.db = self.db_connection.conectar()

        if self.db is None:
            messagebox.showerror(
                "MongoDB",
                "No fue posible conectar con MongoDB."
            )
            return

        self.generador = ReportGenerator(
            self.db
        )

        self.crear_interfaz()

    def crear_interfaz(self):

        tk.Label(
            self,
            text="Reportes",
            font=("Segoe UI", 24, "bold"),
            bg="#f4f6f8",
            fg="#17202A"
        ).pack(
            anchor="w",
            padx=30,
            pady=(30, 5)
        )

        tk.Label(
            self,
            text="Genera reportes reales utilizando la información almacenada en MongoDB.",
            font=("Segoe UI", 11),
            bg="#f4f6f8",
            fg="#566573"
        ).pack(
            anchor="w",
            padx=30,
            pady=(0, 25)
        )

        contenedor = tk.Frame(
            self,
            bg="white",
            padx=30,
            pady=30
        )

        contenedor.pack(
            fill="x",
            padx=30
        )

        # -----------------------------------------------------
        # INFORMACIÓN
        # -----------------------------------------------------

        informacion = tk.Frame(
            contenedor,
            bg="#F8F9F9"
        )

        informacion.pack(
            fill="x",
            pady=(0, 20)
        )

        tk.Label(
            informacion,
            text="Exportación de información",
            font=("Segoe UI", 13, "bold"),
            bg="#F8F9F9",
            fg="#17202A"
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 5)
        )

        tk.Label(
            informacion,
            text=(
                "Selecciona el formato que deseas generar. "
                "Los archivos utilizan los datos almacenados "
                "actualmente en MongoDB."
            ),
            font=("Segoe UI", 10),
            bg="#F8F9F9",
            fg="#566573",
            justify="left",
            wraplength=800
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 15)
        )

        # -----------------------------------------------------
        # BOTONES
        # -----------------------------------------------------

        botones = [
            ("Generar JSON", self.generar_json),
            ("Generar CSV", self.generar_csv),
            ("Generar PDF", self.generar_pdf),
        ]

        for texto, comando in botones:

            tk.Button(
                contenedor,
                text=texto,
                command=comando,
                font=("Segoe UI", 11, "bold"),
                bg="#1F618D",
                fg="white",
                activebackground="#154360",
                activeforeground="white",
                padx=20,
                pady=12,
                relief="flat",
                cursor="hand2"
            ).pack(
                fill="x",
                pady=7
            )

    def seleccionar_ruta(self, extension):

        return filedialog.asksaveasfilename(
            title="Guardar reporte",
            defaultextension=extension,
            filetypes=[
                (
                    extension.upper().replace(".", ""),
                    f"*{extension}"
                )
            ]
        )

    def generar_json(self):

        try:

            ruta = self.seleccionar_ruta(
                ".json"
            )

            if not ruta:
                return

            self.generador.generar_json(
                ruta
            )

            messagebox.showinfo(
                "Reporte generado",
                f"Reporte JSON generado correctamente.\n\n"
                f"Archivo:\n{ruta}"
            )

        except Exception as error:

            messagebox.showerror(
                "Error al generar JSON",
                f"No fue posible generar el reporte.\n\n"
                f"{error}"
            )

    def generar_csv(self):

        try:

            ruta = self.seleccionar_ruta(
                ".csv"
            )

            if not ruta:
                return

            self.generador.generar_csv(
                ruta
            )

            messagebox.showinfo(
                "Reporte generado",
                f"Reporte CSV generado correctamente.\n\n"
                f"Archivo:\n{ruta}"
            )

        except Exception as error:

            messagebox.showerror(
                "Error al generar CSV",
                f"No fue posible generar el reporte.\n\n"
                f"{error}"
            )

    def generar_pdf(self):

        try:

            ruta = self.seleccionar_ruta(
                ".pdf"
            )

            if not ruta:
                return

            self.generador.generar_pdf(
                ruta
            )

            messagebox.showinfo(
                "Reporte generado",
                f"Reporte PDF generado correctamente.\n\n"
                f"Archivo:\n{ruta}"
            )

        except Exception as error:

            messagebox.showerror(
                "Error al generar PDF",
                f"No fue posible generar el reporte.\n\n"
                f"{error}"
            )

