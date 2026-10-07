"""
Repositorio para evaluaciones del LLM.
"""

from datetime import datetime
from bson import ObjectId


class EvaluacionesLLMRepository:

    def __init__(self, db):
        self.collection = db["evaluaciones_llm"]

    def crear(
        self,
        prompt,
        response,
        model,
        latency_ms,
        matched_rules,
        clasificacion_llm=None,
        clasificacion_reglas=None,
        clasificacion_final=None,
        requiere_revision_humana=False
    ):
        documento = {
            "prompt": prompt,
            "response": response,
            "model": model,
            "latency_ms": latency_ms,
            "matched_rules": matched_rules,
            "clasificacion_llm": clasificacion_llm,
            "clasificacion_reglas": clasificacion_reglas,
            "clasificacion_final": clasificacion_final,
            "requiere_revision_humana": requiere_revision_humana,
            "timestamp": datetime.now()
        }

        resultado = self.collection.insert_one(documento)

        return str(resultado.inserted_id)

    def listar(self, limite=100):
        return list(
            self.collection.find()
            .sort("timestamp", -1)
            .limit(limite)
        )

    def obtener_por_id(self, documento_id):
        try:
            return self.collection.find_one(
                {"_id": ObjectId(documento_id)}
            )
        except Exception:
            return None

    def actualizar(self, documento_id, cambios):
        try:
            resultado = self.collection.update_one(
                {"_id": ObjectId(documento_id)},
                {"$set": cambios}
            )

            return resultado.modified_count > 0

        except Exception:
            return False

    def eliminar(self, documento_id):
        try:
            resultado = self.collection.delete_one(
                {"_id": ObjectId(documento_id)}
            )

            return resultado.deleted_count > 0

        except Exception:
            return False