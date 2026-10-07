import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json

from database.incidentes_repository import IncidentesRepository
from services.hybrid_classifier import HybridClassifier


class IncidentesView(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="#f4f6f8")

        self.repo = None
        self.classifier = None

        self.crear_interfaz()

        try:
            self.repo = IncidentesRepository()
            self.classifier = HybridClassifier()

        except Exception as e:
            messagebox.showerror(
                "Error al inicializar servicios",
                f"No se pudieron inicializar los servicios:\n\n{e}"
            )

    def crear_interfaz(self):

        titulo = tk.Label(
            self,
            text="Gestión de incidentes",
            font=("Segoe UI", 22, "bold"),
            bg="#f4f6f8",
            fg="#1f2937"
        )
        titulo.pack(anchor="w", padx=25, pady=(20, 5))

        subtitulo = tk.Label(
            self,
            text="Clasifica correos mediante reglas y LLM, consulta los resultados y administra su estado.",
            font=("Segoe UI", 11),
            bg="#f4f6f8",
            fg="#6b7280"
        )
        subtitulo.pack(anchor="w", padx=25, pady=(0, 20))

        formulario = tk.Frame(
            self,
            bg="white",
            highlightbackground="#d1d5db",
            highlightthickness=1
        )
        formulario.pack(
            fill="x",
            padx=25,
            pady=5
        )

        tk.Label(
            formulario,
            text="Remitente",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#1f2937"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=15,
            pady=(15, 5)
        )

        self.entry_remitente = tk.Entry(
            formulario,
            font=("Segoe UI", 11)
        )
        self.entry_remitente.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 10),
            sticky="ew"
        )

        tk.Label(
            formulario,
            text="Asunto",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#1f2937"
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=15,
            pady=(15, 5)
        )

        self.entry_asunto = tk.Entry(
            formulario,
            font=("Segoe UI", 11)
        )
        self.entry_asunto.grid(
            row=1,
            column=1,
            padx=15,
            pady=(0, 10),
            sticky="ew"
        )

        tk.Label(
            formulario,
            text="Contenido del correo",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#1f2937"
        ).grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="w",
            padx=15,
            pady=(10, 5)
        )

        self.texto_correo = tk.Text(
            formulario,
            height=8,
            font=("Segoe UI", 11),
            wrap="word"
        )
        self.texto_correo.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=15,
            pady=(0, 15),
            sticky="ew"
        )

        formulario.columnconfigure(0, weight=1)
        formulario.columnconfigure(1, weight=1)

        botones = tk.Frame(
            self,
            bg="#f4f6f8"
        )
        botones.pack(
            fill="x",
            padx=25,
            pady=15
        )

        self.boton_clasificar = tk.Button(
            botones,
            text="Clasificar y guardar",
            font=("Segoe UI", 11, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=10,
            command=self.clasificar
        )
        self.boton_clasificar.pack(
            side="left",
            padx=(0, 10)
        )

        self.boton_analizar = tk.Button(
            botones,
            text="Analizar sin guardar",
            font=("Segoe UI", 11),
            bg="#374151",
            fg="white",
            activebackground="#1f2937",
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=10,
            command=self.analizar_sin_guardar
        )
        self.boton_analizar.pack(
            side="left"
        )

        self.progress = ttk.Progressbar(
            botones,
            mode="indeterminate",
            length=180
        )
        self.progress.pack(
            side="right",
            padx=10
        )

        resultado_frame = tk.Frame(
            self,
            bg="white",
            highlightbackground="#d1d5db",
            highlightthickness=1
        )
        resultado_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 25)
        )

        tk.Label(
            resultado_frame,
            text="Resultado",
            font=("Segoe UI", 15, "bold"),
            bg="white",
            fg="#1f2937"
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 10)
        )

        self.resultado = tk.Text(
            resultado_frame,
            font=("Consolas", 10),
            wrap="word",
            state="disabled"
        )
        self.resultado.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

    def obtener_correo(self):

        remitente = self.entry_remitente.get().strip()
        asunto = self.entry_asunto.get().strip()
        contenido = self.texto_correo.get(
            "1.0",
            "end"
        ).strip()

        if not contenido:

            messagebox.showwarning(
                "Dato faltante",
                "Escribe el contenido del correo."
            )

            return None

        return {
            "remitente": remitente,
            "asunto": asunto,
            "contenido": contenido
        }

    def mostrar_resultado(self, texto):

        self.resultado.config(
            state="normal"
        )

        self.resultado.delete(
            "1.0",
            "end"
        )

        self.resultado.insert(
            "1.0",
            texto
        )

        self.resultado.config(
            state="disabled"
        )

    def bloquear_botones(self):

        self.boton_clasificar.config(
            state="disabled"
        )

        self.boton_analizar.config(
            state="disabled"
        )

        self.progress.start(10)

    def desbloquear_botones(self):

        self.boton_clasificar.config(
            state="normal"
        )

        self.boton_analizar.config(
            state="normal"
        )

        self.progress.stop()

    def clasificar(self):

        correo = self.obtener_correo()

        if correo is None:
            return

        if (
            self.repo is None
            or self.classifier is None
        ):

            messagebox.showerror(
                "Servicio no disponible",
                "Los servicios de incidentes no están disponibles."
            )

            return

        self.bloquear_botones()

        hilo = threading.Thread(
            target=self.procesar_clasificacion,
            args=(correo,),
            daemon=True
        )

        hilo.start()

    def procesar_clasificacion(self, correo):

        try:

            asunto = correo["asunto"]
            cuerpo = correo["contenido"]

            # IMPORTANTE:
            # HybridClassifier.clasificar()
            # recibe asunto y cuerpo por separado.
            resultado = self.classifier.clasificar(
                asunto,
                cuerpo
            )

            # La clasificación está dentro de
            # resultado["clasificacion"]
            clasificacion = resultado.get(
                "clasificacion",
                {}
            )

            categoria = clasificacion.get(
                "categoria",
                "otro"
            )

            prioridad = clasificacion.get(
                "prioridad",
                "media"
            )

            entidades = clasificacion.get(
                "entidades",
                []
            )

            resumen = clasificacion.get(
                "resumen",
                ""
            )

            estado = "nuevo"

            datos_extraidos = {
                "remitente": correo["remitente"],
                "asunto": correo["asunto"],
                "entidades": entidades
            }

            incidente_id = self.repo.crear(
                correo_original=(
                    f"Remitente: {correo['remitente']}\n"
                    f"Asunto: {correo['asunto']}\n\n"
                    f"{correo['contenido']}"
                ),
                categoria=categoria,
                prioridad=prioridad,
                entidades=entidades,
                resumen=resumen,
                estado=estado,
                datos_extraidos=datos_extraidos
            )

            resultado_final = {
                "id": incidente_id,
                "categoria": categoria,
                "prioridad": prioridad,
                "entidades": entidades,
                "resumen": resumen,
                "estado": estado,
                "fuente": resultado.get(
                    "fuente",
                    "desconocida"
                ),
                "modelo": resultado.get(
                    "modelo"
                ),
                "latencia_ms": resultado.get(
                    "latencia_ms"
                ),
                "requiere_revision_humana": resultado.get(
                    "requiere_revision_humana",
                    False
                ),
                "coincide_con_reglas": resultado.get(
                    "coincide_con_reglas",
                    False
                ),
                "clasificacion_reglas": resultado.get(
                    "clasificacion_reglas",
                    {}
                ),
                "clasificacion_llm": resultado.get(
                    "clasificacion_llm",
                    {}
                ),
                "resultado_completo": resultado
            }

            self.after(
                0,
                lambda: self.finalizar_clasificacion(
                    resultado_final
                )
            )

        except Exception as e:

            mensaje = (
                "Error durante la clasificación:\n\n"
                f"{type(e).__name__}: {e}"
            )

            self.after(
                0,
                lambda: self.mostrar_error(
                    mensaje
                )
            )

    def finalizar_clasificacion(self, resultado):

        self.desbloquear_botones()

        texto = json.dumps(
            resultado,
            indent=4,
            ensure_ascii=False,
            default=str
        )

        self.mostrar_resultado(
            texto
        )

        messagebox.showinfo(
            "Incidente registrado",
            "El incidente fue clasificado y guardado correctamente."
        )

    def analizar_sin_guardar(self):

        correo = self.obtener_correo()

        if correo is None:
            return

        if self.classifier is None:

            messagebox.showerror(
                "Servicio no disponible",
                "El clasificador no está disponible."
            )

            return

        self.bloquear_botones()

        hilo = threading.Thread(
            target=self.procesar_analisis,
            args=(correo,),
            daemon=True
        )

        hilo.start()

    def procesar_analisis(self, correo):

        try:

            asunto = correo["asunto"]
            cuerpo = correo["contenido"]

            # El clasificador recibe 2 argumentos.
            resultado = self.classifier.clasificar(
                asunto,
                cuerpo
            )

            self.after(
                0,
                lambda: self.finalizar_analisis(
                    resultado
                )
            )

        except Exception as e:

            mensaje = (
                "Error durante el análisis:\n\n"
                f"{type(e).__name__}: {e}"
            )

            self.after(
                0,
                lambda: self.mostrar_error(
                    mensaje
                )
            )

    def finalizar_analisis(self, resultado):

        self.desbloquear_botones()

        texto = json.dumps(
            resultado,
            indent=4,
            ensure_ascii=False,
            default=str
        )

        self.mostrar_resultado(
            texto
        )

    def mostrar_error(self, mensaje):

        self.desbloquear_botones()

        self.mostrar_resultado(
            mensaje
        )

        messagebox.showerror(
            "Error",
            mensaje
        )