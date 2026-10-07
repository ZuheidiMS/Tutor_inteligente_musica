from logiuncodigo import procesar_incidente


resultado = procesar_incidente(
    remitente="operador@logismart.com",
    asunto="URGENTE: derrame en CAM-102",
    cuerpo=(
        "Se reporta un derrame de material químico "
        "en el muelle 3. El camión CAM-102 requiere atención inmediata."
    ),
    simulacion=True,
    guardar=True
)

print("=" * 60)
print("RESULTADO DEL CLASIFICADOR")
print("=" * 60)
print(resultado)