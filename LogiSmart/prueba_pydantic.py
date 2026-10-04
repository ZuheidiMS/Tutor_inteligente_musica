from models.incidente_model import IncidenteLLM


def main():
    print("=" * 60)
    print("PRUEBA DE VALIDACIÓN PYDANTIC")
    print("=" * 60)

    datos = {
        "categoria": "materiales_peligrosos",
        "prioridad": "critica",
        "entidades": [
            "CAM-102",
            "muelle 3"
        ],
        "resumen": (
            "Se reporta un derrame de material químico "
            "que requiere atención inmediata."
        )
    }

    incidente = IncidenteLLM(**datos)

    print("VALIDACIÓN: OK")
    print()
    print("Datos validados:")
    print(incidente.model_dump())

    print()
    print("=" * 60)
    print("PRUEBA FINALIZADA CORRECTAMENTE")
    print("=" * 60)


if __name__ == "__main__":
    main()