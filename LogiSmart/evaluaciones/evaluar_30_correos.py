"""
Evaluación de reglas, LLM e híbrido sobre 30 correos etiquetados.
"""

import json
import time
from collections import Counter

from services.hybrid_classifier import HybridClassifier


CORREOS = [
    ("Derrame químico", "Se reporta derrame de químico inflamable en andén.", "materiales_peligrosos", "critica"),
    ("Carga peligrosa", "Camión transporta sustancia peligrosa sin autorización.", "materiales_peligrosos", "critica"),
    ("Químico", "Se detectó material químico derramado.", "materiales_peligrosos", "critica"),
    ("Exceso peso", "La báscula indica 5 toneladas por encima.", "sobrepeso", "alta"),
    ("Carga excedida", "El camión supera el peso permitido.", "sobrepeso", "alta"),
    ("Báscula", "Peso superior al límite establecido.", "sobrepeso", "alta"),
    ("Acceso", "CAM-102 intentó entrar sin autorización.", "acceso_no_autorizado", "alta"),
    ("Entrada", "Unidad sin permiso intentó ingresar.", "acceso_no_autorizado", "alta"),
    ("Placa bloqueada", "La placa no está autorizada para ingresar.", "acceso_no_autorizado", "alta"),
    ("Servidor", "El servidor presenta una falla.", "falla_hardware", "media"),
    ("Computadora", "Equipo de control dejó de funcionar.", "falla_hardware", "alta"),
    ("Sensor", "Sensor de acceso no responde.", "falla_hardware", "alta"),
    ("Software", "El sistema de control presenta errores.", "falla_software", "media"),
    ("Aplicación", "La aplicación dejó de responder.", "falla_software", "media"),
    ("Sistema", "El software presenta errores de operación.", "falla_software", "media"),
    ("Conductor", "El conductor presenta somnolencia.", "somnolencia_conductor", "critica"),
    ("Sueño", "Operador reporta cansancio extremo y sueño.", "somnolencia_conductor", "critica"),
    ("Fatiga", "Se observa fatiga en el conductor.", "somnolencia_conductor", "alta"),
    ("Químico", "Producto inflamable fue derramado.", "materiales_peligrosos", "critica"),
    ("Peso", "Carga excede el límite permitido.", "sobrepeso", "alta"),
    ("Acceso", "Persona sin permiso intenta entrar.", "acceso_no_autorizado", "alta"),
    ("Servidor", "Servidor físico dejó de responder.", "falla_hardware", "alta"),
    ("Programa", "Programa presenta un error.", "falla_software", "media"),
    ("Cansancio", "Conductor reporta sueño.", "somnolencia_conductor", "alta"),
    ("Material", "Sustancia peligrosa fue encontrada.", "materiales_peligrosos", "critica"),
    ("Báscula", "La unidad supera el peso permitido.", "sobrepeso", "alta"),
    ("Autorización", "Unidad sin autorización de acceso.", "acceso_no_autorizado", "alta"),
    ("Equipo", "Equipo físico presenta una falla.", "falla_hardware", "alta"),
    ("Software", "Error crítico en el sistema.", "falla_software", "alta"),
    ("Conductor", "Conductor se queda dormido durante operación.", "somnolencia_conductor", "critica"),
]


def exactitud(real, predicciones):
    correctas = sum(
        r == p
        for r, p in zip(real, predicciones)
    )

    return correctas / len(real)


def matriz_confusion(real, predicciones):

    categorias = sorted(
        set(real)
    )

    matriz = {
        categoria: Counter()
        for categoria in categorias
    }

    for esperado, obtenido in zip(
        real,
        predicciones
    ):
        matriz[esperado][obtenido] += 1

    return matriz


def main():

    classifier = HybridClassifier()

    reglas_real = []
    reglas_pred = []

    llm_real = []
    llm_pred = []
    llm_latencias = []

    hibrido_real = []
    hibrido_pred = []
    hibrido_latencias = []

    for _, correo, categoria_real, _ in CORREOS:

        reglas_real.append(
            categoria_real
        )

        resultado_reglas = (
            classifier.clasificar_por_reglas(
                correo
            )
        )

        reglas_pred.append(
            resultado_reglas["categoria"]
        )

        inicio_llm = time.perf_counter()

        try:
            resultado_llm = classifier.clasificar_con_llm(
                correo
            )

            latencia_llm = (
                time.perf_counter() - inicio_llm
            ) * 1000

            clasificacion_llm = (
                resultado_llm["clasificacion"]
            )

            llm_pred.append(
                clasificacion_llm["categoria"]
            )

        except Exception:
            latencia_llm = 0
            llm_pred.append(
                "otro"
            )

        llm_latencias.append(
            latencia_llm
        )

        inicio_hibrido = time.perf_counter()

        try:
            resultado_hibrido = (
                classifier.clasificar(
                    correo
                )
            )

            hibrido_pred.append(
                resultado_hibrido[
                    "clasificacion"
                ]["categoria"]
            )

        except Exception:

            hibrido_pred.append(
                resultado_reglas["categoria"]
            )

        hibrido_latencias.append(
            (
                time.perf_counter()
                - inicio_hibrido
            ) * 1000
        )

        hibrido_real.append(
            categoria_real
        )

    resultados = {
        "total": len(CORREOS),

        "reglas": {
            "accuracy": exactitud(
                reglas_real,
                reglas_pred
            )
        },

        "llm": {
            "accuracy": exactitud(
                reglas_real,
                llm_pred
            ),
            "latencia_promedio_ms": (
                sum(llm_latencias)
                / len(llm_latencias)
            )
        },

        "hibrido": {
            "accuracy": exactitud(
                hibrido_real,
                hibrido_pred
            ),
            "latencia_promedio_ms": (
                sum(hibrido_latencias)
                / len(hibrido_latencias)
            ),
            "matriz_confusion": matriz_confusion(
                hibrido_real,
                hibrido_pred
            )
        }
    }

    print(
        json.dumps(
            resultados,
            indent=4,
            ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()