"""
Servicio de comunicación con Ollama para LogiSmart.

Este módulo se encarga únicamente de comunicarse con el LLM local.
La lógica de negocio y la interfaz gráfica no deben comunicarse
directamente con Ollama.
"""

import json
import time
from typing import Any, Dict, Optional

import requests


class OllamaService:
    """Cliente sencillo para consumir un modelo local de Ollama."""

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.generate_url = f"{self.base_url}/api/generate"

    def generar(
        self,
        prompt: str,
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        Envía un prompt al modelo de Ollama.

        Regresa:
            {
                "respuesta": str,
                "modelo": str,
                "latencia_ms": float
            }
        """

        if not prompt.strip():
            raise ValueError("El prompt no puede estar vacío.")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        inicio = time.perf_counter()

        try:
            respuesta = requests.post(
                self.generate_url,
                json=payload,
                timeout=120
            )

            respuesta.raise_for_status()

            datos = respuesta.json()

        except requests.exceptions.ConnectionError as error:
            raise ConnectionError(
                "No fue posible conectarse con Ollama. "
                "Verifica que Ollama esté ejecutándose."
            ) from error

        except requests.exceptions.Timeout as error:
            raise TimeoutError(
                "Ollama tardó demasiado en responder."
            ) from error

        except requests.exceptions.RequestException as error:
            raise RuntimeError(
                f"Error al comunicarse con Ollama: {error}"
            ) from error

        except ValueError as error:
            raise RuntimeError(
                "Ollama devolvió una respuesta que no es JSON válido."
            ) from error

        fin = time.perf_counter()

        latencia_ms = round(
            (fin - inicio) * 1000,
            2
        )

        texto = datos.get("response", "").strip()

        if not texto:
            raise RuntimeError(
                "Ollama no devolvió contenido en la respuesta."
            )

        return {
            "respuesta": texto,
            "modelo": self.model,
            "latencia_ms": latencia_ms
        }

    def generar_json(
        self,
        prompt: str,
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        Solicita una respuesta al LLM y la convierte a JSON.

        Si el modelo devuelve texto que no es JSON válido,
        se genera un error para que la capa superior pueda
        realizar un reintento o utilizar el fallback por reglas.
        """

        resultado = self.generar(
            prompt=prompt,
            temperature=temperature
        )

        texto = resultado["respuesta"]

        try:
            datos_json = json.loads(texto)

        except json.JSONDecodeError as error:
            raise ValueError(
                "El LLM no devolvió un JSON válido."
            ) from error

        if not isinstance(datos_json, dict):
            raise ValueError(
                "La respuesta JSON del LLM debe ser un objeto."
            )

        return {
            "datos": datos_json,
            "modelo": resultado["modelo"],
            "latencia_ms": resultado["latencia_ms"],
            "respuesta_original": texto
        }


def crear_servicio_ollama(
    model: str = "llama3.2"
) -> OllamaService:
    """
    Crea una instancia del servicio Ollama.
    """
    return OllamaService(model=model)