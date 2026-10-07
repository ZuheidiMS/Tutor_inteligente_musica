"""
Generador de reportes JSON, CSV y PDF.
"""

import csv
import json
import os
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class ReportGenerator:

    def __init__(self, db):
        self.db = db

        self.colecciones = [
            "camiones",
            "accesos",
            "incidentes",
            "riesgos_eticos",
            "evaluaciones_llm"
        ]

    def obtener_datos(self):
        datos = {}

        for nombre in self.colecciones:
            documentos = list(
                self.db[nombre].find()
            )

            for documento in documentos:
                if "_id" in documento:
                    documento["_id"] = str(documento["_id"])

                for clave, valor in documento.items():
                    if isinstance(valor, datetime):
                        documento[clave] = valor.isoformat()

            datos[nombre] = documentos

        return datos

    def generar_json(self, ruta):
        datos = self.obtener_datos()

        with open(
            ruta,
            "w",
            encoding="utf-8"
        ) as archivo:
            json.dump(
                datos,
                archivo,
                ensure_ascii=False,
                indent=4
            )

        return ruta

    def generar_csv(self, ruta):
        datos = self.obtener_datos()

        with open(
            ruta,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as archivo:

            escritor = csv.writer(archivo)

            escritor.writerow([
                "coleccion",
                "id",
                "datos"
            ])

            for coleccion, documentos in datos.items():

                for documento in documentos:

                    identificador = documento.pop(
                        "_id",
                        ""
                    )

                    escritor.writerow([
                        coleccion,
                        identificador,
                        json.dumps(
                            documento,
                            ensure_ascii=False
                        )
                    ])

        return ruta

    def generar_pdf(self, ruta):
        datos = self.obtener_datos()

        pdf = canvas.Canvas(
            ruta,
            pagesize=letter
        )

        ancho, alto = letter

        y = alto - 50

        pdf.setFont(
            "Helvetica-Bold",
            16
        )

        pdf.drawString(
            50,
            y,
            "LogiSmart - Reporte general"
        )

        y -= 35

        pdf.setFont(
            "Helvetica",
            10
        )

        pdf.drawString(
            50,
            y,
            f"Generado: {datetime.now():%d/%m/%Y %H:%M}"
        )

        y -= 30

        for coleccion, documentos in datos.items():

            pdf.setFont(
                "Helvetica-Bold",
                12
            )

            pdf.drawString(
                50,
                y,
                f"{coleccion}: {len(documentos)} registros"
            )

            y -= 25

            if y < 60:
                pdf.showPage()
                y = alto - 50

        pdf.save()

        return ruta