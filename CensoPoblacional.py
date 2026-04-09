#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CENSO POBLACIONAL E INTEGRADOR
Aplicación de escritorio con Tkinter
Funciona completamente offline usando SQLite
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import json
import csv
from datetime import datetime, date
import math

# ============================================================
# BASE DE DATOS
# ============================================================
DB_NAME = "censo_poblacional.db"

def get_db_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)

def init_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS personas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombres TEXT NOT NULL,
        apellidos TEXT NOT NULL,
        cedula TEXT UNIQUE,
        fecha_nacimiento TEXT NOT NULL,
        edad INTEGER NOT NULL,
        sexo TEXT NOT NULL,
        estado_civil TEXT NOT NULL,
        direccion TEXT,
        telefono TEXT,
        nivel_educativo TEXT,
        ocupacion TEXT,
        etnia TEXT,
        discapacidad TEXT DEFAULT 'Ninguna',
        vivienda_tipo TEXT,
        num_habitantes_hogar INTEGER DEFAULT 1,
        ingresos_mensuales TEXT,
        seguro_medico TEXT DEFAULT 'No',
        fecha_registro TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def calcular_edad(fecha_nac_str):
    try:
        fn = datetime.strptime(fecha_nac_str, "%Y-%m-%d").date()
        hoy = date.today()
        edad = hoy.year - fn.year - ((hoy.month, hoy.day) < (fn.month, fn.day))
        return max(0, edad)
    except:
        return 0

# ============================================================
# COLORES Y ESTILOS
# ============================================================
COLORS = {
    "bg": "#1a1a2e",
    "bg2": "#16213e",
    "card": "#0f3460",
    "accent": "#e94560",
    "accent2": "#533483",
    "text": "#ffffff",
    "text2": "#a8b2d1",
    "success": "#00b894",
    "warning": "#fdcb6e",
    "input_bg": "#233554",
    "input_border": "#3a5a8c",
    "button_hover": "#ff6b6b",
    "header": "#0a1628",
    "sidebar": "#112240",
    "table_odd": "#1a2744",
    "table_even": "#162038",
    "table_header": "#0d1f3c",
}

# ============================================================
# APLICACIÓN PRINCIPAL
# ============================================================
class CensoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Censo Poblacional e Integrador")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)
        self.root.configure(bg=COLORS["bg"])
        
        init_db()
        self.setup_styles()
        self.create_layout()
        self.show_dashboard()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Header.TFrame", background=COLORS["header"])
        style.configure("Sidebar.TFrame", background=COLORS["sidebar"])
        style.configure("Content.TFrame", background=COLORS["bg"])
        style.configure("Card.TFrame", background=COLORS["card"])
        
        style.configure("Header.TLabel", background=COLORS["header"],
                        foreground=COLORS["text"], font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", background=COLORS["header"],
                        foreground=COLORS["text2"], font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=COLORS["bg"],
                        foreground=COLORS["text"], font=("Segoe UI", 16, "bold"))
        style.configure("Card.TLabel", background=COLORS["card"],
                        foreground=COLORS["text"], font=("Segoe UI", 11))
        style.configure("CardTitle.TLabel", background=COLORS["card"],
                        foreground=COLORS["text"], font=("Segoe UI", 13, "bold"))
        style.configure("CardValue.TLabel", background=COLORS["card"],
                        foreground=COLORS["accent"], font=("Segoe UI", 28, "bold"))
        style.configure("Stat.TLabel", background=COLORS["bg"],
                        foreground=COLORS["text2"], font=("Segoe UI", 10))

        style.configure("Nav.TButton", background=COLORS["sidebar"],
                        foreground=COLORS["text"], font=("Segoe UI", 11),
                        borderwidth=0, padding=(20, 12))
        style.map("Nav.TButton",
                  background=[("active", COLORS["card"]), ("!active", COLORS["sidebar"])],
                  foreground=[("active", COLORS["text"])])

        style.configure("Accent.TButton", background=COLORS["accent"],
                        foreground=COLORS["text"], font=("Segoe UI", 11, "bold"),
                        padding=(20, 10))
        style.map("Accent.TButton",
                  background=[("active", COLORS["button_hover"])])

        style.configure("Success.TButton", background=COLORS["success"],
                        foreground=COLORS["text"], font=("Segoe UI", 11, "bold"),
                        padding=(20, 10))

        style.configure("Custom.TEntry", fieldbackground=COLORS["input_bg"],
                        foreground=COLORS["text"], borderwidth=1,
                        padding=8)
        
        style.configure("Custom.TCombobox", fieldbackground=COLORS["input_bg"],
                        foreground=COLORS["text"], padding=8)

        style.configure("Treeview", background=COLORS["table_odd"],
                        foreground=COLORS["text"], fieldbackground=COLORS["table_odd"],
                        font=("Segoe UI", 10), rowheight=30)
        style.configure("Treeview.Heading", background=COLORS["table_header"],
                        foreground=COLORS["text"], font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", COLORS["accent"])])

    def create_layout(self):
        # Header
        header = ttk.Frame(self.root, style="Header.TFrame", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        hbox = ttk.Frame(header, style="Header.TFrame")
        hbox.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(hbox, text="📊 Censo Poblacional e Integrador",
                  style="Header.TLabel").pack(side="left")
        ttk.Label(hbox, text="Sistema Offline • Base de datos local SQLite",
                  style="Subtitle.TLabel").pack(side="right", pady=8)

        # Body
        body = ttk.Frame(self.root, style="Content.TFrame")
        body.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = ttk.Frame(body, style="Sidebar.TFrame", width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        nav_items = [
            ("🏠  Inicio", self.show_dashboard),
            ("➕  Registrar", self.show_register),
            ("📋  Listado", self.show_list),
            ("📊  Estadísticas", self.show_statistics),
            ("🔍  Buscar", self.show_search),
            ("💾  Exportar", self.export_data),
        ]
        
        ttk.Label(self.sidebar, text="MENÚ", style="Subtitle.TLabel",
                  background=COLORS["sidebar"]).pack(pady=(20, 10), padx=20, anchor="w")
        
        for text, cmd in nav_items:
            btn = ttk.Button(self.sidebar, text=text, style="Nav.TButton", command=cmd)
            btn.pack(fill="x", padx=5, pady=2)

        # Content area
        self.content = ttk.Frame(body, style="Content.TFrame")
        self.content.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ============================================================
    # DASHBOARD
    # ============================================================
    def show_dashboard(self):
        self.clear_content()
        ttk.Label(self.content, text="Panel Principal", style="Title.TLabel").pack(anchor="w", pady=(0, 15))

        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        total = c.execute("SELECT COUNT(*) FROM personas").fetchone()[0]
        avg_age = c.execute("SELECT AVG(edad) FROM personas").fetchone()[0] or 0
        male = c.execute("SELECT COUNT(*) FROM personas WHERE sexo='Masculino'").fetchone()[0]
        female = c.execute("SELECT COUNT(*) FROM personas WHERE sexo='Femenino'").fetchone()[0]
        today_count = c.execute("SELECT COUNT(*) FROM personas WHERE fecha_registro LIKE ?",
                                (datetime.now().strftime("%Y-%m-%d") + "%",)).fetchone()[0]
        conn.close()

        cards_frame = ttk.Frame(self.content, style="Content.TFrame")
        cards_frame.pack(fill="x", pady=(0, 20))

        cards_data = [
            ("Total Registrados", str(total), "👥"),
            ("Edad Promedio", f"{avg_age:.1f}", "📅"),
            ("Masculino", str(male), "👨"),
            ("Femenino", str(female), "👩"),
            ("Hoy", str(today_count), "📝"),
        ]

        for i, (title, value, icon) in enumerate(cards_data):
            card = tk.Frame(cards_frame, bg=COLORS["card"], relief="flat",
                           highlightthickness=1, highlightbackground=COLORS["input_border"])
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            cards_frame.columnconfigure(i, weight=1)
            
            tk.Label(card, text=icon, font=("Segoe UI", 24), bg=COLORS["card"],
                    fg=COLORS["text"]).pack(pady=(15, 5))
            tk.Label(card, text=value, font=("Segoe UI", 28, "bold"), bg=COLORS["card"],
                    fg=COLORS["accent"]).pack()
            tk.Label(card, text=title, font=("Segoe UI", 10), bg=COLORS["card"],
                    fg=COLORS["text2"]).pack(pady=(0, 15))

        # Recent registrations
        recent_frame = tk.Frame(self.content, bg=COLORS["card"], relief="flat",
                               highlightthickness=1, highlightbackground=COLORS["input_border"])
        recent_frame.pack(fill="both", expand=True)
        
        tk.Label(recent_frame, text="📋 Últimos Registros", font=("Segoe UI", 13, "bold"),
                bg=COLORS["card"], fg=COLORS["text"]).pack(anchor="w", padx=15, pady=(15, 10))

        cols = ("Nombre", "Edad", "Sexo", "Fecha Registro")
        tree = ttk.Treeview(recent_frame, columns=cols, show="headings", height=8)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        conn = sqlite3.connect(get_db_path())
        rows = conn.execute(
            "SELECT nombres || ' ' || apellidos, edad, sexo, fecha_registro FROM personas ORDER BY id DESC LIMIT 10"
        ).fetchall()
        conn.close()
        for r in rows:
            tree.insert("", "end", values=r)

    # ============================================================
    # REGISTRO
    # ============================================================
    def show_register(self):
        self.clear_content()
        ttk.Label(self.content, text="Registrar Persona", style="Title.TLabel").pack(anchor="w", pady=(0, 15))

        canvas = tk.Canvas(self.content, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLORS["bg"])
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        fields = {}
        
        def add_field(parent, label, row, col=0, widget_type="entry", options=None, colspan=1):
            frame = tk.Frame(parent, bg=COLORS["bg"])
            frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew", columnspan=colspan)
            
            tk.Label(frame, text=label, font=("Segoe UI", 10), bg=COLORS["bg"],
                    fg=COLORS["text2"]).pack(anchor="w")
            
            if widget_type == "entry":
                entry = tk.Entry(frame, font=("Segoe UI", 11), bg=COLORS["input_bg"],
                                fg=COLORS["text"], insertbackground=COLORS["text"],
                                relief="flat", highlightthickness=1,
                                highlightbackground=COLORS["input_border"])
                entry.pack(fill="x", ipady=6)
                fields[label] = entry
            elif widget_type == "combo":
                var = tk.StringVar()
                combo = ttk.Combobox(frame, textvariable=var, values=options,
                                    state="readonly", style="Custom.TCombobox",
                                    font=("Segoe UI", 11))
                combo.pack(fill="x", ipady=4)
                fields[label] = combo
            elif widget_type == "date":
                df = tk.Frame(frame, bg=COLORS["bg"])
                df.pack(fill="x")
                
                y_var = tk.StringVar()
                m_var = tk.StringVar()
                d_var = tk.StringVar()
                
                years = [str(y) for y in range(date.today().year, 1900, -1)]
                months = [str(m).zfill(2) for m in range(1, 13)]
                days = [str(d).zfill(2) for d in range(1, 32)]
                
                y_cb = ttk.Combobox(df, textvariable=y_var, values=years, width=8,
                                   state="readonly", font=("Segoe UI", 11))
                y_cb.pack(side="left", padx=(0, 5))
                tk.Label(df, text="/", bg=COLORS["bg"], fg=COLORS["text2"]).pack(side="left")
                m_cb = ttk.Combobox(df, textvariable=m_var, values=months, width=5,
                                   state="readonly", font=("Segoe UI", 11))
                m_cb.pack(side="left", padx=5)
                tk.Label(df, text="/", bg=COLORS["bg"], fg=COLORS["text2"]).pack(side="left")
                d_cb = ttk.Combobox(df, textvariable=d_var, values=days, width=5,
                                   state="readonly", font=("Segoe UI", 11))
                d_cb.pack(side="left", padx=(5, 0))
                
                fields[label] = (y_var, m_var, d_var)
            return frame

        form = tk.Frame(scroll_frame, bg=COLORS["bg"])
        form.pack(fill="x", padx=10)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        # Section: Datos Personales
        sec1 = tk.Label(form, text="── Datos Personales ──", font=("Segoe UI", 12, "bold"),
                       bg=COLORS["bg"], fg=COLORS["accent"])
        sec1.grid(row=0, column=0, columnspan=2, pady=(10, 5), sticky="w", padx=10)

        add_field(form, "Nombres *", 1, 0)
        add_field(form, "Apellidos *", 1, 1)
        add_field(form, "Cédula / ID", 2, 0)
        add_field(form, "Fecha de Nacimiento *", 2, 1, "date")
        add_field(form, "Sexo *", 3, 0, "combo", ["Masculino", "Femenino", "Otro"])
        add_field(form, "Estado Civil *", 3, 1, "combo",
                 ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a", "Unión Libre"])
        add_field(form, "Etnia", 4, 0, "combo",
                 ["Mestizo", "Blanco", "Afrodescendiente", "Indígena", "Otro"])
        add_field(form, "Discapacidad", 4, 1, "combo",
                 ["Ninguna", "Física", "Visual", "Auditiva", "Intelectual", "Otra"])

        # Section: Contacto
        sec2 = tk.Label(form, text="── Contacto y Ubicación ──", font=("Segoe UI", 12, "bold"),
                       bg=COLORS["bg"], fg=COLORS["accent"])
        sec2.grid(row=5, column=0, columnspan=2, pady=(20, 5), sticky="w", padx=10)

        add_field(form, "Dirección", 6, 0, colspan=2)
        add_field(form, "Teléfono", 7, 0)

        # Section: Socioeconómico
        sec3 = tk.Label(form, text="── Datos Socioeconómicos ──", font=("Segoe UI", 12, "bold"),
                       bg=COLORS["bg"], fg=COLORS["accent"])
        sec3.grid(row=8, column=0, columnspan=2, pady=(20, 5), sticky="w", padx=10)

        add_field(form, "Nivel Educativo", 9, 0, "combo",
                 ["Sin estudios", "Primaria", "Secundaria", "Técnico", "Universitario", "Postgrado"])
        add_field(form, "Ocupación", 9, 1)
        add_field(form, "Tipo de Vivienda", 10, 0, "combo",
                 ["Propia", "Alquilada", "Prestada", "Invasión", "Otra"])
        add_field(form, "Habitantes en Hogar", 10, 1, "combo",
                 [str(i) for i in range(1, 21)])
        add_field(form, "Ingresos Mensuales", 11, 0, "combo",
                 ["Sin ingresos", "Menos de 1 salario mínimo", "1-2 salarios mínimos",
                  "2-4 salarios mínimos", "Más de 4 salarios mínimos"])
        add_field(form, "Seguro Médico", 11, 1, "combo", ["Sí", "No"])

        # Buttons
        btn_frame = tk.Frame(scroll_frame, bg=COLORS["bg"])
        btn_frame.pack(fill="x", padx=20, pady=20)

        def save():
            nombres = fields["Nombres *"].get().strip()
            apellidos = fields["Apellidos *"].get().strip()
            cedula = fields["Cédula / ID"].get().strip()
            sexo = fields["Sexo *"].get()
            estado_civil = fields["Estado Civil *"].get()
            
            y, m, d = fields["Fecha de Nacimiento *"]
            fecha_nac = f"{y.get()}-{m.get()}-{d.get()}" if y.get() and m.get() and d.get() else ""

            if not nombres or not apellidos or not fecha_nac or not sexo or not estado_civil:
                messagebox.showwarning("Campos requeridos", "Por favor complete todos los campos marcados con *")
                return

            edad = calcular_edad(fecha_nac)

            try:
                conn = sqlite3.connect(get_db_path())
                conn.execute('''INSERT INTO personas 
                    (nombres, apellidos, cedula, fecha_nacimiento, edad, sexo, estado_civil,
                     direccion, telefono, nivel_educativo, ocupacion, etnia, discapacidad,
                     vivienda_tipo, num_habitantes_hogar, ingresos_mensuales, seguro_medico, fecha_registro)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (nombres, apellidos, cedula or None, fecha_nac, edad, sexo, estado_civil,
                     fields.get("Dirección", tk.Entry()).get() if isinstance(fields.get("Dirección"), tk.Entry) else "",
                     fields.get("Teléfono", tk.Entry()).get() if isinstance(fields.get("Teléfono"), tk.Entry) else "",
                     fields.get("Nivel Educativo", ttk.Combobox()).get() if isinstance(fields.get("Nivel Educativo"), ttk.Combobox) else "",
                     fields.get("Ocupación", tk.Entry()).get() if isinstance(fields.get("Ocupación"), tk.Entry) else "",
                     fields.get("Etnia", ttk.Combobox()).get() if isinstance(fields.get("Etnia"), ttk.Combobox) else "",
                     fields.get("Discapacidad", ttk.Combobox()).get() or "Ninguna",
                     fields.get("Tipo de Vivienda", ttk.Combobox()).get() if isinstance(fields.get("Tipo de Vivienda"), ttk.Combobox) else "",
                     int(fields.get("Habitantes en Hogar", ttk.Combobox()).get() or 1),
                     fields.get("Ingresos Mensuales", ttk.Combobox()).get() if isinstance(fields.get("Ingresos Mensuales"), ttk.Combobox) else "",
                     fields.get("Seguro Médico", ttk.Combobox()).get() or "No",
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", f"✅ {nombres} {apellidos} registrado/a correctamente.\nEdad calculada: {edad} años")
                self.show_register()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "La cédula/ID ya existe en la base de datos.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        save_btn = tk.Button(btn_frame, text="💾  Guardar Registro", font=("Segoe UI", 12, "bold"),
                            bg=COLORS["success"], fg=COLORS["text"], relief="flat",
                            cursor="hand2", padx=30, pady=10, command=save)
        save_btn.pack(side="left", padx=(0, 10))

        clear_btn = tk.Button(btn_frame, text="🗑  Limpiar", font=("Segoe UI", 12),
                             bg=COLORS["accent2"], fg=COLORS["text"], relief="flat",
                             cursor="hand2", padx=30, pady=10, command=self.show_register)
        clear_btn.pack(side="left")

    # ============================================================
    # LISTADO
    # ============================================================
    def show_list(self):
        self.clear_content()
        ttk.Label(self.content, text="Listado de Personas", style="Title.TLabel").pack(anchor="w", pady=(0, 15))

        # Toolbar
        toolbar = tk.Frame(self.content, bg=COLORS["bg"])
        toolbar.pack(fill="x", pady=(0, 10))

        tk.Button(toolbar, text="🗑 Eliminar Seleccionado", font=("Segoe UI", 10),
                 bg=COLORS["accent"], fg=COLORS["text"], relief="flat", cursor="hand2",
                 padx=15, pady=5, command=lambda: self.delete_selected(tree)).pack(side="right")

        # Table
        cols = ("ID", "Nombres", "Apellidos", "Edad", "Sexo", "Cédula", "Estado Civil", "Fecha Reg.")
        tree = ttk.Treeview(self.content, columns=cols, show="headings", height=20)
        
        widths = {"ID": 40, "Nombres": 130, "Apellidos": 130, "Edad": 50, "Sexo": 80,
                  "Cédula": 100, "Estado Civil": 100, "Fecha Reg.": 120}
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=widths.get(col, 100), minwidth=40)

        vsb = ttk.Scrollbar(self.content, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        conn = sqlite3.connect(get_db_path())
        rows = conn.execute(
            "SELECT id, nombres, apellidos, edad, sexo, cedula, estado_civil, fecha_registro FROM personas ORDER BY id DESC"
        ).fetchall()
        conn.close()
        
        for i, r in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            tree.insert("", "end", values=r, tags=(tag,))
        tree.tag_configure("even", background=COLORS["table_even"])
        tree.tag_configure("odd", background=COLORS["table_odd"])

    def delete_selected(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Seleccione un registro para eliminar.")
            return
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este registro?"):
            item = tree.item(sel[0])
            pid = item["values"][0]
            conn = sqlite3.connect(get_db_path())
            conn.execute("DELETE FROM personas WHERE id=?", (pid,))
            conn.commit()
            conn.close()
            self.show_list()

    # ============================================================
    # ESTADÍSTICAS
    # ============================================================
    def show_statistics(self):
        self.clear_content()
        ttk.Label(self.content, text="Estadísticas del Censo", style="Title.TLabel").pack(anchor="w", pady=(0, 15))

        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        total = c.execute("SELECT COUNT(*) FROM personas").fetchone()[0]
        
        if total == 0:
            tk.Label(self.content, text="No hay datos registrados aún.\nRegistre personas para ver estadísticas.",
                    font=("Segoe UI", 14), bg=COLORS["bg"], fg=COLORS["text2"]).pack(pady=50)
            conn.close()
            return

        canvas = tk.Canvas(self.content, bg=COLORS["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLORS["bg"])
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Age distribution
        age_groups = c.execute("""
            SELECT 
                CASE 
                    WHEN edad BETWEEN 0 AND 5 THEN '0-5'
                    WHEN edad BETWEEN 6 AND 12 THEN '6-12'
                    WHEN edad BETWEEN 13 AND 17 THEN '13-17'
                    WHEN edad BETWEEN 18 AND 25 THEN '18-25'
                    WHEN edad BETWEEN 26 AND 35 THEN '26-35'
                    WHEN edad BETWEEN 36 AND 45 THEN '36-45'
                    WHEN edad BETWEEN 46 AND 60 THEN '46-60'
                    ELSE '60+'
                END as grupo,
                COUNT(*) as cantidad
            FROM personas GROUP BY grupo ORDER BY MIN(edad)
        """).fetchall()

        sex_data = c.execute("SELECT sexo, COUNT(*) FROM personas GROUP BY sexo").fetchall()
        edu_data = c.execute("SELECT nivel_educativo, COUNT(*) FROM personas WHERE nivel_educativo != '' GROUP BY nivel_educativo").fetchall()
        civil_data = c.execute("SELECT estado_civil, COUNT(*) FROM personas GROUP BY estado_civil").fetchall()
        avg_age = c.execute("SELECT AVG(edad) FROM personas").fetchone()[0]
        min_age = c.execute("SELECT MIN(edad) FROM personas").fetchone()[0]
        max_age = c.execute("SELECT MAX(edad) FROM personas").fetchone()[0]
        median_q = c.execute("SELECT edad FROM personas ORDER BY edad LIMIT 1 OFFSET ?", (total//2,)).fetchone()
        median_age = median_q[0] if median_q else 0
        conn.close()

        # Summary stats
        summary = tk.Frame(scroll_frame, bg=COLORS["card"], relief="flat",
                          highlightthickness=1, highlightbackground=COLORS["input_border"])
        summary.pack(fill="x", padx=5, pady=(0, 15))
        
        tk.Label(summary, text="📈 Resumen General", font=("Segoe UI", 13, "bold"),
                bg=COLORS["card"], fg=COLORS["text"]).pack(anchor="w", padx=15, pady=(15, 10))

        stats_frame = tk.Frame(summary, bg=COLORS["card"])
        stats_frame.pack(fill="x", padx=15, pady=(0, 15))

        stats = [
            ("Total Registros", total), ("Edad Promedio", f"{avg_age:.1f}"),
            ("Edad Mínima", min_age), ("Edad Máxima", max_age),
            ("Edad Mediana", median_age)
        ]
        for i, (label, val) in enumerate(stats):
            f = tk.Frame(stats_frame, bg=COLORS["bg2"], relief="flat")
            f.grid(row=0, column=i, padx=5, sticky="nsew")
            stats_frame.columnconfigure(i, weight=1)
            tk.Label(f, text=str(val), font=("Segoe UI", 20, "bold"), bg=COLORS["bg2"],
                    fg=COLORS["warning"]).pack(pady=(10, 2))
            tk.Label(f, text=label, font=("Segoe UI", 9), bg=COLORS["bg2"],
                    fg=COLORS["text2"]).pack(pady=(0, 10))

        # Bar chart: Age groups
        self.draw_bar_chart(scroll_frame, "📊 Distribución por Edades", age_groups,
                           COLORS["accent"])

        # Charts row
        charts_row = tk.Frame(scroll_frame, bg=COLORS["bg"])
        charts_row.pack(fill="x", padx=5, pady=(0, 15))
        charts_row.columnconfigure(0, weight=1)
        charts_row.columnconfigure(1, weight=1)

        self.draw_bar_chart_in(charts_row, "👫 Por Sexo", sex_data, COLORS["success"], 0, 0)
        self.draw_bar_chart_in(charts_row, "🎓 Nivel Educativo", edu_data, COLORS["accent2"], 0, 1)

        # Civil status
        self.draw_bar_chart(scroll_frame, "💍 Estado Civil", civil_data, COLORS["warning"])

    def draw_bar_chart(self, parent, title, data, color):
        frame = tk.Frame(parent, bg=COLORS["card"], relief="flat",
                        highlightthickness=1, highlightbackground=COLORS["input_border"])
        frame.pack(fill="x", padx=5, pady=(0, 15))
        
        tk.Label(frame, text=title, font=("Segoe UI", 13, "bold"),
                bg=COLORS["card"], fg=COLORS["text"]).pack(anchor="w", padx=15, pady=(15, 10))

        if not data:
            tk.Label(frame, text="Sin datos", bg=COLORS["card"], fg=COLORS["text2"]).pack(pady=10)
            return

        max_val = max(d[1] for d in data) if data else 1
        chart = tk.Frame(frame, bg=COLORS["card"])
        chart.pack(fill="x", padx=15, pady=(0, 15))

        for i, (label, count) in enumerate(data):
            row = tk.Frame(chart, bg=COLORS["card"])
            row.pack(fill="x", pady=3)
            
            tk.Label(row, text=label, font=("Segoe UI", 10), bg=COLORS["card"],
                    fg=COLORS["text"], width=18, anchor="e").pack(side="left")
            
            bar_frame = tk.Frame(row, bg=COLORS["bg2"], height=22)
            bar_frame.pack(side="left", fill="x", expand=True, padx=(10, 10))
            bar_frame.pack_propagate(False)
            
            pct = count / max_val if max_val else 0
            bar = tk.Frame(bar_frame, bg=color, width=max(int(pct * 400), 2))
            bar.place(x=0, y=0, relheight=1)
            
            tk.Label(row, text=str(count), font=("Segoe UI", 10, "bold"),
                    bg=COLORS["card"], fg=color, width=5).pack(side="left")

    def draw_bar_chart_in(self, parent, title, data, color, row, col):
        frame = tk.Frame(parent, bg=COLORS["card"], relief="flat",
                        highlightthickness=1, highlightbackground=COLORS["input_border"])
        frame.grid(row=row, column=col, padx=5, sticky="nsew")
        
        tk.Label(frame, text=title, font=("Segoe UI", 13, "bold"),
                bg=COLORS["card"], fg=COLORS["text"]).pack(anchor="w", padx=15, pady=(15, 10))

        if not data:
            tk.Label(frame, text="Sin datos", bg=COLORS["card"], fg=COLORS["text2"]).pack(pady=10)
            return

        max_val = max(d[1] for d in data) if data else 1
        chart = tk.Frame(frame, bg=COLORS["card"])
        chart.pack(fill="x", padx=15, pady=(0, 15))

        for label, count in data:
            row_f = tk.Frame(chart, bg=COLORS["card"])
            row_f.pack(fill="x", pady=3)
            tk.Label(row_f, text=label[:15], font=("Segoe UI", 9), bg=COLORS["card"],
                    fg=COLORS["text"], width=14, anchor="e").pack(side="left")
            bar_frame = tk.Frame(row_f, bg=COLORS["bg2"], height=20)
            bar_frame.pack(side="left", fill="x", expand=True, padx=(8, 8))
            bar_frame.pack_propagate(False)
            pct = count / max_val if max_val else 0
            bar = tk.Frame(bar_frame, bg=color, width=max(int(pct * 200), 2))
            bar.place(x=0, y=0, relheight=1)
            tk.Label(row_f, text=str(count), font=("Segoe UI", 9, "bold"),
                    bg=COLORS["card"], fg=color, width=4).pack(side="left")

    # ============================================================
    # BÚSQUEDA
    # ============================================================
    def show_search(self):
        self.clear_content()
        ttk.Label(self.content, text="Buscar Personas", style="Title.TLabel").pack(anchor="w", pady=(0, 15))

        search_frame = tk.Frame(self.content, bg=COLORS["bg"])
        search_frame.pack(fill="x", pady=(0, 15))

        tk.Label(search_frame, text="Buscar:", font=("Segoe UI", 11), bg=COLORS["bg"],
                fg=COLORS["text"]).pack(side="left", padx=(0, 10))
        
        search_entry = tk.Entry(search_frame, font=("Segoe UI", 12), bg=COLORS["input_bg"],
                               fg=COLORS["text"], insertbackground=COLORS["text"],
                               relief="flat", highlightthickness=1,
                               highlightbackground=COLORS["input_border"])
        search_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))

        cols = ("ID", "Nombres", "Apellidos", "Edad", "Sexo", "Cédula", "Dirección")
        tree = ttk.Treeview(self.content, columns=cols, show="headings", height=18)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.column("ID", width=40)
        
        vsb = ttk.Scrollbar(self.content, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        def do_search(*args):
            q = search_entry.get().strip()
            for item in tree.get_children():
                tree.delete(item)
            conn = sqlite3.connect(get_db_path())
            rows = conn.execute(
                """SELECT id, nombres, apellidos, edad, sexo, cedula, direccion FROM personas
                   WHERE nombres LIKE ? OR apellidos LIKE ? OR cedula LIKE ? OR direccion LIKE ?
                   ORDER BY id DESC""",
                (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%")
            ).fetchall()
            conn.close()
            for i, r in enumerate(rows):
                tag = "even" if i % 2 == 0 else "odd"
                tree.insert("", "end", values=r, tags=(tag,))
            tree.tag_configure("even", background=COLORS["table_even"])
            tree.tag_configure("odd", background=COLORS["table_odd"])

        search_entry.bind("<KeyRelease>", do_search)

        tk.Button(search_frame, text="🔍 Buscar", font=("Segoe UI", 11), bg=COLORS["accent"],
                 fg=COLORS["text"], relief="flat", cursor="hand2", padx=20, pady=5,
                 command=do_search).pack(side="left")

        do_search()

    # ============================================================
    # EXPORTAR
    # ============================================================
    def export_data(self):
        conn = sqlite3.connect(get_db_path())
        rows = conn.execute("SELECT * FROM personas").fetchall()
        cols = [desc[0] for desc in conn.execute("SELECT * FROM personas LIMIT 0").description]
        conn.close()

        if not rows:
            messagebox.showinfo("Exportar", "No hay datos para exportar.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("JSON", "*.json")],
            title="Exportar datos del censo"
        )
        if not filepath:
            return

        try:
            if filepath.endswith(".json"):
                data = [dict(zip(cols, row)) for row in rows]
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                with open(filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(cols)
                    writer.writerows(rows)
            messagebox.showinfo("Éxito", f"✅ Datos exportados correctamente.\n{len(rows)} registros guardados.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")


# ============================================================
# EJECUTAR
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = CensoApp(root)
    root.mainloop()
