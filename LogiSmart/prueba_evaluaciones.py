from database.mongodb import MongoDB
from database.evaluaciones_repository import EvaluacionesLLMRepository


def main():
    print("=" * 60)
    print("PRUEBA DEL REPOSITORIO DE EVALUACIONES LLM")
    print("=" * 60)

    mongo = MongoDB()
    db = mongo.conectar()

    if db is None:
        print("No fue posible conectar con MongoDB.")
        return

    repositorio = EvaluacionesLLMRepository(db)

    evaluacion_id = repositorio.crear(
        prompt="Clasifica el siguiente incidente: derrame químico en CAM-102.",
        response='{"categoria":"materiales_peligrosos","prioridad":"alta"}',
        model="llama3.2",
        latency_ms=25900.78,
        matched_rules=False,
        clasificacion_llm={
            "categoria": "materiales_peligrosos",
            "prioridad": "alta"
        },
        clasificacion_reglas={
            "categoria": "materiales_peligrosos",
            "prioridad": "critica"
        },
        clasificacion_final={
            "categoria": "materiales_peligrosos",
            "prioridad": "critica"
        },
        requiere_revision_humana=True
    )

    print("\nEvaluación creada correctamente.")
    print(f"ID: {evaluacion_id}")

    evaluaciones = repositorio.listar()

    print(f"\nTotal de evaluaciones: {len(evaluaciones)}")

    print("\nÚltima evaluación:")
    print(evaluaciones[0])

    evaluacion = repositorio.obtener_por_id(
        evaluacion_id
    )

    print("\nEvaluación recuperada por ID:")
    print(evaluacion)

    mongo.cerrar()

    print("\n" + "=" * 60)
    print("PRUEBA FINALIZADA CORRECTAMENTE")
    print("=" * 60)


if __name__ == "__main__":
    main()