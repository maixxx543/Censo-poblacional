
# ════════════════════════════════════════════════════════════════════════════════
# ██████████████████████████████████████████████████████████████████████████████
# ║                                                                            ║
# ║       SISTEMA DE CENSO POBLACIONAL COMUNITARIO                             ║
# ║       Estado Táchira - Municipio Junín                                     ║
# ║       República Bolivariana de Venezuela                                   ║
# ║                                                                            ║
# ║  VERSIÓN OPTIMIZADA Y DOCUMENTADA                                          ║
# ║  Se eliminaron imports no usados, código duplicado y funciones             ║
# ║  redundantes. Cada sección está comentada de forma clara.                  ║
# ║                                                                            ║
# ██████████████████████████████████████████████████████████████████████████████
# ════════════════════════════════════════════════════════════════════════════════

"""
╔══════════════════════════════════════════════════════════════╗
║       SISTEMA DE CENSO POBLACIONAL COMUNITARIO               ║
║       Estado Táchira - Municipio Junín                       ║
║       República Bolivariana de Venezuela                     ║
╚══════════════════════════════════════════════════════════════╝

=== ¿QUÉ HACE ESTE PROGRAMA? ===
Es una aplicación de escritorio (ventana) que permite gestionar un censo
poblacional del Municipio Junín, Estado Táchira, Venezuela.

=== FUNCIONALIDADES PRINCIPALES ===
    1. INICIO DE SESIÓN: Acceso con usuario y contraseña (guardados en base de datos SQLite).
    2. REGISTRO DE HABITANTES: Formulario para ingresar datos personales (nombre, cédula, etc.).
    3. CONSULTA Y BÚSQUEDA: Tabla interactiva para ver, buscar, filtrar y editar registros.
    4. ESTADÍSTICAS: Gráficos de barras que muestran distribución por género y edad.
    5. IMPRESIÓN: Genera reportes en formato HTML que se abren en el navegador.
    6. FAMILIAS: Crear grupos familiares, asignar jefes de familia y vincular miembros.
    7. DATOS EXTENDIDOS: Nacionalidad, nivel educativo, tipo y tenencia de vivienda.

=== TECNOLOGÍAS USADAS ===
    - tkinter: Librería estándar de Python para crear interfaces gráficas (ventanas, botones, etc.).
    - sqlite3: Base de datos ligera que guarda la información en un archivo local (.db).
    - webbrowser: Abre archivos HTML en el navegador para imprimir reportes.
    - re: Expresiones regulares para validar formatos (como correos electrónicos).
    - tempfile: Para crear archivos temporales (planillas HTML).
    - datetime: Para calcular edades y manejar fechas.

=== OPTIMIZACIONES APLICADAS EN ESTA VERSIÓN ===
    1. Eliminado "import csv" (no se usaba en ninguna parte).
    2. Eliminado "filedialog" del import (no se usaba en ninguna parte).
    3. Eliminado método "_exportar_csv" (nombre engañoso, era un wrapper innecesario).
    4. Extraído "_centrar_ventana" como función global (estaba duplicado en 2 clases).
    5. Extraído el código de scroll con mousewheel como función reutilizable.
    6. Unificada la constante RANGOS_EDAD con la función clasificar_edad().
    7. Eliminada variable "count" innecesaria en _cargar_habitantes.
    8. Eliminada recarga innecesaria de familias al buscar/filtrar habitantes.
    9. Eliminada doble asignación de habitante_id_seleccionado en _editar_desde_tabla.
    10. Corregido doble cálculo de edad en _imprimir_por_edad.
    11. Comentarios excesivos reducidos a lo esencial sin perder claridad.
"""

# ════════════════════════════════════════════════════════════
# SECCIÓN 1: IMPORTACIONES
# ────────────────────────────────────────────────────────────
# Aquí se cargan todas las librerías que el programa necesita.
# Cada "import" trae herramientas específicas que usamos más adelante.
#
# OPTIMIZACIÓN: Se eliminaron "csv" y "filedialog" porque no se
# usaban en ninguna parte del código.
# ════════════════════════════════════════════════════════════

import tkinter as tk                          # [INTERFAZ] Librería principal para crear ventanas y widgets
from tkinter import ttk, messagebox           # [INTERFAZ] ttk=widgets modernos, messagebox=alertas
#                                               ↑ OPTIMIZACIÓN: Se quitó "filedialog" (nunca se usaba)
import sqlite3                                 # [BASE DE DATOS] Para conectar y operar con la base de datos SQLite
import re                                      # [VALIDACIÓN] Expresiones regulares para validar formatos como email
from datetime import datetime, date            # [FECHAS] Para trabajar con fechas y calcular edades
import os                                      # [SISTEMA] Para operaciones del sistema operativo (rutas de archivos)
# import csv  ← ELIMINADO: nunca se usaba en el código (el método _exportar_csv generaba HTML, no CSV)
import webbrowser                              # [NAVEGADOR] Para abrir archivos HTML en el navegador web
import tempfile                                # [ARCHIVOS TEMPORALES] Para crear archivos temporales de planillas

# ════════════════════════════════════════════════════════════
# SECCIÓN 2: CONSTANTES Y CONFIGURACIÓN
# ────────────────────────────────────────────────────────────
# Las constantes son valores que NO cambian durante la ejecución.
# Se definen aquí para poder modificarlas fácilmente en un solo lugar.
# ════════════════════════════════════════════════════════════

# [NOMBRE DEL ARCHIVO] de la base de datos SQLite (se crea automáticamente)
DB_NAME = "censo_poblacional.db"

# [PALETA DE COLORES] Diccionario con todos los colores usados en la interfaz.
# Cada color tiene un nombre descriptivo y su código hexadecimal (#RRGGBB).
# Los colores principales están inspirados en la bandera de Venezuela.
COLORES = {
    "rojo_vzla":      "#CF142B",    # Rojo de la bandera venezolana (botones principales)
    "rojo_oscuro":    "#A01025",    # Rojo más oscuro (efecto hover/presionar botones)
    "amarillo_vzla":  "#FCDD09",    # Amarillo de la bandera (textos destacados, títulos)
    "azul_vzla":      "#00209F",    # Azul de la bandera (bordes, acentos)
    "azul_oscuro":    "#001A7A",    # Azul más oscuro (variante del azul)
    "blanco":         "#FFFFFF",    # Blanco puro (fondos claros, textos sobre oscuro)
    "gris_claro":     "#F0F0F0",    # Gris claro (fondos secundarios)
    "gris_medio":     "#D0D0D0",    # Gris medio (textos descriptivos)
    "gris_oscuro":    "#333333",    # Gris oscuro (texto principal en fondo claro)
    "fondo_app":      "#1A1A2E",    # Azul muy oscuro (fondo general de la aplicación)
    "fondo_panel":    "#16213E",    # Azul oscuro (fondo de paneles y secciones)
    "fondo_card":     "#0F3460",    # Azul medio (fondo de tarjetas y campos de texto)
    "texto_claro":    "#E8E8E8",    # Gris muy claro (textos sobre fondo oscuro)
    "acento":         "#E94560",    # Rojo rosado (botones de eliminar, alertas)
    "acento_hover":   "#FF6B81",    # Rosado claro (hover del acento)
    "verde":          "#2ECC71",    # Verde (botones de guardar/éxito)
    "naranja":        "#F39C12",    # Naranja (botones de editar/precaución)
}

# [PARROQUIAS] Lista de parroquias del Municipio Junín, Estado Táchira.
# Se usan en los menús desplegables (Combobox) del formulario.
PARROQUIAS_JUNIN = [
    "Rubio", "Bramón", "La Petrólea", "Delicias",
    "Quinimarí", "San Juan de Colón"
]

# [OPCIONES DE FORMULARIO] Listas de opciones para los campos desplegables
ESTADOS_CIVILES = ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a", "Unión Libre"]
GENEROS = ["Masculino", "Femenino"]

# [TIPOS DE VIVIENDA] Opciones para clasificar el tipo de vivienda del habitante
TIPOS_VIVIENDA = [
    "Casa", "Apartamento", "Quinta", "Townhouse",
    "Rancho", "Habitación", "Casa de vecindad", "Otra"
]

# [TENENCIA DE VIVIENDA] Si la vivienda es propia, alquilada o cedida
TENENCIA_VIVIENDA = ["Propia", "Alquilada", "Cedida"]

# [NIVELES DE EDUCACIÓN] Desde sin instrucción hasta doctorado
NIVELES_EDUCACION = [
    "Sin instrucción", "Preescolar", "Primaria incompleta", "Primaria completa",
    "Secundaria incompleta", "Secundaria completa", "Técnico medio",
    "Técnico superior (TSU)", "Universitario incompleto", "Universitario completo",
    "Postgrado (Especialización)", "Postgrado (Maestría)", "Postgrado (Doctorado)"
]

# [NACIONALIDADES] Solo dos opciones: venezolano o extranjero
NACIONALIDADES = ["Venezolano/a", "Extranjero/a"]

# [PAÍSES] Lista de países para seleccionar el origen de un extranjero
PAISES = [
    "Colombia", "Brasil", "Ecuador", "Perú", "Chile", "Argentina",
    "Bolivia", "Uruguay", "Paraguay", "Panamá", "Costa Rica",
    "México", "Guatemala", "Honduras", "El Salvador", "Nicaragua",
    "Cuba", "República Dominicana", "Haití", "Trinidad y Tobago",
    "Guyana", "Surinam", "Estados Unidos", "España", "Portugal",
    "Italia", "China", "Otro"
]

# [RANGOS DE EDAD] Diccionario que define los grupos etarios.
# Cada grupo tiene un nombre, una etiqueta corta y un rango (mínimo, máximo).
# OPTIMIZACIÓN: Ahora es la ÚNICA fuente de verdad para los rangos.
# La función clasificar_edad() usa este diccionario en vez de tener
# los rangos duplicados con if/elif.
RANGOS_EDAD = {
    "Niños (0-11)": (0, 11),           # De 0 a 11 años = Niño
    "Jóvenes (12-17)": (12, 17),       # De 12 a 17 años = Joven
    "Adultos (18-59)": (18, 59),       # De 18 a 59 años = Adulto
    "Adultos Mayores (60+)": (60, 200), # De 60 años en adelante = Adulto Mayor
}

# [ETIQUETAS CORTAS] Mapeo de los rangos a nombres cortos para uso en estadísticas/fichas.
# Se usa junto con RANGOS_EDAD para evitar duplicar los rangos numéricos.
ETIQUETAS_GRUPO_ETARIO = {
    "Niños (0-11)": "Niño",
    "Jóvenes (12-17)": "Joven",
    "Adultos (18-59)": "Adulto",
    "Adultos Mayores (60+)": "Adulto Mayor",
}

# [FUENTES TIPOGRÁFICAS] Configuración de las fuentes (tipo de letra) usadas.
# Formato: ("Nombre de fuente", tamaño, "estilo")
FUENTE_TITULO = ("Segoe UI", 18, "bold")      # Para títulos principales (grande y negrita)
FUENTE_SUBTITULO = ("Segoe UI", 14, "bold")    # Para subtítulos (mediano y negrita)
FUENTE_NORMAL = ("Segoe UI", 11)               # Para texto normal
FUENTE_SMALL = ("Segoe UI", 10)                # Para texto pequeño
FUENTE_BOTON = ("Segoe UI", 11, "bold")        # Para texto de botones (negrita)
FUENTE_SECCION = ("Segoe UI", 12, "bold")      # Para títulos de secciones


# ════════════════════════════════════════════════════════════
# SECCIÓN 3: BASE DE DATOS
# ────────────────────────────────────────────────────────────
# Funciones para crear y conectar a la base de datos SQLite.
# SQLite guarda toda la información en un archivo local (.db).
# ════════════════════════════════════════════════════════════

def inicializar_db():
    """
    [FUNCIÓN: INICIALIZAR BASE DE DATOS]
    
    ¿Qué hace?
    → Crea el archivo de base de datos y las tablas necesarias si no existen.
    → Si la base de datos ya existe, agrega columnas nuevas (migración).
    → Crea el usuario administrador por defecto (admin/admin123).
    
    ¿Cuándo se ejecuta?
    → Una sola vez al iniciar el programa (en la línea final del código).
    
    Tablas que crea:
    1. "usuarios" → Guarda usuarios y contraseñas para el login.
    2. "habitantes" → Guarda todos los datos de cada habitante censado.
    3. "familias" → Guarda los grupos familiares.
    """
    # Paso 1: Conectar a la base de datos (si no existe, la crea automáticamente)
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()  # El "cursor" es como un puntero que ejecuta comandos SQL

    # Paso 2: Crear la tabla de USUARIOS (si no existe)
    # Esta tabla almacena las credenciales de acceso al sistema
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- ID único auto-incrementable
            usuario TEXT UNIQUE NOT NULL,            -- Nombre de usuario (no puede repetirse)
            clave TEXT NOT NULL                      -- Contraseña del usuario
        )
    """)

    # Paso 3: Crear la tabla de HABITANTES (si no existe)
    # Esta es la tabla principal donde se guardan todos los datos del censo
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habitantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,       -- ID único del habitante
            nombres TEXT NOT NULL,                       -- Nombres del habitante
            apellidos TEXT NOT NULL,                     -- Apellidos del habitante
            cedula TEXT UNIQUE NOT NULL,                 -- Cédula de identidad (única)
            fecha_nacimiento TEXT NOT NULL,              -- Fecha de nacimiento (DD/MM/AAAA)
            genero TEXT NOT NULL,                        -- Género: Masculino o Femenino
            estado_civil TEXT NOT NULL,                  -- Estado civil
            discapacidad TEXT DEFAULT 'Ninguna',         -- Discapacidad (si tiene)
            direccion TEXT NOT NULL,                     -- Dirección de residencia
            telefono TEXT NOT NULL,                      -- Número de teléfono
            ocupacion TEXT DEFAULT '',                   -- Ocupación o trabajo
            correo TEXT DEFAULT '',                      -- Correo electrónico (opcional)
            tipo_vivienda TEXT NOT NULL,                 -- Tipo de vivienda
            parroquia TEXT NOT NULL,                     -- Parroquia donde vive
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP, -- Fecha automática del registro
            nacionalidad TEXT DEFAULT 'Venezolano/a',   -- Nacionalidad
            pais_origen TEXT DEFAULT '',                 -- País de origen (si es extranjero)
            estado_origen TEXT DEFAULT '',               -- Estado/provincia de origen
            municipio_origen TEXT DEFAULT '',            -- Municipio/ciudad de origen
            nivel_educacion TEXT DEFAULT '',             -- Nivel de educación
            tenencia_vivienda TEXT DEFAULT 'Propia',     -- Si la vivienda es propia/alquilada/cedida
            familia_id INTEGER DEFAULT NULL              -- ID de la familia a la que pertenece
        )
    """)

    # Paso 4: Crear la tabla de FAMILIAS (si no existe)
    # Almacena los grupos familiares con su jefe de familia
    cur.execute("""
        CREATE TABLE IF NOT EXISTS familias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,       -- ID único de la familia
            nombre_familia TEXT NOT NULL,                -- Apellido o nombre de la familia
            jefe_familia_id INTEGER,                    -- ID del habitante que es jefe
            direccion TEXT DEFAULT '',                   -- Dirección de la familia
            parroquia TEXT DEFAULT '',                   -- Parroquia de la familia
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP, -- Fecha de registro
            FOREIGN KEY (jefe_familia_id) REFERENCES habitantes(id)  -- Relación con tabla habitantes
        )
    """)

    # Paso 5: MIGRACIÓN AUTOMÁTICA
    # Si la base de datos ya existía con una versión anterior, estas columnas
    # se agregan automáticamente para no perder los datos existentes.
    columnas_nuevas = [
        ("nacionalidad", "TEXT DEFAULT 'Venezolano/a'"),
        ("pais_origen", "TEXT DEFAULT ''"),
        ("estado_origen", "TEXT DEFAULT ''"),
        ("municipio_origen", "TEXT DEFAULT ''"),
        ("nivel_educacion", "TEXT DEFAULT ''"),
        ("tenencia_vivienda", "TEXT DEFAULT 'Propia'"),
        ("familia_id", "INTEGER DEFAULT NULL"),
    ]
    for col_name, col_type in columnas_nuevas:
        try:
            # ALTER TABLE agrega una columna nueva a una tabla existente
            cur.execute(f"ALTER TABLE habitantes ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass  # Si la columna ya existe, simplemente la ignora (no da error)

    # Paso 6: Crear el usuario administrador por defecto
    try:
        cur.execute(
            "INSERT INTO usuarios (usuario, clave) VALUES (?, ?)",
            ("admin", "admin123")  # Usuario: admin, Contraseña: admin123
        )
    except sqlite3.IntegrityError:
        pass  # Si el usuario ya existe, lo ignora (no duplica)

    # Paso 7: Guardar los cambios y cerrar la conexión
    conn.commit()   # commit() = "guardar" los cambios en el archivo de base de datos
    conn.close()    # close() = cerrar la conexión con la base de datos


def obtener_conexion():
    """
    [FUNCIÓN: OBTENER CONEXIÓN A LA BASE DE DATOS]
    
    ¿Qué hace?
    → Crea y devuelve una nueva conexión a la base de datos.
    
    ¿Por qué se usa?
    → Cada vez que necesitamos leer o escribir datos, abrimos una conexión,
      hacemos la operación, y luego la cerramos. Esto evita bloqueos.
    
    Retorna:
    → Un objeto "Connection" de sqlite3 listo para usar.
    """
    return sqlite3.connect(DB_NAME)


# ════════════════════════════════════════════════════════════
# SECCIÓN 4: FUNCIONES AUXILIARES (UTILIDADES)
# ────────────────────────────────────────────────────────────
# Funciones pequeñas que se reutilizan en varias partes del programa.
# Son "herramientas" que ayudan a hacer cálculos y validaciones.
#
# OPTIMIZACIÓN: Se agregó centrar_ventana() como función global
# (antes estaba duplicada en VentanaLogin y AplicacionCenso).
# Se agregó configurar_scroll_mousewheel() para evitar duplicar
# el mismo código de scroll en las pestañas Registro e Imprimir.
# Se unificó clasificar_edad() para que use RANGOS_EDAD.
# ════════════════════════════════════════════════════════════

def centrar_ventana(root, ancho, alto):
    """
    [FUNCIÓN GLOBAL: CENTRAR VENTANA EN LA PANTALLA]
    
    OPTIMIZACIÓN: Antes esta función estaba duplicada dentro de
    VentanaLogin._centrar_ventana() y AplicacionCenso._centrar_ventana().
    Ahora existe una sola vez aquí y ambas clases la llaman.
    
    ¿Qué hace?
    → Calcula la posición X,Y para que la ventana aparezca centrada.
    
    ¿Cómo funciona?
    → Obtiene el ancho y alto de la pantalla del monitor.
    → Resta el tamaño de la ventana y divide entre 2.
    → Esto da las coordenadas del centro.
    
    Parámetros:
    → root: La ventana de tkinter que se quiere centrar.
    → ancho: Ancho de la ventana en píxeles.
    → alto: Alto de la ventana en píxeles.
    """
    x = (root.winfo_screenwidth() // 2) - (ancho // 2)   # Posición X centrada
    y = (root.winfo_screenheight() // 2) - (alto // 2)   # Posición Y centrada
    root.geometry(f"{ancho}x{alto}+{x}+{y}")  # Aplicar posición


def configurar_scroll_mousewheel(canvas):
    """
    [FUNCIÓN GLOBAL: CONFIGURAR SCROLL CON RUEDA DEL MOUSE]
    
    OPTIMIZACIÓN: Antes este mismo bloque de código estaba duplicado
    en _crear_tab_registro() y _crear_tab_imprimir(). Ahora existe
    una sola vez aquí y ambos métodos la llaman.
    
    ¿Qué hace?
    → Vincula los eventos de la rueda del mouse a un Canvas.
    → Cuando el mouse ENTRA al canvas, se activa el scroll.
    → Cuando el mouse SALE del canvas, se desactiva el scroll.
    → Soporta Windows/Mac (event.delta) y Linux (Button-4/5).
    
    Parámetro:
    → canvas: El widget Canvas de tkinter al que se le agrega scroll.
    """
    def _on_mousewheel(event):
        """Maneja el evento de la rueda del mouse para hacer scroll."""
        if event.delta:
            # Windows/Mac: event.delta contiene la dirección y magnitud
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            # Linux: Button-4 = scroll hacia arriba
            canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            # Linux: Button-5 = scroll hacia abajo
            canvas.yview_scroll(3, "units")

    def _bind_mousewheel(event):
        """Se activa cuando el mouse ENTRA al canvas (empieza a escuchar scroll)."""
        canvas.bind_all("<MouseWheel>", _on_mousewheel)    # Windows/Mac
        canvas.bind_all("<Button-4>", _on_mousewheel)      # Linux arriba
        canvas.bind_all("<Button-5>", _on_mousewheel)      # Linux abajo

    def _unbind_mousewheel(event):
        """Se activa cuando el mouse SALE del canvas (deja de escuchar scroll)."""
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    # Vincular Enter/Leave del mouse al canvas para activar/desactivar scroll
    canvas.bind("<Enter>", _bind_mousewheel)    # Mouse entra → activar scroll
    canvas.bind("<Leave>", _unbind_mousewheel)  # Mouse sale → desactivar scroll


def calcular_edad(fecha_nac_str):
    """
    [FUNCIÓN: CALCULAR EDAD]
    
    ¿Qué hace?
    → Recibe una fecha de nacimiento en formato "DD/MM/AAAA" (texto).
    → Calcula cuántos años tiene esa persona HOY.
    
    ¿Cómo funciona?
    1. Convierte el texto "DD/MM/AAAA" a un objeto fecha de Python.
    2. Obtiene la fecha de hoy.
    3. Resta el año de nacimiento al año actual.
    4. Si aún no ha cumplido años este año, resta 1.
    
    Parámetro:
    → fecha_nac_str (str): Fecha en formato "DD/MM/AAAA", ejemplo: "15/03/1990"
    
    Retorna:
    → int: La edad en años (ejemplo: 35)
    → None: Si la fecha es inválida o tiene formato incorrecto
    """
    try:
        # strptime() convierte un texto a objeto fecha usando el formato indicado
        # %d = día, %m = mes, %Y = año con 4 dígitos
        fecha_nac = datetime.strptime(fecha_nac_str, "%d/%m/%Y").date()
        hoy = date.today()  # Obtiene la fecha de hoy
        
        # Cálculo básico: año actual - año de nacimiento
        edad = hoy.year - fecha_nac.year
        
        # Ajuste: si el mes/día actual es ANTES del cumpleaños, aún no los ha cumplido
        if (hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day):
            edad -= 1  # Resta 1 porque aún no ha cumplido este año
        
        return edad
    except ValueError:
        return None  # Si la fecha es inválida, retorna None (nulo)


def clasificar_edad(edad):
    """
    [FUNCIÓN: CLASIFICAR EDAD EN GRUPO ETARIO]
    
    OPTIMIZACIÓN: Ahora usa el diccionario RANGOS_EDAD en vez de tener
    los rangos duplicados con if/elif. Antes existían DOS fuentes de verdad
    para los mismos rangos; ahora solo hay UNA (RANGOS_EDAD).
    
    ¿Qué hace?
    → Recibe una edad numérica y devuelve a qué grupo pertenece.
    
    Grupos (definidos en RANGOS_EDAD):
    → 0-11 años   = "Niño"
    → 12-17 años  = "Joven"
    → 18-59 años  = "Adulto"
    → 60+ años    = "Adulto Mayor"
    
    Parámetro:
    → edad (int o None): La edad de la persona
    
    Retorna:
    → str: El nombre del grupo etario
    """
    if edad is None:
        return "Desconocido"     # Si no se pudo calcular la edad
    # Recorrer cada rango definido en RANGOS_EDAD
    for nombre_rango, (minimo, maximo) in RANGOS_EDAD.items():
        if minimo <= edad <= maximo:
            # Retornar la etiqueta corta correspondiente
            return ETIQUETAS_GRUPO_ETARIO.get(nombre_rango, "Desconocido")
    return "Desconocido"  # Si no encaja en ningún rango


def validar_email(email):
    """
    [FUNCIÓN: VALIDAR CORREO ELECTRÓNICO]
    
    ¿Qué hace?
    → Verifica si un texto tiene formato válido de correo electrónico.
    → Ejemplo válido: "juan@gmail.com"
    → Ejemplo inválido: "juan@", "juan.com", "@gmail.com"
    
    ¿Cómo funciona?
    → Usa una expresión regular (regex) que define el patrón de un email:
      - Letras/números antes del @
      - Un @ en el medio
      - Un dominio con al menos un punto
    
    Retorna:
    → True: Si el email es válido o está vacío (es opcional)
    → False: Si el email tiene formato incorrecto
    """
    if not email:
        return True  # Si está vacío, es válido (el correo es opcional)
    # El patrón regex define la estructura de un email válido
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None


def solo_numeros(texto):
    """
    [FUNCIÓN: VALIDAR SOLO NÚMEROS]
    
    ¿Qué hace?
    → Verifica que un texto contenga SOLO dígitos numéricos (0-9).
    → Se usa para validar campos como cédula y teléfono.
    
    Retorna:
    → True: Si el texto está vacío o solo contiene números
    → False: Si contiene letras u otros caracteres
    """
    return texto == "" or texto.isdigit()


# ════════════════════════════════════════════════════════════
# SECCIÓN 5: CLASE VentanaLogin (PANTALLA DE INICIO DE SESIÓN)
# ────────────────────────────────────────────────────────────
# Esta clase crea la primera ventana que ve el usuario.
# Muestra un formulario de login con usuario y contraseña.
# Si las credenciales son correctas, abre la aplicación principal.
# ════════════════════════════════════════════════════════════

class VentanaLogin:
    """
    [CLASE: VENTANA DE LOGIN]
    
    ¿Qué es una clase?
    → Es como un "molde" o "plano" que define cómo crear un objeto.
    → En este caso, el objeto es la ventana de inicio de sesión.
    
    ¿Qué contiene?
    → __init__: Se ejecuta al crear la ventana (configuración inicial).
    → _crear_interfaz: Dibuja todos los elementos visuales (labels, botones, etc.).
    → _iniciar_sesion: Verifica usuario/contraseña y abre la app principal.
    
    OPTIMIZACIÓN: Se eliminó el método _centrar_ventana() de esta clase.
    Ahora se usa la función global centrar_ventana().
    """
    
    def __init__(self, root):
        """
        [MÉTODO: CONSTRUCTOR / INICIALIZADOR]
        
        ¿Qué hace?
        → Se ejecuta automáticamente al crear una instancia de VentanaLogin.
        → Configura la ventana principal: título, tamaño, color, posición.
        → Llama a _crear_interfaz() para dibujar los elementos visuales.
        
        Parámetro:
        → root: La ventana principal de tkinter (tk.Tk())
        """
        self.root = root  # Guardar referencia a la ventana principal
        
        # Configurar propiedades de la ventana
        self.root.title("🇻🇪 Censo Poblacional - Iniciar Sesión")  # Título en la barra
        self.root.geometry("600x780")          # Tamaño: 600px ancho x 780px alto
        self.root.resizable(False, False)       # No permitir redimensionar
        self.root.configure(bg=COLORES["blanco"])  # Fondo blanco
        
        # OPTIMIZACIÓN: Ahora usa la función global en vez del método duplicado
        centrar_ventana(self.root, 600, 780)   # Centrar en la pantalla
        self._crear_interfaz()                 # Dibujar los elementos visuales

    def _crear_interfaz(self):
        """
        [MÉTODO: CREAR INTERFAZ DE LOGIN]
        
        ¿Qué hace?
        → Dibuja todos los elementos visuales de la pantalla de login:
          - Franjas de colores de la bandera (rojo, amarillo, azul)
          - Bandera venezolana dibujada en un canvas
          - Títulos del sistema
          - Tarjeta de login con campos de usuario y contraseña
          - Botón de ingresar
          - Texto informativo con las credenciales por defecto
        """
        # ── FRANJAS SUPERIORES (colores de la bandera) ──
        # Son rectángulos horizontales decorativos en la parte superior
        franja_top = tk.Frame(self.root, bg=COLORES["rojo_vzla"], height=8)
        franja_top.pack(fill="x")  # fill="x" = se extiende horizontalmente
        franja_amarilla = tk.Frame(self.root, bg=COLORES["amarillo_vzla"], height=4)
        franja_amarilla.pack(fill="x")
        franja_azul = tk.Frame(self.root, bg=COLORES["azul_vzla"], height=4)
        franja_azul.pack(fill="x")

        # ── FRAME PRINCIPAL ──
        # Contenedor que agrupa todo el contenido central
        main_frame = tk.Frame(self.root, bg=COLORES["blanco"])
        main_frame.pack(expand=True, fill="both", padx=40, pady=20)

        # ── BANDERA VENEZOLANA (dibujada con Canvas) ──
        # Canvas es un "lienzo" donde se pueden dibujar formas geométricas
        bandera_frame = tk.Frame(main_frame, bg=COLORES["fondo_app"])
        bandera_frame.pack(pady=(10, 5))
        canvas_bandera = tk.Canvas(
            bandera_frame, width=200, height=120,
            bg=COLORES["fondo_app"], highlightthickness=0  # Sin borde
        )
        canvas_bandera.pack()
        
        # Dibujar las 3 franjas de la bandera como rectángulos
        canvas_bandera.create_rectangle(0, 0, 200, 40, fill=COLORES["amarillo_vzla"], outline="")
        canvas_bandera.create_rectangle(0, 40, 200, 80, fill=COLORES["azul_vzla"], outline="")
        canvas_bandera.create_rectangle(0, 80, 200, 120, fill=COLORES["rojo_vzla"], outline="")
        
        # Dibujar 8 estrellas en la franja azul
        for i in range(8):
            x = 60 + i * 12  # Espaciado horizontal entre estrellas
            canvas_bandera.create_text(x, 60, text="★", fill=COLORES["blanco"],
                                        font=("Segoe UI", 8, "bold"))
        
        # Dibujar el escudo (un círculo con "VE")
        canvas_bandera.create_oval(85, 45, 115, 75, fill=COLORES["rojo_vzla"],
                                    outline=COLORES["amarillo_vzla"], width=2)
        canvas_bandera.create_text(100, 60, text="VE", fill=COLORES["blanco"],
                                    font=("Segoe UI", 9, "bold"))

        # ── TÍTULOS DEL SISTEMA ──
        tk.Label(
            main_frame, text="🇻🇪 CENSO POBLACIONAL",
            font=("Segoe UI", 22, "bold"), fg=COLORES["gris_oscuro"],
            bg=COLORES["blanco"]
        ).pack(pady=(10, 0))
        tk.Label(
            main_frame, text="Municipio Junín — Estado Táchira",
            font=FUENTE_NORMAL, fg=COLORES["gris_oscuro"],
            bg=COLORES["blanco"]
        ).pack(pady=(0, 5))
        tk.Label(
            main_frame, text="República Bolivariana de Venezuela",
            font=FUENTE_SMALL, fg=COLORES["gris_oscuro"],
            bg=COLORES["blanco"]
        ).pack(pady=(0, 20))

        # ── TARJETA DE LOGIN ──
        # Es un Frame estilizado como "tarjeta" con fondo oscuro y borde rojo
        card = tk.Frame(main_frame, bg=COLORES["fondo_panel"],
                        highlightbackground=COLORES["rojo_vzla"],
                        highlightthickness=2, padx=30, pady=25)
        card.pack(fill="x")

        # Título de la tarjeta
        tk.Label(card, text="INICIAR SESIÓN", font=FUENTE_SUBTITULO,
                 fg=COLORES["blanco"], bg=COLORES["fondo_panel"]).pack(pady=(0, 20))

        # ── CAMPO DE USUARIO ──
        tk.Label(card, text="👤 Usuario:", font=FUENTE_NORMAL,
                 fg=COLORES["texto_claro"], bg=COLORES["fondo_panel"],
                 anchor="w").pack(fill="x")  # anchor="w" = alineado a la izquierda (west)
        
        # Entry = campo de texto donde el usuario escribe
        self.entry_usuario = tk.Entry(card, font=FUENTE_NORMAL, bg=COLORES["blanco"],
                                      fg=COLORES["gris_oscuro"],
                                      insertbackground=COLORES["gris_oscuro"],  # Color del cursor
                                      relief="flat", bd=0)  # Sin borde 3D
        self.entry_usuario.pack(fill="x", ipady=8, pady=(2, 15))  # ipady = padding interno

        # ── CAMPO DE CONTRASEÑA ──
        tk.Label(card, text="🔒 Contraseña:", font=FUENTE_NORMAL,
                 fg=COLORES["texto_claro"], bg=COLORES["fondo_panel"],
                 anchor="w").pack(fill="x")
        
        # show="●" hace que cada carácter se muestre como un punto (ocultar contraseña)
        self.entry_clave = tk.Entry(card, font=FUENTE_NORMAL, show="●",
                                    bg=COLORES["blanco"], fg=COLORES["gris_oscuro"],
                                    insertbackground=COLORES["gris_oscuro"],
                                    relief="flat", bd=0)
        self.entry_clave.pack(fill="x", ipady=8, pady=(2, 20))
        
        # Vincular la tecla Enter para que también inicie sesión
        self.entry_clave.bind("<Return>", lambda e: self._iniciar_sesion())

        # ── BOTÓN DE INGRESAR ──
        btn_login = tk.Button(card, text="INGRESAR AL SISTEMA", font=FUENTE_BOTON,
                              bg=COLORES["rojo_vzla"], fg=COLORES["blanco"],
                              activebackground=COLORES["rojo_oscuro"],  # Color al hacer clic
                              activeforeground=COLORES["blanco"], relief="flat",
                              cursor="hand2",  # Cursor de mano al pasar por encima
                              command=self._iniciar_sesion, bd=0)
        btn_login.pack(fill="x", ipady=10)
        
        # Efecto hover: cambiar color cuando el mouse pasa por encima
        btn_login.bind("<Enter>", lambda e: btn_login.config(bg=COLORES["rojo_oscuro"]))
        btn_login.bind("<Leave>", lambda e: btn_login.config(bg=COLORES["rojo_vzla"]))

        # ── TEXTO INFORMATIVO (credenciales por defecto) ──
        tk.Label(
            main_frame,
            text="Credenciales del sistema: Usuario: admin | Contraseña: admin123",
            font=("Segoe UI", 12, "bold"), fg=COLORES["gris_oscuro"],
            bg=COLORES["blanco"], wraplength=520, justify="center"
        ).pack(pady=(18, 0))

        # ── FRANJA INFERIOR DECORATIVA ──
        franja_bottom = tk.Frame(self.root, bg=COLORES["rojo_vzla"], height=8)
        franja_bottom.pack(side="bottom", fill="x")

    def _iniciar_sesion(self):
        """
        [MÉTODO: VERIFICAR CREDENCIALES E INICIAR SESIÓN]
        
        ¿Qué hace?
        → Obtiene lo que el usuario escribió en los campos.
        → Busca en la base de datos si existe esa combinación usuario/contraseña.
        → Si es correcta: cierra la ventana de login y abre la aplicación principal.
        → Si es incorrecta: muestra un mensaje de error.
        
        Flujo:
        1. Leer campos → 2. Validar vacíos → 3. Consultar BD → 4. Abrir app o mostrar error
        """
        # Obtener texto de los campos (strip() elimina espacios al inicio y final)
        usuario = self.entry_usuario.get().strip()
        clave = self.entry_clave.get().strip()
        
        # Validar que no estén vacíos
        if not usuario or not clave:
            messagebox.showwarning("Campos vacíos", "Ingrese usuario y contraseña.")
            return
        
        # Buscar en la base de datos si existe la combinación usuario + contraseña
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario=? AND clave=?", (usuario, clave))
        resultado = cur.fetchone()  # fetchone() obtiene una fila o None si no hay
        conn.close()
        
        if resultado:
            # ✅ LOGIN EXITOSO
            self.root.destroy()               # Cerrar la ventana de login
            root_app = tk.Tk()                # Crear nueva ventana para la app
            AplicacionCenso(root_app, usuario) # Iniciar la aplicación principal
            root_app.mainloop()               # Mantener la app abierta
        else:
            # ❌ CREDENCIALES INCORRECTAS
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")


# ════════════════════════════════════════════════════════════
# SECCIÓN 6: CLASE AplicacionCenso (APLICACIÓN PRINCIPAL)
# ────────────────────────────────────────────────────────────
# Esta es la clase más grande del programa.
# Contiene toda la lógica de la aplicación principal:
# - Formulario de registro
# - Tabla de habitantes
# - Gestión de familias
# - Estadísticas
# - Impresión/Exportación
# ════════════════════════════════════════════════════════════

class AplicacionCenso:
    """
    [CLASE: APLICACIÓN PRINCIPAL DEL CENSO]
    
    ¿Qué es?
    → Es la ventana principal que aparece después del login.
    → Tiene 5 pestañas (tabs) con diferentes funcionalidades.
    
    Pestañas:
    1. 📝 Registro: Formulario para agregar nuevos habitantes.
    2. 👥 Habitantes: Tabla con todos los registros (buscar, filtrar, editar).
    3. 👨‍👩‍👧‍👦 Familias: Gestionar grupos familiares.
    4. 📊 Estadísticas: Gráficos de distribución.
    5. 🖨️ Imprimir: Generar planillas HTML para imprimir.
    
    Atributos principales:
    → self.root: La ventana de tkinter
    → self.notebook: El widget de pestañas
    → self.campos: Diccionario con todos los campos del formulario
    → self.tree_habitantes: Tabla de habitantes
    → self.tree_familias: Tabla de familias
    
    OPTIMIZACIONES:
    → Se eliminó _centrar_ventana() (usa función global).
    → Se eliminó _exportar_csv() (wrapper innecesario con nombre engañoso).
    → Se simplificó _cargar_habitantes() (sin variable count innecesaria,
      sin recarga de familias al buscar/filtrar).
    """
    
    def __init__(self, root, usuario_actual):
        """
        [MÉTODO: CONSTRUCTOR DE LA APLICACIÓN PRINCIPAL]
        
        ¿Qué hace?
        → Configura la ventana principal (título, tamaño, color).
        → Registra la validación de solo números para campos numéricos.
        → Crea los estilos visuales (colores de widgets).
        → Construye toda la interfaz (pestañas, formularios, tablas).
        → Carga los datos existentes de la base de datos.
        → Configura los atajos de teclado.
        
        Parámetros:
        → root: Ventana principal de tkinter.
        → usuario_actual: Nombre del usuario que inició sesión.
        """
        self.root = root
        self.usuario_actual = usuario_actual
        
        # Configurar la ventana principal
        self.root.title(f"🇻🇪 Censo Poblacional — Municipio Junín, Táchira | Usuario: {usuario_actual}")
        self.root.geometry("1350x800")          # Tamaño de la ventana
        self.root.minsize(1200, 700)            # Tamaño mínimo (no puede ser más pequeña)
        self.root.configure(bg=COLORES["fondo_app"])  # Fondo azul oscuro
        # OPTIMIZACIÓN: Usa función global en vez de método duplicado
        centrar_ventana(self.root, 1350, 800)

        # Registrar la función de validación numérica para usarla en campos Entry
        # vcmd_num se pasa como parámetro "validatecommand" a los Entry de solo números
        self.vcmd_num = (self.root.register(solo_numeros), '%P')
        # '%P' es una sustitución de tkinter: pasa el texto que QUEDARÁ después de escribir

        # Inicializar la interfaz
        self._crear_estilos()       # Configurar colores y temas de los widgets
        self._crear_interfaz()      # Construir toda la interfaz visual
        self._cargar_habitantes()   # Cargar habitantes existentes desde la base de datos
        self._cargar_familias()     # Cargar familias existentes desde la base de datos

        # ── ATAJOS DE TECLADO ──
        # Permiten navegar más rápido usando combinaciones de teclas
        self.root.bind("<Control-n>", lambda e: self.notebook.select(0))  # Ctrl+N → Ir a Registro
        self.root.bind("<Control-h>", lambda e: self.notebook.select(1))  # Ctrl+H → Ir a Habitantes
        self.root.bind("<Control-f>", lambda e: self.notebook.select(2))  # Ctrl+F → Ir a Familias
        self.root.bind("<Control-e>", lambda e: self.notebook.select(3))  # Ctrl+E → Ir a Estadísticas
        self.root.bind("<Control-p>", lambda e: self.notebook.select(4))  # Ctrl+P → Ir a Imprimir
        self.root.bind("<Control-s>", lambda e: self._guardar_habitante())  # Ctrl+S → Guardar
        self.root.bind("<Control-l>", lambda e: self._limpiar_formulario()) # Ctrl+L → Limpiar
        self.root.bind("<Escape>", lambda e: self._limpiar_formulario())    # Escape → Limpiar

    def _crear_estilos(self):
        """
        [MÉTODO: CONFIGURAR ESTILOS VISUALES]
        
        ¿Qué hace?
        → Personaliza la apariencia de los widgets de ttk (Treeview, Notebook, etc.)
        → ttk usa "estilos" que se configuran una vez y se aplican a todos los widgets.
        
        ¿Qué configura?
        → TNotebook: Las pestañas (color de fondo, color de texto, padding).
        → TNotebook.Tab: Cada pestaña individual (color normal y seleccionada).
        → Treeview: Las tablas (colores de filas, encabezados, selección).
        → TCombobox: Los menús desplegables.
        """
        style = ttk.Style()
        style.theme_use("clam")  # "clam" es un tema base que permite más personalización
        
        # Estilo del contenedor de pestañas
        style.configure("TNotebook", background=COLORES["fondo_app"], borderwidth=0)
        
        # Estilo de cada pestaña individual
        style.configure("TNotebook.Tab", background=COLORES["fondo_panel"],
                        foreground=COLORES["texto_claro"], padding=[20, 10],
                        font=FUENTE_BOTON)
        # map() define estilos para estados específicos (seleccionada, hover, etc.)
        style.map("TNotebook.Tab",
                  background=[("selected", COLORES["rojo_vzla"])],    # Pestaña activa = roja
                  foreground=[("selected", COLORES["blanco"])])       # Texto = blanco
        
        # Estilo de las tablas (Treeview)
        style.configure("Treeview", background=COLORES["fondo_panel"],
                        foreground=COLORES["texto_claro"],
                        fieldbackground=COLORES["fondo_panel"],
                        rowheight=30, font=FUENTE_SMALL)
        style.configure("Treeview.Heading", background=COLORES["rojo_vzla"],
                        foreground=COLORES["blanco"],
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", COLORES["azul_vzla"])],    # Fila seleccionada = azul
                  foreground=[("selected", COLORES["blanco"])])
        
        # Estilo de los menús desplegables
        style.configure("TCombobox", fieldbackground=COLORES["fondo_card"],
                        background=COLORES["fondo_card"],
                        foreground=COLORES["blanco"])
        
        # Estilo para secciones con marco (LabelFrame)
        style.configure("Seccion.TLabelframe", background=COLORES["fondo_panel"],
                        foreground=COLORES["amarillo_vzla"])
        style.configure("Seccion.TLabelframe.Label", background=COLORES["fondo_panel"],
                        foreground=COLORES["amarillo_vzla"], font=FUENTE_SECCION)

    # ────────────────────────────────────────────────────────
    # INTERFAZ PRINCIPAL (Encabezado + Pestañas)
    # ────────────────────────────────────────────────────────

    def _crear_interfaz(self):
        """
        [MÉTODO: CONSTRUIR LA INTERFAZ PRINCIPAL]
        
        ¿Qué hace?
        → Crea el encabezado superior con el título y botón de cerrar sesión.
        → Crea las franjas decorativas (amarillo, azul).
        → Crea el Notebook (sistema de pestañas) con 5 pestañas.
        → Crea el pie de página con información del sistema.
        """
        # ── ENCABEZADO SUPERIOR ──
        header = tk.Frame(self.root, bg=COLORES["rojo_vzla"], height=50)
        header.pack(fill="x")
        header.pack_propagate(False)  # Evita que el frame cambie de tamaño
        
        # Línea amarilla decorativa a la izquierda
        tk.Frame(header, bg=COLORES["amarillo_vzla"], width=6).pack(side="left", fill="y")
        
        # Título del sistema
        tk.Label(header, text="★ CENSO POBLACIONAL COMUNITARIO ★",
                 font=("Segoe UI", 16, "bold"), fg=COLORES["blanco"],
                 bg=COLORES["rojo_vzla"]).pack(side="left", padx=15)
        tk.Label(header, text="Municipio Junín | Estado Táchira",
                 font=FUENTE_NORMAL, fg=COLORES["amarillo_vzla"],
                 bg=COLORES["rojo_vzla"]).pack(side="left", padx=10)

        # Botón de cerrar sesión (alineado a la derecha)
        btn_logout = tk.Button(header, text="🚪 Cerrar Sesión", font=FUENTE_SMALL,
                               bg=COLORES["rojo_oscuro"], fg=COLORES["blanco"],
                               relief="flat", cursor="hand2",
                               command=self._cerrar_sesion, bd=0)
        btn_logout.pack(side="right", padx=15, pady=10)

        # ── FRANJAS DECORATIVAS ──
        franjas = tk.Frame(self.root, bg=COLORES["fondo_app"])
        franjas.pack(fill="x")
        tk.Frame(franjas, bg=COLORES["amarillo_vzla"], height=3).pack(fill="x")
        tk.Frame(franjas, bg=COLORES["azul_vzla"], height=3).pack(fill="x")

        # ── NOTEBOOK (SISTEMA DE PESTAÑAS) ──
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Pestaña 1: REGISTRO de nuevos habitantes
        self.tab_registro = tk.Frame(self.notebook, bg=COLORES["fondo_app"])
        self.notebook.add(self.tab_registro, text="  📝 Registro  ")
        self._crear_tab_registro()

        # Pestaña 2: LISTA DE HABITANTES registrados
        self.tab_habitantes = tk.Frame(self.notebook, bg=COLORES["fondo_app"])
        self.notebook.add(self.tab_habitantes, text="  👥 Habitantes  ")
        self._crear_tab_habitantes()

        # Pestaña 3: GESTIÓN DE FAMILIAS
        self.tab_familias = tk.Frame(self.notebook, bg=COLORES["fondo_app"])
        self.notebook.add(self.tab_familias, text="  👨‍👩‍👧‍👦 Familias  ")
        self._crear_tab_familias()

        # Pestaña 4: ESTADÍSTICAS y gráficos
        self.tab_stats = tk.Frame(self.notebook, bg=COLORES["fondo_app"])
        self.notebook.add(self.tab_stats, text="  📊 Estadísticas  ")
        self._crear_tab_estadisticas()

        # Pestaña 5: IMPRIMIR / EXPORTAR reportes
        self.tab_imprimir = tk.Frame(self.notebook, bg=COLORES["fondo_app"])
        self.notebook.add(self.tab_imprimir, text="  🖨️ Imprimir  ")
        self._crear_tab_imprimir()

        # ── PIE DE PÁGINA ──
        footer = tk.Frame(self.root, bg=COLORES["rojo_vzla"], height=30)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        tk.Label(footer,
                 text="🇻🇪 República Bolivariana de Venezuela — Sistema de Censo Poblacional v3.0 ★",
                 font=("Segoe UI", 9), fg=COLORES["amarillo_vzla"],
                 bg=COLORES["rojo_vzla"]).pack(expand=True)

    # ────────────────────────────────────────────────────────
    # PESTAÑA 1: FORMULARIO DE REGISTRO
    # ────────────────────────────────────────────────────────

    def _crear_tab_registro(self):
        """
        [MÉTODO: CREAR PESTAÑA DE REGISTRO]
        
        ¿Qué hace?
        → Crea un formulario scrolleable con todos los campos del censo.
        → Organiza los campos en 3 secciones: Datos Personales, Socioeconómicos y Vivienda.
        → Incluye botones: Guardar, Actualizar, Eliminar y Limpiar.
        
        OPTIMIZACIÓN: El código de scroll con mousewheel ahora usa la función
        global configurar_scroll_mousewheel() en vez de repetir el mismo código.
        """
        # ── SISTEMA DE SCROLL ──
        canvas = tk.Canvas(self.tab_registro, bg=COLORES["fondo_app"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.tab_registro, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLORES["fondo_app"])

        # Cuando scroll_frame cambia de tamaño, actualizar la región de scroll
        scroll_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ── AJUSTE DE ANCHO RESPONSIVO ──
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        # OPTIMIZACIÓN: Usa función global en vez de código duplicado
        configurar_scroll_mousewheel(canvas)

        # ── TÍTULO DEL FORMULARIO ──
        titulo_frame = tk.Frame(scroll_frame, bg=COLORES["fondo_card"], padx=15, pady=10)
        titulo_frame.pack(fill="x", padx=20, pady=(15, 10))
        tk.Label(titulo_frame, text="📋 FORMULARIO DE REGISTRO DE HABITANTE",
                 font=FUENTE_SUBTITULO, fg=COLORES["amarillo_vzla"],
                 bg=COLORES["fondo_card"]).pack(anchor="w")

        # ── DICCIONARIO DE CAMPOS ──
        self.campos = {}

        # ── FUNCIÓN AUXILIAR: CREAR CAMPO ──
        def crear_campo(parent, label, row, col, tipo="entry", opciones=None,
                        validar_num=False, ancho=30):
            """
            [FUNCIÓN INTERNA: CREAR UN CAMPO DEL FORMULARIO]
            
            ¿Qué hace?
            → Crea un par Label + Widget (campo de texto, desplegable, etc.)
            → Los posiciona en una cuadrícula (grid) usando fila y columna.
            
            Parámetros:
            → parent: Frame contenedor donde se coloca el campo
            → label: Texto de la etiqueta (ej: "Nombres:")
            → row: Número de fila en la cuadrícula
            → col: Número de columna (0=izquierda, 1=derecha)
            → tipo: "entry" (texto), "combo" (desplegable), "text" (texto grande)
            → opciones: Lista de opciones para Combobox
            → validar_num: Si True, solo acepta números
            → ancho: Ancho del campo en caracteres
            
            Retorna:
            → El widget creado (Entry, Combobox o Text)
            """
            lbl = tk.Label(parent, text=label, font=FUENTE_NORMAL,
                           fg=COLORES["texto_claro"], bg=COLORES["fondo_panel"],
                           anchor="w")
            lbl.grid(row=row, column=col * 2, sticky="w", padx=5, pady=6)

            if tipo == "entry":
                kwargs = dict(font=FUENTE_NORMAL, bg=COLORES["fondo_card"],
                              fg=COLORES["blanco"], insertbackground=COLORES["blanco"],
                              relief="flat", width=ancho,
                              highlightthickness=2,
                              highlightcolor=COLORES["amarillo_vzla"],
                              highlightbackground=COLORES["fondo_panel"])
                if validar_num:
                    kwargs["validate"] = "key"
                    kwargs["validatecommand"] = self.vcmd_num
                widget = tk.Entry(parent, **kwargs)
                
            elif tipo == "combo":
                widget = ttk.Combobox(parent, values=opciones, state="readonly",
                                      font=FUENTE_NORMAL, width=ancho - 2)
                
            elif tipo == "text":
                widget = tk.Text(parent, font=FUENTE_NORMAL, bg=COLORES["fondo_card"],
                                 fg=COLORES["blanco"], insertbackground=COLORES["blanco"],
                                 relief="flat", width=ancho, height=2)

            widget.grid(row=row, column=col * 2 + 1, sticky="ew", padx=5, pady=6)
            return widget

        # ═══════════════════════════════════════════
        # SECCIÓN 1: DATOS PERSONALES
        # ═══════════════════════════════════════════
        seccion1_frame = tk.Frame(scroll_frame, bg=COLORES["fondo_panel"],
                                  highlightbackground=COLORES["azul_vzla"],
                                  highlightthickness=1, padx=25, pady=15)
        seccion1_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(seccion1_frame, text="━━━ 👤 DATOS PERSONALES ━━━",
                 font=FUENTE_SECCION, fg=COLORES["amarillo_vzla"],
                 bg=COLORES["fondo_panel"]).grid(row=0, column=0, columnspan=4,
                                                   sticky="w", padx=5, pady=(0, 10))

        self.campos["nombres"] = crear_campo(seccion1_frame, "Nombres:", 1, 0)
        self.campos["apellidos"] = crear_campo(seccion1_frame, "Apellidos:", 1, 1)
        self.campos["cedula"] = crear_campo(seccion1_frame, "Cédula:", 2, 0, validar_num=True)
        self.campos["fecha_nac"] = crear_campo(seccion1_frame, "F. Nacimiento (DD/MM/AAAA):", 2, 1)
        self.campos["genero"] = crear_campo(seccion1_frame, "Género:", 3, 0,
                                            tipo="combo", opciones=GENEROS)
        self.campos["estado_civil"] = crear_campo(seccion1_frame, "Estado Civil:", 3, 1,
                                                  tipo="combo", opciones=ESTADOS_CIVILES)
        self.campos["discapacidad"] = crear_campo(seccion1_frame, "Discapacidad:", 4, 0)
        self.campos["telefono"] = crear_campo(seccion1_frame, "Teléfono:", 4, 1,
                                              validar_num=True)
        self.campos["correo"] = crear_campo(seccion1_frame, "Correo Electrónico:", 5, 0)
        self.campos["nacionalidad"] = crear_campo(seccion1_frame, "Nacionalidad:", 5, 1,
                                                  tipo="combo", opciones=NACIONALIDADES)
        self.campos["nacionalidad"].bind("<<ComboboxSelected>>",
                                         lambda e: self._toggle_extranjero())

        # ── FRAME DE DATOS DE EXTRANJERO (oculto inicialmente) ──
        self.frame_extranjero = tk.Frame(seccion1_frame, bg=COLORES["fondo_panel"])
        self.frame_extranjero.grid(row=6, column=0, columnspan=4, sticky="ew",
                                   padx=5, pady=5)

        tk.Label(self.frame_extranjero, text="  🌍 Datos de origen (extranjero):",
                 font=FUENTE_SMALL, fg=COLORES["acento"],
                 bg=COLORES["fondo_panel"]).grid(row=0, column=0, columnspan=4,
                                                   sticky="w", pady=(0, 5))

        self.campos["pais_origen"] = crear_campo(self.frame_extranjero, "País de origen:", 1, 0,
                                                 tipo="combo", opciones=PAISES)
        self.campos["estado_origen"] = crear_campo(self.frame_extranjero, "Estado/Provincia:", 1, 1)
        self.campos["municipio_origen"] = crear_campo(self.frame_extranjero, "Municipio/Ciudad:", 2, 0)

        self.frame_extranjero.grid_remove()

        # ═══════════════════════════════════════════
        # SECCIÓN 2: DATOS SOCIOECONÓMICOS
        # ═══════════════════════════════════════════
        seccion2_frame = tk.Frame(scroll_frame, bg=COLORES["fondo_panel"],
                                  highlightbackground=COLORES["verde"],
                                  highlightthickness=1, padx=25, pady=15)
        seccion2_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(seccion2_frame, text="━━━ 💼 DATOS SOCIOECONÓMICOS ━━━",
                 font=FUENTE_SECCION, fg=COLORES["amarillo_vzla"],
                 bg=COLORES["fondo_panel"]).grid(row=0, column=0, columnspan=4,
                                                   sticky="w", padx=5, pady=(0, 10))

        self.campos["ocupacion"] = crear_campo(seccion2_frame, "Ocupación:", 1, 0)
        self.campos["nivel_educacion"] = crear_campo(seccion2_frame, "Nivel de Educación:", 1, 1,
                                                     tipo="combo", opciones=NIVELES_EDUCACION)

        # ═══════════════════════════════════════════
        # SECCIÓN 3: DATOS DE VIVIENDA Y HOGAR
        # ═══════════════════════════════════════════
        seccion3_frame = tk.Frame(scroll_frame, bg=COLORES["fondo_panel"],
                                  highlightbackground=COLORES["naranja"],
                                  highlightthickness=1, padx=25, pady=15)
        seccion3_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(seccion3_frame, text="━━━ 🏠 DATOS DE VIVIENDA Y HOGAR ━━━",
                 font=FUENTE_SECCION, fg=COLORES["amarillo_vzla"],
                 bg=COLORES["fondo_panel"]).grid(row=0, column=0, columnspan=4,
                                                   sticky="w", padx=5, pady=(0, 10))

        self.campos["tipo_vivienda"] = crear_campo(seccion3_frame, "Tipo de Vivienda:", 1, 0,
                                                   tipo="combo", opciones=TIPOS_VIVIENDA)
        self.campos["tenencia_vivienda"] = crear_campo(seccion3_frame, "Tenencia de Vivienda:", 1, 1,
                                                       tipo="combo", opciones=TENENCIA_VIVIENDA)
        self.campos["parroquia"] = crear_campo(seccion3_frame, "Parroquia:", 2, 0,
                                               tipo="combo", opciones=PARROQUIAS_JUNIN)

        # Campo de dirección (ocupa todo el ancho)
        lbl_dir = tk.Label(seccion3_frame, text="Dirección:", font=FUENTE_NORMAL,
                           fg=COLORES["texto_claro"], bg=COLORES["fondo_panel"],
                           anchor="w")
        lbl_dir.grid(row=3, column=0, sticky="w", padx=5, pady=6)
        self.campos["direccion"] = tk.Entry(
            seccion3_frame, font=FUENTE_NORMAL, bg=COLORES["fondo_card"],
            fg=COLORES["blanco"], insertbackground=COLORES["blanco"],
            relief="flat", width=70
        )
        self.campos["direccion"].grid(row=3, column=1, columnspan=3,
                                      sticky="ew", padx=5, pady=6)

        # ── BARRA DE INFORMACIÓN FIJA ──
        info_frame = tk.Frame(scroll_frame, bg=COLORES["azul_vzla"], padx=15, pady=8)
        info_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(info_frame,
                 text="📍 Estado: Táchira  |  Municipio: Junín  |  La edad se calcula automáticamente",
                 font=FUENTE_SMALL, fg=COLORES["amarillo_vzla"],
                 bg=COLORES["azul_vzla"]).pack(anchor="w")

        # ── BOTONES DE ACCIÓN ──
        btn_frame = tk.Frame(scroll_frame, bg=COLORES["fondo_app"])
        btn_frame.pack(fill="x", padx=20, pady=15)

        botones = [
            ("💾 Guardar", COLORES["verde"], self._guardar_habitante),
            ("✏️ Actualizar", COLORES["azul_vzla"], self._actualizar_habitante),
            ("🗑️ Eliminar", COLORES["acento"], self._eliminar_habitante),
            ("🧹 Limpiar", COLORES["naranja"], self._limpiar_formulario),
        ]

        for texto, color, comando in botones:
            btn = tk.Button(btn_frame, text=texto, font=FUENTE_BOTON,
                            bg=color, fg=COLORES["blanco"], relief="flat",
                            cursor="hand2", command=comando, bd=0, padx=20, pady=8)
            btn.pack(side="left", padx=5)
            color_hover = COLORES["rojo_oscuro"]
            btn.bind("<Enter>", lambda e, b=btn, c=color_hover: b.config(bg=c))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))

        # Variable para saber si estamos editando un habitante existente
        self.habitante_id_seleccionado = None

    def _toggle_extranjero(self):
        """
        [MÉTODO: MOSTRAR/OCULTAR CAMPOS DE EXTRANJERO]
        
        ¿Qué hace?
        → Si la nacionalidad seleccionada es "Extranjero/a", muestra los campos adicionales.
        → Si es "Venezolano/a", oculta esos campos y los limpia.
        """
        nac = self.campos["nacionalidad"].get()
        if nac == "Extranjero/a":
            self.frame_extranjero.grid()
        else:
            self.frame_extranjero.grid_remove()
            self.campos["pais_origen"].set("")
            self.campos["estado_origen"].delete(0, "end")
            self.campos["municipio_origen"].delete(0, "end")

    # ────────────────────────────────────────────────────────
    # PESTAÑA 2: TABLA DE HABITANTES
    # ────────────────────────────────────────────────────────

    def _crear_tab_habitantes(self):
        """
        [MÉTODO: CREAR PESTAÑA DE HABITANTES]
        
        ¿Qué hace?
        → Crea una barra de herramientas con búsqueda, filtros y botones.
        → Crea un contador de habitantes.
        → Crea una tabla (Treeview) con columnas para mostrar los datos.
        """
        # ── BARRA DE HERRAMIENTAS ──
        toolbar = tk.Frame(self.tab_habitantes, bg=COLORES["fondo_card"], padx=15, pady=10)
        toolbar.pack(fill="x", padx=10, pady=(10, 5))

        # Campo de búsqueda
        tk.Label(toolbar, text="🔍 Buscar:", font=FUENTE_NORMAL,
                 fg=COLORES["texto_claro"], bg=COLORES["fondo_card"]).pack(side="left")

        self.entry_busqueda = tk.Entry(toolbar, font=FUENTE_NORMAL,
                                       bg=COLORES["fondo_panel"], fg=COLORES["blanco"],
                                       insertbackground=COLORES["blanco"],
                                       relief="flat", width=30)
        self.entry_busqueda.pack(side="left", padx=10, ipady=5)
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self._buscar_habitantes())

        # Filtro de género
        tk.Label(toolbar, text="Género:", font=FUENTE_NORMAL,
                 fg=COLORES["texto_claro"], bg=COLORES["fondo_card"]).pack(side="left", padx=(20, 5))
        self.filtro_genero = ttk.Combobox(toolbar, values=["Todos"] + GENEROS,
                                          state="readonly", font=FUENTE_SMALL, width=12)
        self.filtro_genero.set("Todos")
        self.filtro_genero.pack(side="left", padx=5)
        self.filtro_genero.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())

        # Filtro de rango de edad
        tk.Label(toolbar, text="Edad:", font=FUENTE_NORMAL,
                 fg=COLORES["texto_claro"], bg=COLORES["fondo_card"]).pack(side="left", padx=(20, 5))
        self.filtro_edad = ttk.Combobox(toolbar, values=["Todos"] + list(RANGOS_EDAD.keys()),
                                        state="readonly", font=FUENTE_SMALL, width=20)
        self.filtro_edad.set("Todos")
        self.filtro_edad.pack(side="left", padx=5)
        self.filtro_edad.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros())

        # Botón "Ver Detalle"
        btn_detalle = tk.Button(toolbar, text="👁️ Ver Detalle", font=FUENTE_SMALL,
                                bg=COLORES["azul_vzla"], fg=COLORES["blanco"],
                                relief="flat", cursor="hand2",
                                command=self._ver_detalle_habitante, bd=0, padx=15)
        btn_detalle.pack(side="right", padx=5)

        # Botón "Editar"
        btn_editar = tk.Button(toolbar, text="✏️ Editar", font=FUENTE_SMALL,
                               bg=COLORES["naranja"], fg=COLORES["blanco"],
                               relief="flat", cursor="hand2",
                               command=self._editar_desde_tabla, bd=0, padx=15)
        btn_editar.pack(side="right", padx=5)

        # ── CONTADOR DE HABITANTES ──
        self.lbl_contador = tk.Label(self.tab_habitantes, text="Total: 0 habitantes",
                                     font=FUENTE_NORMAL, fg=COLORES["amarillo_vzla"],
                                     bg=COLORES["fondo_app"])
        self.lbl_contador.pack(anchor="w", padx=15, pady=2)

        # ── TABLA DE HABITANTES (Treeview) ──
        columnas = ("id", "nombres", "apellidos", "cedula", "edad",
                    "genero", "parroquia", "telefono", "tipo_vivienda", "nacionalidad")
        tabla_frame = tk.Frame(self.tab_habitantes, bg=COLORES["fondo_app"])
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree_habitantes = ttk.Treeview(tabla_frame, columns=columnas,
                                            show="headings", selectmode="browse")

        encabezados = {
            "id": ("ID", 40), "nombres": ("Nombres", 120),
            "apellidos": ("Apellidos", 120), "cedula": ("Cédula", 100),
            "edad": ("Edad", 50), "genero": ("Género", 80),
            "parroquia": ("Parroquia", 120), "telefono": ("Teléfono", 100),
            "tipo_vivienda": ("Vivienda", 80), "nacionalidad": ("Nacionalidad", 90),
        }

        for col, (texto, ancho) in encabezados.items():
            self.tree_habitantes.heading(col, text=texto)
            self.tree_habitantes.column(col, width=ancho, anchor="center")

        scroll_y = tk.Scrollbar(tabla_frame, orient="vertical",
                                command=self.tree_habitantes.yview)
        self.tree_habitantes.configure(yscrollcommand=scroll_y.set)
        self.tree_habitantes.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        
        # Doble clic en una fila → ver detalle
        self.tree_habitantes.bind("<Double-1>", lambda e: self._ver_detalle_habitante())

    # ────────────────────────────────────────────────────────
    # PESTAÑA 3: GESTIÓN DE FAMILIAS
    # ────────────────────────────────────────────────────────

    def _crear_tab_familias(self):
        """
        [MÉTODO: CREAR PESTAÑA DE FAMILIAS]
        
        ¿Qué hace?
        → Crea una barra con botones: Nueva Familia, Eliminar, Ver Grupo, Vincular, Actualizar Nombre.
        → Crea una tabla que muestra las familias registradas.
        """
        # ── BARRA DE HERRAMIENTAS ──
        top_frame = tk.Frame(self.tab_familias, bg=COLORES["fondo_card"], padx=15, pady=10)
        top_frame.pack(fill="x", padx=10, pady=(10, 5))

        tk.Label(top_frame, text="👨‍👩‍👧‍👦 GESTIÓN DE GRUPOS FAMILIARES",
                 font=FUENTE_SUBTITULO, fg=COLORES["amarillo_vzla"],
                 bg=COLORES["fondo_card"]).pack(side="left")

        # Botones de acción para familias
        btn_nueva = tk.Button(top_frame, text="➕ Nueva Familia", font=FUENTE_BOTON,
                              bg=COLORES["verde"], fg=COLORES["blanco"],
                              relief="flat", cursor="hand2",
                              command=self._nueva_familia, bd=0, padx=15, pady=5)
        btn_nueva.pack(side="right", padx=5)

        btn_eliminar_fam = tk.Button(top_frame, text="🗑️ Eliminar Familia", font=FUENTE_SMALL,
                                     bg=COLORES["acento"], fg=COLORES["blanco"],
                                     relief="flat", cursor="hand2",
                                     command=self._eliminar_familia, bd=0, padx=15, pady=5)
        btn_eliminar_fam.pack(side="right", padx=5)

        btn_ver_grupo = tk.Button(top_frame, text="👁️ Ver Grupo", font=FUENTE_SMALL,
                                  bg=COLORES["azul_vzla"], fg=COLORES["blanco"],
                                  relief="flat", cursor="hand2",
                                  command=self._ver_grupo_familiar, bd=0, padx=15, pady=5)
        btn_ver_grupo.pack(side="right", padx=5)

        btn_vincular = tk.Button(top_frame, text="🔗 Vincular Habitante", font=FUENTE_SMALL,
                                 bg=COLORES["naranja"], fg=COLORES["blanco"],
                                 relief="flat", cursor="hand2",
                                 command=self._vincular_habitante_familia, bd=0, padx=15, pady=5)
        btn_vincular.pack(side="right", padx=5)

        btn_actualizar_nombre = tk.Button(top_frame, text="✏️ Actualizar Nombre", font=FUENTE_SMALL,
                                          bg=COLORES["azul_oscuro"], fg=COLORES["blanco"],
                                          relief="flat", cursor="hand2",
                                          command=self._actualizar_nombre_familia, bd=0, padx=15, pady=5)
        btn_actualizar_nombre.pack(side="right", padx=5)

        # Contador de familias
        self.lbl_contador_familias = tk.Label(self.tab_familias,
                                              text="Total: 0 familias",
                                              font=FUENTE_NORMAL,
                                              fg=COLORES["amarillo_vzla"],
                                              bg=COLORES["fondo_app"])
        self.lbl_contador_familias.pack(anchor="w", padx=15, pady=2)

        # ── TABLA DE FAMILIAS ──
        columnas_fam = ("id", "nombre_familia", "jefe", "cedula_jefe",
                        "miembros", "direccion", "parroquia")
        tabla_fam_frame = tk.Frame(self.tab_familias, bg=COLORES["fondo_app"])
        tabla_fam_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree_familias = ttk.Treeview(tabla_fam_frame, columns=columnas_fam,
                                          show="headings", selectmode="browse")

        encabezados_fam = {
            "id": ("ID", 40), "nombre_familia": ("Nombre Familia", 180),
            "jefe": ("Jefe de Familia", 180), "cedula_jefe": ("Cédula Jefe", 100),
            "miembros": ("Miembros", 70), "direccion": ("Dirección", 200),
            "parroquia": ("Parroquia", 120),
        }

        for col, (texto, ancho) in encabezados_fam.items():
            self.tree_familias.heading(col, text=texto)
            self.tree_familias.column(col, width=ancho, anchor="center")

        scroll_fam = tk.Scrollbar(tabla_fam_frame, orient="vertical",
                                  command=self.tree_familias.yview)
        self.tree_familias.configure(yscrollcommand=scroll_fam.set)
        self.tree_familias.pack(side="left", fill="both", expand=True)
        scroll_fam.pack(side="right", fill="y")

        # Doble clic en una familia → ver sus miembros
        self.tree_familias.bind("<Double-1>", lambda e: self._ver_grupo_familiar())

    def _cargar_familias(self):
        """
        [MÉTODO: CARGAR FAMILIAS EN LA TABLA VISUAL]
        
        ¿Qué hace?
        → Limpia la tabla de familias.
        → Consulta todas las familias de la BD.
        → Para cada familia obtiene: jefe, cédula del jefe y cantidad de miembros.
        → Inserta cada familia como una fila en la tabla.
        → Actualiza el contador.
        """
        for item in self.tree_familias.get_children():
            self.tree_familias.delete(item)

        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT * FROM familias ORDER BY nombre_familia")
        familias = cur.fetchall()

        count = 0
        for fam in familias:
            jefe_nombre = "Sin asignar"
            jefe_cedula = "-"
            if fam[2]:
                cur.execute("SELECT nombres, apellidos, cedula FROM habitantes WHERE id=?",
                            (fam[2],))
                jefe = cur.fetchone()
                if jefe:
                    jefe_nombre = f"{jefe[0]} {jefe[1]}"
                    jefe_cedula = jefe[2]

            cur.execute("SELECT COUNT(*) FROM habitantes WHERE familia_id=?", (fam[0],))
            num_miembros = cur.fetchone()[0]

            self.tree_familias.insert("", "end", values=(
                fam[0], fam[1], jefe_nombre, jefe_cedula,
                num_miembros, fam[3], fam[4]
            ))
            count += 1

        conn.close()
        self.lbl_contador_familias.config(text=f"Total: {count} familias")

    def _nueva_familia(self):
        """
        [MÉTODO: CREAR UNA NUEVA FAMILIA]
        
        ¿Qué hace?
        → Abre una ventana emergente con un formulario.
        → Campos: Nombre de familia, Cédula del jefe, Dirección, Parroquia.
        → El jefe de familia es OPCIONAL.
        → Valida que no exista otra familia con el mismo nombre.
        → Valida que el jefe no pertenezca ya a otra familia.
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Nueva Familia")
        ventana.geometry("450x420")
        ventana.configure(bg=COLORES["fondo_app"])
        ventana.resizable(False, False)

        # Encabezado visual
        hdr = tk.Frame(ventana, bg=COLORES["rojo_vzla"], height=40)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="➕ NUEVA FAMILIA",
                 font=FUENTE_SUBTITULO, fg=COLORES["blanco"],
                 bg=COLORES["rojo_vzla"]).pack(expand=True)
        tk.Frame(ventana, bg=COLORES["amarillo_vzla"], height=3).pack(fill="x")

        # Formulario
        form = tk.Frame(ventana, bg=COLORES["fondo_panel"], padx=25, pady=20)
        form.pack(fill="both", expand=True, padx=15, pady=15)

        # Campo: Nombre de la familia
        tk.Label(form, text="Nombre de la Familia:", font=FUENTE_NORMAL,
                 fg=COLORES["texto_claro"], bg=COLORES["fondo_panel"]).pack(anchor="w")
        entry_nombre = tk.Entry(form, font=FUENTE_NORMAL, bg=COLORES["fondo_card"],
                                fg=COLORES["blanco"], insertbackground=COLORES["blanco"],
                                relief="flat")
        entry_nombre.pack(fill="x", ipady=5, pady=(2, 10))

        # Campo: Cédula del jefe de familia
        tk.Label(form, text="Cédula del Jefe de Familia:", font=FUENTE_NORMAL,
                 fg=COLORES["texto_claro"], bg=COLORES["fondo_panel"]).pack(anchor="w")
        entry_cedula_jefe = tk.Entry(form, font=FUENTE_NORMAL, bg=COLORES["fondo_card"],
                                     fg=COLORES["blanco"], insertbackground=COLORES["blanco"],
                                     relief="flat")
        entry_cedula_jefe.pack(fill="x", ipady=5, pady=(2, 10))

        # Campo: Dirección
        tk.Label(form, text="Dirección:", font=FUENTE_NORMAL,
                 fg=COLORES["texto_claro"], bg=COLORES["fondo_panel"]).pack(anchor="w")
        entry_dir = tk.Entry(form, font=FUENTE_NORMAL, bg=COLORES["fondo_card"],
                             fg=COLORES["blanco"], insertbackground=COLORES["blanco"],
                             relief="flat")
        entry_dir.pack(fill="x", ipady=5, pady=(2, 10))

        # Campo: Parroquia (desplegable)
        tk.Label(form, text="Parroquia:", font=FUENTE_NORMAL,
                 fg=COLORES["texto_claro"], bg=COLORES["fondo_panel"]).pack(anchor="w")
        combo_parr = ttk.Combobox(form, values=PARROQUIAS_JUNIN, state="readonly",
                                  font=FUENTE_NORMAL)
        combo_parr.pack(fill="x", pady=(2, 10))

        def guardar_familia():
            """Valida y guarda la nueva familia en la BD."""
            nombre = entry_nombre.get().strip()
            cedula_jefe = entry_cedula_jefe.get().strip()
            direccion = entry_dir.get().strip()
            parroquia = combo_parr.get()

            if not nombre:
                messagebox.showwarning("Campo requerido", "Ingrese el nombre de la familia.")
                return

            conn = obtener_conexion()
            cur = conn.cursor()

            # Validar nombre duplicado
            cur.execute("SELECT COUNT(*) FROM familias WHERE LOWER(nombre_familia) = LOWER(?)", (nombre,))
            if cur.fetchone()[0] > 0:
                messagebox.showerror("Familia duplicada",
                                     "Este grupo familiar ya existe.\n"
                                     "Por favor, elija un nombre diferente para la familia.")
                conn.close()
                return

            # Validar jefe de familia (opcional)
            jefe_id = None
            if cedula_jefe:
                cur.execute("SELECT id, familia_id FROM habitantes WHERE cedula=?", (cedula_jefe,))
                result = cur.fetchone()
                if result:
                    if result[1] is not None:
                        messagebox.showerror("Habitante ya vinculado",
                                             "Esta persona ya pertenece a otra familia.\n"
                                             "Un habitante no puede estar en dos familias a la vez.")
                        conn.close()
                        return
                    jefe_id = result[0]
                else:
                    messagebox.showerror("Error",
                                         f"No se encontró habitante con cédula {cedula_jefe}.\n"
                                         "Debe registrar al jefe de familia primero.")
                    conn.close()
                    return

            # Insertar la nueva familia
            cur.execute("""
                INSERT INTO familias (nombre_familia, jefe_familia_id, direccion, parroquia)
                VALUES (?, ?, ?, ?)
            """, (nombre, jefe_id, direccion, parroquia))

            familia_id = cur.lastrowid

            # Vincular al jefe con la familia
            if jefe_id:
                cur.execute("UPDATE habitantes SET familia_id=? WHERE id=?",
                            (familia_id, jefe_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", f"Familia '{nombre}' registrada correctamente.")
            ventana.destroy()
            self._cargar_familias()

        tk.Button(form, text="💾 Guardar Familia", font=FUENTE_BOTON,
                  bg=COLORES["verde"], fg=COLORES["blanco"],
                  relief="flat", cursor="hand2", command=guardar_familia,
                  bd=0, padx=20, pady=8).pack(pady=10)

    def _actualizar_nombre_familia(self):
        """
        [MÉTODO: ACTUALIZAR NOMBRE DE FAMILIA]
        
        ¿Qué hace?
        → Permite cambiar el nombre de una familia seleccionada.
        → Valida que el nuevo nombre no esté duplicado.
        """
        seleccion = self.tree_familias.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione una familia de la tabla.")
            return

        item = self.tree_familias.item(seleccion[0])
        fam_id = item["values"][0]
        fam_nombre_actual = item["values"][1]

        ventana = tk.Toplevel(self.root)
        ventana.title(f"Actualizar Nombre de Familia")
        ventana.geometry("450x250")
        ventana.configure(bg=COLORES["fondo_app"])
        ventana.resizable(False, False)

        hdr = tk.Frame(ventana, bg=COLORES["azul_vzla"], height=40)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="✏️ ACTUALIZAR NOMBRE DE FAMILIA",
                 font=FUENTE_SUBTITULO, fg=COLORES["blanco"],
                 bg=COLORES["azul_vzla"]).pack(expand=True)
        tk.Frame(ventana, bg=COLORES["amarillo_vzla"], height=3).pack(fill="x")

        form = tk.Frame(ventana, bg=COLORES["fondo_panel"], padx=25, pady=20)
        form.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(form, text="Nuevo nombre de la familia:", font=FUENTE_NORMAL,
                 fg=COLORES["texto_claro"], bg=COLORES["fondo_panel"]).pack(anchor="w")
        entry_nuevo_nombre = tk.Entry(form, font=FUENTE_NORMAL, bg=COLORES["fondo_card"],
                                       fg=COLORES["blanco"], insertbackground=COLORES["blanco"],
                                       relief="flat")
        entry_nuevo_nombre.pack(fill="x", ipady=5, pady=(2, 10))
        entry_nuevo_nombre.insert(0, fam_nombre_actual)
        entry_nuevo_nombre.select_range(0, tk.END)

        def guardar_nuevo_nombre():
            """Valida y guarda el nuevo nombre en la BD."""
            nuevo_nombre = entry_nuevo_nombre.get().strip()
            if not nuevo_nombre:
                messagebox.showwarning("Campo requerido", "Ingrese el nombre de la familia.")
                return

            conn = obtener_conexion()
            cur = conn.cursor()

            # Validar nombre duplicado (excluyendo la familia actual)
            cur.execute("""
                SELECT COUNT(*) FROM familias 
                WHERE LOWER(nombre_familia) = LOWER(?) AND id != ?
            """, (nuevo_nombre, fam_id))
            if cur.fetchone()[0] > 0:
                messagebox.showerror("Familia duplicada",
                                     "Este grupo familiar ya existe.\n"
                                     "Por favor, elija un nombre diferente.")
                conn.close()
                return

            cur.execute("UPDATE familias SET nombre_familia=? WHERE id=?",
                        (nuevo_nombre, fam_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", f"Nombre actualizado a '{nuevo_nombre}'.")
            ventana.destroy()
            self._cargar_familias()

        tk.Button(form, text="💾 Guardar Cambio", font=FUENTE_BOTON,
                  bg=COLORES["verde"], fg=COLORES["blanco"],
                  relief="flat", cursor="hand2", command=guardar_nuevo_nombre,
                  bd=0, padx=20, pady=8).pack(pady=10)

    def _eliminar_familia(self):
        """
        [MÉTODO: ELIMINAR UNA FAMILIA]
        
        ¿Qué hace?
        → Pide confirmación y elimina la familia seleccionada.
        → Desvincula a todos los miembros (familia_id = NULL).
        → Los habitantes NO se eliminan, solo se desvinculan.
        """
        seleccion = self.tree_familias.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione una familia de la tabla.")
            return

        item = self.tree_familias.item(seleccion[0])
        fam_id = item["values"][0]
        fam_nombre = item["values"][1]

        if not messagebox.askyesno("Confirmar",
                                    f"¿Está seguro de eliminar la familia '{fam_nombre}'?\n"
                                    "Los miembros no serán eliminados, solo desvinculados."):
            return

        conn = obtener_conexion()
        cur = conn.cursor()
        # Desvincular todos los miembros
        cur.execute("UPDATE habitantes SET familia_id=NULL WHERE familia_id=?", (fam_id,))
        # Eliminar la familia
        cur.execute("DELETE FROM familias WHERE id=?", (fam_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", f"Familia '{fam_nombre}' eliminada correctamente.")
        self._cargar_familias()

    def _vincular_habitante_familia(self):
        """
        [MÉTODO: VINCULAR UN HABITANTE A UNA FAMILIA]
        
        ¿Qué hace?
        → Abre una ventana para ingresar la cédula del habitante.
        → Valida que el habitante exista y no pertenezca a otra familia.
        → Lo vincula a la familia seleccionada.
        """
        seleccion = self.tree_familias.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione una familia de la tabla.")
            return

        item = self.tree_familias.item(seleccion[0])
        fam_id = item["values"][0]
        fam_nombre = item["values"][1]

        ventana = tk.Toplevel(self.root)
        ventana.title(f"Vincular habitante a: {fam_nombre}")
        ventana.geometry("400x220")
        ventana.configure(bg=COLORES["fondo_app"])
        ventana.resizable(False, False)

        hdr = tk.Frame(ventana, bg=COLORES["azul_vzla"], height=40)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🔗 VINCULAR HABITANTE",
                 font=FUENTE_SUBTITULO, fg=COLORES["blanco"],
                 bg=COLORES["azul_vzla"]).pack(expand=True)
        tk.Frame(ventana, bg=COLORES["amarillo_vzla"], height=3).pack(fill="x")

        form = tk.Frame(ventana, bg=COLORES["fondo_panel"], padx=25, pady=20)
        form.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(form, text="Cédula del habitante a vincular:", font=FUENTE_NORMAL,
                 fg=COLORES["texto_claro"], bg=COLORES["fondo_panel"]).pack(anchor="w")
        entry_ced = tk.Entry(form, font=FUENTE_NORMAL, bg=COLORES["fondo_card"],
                             fg=COLORES["blanco"], insertbackground=COLORES["blanco"],
                             relief="flat")
        entry_ced.pack(fill="x", ipady=5, pady=(2, 10))

        def vincular():
            """Valida y vincula al habitante con la familia."""
            cedula = entry_ced.get().strip()
            if not cedula:
                messagebox.showwarning("Campo requerido", "Ingrese la cédula del habitante.")
                return

            conn = obtener_conexion()
            cur = conn.cursor()
            cur.execute("SELECT id, familia_id FROM habitantes WHERE cedula=?", (cedula,))
            result = cur.fetchone()
            if not result:
                messagebox.showerror("Error", f"No se encontró habitante con cédula {cedula}.")
                conn.close()
                return

            # Validar que no pertenezca a otra familia
            if result[1] is not None:
                if result[1] == fam_id:
                    messagebox.showinfo("Ya vinculado",
                                        "Este habitante ya pertenece a esta familia.")
                else:
                    messagebox.showerror("Habitante ya vinculado",
                                         "Esta persona ya pertenece a otra familia.\n"
                                         "Un habitante no puede estar en dos familias a la vez.\n"
                                         "Debe desvincularlo de la otra familia primero.")
                conn.close()
                return

            # Vincular
            cur.execute("UPDATE habitantes SET familia_id=? WHERE id=?",
                        (fam_id, result[0]))
            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", f"Habitante vinculado a la familia '{fam_nombre}'.")
            ventana.destroy()
            self._cargar_familias()

        tk.Button(form, text="🔗 Vincular", font=FUENTE_BOTON,
                  bg=COLORES["verde"], fg=COLORES["blanco"],
                  relief="flat", cursor="hand2", command=vincular,
                  bd=0, padx=20, pady=8).pack(pady=5)

    def _ver_grupo_familiar(self):
        """
        [MÉTODO: VER LOS MIEMBROS DE UNA FAMILIA]
        
        ¿Qué hace?
        → Abre una ventana con todos los miembros de la familia seleccionada.
        → Muestra jefe, dirección, parroquia y total de miembros.
        → Permite desvincular miembros, asignar/cambiar jefe y quitar rol de jefe.
        """
        seleccion = self.tree_familias.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione una familia de la tabla.")
            return

        item = self.tree_familias.item(seleccion[0])
        fam_id = item["values"][0]
        fam_nombre = item["values"][1]

        conn = obtener_conexion()
        cur = conn.cursor()

        cur.execute("SELECT * FROM familias WHERE id=?", (fam_id,))
        fam = cur.fetchone()

        cur.execute("SELECT * FROM habitantes WHERE familia_id=? ORDER BY apellidos, nombres",
                    (fam_id,))
        miembros = cur.fetchall()

        jefe_info = None
        if fam[2]:
            cur.execute("SELECT nombres, apellidos, cedula FROM habitantes WHERE id=?", (fam[2],))
            jefe_info = cur.fetchone()

        conn.close()

        # ── CREAR VENTANA DE GRUPO FAMILIAR ──
        ventana = tk.Toplevel(self.root)
        ventana.title(f"Grupo Familiar: {fam_nombre}")
        ventana.geometry("750x600")
        ventana.minsize(750, 600)
        ventana.configure(bg=COLORES["fondo_app"])

        # Encabezado
        hdr = tk.Frame(ventana, bg=COLORES["rojo_vzla"], height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"👨‍👩‍👧‍👦 Familia: {fam_nombre}",
                 font=FUENTE_SUBTITULO, fg=COLORES["blanco"],
                 bg=COLORES["rojo_vzla"]).pack(expand=True)
        tk.Frame(ventana, bg=COLORES["amarillo_vzla"], height=3).pack(fill="x")

        # Información de la familia
        info = tk.Frame(ventana, bg=COLORES["fondo_panel"], padx=20, pady=10)
        info.pack(fill="x", padx=10, pady=5)

        jefe_texto = f"{jefe_info[0]} {jefe_info[1]} (C.I. {jefe_info[2]})" if jefe_info else "Sin asignar"
        tk.Label(info, text=f"Jefe de Familia: {jefe_texto}",
                 font=FUENTE_NORMAL, fg=COLORES["amarillo_vzla"],
                 bg=COLORES["fondo_panel"]).pack(anchor="w")
        tk.Label(info, text=f"Dirección: {fam[3]}  |  Parroquia: {fam[4]}",
                 font=FUENTE_SMALL, fg=COLORES["texto_claro"],
                 bg=COLORES["fondo_panel"]).pack(anchor="w")
        tk.Label(info, text=f"Total de miembros: {len(miembros)}",
                 font=FUENTE_SMALL, fg=COLORES["verde"],
                 bg=COLORES["fondo_panel"]).pack(anchor="w")

        # Tabla de miembros
        cols = ("nombres", "apellidos", "cedula", "edad", "parentesco_info")
        tabla_frame = tk.Frame(ventana, bg=COLORES["fondo_app"])
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=5)

        tree_miembros = ttk.Treeview(tabla_frame, columns=cols,
                                     show="headings", selectmode="browse")
        for c, (txt, w) in {"nombres": ("Nombres", 150), "apellidos": ("Apellidos", 150),
                             "cedula": ("Cédula", 100), "edad": ("Edad", 60),
                             "parentesco_info": ("Rol", 120)}.items():
            tree_miembros.heading(c, text=txt)
            tree_miembros.column(c, width=w, anchor="center")

        for m in miembros:
            edad = calcular_edad(m[4])
            edad_str = str(edad) if edad is not None else "?"
            rol = "JEFE" if (fam[2] and m[0] == fam[2]) else "Miembro"
            tree_miembros.insert("", "end", values=(m[1], m[2], m[3], edad_str, rol))

        scroll_m = tk.Scrollbar(tabla_frame, orient="vertical",
                                command=tree_miembros.yview)
        tree_miembros.configure(yscrollcommand=scroll_m.set)
        tree_miembros.pack(side="left", fill="both", expand=True)
        scroll_m.pack(side="right", fill="y")

        # ── BOTONES DE ACCIÓN ──
        btn_frame = tk.Frame(ventana, bg=COLORES["fondo_app"], pady=10)
        btn_frame.pack(fill="x", padx=10, pady=(5, 10))

        def desvincular():
            """Quita al miembro seleccionado de la familia (sin eliminarlo del censo)."""
            sel = tree_miembros.selection()
            if not sel:
                messagebox.showwarning("Sin selección", "Seleccione un miembro.")
                return
            vals = tree_miembros.item(sel[0])["values"]
            cedula = vals[2]
            if not messagebox.askyesno("Confirmar",
                                        f"¿Desvincular a {vals[0]} {vals[1]} de esta familia?\n"
                                        "El habitante NO será eliminado del censo."):
                return
            conn2 = obtener_conexion()
            cur2 = conn2.cursor()

            # Si este miembro es el jefe, quitar la referencia
            cur2.execute("SELECT id FROM habitantes WHERE cedula=?", (cedula,))
            hab = cur2.fetchone()
            if hab:
                cur2.execute("UPDATE familias SET jefe_familia_id=NULL WHERE jefe_familia_id=? AND id=?",
                             (hab[0], fam_id))

            cur2.execute("UPDATE habitantes SET familia_id=NULL WHERE cedula=?", (cedula,))
            conn2.commit()
            conn2.close()
            tree_miembros.delete(sel[0])
            self._cargar_familias()
            messagebox.showinfo("Éxito", "Miembro desvinculado de la familia.")

        def asignar_jefe():
            """Asigna o cambia el jefe de familia al miembro seleccionado."""
            sel = tree_miembros.selection()
            if not sel:
                messagebox.showwarning("Sin selección",
                                       "Seleccione un miembro para asignarlo como jefe de familia.")
                return

            vals = tree_miembros.item(sel[0])["values"]
            cedula_seleccionado = vals[2]
            nombre_seleccionado = f"{vals[0]} {vals[1]}"

            conn2 = obtener_conexion()
            cur2 = conn2.cursor()
            cur2.execute("SELECT id FROM habitantes WHERE cedula=?", (cedula_seleccionado,))
            hab = cur2.fetchone()
            if not hab:
                conn2.close()
                messagebox.showerror("Error", "No se encontró al habitante en la base de datos.")
                return
            nuevo_jefe_id = hab[0]

            cur2.execute("SELECT jefe_familia_id FROM familias WHERE id=?", (fam_id,))
            familia_data = cur2.fetchone()
            jefe_actual_id = familia_data[0] if familia_data else None

            if jefe_actual_id == nuevo_jefe_id:
                conn2.close()
                messagebox.showinfo("Información",
                                    f"{nombre_seleccionado} ya es el jefe de esta familia.")
                return

            if jefe_actual_id:
                cur2.execute("SELECT nombres, apellidos FROM habitantes WHERE id=?",
                             (jefe_actual_id,))
                jefe_actual_info = cur2.fetchone()
                nombre_jefe_actual = f"{jefe_actual_info[0]} {jefe_actual_info[1]}" if jefe_actual_info else "Desconocido"

                if not messagebox.askyesno("Cambiar Jefe de Familia",
                                           f"El jefe actual es: {nombre_jefe_actual}\n\n"
                                           f"¿Desea reemplazarlo por {nombre_seleccionado}?\n\n"
                                           "El jefe anterior seguirá como miembro de la familia."):
                    conn2.close()
                    return

            cur2.execute("UPDATE familias SET jefe_familia_id=? WHERE id=?",
                         (nuevo_jefe_id, fam_id))
            conn2.commit()
            conn2.close()

            # Actualizar tabla visual
            for item_id in tree_miembros.get_children():
                item_vals = list(tree_miembros.item(item_id)["values"])
                if str(item_vals[2]) == str(cedula_seleccionado):
                    item_vals[4] = "JEFE"
                else:
                    item_vals[4] = "Miembro"
                tree_miembros.item(item_id, values=item_vals)

            self._cargar_familias()

            if jefe_actual_id:
                messagebox.showinfo("Jefe Actualizado",
                                    f"{nombre_seleccionado} es ahora el nuevo jefe de familia.")
            else:
                messagebox.showinfo("Jefe Asignado",
                                    f"{nombre_seleccionado} ha sido asignado como jefe de familia.")

        def quitar_jefe():
            """Quita el rol de jefe al miembro seleccionado (sigue como miembro normal)."""
            sel = tree_miembros.selection()
            if not sel:
                messagebox.showwarning("Sin selección",
                                       "Seleccione al miembro que es jefe de familia para quitarle el rol.")
                return

            vals = tree_miembros.item(sel[0])["values"]
            cedula_seleccionado = vals[2]
            nombre_seleccionado = f"{vals[0]} {vals[1]}"

            conn2 = obtener_conexion()
            cur2 = conn2.cursor()

            # Verificar si la familia tiene un jefe asignado
            cur2.execute("SELECT jefe_familia_id FROM familias WHERE id=?", (fam_id,))
            familia_data = cur2.fetchone()
            jefe_actual_id = familia_data[0] if familia_data else None

            if jefe_actual_id is None:
                conn2.close()
                messagebox.showinfo("Sin jefe asignado",
                                    "Esta familia actualmente no tiene un jefe de familia asignado.")
                return

            # Obtener el ID del miembro seleccionado
            cur2.execute("SELECT id FROM habitantes WHERE cedula=?", (cedula_seleccionado,))
            hab = cur2.fetchone()
            if not hab:
                conn2.close()
                messagebox.showerror("Error", "No se encontró al habitante en la base de datos.")
                return

            id_seleccionado = hab[0]

            # Verificar que el seleccionado sea el jefe
            if id_seleccionado != jefe_actual_id:
                conn2.close()
                messagebox.showinfo("No es jefe",
                                    f"{nombre_seleccionado} no es el jefe de esta familia.\n"
                                    "Solo se puede quitar el rol de jefe al miembro que\n"
                                    "actualmente tiene ese rol asignado.")
                return

            # Pedir confirmación
            if not messagebox.askyesno("Confirmar quitar rol de jefe",
                                       f"¿Está seguro de que desea quitar el rol de jefe de familia "
                                       f"a {nombre_seleccionado}?\n\n"
                                       f"• Pasará a ser un miembro normal de la familia.\n"
                                       f"• NO será eliminado/a ni desvinculado/a de la familia.\n"
                                       f"• La familia quedará sin jefe asignado."):
                conn2.close()
                return

            # Actualizar la BD
            cur2.execute("UPDATE familias SET jefe_familia_id = NULL WHERE id = ?", (fam_id,))
            conn2.commit()
            conn2.close()

            # Actualizar la tabla visual
            for item_id in tree_miembros.get_children():
                item_vals = list(tree_miembros.item(item_id)["values"])
                if str(item_vals[2]) == str(cedula_seleccionado):
                    item_vals[4] = "Miembro"
                tree_miembros.item(item_id, values=item_vals)

            self._cargar_familias()
            messagebox.showinfo("Rol de jefe removido",
                                f"Se ha quitado el rol de jefe de familia a {nombre_seleccionado}.\n\n"
                                f"La familia '{fam_nombre}' actualmente no tiene jefe asignado.\n"
                                f"Puede asignar un nuevo jefe usando el botón '👑 Asignar/Cambiar Jefe'.")

        # Botones
        tk.Button(btn_frame, text="🔓 Desvincular Miembro", font=FUENTE_SMALL,
                  bg=COLORES["acento"], fg=COLORES["blanco"],
                  relief="flat", cursor="hand2", command=desvincular,
                  bd=0, padx=15, pady=8).pack(side="left", padx=5)

        tk.Button(btn_frame, text="👑 Asignar/Cambiar Jefe", font=FUENTE_SMALL,
                  bg=COLORES["naranja"], fg=COLORES["blanco"],
                  relief="flat", cursor="hand2", command=asignar_jefe,
                  bd=0, padx=15, pady=8).pack(side="left", padx=5)

        tk.Button(btn_frame, text="❌ Quitar Rol de Jefe", font=FUENTE_SMALL,
                  bg=COLORES["rojo_vzla"], fg=COLORES["blanco"],
                  relief="flat", cursor="hand2", command=quitar_jefe,
                  bd=0, padx=15, pady=8).pack(side="left", padx=5)

    # ────────────────────────────────────────────────────────
    # PESTAÑA 4: ESTADÍSTICAS
    # ────────────────────────────────────────────────────────

    def _crear_tab_estadisticas(self):
        """
        [MÉTODO: CREAR PESTAÑA DE ESTADÍSTICAS]
        
        ¿Qué hace?
        → Crea 8 tarjetas de contadores y un Canvas para gráficos de barras.
        """
        stats_frame = tk.Frame(self.tab_stats, bg=COLORES["fondo_app"])
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)

        contadores_frame = tk.Frame(stats_frame, bg=COLORES["fondo_app"])
        contadores_frame.pack(fill="x", pady=(0, 10))

        self.stats_cards = {}
        
        cards_data = [
            ("total", "👥 Total Hab.", COLORES["azul_vzla"]),
            ("masculino", "👨 Masculino", COLORES["azul_oscuro"]),
            ("femenino", "👩 Femenino", COLORES["acento"]),
            ("ninos", "👶 Niños (0-11)", COLORES["verde"]),
            ("jovenes", "🧑 Jóvenes (12-17)", COLORES["naranja"]),
            ("adultos", "🧔 Adultos (18-59)", COLORES["rojo_vzla"]),
            ("mayores", "👴 Ad. Mayores (60+)", COLORES["fondo_card"]),
            ("familias", "👨‍👩‍👧 Familias", COLORES["azul_vzla"]),
        ]

        for key, texto, color in cards_data:
            card = tk.Frame(contadores_frame, bg=color, padx=10, pady=6,
                            highlightbackground=COLORES["amarillo_vzla"],
                            highlightthickness=1)
            card.pack(side="left", expand=True, fill="x", padx=2)
            tk.Label(card, text=texto, font=("Segoe UI", 9),
                     fg=COLORES["blanco"], bg=color).pack()
            lbl_num = tk.Label(card, text="0", font=("Segoe UI", 20, "bold"),
                               fg=COLORES["amarillo_vzla"], bg=color)
            lbl_num.pack()
            self.stats_cards[key] = lbl_num

        graficos_frame = tk.Frame(stats_frame, bg=COLORES["fondo_panel"],
                                  highlightbackground=COLORES["azul_vzla"],
                                  highlightthickness=1)
        graficos_frame.pack(fill="both", expand=True)

        tk.Label(graficos_frame, text="📊 DISTRIBUCIÓN ESTADÍSTICA",
                 font=FUENTE_SUBTITULO, fg=COLORES["amarillo_vzla"],
                 bg=COLORES["fondo_panel"]).pack(pady=10)

        self.canvas_stats = tk.Canvas(graficos_frame, bg=COLORES["fondo_panel"],
                                      highlightthickness=0)
        self.canvas_stats.pack(fill="both", expand=True, padx=20, pady=10)

        btn_refresh = tk.Button(stats_frame, text="🔄 Actualizar Estadísticas",
                                font=FUENTE_BOTON, bg=COLORES["rojo_vzla"],
                                fg=COLORES["blanco"], relief="flat", cursor="hand2",
                                command=self._actualizar_estadisticas, bd=0, padx=20, pady=8)
        btn_refresh.pack(pady=10)

    # ────────────────────────────────────────────────────────
    # PESTAÑA 5: IMPRIMIR / EXPORTAR
    # ────────────────────────────────────────────────────────

    def _crear_tab_imprimir(self):
        """
        [MÉTODO: CREAR PESTAÑA DE IMPRESIÓN]
        
        ¿Qué hace?
        → Crea opciones de impresión: Todos, Por Género, Por Edad, Individual, Familias.
        
        OPTIMIZACIÓN: Usa configurar_scroll_mousewheel() en vez de código duplicado.
        """
        canvas_imp = tk.Canvas(self.tab_imprimir, bg=COLORES["fondo_app"], highlightthickness=0)
        scrollbar_imp = tk.Scrollbar(self.tab_imprimir, orient="vertical",
                                     command=canvas_imp.yview)
        main = tk.Frame(canvas_imp, bg=COLORES["fondo_app"])

        main.bind("<Configure>",
                  lambda e: canvas_imp.configure(scrollregion=canvas_imp.bbox("all")))
        canvas_imp.create_window((0, 0), window=main, anchor="nw")
        canvas_imp.configure(yscrollcommand=scrollbar_imp.set)
        canvas_imp.pack(side="left", fill="both", expand=True)
        scrollbar_imp.pack(side="right", fill="y")

        # OPTIMIZACIÓN: Usa función global en vez de código duplicado
        configurar_scroll_mousewheel(canvas_imp)

        main.configure(padx=20, pady=20)

        titulo = tk.Frame(main, bg=COLORES["fondo_card"], padx=15, pady=10)
        titulo.pack(fill="x", pady=(0, 15))
        tk.Label(titulo, text="🖨️ OPCIONES DE IMPRESIÓN Y EXPORTACIÓN",
                 font=FUENTE_SUBTITULO, fg=COLORES["amarillo_vzla"],
                 bg=COLORES["fondo_card"]).pack(anchor="w")

        opciones = [
            ("📋 Imprimir TODOS los Habitantes",
             "Exporta la lista completa de todos los habitantes registrados",
             self._imprimir_todos),
            ("👫 Imprimir por Género",
             "Filtra y exporta por género (Masculino/Femenino)",
             self._imprimir_por_genero),
            ("📅 Imprimir por Rango de Edad",
             "Filtra por grupos etarios y genera planilla",
             self._imprimir_por_edad),
            ("👤 Imprimir Habitante Individual",
             "Imprime la ficha completa del habitante seleccionado",
             self._imprimir_individual),
            ("👨‍👩‍👧‍👦 Imprimir Familias",
             "Exporta la lista de todas las familias con sus miembros",
             self._imprimir_familias),
        ]

        for titulo_op, desc, comando in opciones:
            card = tk.Frame(main, bg=COLORES["fondo_panel"],
                            highlightbackground=COLORES["azul_vzla"],
                            highlightthickness=1, padx=20, pady=15)
            card.pack(fill="x", pady=5)

            tk.Label(card, text=titulo_op, font=FUENTE_SUBTITULO,
                     fg=COLORES["blanco"],
                     bg=COLORES["fondo_panel"]).pack(anchor="w")
            tk.Label(card, text=desc, font=FUENTE_SMALL,
                     fg=COLORES["gris_medio"],
                     bg=COLORES["fondo_panel"]).pack(anchor="w", pady=(2, 8))

            btn = tk.Button(card, text="📄 Generar Planilla", font=FUENTE_BOTON,
                            bg=COLORES["rojo_vzla"], fg=COLORES["blanco"],
                            relief="flat", cursor="hand2", command=comando,
                            bd=0, padx=20, pady=6)
            btn.pack(anchor="w")

        # ── BANDERA DECORATIVA AL FINAL ──
        bandera = tk.Frame(main, bg=COLORES["fondo_app"], pady=20)
        bandera.pack(fill="x")
        canvas_b = tk.Canvas(bandera, width=300, height=60, bg=COLORES["fondo_app"],
                             highlightthickness=0)
        canvas_b.pack()
        canvas_b.create_rectangle(0, 0, 300, 20, fill=COLORES["amarillo_vzla"], outline="")
        canvas_b.create_rectangle(0, 20, 300, 40, fill=COLORES["azul_vzla"], outline="")
        canvas_b.create_rectangle(0, 40, 300, 60, fill=COLORES["rojo_vzla"], outline="")
        for i in range(8):
            canvas_b.create_text(110 + i * 12, 30, text="★",
                                 fill=COLORES["blanco"], font=("Segoe UI", 7, "bold"))

    # ────────────────────────────────────────────────────────
    # OPERACIONES CRUD (Crear, Leer, Actualizar, Eliminar)
    # ────────────────────────────────────────────────────────

    def _obtener_valor_campo(self, campo):
        """
        [MÉTODO: OBTENER EL VALOR DE UN CAMPO DEL FORMULARIO]
        
        → Soporta Entry (texto), Combobox (desplegable) y Text (multilínea).
        """
        widget = self.campos[campo]
        if isinstance(widget, ttk.Combobox):
            return widget.get()
        elif isinstance(widget, tk.Text):
            return widget.get("1.0", "end-1c").strip()
        else:
            return widget.get().strip()

    def _set_valor_campo(self, campo, valor):
        """
        [MÉTODO: ESTABLECER EL VALOR DE UN CAMPO DEL FORMULARIO]
        
        → Primero limpia el contenido actual, luego inserta el nuevo valor.
        """
        widget = self.campos[campo]
        if isinstance(widget, ttk.Combobox):
            widget.set(valor)
        elif isinstance(widget, tk.Text):
            widget.delete("1.0", "end")
            widget.insert("1.0", valor)
        else:
            widget.delete(0, "end")
            widget.insert(0, valor)

    def _limpiar_formulario(self):
        """
        [MÉTODO: LIMPIAR TODOS LOS CAMPOS DEL FORMULARIO]
        
        → Vacía todos los campos y resetea el ID seleccionado.
        → Oculta los campos de extranjero.
        """
        for campo, widget in self.campos.items():
            if isinstance(widget, ttk.Combobox):
                widget.set("")
            elif isinstance(widget, tk.Text):
                widget.delete("1.0", "end")
            else:
                widget.delete(0, "end")
        self.habitante_id_seleccionado = None
        self.frame_extranjero.grid_remove()

    def _validar_campos(self):
        """
        [MÉTODO: VALIDAR QUE LOS CAMPOS OBLIGATORIOS ESTÉN LLENOS]
        
        → Verifica campos obligatorios, formato de fecha, email y datos de extranjero.
        → Retorna True si todo es válido, False si hay errores.
        """
        campos_obligatorios = {
            "nombres": "Nombres", "apellidos": "Apellidos",
            "cedula": "Cédula", "fecha_nac": "Fecha de Nacimiento",
            "genero": "Género", "estado_civil": "Estado Civil",
            "direccion": "Dirección", "telefono": "Teléfono",
            "tipo_vivienda": "Tipo de Vivienda", "parroquia": "Parroquia",
        }

        for campo, nombre_campo in campos_obligatorios.items():
            valor = self._obtener_valor_campo(campo)
            if not valor:
                messagebox.showwarning("Campo requerido",
                                        f"El campo '{nombre_campo}' es obligatorio.")
                return False

        # Validar formato de fecha
        fecha = self._obtener_valor_campo("fecha_nac")
        edad = calcular_edad(fecha)
        if edad is None:
            messagebox.showwarning("Fecha inválida",
                                    "Formato de fecha incorrecto. Use DD/MM/AAAA.")
            return False

        # Validar formato de email (si se proporcionó)
        correo = self._obtener_valor_campo("correo")
        if correo and not validar_email(correo):
            messagebox.showwarning("Correo inválido",
                                    "El formato del correo electrónico no es válido.")
            return False

        # Si es extranjero, validar que se seleccionó país de origen
        nac = self._obtener_valor_campo("nacionalidad")
        if nac == "Extranjero/a":
            if not self._obtener_valor_campo("pais_origen"):
                messagebox.showwarning("Campo requerido",
                                        "Seleccione el país de origen del extranjero.")
                return False

        return True

    def _guardar_habitante(self):
        """
        [MÉTODO: GUARDAR UN NUEVO HABITANTE EN LA BASE DE DATOS]
        
        → Valida campos, recopila datos y ejecuta INSERT SQL.
        → Si la cédula ya existe, muestra error.
        """
        if not self._validar_campos():
            return

        datos = {campo: self._obtener_valor_campo(campo) for campo in self.campos}
        discapacidad = datos.get("discapacidad", "").strip()
        if not discapacidad:
            discapacidad = "Ninguna"

        nacionalidad = datos.get("nacionalidad", "Venezolano/a") or "Venezolano/a"

        conn = obtener_conexion()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO habitantes
                (nombres, apellidos, cedula, fecha_nacimiento, genero,
                 estado_civil, discapacidad, direccion, telefono, ocupacion,
                 correo, tipo_vivienda, parroquia, nacionalidad, pais_origen,
                 estado_origen, municipio_origen, nivel_educacion, tenencia_vivienda)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datos["nombres"], datos["apellidos"], datos["cedula"],
                datos["fecha_nac"], datos["genero"], datos["estado_civil"],
                discapacidad, datos["direccion"], datos["telefono"],
                datos["ocupacion"], datos["correo"], datos["tipo_vivienda"],
                datos["parroquia"], nacionalidad,
                datos.get("pais_origen", ""), datos.get("estado_origen", ""),
                datos.get("municipio_origen", ""), datos.get("nivel_educacion", ""),
                datos.get("tenencia_vivienda", "Propia")
            ))
            conn.commit()
            messagebox.showinfo("Éxito", "Habitante registrado correctamente.")
            self._limpiar_formulario()
            self._cargar_habitantes()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe un habitante con esa cédula.")
        finally:
            conn.close()

    def _actualizar_habitante(self):
        """
        [MÉTODO: ACTUALIZAR UN HABITANTE EXISTENTE]
        
        → Usa UPDATE en vez de INSERT.
        → Solo funciona si hay un habitante seleccionado para edición.
        """
        if self.habitante_id_seleccionado is None:
            messagebox.showwarning("Sin selección",
                                    "Seleccione un habitante desde la tabla para actualizar.")
            return

        if not self._validar_campos():
            return

        datos = {campo: self._obtener_valor_campo(campo) for campo in self.campos}
        discapacidad = datos.get("discapacidad", "").strip() or "Ninguna"
        nacionalidad = datos.get("nacionalidad", "Venezolano/a") or "Venezolano/a"

        conn = obtener_conexion()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE habitantes SET
                    nombres=?, apellidos=?, cedula=?, fecha_nacimiento=?,
                    genero=?, estado_civil=?, discapacidad=?, direccion=?,
                    telefono=?, ocupacion=?, correo=?, tipo_vivienda=?, parroquia=?,
                    nacionalidad=?, pais_origen=?, estado_origen=?, municipio_origen=?,
                    nivel_educacion=?, tenencia_vivienda=?
                WHERE id=?
            """, (
                datos["nombres"], datos["apellidos"], datos["cedula"],
                datos["fecha_nac"], datos["genero"], datos["estado_civil"],
                discapacidad, datos["direccion"], datos["telefono"],
                datos["ocupacion"], datos["correo"], datos["tipo_vivienda"],
                datos["parroquia"], nacionalidad,
                datos.get("pais_origen", ""), datos.get("estado_origen", ""),
                datos.get("municipio_origen", ""), datos.get("nivel_educacion", ""),
                datos.get("tenencia_vivienda", "Propia"),
                self.habitante_id_seleccionado
            ))
            conn.commit()
            messagebox.showinfo("Éxito", "Habitante actualizado correctamente.")
            self._limpiar_formulario()
            self._cargar_habitantes()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ya existe otro habitante con esa cédula.")
        finally:
            conn.close()

    def _eliminar_habitante(self):
        """
        [MÉTODO: ELIMINAR UN HABITANTE DE LA BASE DE DATOS]
        
        → Pide confirmación y ejecuta DELETE.
        """
        if self.habitante_id_seleccionado is None:
            messagebox.showwarning("Sin selección",
                                    "Seleccione un habitante desde la tabla para eliminar.")
            return

        if not messagebox.askyesno("Confirmar",
                                    "¿Está seguro de eliminar este registro?"):
            return

        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("DELETE FROM habitantes WHERE id=?",
                    (self.habitante_id_seleccionado,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
        self._limpiar_formulario()
        self._cargar_habitantes()

    # ────────────────────────────────────────────────────────
    # CARGA DE DATOS Y FILTROS
    # ────────────────────────────────────────────────────────

    def _cargar_habitantes(self, datos=None):
        """
        [MÉTODO: CARGAR HABITANTES EN LA TABLA VISUAL]
        
        ¿Qué hace?
        → Limpia la tabla, consulta la BD si no se pasan datos, inserta filas.
        → Actualiza el contador y las estadísticas.
        
        OPTIMIZACIÓN:
        → Se eliminó la variable "count" innecesaria (se usa len(datos)).
        → Se eliminó la recarga de familias (era innecesaria al buscar/filtrar).
        """
        for item in self.tree_habitantes.get_children():
            self.tree_habitantes.delete(item)

        if datos is None:
            conn = obtener_conexion()
            cur = conn.cursor()
            cur.execute("SELECT * FROM habitantes ORDER BY id DESC")
            datos = cur.fetchall()
            conn.close()

        for row in datos:
            edad = calcular_edad(row[4])
            edad_str = str(edad) if edad is not None else "?"
            nac = row[15] if len(row) > 15 and row[15] else "Venezolano/a"
            
            self.tree_habitantes.insert("", "end", values=(
                row[0], row[1], row[2], row[3],
                edad_str, row[5], row[13], row[9],
                row[12], nac
            ))

        # OPTIMIZACIÓN: Usa len(datos) en vez de variable count innecesaria
        self.lbl_contador.config(text=f"Total: {len(datos)} habitantes")
        self._actualizar_estadisticas()
        # OPTIMIZACIÓN: Se eliminó la recarga innecesaria de familias aquí

    def _buscar_habitantes(self):
        """
        [MÉTODO: BUSCAR HABITANTES EN TIEMPO REAL]
        
        → Busca por nombres, apellidos, cédula o parroquia usando LIKE.
        """
        texto = self.entry_busqueda.get().strip().lower()
        conn = obtener_conexion()
        cur = conn.cursor()

        if texto:
            cur.execute("""
                SELECT * FROM habitantes
                WHERE LOWER(nombres) LIKE ? OR LOWER(apellidos) LIKE ?
                OR cedula LIKE ? OR LOWER(parroquia) LIKE ?
                ORDER BY id DESC
            """, (f"%{texto}%", f"%{texto}%", f"%{texto}%", f"%{texto}%"))
        else:
            cur.execute("SELECT * FROM habitantes ORDER BY id DESC")

        datos = cur.fetchall()
        conn.close()
        self._cargar_habitantes(datos)

    def _aplicar_filtros(self):
        """
        [MÉTODO: FILTRAR HABITANTES POR GÉNERO Y/O RANGO DE EDAD]
        """
        genero = self.filtro_genero.get()
        rango = self.filtro_edad.get()

        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT * FROM habitantes ORDER BY id DESC")
        todos = cur.fetchall()
        conn.close()

        filtrados = []
        for row in todos:
            if genero != "Todos" and row[5] != genero:
                continue
            
            if rango != "Todos":
                edad = calcular_edad(row[4])
                if edad is None:
                    continue
                rango_min, rango_max = RANGOS_EDAD[rango]
                if not (rango_min <= edad <= rango_max):
                    continue
            
            filtrados.append(row)

        self._cargar_habitantes(filtrados)

    # ────────────────────────────────────────────────────────
    # VER DETALLE DE UN HABITANTE
    # ────────────────────────────────────────────────────────

    def _ver_detalle_habitante(self):
        """
        [MÉTODO: MOSTRAR VENTANA CON TODOS LOS DATOS DE UN HABITANTE]
        """
        seleccion = self.tree_habitantes.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un habitante de la tabla.")
            return

        item = self.tree_habitantes.item(seleccion[0])
        hab_id = item["values"][0]

        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT * FROM habitantes WHERE id=?", (hab_id,))
        hab = cur.fetchone()
        conn.close()

        if not hab:
            return

        edad = calcular_edad(hab[4])
        grupo = clasificar_edad(edad)

        detalle = tk.Toplevel(self.root)
        detalle.title(f"Detalle — {hab[1]} {hab[2]}")
        detalle.geometry("600x750")
        detalle.configure(bg=COLORES["fondo_app"])

        hdr = tk.Frame(detalle, bg=COLORES["rojo_vzla"], height=40)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"👤 {hab[1]} {hab[2]}",
                 font=FUENTE_SUBTITULO, fg=COLORES["blanco"],
                 bg=COLORES["rojo_vzla"]).pack(expand=True)
        tk.Frame(detalle, bg=COLORES["amarillo_vzla"], height=3).pack(fill="x")

        canvas_det = tk.Canvas(detalle, bg=COLORES["fondo_app"], highlightthickness=0)
        scrollbar_det = tk.Scrollbar(detalle, orient="vertical", command=canvas_det.yview)
        info_frame = tk.Frame(canvas_det, bg=COLORES["fondo_panel"], padx=25, pady=20)
        info_frame.bind("<Configure>",
                        lambda e: canvas_det.configure(scrollregion=canvas_det.bbox("all")))
        canvas_det.create_window((0, 0), window=info_frame, anchor="nw")
        canvas_det.configure(yscrollcommand=scrollbar_det.set)
        canvas_det.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        scrollbar_det.pack(side="right", fill="y")

        nac = hab[15] if len(hab) > 15 and hab[15] else "Venezolano/a"
        pais_origen = hab[16] if len(hab) > 16 and hab[16] else ""
        estado_origen = hab[17] if len(hab) > 17 and hab[17] else ""
        municipio_origen = hab[18] if len(hab) > 18 and hab[18] else ""
        nivel_edu = hab[19] if len(hab) > 19 and hab[19] else ""
        tenencia = hab[20] if len(hab) > 20 and hab[20] else ""

        campos_detalle = [
            ("━━━ DATOS PERSONALES ━━━", ""),
            ("Nombres", hab[1]), ("Apellidos", hab[2]),
            ("Cédula", hab[3]), ("Fecha de Nacimiento", hab[4]),
            ("Edad", f"{edad} años ({grupo})"),
            ("Género", hab[5]), ("Estado Civil", hab[6]),
            ("Discapacidad", hab[7]), ("Teléfono", hab[9]),
            ("Correo Electrónico", hab[11]), ("Nacionalidad", nac),
        ]

        if nac == "Extranjero/a":
            campos_detalle.extend([
                ("País de Origen", pais_origen),
                ("Estado/Provincia de Origen", estado_origen),
                ("Municipio/Ciudad de Origen", municipio_origen),
            ])

        campos_detalle.extend([
            ("━━━ DATOS SOCIOECONÓMICOS ━━━", ""),
            ("Ocupación", hab[10]), ("Nivel de Educación", nivel_edu),
            ("━━━ DATOS DE VIVIENDA Y HOGAR ━━━", ""),
            ("Tipo de Vivienda", hab[12]), ("Tenencia de Vivienda", tenencia),
            ("Dirección", hab[8]), ("Parroquia", hab[13]),
            ("Estado", "Táchira"), ("Municipio", "Junín"),
        ])

        for i, (label, valor) in enumerate(campos_detalle):
            if label.startswith("━━━"):
                tk.Label(info_frame, text=label,
                         font=FUENTE_SECCION,
                         fg=COLORES["amarillo_vzla"],
                         bg=COLORES["fondo_panel"]).grid(row=i, column=0,
                                                          columnspan=2, sticky="w",
                                                          pady=(10, 5), padx=5)
            else:
                tk.Label(info_frame, text=f"{label}:",
                         font=("Segoe UI", 10, "bold"),
                         fg=COLORES["amarillo_vzla"],
                         bg=COLORES["fondo_panel"],
                         anchor="w").grid(row=i, column=0, sticky="w", pady=3, padx=5)
                tk.Label(info_frame, text=str(valor),
                         font=FUENTE_NORMAL,
                         fg=COLORES["texto_claro"],
                         bg=COLORES["fondo_panel"],
                         anchor="w").grid(row=i, column=1, sticky="w", pady=3, padx=15)

        btn_print = tk.Button(
            detalle, text="🖨️ Imprimir este registro",
            font=FUENTE_BOTON, bg=COLORES["rojo_vzla"],
            fg=COLORES["blanco"], relief="flat", cursor="hand2",
            command=lambda: self._exportar_individual(hab), bd=0, padx=20, pady=8
        )
        btn_print.pack(pady=10)

    def _editar_desde_tabla(self):
        """
        [MÉTODO: CARGAR DATOS DE UN HABITANTE EN EL FORMULARIO PARA EDITAR]
        
        OPTIMIZACIÓN: Se eliminó la doble asignación de habitante_id_seleccionado.
        Antes se asignaba en la línea 3364, luego _limpiar_formulario() la reseteaba
        a None, y se volvía a asignar en la línea 3396. Ahora solo se asigna una vez
        al final, después de limpiar el formulario.
        """
        seleccion = self.tree_habitantes.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un habitante de la tabla.")
            return

        item = self.tree_habitantes.item(seleccion[0])
        hab_id = item["values"][0]

        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT * FROM habitantes WHERE id=?", (hab_id,))
        hab = cur.fetchone()
        conn.close()

        if not hab:
            return

        # OPTIMIZACIÓN: Se eliminó la primera asignación que era sobrescrita por _limpiar_formulario()
        self._limpiar_formulario()

        # Cargar cada campo con los datos del habitante
        self._set_valor_campo("nombres", hab[1])
        self._set_valor_campo("apellidos", hab[2])
        self._set_valor_campo("cedula", hab[3])
        self._set_valor_campo("fecha_nac", hab[4])
        self._set_valor_campo("genero", hab[5])
        self._set_valor_campo("estado_civil", hab[6])
        self._set_valor_campo("discapacidad", hab[7] if hab[7] else "")
        self._set_valor_campo("direccion", hab[8])
        self._set_valor_campo("telefono", hab[9])
        self._set_valor_campo("ocupacion", hab[10] if hab[10] else "")
        self._set_valor_campo("correo", hab[11] if hab[11] else "")
        self._set_valor_campo("tipo_vivienda", hab[12])
        self._set_valor_campo("parroquia", hab[13])

        nac = hab[15] if len(hab) > 15 and hab[15] else "Venezolano/a"
        self._set_valor_campo("nacionalidad", nac)

        if nac == "Extranjero/a":
            self.frame_extranjero.grid()
            self._set_valor_campo("pais_origen", hab[16] if len(hab) > 16 and hab[16] else "")
            self._set_valor_campo("estado_origen", hab[17] if len(hab) > 17 and hab[17] else "")
            self._set_valor_campo("municipio_origen", hab[18] if len(hab) > 18 and hab[18] else "")

        self._set_valor_campo("nivel_educacion", hab[19] if len(hab) > 19 and hab[19] else "")
        self._set_valor_campo("tenencia_vivienda", hab[20] if len(hab) > 20 and hab[20] else "Propia")

        # OPTIMIZACIÓN: Única asignación del ID (después de limpiar el formulario)
        self.habitante_id_seleccionado = hab[0]
        self.notebook.select(0)

        messagebox.showinfo("Edición",
                            "Datos cargados en el formulario. Modifique y presione 'Actualizar'.")

    # ────────────────────────────────────────────────────────
    # ESTADÍSTICAS
    # ────────────────────────────────────────────────────────

    def _actualizar_estadisticas(self):
        """
        [MÉTODO: CALCULAR Y DIBUJAR ESTADÍSTICAS]
        
        → Cuenta totales por género y grupo etario.
        → Dibuja gráficos de barras en el Canvas.
        """
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT * FROM habitantes")
        todos = cur.fetchall()

        cur.execute("SELECT COUNT(*) FROM familias")
        total_familias = cur.fetchone()[0]
        conn.close()

        total = len(todos)
        masculino = sum(1 for r in todos if r[5] == "Masculino")
        femenino = sum(1 for r in todos if r[5] == "Femenino")

        edades = [calcular_edad(r[4]) for r in todos]
        edades = [e for e in edades if e is not None]

        ninos = sum(1 for e in edades if e <= 11)
        jovenes = sum(1 for e in edades if 12 <= e <= 17)
        adultos = sum(1 for e in edades if 18 <= e <= 59)
        mayores = sum(1 for e in edades if e >= 60)

        self.stats_cards["total"].config(text=str(total))
        self.stats_cards["masculino"].config(text=str(masculino))
        self.stats_cards["femenino"].config(text=str(femenino))
        self.stats_cards["ninos"].config(text=str(ninos))
        self.stats_cards["jovenes"].config(text=str(jovenes))
        self.stats_cards["adultos"].config(text=str(adultos))
        self.stats_cards["mayores"].config(text=str(mayores))
        self.stats_cards["familias"].config(text=str(total_familias))

        # ── DIBUJAR GRÁFICOS DE BARRAS ──
        self.canvas_stats.delete("all")
        self.canvas_stats.update_idletasks()
        c_width = self.canvas_stats.winfo_width()
        c_height = self.canvas_stats.winfo_height()

        if c_width < 100 or c_height < 100:
            return

        # Gráfico izquierdo: DISTRIBUCIÓN POR GÉNERO
        self.canvas_stats.create_text(
            c_width // 4, 20, text="DISTRIBUCIÓN POR GÉNERO",
            fill=COLORES["amarillo_vzla"], font=("Segoe UI", 11, "bold")
        )

        max_val = max(masculino, femenino, 1)
        bar_max_h = c_height - 80

        bm_h = int((masculino / max_val) * bar_max_h) if max_val > 0 else 0
        x1, y1 = c_width // 4 - 50, c_height - 30 - bm_h
        x2, y2 = c_width // 4 - 10, c_height - 30
        self.canvas_stats.create_rectangle(x1, y1, x2, y2,
                                            fill=COLORES["azul_vzla"], outline="")
        self.canvas_stats.create_text((x1 + x2) // 2, y1 - 12, text=str(masculino),
                                      fill=COLORES["blanco"], font=FUENTE_SMALL)
        self.canvas_stats.create_text((x1 + x2) // 2, y2 + 12, text="Masc.",
                                      fill=COLORES["texto_claro"], font=FUENTE_SMALL)

        bf_h = int((femenino / max_val) * bar_max_h) if max_val > 0 else 0
        x1, y1 = c_width // 4 + 10, c_height - 30 - bf_h
        x2, y2 = c_width // 4 + 50, c_height - 30
        self.canvas_stats.create_rectangle(x1, y1, x2, y2,
                                            fill=COLORES["acento"], outline="")
        self.canvas_stats.create_text((x1 + x2) // 2, y1 - 12, text=str(femenino),
                                      fill=COLORES["blanco"], font=FUENTE_SMALL)
        self.canvas_stats.create_text((x1 + x2) // 2, y2 + 12, text="Fem.",
                                      fill=COLORES["texto_claro"], font=FUENTE_SMALL)

        # Gráfico derecho: DISTRIBUCIÓN POR EDAD
        self.canvas_stats.create_text(
            3 * c_width // 4, 20, text="DISTRIBUCIÓN POR EDAD",
            fill=COLORES["amarillo_vzla"], font=("Segoe UI", 11, "bold")
        )

        grupos = [
            ("Niños", ninos, COLORES["verde"]),
            ("Jóvenes", jovenes, COLORES["naranja"]),
            ("Adultos", adultos, COLORES["rojo_vzla"]),
            ("Mayores", mayores, COLORES["azul_vzla"]),
        ]

        max_val_edad = max((g[1] for g in grupos), default=1) or 1
        bar_w = 40
        spacing = 15
        total_w = len(grupos) * (bar_w + spacing) - spacing
        start_x = 3 * c_width // 4 - total_w // 2

        for i, (nombre, valor, color) in enumerate(grupos):
            bh = int((valor / max_val_edad) * bar_max_h) if max_val_edad > 0 else 0
            x1 = start_x + i * (bar_w + spacing)
            y1 = c_height - 30 - bh
            x2 = x1 + bar_w
            y2 = c_height - 30
            self.canvas_stats.create_rectangle(x1, y1, x2, y2,
                                                fill=color, outline="")
            self.canvas_stats.create_text((x1 + x2) // 2, y1 - 12, text=str(valor),
                                          fill=COLORES["blanco"], font=FUENTE_SMALL)
            self.canvas_stats.create_text((x1 + x2) // 2, y2 + 12, text=nombre,
                                          fill=COLORES["texto_claro"],
                                          font=("Segoe UI", 8))

    # ────────────────────────────────────────────────────────
    # IMPRESIÓN Y EXPORTACIÓN
    # ────────────────────────────────────────────────────────

    def _generar_html_base(self, titulo_reporte, contenido_body):
        """
        [MÉTODO: GENERAR LA PLANTILLA HTML BASE]
        
        → Crea documento HTML completo con estilos CSS, encabezado, contenido y pie.
        """
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{titulo_reporte}</title>
<style>
    @media print {{
        body {{ margin: 0; }}
        .no-print {{ display: none !important; }}
        .page-break {{ page-break-before: always; }}
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #1a1a2e;
        background: #fff;
        font-size: 11pt;
    }}
    .btn-imprimir {{
        position: fixed; top: 15px; right: 20px;
        background: #CF142B; color: white; border: none;
        padding: 12px 30px; font-size: 14pt; font-weight: bold;
        border-radius: 6px; cursor: pointer; z-index: 1000;
    }}
    .btn-imprimir:hover {{ background: #A01025; }}
    .encabezado {{
        text-align: center; padding: 20px 0 10px;
        border-bottom: 4px double #CF142B;
        margin-bottom: 5px;
    }}
    .franja {{ height: 6px; display: flex; }}
    .franja .amarillo {{ flex: 1; background: #FCDD09; }}
    .franja .azul {{ flex: 1; background: #00209F; }}
    .franja .rojo {{ flex: 1; background: #CF142B; }}
    .encabezado h1 {{ font-size: 18pt; color: #CF142B; margin: 8px 0 2px; letter-spacing: 2px; }}
    .encabezado h2 {{ font-size: 12pt; color: #00209F; font-weight: normal; }}
    .encabezado .republica {{ font-size: 9pt; color: #555; margin-top: 3px; }}
    .info-reporte {{
        display: flex; justify-content: space-between;
        padding: 8px 20px; background: #f5f5f5;
        border: 1px solid #ddd; margin: 10px 20px; font-size: 10pt;
    }}
    .tabla-censo {{
        width: calc(100% - 40px); margin: 10px 20px;
        border-collapse: collapse; font-size: 9pt;
    }}
    .tabla-censo th {{
        background: #CF142B; color: white;
        padding: 6px 4px; text-align: left;
        font-weight: bold; border: 1px solid #a01025; white-space: nowrap;
    }}
    .tabla-censo td {{ padding: 5px 4px; border: 1px solid #ccc; }}
    .tabla-censo tr:nth-child(even) {{ background: #f9f9f9; }}
    .tabla-censo tr:hover {{ background: #fff3cd; }}
    .ficha {{
        max-width: 700px; margin: 20px auto;
        border: 2px solid #CF142B; border-radius: 8px; overflow: hidden;
    }}
    .ficha-header {{
        background: linear-gradient(135deg, #CF142B, #A01025);
        color: white; text-align: center;
        padding: 15px; font-size: 14pt; font-weight: bold;
    }}
    .ficha-body {{ padding: 0; }}
    .ficha-seccion {{
        background: #00209F; color: #FCDD09; padding: 8px 15px;
        font-weight: bold; font-size: 11pt;
    }}
    .ficha-row {{ display: flex; border-bottom: 1px solid #e0e0e0; }}
    .ficha-row:last-child {{ border-bottom: none; }}
    .ficha-label {{
        width: 200px; min-width: 200px;
        background: #16213E; color: #FCDD09;
        padding: 10px 15px; font-weight: bold; font-size: 10pt;
    }}
    .ficha-valor {{ flex: 1; padding: 10px 15px; font-size: 10pt; background: #fff; }}
    .ficha-row:nth-child(even) .ficha-valor {{ background: #f7f9fc; }}
    .pie-pagina {{
        text-align: center; padding: 10px; font-size: 8pt; color: #888;
        border-top: 2px solid #CF142B; margin-top: 15px;
    }}
    .resumen {{
        margin: 10px 20px; padding: 8px 15px;
        background: #16213E; color: white;
        border-radius: 4px; font-weight: bold; font-size: 10pt;
    }}
    .familia-card {{
        max-width: 800px; margin: 15px auto;
        border: 2px solid #00209F; border-radius: 8px; overflow: hidden;
    }}
    .familia-header {{
        background: linear-gradient(135deg, #00209F, #001A7A);
        color: white; padding: 12px 15px; font-size: 13pt; font-weight: bold;
    }}
    .familia-info {{
        background: #f5f5f5; padding: 10px 15px; font-size: 10pt;
        border-bottom: 1px solid #ddd;
    }}
    .miembros-tabla {{
        width: 100%; border-collapse: collapse; font-size: 9pt;
    }}
    .miembros-tabla th {{
        background: #CF142B; color: white; padding: 5px 8px;
        text-align: left; border: 1px solid #a01025;
    }}
    .miembros-tabla td {{ padding: 5px 8px; border: 1px solid #ddd; }}
    .miembros-tabla tr:nth-child(even) {{ background: #f9f9f9; }}
</style>
</head>
<body>
<button class="btn-imprimir no-print" onclick="window.print()">🖨️ IMPRIMIR</button>
<div class="franja"><div class="amarillo"></div><div class="azul"></div><div class="rojo"></div></div>
<div class="encabezado">
    <h1>🇻🇪 CENSO POBLACIONAL COMUNITARIO</h1>
    <h2>Municipio Junín — Estado Táchira</h2>
    <p class="republica">República Bolivariana de Venezuela</p>
</div>
<div class="info-reporte">
    <span><strong>Reporte:</strong> {titulo_reporte}</span>
    <span><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
</div>
{contenido_body}
<div class="pie-pagina">
    🇻🇪 Sistema de Censo Poblacional Comunitario — Municipio Junín, Estado Táchira<br>
    República Bolivariana de Venezuela — Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
</div>
</body>
</html>"""

    def _generar_tabla_html(self, datos):
        """
        [MÉTODO: GENERAR UNA TABLA HTML CON LOS DATOS DE HABITANTES]
        """
        encabezados = [
            "N°", "Nombres", "Apellidos", "Cédula", "F. Nacimiento",
            "Edad", "Grupo", "Género", "Edo. Civil", "Discapacidad",
            "Dirección", "Teléfono", "Ocupación", "Correo",
            "Vivienda", "Tenencia", "Parroquia", "Nacionalidad", "Educación"
        ]
        filas = ""
        for i, row in enumerate(datos, 1):
            edad = calcular_edad(row[4])
            grupo = clasificar_edad(edad)
            nac = row[15] if len(row) > 15 and row[15] else "Venezolano/a"
            tenencia = row[20] if len(row) > 20 and row[20] else ""
            nivel_edu = row[19] if len(row) > 19 and row[19] else ""
            filas += f"""<tr>
                <td>{i}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td>
                <td>{row[4]}</td><td>{edad}</td><td>{grupo}</td><td>{row[5]}</td>
                <td>{row[6]}</td><td>{row[7]}</td><td>{row[8]}</td><td>{row[9]}</td>
                <td>{row[10]}</td><td>{row[11]}</td><td>{row[12]}</td><td>{tenencia}</td>
                <td>{row[13]}</td><td>{nac}</td><td>{nivel_edu}</td>
            </tr>"""

        resumen = f'<div class="resumen">Total de habitantes: {len(datos)}</div>'
        tabla = f"""
{resumen}
<table class="tabla-censo">
<thead><tr>{"".join(f'<th>{h}</th>' for h in encabezados)}</tr></thead>
<tbody>{filas}</tbody>
</table>"""
        return tabla

    def _generar_ficha_html(self, hab):
        """
        [MÉTODO: GENERAR FICHA HTML INDIVIDUAL DE UN HABITANTE]
        """
        edad = calcular_edad(hab[4])
        grupo = clasificar_edad(edad)
        nac = hab[15] if len(hab) > 15 and hab[15] else "Venezolano/a"
        pais_origen = hab[16] if len(hab) > 16 and hab[16] else ""
        estado_origen = hab[17] if len(hab) > 17 and hab[17] else ""
        municipio_origen = hab[18] if len(hab) > 18 and hab[18] else ""
        nivel_edu = hab[19] if len(hab) > 19 and hab[19] else ""
        tenencia = hab[20] if len(hab) > 20 and hab[20] else ""

        filas = ""

        filas += '<div class="ficha-seccion">👤 DATOS PERSONALES</div>'
        campos_personales = [
            ("Nombres", hab[1]), ("Apellidos", hab[2]),
            ("Cédula de Identidad", hab[3]), ("Fecha de Nacimiento", hab[4]),
            ("Edad", f"{edad} años"), ("Grupo Etario", grupo),
            ("Género", hab[5]), ("Estado Civil", hab[6]),
            ("Discapacidad", hab[7]), ("Teléfono", hab[9]),
            ("Correo Electrónico", hab[11]), ("Nacionalidad", nac),
        ]
        if nac == "Extranjero/a":
            campos_personales.extend([
                ("País de Origen", pais_origen),
                ("Estado/Provincia de Origen", estado_origen),
                ("Municipio/Ciudad de Origen", municipio_origen),
            ])
        for label, valor in campos_personales:
            filas += (f'<div class="ficha-row"><div class="ficha-label">{label}</div>'
                      f'<div class="ficha-valor">{valor}</div></div>')

        filas += '<div class="ficha-seccion">💼 DATOS SOCIOECONÓMICOS</div>'
        for label, valor in [("Ocupación", hab[10]), ("Nivel de Educación", nivel_edu)]:
            filas += (f'<div class="ficha-row"><div class="ficha-label">{label}</div>'
                      f'<div class="ficha-valor">{valor}</div></div>')

        filas += '<div class="ficha-seccion">🏠 DATOS DE VIVIENDA Y HOGAR</div>'
        for label, valor in [
            ("Tipo de Vivienda", hab[12]), ("Tenencia de Vivienda", tenencia),
            ("Dirección", hab[8]), ("Parroquia", hab[13]),
            ("Estado", "Táchira"), ("Municipio", "Junín"),
        ]:
            filas += (f'<div class="ficha-row"><div class="ficha-label">{label}</div>'
                      f'<div class="ficha-valor">{valor}</div></div>')

        return f"""
<div class="ficha">
    <div class="ficha-header">FICHA INDIVIDUAL DEL HABITANTE</div>
    <div class="ficha-body">{filas}</div>
</div>"""

    def _abrir_planilla(self, titulo, contenido):
        """
        [MÉTODO: GENERAR Y ABRIR PLANILLA HTML EN EL NAVEGADOR]
        
        → Genera HTML, lo guarda como archivo temporal y lo abre en el navegador.
        """
        html = self._generar_html_base(titulo, contenido)
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False,
                                          encoding='utf-8') as f:
            f.write(html)
            ruta = f.name
        webbrowser.open(f'file://{os.path.abspath(ruta)}')
        messagebox.showinfo("Planilla generada",
                            "La planilla se abrió en su navegador.\n"
                            "Use el botón 'IMPRIMIR' o Ctrl+P para imprimir.")

    # OPTIMIZACIÓN: Se eliminó el método _exportar_csv() que era un wrapper
    # innecesario con nombre engañoso (generaba HTML, no CSV).
    # Ahora _imprimir_todos() llama directamente a los métodos reales.

    def _imprimir_todos(self):
        """[MÉTODO: IMPRIMIR TODOS LOS HABITANTES] → Genera planilla con la lista completa."""
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT * FROM habitantes ORDER BY apellidos, nombres")
        datos = cur.fetchall()
        conn.close()
        if not datos:
            messagebox.showinfo("Sin datos", "No hay datos para exportar.")
            return
        # OPTIMIZACIÓN: Llamada directa en vez de pasar por _exportar_csv()
        contenido = self._generar_tabla_html(datos)
        self._abrir_planilla("Censo Completo", contenido)

    def _imprimir_por_genero(self):
        """
        [MÉTODO: IMPRIMIR HABITANTES FILTRADOS POR GÉNERO]
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Seleccionar Género")
        ventana.geometry("300x180")
        ventana.configure(bg=COLORES["fondo_app"])
        ventana.resizable(False, False)

        tk.Label(ventana, text="Seleccione el género:", font=FUENTE_NORMAL,
                 fg=COLORES["texto_claro"], bg=COLORES["fondo_app"]).pack(pady=15)
        combo = ttk.Combobox(ventana, values=GENEROS, state="readonly",
                             font=FUENTE_NORMAL, width=15)
        combo.pack(pady=5)

        def exportar():
            genero = combo.get()
            if not genero:
                messagebox.showwarning("Selección", "Seleccione un género.")
                return
            conn = obtener_conexion()
            cur = conn.cursor()
            cur.execute("SELECT * FROM habitantes WHERE genero=? ORDER BY apellidos",
                        (genero,))
            datos = cur.fetchall()
            conn.close()
            ventana.destroy()
            contenido = self._generar_tabla_html(datos)
            self._abrir_planilla(f"Habitantes - Género {genero}", contenido)

        tk.Button(ventana, text="Generar Planilla", font=FUENTE_BOTON,
                  bg=COLORES["rojo_vzla"], fg=COLORES["blanco"],
                  relief="flat", command=exportar, bd=0, padx=20, pady=6).pack(pady=15)

    def _imprimir_por_edad(self):
        """
        [MÉTODO: IMPRIMIR HABITANTES FILTRADOS POR RANGO DE EDAD]
        
        OPTIMIZACIÓN: Se corrigió el doble cálculo de calcular_edad().
        Antes se llamaba dos veces por cada habitante en el list comprehension.
        Ahora se calcula una sola vez y se reutiliza.
        """
        ventana = tk.Toplevel(self.root)
        ventana.title("Seleccionar Rango de Edad")
        ventana.geometry("350x180")
        ventana.configure(bg=COLORES["fondo_app"])
        ventana.resizable(False, False)

        tk.Label(ventana, text="Seleccione el rango de edad:", font=FUENTE_NORMAL,
                 fg=COLORES["texto_claro"], bg=COLORES["fondo_app"]).pack(pady=15)
        combo = ttk.Combobox(ventana, values=list(RANGOS_EDAD.keys()),
                             state="readonly", font=FUENTE_NORMAL, width=22)
        combo.pack(pady=5)

        def exportar():
            rango = combo.get()
            if not rango:
                messagebox.showwarning("Selección", "Seleccione un rango.")
                return
            rango_min, rango_max = RANGOS_EDAD[rango]
            conn = obtener_conexion()
            cur = conn.cursor()
            cur.execute("SELECT * FROM habitantes")
            todos = cur.fetchall()
            conn.close()
            # OPTIMIZACIÓN: Se calcula edad una sola vez por habitante
            filtrados = []
            for r in todos:
                edad = calcular_edad(r[4])
                if edad is not None and rango_min <= edad <= rango_max:
                    filtrados.append(r)
            ventana.destroy()
            contenido = self._generar_tabla_html(filtrados)
            self._abrir_planilla(f"Habitantes - {rango}", contenido)

        tk.Button(ventana, text="Generar Planilla", font=FUENTE_BOTON,
                  bg=COLORES["rojo_vzla"], fg=COLORES["blanco"],
                  relief="flat", command=exportar, bd=0, padx=20, pady=6).pack(pady=15)

    def _imprimir_individual(self):
        """
        [MÉTODO: IMPRIMIR FICHA INDIVIDUAL]
        """
        seleccion = self.tree_habitantes.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección",
                                    "Seleccione un habitante en la pestaña 'Habitantes'.")
            self.notebook.select(1)
            return

        item = self.tree_habitantes.item(seleccion[0])
        hab_id = item["values"][0]

        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT * FROM habitantes WHERE id=?", (hab_id,))
        hab = cur.fetchone()
        conn.close()

        if hab:
            self._exportar_individual(hab)

    def _exportar_individual(self, hab):
        """[MÉTODO: GENERAR Y ABRIR FICHA INDIVIDUAL]"""
        contenido = self._generar_ficha_html(hab)
        self._abrir_planilla(f"Ficha Individual - {hab[1]} {hab[2]}", contenido)

    def _imprimir_familias(self):
        """
        [MÉTODO: IMPRIMIR LISTA DE TODAS LAS FAMILIAS CON SUS MIEMBROS]
        """
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT * FROM familias ORDER BY nombre_familia")
        familias = cur.fetchall()

        if not familias:
            messagebox.showinfo("Sin datos", "No hay familias registradas.")
            conn.close()
            return

        contenido = f'<div class="resumen">Total de familias: {len(familias)}</div>'

        for fam in familias:
            jefe_nombre = "Sin asignar"
            jefe_cedula = "-"
            if fam[2]:
                cur.execute("SELECT nombres, apellidos, cedula FROM habitantes WHERE id=?",
                            (fam[2],))
                jefe = cur.fetchone()
                if jefe:
                    jefe_nombre = f"{jefe[0]} {jefe[1]}"
                    jefe_cedula = jefe[2]

            cur.execute("""SELECT nombres, apellidos, cedula, fecha_nacimiento, genero
                          FROM habitantes WHERE familia_id=?
                          ORDER BY apellidos, nombres""", (fam[0],))
            miembros = cur.fetchall()

            miembros_html = ""
            for i, m in enumerate(miembros, 1):
                edad = calcular_edad(m[3])
                edad_str = str(edad) if edad is not None else "?"
                miembros_html += f"""<tr>
                    <td>{i}</td><td>{m[0]}</td><td>{m[1]}</td>
                    <td>{m[2]}</td><td>{edad_str}</td><td>{m[4]}</td>
                </tr>"""

            if not miembros_html:
                miembros_html = '<tr><td colspan="6" style="text-align:center;color:#888;">Sin miembros registrados</td></tr>'

            contenido += f"""
<div class="familia-card">
    <div class="familia-header">👨‍👩‍👧‍👦 Familia: {fam[1]}</div>
    <div class="familia-info">
        <strong>Jefe de Familia:</strong> {jefe_nombre} (C.I. {jefe_cedula})<br>
        <strong>Dirección:</strong> {fam[3]} | <strong>Parroquia:</strong> {fam[4]}<br>
        <strong>Total de miembros:</strong> {len(miembros)}
    </div>
    <table class="miembros-tabla">
        <thead><tr><th>N°</th><th>Nombres</th><th>Apellidos</th><th>Cédula</th><th>Edad</th><th>Género</th></tr></thead>
        <tbody>{miembros_html}</tbody>
    </table>
</div>"""

        conn.close()
        self._abrir_planilla("Listado de Familias", contenido)

    def _cerrar_sesion(self):
        """
        [MÉTODO: CERRAR SESIÓN Y VOLVER AL LOGIN]
        """
        if messagebox.askyesno("Cerrar sesión", "¿Desea cerrar la sesión?"):
            self.root.destroy()
            root_login = tk.Tk()
            VentanaLogin(root_login)
            root_login.mainloop()


# ════════════════════════════════════════════════════════════
# SECCIÓN 7: PUNTO DE ENTRADA DEL PROGRAMA
# ────────────────────────────────────────────────────────────
# Esta es la sección que se ejecuta cuando se inicia el programa.
#
# ¿Cómo funciona?
# 1. "if __name__ == '__main__':" verifica que el archivo se ejecute
#    directamente (no importado desde otro archivo).
# 2. inicializar_db() crea la base de datos si no existe.
# 3. tk.Tk() crea la ventana principal de tkinter.
# 4. VentanaLogin(root) crea e inicializa la pantalla de login.
# 5. root.mainloop() mantiene la ventana abierta esperando eventos.
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    inicializar_db()        # Paso 1: Crear/verificar la base de datos
    root = tk.Tk()          # Paso 2: Crear la ventana principal
    app = VentanaLogin(root) # Paso 3: Mostrar la pantalla de login
    root.mainloop()         # Paso 4: Iniciar el bucle de eventos (mantener abierto)
