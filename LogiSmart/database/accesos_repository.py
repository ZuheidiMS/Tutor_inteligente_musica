"""
Repositorio MongoDB para las decisiones de control de acceso.
"""

from datetime import datetime, timedelta
from pymongo.errors import PyMongoError


class AccesosRepository:

    def __init__(self, db):
        self.collection = db["accesos"]

    def crear(
        self,
        placa,
        camion_id,
        operador,
        P,
        Q,
        R,
        S,
        T,
        HR,
        A,
        E,
        C,
        H,
        resultado_final,
        explicacion
    ):
        documento = {
            "placa": placa,
            "camion_id": camion_id,
            "operador": operador,

            "premisas": {
                "P": bool(P),
                "Q": bool(Q),
                "R": bool(R),
                "S": bool(S),
                "T": bool(T),
                "HR": bool(HR)
            },

            "resultados": {
                "A": bool(A),
                "E": bool(E),
                "C": bool(C),
                "H": bool(H)
            },

            "resultado_final": resultado_final,
            "explicacion": explicacion,
            "timestamp": datetime.now()
        }

        try:
            resultado = self.collection.insert_one(documento)
            return str(resultado.inserted_id)
        except PyMongoError as error:
            print(f"Error guardando acceso: {error}")
            return None

    def listar(self, limite=100):
        try:
            return list(
                self.collection.find()
                .sort("timestamp", -1)
                .limit(limite)
            )
        except PyMongoError as error:
            print(f"Error consultando accesos: {error}")
            return []

    def buscar_por_placa(self, placa):
        try:
            return list(
                self.collection.find(
                    {"placa": {"$regex": placa, "$options": "i"}}
                ).sort("timestamp", -1)
            )
        except PyMongoError as error:
            print(f"Error buscando placa: {error}")
            return []

    def eliminar(self, documento_id):
        from bson import ObjectId

        try:
            resultado = self.collection.delete_one(
                {"_id": ObjectId(documento_id)}
            )
            return resultado.deleted_count > 0
        except Exception as error:
            print(f"Error eliminando acceso: {error}")
            return False

    def contar(self):
        try:
            return self.collection.count_documents({})
        except PyMongoError:
            return 0