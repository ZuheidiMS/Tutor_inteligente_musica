from database.mongodb import MongoDB
from database.evaluaciones_repository import EvaluacionesLLMRepository
from services.hybrid_classifier import HybridClassifier


def main():
    print("=" * 70)
    print("PRUEBA DEL CLASIFICADOR HÍBRIDO")
    print("=" * 70)

    mongo = MongoDB()
    db = mongo.conectar()

    if db is None:
        print("No fue posible conectar con MongoDB.")
        return

    repositorio = EvaluacionesLLMRepository(db)

    clasificador = HybridClassifier(
        model="llama3.2",
        max_reintentos=1,
        evaluaciones_repository=repositorio
    )

    asunto = "URGENTE: derrame en CAM-102"

    cuerpo = (
        "Se reporta un derrame de material químico "
        "en el muelle 3. El camión CAM-102 "
        "requiere atención inmediata."
    )

    resultado = clasificador.clasificar(
        asunto=asunto,
        cuerpo=cuerpo
    )

    print("\n--- CLASIFICACIÓN FINAL ---")
    print(resultado["clasificacion"])

    print("\n--- CLASIFICACIÓN POR REGLAS ---")
    print(resultado["clasificacion_reglas"])

    print("\n--- CLASIFICACIÓN DEL LLM ---")
    print(resultado["clasificacion_llm"])

    print("\n--- INFORMACIÓN DEL PROCESO ---")
    print(f"Fuente: {resultado['fuente']}")
    print(f"Modelo: {resultado['modelo']}")
    print(f"Latencia: {resultado['latencia_ms']} ms")

    print(
        f"¿Coincide con reglas?: "
        f"{resultado['coincide_con_reglas']}"
    )

    print(
        f"¿Requiere revisión humana?: "
        f"{resultado['requiere_revision_humana']}"
    )

    print("\n--- RESPUESTA ORIGINAL DEL LLM ---")
    print(resultado["respuesta_original"])

    evaluacion = clasificador.preparar_evaluacion(
        asunto=asunto,
        cuerpo=cuerpo,
        resultado=resultado
    )

    print("\n--- DATOS PARA EVALUACIÓN EN MONGODB ---")
    print(evaluacion)

    evaluacion_id = clasificador.guardar_evaluacion(
        asunto=asunto,
        cuerpo=cuerpo,
        resultado=resultado
    )

    print("\n--- EVALUACIÓN GUARDADA AUTOMÁTICAMENTE ---")
    print(f"ID de evaluación: {evaluacion_id}")

    mongo.cerrar()

    print("\n" + "=" * 70)
    print("PRUEBA FINALIZADA")
    print("=" * 70)


if __name__ == "__main__":
    main()