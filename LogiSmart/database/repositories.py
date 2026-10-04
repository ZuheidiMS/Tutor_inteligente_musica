"""
Repositorios de acceso a datos para LogiSmart.

Este módulo contiene las operaciones CRUD sobre MongoDB.
La interfaz gráfica y la lógica de negocio utilizarán estas
funciones en lugar de conectarse directamente a MongoDB.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pymongo.errors import PyMongoError

from database.mongodb import MongoDB


class CamionesRepository:
    """Repositorio CRUD para la colección camiones."""

    COLLECTION = "camiones"

    def __init__(self, mongo: Optional[MongoDB] = None):
        self.mongo = mongo or MongoDB()

    def crear(
        self,
        placa: str,
        camion_id: str,
        empresa: str,
        autorizado: bool,
        certificacion_conductor: bool
    ):
        """
        Crea un registro de camión.

        Campos requeridos:
        - placa
        - camion_id
        - empresa
        - autorizado
        - certificacion_conductor
        """

        if not placa.strip():
            raise ValueError("La placa es obligatoria.")

        if not camion_id.strip():
            raise ValueError("El ID del camión es obligatorio.")

        if not empresa.strip():
            raise ValueError("La empresa es obligatoria.")

        if not isinstance(autorizado, bool):
            raise TypeError("autorizado debe ser bool.")

        if not isinstance(certificacion_conductor, bool):
            raise TypeError(
                "certificacion_conductor debe ser bool."
            )

        db = self.mongo.conectar()

        if db is None:
            raise ConnectionError(
                "No fue posible conectar con MongoDB."
            )

        try:
            coleccion = self.mongo.obtener_coleccion(
                self.COLLECTION
            )

            documento = {
                "placa": placa.strip().upper(),
                "camion_id": camion_id.strip().upper(),
                "empresa": empresa.strip(),
                "autorizado": autorizado,
                "certificacion_conductor": (
                    certificacion_conductor
                ),
                "fecha_registro": datetime.now()
            }

            resultado = coleccion.insert_one(documento)

            return resultado.inserted_id

        except PyMongoError as error:
            raise RuntimeError(
                f"Error al crear el camión: {error}"
            ) from error

        finally:
            self.mongo.cerrar()

    def obtener_todos(self) -> List[Dict[str, Any]]:
        """Obtiene todos los camiones registrados."""

        db = self.mongo.conectar()

        if db is None:
            raise ConnectionError(
                "No fue posible conectar con MongoDB."
            )

        try:
            coleccion = self.mongo.obtener_coleccion(
                self.COLLECTION
            )

            return list(
                coleccion.find().sort("fecha_registro", -1)
            )

        except PyMongoError as error:
            raise RuntimeError(
                f"Error al consultar camiones: {error}"
            ) from error

        finally:
            self.mongo.cerrar()

    def buscar_por_placa(
        self,
        placa: str
    ) -> Optional[Dict[str, Any]]:
        """Busca un camión por su placa."""

        if not placa.strip():
            raise ValueError("La placa es obligatoria.")

        db = self.mongo.conectar()

        if db is None:
            raise ConnectionError(
                "No fue posible conectar con MongoDB."
            )

        try:
            coleccion = self.mongo.obtener_coleccion(
                self.COLLECTION
            )

            return coleccion.find_one({
                "placa": placa.strip().upper()
            })

        except PyMongoError as error:
            raise RuntimeError(
                f"Error al buscar el camión: {error}"
            ) from error

        finally:
            self.mongo.cerrar()

    def actualizar(
        self,
        placa: str,
        empresa: Optional[str] = None,
        autorizado: Optional[bool] = None,
        certificacion_conductor: Optional[bool] = None
    ) -> bool:
        """Actualiza los datos de un camión."""

        if not placa.strip():
            raise ValueError("La placa es obligatoria.")

        cambios = {}

        if empresa is not None:
            if not empresa.strip():
                raise ValueError(
                    "La empresa no puede estar vacía."
                )
            cambios["empresa"] = empresa.strip()

        if autorizado is not None:
            if not isinstance(autorizado, bool):
                raise TypeError(
                    "autorizado debe ser bool."
                )
            cambios["autorizado"] = autorizado

        if certificacion_conductor is not None:
            if not isinstance(
                certificacion_conductor,
                bool
            ):
                raise TypeError(
                    "certificacion_conductor debe ser bool."
                )
            cambios[
                "certificacion_conductor"
            ] = certificacion_conductor

        if not cambios:
            raise ValueError(
                "No se proporcionaron datos para actualizar."
            )

        cambios["fecha_actualizacion"] = datetime.now()

        db = self.mongo.conectar()

        if db is None:
            raise ConnectionError(
                "No fue posible conectar con MongoDB."
            )

        try:
            coleccion = self.mongo.obtener_coleccion(
                self.COLLECTION
            )

            resultado = coleccion.update_one(
                {
                    "placa": placa.strip().upper()
                },
                {
                    "$set": cambios
                }
            )

            return resultado.modified_count > 0

        except PyMongoError as error:
            raise RuntimeError(
                f"Error al actualizar el camión: {error}"
            ) from error

        finally:
            self.mongo.cerrar()

    def eliminar(self, placa: str) -> bool:
        """Elimina un camión por su placa."""

        if not placa.strip():
            raise ValueError("La placa es obligatoria.")

        db = self.mongo.conectar()

        if db is None:
            raise ConnectionError(
                "No fue posible conectar con MongoDB."
            )

        try:
            coleccion = self.mongo.obtener_coleccion(
                self.COLLECTION
            )

            resultado = coleccion.delete_one({
                "placa": placa.strip().upper()
            })

            return resultado.deleted_count > 0

        except PyMongoError as error:
            raise RuntimeError(
                f"Error al eliminar el camión: {error}"
            ) from error

        finally:
            self.mongo.cerrar()