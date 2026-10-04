"""
Persistencia del historial del asistente LLM.
"""

from datetime import datetime


class AsistenteRepository:

    def __init__(self, db):
        self.collection = db["historial_asistente"]

    def guardar(self, pregunta, respuesta, fuentes=None):
        documento = {
            "pregunta": pregunta,
            "respuesta": respuesta,
            "fuentes": fuentes or [],
            "timestamp": datetime.now()
        }

        resultado = self.collection.insert_one(documento)

        return str(resultado.inserted_id)

    def listar(self, limite=50):
        return list(
            self.collection.find()
            .sort("timestamp", -1)
            .limit(limite)
        )

    def limpiar(self):
        resultado = self.collection.delete_many({})
        return resultado.deleted_count
