import json
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from database.mongodb import MongoDB
from services.llm_service import OllamaService

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
    separador,
)


class AsistenteView(tk.Frame):

    def __init__(self, parent):
        super().__init__(
            parent,
            bg=BG
        )

        self.mongo = None
        self.db = None
        self.ollama = None

        self.historial = []
        self.ultima_respuesta = ""

        self.crear_interfaz()
        self.inicializar_servicios()

        # Esperar a que la ventana termine de dibujarse
        self.after(300, self.activar_campo)

    # =========================================================
    # INTERFAZ
    # =========================================================

    def crear_interfaz(self):

        encabezado(
            self,
            "Asistente LLM",
            "Consulta información del sistema mediante MongoDB y Ollama."
        )

        contenedor = tk.Frame(
            self,
            bg=BG
        )

        contenedor.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 25)
        )

        # =====================================================
        # TARJETA PRINCIPAL
        # =====================================================

        tarjeta_chat = tarjeta(
            contenedor
        )

        tarjeta_chat.pack(
            fill="both",
            expand=True
        )

        # =====================================================
        # CABECERA
        # =====================================================

        cabecera = tk.Frame(
            tarjeta_chat,
            bg=SURFACE
        )

        cabecera.pack(
            fill="x",
            padx=24,
            pady=20
        )

        izquierda = tk.Frame(
            cabecera,
            bg=SURFACE
        )

        izquierda.pack(
            side="left",
            fill="x",
            expand=True
        )

        tk.Label(
            izquierda,
            text="Asistente de LogiSmart",
            font=FONT_SECTION,
            bg=SURFACE,
            fg=TEXT
        ).pack(
            anchor="w"
        )

        tk.Label(
            izquierda,
            text=(
                "Consulta información registrada en MongoDB "
                "mediante el modelo local Ollama."
            ),
            font=FONT_SMALL,
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        self.estado = tk.Label(
            cabecera,
            text="● Inicializando",
            font=("Segoe UI", 9, "bold"),
            bg=WARNING_SOFT,
            fg=WARNING,
            padx=12,
            pady=6
        )

        self.estado.pack(
            side="right"
        )

        separador(
            tarjeta_chat
        ).pack(
            fill="x"
        )

        # =====================================================
        # ÁREA DEL CHAT
        # =====================================================

        area_chat = tk.Frame(
            tarjeta_chat,
            bg=SURFACE_SOFT
        )

        area_chat.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=18
        )

        self.chat = tk.Text(
            area_chat,
            font=FONT_BODY,
            bg=SURFACE_SOFT,
            fg=TEXT,
            relief="flat",
            bd=0,
            wrap="word",
            state=tk.DISABLED,
            padx=18,
            pady=18,
            cursor="arrow"
        )

        scrollbar = ttk.Scrollbar(
            area_chat,
            orient="vertical",
            command=self.chat.yview
        )

        self.chat.configure(
            yscrollcommand=scrollbar.set
        )

        self.chat.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # =====================================================
        # ESTILOS DEL CHAT
        # =====================================================

        self.chat.tag_configure(
            "usuario",
            font=("Segoe UI", 10, "bold"),
            foreground=PRIMARY
        )

        self.chat.tag_configure(
            "asistente",
            font=("Segoe UI", 10, "bold"),
            foreground=SUCCESS
        )

        self.chat.tag_configure(
            "fuente",
            font=("Segoe UI", 9),
            foreground=INFO
        )

        self.chat.tag_configure(
            "sistema",
            font=("Segoe UI", 9, "italic"),
            foreground=TEXT_MUTED
        )

        self.chat.tag_configure(
            "error",
            font=("Segoe UI", 9),
            foreground=DANGER
        )

        self.chat.tag_configure(
            "normal",
            font=FONT_BODY,
            foreground=TEXT
        )

        # =====================================================
        # MENSAJE INICIAL
        # =====================================================

        self.agregar_sistema(
            "Hola. Soy el asistente de LogiSmart.\n"
            "Puedes preguntarme por camiones, accesos o incidentes."
        )

        # =====================================================
        # BARRA DE CARGA
        # =====================================================

        carga = tk.Frame(
            tarjeta_chat,
            bg=SURFACE
        )

        carga.pack(
            fill="x",
            padx=24,
            pady=(0, 10)
        )

        self.progress = ttk.Progressbar(
            carga,
            mode="indeterminate"
        )

        self.progress.pack(
            fill="x"
        )

        self.progress.pack_forget()

        self.estado_carga = tk.Label(
            carga,
            text="",
            font=FONT_SMALL,
            bg=SURFACE,
            fg=TEXT_SECONDARY
        )

        self.estado_carga.pack(
            anchor="w",
            pady=(5, 0)
        )

        # =====================================================
        # ZONA DE PREGUNTA
        # =====================================================

        inferior = tk.Frame(
            tarjeta_chat,
            bg=SURFACE
        )

        inferior.pack(
            fill="x",
            padx=24,
            pady=(5, 20)
        )

        tk.Label(
            inferior,
            text="Pregunta al asistente",
            font=("Segoe UI", 9, "bold"),
            bg=SURFACE,
            fg=TEXT_SECONDARY
        ).pack(
            anchor="w",
            pady=(0, 6)
        )

        fila = tk.Frame(
            inferior,
            bg=SURFACE
        )

        fila.pack(
            fill="x"
        )

        # =====================================================
        # CAMPO DE ESCRITURA
        # =====================================================

        self.entrada = tk.Entry(
            fila,
            font=("Segoe UI", 12),
            bg="white",
            fg="black",
            insertbackground="black",
            insertwidth=2,
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightbackground=BORDER,
            highlightcolor=PRIMARY,
            state="normal",
            takefocus=True
        )

        self.entrada.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=10
        )

        # IMPORTANTE:
        # Eventos para garantizar que el campo reciba el teclado.

        self.entrada.bind(
            "<Button-1>",
            self.enfocar_entrada
        )
        

        self.entrada.bind(
            "<Return>",
            self.preguntar_enter
        )

        self.entrada.bind(
            "<FocusIn>",
            self.cambiar_borde_entrada
        )

        self.entrada.bind(
            "<FocusOut>",
            self.quitar_borde_entrada
        )

        # =====================================================
        # BOTÓN PREGUNTAR
        # =====================================================

        self.boton_preguntar = boton(
            fila,
            "Preguntar",
            self.preguntar,
            "primary"
        )

        self.boton_preguntar.pack(
            side="left",
            padx=(10, 0)
        )

        # =====================================================
        # BOTÓN LIMPIAR
        # =====================================================

        self.boton_limpiar = boton(
            fila,
            "Limpiar",
            self.limpiar_chat,
            "secondary"
        )

        self.boton_limpiar.pack(
            side="left",
            padx=(8, 0)
        )

        # =====================================================
        # BOTÓN COPIAR
        # =====================================================

        self.boton_copiar = boton(
            fila,
            "Copiar",
            self.copiar_respuesta,
            "secondary"
        )

        self.boton_copiar.pack(
            side="left",
            padx=(8, 0)
        )

       # =========================================================
    # FOCO DEL CAMPO
    # =========================================================

    def activar_campo(self):

        try:

            self.entrada.config(
                state="normal"
            )

            self.focus_set()

            self.entrada.focus_force()

            self.entrada.icursor(
                tk.END
            )

        except tk.TclError as error:

            print(
                "Error al activar campo:",
                error
            )
        
        except tk.TclError as error:

            print(
                "Error al activar campo:",
                error
            )

    def enfocar_entrada(self, event=None):

        print(">>> CLICK DETECTADO")
        print(">>> WIDGET:", event.widget if event else "ninguno")

        try:

            self.entrada.config(
                state="normal"
            )

            self.entrada.focus_set()

            self.entrada.focus_force()

            self.entrada.icursor(tk.END)

            print(">>> FOCO COLOCADO EN ENTRY")

        except tk.TclError as error:

            print(
                ">>> ERROR DE FOCO:",
                error
            )


    def cambiar_borde_entrada(
        self,
        event=None
    ):

        try:

            self.entrada.config(
                highlightbackground=PRIMARY,
                highlightcolor=PRIMARY
            )

        except tk.TclError:

            pass

    def quitar_borde_entrada(
        self,
        event=None
    ):
        

        

        try:

            self.entrada.config(
                highlightbackground=BORDER,
                highlightcolor=PRIMARY
            )

        except tk.TclError:

            pass

    # =========================================================
    # SERVICIOS
    # =========================================================

    def inicializar_servicios(self):

        try:

            self.mongo = MongoDB()

            self.db = self.mongo.conectar()

            if self.db is None:

                self.actualizar_estado(
                    "● MongoDB no disponible",
                    "warning"
                )

                self.agregar_error(
                    "No fue posible conectar con MongoDB."
                )

                self.activar_campo()

                return

            self.ollama = OllamaService(
                model="llama3.2"
            )

            self.actualizar_estado(
                "● Conectado",
                "success"
            )

            self.agregar_sistema(
                "MongoDB conectado correctamente.\n"
                "Modelo Ollama configurado: llama3.2"
            )

            self.activar_campo()

        except Exception as error:

            self.actualizar_estado(
                "● Error",
                "danger"
            )

            self.agregar_error(
                f"Error al inicializar el asistente:\n{error}"
            )

            self.activar_campo()

    # =========================================================
    # PREGUNTAR CON ENTER
    # =========================================================

    def preguntar_enter(
        self,
        event=None
    ):

        self.preguntar()

        return "break"

    # =========================================================
    # PREGUNTAR
    # =========================================================

    def preguntar(self):

        try:

            # Asegurar que el Entry esté habilitado
            self.entrada.config(
                state="normal"
            )

            pregunta = self.entrada.get().strip()

        except Exception:

            pregunta = ""

        if not pregunta:

            messagebox.showwarning(
                "Validación",
                "Escribe una pregunta."
            )

            self.activar_campo()

            return

        if self.db is None:

            messagebox.showerror(
                "MongoDB",
                "No existe conexión con MongoDB."
            )

            self.activar_campo()

            return

        if self.ollama is None:

            messagebox.showerror(
                "Ollama",
                "El servicio Ollama no está disponible."
            )

            self.activar_campo()

            return

        # =====================================================
        # MOSTRAR PREGUNTA
        # =====================================================

        self.agregar_usuario(
            pregunta
        )

        # Limpiar campo
        self.entrada.delete(
            0,
            tk.END
        )

        # =====================================================
        # DESACTIVAR BOTONES DURANTE CONSULTA
        # =====================================================

        self.boton_preguntar.config(
            state=tk.DISABLED
        )

        self.boton_limpiar.config(
            state=tk.DISABLED
        )

        self.boton_copiar.config(
            state=tk.DISABLED
        )

        # El Entry NO se bloquea permanentemente.
        # Solo se evita escribir mientras se procesa.
        self.entrada.config(
            state="disabled"
        )

        # =====================================================
        # MOSTRAR PROGRESO
        # =====================================================

        self.progress.pack(
            fill="x"
        )

        self.progress.start(10)

        self.estado_carga.config(
            text="Consultando información en MongoDB y Ollama..."
        )

        # =====================================================
        # HILO
        # =====================================================

        hilo = threading.Thread(
            target=self.procesar_pregunta,
            args=(pregunta,),
            daemon=True
        )

        hilo.start()

    # =========================================================
    # PROCESAR PREGUNTA
    # =========================================================

    def procesar_pregunta(
        self,
        pregunta
    ):

        try:

            registros = self.buscar_informacion(
                pregunta
            )

            if not registros:

                resultado = {
                    "respuesta": (
                        "No tengo información suficiente "
                        "en los registros de LogiSmart "
                        "para responder esa pregunta."
                    ),
                    "fuentes": [],
                    "modelo": None,
                    "latencia_ms": 0
                }

            else:

                contexto = self.construir_contexto(
                    registros
                )

                prompt = self.construir_prompt(
                    pregunta,
                    contexto
                )

                respuesta = self.ollama.generar(
                    prompt
                )

                resultado = {
                    "respuesta": respuesta["respuesta"],
                    "fuentes": registros,
                    "modelo": respuesta["modelo"],
                    "latencia_ms": respuesta["latencia_ms"]
                }

            self.after(
                0,
                lambda resultado=resultado:
                self.mostrar_respuesta(resultado)
            )

        except Exception as error:

            self.after(
                0,
                lambda error=error:
                self.mostrar_error(error)
            )

    # =========================================================
    # BUSCAR INFORMACIÓN
    # =========================================================

    def buscar_informacion(
        self,
        pregunta
    ):

        pregunta_lower = pregunta.lower()

        registros = []

        # =====================================================
        # CAMIONES
        # =====================================================

        palabras_camiones = [
            "camion",
            "camión",
            "camiones",
            "placa",
            "empresa",
            "conductor",
            "cam-"
        ]

        if any(
            palabra in pregunta_lower
            for palabra in palabras_camiones
        ):

            documentos = list(
                self.db["camiones"].find(
                    {},
                    {
                        "_id": 0,
                        "placa": 1,
                        "camion_id": 1,
                        "empresa": 1,
                        "autorizacion": 1,
                        "certificacion_conductor": 1
                    }
                ).limit(10)
            )

            for documento in documentos:

                registros.append(
                    {
                        "coleccion": "camiones",
                        "datos": documento
                    }
                )

        # =====================================================
        # ACCESOS
        # =====================================================

        palabras_accesos = [
            "acceso",
            "inspeccion",
            "inspección",
            "premisa",
            "resultado",
            "permitido",
            "autorizado",
            "bloqueado"
        ]

        if any(
            palabra in pregunta_lower
            for palabra in palabras_accesos
        ):

            documentos = list(
                self.db["accesos"].find(
                    {},
                    {
                        "_id": 0,
                        "P": 1,
                        "Q": 1,
                        "R": 1,
                        "S": 1,
                        "resultado_A": 1,
                        "resultado_E": 1,
                        "timestamp": 1,
                        "operador": 1,
                        "explicacion": 1
                    }
                ).sort(
                    "timestamp",
                    -1
                ).limit(10)
            )

            for documento in documentos:

                if "timestamp" in documento:

                    documento["timestamp"] = str(
                        documento["timestamp"]
                    )

                registros.append(
                    {
                        "coleccion": "accesos",
                        "datos": documento
                    }
                )

        # =====================================================
        # INCIDENTES
        # =====================================================

        palabras_incidentes = [
            "incidente",
            "incidentes",
            "correo",
            "material",
            "peligroso",
            "prioridad",
            "emergencia",
            "evento"
        ]

        if any(
            palabra in pregunta_lower
            for palabra in palabras_incidentes
        ):

            documentos = list(
                self.db["incidentes"].find(
                    {},
                    {
                        "_id": 0,
                        "correo_original": 1,
                        "categoria": 1,
                        "prioridad": 1,
                        "entidades": 1,
                        "resumen": 1,
                        "datos_extraidos": 1,
                        "estado": 1,
                        "fecha_creacion": 1,
                        "fecha_actualizacion": 1
                    }
                ).sort(
                    "fecha_creacion",
                    -1
                ).limit(10)
            )

            for documento in documentos:

                if "fecha_creacion" in documento:

                    documento["fecha_creacion"] = str(
                        documento["fecha_creacion"]
                    )

                if "fecha_actualizacion" in documento:

                    documento["fecha_actualizacion"] = str(
                        documento["fecha_actualizacion"]
                    )

                registros.append(
                    {
                        "coleccion": "incidentes",
                        "datos": documento
                    }
                )

        # =====================================================
        # EVALUACIONES LLM
        # =====================================================

        palabras_evaluacion = [
            "llm",
            "modelo",
            "evaluacion",
            "evaluación",
            "latencia",
            "clasificacion",
            "clasificación"
        ]

        if any(
            palabra in pregunta_lower
            for palabra in palabras_evaluacion
        ):

            documentos = list(
                self.db["evaluaciones_llm"].find(
                    {},
                    {
                        "_id": 0,
                        "prompt": 1,
                        "respuesta": 1,
                        "response": 1,
                        "modelo": 1,
                        "model": 1,
                        "latencia": 1,
                        "latencia_ms": 1,
                        "matched_rules": 1,
                        "requiere_revision_humana": 1
                    }
                ).limit(10)
            )

            for documento in documentos:

                registros.append(
                    {
                        "coleccion": "evaluaciones_llm",
                        "datos": documento
                    }
                )

        return registros[:15]

    # =========================================================
    # CONSTRUIR CONTEXTO
    # =========================================================

    def construir_contexto(
        self,
        registros
    ):

        partes = []

        for numero, registro in enumerate(
            registros,
            start=1
        ):

            texto = json.dumps(
                registro["datos"],
                ensure_ascii=False,
                default=str
            )

            partes.append(
                f"FUENTE {numero}\n"
                f"Colección: {registro['coleccion']}\n"
                f"Datos: {texto}"
            )

        return "\n\n".join(
            partes
        )

    # =========================================================
    # PROMPT
    # =========================================================

    def construir_prompt(
        self,
        pregunta,
        contexto
    ):

        prompt = f"""
Eres el asistente explicativo del sistema LogiSmart.

Debes responder la pregunta del operador utilizando
EXCLUSIVAMENTE los datos recuperados de MongoDB.

REGLAS:

1. No inventes información.
2. No supongas información que no aparezca en los registros.
3. No agregues datos externos.
4. Si la información no permite responder, indica:
"No tengo información suficiente en los registros de LogiSmart
para responder esa pregunta."
5. Menciona las fuentes utilizadas.
6. Si hay una contradicción entre registros, indícala.
7. Responde en español.
8. Sé claro y conciso.
9. No realices diagnósticos médicos.

PREGUNTA DEL OPERADOR:
{pregunta}

INFORMACIÓN RECUPERADA DE MONGODB:
{contexto}

RESPUESTA:
"""

        return prompt.strip()

    # =========================================================
    # MOSTRAR RESPUESTA
    # =========================================================

    def mostrar_respuesta(
        self,
        resultado
    ):

        self.progress.stop()

        self.progress.pack_forget()

        self.estado_carga.config(
            text=""
        )

        self.boton_preguntar.config(
            state=tk.NORMAL
        )

        self.boton_limpiar.config(
            state=tk.NORMAL
        )

        self.boton_copiar.config(
            state=tk.NORMAL
        )

        self.ultima_respuesta = resultado[
            "respuesta"
        ]

        self.agregar_asistente(
            self.ultima_respuesta
        )

        fuentes = resultado[
            "fuentes"
        ]

        if fuentes:

            colecciones = []

            for fuente in fuentes:

                coleccion = fuente[
                    "coleccion"
                ]

                if coleccion not in colecciones:

                    colecciones.append(
                        coleccion
                    )

            self.agregar_fuente(
                f"Fuentes consultadas: "
                f"{len(fuentes)} registro(s)"
            )

            self.agregar_fuente(
                "Colecciones: "
                + ", ".join(
                    colecciones
                )
            )

            self.agregar_fuente(
                f"Modelo: {resultado['modelo']} | "
                f"Latencia: {resultado['latencia_ms']} ms"
            )

        else:

            self.agregar_sistema(
                "No se encontraron registros relacionados "
                "en MongoDB."
            )

        # =====================================================
        # VOLVER A HABILITAR EL CAMPO
        # =====================================================

        self.entrada.config(
            state="normal"
        )

        self.activar_campo()

    # =========================================================
    # MOSTRAR ERROR
    # =========================================================

    def mostrar_error(
        self,
        error
    ):

        self.progress.stop()

        self.progress.pack_forget()

        self.estado_carga.config(
            text=""
        )

        self.boton_preguntar.config(
            state=tk.NORMAL
        )

        self.boton_limpiar.config(
            state=tk.NORMAL
        )

        self.boton_copiar.config(
            state=tk.NORMAL
        )

        self.entrada.config(
            state="normal"
        )

        self.agregar_error(
            f"No fue posible procesar la pregunta:\n{error}"
        )

        self.activar_campo()

    # =========================================================
    # MENSAJE DEL USUARIO
    # =========================================================





    def agregar_usuario(
        self,
        mensaje
    ):

        self.chat.config(
            state=tk.NORMAL
        )

        self.chat.insert(
            tk.END,
            "\nTú\n",
            "usuario"
        )

        self.chat.insert(
            tk.END,
            mensaje + "\n\n",
            "normal"
        )

        self.chat.config(
            state=tk.DISABLED
        )

        self.chat.see(
            tk.END
        )

        self.historial.append(
            {
                "rol": "usuario",
                "mensaje": mensaje
            }
        )

    # =========================================================
    # MENSAJE DEL ASISTENTE
    # =========================================================

    def agregar_asistente(
        self,
        mensaje
    ):

        self.chat.config(
            state=tk.NORMAL
        )

        self.chat.insert(
            tk.END,
            "\nLogiSmart\n",
            "asistente"
        )

        self.chat.insert(
            tk.END,
            mensaje + "\n\n",
            "normal"
        )

        self.chat.config(
            state=tk.DISABLED
        )

        self.chat.see(
            tk.END
        )

        self.historial.append(
            {
                "rol": "asistente",
                "mensaje": mensaje
            }
        )

    # =========================================================
    # MENSAJE DE FUENTE
    # =========================================================

    def agregar_fuente(
        self,
        mensaje
    ):

        self.chat.config(
            state=tk.NORMAL
        )

        self.chat.insert(
            tk.END,
            mensaje + "\n",
            "fuente"
        )

        self.chat.insert(
            tk.END,
            "\n"
        )

        self.chat.config(
            state=tk.DISABLED
        )

        self.chat.see(
            tk.END
        )

    # =========================================================
    # MENSAJE DEL SISTEMA
    # =========================================================

    def agregar_sistema(
        self,
        mensaje
    ):

        self.chat.config(
            state=tk.NORMAL
        )

        self.chat.insert(
            tk.END,
            mensaje + "\n\n",
            "sistema"
        )

        self.chat.config(
            state=tk.DISABLED
        )

        self.chat.see(
            tk.END
        )

    # =========================================================
    # MENSAJE DE ERROR
    # =========================================================

    def agregar_error(
        self,
        mensaje
    ):

        self.chat.config(
            state=tk.NORMAL
        )

        self.chat.insert(
            tk.END,
            "\nERROR\n",
            "error"
        )

        self.chat.insert(
            tk.END,
            mensaje + "\n\n",
            "error"
        )

        self.chat.config(
            state=tk.DISABLED
        )

        self.chat.see(
            tk.END
        )

    # =========================================================
    # LIMPIAR CHAT
    # =========================================================

    def limpiar_chat(self):

        confirmar = messagebox.askyesno(
            "Limpiar conversación",
            "¿Deseas limpiar la conversación?"
        )

        if not confirmar:

            return

        self.historial = []

        self.ultima_respuesta = ""

        self.chat.config(
            state=tk.NORMAL
        )

        self.chat.delete(
            "1.0",
            tk.END
        )

        self.chat.config(
            state=tk.DISABLED
        )

        self.agregar_sistema(
            "Conversación limpiada."
        )

        self.activar_campo()

    # =========================================================
    # COPIAR RESPUESTA
    # =========================================================

    def copiar_respuesta(self):

        if not self.ultima_respuesta:

            messagebox.showinfo(
                "Copiar",
                "Todavía no existe una respuesta."
            )

            self.activar_campo()

            return

        self.clipboard_clear()

        self.clipboard_append(
            self.ultima_respuesta
        )

        self.update()

        messagebox.showinfo(
            "Copiado",
            "La respuesta fue copiada."
        )

        self.activar_campo()

    # =========================================================
    # ESTADO
    # =========================================================

    def actualizar_estado(
        self,
        texto,
        tipo
    ):

        colores = {
            "success": (
                SUCCESS_SOFT,
                SUCCESS
            ),
            "warning": (
                WARNING_SOFT,
                WARNING
            ),
            "danger": (
                DANGER_SOFT,
                DANGER
            ),
            "info": (
                INFO_SOFT,
                INFO
            )
        }

        fondo, color = colores.get(
            tipo,
            (
                SURFACE_SOFT,
                TEXT_SECONDARY
            )
        )

        self.estado.config(
            text=texto,
            bg=fondo,
            fg=color
        )