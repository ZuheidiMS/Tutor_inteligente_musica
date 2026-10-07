"""
Repositorio de indicadores y agregaciones del Dashboard.
"""

from datetime import datetime, timedelta


class DashboardRepository:

    def __init__(self, db):
        self.db = db
        self.camiones = db["camiones"]
        self.accesos = db["accesos"]
        self.incidentes = db["incidentes"]
        self.riesgos = db["riesgos_eticos"]
        self.evaluaciones = db["evaluaciones_llm"]

    def obtener_indicadores(
        self,
        fecha_inicio=None,
        fecha_fin=None
    ):
        filtro_fecha = {}

        if fecha_inicio or fecha_fin:
            filtro_fecha["timestamp"] = {}

            if fecha_inicio:
                filtro_fecha["timestamp"]["$gte"] = fecha_inicio

            if fecha_fin:
                filtro_fecha["timestamp"]["$lte"] = fecha_fin

        filtro_incidentes = {}

        if fecha_inicio or fecha_fin:
            filtro_incidentes["creado_en"] = {}

            if fecha_inicio:
                filtro_incidentes["creado_en"]["$gte"] = fecha_inicio

            if fecha_fin:
                filtro_incidentes["creado_en"]["$lte"] = fecha_fin

        filtro_riesgos = {}

        if fecha_inicio or fecha_fin:
            filtro_riesgos["fecha_creacion"] = {}

            if fecha_inicio:
                filtro_riesgos["fecha_creacion"]["$gte"] = fecha_inicio

            if fecha_fin:
                filtro_riesgos["fecha_creacion"]["$lte"] = fecha_fin

        return {
            "camiones_atendidos": self.accesos.count_documents(
                filtro_fecha
            ),

            "incidentes_abiertos": self.incidentes.count_documents({
                **filtro_incidentes,
                "estado": {"$in": ["nuevo", "en_atencion"]}
            }),

            "incidentes_criticos": self.incidentes.count_documents({
                **filtro_incidentes,
                "prioridad": "critica"
            }),

            "riesgos_criticos": self.riesgos.count_documents({
                **filtro_riesgos,
                "nivel": "critico"
            }),

            "evaluaciones_llm": self.evaluaciones.count_documents({}),

            "accesos_registrados": self.accesos.count_documents(
                filtro_fecha
            )
        }

    def incidentes_por_categoria(self):
        pipeline = [
            {
                "$group": {
                    "_id": "$categoria",
                    "total": {"$sum": 1}
                }
            },
            {
                "$sort": {
                    "total": -1
                }
            }
        ]

        return list(
            self.incidentes.aggregate(pipeline)
        )

    def incidentes_por_semana(self):
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%U",
                            "date": "$creado_en"
                        }
                    },
                    "total": {"$sum": 1}
                }
            },
            {
                "$sort": {
                    "_id": 1
                }
            }
        ]

        return list(
            self.incidentes.aggregate(pipeline)
        )

    def incidentes_por_categoria_y_semana(self):
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "categoria": "$categoria",
                        "semana": {
                            "$dateToString": {
                                "format": "%Y-%U",
                                "date": "$creado_en"
                            }
                        }
                    },
                    "total": {"$sum": 1}
                }
            },
            {
                "$sort": {
                    "_id.semana": 1
                }
            }
        ]

        return list(
            self.incidentes.aggregate(pipeline)
        )

    def evaluar_servicios(self):
        mongo_ok = False
        ollama_ok = False

        try:
            self.db.command("ping")
            mongo_ok = True
        except Exception:
            mongo_ok = False

        try:
            import requests

            respuesta = requests.get(
                "http://localhost:11434/api/tags",
                timeout=3
            )

            ollama_ok = respuesta.status_code == 200

        except Exception:
            ollama_ok = False

        return {
            "MongoDB": mongo_ok,
            "Ollama": ollama_ok
        }