from services.hybrid_classifier import HybridClassifier


def main():
    print("=" * 60)
    print("PRUEBA DEL CLASIFICADOR HÍBRIDO CON OLLAMA")
    print("=" * 60)

    clasificador = HybridClassifier(
        model="llama3.2"
    )

    resultado = clasificador.clasificar(
        asunto="URGENTE: derrame en CAM-102",
        cuerpo=(
            "Se reporta un derrame de material químico "
            "en el muelle 3. El camión CAM-102 "
            "requiere atención inmediata."
        )
    )

    print("\nCLASIFICACIÓN VALIDADA:")
    print(resultado["clasificacion"])

    print(f"\nModelo: {resultado['modelo']}")
    print(f"Latencia: {resultado['latencia_ms']} ms")

    print("\nRESPUESTA ORIGINAL DEL LLM:")
    print(resultado["respuesta_original"])

    print("\n" + "=" * 60)
    print("PRUEBA FINALIZADA CORRECTAMENTE")
    print("=" * 60)


if __name__ == "__main__":
    main()