from datetime import datetime
from bson import ObjectId
from pymongo.errors import PyMongoError

from database.mongodb import MongoDB


class IncidentesRepository:
    ESTADOS_VALIDOS = ("nuevo", "en_atencion", "cerrado")

    def __init__(self):
        self.mongo = MongoDB()
        self.db = self.mongo.conectar()
        if self.db is None:
            raise ConnectionError("No se pudo conectar con MongoDB.")
        self.coleccion = self.db["incidentes"]

    def crear(
        self,
        correo_original,
        categoria,
        prioridad,
        entidades=None,
        resumen="",
        estado="nuevo",
        datos_extraidos=None,
    ):
        if not correo_original or not str(correo_original).strip():
            raise ValueError("El correo original es obligatorio.")

        if not categoria or not str(categoria).strip():
            raise ValueError("La categoría es obligatoria.")

        if prioridad not in ("baja", "media", "alta", "critica"):
            raise ValueError("Prioridad inválida.")

        if estado not in self.ESTADOS_VALIDOS:
            raise ValueError("Estado inválido.")

        documento = {
            "correo_original": str(correo_original).strip(),
            "categoria": str(categoria).strip(),
            "prioridad": prioridad,
            "entidades": entidades or [],
            "resumen": str(resumen or "").strip(),
            "datos_extraidos": datos_extraidos or {},
            "estado": estado,
            "fecha_creacion": datetime.now(),
            "fecha_actualizacion": datetime.now(),
        }

        try:
            resultado = self.coleccion.insert_one(documento)
            return str(resultado.inserted_id)
        except PyMongoError as e:
            raise RuntimeError(f"Error al guardar incidente: {e}") from e

    def obtener_todos(self, fecha_inicio=None, fecha_fin=None):
        filtro = {}

        if fecha_inicio or fecha_fin:
            filtro["fecha_creacion"] = {}

            if fecha_inicio:
                filtro["fecha_creacion"]["$gte"] = fecha_inicio

            if fecha_fin:
                filtro["fecha_creacion"]["$lte"] = fecha_fin

        try:
            return list(
                self.coleccion.find(filtro).sort("fecha_creacion", -1)
            )
        except PyMongoError as e:
            raise RuntimeError(f"Error al consultar incidentes: {e}") from e

    def buscar_por_id(self, incidente_id):
        try:
            if isinstance(incidente_id, ObjectId):
                object_id = incidente_id
            else:
                object_id = ObjectId(str(incidente_id))

            return self.coleccion.find_one({"_id": object_id})

        except Exception as e:
            raise ValueError(f"ID de incidente inválido: {e}") from e

    def actualizar(
        self,
        incidente_id,
        categoria=None,
        prioridad=None,
        resumen=None,
        estado=None,
        entidades=None,
        datos_extraidos=None,
    ):
        cambios = {}

        if categoria is not None:
            if not str(categoria).strip():
                raise ValueError("La categoría no puede estar vacía.")
            cambios["categoria"] = str(categoria).strip()

        if prioridad is not None:
            if prioridad not in ("baja", "media", "alta", "critica"):
                raise ValueError("Prioridad inválida.")
            cambios["prioridad"] = prioridad

        if resumen is not None:
            cambios["resumen"] = str(resumen).strip()

        if estado is not None:
            if estado not in self.ESTADOS_VALIDOS:
                raise ValueError("Estado inválido.")
            cambios["estado"] = estado

        if entidades is not None:
            cambios["entidades"] = entidades

        if datos_extraidos is not None:
            cambios["datos_extraidos"] = datos_extraidos

        if not cambios:
            raise ValueError("No hay datos para actualizar.")

        cambios["fecha_actualizacion"] = datetime.now()

        try:
            object_id = (
                incidente_id
                if isinstance(incidente_id, ObjectId)
                else ObjectId(str(incidente_id))
            )

            resultado = self.coleccion.update_one(
                {"_id": object_id},
                {"$set": cambios},
            )

            if resultado.matched_count == 0:
                raise ValueError("Incidente no encontrado.")

            return resultado.modified_count > 0

        except PyMongoError as e:
            raise RuntimeError(f"Error al actualizar incidente: {e}") from e

    def eliminar(self, incidente_id):
        try:
            object_id = (
                incidente_id
                if isinstance(incidente_id, ObjectId)
                else ObjectId(str(incidente_id))
            )

            resultado = self.coleccion.delete_one({"_id": object_id})

            if resultado.deleted_count == 0:
                raise ValueError("Incidente no encontrado.")

            return True

        except PyMongoError as e:
            raise RuntimeError(f"Error al eliminar incidente: {e}") from e

    def cerrar(self):
        self.mongo.cerrar()