
import tkinter as tk

def probar():
    texto = entrada.get()
    resultado.config(text=f"Escribiste: {texto}")

ventana = tk.Tk()

ventana.title("Prueba de teclado - LogiSmart")
ventana.geometry("600x300")

tk.Label(
    ventana,
    text="PRUEBA DEL TECLADO",
    font=("Segoe UI", 18, "bold")
).pack(pady=30)

entrada = tk.Entry(
    ventana,
    font=("Segoe UI", 16),
    width=40,
    bg="white",
    fg="black",
    insertbackground="black",
    relief="solid",
    bd=2
)

entrada.pack(pady=10)

boton = tk.Button(
    ventana,
    text="Probar",
    font=("Segoe UI", 12),
    command=probar
)

boton.pack(pady=10)

resultado = tk.Label(
    ventana,
    text="",
    font=("Segoe UI", 12)
)

resultado.pack(pady=10)

ventana.after(500, lambda: entrada.focus_force())

ventana.mainloop()

