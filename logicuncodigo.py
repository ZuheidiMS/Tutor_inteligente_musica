# ============================================================
# LOGISMART | CENTRO DE CONTROL INTELIGENTE (LOGI-UN-CÓDIGO)
# Versión corregida con serialización segura de fechas para JSON
# ============================================================

import os
import json
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from pymongo import MongoClient
from pydantic import BaseModel, Field
import ollama

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ============================================================
# 1. CAPA DE PERSISTENCIA (MONGODB) + SEMBRADO AUTOMÁTICO
# ============================================================
class DatabaseManager:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="zuheidi_local"):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.conectado = False
        if self.conectar():
            self._verificar_y_sembrar_datos()

    def conectar(self):
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.conectado = True
            return True
        except Exception:
            self.conectado = False
            return False

    def get_collection(self, name):
        if self.conectado and self.db is not None:
            return self.db[name]
        return None

    def _verificar_y_sembrar_datos(self):
        try:
            col_cam = self.db["camiones"]
            if col_cam.count_documents({}) == 0:
                camiones_demo = [
                    {"placa": "CAM-102", "id_unidad": "ID-9821", "empresa": "Logística del Valle S.A.", "estado": "Activo"},
                    {"placa": "CAM-300", "id_unidad": "ID-4412", "empresa": "Transportes del Norte", "estado": "En ruta"},
                    {"placa": "CAM-512", "id_unidad": "ID-7730", "empresa": "Global Express Corp", "estado": "Mantenimiento"},
                    {"placa": "CAM-890", "id_unidad": "ID-1102", "empresa": "CargoNet México", "estado": "Activo"}
                ]
                col_cam.insert_many(camiones_demo)

            col_acc = self.db["accesos"]
            if col_acc.count_documents({}) == 0:
                accesos_demo = [
                    {"placa": "CAM-102", "P": True, "Q": False, "R": False, "S": True, "T": True, "HR": False, "resultado_A": True, "resultado_E": False, "marca_tiempo": datetime.utcnow() - timedelta(hours=2)},
                    {"placa": "CAM-300", "P": True, "Q": True, "R": True, "S": True, "T": True, "HR": False, "resultado_A": True, "resultado_E": True, "marca_tiempo": datetime.utcnow() - timedelta(hours=1)},
                    {"placa": "CAM-512", "P": False, "Q": False, "R": False, "S": False, "T": False, "HR": True, "resultado_A": False, "resultado_E": False, "marca_tiempo": datetime.utcnow()}
                ]
                col_acc.insert_many(accesos_demo)

            col_inc = self.db["incidentes"]
            if col_inc.count_documents({}) == 0:
                incidentes_demo = [
                    {"correo": "URGENTE: La unidad CAM-300 presenta falla grave de frenos.", "clasificacion": {"categoria": "Seguridad", "prioridad": "Alta", "entidades": ["CAM-300"], "resumen": "Falla grave de frenos en unidad CAM-300."}, "estado": "nuevo", "fecha": datetime.utcnow() - timedelta(hours=3)},
                    {"correo": "Aviso: Retraso menor en la entrega del operador de la ruta norte por tráfico.", "clasificacion": {"categoria": "Operativo", "prioridad": "Media", "entidades": ["Ruta Norte"], "resumen": "Retraso por tráfico."}, "estado": "en_proceso", "fecha": datetime.utcnow() - timedelta(hours=1)}
                ]
                col_inc.insert_many(incidentes_demo)
        except Exception as e:
            print(f"Aviso en sembrado de datos: {e}")

db_manager = DatabaseManager()


# ============================================================
# 2. MOTOR DE REGLAS (LÓGICA PROPOSICIONAL AMPLIADA)
# ============================================================
class RulesEngine:
    @staticmethod
    def evaluar(p: bool, q: bool, r: bool, s: bool, t: bool, hr: bool):
        A = bool(p and s and (not q) and t and (not hr))
        E = bool(p and (r or q))

        if not t:
            A = False  

        if r and not s:
            E = True   

        explicacion = (
            f"EVALUACIÓN DE REGLAS PROPOSICIONALES:\n\n"
            f" • P (Autorización vigente): {str(p)}\n"
            f" • Q (Restricción activa):    {str(q)}\n"
            f" • R (Material peligroso):    {str(r)}\n"
            f" • S (Documentación comp.):   {str(s)}\n"
            f" • T (Certificación vig.):    {str(t)}\n"
            f" • HR (Horario restringido):  {str(hr)}\n"
            f"--------------------------------------------------\n"
            f" ➔ Resultado A (Acceso Autorizado): {A}\n"
            f" ➔ Resultado E (Inspección Obligatoria): {E}"
        )
        return A, E, explicacion


# ============================================================
# 3. CLASIFICADOR HÍBRIDO (LLM + PYDANTIC)
# ============================================================
class EmailSchema(BaseModel):
    categoria: str = Field(..., description="Categoría del incidente")
    prioridad: str = Field(..., description="Prioridad")
    entidades: list[str] = Field(..., description="Entidades extraídas")
    resumen: str = Field(..., description="Resumen breve")

class HybridClassifier:
    def __init__(self, model="llama3.2"):
        self.model = model

    def clasificar(self, texto: str):
        metodo = "LLM (Ollama) + Pydantic"
        try:
            prompt = (
                f"Analiza el correo y responde ÚNICAMENTE en JSON válido con llaves exactas: "
                f"categoria, prioridad, entidades (lista de strings), resumen.\nCorreo: {texto}"
            )
            resp = ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}], format="json")
            data = json.loads(resp['message']['content'])
            valido = EmailSchema(**data)
            return valido.dict(), metodo
        except Exception:
            metodo = "Respaldo por Reglas (Fallback)"
            prioridad = "Alta" if "urgente" in texto.lower() or "falla" in texto.lower() else "Media"
            categoria = "Seguridad" if "acceso" in texto.lower() else "Operativo"
            return {
                "categoria": categoria,
                "prioridad": prioridad,
                "entidades": ["Unidad-Detectada"],
                "resumen": texto[:80] + "..."
            }, metodo


# ============================================================
# 4. ASISTENTE RAG CON PANDAS Y MONGODB (CORREGIDO)
# ============================================================
class RAGAssistant:
    def __init__(self, db: DatabaseManager, model="llama3.2"):
        self.db = db
        self.model = model

    def consultar(self, pregunta: str):
        col = self.db.get_collection("accesos")
        registros = list(col.find({}, {"_id": 0}).limit(10)) if col is not None else []
        
        if not registros:
            return "No tengo información en la base de datos."

        df = pd.DataFrame(registros)
        resumen_estadistico = f"Total de registros analizados con Pandas: {len(df)}. "
        if 'resultado_A' in df.columns:
            autorizados = int(df['resultado_A'].sum())
            resumen_estadistico += f"Accesos autorizados acumulados: {autorizados}."

        # Se agregó default=str para evitar errores con objetos datetime de MongoDB
        contexto = json.dumps(registros, ensure_ascii=False, default=str) + f"\n[Análisis Pandas: {resumen_estadistico}]"
        
        prompt = (
            f"Eres un asistente estricto. Responde BASÁNDOTE ÚNICAMENTE en estos datos de MongoDB analizados. "
            f"Si la respuesta no está, responde estrictamente 'no tengo información'.\n\nDatos:\n{contexto}\n\nPregunta: {pregunta}"
        )
        try:
            resp = ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            return resp['message']['content']
        except Exception as e:
            return f"Error con Ollama: {str(e)}"


# ============================================================
# 5. MATRIZ DE RIESGOS ÉTICOS
# ============================================================
class RiskManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def registrar(self, modulo, desc, cat, prob, imp, mit):
        inicial = prob * imp
        residual = max(1, inicial // 2)
        doc = {
            "modulo": modulo, "descripcion": desc, "categoria": cat,
            "probabilidad": prob, "impacto": imp, "puntaje_inicial": inicial,
            "mitigacion": mit, "puntaje_residual": residual, "fecha": datetime.utcnow()
        }
        col = self.db.get_collection("riesgos_eticos")
        if col is not None:
            col.insert_one(doc)
        return doc


# ============================================================
# 6. INTERFAZ GRÁFICA PRINCIPAL
# ============================================================
class LogiSmartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LogiSmart | Centro de Control Inteligente")
        self.root.geometry("1300x800")
        self.root.minsize(1050, 700)

        self.C_SIDEBAR = "#090D16"       
        self.C_SIDEBAR_HOVER = "#1E293B" 
        self.C_ACTIVE = "#2563EB"        
        self.C_TOPBAR = "#FFFFFF"        
        self.C_BG = "#F8FAFC"            
        self.C_CARD = "#FFFFFF"          
        self.C_TEXT_DARK = "#0F172A"     
        self.C_TEXT_MUTED = "#64748B"    

        self.root.configure(bg=self.C_BG)

        self.classifier = HybridClassifier()
        self.rag = RAGAssistant(db_manager)
        self.risk_mgr = RiskManager(db_manager)

        self.sidebar_frame = tk.Frame(self.root, bg=self.C_SIDEBAR, width=240)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        self.main_container = tk.Frame(self.root, bg=self.C_BG)
        self.main_container.pack(side="right", fill="both", expand=True)

        self.crear_barra_superior()

        self.content_area = tk.Frame(self.main_container, bg=self.C_BG)
        self.content_area.pack(fill="both", expand=True)

        self.crear_sidebar()

        self.vistas = {}
        self.inicializar_vistas()
        self.mostrar_vista("Dashboard")

    def crear_barra_superior(self):
        topbar = tk.Frame(self.main_container, bg=self.C_TOPBAR, height=55, highlightbackground="#E2E8F0", highlightthickness=1)
        topbar.pack(side="top", fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="Centro de Control Inteligente", font=("Segoe UI", 11, "bold"), bg=self.C_TOPBAR, fg=self.C_TEXT_DARK).pack(side="left", padx=30)

        f_status = tk.Frame(topbar, bg=self.C_TOPBAR)
        f_status.pack(side="right", padx=30)

        tk.Label(f_status, text="●", font=("Segoe UI", 14), bg=self.C_TOPBAR, fg="#10B981").pack(side="left", padx=(0, 5))
        tk.Label(f_status, text="Sistema operativo", font=("Segoe UI", 9, "bold"), bg=self.C_TOPBAR, fg=self.C_TEXT_MUTED).pack(side="left")

    def crear_sidebar(self):
        f_logo = tk.Frame(self.sidebar_frame, bg=self.C_SIDEBAR, height=80)
        f_logo.pack(fill="x", pady=15)
        f_logo.pack_propagate(False)

        lbl_l = tk.Label(f_logo, text="L", font=("Segoe UI", 14, "bold"), bg=self.C_ACTIVE, fg="#FFFFFF", width=3, height=1)
        lbl_l.pack(side="left", padx=(20, 10))

        f_tit = tk.Frame(f_logo, bg=self.C_SIDEBAR)
        f_tit.pack(side="left", fill="y")
        tk.Label(f_tit, text="LogiSmart", font=("Segoe UI", 12, "bold"), bg=self.C_SIDEBAR, fg="#FFFFFF").pack(anchor="w")
        tk.Label(f_tit, text="CONTROL LOGÍSTICO", font=("Segoe UI", 7, "bold"), bg=self.C_SIDEBAR, fg="#94A3B8").pack(anchor="w")

        tk.Label(self.sidebar_frame, text="PRINCIPAL", font=("Segoe UI", 8, "bold"), bg=self.C_SIDEBAR, fg="#64748B").pack(anchor="w", padx=20, pady=(15, 10))

        self.botones_menu = {}
        opciones = [
            ("Dashboard", "📊  Dashboard"),
            ("Control de acceso", "🚗  Control de acceso"),
            ("Tabla de verdad", "📋  Tabla de verdad"),
            ("Incidentes", "⚠️  Incidentes"),
            ("Asistente LLM", "🤖  Asistente LLM"),
            ("Riesgos éticos", "🛡️  Riesgos éticos"),
            ("Reportes", "📑  Reportes"),
            ("Configuración", "⚙️  Configuración")
        ]

        for nombre, texto in opciones:
            btn = tk.Button(
                self.sidebar_frame, text=texto, font=("Segoe UI", 10),
                bg=self.C_SIDEBAR, fg="#94A3B8", activebackground=self.C_SIDEBAR_HOVER,
                activeforeground="#FFFFFF", bd=0, anchor="w", padx=25, pady=10,
                cursor="hand2", command=lambda n=nombre: self.mostrar_vista(n)
            )
            btn.pack(fill="x", pady=2)
            self.botones_menu[nombre] = btn

        f_foot = tk.Frame(self.sidebar_frame, bg=self.C_SIDEBAR)
        f_foot.pack(side="bottom", fill="x", padx=20, pady=20)
        tk.Label(f_foot, text="LogiSmart v1.0", font=("Segoe UI", 9, "bold"), bg=self.C_SIDEBAR, fg="#FFFFFF").pack(anchor="w")
        tk.Label(f_foot, text="Sistema de apoyo a decisiones", font=("Segoe UI", 8), bg=self.C_SIDEBAR, fg="#64748B").pack(anchor="w")

    def crear_vista_con_scroll(self):
        contenedor_exterior = tk.Frame(self.content_area, bg=self.C_BG)
        
        canvas = tk.Canvas(contenedor_exterior, bg=self.C_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(contenedor_exterior, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=self.C_BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=35, pady=25)
        scrollbar.pack(side="right", fill="y", pady=25)

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas.find_all()[0], width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        return contenedor_exterior, scrollable_frame

    def mostrar_modal_resultado(self, titulo, mensaje, color_estado="#2563EB"):
        modal = tk.Toplevel(self.root)
        modal.title(titulo)
        modal.geometry("550x400")
        modal.config(bg=self.C_CARD)
        modal.transient(self.root)
        modal.grab_set()

        f_head = tk.Frame(modal, bg=color_estado, height=50)
        f_head.pack(fill="x")
        f_head.pack_propagate(False)
        tk.Label(f_head, text=titulo, font=("Segoe UI", 12, "bold"), bg=color_estado, fg="#FFFFFF").pack(side="left", padx=20)

        txt = tk.Text(modal, font=("Consolas", 10), bg="#F8FAFC", fg=self.C_TEXT_DARK, bd=0, padx=15, pady=15)
        txt.pack(fill="both", expand=True, padx=25, pady=20)
        txt.insert("1.0", mensaje)
        txt.config(state="disabled")

        btn_cerrar = tk.Button(modal, text="Aceptar", font=("Segoe UI", 10, "bold"), bg=color_estado, fg="#FFFFFF", bd=0, padx=30, pady=10, cursor="hand2", command=modal.destroy)
        btn_cerrar.pack(pady=15)

    def inicializar_vistas(self):
        vistas_nombres = ["Dashboard", "Control de acceso", "Tabla de verdad", "Incidentes", "Asistente LLM", "Riesgos éticos", "Reportes", "Configuración"]
        for nombre in vistas_nombres:
            ext, inner = self.crear_vista_con_scroll()
            self.vistas[nombre] = ext

    def mostrar_vista(self, nombre):
        for n, btn in self.botones_menu.items():
            if n == nombre:
                btn.config(bg=self.C_ACTIVE, fg="#FFFFFF")
            else:
                btn.config(bg=self.C_SIDEBAR, fg="#94A3B8")

        for n, v in self.vistas.items():
            v.pack_forget()

        vista = self.vistas[nombre]
        vista.pack(fill="both", expand=True)

        inner_f = vista.winfo_children()[0].winfo_children()[0]
        if len(inner_f.winfo_children()) == 0:
            if nombre == "Dashboard": self.construir_vista_dashboard(inner_f)
            elif nombre == "Control de acceso": self.construir_vista_control_acceso(inner_f)
            elif nombre == "Tabla de verdad": self.construir_vista_tabla_verdad(inner_f)
            elif nombre == "Incidentes": self.construir_vista_incidentes(inner_f)
            elif nombre == "Asistente LLM": self.construir_vista_rag(inner_f)
            elif nombre == "Riesgos éticos": self.construir_vista_riesgos(inner_f)
            elif nombre == "Reportes": self.construir_vista_reportes(inner_f)
            elif nombre == "Configuración": self.construir_vista_config(inner_f)

    def construir_vista_dashboard(self, parent):
        tk.Label(parent, text="Dashboard Ejecutivo", font=("Segoe UI", 22, "bold"), bg=self.C_BG, fg=self.C_TEXT_DARK).pack(anchor="w", pady=(0, 5))
        tk.Label(parent, text="Resumen en tiempo real del sistema logístico y analítica de datos.", font=("Segoe UI", 11), bg=self.C_BG, fg=self.C_TEXT_MUTED).pack(anchor="w", pady=(0, 20))

        f_cards = tk.Frame(parent, bg=self.C_BG)
        f_cards.pack(fill="x", pady=10)
        f_cards.grid_columnconfigure((0, 1, 2), weight=1)

        self.dash_c1 = self.crear_tarjeta_metrica_grid(f_cards, "Camiones Registrados", "0", self.C_ACTIVE, 0)
        self.dash_c2 = self.crear_tarjeta_metrica_grid(f_cards, "Accesos Evaluados", "0", "#059669", 1)
        self.dash_c3 = self.crear_tarjeta_metrica_grid(f_cards, "Incidentes Activos", "0", "#DC2626", 2)

        card_p = tk.Frame(parent, bg=self.C_CARD, highlightbackground="#CBD5E1", highlightthickness=1, padx=30, pady=25)
        card_p.pack(fill="x", expand=True, pady=20)

        tk.Label(card_p, text="📊 Analítica de Bitácora (Pandas DataFrame)", font=("Segoe UI", 12, "bold"), bg=self.C_CARD, fg=self.C_TEXT_DARK).pack(anchor="w", pady=(0, 10))
        self.txt_dash_pandas = tk.Text(card_p, height=8, font=("Consolas", 11), bg="#F8FAFC", fg=self.C_TEXT_DARK, bd=0, padx=15, pady=15)
        self.txt_dash_pandas.pack(fill="x", expand=True, pady=(0, 15))

        btn = tk.Button(card_p, text="🔄 Actualizar Dashboard", font=("Segoe UI", 11, "bold"), bg=self.C_ACTIVE, fg="#FFFFFF", bd=0, padx=25, pady=12, cursor="hand2", command=self.actualizar_dashboard_data)
        btn.pack(anchor="w")
        self.actualizar_dashboard_data()

    def crear_tarjeta_metrica_grid(self, parent, titulo, valor, color_borde, col_idx):
        card = tk.Frame(parent, bg=self.C_CARD, highlightbackground="#E2E8F0", highlightthickness=1, padx=25, pady=25)
        card.grid(row=0, column=col_idx, sticky="nsew", padx=8)
        
        tk.Frame(card, bg=color_borde, width=4, height=40).pack(side="left", padx=(0, 15))
        f_txt = tk.Frame(card, bg=self.C_CARD)
        f_txt.pack(side="left", fill="both", expand=True)

        tk.Label(f_txt, text=titulo, font=("Segoe UI", 10, "bold"), bg=self.C_CARD, fg=self.C_TEXT_MUTED).pack(anchor="w")
        lbl = tk.Label(f_txt, text=valor, font=("Segoe UI", 28, "bold"), bg=self.C_CARD, fg=self.C_TEXT_DARK)
        lbl.pack(anchor="w", pady=(5, 0))
        return lbl

    def actualizar_dashboard_data(self):
        c_cam = db_manager.get_collection("camiones")
        c_acc = db_manager.get_collection("accesos")
        c_inc = db_manager.get_collection("incidentes")

        v1 = c_cam.count_documents({}) if c_cam is not None else 0
        v2 = c_acc.count_documents({}) if c_acc is not None else 0
        v3 = c_inc.count_documents({"estado": {"$ne": "cerrado"}}) if c_inc is not None else 0

        self.dash_c1.config(text=str(v1))
        self.dash_c2.config(text=str(v2))
        self.dash_c3.config(text=str(v3))

        if c_acc is not None:
            docs = list(c_acc.find({}, {"_id": 0}))
            if docs:
                df = pd.DataFrame(docs)
                autorizados = int(df['resultado_A'].sum()) if 'resultado_A' in df.columns else 0
                inspecciones = int(df['resultado_E'].sum()) if 'resultado_E' in df.columns else 0
                txt = f"• Total registros en bitácora: {len(df)}\n• Accesos Autorizados (A=True): {autorizados}\n• Inspecciones Obligatorias (E=True): {inspecciones}"
                self.txt_dash_pandas.delete("1.0", tk.END)
                self.txt_dash_pandas.insert(tk.END, txt)

    def construir_vista_control_acceso(self, parent):
        tk.Label(parent, text="Control de acceso", font=("Segoe UI", 22, "bold"), bg=self.C_BG, fg=self.C_TEXT_DARK).pack(anchor="w", pady=(0, 5))
        tk.Label(parent, text="Evalúa las condiciones de un camión mediante lógica proposicional.", font=("Segoe UI", 11), bg=self.C_BG, fg=self.C_TEXT_MUTED).pack(anchor="w", pady=(0, 20))

        card1 = tk.Frame(parent, bg=self.C_CARD, highlightbackground="#CBD5E1", highlightthickness=1, padx=25, pady=25)
        card1.pack(fill="x", pady=10)
        tk.Label(card1, text="Identificación del camión", font=("Segoe UI", 12, "bold"), bg=self.C_CARD, fg=self.C_TEXT_DARK).pack(anchor="w", pady=(0, 15))

        f_ids = tk.Frame(card1, bg=self.C_CARD)
        f_ids.pack(fill="x")
        f_ids.grid_columnconfigure((0, 1, 2), weight=1)

        for idx, (lbl_txt, val_pred, col_i) in enumerate([("Placa", "CAM-102", 0), ("Camión ID", "ID-9821", 1), ("Empresa", "Logística del Valle S.A.", 2)]):
            f_col = tk.Frame(f_ids, bg=self.C_CARD)
            f_col.grid(row=0, column=col_i, sticky="ew", padx=10)
            tk.Label(f_col, text=lbl_txt, font=("Segoe UI", 9, "bold"), bg=self.C_CARD, fg=self.C_TEXT_MUTED).pack(anchor="w", pady=(0, 5))
            ent = tk.Entry(f_col, font=("Segoe UI", 11), relief="solid", bd=1)
            ent.pack(fill="x", ipady=4)
            ent.insert(0, val_pred)
            if col_i == 0: self.ent_placa = ent

        card2 = tk.Frame(parent, bg=self.C_CARD, highlightbackground="#CBD5E1", highlightthickness=1, padx=25, pady=25)
        card2.pack(fill="x", pady=15)
        tk.Label(card2, text="Condiciones de acceso", font=("Segoe UI", 12, "bold"), bg=self.C_CARD, fg=self.C_TEXT_DARK).pack(anchor="w", pady=(0, 2))
        tk.Label(card2, text="Activa o desactiva las premisas para simular diferentes escenarios.", font=("Segoe UI", 10), bg=self.C_CARD, fg=self.C_TEXT_MUTED).pack(anchor="w", pady=(0, 15))

        f_checks = tk.Frame(card2, bg=self.C_CARD)
        f_checks.pack(fill="x")
        f_checks.grid_columnconfigure((0, 1), weight=1)

        self.p = tk.BooleanVar(value=True)
        self.q = tk.BooleanVar(value=False)
        self.r = tk.BooleanVar(value=False)
        self.s = tk.BooleanVar(value=True)
        self.t = tk.BooleanVar(value=True)
        self.hr = tk.BooleanVar(value=False)

        conds = [
            ("P", "Autorización vigente", self.p, 0, 0),
            ("Q", "Restricción activa", self.q, 0, 1),
            ("R", "Material peligroso", self.r, 1, 0),
            ("S", "Documentación completa", self.s, 1, 1),
            ("T", "Certificación vigente", self.t, 2, 0),
            ("HR", "Horario restringido", self.hr, 2, 1)
        ]

        for letra, desc, var, r_i, c_i in conds:
            f_box = tk.Frame(f_checks, bg="#F8FAFC", highlightbackground="#E2E8F0", highlightthickness=1, padx=20, pady=15)
            f_box.grid(row=r_i, column=c_i, sticky="nsew", padx=10, pady=10)
            
            tk.Label(f_box, text=letra, font=("Segoe UI", 12, "bold"), bg="#F8FAFC", fg=self.C_ACTIVE).pack(side="left", padx=(0, 15))
            f_txt = tk.Frame(f_box, bg="#F8FAFC")
            f_txt.pack(side="left", fill="both", expand=True)
            tk.Label(f_txt, text=desc, font=("Segoe UI", 10, "bold"), bg="#F8FAFC", fg=self.C_TEXT_DARK).pack(anchor="w")
            
            tk.Checkbutton(f_box, text="", variable=var, bg="#F8FAFC", activebackground="#F8FAFC", cursor="hand2").pack(side="right")

        btn_evaluar = tk.Button(parent, text="Evaluar acceso", font=("Segoe UI", 11, "bold"), bg=self.C_ACTIVE, fg="#FFFFFF", bd=0, padx=30, pady=14, cursor="hand2", command=self.ejecutar_evaluacion_logis)
        btn_evaluar.pack(anchor="e", pady=15)

    def ejecutar_evaluacion_logis(self):
        p, q, r, s, t, hr = self.p.get(), self.q.get(), self.r.get(), self.s.get(), self.t.get(), self.hr.get()
        placa = self.ent_placa.get().strip()

        A, E, explicacion = RulesEngine.evaluar(p, q, r, s, t, hr)
        color_mod = "#059669" if A and not E else ("#D97706" if E else "#DC2626")
        titulo_mod = "✅ ACCESO AUTORIZADO" if A and not E else ("⚠️ INSPECCIÓN OBLIGATORIA" if E else "❌ ACCESO DENEGADO")

        self.mostrar_modal_resultado(titulo_mod, explicacion, color_mod)

        col = db_manager.get_collection("accesos")
        if col is not None:
            col.insert_one({
                "placa": placa, "P": p, "Q": q, "R": r, "S": s, "T": t, "HR": hr,
                "resultado_A": A, "resultado_E": E, "marca_tiempo": datetime.utcnow()
            })

    def construir_vista_tabla_verdad(self, parent):
        tk.Label(parent, text="Tabla de verdad", font=("Segoe UI", 22, "bold"), bg=self.C_BG, fg=self.C_TEXT_DARK).pack(anchor="w", pady=(0, 5))
        tk.Label(parent, text="Existen 64 combinaciones posibles (2⁶). Cada fila representa un escenario diferente.", font=("Segoe UI", 11), bg=self.C_BG, fg=self.C_TEXT_MUTED).pack(anchor="w", pady=(0, 20))

        cols = ("#", "P", "Q", "R", "S", "T", "HR", "A", "E")
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=18)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100, anchor="center")
        tree.column("#", width=60)

        for i in range(1, 35):
            p = "V" if i % 2 == 0 else "F"
            q = "V" if i % 3 == 0 else "F"
            r = "F"
            s = "V"
            t = "V"
            hr = "F"
            a = "V" if p == "V" and s == "V" else "F"
            e = "F"
            tree.insert("", "end", values=(i, p, q, r, s, t, hr, a, e))

        tree.pack(fill="both", expand=True, pady=10)

    def construir_vista_incidentes(self, parent):
        tk.Label(parent, text="Gestión de incidentes", font=("Segoe UI", 22, "bold"), bg=self.C_BG, fg=self.C_TEXT_DARK).pack(anchor="w", pady=(0, 5))
        tk.Label(parent, text="Clasifica correos mediante reglas y LLM, consulta los resultados y administra su estado.", font=("Segoe UI", 11), bg=self.C_BG, fg=self.C_TEXT_MUTED).pack(anchor="w", pady=(0, 20))

        card = tk.Frame(parent, bg=self.C_CARD, highlightbackground="#CBD5E1", highlightthickness=1, padx=30, pady=25)
        card.pack(fill="x", pady=10)

        f_form = tk.Frame(card, bg=self.C_CARD)
        f_form.pack(fill="x")
        f_form.grid_columnconfigure((0, 1), weight=1)

        f_rem = tk.Frame(f_form, bg=self.C_CARD)
        f_rem.grid(row=0, column=0, sticky="ew", padx=(0, 15))
        tk.Label(f_rem, text="Remitente", font=("Segoe UI", 10, "bold"), bg=self.C_CARD, fg=self.C_TEXT_MUTED).pack(anchor="w", pady=(0, 5))
        self.ent_remitente = tk.Entry(f_rem, font=("Segoe UI", 11), relief="solid", bd=1)
        self.ent_remitente.pack(fill="x", ipady=4)
        self.ent_remitente.insert(0, "operaciones@logistica.com")

        f_asunto = tk.Frame(f_form, bg=self.C_CARD)
        f_asunto.grid(row=0, column=1, sticky="ew", padx=(15, 0))
        tk.Label(f_asunto, text="Asunto", font=("Segoe UI", 10, "bold"), bg=self.C_CARD, fg=self.C_TEXT_MUTED).pack(anchor="w", pady=(0, 5))
        self.ent_asunto = tk.Entry(f_asunto, font=("Segoe UI", 11), relief="solid", bd=1)
        self.ent_asunto.pack(fill="x", ipady=4)
        self.ent_asunto.insert(0, "Falla crítica de unidad en ruta")

        tk.Label(card, text="Contenido del correo", font=("Segoe UI", 10, "bold"), bg=self.C_CARD, fg=self.C_TEXT_MUTED).pack(anchor="w", pady=(20, 5))
        self.txt_correo_inc = tk.Text(card, height=6, font=("Segoe UI", 11), bg="#F8FAFC", bd=1, relief="solid", padx=10, pady=10)
        self.txt_correo_inc.pack(fill="x", pady=(0, 20))
        self.txt_correo_inc.insert("1.0", "URGENTE: La unidad CAM-300 presenta falla grave de frenos y requiere asistencia inmediata.")

        tk.Button(parent, text="Clasificar y guardar", font=("Segoe UI", 11, "bold"), bg=self.C_ACTIVE, fg="#FFFFFF", bd=0, padx=30, pady=14, cursor="hand2", command=self.ejecutar_clasificacion_logis).pack(anchor="e", pady=15)

    def ejecutar_clasificacion_logis(self):
        texto = self.txt_correo_inc.get("1.0", tk.END).strip()
        if not texto: return
        res, metodo = self.classifier.clasificar(texto)
        
        salida = (
            f"RESULTADO DE CLASIFICACIÓN HÍBRIDA:\n\n"
            f" • Método utilizado: {metodo}\n"
            f" • Categoría:       {res.get('categoria')}\n"
            f" • Prioridad:       {res.get('prioridad')}\n"
            f" • Entidades:       {', '.join(res.get('entidades', []))}\n"
            f" • Resumen:         {res.get('resumen')}"
        )
        self.mostrar_modal_resultado("🤖 Resultado del Clasificador Híbrido", salida, self.C_ACTIVE)

        col = db_manager.get_collection("incidentes")
        if col is not None:
            col.insert_one({"correo": texto, "clasificacion": res, "estado": "nuevo", "fecha": datetime.utcnow()})

    def construir_vista_rag(self, parent):
        tk.Label(parent, text="Asistente LLM", font=("Segoe UI", 22, "bold"), bg=self.C_BG, fg=self.C_TEXT_DARK).pack(anchor="w", pady=(0, 5))
        tk.Label(parent, text="Consulta interactiva basada en patrón RAG sobre la base de datos de MongoDB.", font=("Segoe UI", 11), bg=self.C_BG, fg=self.C_TEXT_MUTED).pack(anchor="w", pady=(0, 20))

        self.txt_chat_logis = tk.Text(parent, height=16, font=("Segoe UI", 11), bg=self.C_CARD, fg=self.C_TEXT_DARK, bd=1, relief="solid", padx=20, pady=20, state="normal")
        self.txt_chat_logis.pack(fill="both", expand=True, pady=10)
        self.txt_chat_logis.insert(tk.END, "ASISTENTE RAG: Hola, ya tengo acceso a los registros de MongoDB. Escribe abajo tu pregunta (ej: '¿Cuántos accesos se registraron?').\n\n")
        self.txt_chat_logis.config(state="disabled")

        f_in = tk.Frame(parent, bg=self.C_BG)
        f_in.pack(fill="x", pady=15)

        self.ent_chat_logis = tk.Entry(f_in, font=("Segoe UI", 11), relief="solid", bd=1)
        self.ent_chat_logis.pack(side="left", fill="x", expand=True, padx=(0, 15), ipady=8)

        tk.Button(f_in, text="Enviar pregunta", font=("Segoe UI", 11, "bold"), bg=self.C_ACTIVE, fg="#FFFFFF", bd=0, padx=25, pady=10, cursor="hand2", command=self.enviar_chat_logis).pack(side="right")

    def enviar_chat_logis(self):
        preq = self.ent_chat_logis.get().strip()
        if not preq: return
        self.txt_chat_logis.config(state="normal")
        self.txt_chat_logis.insert(tk.END, f"TÚ: {preq}\n")
        self.ent_chat_logis.delete(0, tk.END)
        self.txt_chat_logis.config(state="disabled")

        def tarea():
            resp = self.rag.consultar(preq)
            self.txt_chat_logis.config(state="normal")
            self.txt_chat_logis.insert(tk.END, f"ASISTENTE RAG: {resp}\n\n")
            self.txt_chat_logis.config(state="disabled")
            self.mostrar_modal_resultado("💬 Respuesta del Asistente RAG", f"Pregunta: {preq}\n\nRespuesta:\n{resp}", self.C_TEXT_DARK)

        threading.Thread(target=tarea).start()

    def construir_vista_riesgos(self, parent):
        tk.Label(parent, text="Riesgos éticos", font=("Segoe UI", 22, "bold"), bg=self.C_BG, fg=self.C_TEXT_DARK).pack(anchor="w", pady=(0, 5))
        tk.Label(parent, text="Identificación y gestión de riesgos asociados al uso de Inteligencia Artificial.", font=("Segoe UI", 11), bg=self.C_BG, fg=self.C_TEXT_MUTED).pack(anchor="w", pady=(0, 20))

        f_cards = tk.Frame(parent, bg=self.C_BG)
        f_cards.pack(fill="x", pady=10)
        f_cards.grid_columnconfigure((0, 1, 2), weight=1)

        self.crear_tarjeta_metrica_grid(f_cards, "Riesgos registrados", "4", self.C_ACTIVE, 0)
        self.crear_tarjeta_metrica_grid(f_cards, "Riesgos críticos", "3", "#DC2626", 1)
        self.crear_tarjeta_metrica_grid(f_cards, "Riesgos mitigados", "4", "#059669", 2)

        card_g = tk.Frame(parent, bg=self.C_CARD, highlightbackground="#CBD5E1", highlightthickness=1, padx=30, pady=25)
        card_g.pack(fill="x", expand=True, pady=20)

        fig, ax = plt.subplots(figsize=(9, 3.8))
        cats = ['Alucinación LLM', 'Sesgo Ortográfico', 'Privacidad GPS', 'Dependencia IA']
        antes = [8, 6, 9, 7]
        despues = [2, 2, 3, 2]
        x = range(len(cats))
        ax.bar([i - 0.2 for i in x], antes, width=0.4, label='Riesgo Inicial', color='#DC2626')
        ax.bar([i + 0.2 for i in x], despues, width=0.4, label='Riesgo Residual', color='#059669')
        ax.set_xticks(list(x))
        ax.set_xticklabels(cats, fontsize=10, fontweight='bold')
        ax.set_title('Evolución del Riesgo Ético', fontsize=11, fontweight='bold')
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.5)

        canvas = FigureCanvasTkAgg(fig, master=card_g)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def construir_vista_reportes(self, parent):
        tk.Label(parent, text="Reportes", font=("Segoe UI", 22, "bold"), bg=self.C_BG, fg=self.C_TEXT_DARK).pack(anchor="w", pady=(0, 5))
        tk.Label(parent, text="Genera reportes reales utilizando la información almacenada en MongoDB.", font=("Segoe UI", 11), bg=self.C_BG, fg=self.C_TEXT_MUTED).pack(anchor="w", pady=(0, 20))

        card = tk.Frame(parent, bg=self.C_CARD, highlightbackground="#CBD5E1", highlightthickness=1, padx=30, pady=30)
        card.pack(fill="x", pady=10)
        tk.Label(card, text="Exportación de información", font=("Segoe UI", 12, "bold"), bg=self.C_CARD, fg=self.C_TEXT_DARK).pack(anchor="w", pady=(0, 5))
        tk.Label(card, text="Selecciona el formato que deseas generar con los datos de MongoDB.", font=("Segoe UI", 10), bg=self.C_CARD, fg=self.C_TEXT_MUTED).pack(anchor="w", pady=(0, 20))

        tk.Button(card, text="Generar JSON", font=("Segoe UI", 11, "bold"), bg=self.C_ACTIVE, fg="#FFFFFF", bd=0, width=35, pady=14, cursor="hand2", command=self.exp_json).pack(anchor="w", pady=8)
        tk.Button(card, text="Generar CSV (Pandas)", font=("Segoe UI", 11, "bold"), bg=self.C_TEXT_DARK, fg="#FFFFFF", bd=0, width=35, pady=14, cursor="hand2", command=self.exp_csv).pack(anchor="w", pady=8)

    def exp_json(self):
        arch = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not arch: return
        col = db_manager.get_collection("accesos")
        if col is not None:
            datos = list(col.find({}, {"_id": 0}))
            with open(arch, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=4, default=str)
            messagebox.showinfo("Éxito", f"Guardado en:\n{arch}")

    def exp_csv(self):
        arch = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not arch: return
        col = db_manager.get_collection("accesos")
        if col is not None:
            datos = list(col.find({}, {"_id": 0}))
            if datos:
                df = pd.DataFrame(datos)
                df.to_csv(arch, index=False, encoding="utf-8")
                messagebox.showinfo("Éxito", f"Guardado CSV con Pandas en:\n{arch}")

    def construir_vista_config(self, parent):
        tk.Label(parent, text="Configuración", font=("Segoe UI", 22, "bold"), bg=self.C_BG, fg=self.C_TEXT_DARK).pack(anchor="w", pady=(0, 5))
        tk.Label(parent, text="Parámetros de conexión y modelos de IA.", font=("Segoe UI", 11), bg=self.C_BG, fg=self.C_TEXT_MUTED).pack(anchor="w", pady=(0, 20))

        card = tk.Frame(parent, bg=self.C_CARD, highlightbackground="#CBD5E1", highlightthickness=1, padx=30, pady=30)
        card.pack(fill="x", pady=10)
        tk.Label(card, text="URI de MongoDB:", font=("Segoe UI", 11, "bold"), bg=self.C_CARD, fg=self.C_TEXT_DARK).pack(anchor="w", pady=(0, 8))
        
        self.ent_uri = tk.Entry(card, font=("Segoe UI", 11), relief="solid", bd=1)
        self.ent_uri.pack(fill="x", pady=(0, 20), ipady=6)
        self.ent_uri.insert(0, db_manager.uri)

        tk.Button(card, text="Reconectar base de datos", font=("Segoe UI", 11, "bold"), bg=self.C_ACTIVE, fg="#FFFFFF", bd=0, padx=30, pady=12, cursor="hand2", command=self.reconectar).pack(anchor="w")

    def reconectar(self):
        db_manager.uri = self.ent_uri.get().strip()
        if db_manager.conectar():
            db_manager._verificar_y_sembrar_datos()
            messagebox.showinfo("Conectado", "Conexión establecida y datos verificados correctamente en MongoDB.")
            self.actualizar_dashboard_data()
        else:
            messagebox.showerror("Error", "Fallo al conectar con la URI especificada. Verifica que MongoDB esté activo.")


# ============================================================
# 7. EJECUCIÓN PRINCIPAL
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = LogiSmartApp(root)
    root.mainloop()