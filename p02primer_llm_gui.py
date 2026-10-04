# ============================================================
# PRACTICA 2
# TUTOR INTELIGENTE DE MUSICA CON LLM
# ============================================================

import tkinter as tk
from tkinter import messagebox
import ollama


# ------------------------------------------------------------
# 1. CONFIGURACION DEL MODELO
# ------------------------------------------------------------

MODELO = "llama3.2"


# ------------------------------------------------------------
# 2. CONFIGURACION DEL SISTEMA
# ------------------------------------------------------------

mensaje_sistema = """
Eres un tutor experto en música y teoría musical.

Tu función es ayudar a estudiantes y personas interesadas
en aprender sobre música de manera clara, sencilla y práctica.

Debes:

1. Explicar conceptos musicales de forma clara y comprensible.
2. Explicar teoría musical paso a paso.
3. Ayudar con escalas, acordes, notas, intervalos y ritmo.
4. Explicar diferentes géneros y estilos musicales.
5. Proporcionar información sobre instrumentos musicales.
6. Explicar conceptos de composición y armonía.
7. Utilizar ejemplos musicales sencillos cuando sea posible.
8. Adaptar tus explicaciones al nivel del usuario.
9. Si el usuario comete un error musical, explicar cómo corregirlo.
10. No limitarte a proporcionar una respuesta; explica el concepto
    para que el usuario pueda aprender.
11. Mantener un lenguaje amigable y educativo.
12. Si una pregunta puede tener varias respuestas dependiendo
    del género o contexto musical, explicarlo.
"""


# ------------------------------------------------------------
# 3. HISTORIAL
# ------------------------------------------------------------

mensajes = [
    {
        "role": "system",
        "content": mensaje_sistema
    }
]


# ------------------------------------------------------------
# 4. FUNCION PARA MOSTRAR MENSAJES
# ------------------------------------------------------------

def agregar_mensaje(remitente, texto):

    area_chat.config(state="normal")

    area_chat.insert(
        tk.END,
        remitente + "\n",
        "remitente"
    )

    area_chat.insert(
        tk.END,
        texto + "\n\n",
        "mensaje"
    )

    area_chat.config(state="disabled")

    area_chat.see(tk.END)


# ------------------------------------------------------------
# 5. ESTADO
# ------------------------------------------------------------

def mostrar_estado(texto):

    etiqueta_estado.config(
        text=texto
    )


# ------------------------------------------------------------
# 6. PREGUNTAR AL TUTOR
# ------------------------------------------------------------

def preguntar():

    pregunta = entrada_pregunta.get().strip()

    if not pregunta:

        messagebox.showwarning(
            "Pregunta vacía",
            "Escribe una pregunta de música."
        )

        entrada_pregunta.focus_set()

        return


    # Mostrar pregunta

    agregar_mensaje(
        "TÚ",
        pregunta
    )


    # Guardar pregunta

    mensajes.append(
        {
            "role": "user",
            "content": pregunta
        }
    )


    mostrar_estado(
        "🎵 El tutor está pensando..."
    )

    boton_preguntar.config(
        state="disabled"
    )

    ventana.update_idletasks()


    # --------------------------------------------------------
    # CONECTAR CON OLLAMA
    # --------------------------------------------------------

    try:

        respuesta = ollama.chat(
            model=MODELO,
            messages=mensajes
        )

    except Exception as error:

        mensajes.pop()

        mostrar_estado(
            "Error de conexión con Ollama."
        )

        boton_preguntar.config(
            state="normal"
        )

        messagebox.showerror(
            "Error",
            "No fue posible comunicarse con Ollama.\n\n"
            "Verifica que Ollama esté ejecutándose.\n\n"
            f"Detalle:\n{error}"
        )

        entrada_pregunta.focus_set()

        return


    # --------------------------------------------------------
    # OBTENER RESPUESTA
    # --------------------------------------------------------

    contenido = respuesta["message"]["content"]


    # Guardar respuesta

    mensajes.append(
        {
            "role": "assistant",
            "content": contenido
        }
    )


    # Mostrar respuesta

    agregar_mensaje(
        "🎵 TUTOR DE MÚSICA",
        contenido
    )


    mostrar_estado(
        "✨ Listo. Puedes hacer otra pregunta."
    )

    boton_preguntar.config(
        state="normal"
    )

    entrada_pregunta.delete(
        0,
        tk.END
    )

    entrada_pregunta.focus_set()


# ------------------------------------------------------------
# 7. ENTER PARA PREGUNTAR
# ------------------------------------------------------------

def presionar_enter(event):

    preguntar()


# ------------------------------------------------------------
# 8. LIMPIAR HISTORIAL
# ------------------------------------------------------------

def limpiar_historial():

    global mensajes

    respuesta = messagebox.askyesno(
        "Limpiar historial",
        "¿Deseas borrar toda la conversación?"
    )

    if not respuesta:
        return


    mensajes = [
        {
            "role": "system",
            "content": mensaje_sistema
        }
    ]


    area_chat.config(
        state="normal"
    )

    area_chat.delete(
        "1.0",
        tk.END
    )

    area_chat.config(
        state="disabled"
    )


    agregar_mensaje(
        "🎵 TUTOR DE MÚSICA",
        "¡Hola! Soy tu tutor experto en música.\n\n"
        "Puedes preguntarme sobre teoría musical, "
        "instrumentos, acordes, escalas, géneros, "
        "ritmo, armonía o composición.\n\n"
        "¿Qué te gustaría aprender?"
    )


    mostrar_estado(
        "✨ Historial limpiado."
    )

    entrada_pregunta.focus_set()


# ============================================================
# VENTANA PRINCIPAL
# ============================================================

ventana = tk.Tk()

ventana.title(
    "🎵 Tutor Inteligente de Música"
)

ventana.geometry(
    "950x700"
)

ventana.minsize(
    750,
    550
)


# ------------------------------------------------------------
# COLORES LILA / MORADO
# ------------------------------------------------------------

MORADO_OSCURO = "#6A1B9A"
MORADO = "#8E44AD"
LILA = "#EDE7F6"
LILA_CLARO = "#F8F5FC"
LILA_BOTON = "#9C6ADE"
BLANCO = "#FFFFFF"
TEXTO = "#3D2352"
GRIS = "#7B6F83"


ventana.configure(
    bg=LILA_CLARO
)


# ============================================================
# ENCABEZADO
# ============================================================

marco_encabezado = tk.Frame(
    ventana,
    bg=MORADO_OSCURO,
    height=105
)

marco_encabezado.pack(
    fill="x"
)

marco_encabezado.pack_propagate(
    False
)


titulo = tk.Label(
    marco_encabezado,
    text="🎵 Tutor Inteligente de Música",
    font=("Arial", 25, "bold"),
    bg=MORADO_OSCURO,
    fg=BLANCO
)

titulo.pack(
    pady=(18, 2)
)


subtitulo = tk.Label(
    marco_encabezado,
    text="Aprende música de una manera fácil y divertida",
    font=("Arial", 11),
    bg=MORADO_OSCURO,
    fg="#E8DDF0"
)

subtitulo.pack()


# ============================================================
# INFORMACION
# ============================================================

marco_info = tk.Frame(
    ventana,
    bg=LILA_CLARO
)

marco_info.pack(
    fill="x",
    padx=25,
    pady=(15, 5)
)


etiqueta_modelo = tk.Label(
    marco_info,
    text=f"🤖 Modelo: {MODELO}",
    font=("Arial", 10, "bold"),
    bg=LILA_CLARO,
    fg=MORADO_OSCURO
)

etiqueta_modelo.pack(
    side="left"
)


etiqueta_especialidad = tk.Label(
    marco_info,
    text="🎼 Especialidad: Música y teoría musical",
    font=("Arial", 10),
    bg=LILA_CLARO,
    fg=MORADO
)

etiqueta_especialidad.pack(
    side="right"
)


# ============================================================
# AREA DE CHAT
# ============================================================

marco_chat = tk.Frame(
    ventana,
    bg=BLANCO,
    bd=1,
    relief="solid"
)

marco_chat.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=10
)


area_chat = tk.Text(
    marco_chat,
    wrap="word",
    font=("Arial", 12),
    bg=BLANCO,
    fg=TEXTO,
    padx=18,
    pady=18,
    relief="flat",
    state="disabled"
)

area_chat.pack(
    side="left",
    fill="both",
    expand=True
)


# ------------------------------------------------------------
# SCROLL
# ------------------------------------------------------------

scroll_chat = tk.Scrollbar(
    marco_chat,
    command=area_chat.yview
)

scroll_chat.pack(
    side="right",
    fill="y"
)

area_chat.config(
    yscrollcommand=scroll_chat.set
)


# ------------------------------------------------------------
# ESTILOS DEL TEXTO
# ------------------------------------------------------------

area_chat.tag_config(
    "remitente",
    font=("Arial", 11, "bold"),
    foreground=MORADO_OSCURO
)

area_chat.tag_config(
    "mensaje",
    font=("Arial", 12),
    foreground=TEXTO
)


# ============================================================
# AREA DE PREGUNTA
# ============================================================

marco_entrada = tk.Frame(
    ventana,
    bg=LILA_CLARO
)

marco_entrada.pack(
    fill="x",
    padx=25,
    pady=(5, 5)
)


entrada_pregunta = tk.Entry(
    marco_entrada,
    font=("Arial", 13),
    bg=BLANCO,
    fg=TEXTO,
    insertbackground=MORADO_OSCURO,
    relief="solid",
    bd=1
)

entrada_pregunta.pack(
    side="left",
    fill="x",
    expand=True,
    ipady=11,
    padx=(0, 10)
)


# ============================================================
# BOTON PREGUNTAR
# ============================================================

boton_preguntar = tk.Button(
    marco_entrada,
    text="🎵 Preguntar",
    font=("Arial", 11, "bold"),
    bg=MORADO,
    fg=BLANCO,
    activebackground=MORADO_OSCURO,
    activeforeground=BLANCO,
    relief="flat",
    padx=22,
    pady=10,
    cursor="hand2",
    command=preguntar
)

boton_preguntar.pack(
    side="right"
)


# ============================================================
# ENTER
# ============================================================

entrada_pregunta.bind(
    "<Return>",
    presionar_enter
)


# ============================================================
# PARTE INFERIOR
# ============================================================

marco_inferior = tk.Frame(
    ventana,
    bg=LILA_CLARO
)

marco_inferior.pack(
    fill="x",
    padx=25,
    pady=(0, 12)
)


boton_limpiar = tk.Button(
    marco_inferior,
    text="🗑 Limpiar historial",
    font=("Arial", 10),
    bg=LILA,
    fg=MORADO_OSCURO,
    activebackground="#D1C4E9",
    activeforeground=MORADO_OSCURO,
    relief="flat",
    padx=15,
    pady=7,
    cursor="hand2",
    command=limpiar_historial
)

boton_limpiar.pack(
    side="left"
)


etiqueta_estado = tk.Label(
    marco_inferior,
    text="✨ Listo para ayudarte.",
    font=("Arial", 10),
    bg=LILA_CLARO,
    fg=GRIS
)

etiqueta_estado.pack(
    side="right"
)


# ============================================================
# MENSAJE INICIAL
# ============================================================

agregar_mensaje(
    "🎵 TUTOR DE MÚSICA",
    "¡Hola! Soy tu tutor experto en música.\n\n"
    "Puedo ayudarte a aprender sobre:\n\n"
    "🎼 Notas musicales\n"
    "🎹 Escalas y acordes\n"
    "🥁 Ritmo\n"
    "🎸 Instrumentos\n"
    "🎧 Géneros musicales\n"
    "🎶 Armonía\n"
    "✍️ Composición\n"
    "📚 Historia de la música\n\n"
    "¿Qué te gustaría aprender?"
)


# ============================================================
# ENFOCAR CUADRO DE TEXTO
# ============================================================

entrada_pregunta.focus_set()


# ============================================================
# INICIAR PROGRAMA
# ============================================================

ventana.mainloop()