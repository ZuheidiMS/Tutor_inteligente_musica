import json
import urllib.request

OLLAMA_URL = "http://localhost:11434/api/generate"

datos = {
    "model": "llama3.2",
    "prompt": "Responde brevemente en español: ¿Qué es un sistema de inteligencia artificial?",
    "stream": False
}

try:
    solicitud = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(datos).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(solicitud, timeout=60) as respuesta:
        resultado = json.loads(respuesta.read().decode("utf-8"))

    print("===================================")
    print(" CONEXIÓN CON OLLAMA: OK")
    print("===================================")
    print(f"Modelo utilizado: {resultado.get('model')}")
    print("\nRespuesta del modelo:")
    print(resultado.get("response", ""))

except Exception as e:
    print("===================================")
    print(" ERROR AL CONECTAR CON OLLAMA")
    print("===================================")
    print(f"Detalle: {e}")