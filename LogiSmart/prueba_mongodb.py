from pymongo import MongoClient

try:
    # 1. Conexión al servidor MongoDB
    cliente = MongoClient(
        "mongodb://localhost:27017/",
        serverSelectionTimeoutMS=5000
    )

    # Comprobar que el servidor responde
    cliente.admin.command("ping")
    print("===================================")
    print(" CONEXIÓN A MONGODB: OK")
    print("===================================")

    # 2. Seleccionar base de datos
    db = cliente["logismart"]

    # 3. Seleccionar colección de prueba
    coleccion = db["prueba"]

    # 4. Insertar documento
    documento = {
        "tipo": "prueba",
        "mensaje": "LogiSmart conectado correctamente",
        "activo": True
    }

    resultado_insertar = coleccion.insert_one(documento)

    print("\n[1] INSERTAR: OK")
    print(f"ID generado: {resultado_insertar.inserted_id}")

    # 5. Consultar documento
    documento_encontrado = coleccion.find_one(
        {"_id": resultado_insertar.inserted_id}
    )

    print("\n[2] CONSULTAR: OK")
    print(f"Documento encontrado: {documento_encontrado}")

    # 6. Actualizar documento
    resultado_actualizar = coleccion.update_one(
        {"_id": resultado_insertar.inserted_id},
        {"$set": {"activo": False}}
    )

    print("\n[3] ACTUALIZAR: OK")
    print(f"Documentos modificados: {resultado_actualizar.modified_count}")

    # 7. Eliminar documento de prueba
    resultado_eliminar = coleccion.delete_one(
        {"_id": resultado_insertar.inserted_id}
    )

    print("\n[4] ELIMINAR: OK")
    print(f"Documentos eliminados: {resultado_eliminar.deleted_count}")

    print("\n===================================")
    print(" PRUEBA CRUD COMPLETADA")
    print("===================================")

    cliente.close()

except Exception as e:
    print("\n===================================")
    print(" ERROR EN LA PRUEBA DE MONGODB")
    print("===================================")
    print(f"Detalle: {e}")