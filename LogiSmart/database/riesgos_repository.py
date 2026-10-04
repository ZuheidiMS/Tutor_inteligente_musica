"""
CRUD de riesgos éticos de LogiSmart.
"""

from datetime import datetime
from bson import ObjectId


CATEGORIAS = {
    "alucinacion_llm",
    "sesgo",
    "privacidad",
    "sobredependencia_automatizacion",
    "seguridad",
    "responsabilidad",
    "otro"
}


class RiesgosRepository:

    def __init__(self, db):
        self.collection = db["riesgos_eticos"]

    def calcular(self, probabilidad, impacto):
        score = int(probabilidad) * int(impacto)

        if score <= 4:
            nivel = "bajo"
        elif score <= 9:
            nivel = "medio"
        elif score <= 16:
            nivel = "alto"
        else:
            nivel = "critico"

        return score, nivel

    def crear(
        self,
        modulo,
        descripcion,
        categoria,
        probabilidad,
        impacto,
        mitigacion,
        probabilidad_residual=None,
        impacto_residual=None
    ):
        if categoria not in CATEGORIAS:
            raise ValueError("Categoría de riesgo no válida.")

        score, nivel = self.calcular(
            probabilidad,
            impacto
        )

        if probabilidad_residual is None:
            probabilidad_residual = probabilidad

        if impacto_residual is None:
            impacto_residual = impacto

        score_residual, nivel_residual = self.calcular(
            probabilidad_residual,
            impacto_residual
        )

        documento = {
            "modulo": modulo,
            "descripcion": descripcion,
            "categoria": categoria,
            "probabilidad": int(probabilidad),
            "impacto": int(impacto),
            "score": score,
            "nivel": nivel,
            "mitigacion": mitigacion,
            "probabilidad_residual": int(probabilidad_residual),
            "impacto_residual": int(impacto_residual),
            "score_residual": score_residual,
            "nivel_residual": nivel_residual,
            "estado": "abierto",
            "fecha_creacion": datetime.now(),
            "historico": [
                {
                    "fecha": datetime.now(),
                    "accion": "creado",
                    "nivel": nivel
                }
            ]
        }

        resultado = self.collection.insert_one(documento)

        return str(resultado.inserted_id)

    def listar(self):
        return list(
            self.collection.find().sort(
                "score",
                -1
            )
        )

    def obtener_por_id(self, documento_id):
        try:
            return self.collection.find_one(
                {"_id": ObjectId(documento_id)}
            )
        except Exception:
            return None

    def actualizar(
        self,
        documento_id,
        modulo,
        descripcion,
        categoria,
        probabilidad,
        impacto,
        mitigacion,
        probabilidad_residual,
        impacto_residual,
        estado
    ):
        score, nivel = self.calcular(
            probabilidad,
            impacto
        )

        score_residual, nivel_residual = self.calcular(
            probabilidad_residual,
            impacto_residual
        )

        cambios = {
            "modulo": modulo,
            "descripcion": descripcion,
            "categoria": categoria,
            "probabilidad": int(probabilidad),
            "impacto": int(impacto),
            "score": score,
            "nivel": nivel,
            "mitigacion": mitigacion,
            "probabilidad_residual": int(probabilidad_residual),
            "impacto_residual": int(impacto_residual),
            "score_residual": score_residual,
            "nivel_residual": nivel_residual,
            "estado": estado,
            "fecha_actualizacion": datetime.now()
        }

        self.collection.update_one(
            {"_id": ObjectId(documento_id)},
            {
                "$set": cambios,
                "$push": {
                    "historico": {
                        "fecha": datetime.now(),
                        "accion": "actualizado",
                        "nivel": nivel,
                        "nivel_residual": nivel_residual
                    }
                }
            }
        )

        return True

    def eliminar(self, documento_id):
        try:
            resultado = self.collection.delete_one(
                {"_id": ObjectId(documento_id)}
            )

            return resultado.deleted_count > 0

        except Exception:
            return False