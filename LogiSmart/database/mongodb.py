"""
Conexión centralizada a MongoDB para LogiSmart.
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


MONGODB_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "logismart"


class MongoDB:
    """Gestiona la conexión y acceso a la base de datos LogiSmart."""

    def __init__(
        self,
        uri: str = MONGODB_URI,
        database_name: str = DATABASE_NAME
    ):
        self.uri = uri
        self.database_name = database_name
        self.client = None
        self.db = None

    def conectar(self):
        """Conecta con MongoDB y verifica que el servidor responda."""

        try:
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=5000
            )

            # Verifica que MongoDB esté disponible.
            self.client.admin.command("ping")

            self.db = self.client[self.database_name]

            print("===================================")
            print(" CONEXIÓN MONGODB: OK")
            print("===================================")
            print(f"Base de datos: {self.database_name}")

            return self.db

        except (ConnectionFailure, ServerSelectionTimeoutError) as error:
            print("===================================")
            print(" ERROR DE CONEXIÓN A MONGODB")
            print("===================================")
            print(f"Detalle: {error}")

            self.client = None
            self.db = None

            return None

    def obtener_coleccion(self, nombre: str):
        """Obtiene una colección de la base de datos."""

        if self.db is None:
            raise RuntimeError(
                "MongoDB no está conectado. "
                "Ejecuta conectar() primero."
            )

        return self.db[nombre]

    def cerrar(self):
        """Cierra la conexión con MongoDB."""

        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None
            print("Conexión MongoDB cerrada.")