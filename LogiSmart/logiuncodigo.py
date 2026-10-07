#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 LogiSmart Python Suite  -  Prototipo del centro de control inteligente
==============================================================================
Contenido:
  Sección 1 -> Diseño PEAS del sistema (estructura de datos + impresión)
  Sección 2 -> Motor de reglas lógicas (lógica proposicional) + tablas de verdad
  Sección 3 -> Clasificador de incidentes + envío de correo + salida JSON
  Sección 4 -> Clase EvaluadorRiesgosIA (matriz de riesgos éticos)
  Pruebas   -> unittest para las secciones 2, 3 y 4

Uso:
  python logismart_suite.py            -> ejecuta la demostración completa
  python logismart_suite.py --tests    -> ejecuta solo las pruebas unitarias
  python -m unittest logismart_suite -v (alternativa para las pruebas)

Solo usa la biblioteca estándar de Python 3.8+ (sin instalar nada).
==============================================================================
"""

# -----------------------------------------------------------------------------
# IMPORTACIONES
# -----------------------------------------------------------------------------
import itertools          # Para generar todas las combinaciones de la tabla de verdad
import json               # Para serializar la salida estricta en JSON
import logging            # Para mensajes de diagnóstico SIN contaminar la salida JSON
import os                 # Para leer credenciales SMTP desde variables de entorno
import re                 # Expresiones regulares para extraer datos del correo
import smtplib            # Cliente SMTP para el envío real del correo
import sys                # Para leer argumentos de línea de comandos
import unittest           # Marco de pruebas unitarias de la biblioteca estándar
from dataclasses import dataclass, field, asdict
from datetime import datetime
from email.message import EmailMessage
from typing import Dict, List, Optional
from database.mongodb import MongoDB
from database.incidentes_repository import IncidentesRepository
# Los mensajes de log van a stderr; el JSON se entrega solo por el valor de retorno.
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("logismart")


# =============================================================================
# SECCIÓN 1: DISEÑO PEAS (Performance, Environment, Actuators, Sensors)
# =============================================================================
# PEAS describe a un agente racional definiendo:
#   P = Medida de desempeño : ¿cómo sabemos que el agente lo hace bien?
#   E = Entorno             : ¿dónde opera y cómo es (propiedades)?
#   A = Actuadores          : ¿con qué actúa sobre el entorno?
#   S = Sensores            : ¿con qué percibe el entorno?
# Se modela como diccionario para poder imprimirlo, exportarlo o probarlo.

PEAS_LOGISMART: Dict[str, object] = {
    "agente": "Agente de control inteligente de acceso y seguridad logística LogiSmart",
    "P_desempeno": [
        "Tiempo promedio de atención por camión (minutos) -> minimizar",
        "% de camiones autorizados que ingresan sin fricción -> maximizar",
        "% de camiones no autorizados / con sobrepeso detenidos -> maximizar (meta 100%)",
        "Falsos positivos de inspección especial -> minimizar",
        "Falsos negativos (carga peligrosa que no fue inspeccionada) -> minimizar (meta 0)",
        "Incidentes de seguridad y accidentes en patio -> minimizar",
        "Tiempo de clasificación y respuesta a incidentes de soporte -> minimizar",
    ],
    "E_entorno": {
        "descripcion": "Patio de maniobras, casetas de acceso, básculas y andenes del centro logístico",
        "propiedades": {
            "observabilidad": "Parcialmente observable (sensores con ruido, mala visión nocturna)",
            "determinismo": "Estocástico (llegadas, clima y fallas impredecibles)",
            "episodico": "Secuencial (una decisión afecta el tráfico posterior)",
            "dinamico": "Dinámico (el entorno cambia mientras el agente decide)",
            "discreto": "Mixto (estados discretos de acceso; peso y posición continuos)",
            "agentes": "Multiagente (conductores, personal, otros sistemas)",
        },
        "actores_externos": ["Conductores", "Operadores de caseta", "Personal de seguridad", "Autoridades"],
    },
    "A_actuadores": [
        "Barrera vehicular (abrir / cerrar)",
        "Semáforo y pantallas de instrucciones al conductor",
        "Alarma sonora y luminosa",
        "Sistema de asignación de andén / carril de inspección especial",
        "Notificaciones (correo, SMS, panel) a supervisores y soporte",
        "Registro en base de datos (bitácora de accesos e incidentes)",
    ],
    "S_sensores": [
        "Cámaras con lector de placas (LPR) y cámara de somnolencia del conductor",
        "Báscula de piso (peso del vehículo)",
        "Lector RFID / QR de autorización previa",
        "Escáner de documentos (certificación del conductor)",
        "Sensores de detección de materiales peligrosos / lectura de placas de riesgo (NOM)",
        "Buzón de correo de soporte (entrada de texto de incidentes)",
    ],
}


def imprimir_peas(peas: Dict[str, object] = PEAS_LOGISMART) -> None:
    """Imprime el marco PEAS de forma legible en consola."""
    print("=" * 78)
    print("SECCIÓN 1 - MARCO PEAS")
    print("=" * 78)
    print(f"Agente: {peas['agente']}\n")
    print("P (Medidas de desempeño):")
    for item in peas["P_desempeno"]:
        print(f"   - {item}")
    entorno = peas["E_entorno"]
    print(f"\nE (Entorno): {entorno['descripcion']}")
    for nombre, valor in entorno["propiedades"].items():
        print(f"   - {nombre}: {valor}")
    print("\nA (Actuadores):")
    for item in peas["A_actuadores"]:
        print(f"   - {item}")
    print("\nS (Sensores):")
    for item in peas["S_sensores"]:
        print(f"   - {item}")
    print()


# =============================================================================
# SECCIÓN 2: MOTOR DE REGLAS LÓGICAS (LÓGICA PROPOSICIONAL)
# =============================================================================
# Premisas (variables booleanas):
#   P: Vehículo con autorización previa
#   Q: El peso excede el límite
#   R: Carga con materiales peligrosos
#   S: Conductor con certificación vigente
#
# Fórmulas:
#   A (Acceso Estándar)      = P ∧ S ∧ ¬Q
#   E (Inspección Especial)  = P ∧ (R ∨ Q)
#
# En Python:  ∧ -> and,   ∨ -> or,   ¬ -> not

def evaluar_camion(
    P: bool,
    Q: bool,
    R: bool,
    S: bool,
    guardar: bool = False,
    operador: str = "sistema"
) -> Dict[str, bool]:




    """
    Evalúa las reglas de acceso e inspección para un camión.

    Parámetros
    ----------
    P : bool  -> ¿Tiene autorización previa?
    Q : bool  -> ¿El peso excede el límite?
    R : bool  -> ¿Lleva materiales peligrosos?
    S : bool  -> ¿El conductor tiene certificación vigente?

    Retorna
    -------
    dict con:
        "acceso_estandar"       (A): True si se permite el acceso estándar
        "inspeccion_especial"   (E): True si debe activarse inspección especial
    """
    # Validación defensiva: las premisas deben ser booleanas estrictas.
    # (Evita que un 1, "si" o None pase silenciosamente y dé resultados ambiguos.)
    for nombre, valor in (("P", P), ("Q", Q), ("R", R), ("S", S)):
        if not isinstance(valor, bool):
            raise TypeError(f"La premisa {nombre} debe ser bool, se recibió {type(valor).__name__}")

    acceso_estandar = P and S and (not Q)
    inspeccion_especial = P and (R or Q)

    if guardar:
        guardar_acceso_mongodb(
            P,
            Q,
            R,
            S,
            acceso_estandar,
            inspeccion_especial,
            operador
        )

    return {
        "acceso_estandar": acceso_estandar,
        "inspeccion_especial": inspeccion_especial
    }

def guardar_acceso_mongodb(
    P: bool,
    Q: bool,
    R: bool,
    S: bool,
    resultado_A: bool,
    resultado_E: bool,
    operador: str = "sistema"
):
    """
    Guarda la decisión del motor de reglas en MongoDB.
    """

    mongo = MongoDB()
    db = mongo.conectar()

    if db is None:
        logging.error("No fue posible conectar con MongoDB.")
        return None

    try:
        coleccion = mongo.obtener_coleccion("accesos")

        documento = {
            "P": P,
            "Q": Q,
            "R": R,
            "S": S,
            "resultado_A": resultado_A,
            "resultado_E": resultado_E,
            "timestamp": datetime.now(),
            "operador": operador,
            "explicacion": {
                "A": "P AND S AND NOT Q",
                "E": "P AND (R OR Q)"
            }
        }

        resultado = coleccion.insert_one(documento)

        logging.info(
            "Acceso guardado en MongoDB: %s",
            resultado.inserted_id
        )

        return resultado.inserted_id

    except Exception as error:
        logging.error(
            "Error al guardar acceso en MongoDB: %s",
            error
        )
        return None

    finally:
        mongo.cerrar()

# =============================================================================
# REGLAS ADICIONALES DEL MOTOR DE INFERENCIA
# =============================================================================

def evaluar_certificacion(
    P: bool,
    T: bool,
    Q: bool
) -> bool:
    """
    Regla C - Certificación válida.

    C = P AND T AND NOT Q

    P: autorización previa
    T: certificación del conductor válida
    Q: sobrepeso
    """

    for nombre, valor in (("P", P), ("T", T), ("Q", Q)):
        if not isinstance(valor, bool):
            raise TypeError(
                f"{nombre} debe ser de tipo bool."
            )

    return P and T and (not Q)


def evaluar_horario_restringido(
    R: bool,
    HR: bool
) -> bool:
    """
    Regla H - Restricción de horario para materiales peligrosos.

    H = R AND HR

    R: transporte de materiales peligrosos
    HR: horario restringido
    """

    for nombre, valor in (("R", R), ("HR", HR)):
        if not isinstance(valor, bool):
            raise TypeError(
                f"{nombre} debe ser de tipo bool."
            )

    return R and HR


# =============================================================================
# TABLAS DE VERDAD DE LAS REGLAS ADICIONALES
# =============================================================================

def generar_tablas_reglas_adicionales() -> Dict[str, List[Dict[str, bool]]]:
    """
    Genera las tablas de verdad de las reglas adicionales:

    C = P ∧ T ∧ ¬Q
    H = R ∧ HR

    C:
        P  -> autorización previa
        T  -> certificación del conductor válida
        Q  -> sobrepeso

    H:
        R  -> materiales peligrosos
        HR -> horario restringido
    """

    tabla_C: List[Dict[str, bool]] = []

    for P, T, Q in itertools.product(
        [True, False],
        repeat=3
    ):
        tabla_C.append({
            "P": P,
            "T": T,
            "Q": Q,
            "no_Q": not Q,
            "C": evaluar_certificacion(P, T, Q)
        })

    tabla_H: List[Dict[str, bool]] = []

    for R, HR in itertools.product(
        [True, False],
        repeat=2
    ):
        tabla_H.append({
            "R": R,
            "HR": HR,
            "H": evaluar_horario_restringido(R, HR)
        })

    return {
        "C": tabla_C,
        "H": tabla_H
    }


def imprimir_tablas_reglas_adicionales() -> None:
    """
    Imprime las tablas de verdad de las reglas C y H.
    """

    v = lambda b: "V" if b else "F"

    tablas = generar_tablas_reglas_adicionales()

    print("=" * 78)
    print("TABLAS DE VERDAD - REGLAS ADICIONALES")
    print("=" * 78)

    print("\nRegla C = P ∧ T ∧ ¬Q")
    print(" P  T  Q  |  ¬Q  |  C")
    print("------------------------")

    for fila in tablas["C"]:
        print(
            f" {v(fila['P'])}  "
            f"{v(fila['T'])}  "
            f"{v(fila['Q'])}  |   "
            f"{v(fila['no_Q'])}   |  "
            f"{v(fila['C'])}"
        )

    print("\nRegla H = R ∧ HR")
    print(" R  HR |  H")
    print("-------------")

    for fila in tablas["H"]:
        print(
            f" {v(fila['R'])}  "
            f"{v(fila['HR'])}  |  "
            f"{v(fila['H'])}"
        )


def generar_tabla_verdad() -> List[Dict[str, bool]]:
    """
    Genera la tabla de verdad completa (2^4 = 16 filas) con columnas intermedias.

    Las columnas intermedias (¬Q, P∧S, R∨Q) permiten justificar paso a paso
    cómo se llega a A y a E.
    Orden de filas: convención clásica (de V,V,V,V hasta F,F,F,F).
    """
    filas: List[Dict[str, bool]] = []
    # itertools.product([True, False], repeat=4) produce las 16 combinaciones de (P,Q,R,S)
    for P, Q, R, S in itertools.product([True, False], repeat=4):
        resultado = evaluar_camion(P, Q, R, S)
        filas.append({
            "P": P, "Q": Q, "R": R, "S": S,
            "no_Q": not Q,             # ¬Q
            "P_y_S": P and S,          # P ∧ S
            "R_o_Q": R or Q,           # R ∨ Q
            "A": resultado["acceso_estandar"],
            "E": resultado["inspeccion_especial"],
        })
    return filas


def imprimir_tablas_verdad() -> None:
    """Imprime las tablas de verdad de A y de E (columna intermedia incluida)."""
    v = lambda b: "V" if b else "F"   # Traduce True/False a V/F para leer mejor
    tabla = generar_tabla_verdad()

    print("=" * 78)
    print("SECCIÓN 2 - TABLAS DE VERDAD")
    print("=" * 78)

    # --- Tabla A --------------------------------------------------------------
    print("\nTabla 1: A = P ∧ S ∧ ¬Q")
    print(f"{'P':^3}{'Q':^3}{'S':^3} | {'¬Q':^4}{'P∧S':^6}{'A':^4}")
    print("-" * 28)
    vistos = set()   # A no depende de R: mostramos solo las 8 combinaciones (P,Q,S) únicas
    for f in tabla:
        clave = (f["P"], f["Q"], f["S"])
        if clave in vistos:
            continue
        vistos.add(clave)
        print(f"{v(f['P']):^3}{v(f['Q']):^3}{v(f['S']):^3} | "
              f"{v(f['no_Q']):^4}{v(f['P_y_S']):^6}{v(f['A']):^4}")

    # --- Tabla E --------------------------------------------------------------
    print("\nTabla 2: E = P ∧ (R ∨ Q)")
    print(f"{'P':^3}{'Q':^3}{'R':^3} | {'R∨Q':^5}{'E':^4}")
    print("-" * 24)
    vistos = set()   # E no depende de S: 8 combinaciones (P,Q,R) únicas
    for f in tabla:
        clave = (f["P"], f["Q"], f["R"])
        if clave in vistos:
            continue
        vistos.add(clave)
        print(f"{v(f['P']):^3}{v(f['Q']):^3}{v(f['R']):^3} | "
              f"{v(f['R_o_Q']):^5}{v(f['E']):^4}")

    # --- Tabla completa conjunta ---------------------------------------------
    print("\nTabla 3: tabla completa (16 combinaciones) con A y E")
    print(f"{'P':^3}{'Q':^3}{'R':^3}{'S':^3} | {'¬Q':^4}{'P∧S':^6}{'R∨Q':^6} | {'A':^3}{'E':^3}")
    print("-" * 42)
    for f in tabla:
        print(f"{v(f['P']):^3}{v(f['Q']):^3}{v(f['R']):^3}{v(f['S']):^3} | "
              f"{v(f['no_Q']):^4}{v(f['P_y_S']):^6}{v(f['R_o_Q']):^6} | "
              f"{v(f['A']):^3}{v(f['E']):^3}")

    # --- Conclusiones para justificar ----------------------------------------
    n_A = sum(f["A"] for f in tabla)
    n_E = sum(f["E"] for f in tabla)
    n_ambas = sum(f["A"] and f["E"] for f in tabla)
    print(f"\nA es verdadera en {n_A}/16 combinaciones; E en {n_E}/16.")
    print(f"Ambas verdaderas simultáneamente en {n_ambas}/16 casos "
          "(P∧S∧¬Q∧R: acceso estándar Y revisión por carga peligrosa).")
    print("Observaciones: sin P (autorización previa) tanto A como E son siempre F;")
    print("si Q es V, A es siempre F (el exceso de peso bloquea el acceso estándar) y, con P, E es V.\n")


# =============================================================================
# SECCIÓN 3: CLASIFICADOR DE INCIDENTES Y EXTRACCIÓN -> JSON ESTRICTO
# =============================================================================
# Flujo:
#   1) Se recibe el correo del incidente (remitente, asunto, cuerpo).
#   2) Se CLASIFICA (categoría y prioridad) con reglas por palabras clave.
#   3) Se EXTRAE información estructurada con expresiones regulares.
#   4) Se ENVÍA el correo de soporte (SMTP real o simulación).
#   5) Se DEVUELVE únicamente un JSON válido (string), nada más.
#
# Nota: el clasificador es basado en reglas para que funcione sin internet.
# Podría sustituirse por una llamada a un LLM manteniendo el mismo contrato JSON.

# Categorías con sus palabras clave (en minúsculas y sin acentos, ver _normalizar)
CATEGORIAS: Dict[str, List[str]] = {
    "materiales_peligrosos": ["peligroso", "derrame", "fuga", "quimico", "inflamable", "toxico", "corrosivo"],
    "sobrepeso": ["sobrepeso", "excede", "bascula", "exceso de peso", "sobrecarga"],
    "acceso_no_autorizado": ["sin autorizacion", "no autorizado", "acceso denegado", "barrera", "intruso"],
    "falla_hardware": ["camara", "sensor", "lector", "rfid", "no enciende", "apagado", "danado", "falla electrica"],
    "falla_software": ["sistema", "error", "pantalla", "caido", "no carga", "lento", "software", "aplicacion"],
    "somnolencia_conductor": ["somnolencia", "dormido", "cansancio", "fatiga", "sueno"],
}

# Palabras que elevan la prioridad sin importar la categoría
PALABRAS_URGENTES = ["urgente", "emergencia", "accidente", "incendio", "herido", "critico", "inmediato"]

# Prioridad base por categoría (se puede escalar con palabras urgentes)
PRIORIDAD_BASE: Dict[str, str] = {
    "materiales_peligrosos": "critica",
    "somnolencia_conductor": "alta",
    "acceso_no_autorizado": "alta",
    "sobrepeso": "media",
    "falla_hardware": "media",
    "falla_software": "baja",
    "otro": "baja",
}
ORDEN_PRIORIDAD = ["baja", "media", "alta", "critica"]


def _normalizar(texto: str) -> str:
    """Pasa a minúsculas y quita acentos/ñ para comparar palabras clave sin sorpresas."""
    tabla = str.maketrans("áéíóúüñ", "aeiouun")
    return texto.lower().translate(tabla)


def clasificar_incidente(asunto: str, cuerpo: str) -> Dict[str, object]:
    """
    Clasifica el incidente por conteo de palabras clave.
    Devuelve categoría, prioridad y las palabras que dispararon la decisión.
    """
    texto = _normalizar(f"{asunto} {cuerpo}")

    # Puntuación por categoría = número de palabras clave encontradas
    puntajes: Dict[str, List[str]] = {
        cat: [kw for kw in kws if kw in texto] for cat, kws in CATEGORIAS.items()
    }
    # Elegimos la categoría con más coincidencias; en empate gana la primera del diccionario
    # (materiales peligrosos primero: ante la duda, se privilegia la seguridad).
    mejor_cat = max(puntajes, key=lambda c: len(puntajes[c]))
    if not puntajes[mejor_cat]:
        mejor_cat = "otro"
        coincidencias: List[str] = []
    else:
        coincidencias = puntajes[mejor_cat]

    # Prioridad: base por categoría y escalamiento de un nivel si hay palabras urgentes
    prioridad = PRIORIDAD_BASE[mejor_cat]
    urgentes = [p for p in PALABRAS_URGENTES if p in texto]
    if urgentes:
        idx = min(ORDEN_PRIORIDAD.index(prioridad) + 1, len(ORDEN_PRIORIDAD) - 1)
        prioridad = ORDEN_PRIORIDAD[idx]

    return {
        "categoria": mejor_cat,
        "prioridad": prioridad,
        "palabras_clave": coincidencias + urgentes,
    }


def extraer_datos(asunto: str, cuerpo: str) -> Dict[str, Optional[object]]:
    """
    Extrae entidades del texto con expresiones regulares.
    Cada campo que no se encuentre queda en None (null en JSON), nunca se inventa.
    """
    texto = f"{asunto}\n{cuerpo}"

    # Placa tipo mexicano: ABC-123-D (3 caracteres - 2/3 dígitos - 1/2 caracteres)
    m_placa = re.search(r"\b[A-Z0-9]{2,3}-\d{2,3}-[A-Z0-9]{1,2}\b", texto.upper())

    # ID interno de camión: CAM-102, CAM-7, etc.
    m_camion = re.search(r"\bCAM-\d+\b", texto.upper())

    # Peso reportado: "48.5 toneladas", "48,5 t", "32000 kg"
    m_peso = re.search(r"(\d+(?:[.,]\d+)?)\s*(toneladas|tonelada|ton|t|kg)\b", texto.lower())
    peso_kg: Optional[float] = None
    if m_peso:
        valor = float(m_peso.group(1).replace(",", "."))
        peso_kg = valor if m_peso.group(2) == "kg" else valor * 1000  # todo a kilogramos

    # Ubicación: "andén 3", "puerta B", "muelle 2", "caseta norte"
    m_ubic = re.search(r"\b(and[eé]n|puerta|muelle|caseta|dock)\s+([A-Za-z0-9]+)", texto, re.IGNORECASE)

    return {
        "placa": m_placa.group(0) if m_placa else None,
        "camion_id": m_camion.group(0) if m_camion else None,
        "peso_reportado_kg": peso_kg,
        "ubicacion": f"{m_ubic.group(1)} {m_ubic.group(2)}".lower() if m_ubic else None,
    }

def guardar_incidente_mongodb(
    remitente: str,
    asunto: str,
    cuerpo: str,
    clasificacion: Dict[str, object],
    datos_extraidos: Dict[str, Optional[object]]
):
    """
    Guarda un incidente clasificado en MongoDB.

    La información original, clasificación y datos extraídos
    quedan almacenados para consulta posterior desde la aplicación.
    """

    repositorio = IncidentesRepository()

    entidades = []

    if datos_extraidos.get("placa"):
        entidades.append(datos_extraidos["placa"])

    if datos_extraidos.get("camion_id"):
        entidades.append(datos_extraidos["camion_id"])

    if datos_extraidos.get("ubicacion"):
        entidades.append(datos_extraidos["ubicacion"])

    resumen = (
        f"Incidente clasificado como "
        f"{clasificacion['categoria']} con prioridad "
        f"{clasificacion['prioridad']}."
    )

    return repositorio.crear(
        correo_original=(
            f"Remitente: {remitente}\n"
            f"Asunto: {asunto}\n\n"
            f"{cuerpo}"
        ),
        categoria=str(clasificacion["categoria"]),
        prioridad=str(clasificacion["prioridad"]),
        entidades=entidades,
        resumen=resumen,
        estado="nuevo",
        datos_extraidos=datos_extraidos
    )



def enviar_correo_soporte(remitente: str, destinatario: str, asunto: str, cuerpo: str,
                          simulacion: bool = True) -> Dict[str, object]:
    """
    Envía un correo de soporte por SMTP.

    - simulacion=True  (por defecto): NO se conecta a ningún servidor; solo construye
      el mensaje. Ideal para clase y pruebas unitarias.
    - simulacion=False: usa variables de entorno SMTP_HOST, SMTP_PORT, SMTP_USER,
      SMTP_PASSWORD (nunca escribas contraseñas en el código).

    Devuelve un dict con el estado del envío (no lanza excepción por fallo de red;
    el fallo se reporta en el JSON final para no romper el flujo del sistema).
    """
    # Construcción del mensaje MIME estándar
    msg = EmailMessage()
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.set_content(cuerpo)

    if simulacion:
        log.info("Envío SIMULADO de correo a %s (asunto: %s)", destinatario, asunto)
        return {"enviado": True, "modo": "simulacion", "error": None}

    try:
        host = os.environ["SMTP_HOST"]
        puerto = int(os.environ.get("SMTP_PORT", "587"))
        usuario = os.environ["SMTP_USER"]
        clave = os.environ["SMTP_PASSWORD"]
        with smtplib.SMTP(host, puerto, timeout=15) as servidor:
            servidor.starttls()               # Cifra la conexión antes de autenticarse
            servidor.login(usuario, clave)
            servidor.send_message(msg)
        log.info("Correo enviado a %s", destinatario)
        return {"enviado": True, "modo": "smtp", "error": None}
    except (KeyError, OSError, smtplib.SMTPException) as exc:
        # KeyError: falta variable de entorno; OSError/SMTPException: fallo de red o servidor
        log.error("No se pudo enviar el correo: %s", exc)
        return {"enviado": False, "modo": "smtp", "error": f"{type(exc).__name__}: {exc}"}



def procesar_incidente(
    remitente: str,
    asunto: str,
    cuerpo: str,
    destinatario_soporte: str = "soporte@logismart.example",
    simulacion: bool = True,
    guardar: bool = False
) -> str:
    """
    FUNCIÓN PRINCIPAL DE LA SECCIÓN 3.

    Clasifica + extrae + envía correo de soporte y,
    opcionalmente, guarda el incidente en MongoDB.

    Devuelve estrictamente un JSON válido.
    """

    # =========================================================
    # 1. CLASIFICAR
    # =========================================================
    clasificacion = clasificar_incidente(asunto, cuerpo)

    # =========================================================
    # 2. EXTRAER DATOS
    # =========================================================
    datos = extraer_datos(asunto, cuerpo)

    # =========================================================
    # 3. GUARDAR EN MONGODB SI SE SOLICITA
    # =========================================================
    incidente_id = None

    if guardar:
        try:
            incidente_id = guardar_incidente_mongodb(
                remitente,
                asunto,
                cuerpo,
                clasificacion,
                datos
            )

            log.info(
                "Incidente guardado en MongoDB con ID: %s",
                incidente_id
            )

        except Exception as error:
            log.error(
                "No se pudo guardar el incidente en MongoDB: %s",
                error
            )

    # =========================================================
    # 4. PREPARAR CORREO DE SOPORTE
    # =========================================================
    asunto_soporte = (
        f"[{clasificacion['prioridad'].upper()}] "
        f"{clasificacion['categoria']} - {asunto}"
    )

    cuerpo_soporte = (
        f"Incidente reportado por: {remitente}\n"
        f"Categoría: {clasificacion['categoria']}\n"
        f"Prioridad: {clasificacion['prioridad']}\n"
        f"Datos extraídos: "
        f"{json.dumps(datos, ensure_ascii=False)}\n\n"
        f"Mensaje original:\n{cuerpo}"
    )

    # =========================================================
    # 5. ENVIAR CORREO
    # =========================================================
    envio = enviar_correo_soporte(
        remitente,
        destinatario_soporte,
        asunto_soporte,
        cuerpo_soporte,
        simulacion=simulacion
    )

    # =========================================================
    # 6. CONSTRUIR JSON FINAL
    # =========================================================
    resultado = {
        "fecha_procesamiento": datetime.now().isoformat(
            timespec="seconds"
        ),
        "incidente_id": (
            str(incidente_id)
            if incidente_id is not None
            else None
        ),
        "remitente": remitente,
        "asunto_original": asunto,
        "clasificacion": clasificacion,
        "datos_extraidos": datos,
        "correo_soporte": {
            "destinatario": destinatario_soporte,
            **envio
        },
    }

    # =========================================================
    # 7. VALIDAR QUE EL JSON SEA CORRECTO
    # =========================================================
    salida = json.dumps(
        resultado,
        ensure_ascii=False,
        indent=2
    )

    json.loads(salida)

    return salida
    
# =============================================================================
# SECCIÓN 4: EVALUACIÓN ÉTICA Y MATRIZ DE RIESGOS
# =============================================================================
# Matriz de riesgos: puntaje = probabilidad (1-5) x impacto (1-5)  -> rango 1..25
#   1-4  bajo | 5-9 medio | 10-16 alto | 17-25 crítico

@dataclass
class RiesgoEtico:
    """Un riesgo ético asociado a un módulo del sistema."""
    descripcion: str            # Ej. "Sesgo en visión nocturna"
    categoria: str              # Ej. "sesgo", "privacidad", "transparencia", "seguridad"
    probabilidad: int           # 1 (muy improbable) a 5 (casi seguro)
    impacto: int                # 1 (insignificante) a 5 (catastrófico)
    mitigacion: str = ""        # Acción propuesta para reducir el riesgo

    @property
    def puntaje(self) -> int:
        """Puntaje de la matriz = probabilidad x impacto."""
        return self.probabilidad * self.impacto

    @property
    def nivel(self) -> str:
        """Clasificación cualitativa según el puntaje."""
        p = self.puntaje
        if p >= 17:
            return "crítico"
        if p >= 10:
            return "alto"
        if p >= 5:
            return "medio"
        return "bajo"


@dataclass
class ModuloIA:
    """Módulo del sistema que se evalúa (con su lista de riesgos)."""
    nombre: str
    descripcion: str = ""
    riesgos: List[RiesgoEtico] = field(default_factory=list)


class EvaluadorRiesgosIA:
    """
    Registra módulos de un sistema de IA, sus riesgos éticos y genera reportes.

    Ejemplo:
        ev = EvaluadorRiesgosIA("LogiSmart")
        ev.registrar_modulo("Cámara de Detección de Somnolencia", "Visión por computadora")
        ev.registrar_riesgo("Cámara de Detección de Somnolencia",
                            "Sesgo en visión nocturna", "sesgo", 4, 4, "Entrenar con datos nocturnos diversos")
        print(ev.reporte_texto())
    """
    CATEGORIAS_VALIDAS = {"sesgo", "privacidad", "transparencia", "seguridad", "responsabilidad", "otro"}

    def __init__(self, nombre_sistema: str) -> None:
        self.nombre_sistema = nombre_sistema
        self._modulos: Dict[str, ModuloIA] = {}   # nombre -> módulo (evita duplicados)

    # ----------------------------- Registro ---------------------------------
    def registrar_modulo(self, nombre: str, descripcion: str = "") -> ModuloIA:
        """Da de alta un módulo. Lanza ValueError si ya existe o el nombre está vacío."""
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del módulo no puede estar vacío")
        if nombre in self._modulos:
            raise ValueError(f"El módulo '{nombre}' ya está registrado")
        modulo = ModuloIA(nombre=nombre.strip(), descripcion=descripcion)
        self._modulos[nombre] = modulo
        return modulo

    def registrar_riesgo(self, modulo: str, descripcion: str, categoria: str,
                         probabilidad: int, impacto: int, mitigacion: str = "") -> RiesgoEtico:
        """Asocia un riesgo ético a un módulo ya registrado (validando escalas 1-5)."""
        if modulo not in self._modulos:
            raise KeyError(f"El módulo '{modulo}' no existe; regístralo primero")
        if categoria not in self.CATEGORIAS_VALIDAS:
            raise ValueError(f"Categoría inválida '{categoria}'. Usa una de {sorted(self.CATEGORIAS_VALIDAS)}")
        for nombre, valor in (("probabilidad", probabilidad), ("impacto", impacto)):
            if not isinstance(valor, int) or isinstance(valor, bool) or not 1 <= valor <= 5:
                raise ValueError(f"{nombre} debe ser un entero entre 1 y 5")
        riesgo = RiesgoEtico(descripcion, categoria, probabilidad, impacto, mitigacion)
        self._modulos[modulo].riesgos.append(riesgo)
        return riesgo

    # ----------------------------- Consultas --------------------------------
    def todos_los_riesgos(self) -> List[tuple]:
        """Lista plana de (nombre_modulo, riesgo), ordenada de mayor a menor puntaje."""
        plano = [(m.nombre, r) for m in self._modulos.values() for r in m.riesgos]
        return sorted(plano, key=lambda par: par[1].puntaje, reverse=True)

    def resumen(self) -> Dict[str, object]:
        """Estadísticas agregadas del sistema evaluado."""
        riesgos = self.todos_los_riesgos()
        por_nivel = {"crítico": 0, "alto": 0, "medio": 0, "bajo": 0}
        por_categoria: Dict[str, int] = {}
        for _, r in riesgos:
            por_nivel[r.nivel] += 1
            por_categoria[r.categoria] = por_categoria.get(r.categoria, 0) + 1
        puntajes = [r.puntaje for _, r in riesgos]
        return {
            "sistema": self.nombre_sistema,
            "total_modulos": len(self._modulos),
            "total_riesgos": len(riesgos),
            "riesgos_por_nivel": por_nivel,
            "riesgos_por_categoria": por_categoria,
            "puntaje_promedio": round(sum(puntajes) / len(puntajes), 2) if puntajes else 0,
            "modulos_sin_evaluar": [m.nombre for m in self._modulos.values() if not m.riesgos],
        }

    # ----------------------------- Reportes ---------------------------------
    def reporte_texto(self) -> str:
        """Reporte resumido en texto plano, listo para imprimir o guardar."""
        r = self.resumen()
        L = []
        L.append("=" * 78)
        L.append(f"REPORTE DE RIESGOS ÉTICOS DE IA - {r['sistema']}")
        L.append(f"Generado: {datetime.now():%Y-%m-%d %H:%M}")
        L.append("=" * 78)
        L.append(f"Módulos: {r['total_modulos']} | Riesgos: {r['total_riesgos']} | "
                 f"Puntaje promedio: {r['puntaje_promedio']}")
        L.append("Por nivel: " + ", ".join(f"{k}={v}" for k, v in r["riesgos_por_nivel"].items()))
        L.append("Por categoría: " + (", ".join(f"{k}={v}" for k, v in r["riesgos_por_categoria"].items()) or "-"))
        if r["modulos_sin_evaluar"]:
            L.append("ATENCIÓN - Módulos sin riesgos evaluados: " + ", ".join(r["modulos_sin_evaluar"]))
        L.append("\nMATRIZ (ordenada de mayor a menor riesgo):")
        L.append(f"{'Módulo':<32}{'Riesgo':<34}{'P':>2}{'I':>3}{'Pts':>5}  Nivel")
        L.append("-" * 78)
        for modulo, riesgo in self.todos_los_riesgos():
            L.append(f"{modulo[:31]:<32}{riesgo.descripcion[:33]:<34}"
                     f"{riesgo.probabilidad:>2}{riesgo.impacto:>3}{riesgo.puntaje:>5}  {riesgo.nivel}")
        L.append("\nMITIGACIONES PROPUESTAS:")
        for modulo, riesgo in self.todos_los_riesgos():
            if riesgo.mitigacion:
                L.append(f"  - [{riesgo.nivel.upper()}] {modulo}: {riesgo.mitigacion}")
        return "\n".join(L)

    def exportar_json(self, ruta: Optional[str] = None) -> str:
        """Exporta el reporte completo en JSON. Si se da 'ruta', también lo guarda en archivo."""
        datos = {
            "resumen": self.resumen(),
            "modulos": [
                {"nombre": m.nombre, "descripcion": m.descripcion,
                 "riesgos": [{**asdict(r), "puntaje": r.puntaje, "nivel": r.nivel} for r in m.riesgos]}
                for m in self._modulos.values()
            ],
        }
        texto = json.dumps(datos, ensure_ascii=False, indent=2)
        if ruta:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(texto)
        return texto

    def exportar_texto(self, ruta: str) -> None:
        """Guarda el reporte de texto en un archivo .txt (UTF-8)."""
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(self.reporte_texto())


# =============================================================================
# PRUEBAS UNITARIAS
# =============================================================================
class TestSeccion2Logica(unittest.TestCase):
    """Verifica el motor de reglas contra una tabla de verdad escrita A MANO
    (independiente de la implementación) y contra propiedades lógicas."""

    # Tabla esperada (P,Q,R,S) -> (A,E). Orden V→F igual que la tabla impresa.
    ESPERADO = {
        (1, 1, 1, 1): (0, 1), (1, 1, 1, 0): (0, 1), (1, 1, 0, 1): (0, 1), (1, 1, 0, 0): (0, 1),
        (1, 0, 1, 1): (1, 1), (1, 0, 1, 0): (0, 1), (1, 0, 0, 1): (1, 0), (1, 0, 0, 0): (0, 0),
        (0, 1, 1, 1): (0, 0), (0, 1, 1, 0): (0, 0), (0, 1, 0, 1): (0, 0), (0, 1, 0, 0): (0, 0),
        (0, 0, 1, 1): (0, 0), (0, 0, 1, 0): (0, 0), (0, 0, 0, 1): (0, 0), (0, 0, 0, 0): (0, 0),
    }

    def test_tabla_completa(self):
        for (p, q, r, s), (a, e) in self.ESPERADO.items():
            res = evaluar_camion(bool(p), bool(q), bool(r), bool(s))
            self.assertEqual(res["acceso_estandar"], bool(a), f"A mal en {(p, q, r, s)}")
            self.assertEqual(res["inspeccion_especial"], bool(e), f"E mal en {(p, q, r, s)}")

    def test_sin_autorizacion_nunca_pasa(self):
        for q, r, s in itertools.product([True, False], repeat=3):
            res = evaluar_camion(False, q, r, s)
            self.assertFalse(res["acceso_estandar"])
            self.assertFalse(res["inspeccion_especial"])

    def test_sobrepeso_bloquea_acceso_estandar(self):
        for r, s in itertools.product([True, False], repeat=2):
            self.assertFalse(evaluar_camion(True, True, r, s)["acceso_estandar"])

    def test_caso_ambas_reglas_verdaderas(self):
        self.assertEqual(evaluar_camion(True, False, True, True),
                         {"acceso_estandar": True, "inspeccion_especial": True})

    def test_tipo_invalido(self):
        with self.assertRaises(TypeError):
            evaluar_camion(1, False, False, True)   # 1 no es bool estricto

    def test_tabla_verdad_tiene_16_filas(self):
        self.assertEqual(len(generar_tabla_verdad()), 16)

    def test_regla_certificacion(self):
        """C debe ser verdadera solo con P=True, T=True y Q=False."""
        self.assertTrue(
            evaluar_certificacion(True, True, False)
        )

        self.assertFalse(
            evaluar_certificacion(True, True, True)
        )

        self.assertFalse(
            evaluar_certificacion(False, True, False)
        )

        self.assertFalse(
            evaluar_certificacion(True, False, False)
        )

    def test_regla_horario_restringido(self):
        """H debe ser verdadera solo con R=True y HR=True."""
        self.assertTrue(
            evaluar_horario_restringido(True, True)
        )

        self.assertFalse(
            evaluar_horario_restringido(True, False)
        )

        self.assertFalse(
            evaluar_horario_restringido(False, True)
        )

        self.assertFalse(
            evaluar_horario_restringido(False, False)
        )


class TestSeccion3Incidentes(unittest.TestCase):
    """Verifica clasificación, extracción y que la salida sea JSON estricto."""

    CORREO = dict(
        remitente="operador@planta.example",
        asunto="URGENTE: derrame en andén 3",
        cuerpo="El camión CAM-102 con placas ABC-123-D presenta fuga de químico inflamable. "
               "La báscula marcó 48.5 toneladas.",
    )

    def test_salida_es_json_valido_y_solo_json(self):
        salida = procesar_incidente(**self.CORREO, simulacion=True)
        datos = json.loads(salida)          # Si hubiera texto extra, esto fallaría
        self.assertIsInstance(datos, dict)
        self.assertTrue(salida.lstrip().startswith("{") and salida.rstrip().endswith("}"))

    def test_clasificacion_y_extraccion(self):
        datos = json.loads(procesar_incidente(**self.CORREO, simulacion=True))
        self.assertEqual(datos["clasificacion"]["categoria"], "materiales_peligrosos")
        self.assertEqual(datos["clasificacion"]["prioridad"], "critica")  # ya era crítica, no excede
        self.assertEqual(datos["datos_extraidos"]["placa"], "ABC-123-D")
        self.assertEqual(datos["datos_extraidos"]["camion_id"], "CAM-102")
        self.assertEqual(datos["datos_extraidos"]["peso_reportado_kg"], 48500.0)
        self.assertEqual(datos["datos_extraidos"]["ubicacion"], "andén 3")
        self.assertTrue(datos["correo_soporte"]["enviado"])

    def test_campos_faltantes_son_null(self):
        datos = json.loads(procesar_incidente("a@b.c", "Consulta", "Hola, tengo una duda general.",
                                              simulacion=True))
        self.assertEqual(datos["clasificacion"]["categoria"], "otro")
        self.assertIsNone(datos["datos_extraidos"]["placa"])
        self.assertIsNone(datos["datos_extraidos"]["peso_reportado_kg"])

    def test_urgencia_escala_prioridad(self):
        normal = clasificar_incidente("Pantalla lenta", "El sistema carga lento")
        urgente = clasificar_incidente("Pantalla lenta urgente", "El sistema carga lento")
        self.assertEqual(normal["prioridad"], "baja")
        self.assertEqual(urgente["prioridad"], "media")

    def test_fallo_smtp_no_rompe_json(self):
        # Sin variables de entorno SMTP, el envío real falla pero el JSON sigue siendo válido
        for var in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"):
            os.environ.pop(var, None)
        datos = json.loads(procesar_incidente(**self.CORREO, simulacion=False))
        self.assertFalse(datos["correo_soporte"]["enviado"])
        self.assertIsNotNone(datos["correo_soporte"]["error"])


class TestSeccion4Riesgos(unittest.TestCase):
    """Verifica el registro, validaciones, cálculos y exportación de la matriz."""

    def setUp(self):
        self.ev = EvaluadorRiesgosIA("LogiSmart")
        self.ev.registrar_modulo("Cámara de Detección de Somnolencia", "Visión por computadora")
        self.ev.registrar_modulo("Lector de Placas")

    def test_puntaje_y_nivel(self):
        r = self.ev.registrar_riesgo("Cámara de Detección de Somnolencia",
                                     "Sesgo en visión nocturna", "sesgo", 4, 5)
        self.assertEqual(r.puntaje, 20)
        self.assertEqual(r.nivel, "crítico")

    def test_niveles_limite(self):
        casos = {(1, 4): "bajo", (1, 5): "medio", (2, 5): "alto", (4, 4): "alto", (5, 4): "crítico"}
        for (p, i), esperado in casos.items():
            self.assertEqual(RiesgoEtico("x", "otro", p, i).nivel, esperado, f"{(p, i)}")

    def test_validaciones(self):
        with self.assertRaises(KeyError):
            self.ev.registrar_riesgo("No existe", "x", "sesgo", 1, 1)
        with self.assertRaises(ValueError):
            self.ev.registrar_riesgo("Lector de Placas", "x", "sesgo", 6, 1)
        with self.assertRaises(ValueError):
            self.ev.registrar_riesgo("Lector de Placas", "x", "inventada", 1, 1)
        with self.assertRaises(ValueError):
            self.ev.registrar_modulo("Lector de Placas")     # duplicado
        with self.assertRaises(ValueError):
            self.ev.registrar_modulo("   ")                  # vacío

    def test_resumen_y_orden(self):
        self.ev.registrar_riesgo("Lector de Placas", "Fuga de datos de placas", "privacidad", 2, 3)
        self.ev.registrar_riesgo("Cámara de Detección de Somnolencia",
                                 "Vigilancia excesiva del conductor", "privacidad", 4, 4)
        res = self.ev.resumen()
        self.assertEqual(res["total_riesgos"], 2)
        self.assertEqual(res["riesgos_por_categoria"], {"privacidad": 2})
        self.assertEqual(self.ev.todos_los_riesgos()[0][1].puntaje, 16)   # el mayor primero

    def test_modulo_sin_riesgos_se_reporta(self):
        self.ev.registrar_riesgo("Lector de Placas", "x", "otro", 1, 1)
        self.assertIn("Cámara de Detección de Somnolencia", self.ev.resumen()["modulos_sin_evaluar"])

    def test_exportar_json_valido(self):
        self.ev.registrar_riesgo("Lector de Placas", "Error de lectura", "seguridad", 3, 3, "Revisión manual")
        datos = json.loads(self.ev.exportar_json())
        self.assertEqual(datos["resumen"]["total_riesgos"], 1)
        self.assertEqual(datos["modulos"][1]["riesgos"][0]["nivel"], "medio")

    def test_reporte_texto_contiene_datos(self):
        self.ev.registrar_riesgo("Lector de Placas", "Error de lectura", "seguridad", 3, 3, "Revisión manual")
        texto = self.ev.reporte_texto()
        self.assertIn("Error de lectura", texto)
        self.assertIn("Revisión manual", texto)


# =============================================================================
# DEMOSTRACIÓN COMPLETA
# =============================================================================
def demo() -> None:
    """Ejecuta las 4 secciones con datos de ejemplo."""
    # ---- Sección 1 ----
    imprimir_peas()

    # ---- Sección 2 ----
    imprimir_tablas_verdad()
    print("Ejemplos del motor de reglas:")
    casos = [
        ("Autorizado, conductor certificado, peso OK, sin peligrosos", (True, False, False, True)),
        ("Autorizado, peso excedido", (True, True, False, True)),
        ("Autorizado, peso OK, carga peligrosa", (True, False, True, True)),
        ("Sin autorización previa", (False, False, False, True)),
    ]
    for descripcion, (P, Q, R, S) in casos:
        res = evaluar_camion(P, Q, R, S)
        print(f"  {descripcion}\n     -> P={P} Q={Q} R={R} S={S} => "
              f"Acceso estándar={res['acceso_estandar']}, Inspección especial={res['inspeccion_especial']}")

    # ---- Sección 3 ----
    print("\n" + "=" * 78)
    print("SECCIÓN 3 - CLASIFICADOR DE INCIDENTES (salida JSON estricta)")
    print("=" * 78)
    salida_json = procesar_incidente(
        remitente="operador.caseta@logismart.example",
        asunto="URGENTE: derrame en andén 3",
        cuerpo=("El camión CAM-102 con placas ABC-123-D presenta una fuga de químico inflamable. "
                "La báscula marcó 48.5 toneladas. Se requiere apoyo inmediato."),
        simulacion=True,     # Cambia a False y define SMTP_* para enviar de verdad
    )
    print(salida_json)

    # ---- Sección 4 ----
    print("\n" + "=" * 78)
    print("SECCIÓN 4 - EVALUACIÓN ÉTICA")
    print("=" * 78)
    ev = EvaluadorRiesgosIA("LogiSmart Python Suite")
    cam = "Cámara de Detección de Somnolencia"
    lpr = "Lector de Placas (LPR)"
    clas = "Clasificador de Incidentes"
    ev.registrar_modulo(cam, "Visión por computadora que monitorea al conductor")
    ev.registrar_modulo(lpr, "Reconoce placas para validar autorización previa")
    ev.registrar_modulo(clas, "Clasifica correos de soporte y extrae datos")
    ev.registrar_riesgo(cam, "Sesgo en visión nocturna (falsos positivos por tono de piel / poca luz)",
                        "sesgo", 4, 4, "Entrenar y auditar con datos nocturnos y diversos; umbral ajustable")
    ev.registrar_riesgo(cam, "Violación de privacidad (video continuo del conductor)",
                        "privacidad", 4, 5, "Procesar en el borde, no almacenar video, aviso y consentimiento")
    ev.registrar_riesgo(lpr, "Lectura errónea que niega acceso injustificadamente",
                        "responsabilidad", 3, 3, "Revisión humana y canal de apelación")
    ev.registrar_riesgo(lpr, "Conservación indebida de datos de placas",
                        "privacidad", 2, 4, "Política de retención y cifrado")
    ev.registrar_riesgo(clas, "Priorizar mal un incidente crítico (falso negativo)",
                        "seguridad", 2, 5, "Palabras críticas siempre escalan; revisión humana de 'otro'")
    print(ev.reporte_texto())
    ev.exportar_texto("reporte_riesgos.txt")
    ev.exportar_json("reporte_riesgos.json")
    print("\n(Archivos generados: reporte_riesgos.txt y reporte_riesgos.json)")


if __name__ == "__main__":
    if "--tests" in sys.argv:
        # Quita nuestro flag para que unittest no lo interprete como argumento suyo
        unittest.main(argv=[sys.argv[0], "-v"])
    else:
        demo()
        print("\n" + "=" * 78)
        print("PRUEBAS UNITARIAS")
        print("=" * 78)
        suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
        unittest.TextTestRunner(verbosity=2).run(suite)