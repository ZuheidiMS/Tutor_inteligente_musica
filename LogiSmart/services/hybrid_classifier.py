"""
Clasificador híbrido de incidentes para LogiSmart.

Flujo:
1. Recibe un correo.
2. Clasifica mediante reglas.
3. Consulta al LLM.
4. Valida la respuesta con Pydantic.
5. Si el LLM falla, realiza un reintento.
6. Si vuelve a fallar, utiliza las reglas como fallback.
7. Si existen diferencias entre reglas y LLM, marca revisión humana.
8. Puede preparar y guardar la evaluación en MongoDB.
"""

from typing import Any, Dict, List

from models.incidente_model import IncidenteLLM
from services.llm_service import OllamaService


ORDEN_PRIORIDAD = [
    "baja",
    "media",
    "alta",
    "critica"
]


CATEGORIAS_REGLAS = {
    "materiales_peligrosos": [
        "peligroso",
        "derrame",
        "fuga",
        "quimico",
        "inflamable",
        "toxico",
        "corrosivo"
    ],
    "sobrepeso": [
        "sobrepeso",
        "excede",
        "bascula",
        "exceso de peso",
        "sobrecarga"
    ],
    "acceso_no_autorizado": [
        "sin autorizacion",
        "no autorizado",
        "acceso denegado",
        "barrera",
        "intruso"
    ],
    "falla_hardware": [
        "camara",
        "sensor",
        "lector",
        "rfid",
        "no enciende",
        "apagado",
        "danado",
        "falla electrica"
    ],
    "falla_software": [
        "sistema",
        "error",
        "pantalla",
        "caido",
        "no carga",
        "lento",
        "software",
        "aplicacion"
    ],
    "somnolencia_conductor": [
        "somnolencia",
        "dormido",
        "cansancio",
        "fatiga",
        "sueno"
    ]
}


PRIORIDAD_BASE = {
    "materiales_peligrosos": "critica",
    "somnolencia_conductor": "alta",
    "acceso_no_autorizado": "alta",
    "sobrepeso": "media",
    "falla_hardware": "media",
    "falla_software": "baja",
    "otro": "baja"
}


PALABRAS_URGENTES = [
    "urgente",
    "emergencia",
    "accidente",
    "incendio",
    "herido",
    "critico",
    "inmediato"
]


class HybridClassifier:
    """Clasificador híbrido basado en reglas y LLM."""

    def __init__(
        self,
        model: str = "llama3.2",
        max_reintentos: int = 1,
        evaluaciones_repository=None
    ):
        self.ollama = OllamaService(model=model)
        self.max_reintentos = max_reintentos
        self.evaluaciones_repository = evaluaciones_repository

    def construir_prompt(
        self,
        asunto: str,
        cuerpo: str
    ) -> str:
        """Construye el prompt estructurado para el LLM."""

        return f"""
Eres un clasificador de incidentes para el sistema LogiSmart.

Analiza el siguiente correo de incidente.

ASUNTO:
{asunto}

CUERPO:
{cuerpo}

Clasifica el incidente utilizando una de estas categorías:

- materiales_peligrosos
- sobrepeso
- acceso_no_autorizado
- falla_hardware
- falla_software
- somnolencia_conductor
- otro

La prioridad debe ser una de:

- baja
- media
- alta
- critica

Extrae únicamente las entidades que aparezcan explícitamente
en el correo, por ejemplo:

- placas
- identificadores de camión
- ubicaciones
- materiales
- equipos

IMPORTANTE:

Responde ÚNICAMENTE con un objeto JSON válido.

No agregues explicaciones.
No utilices Markdown.
No escribas texto antes o después del JSON.

El JSON debe tener EXACTAMENTE esta estructura:

{{
  "categoria": "string",
  "prioridad": "string",
  "entidades": [],
  "resumen": "string"
}}
""".strip()

    def clasificar_por_reglas(
        self,
        asunto: str,
        cuerpo: str
    ) -> Dict[str, Any]:
        """Clasificación de respaldo mediante palabras clave."""

        texto = f"{asunto} {cuerpo}".lower()

        resultados = {}

        for categoria, palabras in CATEGORIAS_REGLAS.items():
            coincidencias = [
                palabra
                for palabra in palabras
                if palabra in texto
            ]

            resultados[categoria] = coincidencias

        categoria = max(
            resultados,
            key=lambda clave: len(resultados[clave])
        )

        if not resultados[categoria]:
            categoria = "otro"

        prioridad = PRIORIDAD_BASE[categoria]

        urgentes = [
            palabra
            for palabra in PALABRAS_URGENTES
            if palabra in texto
        ]

        if urgentes:
            indice = ORDEN_PRIORIDAD.index(prioridad)

            indice = min(
                indice + 1,
                len(ORDEN_PRIORIDAD) - 1
            )

            prioridad = ORDEN_PRIORIDAD[indice]

        entidades = self.extraer_entidades(
            asunto,
            cuerpo
        )

        resumen = (
            f"Incidente clasificado por reglas como "
            f"{categoria} con prioridad {prioridad}."
        )

        return {
            "categoria": categoria,
            "prioridad": prioridad,
            "entidades": entidades,
            "resumen": resumen
        }

    def extraer_entidades(
        self,
        asunto: str,
        cuerpo: str
    ) -> List[str]:
        """Extrae entidades simples sin inventar información."""

        texto = f"{asunto} {cuerpo}"

        entidades = []

        palabras = texto.replace(",", " ").split()

        for palabra in palabras:

            palabra_limpia = (
                palabra
                .strip(".;:!?()[]{}")
            )

            if palabra_limpia.upper().startswith("CAM-"):
                entidades.append(
                    palabra_limpia.upper()
                )

        texto_minusculas = texto.lower()

        ubicaciones = [
            "muelle",
            "puerta",
            "andén",
            "anden",
            "caseta"
        ]

        for ubicacion in ubicaciones:

            if ubicacion in texto_minusculas:

                indice = texto_minusculas.find(
                    ubicacion
                )

                fragmento = texto[
                    indice:indice + 20
                ].strip()

                entidades.append(
                    fragmento.split(".")[0]
                )

        if "material químico" in texto_minusculas:
            entidades.append("material químico")

        return list(dict.fromkeys(entidades))

    def _validar_llm(
        self,
        asunto: str,
        cuerpo: str
    ) -> Dict[str, Any]:
        """Solicita y valida la respuesta del LLM."""

        prompt = self.construir_prompt(
            asunto,
            cuerpo
        )

        resultado = self.ollama.generar_json(
            prompt=prompt,
            temperature=0.0
        )

        incidente = IncidenteLLM(
            **resultado["datos"]
        )

        return {
            "clasificacion": incidente.model_dump(),
            "modelo": resultado["modelo"],
            "latencia_ms": resultado["latencia_ms"],
            "respuesta_original": resultado[
                "respuesta_original"
            ]
        }

    def clasificar(
        self,
        asunto: str,
        cuerpo: str
    ) -> Dict[str, Any]:
        """Ejecuta la clasificación híbrida completa."""

        reglas = self.clasificar_por_reglas(
            asunto,
            cuerpo
        )

        errores_llm = []
        resultado_llm = None

        total_intentos = self.max_reintentos + 1

        for intento in range(total_intentos):

            try:
                resultado_llm = self._validar_llm(
                    asunto,
                    cuerpo
                )

                break

            except Exception as error:

                errores_llm.append(
                    f"Intento {intento + 1}: "
                    f"{type(error).__name__}: {error}"
                )

        if resultado_llm is None:

            return {
                "clasificacion": reglas,
                "fuente": "reglas_fallback",
                "modelo": self.ollama.model,
                "latencia_ms": None,
                "respuesta_original": None,
                "requiere_revision_humana": True,
                "coincide_con_reglas": True,
                "clasificacion_reglas": reglas,
                "clasificacion_llm": {},
                "errores_llm": errores_llm
            }

        clasificacion_llm = resultado_llm[
            "clasificacion"
        ]

        coincide_categoria = (
            reglas["categoria"]
            == clasificacion_llm["categoria"]
        )

        coincide_prioridad = (
            reglas["prioridad"]
            == clasificacion_llm["prioridad"]
        )

        coincide = (
            coincide_categoria
            and coincide_prioridad
        )

        prioridad_reglas = ORDEN_PRIORIDAD.index(
            reglas["prioridad"]
        )

        prioridad_llm = ORDEN_PRIORIDAD.index(
            clasificacion_llm["prioridad"]
        )

        prioridad_final = max(
            prioridad_reglas,
            prioridad_llm
        )

        prioridad_seguridad = ORDEN_PRIORIDAD[
            prioridad_final
        ]

        clasificacion_final = dict(
            clasificacion_llm
        )

        clasificacion_final["prioridad"] = (
            prioridad_seguridad
        )

        return {
            "clasificacion": clasificacion_final,
            "fuente": "hibrido",
            "modelo": resultado_llm["modelo"],
            "latencia_ms": resultado_llm["latencia_ms"],
            "respuesta_original": resultado_llm[
                "respuesta_original"
            ],
            "clasificacion_reglas": reglas,
            "clasificacion_llm": clasificacion_llm,
            "coincide_con_reglas": coincide,
            "requiere_revision_humana": not coincide,
            "errores_llm": errores_llm
        }

    def preparar_evaluacion(
        self,
        asunto: str,
        cuerpo: str,
        resultado: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepara los datos para almacenarlos en MongoDB."""

        prompt = self.construir_prompt(
            asunto,
            cuerpo
        )

        return {
            "prompt": prompt,
            "response": resultado.get(
                "respuesta_original"
            ),
            "model": resultado.get(
                "modelo",
                self.ollama.model
            ),
            "latency_ms": resultado.get(
                "latencia_ms"
            ),
            "matched_rules": resultado.get(
                "coincide_con_reglas",
                False
            ),
            "clasificacion_llm": resultado.get(
                "clasificacion_llm",
                {}
            ),
            "clasificacion_reglas": resultado.get(
                "clasificacion_reglas",
                {}
            ),
            "clasificacion_final": resultado.get(
                "clasificacion",
                {}
            ),
            "requiere_revision_humana": resultado.get(
                "requiere_revision_humana",
                False
            )
        }

    def guardar_evaluacion(
        self,
        asunto: str,
        cuerpo: str,
        resultado: Dict[str, Any]
    ) -> str:
        """Guarda automáticamente la evaluación en MongoDB."""

        if self.evaluaciones_repository is None:
            raise RuntimeError(
                "No se configuró el repositorio de evaluaciones."
            )

        evaluacion = self.preparar_evaluacion(
            asunto=asunto,
            cuerpo=cuerpo,
            resultado=resultado
        )

        return self.evaluaciones_repository.crear(
            **evaluacion
        )