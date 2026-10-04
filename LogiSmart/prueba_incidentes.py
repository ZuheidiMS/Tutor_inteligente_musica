from database.incidentes_repository import IncidentesRepository


repo = IncidentesRepository()

print("=" * 50)
print(" PRUEBA CRUD - INCIDENTES")
print("=" * 50)


# 1. CREAR
incidente_id = repo.crear(
    correo_original=(
        "Buen día, el camión CAM-102 presentó una "
        "falla durante el ingreso a la terminal."
    ),
    categoria="falla_mecanica",
    prioridad="alta",
    entidades=["CAM-102", "terminal"],
    resumen="Se reporta una falla mecánica durante el ingreso.",
    estado="nuevo"
)

print(f"\nIncidente creado: {incidente_id}")


# 2. BUSCAR
incidente = repo.buscar_por_id(incidente_id)

print("\nIncidente encontrado:")
print(incidente)


# 3. ACTUALIZAR
actualizado = repo.actualizar(
    incidente_id=incidente_id,
    prioridad="critica",
    estado="en_atencion",
    resumen=(
        "Se reporta una falla mecánica durante el ingreso. "
        "El incidente requiere atención inmediata."
    )
)

print(f"\nActualización realizada: {actualizado}")


# 4. CONSULTAR DESPUÉS DE ACTUALIZAR
incidente = repo.buscar_por_id(incidente_id)

print("\nIncidente después de actualizar:")
print(incidente)


# 5. OBTENER TODOS
incidentes = repo.obtener_todos()

print(f"\nTotal de incidentes: {len(incidentes)}")


print("\n" + "=" * 50)
print(" PRUEBA CRUD FINALIZADA")
print("=" * 50)