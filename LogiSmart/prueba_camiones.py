from database.repositories import CamionesRepository


repo = CamionesRepository()

print("===================================")
print(" PRUEBA CRUD - CAMIONES")
print("===================================")

camion_id = repo.crear(
    placa="ABC-123-D",
    camion_id="CAM-001",
    empresa="LogiTransportes",
    autorizado=True,
    certificacion_conductor=True
)

print(f"Camión creado: {camion_id}")

camion = repo.buscar_por_placa("ABC-123-D")

print("\nCamión encontrado:")
print(camion)

actualizado = repo.actualizar(
    placa="ABC-123-D",
    empresa="LogiTransportes S.A. de C.V.",
    autorizado=True,
    certificacion_conductor=False
)

print(f"\nActualización realizada: {actualizado}")

camion = repo.buscar_por_placa("ABC-123-D")

print("\nCamión después de actualizar:")
print(camion)

camiones = repo.obtener_todos()

print(f"\nTotal de camiones: {len(camiones)}")