"""
Configuración persistente de LogiSmart.
"""

from datetime import datetime


class ConfigRepository:

    def __init__(self, db):
        self.collection = db["configuracion"]

    def obtener(self):
        configuracion = self.collection.find_one(
            {"tipo": "principal"}
        )

        if configuracion:
            return configuracion

        configuracion = {
            "tipo": "principal",
            "modelo_ollama": "llama3.2",
            "servidor_ollama": "http://localhost:11434",
            "temperatura": 0.0,
            "umbral_revision": "alta",
            "simular_correo": True,
            "actualizado": datetime.now()
        }

        self.collection.insert_one(configuracion)

        return configuracion

    def guardar(
        self,
        modelo,
        servidor,
        temperatura,
        umbral_revision,
        simular_correo
    ):
        documento = {
            "tipo": "principal",
            "modelo_ollama": modelo,
            "servidor_ollama": servidor,
            "temperatura": float(temperatura),
            "umbral_revision": umbral_revision,
            "simular_correo": bool(simular_correo),
            "actualizado": datetime.now()
        }

        self.collection.update_one(
            {"tipo": "principal"},
            {"$set": documento},
            upsert=True
        )

        return documento