from database.mongodb import MongoDB
from database.riesgos_repository import RiesgosRepository


def main():
    print("=" * 70)
    print("PRUEBA CRUD DE RIESGOS ÉTICOS")
    print("=" * 70)

    mongo = MongoDB()
    db = mongo.conectar()

    if db is None:
        print("No fue posible conectar con MongoDB.")
        return

    riesgos = RiesgosRepository(db)

    # ==========================================================
    # CREAR
    # ==========================================================

    print("\n--- CREAR RIESGO ---")

    riesgo_id = riesgos.crear(
        modulo="Asistente LLM",
        descripcion=(
            "El modelo puede generar información incorrecta "
            "sobre la clasificación de un incidente."
        ),
        categoria="alucinacion_llm",
        probabilidad=3,
        impacto=5,
        mitigacion=(
            "Validar la respuesta del LLM mediante reglas, "
            "Pydantic y revisión humana."
        )
    )

    print(f"Riesgo creado correctamente.")
    print(f"ID: {riesgo_id}")

    # ==========================================================
    # LISTAR
    # ==========================================================

    print("\n--- LISTAR RIESGOS ---")

    lista = riesgos.listar()

    print(f"Total de riesgos: {len(lista)}")

    for riesgo in lista:
        print(
            f"- {riesgo['descripcion']} | "
            f"Nivel: {riesgo['nivel_riesgo']} | "
            f"Estado: {riesgo['estado']}"
        )

    # ==========================================================
    # OBTENER POR ID
    # ==========================================================

    print("\n--- OBTENER RIESGO POR ID ---")

    riesgo = riesgos.obtener_por_id(riesgo_id)

    if riesgo:
        print(f"ID: {riesgo['_id']}")
        print(f"Módulo: {riesgo['modulo']}")
        print(f"Categoría: {riesgo['categoria']}")
        print(f"Probabilidad: {riesgo['probabilidad']}")
        print(f"Impacto: {riesgo['impacto']}")
        print(f"Nivel: {riesgo['nivel_riesgo']}")
        print(f"Estado: {riesgo['estado']}")
    else:
        print("No se encontró el riesgo.")

    # ==========================================================
    # ACTUALIZAR
    # ==========================================================

    print("\n--- ACTUALIZAR RIESGO ---")

    actualizado = riesgos.actualizar(
        riesgo_id=riesgo_id,
        modulo="Asistente LLM",
        descripcion=(
            "El modelo puede generar información incorrecta "
            "durante la clasificación de incidentes."
        ),
        categoria="alucinacion_llm",
        probabilidad=2,
        impacto=5,
        mitigacion=(
            "Aplicar validación Pydantic, comparación con reglas "
            "y revisión humana cuando exista discrepancia."
        ),
        estado="mitigado"
    )

    print(f"Actualización realizada: {actualizado}")

    # ==========================================================
    # VERIFICAR HISTÓRICO
    # ==========================================================

    print("\n--- HISTÓRICO ---")

    riesgo_actualizado = riesgos.obtener_por_id(riesgo_id)

    if riesgo_actualizado:
        print(
            f"Registros históricos: "
            f"{len(riesgo_actualizado.get('historico', []))}"
        )

        print(
            f"Nuevo nivel de riesgo: "
            f"{riesgo_actualizado['nivel_riesgo']}"
        )

        print(
            f"Nuevo estado: "
            f"{riesgo_actualizado['estado']}"
        )

    # ==========================================================
    # ELIMINAR
    # ==========================================================

    print("\n--- ELIMINAR RIESGO ---")

    eliminado = riesgos.eliminar(riesgo_id)

    print(f"Eliminación realizada: {eliminado}")

    mongo.cerrar()

    print("\n" + "=" * 70)
    print("PRUEBA CRUD DE RIESGOS FINALIZADA")
    print("=" * 70)


if __name__ == "__main__":
    main()