from database.mongodb import MongoDB


mongo = MongoDB()

db = mongo.conectar()

if db is not None:
    coleccion = mongo.obtener_coleccion("prueba_modular")

    resultado = coleccion.insert_one({
        "tipo": "prueba",
        "mensaje": "Conexión modular de LogiSmart"
    })

    print("\nDocumento insertado correctamente.")
    print(f"ID: {resultado.inserted_id}")

    mongo.cerrar()
else:
    print("\nNo fue posible conectar con MongoDB.")