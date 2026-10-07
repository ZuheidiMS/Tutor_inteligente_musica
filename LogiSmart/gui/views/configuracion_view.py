import tkinter as tk
from tkinter import messagebox

from database.mongodb import MongoDB
from database.config_repository import ConfigRepository


class ConfiguracionView(tk.Frame):

    def __init__(self, parent):
        super().__init__(
            parent,
            bg="#f4f6f8"
        )

        self.mongo = MongoDB()

        self.db = self.mongo.conectar()

        if self.db is None:
            messagebox.showerror(
                "MongoDB",
                "No fue posible conectar con MongoDB."
            )
            return

        self.repo = ConfigRepository(
            self.mongo.db
        )

        self.crear_interfaz()
        self.cargar()

    def crear_interfaz(self):

        tk.Label(
            self,
            text="Configuración",
            font=("Segoe UI", 24, "bold"),
            bg="#f4f6f8"
        ).pack(
            anchor="w",
            padx=30,
            pady=(30, 20)
        )

        frame = tk.Frame(
            self,
            bg="white",
            padx=30,
            pady=30
        )

        frame.pack(
            fill="x",
            padx=30
        )

        self.modelo = self.campo(
            frame,
            "Modelo Ollama:",
            0
        )

        self.servidor = self.campo(
            frame,
            "Servidor Ollama:",
            1
        )

        self.temperatura = self.campo(
            frame,
            "Temperatura:",
            2
        )

        self.umbral = self.campo(
            frame,
            "Umbral de revisión:",
            3
        )

        self.simular = tk.BooleanVar(
            value=True
        )

        tk.Checkbutton(
            frame,
            text="Simular recepción de correos",
            variable=self.simular,
            bg="white",
            font=("Segoe UI", 10)
        ).grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="w",
            pady=15
        )

        tk.Button(
            frame,
            text="Guardar configuración",
            command=self.guardar,
            bg="#1F618D",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20,
            pady=10
        ).grid(
            row=5,
            column=0,
            columnspan=2,
            pady=10
        )

    def campo(self, parent, texto, fila):

        tk.Label(
            parent,
            text=texto,
            bg="white",
            font=("Segoe UI", 10, "bold")
        ).grid(
            row=fila,
            column=0,
            sticky="w",
            pady=8
        )

        entrada = tk.Entry(
            parent,
            width=50,
            font=("Segoe UI", 10)
        )

        entrada.grid(
            row=fila,
            column=1,
            padx=15,
            pady=8
        )

        return entrada

    def cargar(self):

        datos = self.repo.obtener()

        self.modelo.insert(
            0,
            datos.get(
                "modelo_ollama",
                "llama3.2"
            )
        )

        self.servidor.insert(
            0,
            datos.get(
                "servidor_ollama",
                "http://localhost:11434"
            )
        )

        self.temperatura.insert(
            0,
            str(
                datos.get(
                    "temperatura",
                    0.0
                )
            )
        )

        self.umbral.insert(
            0,
            datos.get(
                "umbral_revision",
                "alta"
            )
        )

        self.simular.set(
            datos.get(
                "simular_correo",
                True
            )
        )

    def guardar(self):

        try:

            datos = self.repo.guardar(
                modelo=self.modelo.get().strip(),
                servidor=self.servidor.get().strip(),
                temperatura=float(
                    self.temperatura.get()
                ),
                umbral_revision=self.umbral.get().strip(),
                simular_correo=self.simular.get()
            )

            messagebox.showinfo(
                "Configuración",
                "Configuración guardada correctamente."
            )

        except Exception as error:

            messagebox.showerror(
                "Error",
                f"No fue posible guardar:\n{error}"
            )