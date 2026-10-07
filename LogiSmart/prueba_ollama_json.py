import json
import urllib.request

from pydantic import BaseModel, ValidationError


OLLAMA_URL = "http://localhost:11434/api/generate"


# Modelo que define exactamente la estructura
# que necesitamos para clasificar un incidente.
class ClasificacionIncidente(BaseModel):
    categoria: str
    prioridad: str
    entidades: dict
    resumen: str


correo = """
URGENTE: Se detectó un derrame de materiales peligrosos
en el andén 3. El camión CAM-102 está involucrado.
El operador solicita inspección inmediata.
"""


prompt = f"""
Analiza el siguiente correo de un sistema logístico.

Debes responder ÚNICAMENTE con un objeto JSON válido.
No agregues explicaciones, Markdown ni texto fuera del JSON.

El JSON debe tener exactamente estas propiedades:

{{
  "categoria": "materiales_peligrosos",
  "prioridad": "critica",
  "entidades": {{}},
  "resumen": "..."
}}

Categorías permitidas:
- materiales_peligrosos
- acceso
- mantenimiento
- documentacion
- otro

Prioridades permitidas:
- critica
- alta
- media
- baja

Correo:
{correo}
"""


datos = {
    "model": "llama3.2",
    "prompt": prompt,
    "format": "json",
    "stream": False
}


try:
    solicitud = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(datos).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(solicitud, timeout=120) as respuesta:
        resultado = json.loads(
            respuesta.read().decode("utf-8")
        )

    respuesta_llm = resultado.get("response", "")

    print("===================================")
    print(" RESPUESTA DE OLLAMA")
    print("===================================")
    print(respuesta_llm)

    # Convertimos la respuesta del LLM
    # de texto a objeto Python.
    datos_json = json.loads(respuesta_llm)

    # Validamos la estructura utilizando Pydantic.
    clasificacion = ClasificacionIncidente.model_validate(
        datos_json
    )

    print("\n===================================")
    print(" VALIDACIÓN PYDANTIC: OK")
    print("===================================")

    print(f"Categoría: {clasificacion.categoria}")
    print(f"Prioridad: {clasificacion.prioridad}")
    print(f"Entidades: {clasificacion.entidades}")
    print(f"Resumen: {clasificacion.resumen}")

except json.JSONDecodeError as e:
    print("\n===================================")
    print(" ERROR: JSON INVÁLIDO")
    print("===================================")
    print(f"Detalle: {e}")

except ValidationError as e:
    print("\n===================================")
    print(" ERROR: FALLÓ PYDANTIC")
    print("===================================")
    print(e)

except Exception as e:
    print("\n===================================")
    print(" ERROR GENERAL")
    print("===================================")
    print(f"Detalle: {e}")