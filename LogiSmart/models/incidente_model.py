"""
Modelos Pydantic para LogiSmart.

Valida las respuestas estructuradas generadas por Ollama.
"""

from typing import List
from pydantic import BaseModel, Field, field_validator


CATEGORIAS_VALIDAS = {
    "materiales_peligrosos",
    "sobrepeso",
    "acceso_no_autorizado",
    "falla_hardware",
    "falla_software",
    "somnolencia_conductor",
    "otro",
}

PRIORIDADES_VALIDAS = {
    "baja",
    "media",
    "alta",
    "critica",
}


class IncidenteLLM(BaseModel):
    categoria: str = Field(
        ...,
        description="Categoría asignada al incidente."
    )

    prioridad: str = Field(
        ...,
        description="Prioridad del incidente."
    )

    entidades: List[str] = Field(
        default_factory=list,
        description="Entidades detectadas en el correo."
    )

    resumen: str = Field(
        ...,
        description="Resumen breve del incidente."
    )

    @field_validator("categoria")
    @classmethod
    def validar_categoria(cls, value):
        value = value.strip().lower()

        if value not in CATEGORIAS_VALIDAS:
            raise ValueError(
                f"Categoría no válida: {value}"
            )

        return value

    @field_validator("prioridad")
    @classmethod
    def validar_prioridad(cls, value):
        value = value.strip().lower()

        if value not in PRIORIDADES_VALIDAS:
            raise ValueError(
                f"Prioridad no válida: {value}"
            )

        return value

    @field_validator("resumen")
    @classmethod
    def validar_resumen(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("El resumen no puede estar vacío.")

        return value