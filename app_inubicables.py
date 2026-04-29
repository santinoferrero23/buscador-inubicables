#!/usr/bin/env python3
"""
BUSCADOR DE CONTACTOS PARA INUBICABLES
Uso: streamlit run app_inubicables.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io
from pathlib import Path

import auth

SERVER_CRUCE_PATH = Path(__file__).parent.parent / "uploads" / "B - DETALLE DE TODOS LOS OBJETOS.xlsx"
BASES_DIR = Path(__file__).parent / "bases"


def listar_bases() -> list[Path]:
    """Devuelve los archivos Excel dentro de la carpeta bases/, ordenados por nombre."""
    if not BASES_DIR.exists():
        return []
    return sorted(
        [p for p in BASES_DIR.iterdir() if p.suffix.lower() in ('.xlsx', '.xls')],
        key=lambda p: p.name.lower()
    )

st.set_page_config(
    page_title="Inubicables | Procuraduría Fiscal",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "Buscador de Inubicables — Procuraduría Fiscal\nUso interno",
    },
)

# ── Login obligatorio ──
usuario_actual = auth.require_login()

CSS = """
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, sans-serif;
}

/* ── ESCONDER CHROME DE STREAMLIT ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 1rem !important; }

/* ── BLOQUE DE USUARIO EN SIDEBAR ── */
.user-pill {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.user-avatar {
    background: linear-gradient(135deg, #2e6db4, #4a90d9);
    color: white;
    width: 32px; height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.85rem;
    flex-shrink: 0;
}
.user-info { flex: 1; min-width: 0; }
.user-name {
    color: white;
    font-weight: 600;
    font-size: 0.85rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.user-role {
    color: rgba(255,255,255,0.5);
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── HEADER ── */
.app-header {
    background: linear-gradient(120deg, #1a3a5c 0%, #2e6db4 100%);
    padding: 22px 30px;
    border-radius: 14px;
    margin-bottom: 24px;
}
.app-header-top {
    display: flex;
    align-items: center;
    gap: 18px;
    margin-bottom: 16px;
}
.app-header-text h1 {
    margin: 0;
    font-size: 1.6rem;
    font-weight: 700;
    color: white;
}
.app-header-text p {
    margin: 4px 0 0;
    font-size: 0.8rem;
    color: rgba(255,255,255,0.72);
}

/* ── STEPS ── */
.steps-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}
.step {
    flex: 1 1 200px;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 10px;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 12px;
    backdrop-filter: blur(10px);
}
.step-num {
    background: white;
    color: #1a3a5c;
    width: 26px; height: 26px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.85rem;
    flex-shrink: 0;
}
.step-text {
    color: white;
    font-size: 0.78rem;
    line-height: 1.3;
    font-weight: 500;
}
.step-text b { color: #ffd966; font-weight: 700; }

/* ── METRIC CARDS ── */
.cards-row {
    display: flex;
    gap: 14px;
    margin-bottom: 26px;
}
.metric-card {
    flex: 1;
    background: #1a2332;
    border-radius: 12px;
    padding: 18px 22px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.4);
    border-top: 4px solid #4a90d9;
    border-left: 1px solid rgba(255,255,255,0.05);
    border-right: 1px solid rgba(255,255,255,0.05);
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.metric-card.red   { border-top-color: #ef4444; }
.metric-card.green { border-top-color: #22c55e; }
.metric-card.amber { border-top-color: #f59e0b; }
.metric-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #9ca3af;
    margin-bottom: 7px;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #f9fafb;
    line-height: 1;
}
.metric-sub {
    font-size: 0.73rem;
    color: #6b7280;
    margin-top: 5px;
}

/* ── SECTION TITLE ── */
.section-title {
    font-size: 0.88rem;
    font-weight: 600;
    color: #93c5fd;
    border-bottom: 2px solid rgba(147, 197, 253, 0.2);
    padding-bottom: 7px;
    margin: 18px 0 14px;
}

/* ── ALTERNATIVA CARD ── */
.alt-card {
    background: #1a2332;
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 5px solid #4a90d9;
    border-radius: 8px;
    padding: 13px 17px;
    margin-bottom: 9px;
}
.alt-card.p1 { border-left-color: #22c55e; background: rgba(34, 197, 94, 0.08); }
.alt-card.p2 { border-left-color: #f59e0b; background: rgba(245, 158, 11, 0.08); }
.alt-card.p3 { border-left-color: #ef4444; background: rgba(239, 68, 68, 0.08); }
.alt-tag {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 99px;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
.alt-tag.p1 { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
.alt-tag.p2 { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.alt-tag.p3 { background: rgba(239, 68, 68, 0.2); color: #f87171; }
.alt-name { font-size: 0.9rem; font-weight: 600; color: #f9fafb; }
.alt-contact { font-size: 0.82rem; color: #d1d5db; margin-top: 3px; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: #1a2332;
    border-radius: 9px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.05) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px !important;
    font-weight: 500;
    font-size: 0.84rem;
    color: #9ca3af;
    padding: 7px 18px;
    border: none !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: #2e6db4 !important;
    color: white !important;
    box-shadow: 0 1px 4px rgba(46, 109, 180, 0.4) !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: #1a3a5c !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: rgba(255,255,255,0.88) !important;
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white !important;
}
section[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    color: white !important;
    border-radius: 7px;
}
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.14) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    color: white !important;
    width: 100%;
    border-radius: 7px;
    font-weight: 600;
    transition: background 0.2s;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.25) !important;
}
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
section[data-testid="stSidebar"] .stProgress > div > div {
    background: rgba(255,255,255,0.2) !important;
}
section[data-testid="stSidebar"] .stProgress > div > div > div {
    background: #4ade80 !important;
}

/* ── DOWNLOAD BUTTONS ── */
.stDownloadButton > button {
    width: 100%;
    background: #1a3a5c !important;
    color: white !important;
    border: none !important;
    border-radius: 7px;
    font-weight: 600;
}
.stDownloadButton > button:hover {
    background: #14304f !important;
}

/* ── FOOTER ── */
.app-footer {
    text-align: center;
    font-size: 0.7rem;
    color: #6b7280;
    margin-top: 50px;
    padding-top: 14px;
    border-top: 1px solid rgba(255,255,255,0.08);
}

/* ── EXPANDERS y otros bloques de Streamlit ── */
[data-testid="stExpander"] {
    background: #1a2332;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
    color: #f9fafb !important;
    font-weight: 500;
}

/* Inputs y selects */
[data-baseweb="input"], [data-baseweb="select"] {
    background: #1a2332 !important;
}
.stTextInput input, .stNumberInput input {
    background: #1a2332 !important;
    color: #f9fafb !important;
    border-color: rgba(255,255,255,0.15) !important;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    background: #1a2332;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.08);
}
</style>
"""

LOGO_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="58" height="58" viewBox="0 0 100 100">'
    '<circle cx="50" cy="50" r="48" fill="rgba(255,255,255,0.13)"/>'
    '<circle cx="41" cy="41" r="23" fill="none" stroke="white" stroke-width="9"/>'
    '<line x1="57" y1="57" x2="77" y2="77" stroke="white" stroke-width="9" stroke-linecap="round"/>'
    '<circle cx="41" cy="41" r="11" fill="rgba(255,255,255,0.18)"/>'
    '</svg>'
)

# ============================================================
# FUNCIONES
# ============================================================

def _norm_col(s):
    """Normaliza un nombre de columna para comparación tolerante."""
    import unicodedata
    s = str(s).upper().strip()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return ' '.join(s.split())


# Esquema del archivo de INUBICABLES (reporte de casos)
COLS_INUB = {
    'CUIT':         (True,  ['IDENTIFICACION', 'IDENTIFICACIÓN', 'CUIT FINAL', 'CUIT', 'NRO IDENTIFICACION']),
    'DENOMINACION': (True,  ['NOMBRE DEL SUJETO', 'DENOMINACION FINAL', 'DENOMINACION', 'NOMBRE', 'CONTRIBUYENTE']),
    'DEUDA':        (True,  ['MONTO FINAL', 'DEUDA CORRIENTE ACTUALIZADA', 'DEUDA', 'MONTO', 'IMPORTE DEUDA']),
    'CANT_OBJETOS': (False, ['CANTIDAD DE OBJETOS FINAL', 'CANTIDAD DE OBJETOS', 'CANT OBJETOS']),
    'OBJETOS_TXT':  (False, ['OBJETOS', 'DETALLE OBJETOS', 'DETALLE_OBJETOS']),
    'ESTADO':       (False, ['ULTIMO ESTADO', 'ÚLTIMO ESTADO', 'ESTADO']),
}

# Esquema de la BASE DE CRUCE (con direcciones y contactos)
COLS_CRUCE = {
    'CUIT':         (True,  ['CUIT FINAL', 'CUIT', 'IDENTIFICACION', 'IDENTIFICACIÓN']),
    'DENOMINACION': (True,  ['DENOMINACION FINAL', 'DENOMINACION', 'NOMBRE DEL SUJETO', 'NOMBRE', 'CONTRIBUYENTE']),
    'DOMICILIO':    (True,  ['DOMICILIO_CATASTRO', 'DOMICILIO CATASTRO', 'DOMICILIO', 'DIRECCION']),
    'MAIL':         (True,  ['MAIL PARA ENVIO', 'MAIL', 'EMAIL', 'CORREO']),
    'CELULAR':      (True,  ['CELULAR PARA ENVIO', 'CELULAR', 'TELEFONO', 'TEL']),
    'DEUDA':        (False, ['DEUDA CORRIENTE ACTUALIZADA', 'DEUDA', 'MONTO FINAL', 'IMPORTE DEUDA']),
    'TIPO_CUENTA':  (False, ['TIPO CUENTA', 'TIPO DE CUENTA', 'TIPO_CUENTA', 'CONCEPTO']),
    'CUENTA':       (False, ['CUENTA', 'NRO CUENTA', 'NUMERO CUENTA', 'NRO_CUENTA', 'NRO. CUENTA']),
    'TEL_FIJO':     (False, ['TELEFONO FIJO', 'TEL FIJO', 'FIJO', 'TELEFONO_FIJO']),
    'EMAIL2':       (False, ['MAIL 2', 'EMAIL 2', 'MAIL SECUNDARIO', 'CORREO 2']),
    'TIPO_VINCULO': (False, ['TIPO VINCULO', 'TIPO DE VINCULO', 'VINCULO']),
}


def _mapear(df, esquema):
    cols_actual = {_norm_col(c): c for c in df.columns}
    mapeo, faltantes = {}, []
    for canonico, (obligatoria, aliases) in esquema.items():
        encontrada = next((cols_actual[_norm_col(a)] for a in aliases
                           if _norm_col(a) in cols_actual), None)
        if encontrada:
            mapeo[canonico] = encontrada
        elif obligatoria:
            faltantes.append(f"{canonico} (esperaba: {', '.join(aliases)})")
    if faltantes:
        raise ValueError(
            "Faltan columnas:\n• " + "\n• ".join(faltantes) +
            f"\n\nColumnas disponibles: {list(df.columns)}"
        )
    return mapeo


def _preparar_inub(df):
    df = df.copy()
    m = _mapear(df, COLS_INUB)
    rename = {
        m['CUIT']:         'CUIT FINAL',
        m['DENOMINACION']: 'DENOMINACION FINAL',
        m['DEUDA']:        'Deuda Corriente Actualizada',
    }
    if 'CANT_OBJETOS' in m: rename[m['CANT_OBJETOS']] = 'CANT_OBJETOS'
    if 'OBJETOS_TXT'  in m: rename[m['OBJETOS_TXT']]  = 'OBJETOS_TXT'
    if 'ESTADO'       in m: rename[m['ESTADO']]       = 'ULTIMO_ESTADO'
    df = df.rename(columns=rename)
    df['APELLIDO'] = df['DENOMINACION FINAL'].astype(str).str.split().str[0].str.upper()
    return df


def _preparar_cruce(df):
    df = df.copy()
    m = _mapear(df, COLS_CRUCE)
    rename = {
        m['CUIT']:         'CUIT FINAL',
        m['DENOMINACION']: 'DENOMINACION FINAL',
        m['DOMICILIO']:    'DOMICILIO_CATASTRO',
        m['MAIL']:         'MAIL PARA ENVIO',
        m['CELULAR']:      'CELULAR PARA ENVIO',
    }
    if 'DEUDA'        in m: rename[m['DEUDA']]        = 'Deuda Corriente Actualizada'
    if 'TIPO_CUENTA'  in m: rename[m['TIPO_CUENTA']]  = 'tipo_cuenta'
    if 'CUENTA'       in m: rename[m['CUENTA']]       = 'cuenta'
    if 'TEL_FIJO'     in m: rename[m['TEL_FIJO']]     = 'telefono_fijo'
    if 'EMAIL2'       in m: rename[m['EMAIL2']]       = 'email2'
    if 'TIPO_VINCULO' in m: rename[m['TIPO_VINCULO']] = 'tipo_vinculo'
    df = df.rename(columns=rename)

    if 'Deuda Corriente Actualizada' not in df.columns: df['Deuda Corriente Actualizada'] = 0
    for col in ['tipo_cuenta', 'cuenta', 'telefono_fijo', 'email2', 'tipo_vinculo']:
        if col not in df.columns: df[col] = ''

    df['APELLIDO']       = df['DENOMINACION FINAL'].astype(str).str.split().str[0].str.upper()
    df['DIRECCION_NORM'] = df['DOMICILIO_CATASTRO'].astype(str).str.upper().str.strip()
    df['SIN_CONTACTO']   = (df['MAIL PARA ENVIO'].isna()) & (df['CELULAR PARA ENVIO'].isna())

    def _extraer_muni(dom):
        if pd.isna(dom):
            return 'SIN DATO'
        partes = str(dom).split(' - ')
        return partes[1].strip() if len(partes) >= 2 else 'SIN DATO'

    df['MUNICIPALIDAD'] = df['DOMICILIO_CATASTRO'].apply(_extraer_muni)
    return df


def cargar_datos(archivo_inub, archivo_cruce):
    """Carga base de cruce (obligatoria) e inubicables (opcional)."""
    # Cruce — obligatorio
    try:
        df_cruce_raw = pd.read_excel(archivo_cruce)
    except Exception as e:
        st.error(f"❌ No se pudo leer la **base de cruce**: {e}")
        return None, None
    try:
        df_cruce = _preparar_cruce(df_cruce_raw)
    except ValueError as e:
        st.error(f"❌ Problema con la **base de cruce**:\n\n{e}")
        return None, None

    # Inubicables — opcional
    if archivo_inub is None or (isinstance(archivo_inub, str) and not archivo_inub):
        return None, df_cruce

    try:
        df_inub_raw = pd.read_excel(archivo_inub)
    except Exception as e:
        st.warning(f"⚠️ No se pudo leer el archivo de inubicables: {e}\nSe carga sólo la base de cruce.")
        return None, df_cruce
    try:
        df_inub = _preparar_inub(df_inub_raw)
    except ValueError as e:
        st.warning(f"⚠️ Problema con el archivo de inubicables:\n\n{e}\nSe carga sólo la base de cruce.")
        return None, df_cruce

    # Enriquecer con dirección desde cruce
    enriq = (df_cruce[['CUIT FINAL', 'DOMICILIO_CATASTRO', 'DIRECCION_NORM']]
             .drop_duplicates('CUIT FINAL'))
    df_inub = df_inub.merge(enriq, on='CUIT FINAL', how='left')

    return df_inub, df_cruce

def buscar_alternativas(df, apellido, direccion):
    grupo1 = df[
        (df['APELLIDO'] == apellido) &
        (df['DIRECCION_NORM'] == direccion) &
        ((df['MAIL PARA ENVIO'].notna()) | (df['CELULAR PARA ENVIO'].notna()))
    ]
    grupo2 = df[
        (df['APELLIDO'] == apellido) &
        ((df['MAIL PARA ENVIO'].notna()) | (df['CELULAR PARA ENVIO'].notna()))
    ]
    grupo3 = df[
        (df['DIRECCION_NORM'] == direccion) &
        ((df['MAIL PARA ENVIO'].notna()) | (df['CELULAR PARA ENVIO'].notna()))
    ]
    return {'grupo1': grupo1, 'grupo2': grupo2, 'grupo3': grupo3}

COLUMNAS_EXPORT = [
    'inubicable_nombre', 'inubicable_cuit', 'inubicable_monto', 'inubicable_objetos',
    'tipo_relacion_ia', 'confianza_ia', 'contacto_prioritario',
    'nombre_relacionado', 'cuit_relacionado', 'tipo_cuenta', 'cuenta',
    'telefono_cel', 'telefono_fijo', 'email1', 'email2', 'domicilio',
    'tipo_vinculo', 'deuda_actualizada', 'motivo_deteccion', 'explicacion_ia',
]


def _fila_relacion(inu, rel, tipo, conf, motivo, explicacion=""):
    return {
        'inubicable_nombre':    inu['DENOMINACION FINAL'],
        'inubicable_cuit':      inu['CUIT FINAL'],
        'inubicable_monto':     inu['Deuda Corriente Actualizada'],
        'inubicable_objetos':   inu.get('OBJETOS_TXT', '') if pd.notna(inu.get('OBJETOS_TXT')) else '',
        'tipo_relacion_ia':     tipo,
        'confianza_ia':         conf,
        'contacto_prioritario': '',
        'nombre_relacionado':   rel['DENOMINACION FINAL'],
        'cuit_relacionado':     rel['CUIT FINAL'],
        'tipo_cuenta':          rel.get('tipo_cuenta', ''),
        'cuenta':               rel.get('cuenta', ''),
        'telefono_cel':         rel['CELULAR PARA ENVIO'] if pd.notna(rel['CELULAR PARA ENVIO']) else '',
        'telefono_fijo':        rel.get('telefono_fijo', ''),
        'email1':               rel['MAIL PARA ENVIO'] if pd.notna(rel['MAIL PARA ENVIO']) else '',
        'email2':               rel.get('email2', ''),
        'domicilio':            rel['DOMICILIO_CATASTRO'] if pd.notna(rel['DOMICILIO_CATASTRO']) else '',
        'tipo_vinculo':         rel.get('tipo_vinculo', ''),
        'deuda_actualizada':    rel['Deuda Corriente Actualizada'] if pd.notna(rel['Deuda Corriente Actualizada']) else 0,
        'motivo_deteccion':     motivo,
        'explicacion_ia':       explicacion,
    }


def _fila_sin_match(inu):
    return {
        'inubicable_nombre':    inu['DENOMINACION FINAL'],
        'inubicable_cuit':      inu['CUIT FINAL'],
        'inubicable_monto':     inu['Deuda Corriente Actualizada'],
        'inubicable_objetos':   inu.get('OBJETOS_TXT', '') if pd.notna(inu.get('OBJETOS_TXT')) else '',
        'tipo_relacion_ia':     'SIN RELACIONADOS',
        'confianza_ia':         '',
        'contacto_prioritario': '',
        'nombre_relacionado':   '', 'cuit_relacionado': '', 'tipo_cuenta': '',
        'cuenta':               '', 'telefono_cel': '', 'telefono_fijo': '',
        'email1':               '', 'email2': '', 'domicilio': '',
        'tipo_vinculo':         '', 'deuda_actualizada': '',
        'motivo_deteccion':     'No se encontraron relacionados en la base de cruce',
        'explicacion_ia':       '',
    }


def generar_relacionados(df_inub, df_cruce, max_apellido=10, max_direccion=10):
    """Por cada inubicable, busca relacionados en la base de cruce y devuelve un DF
    con el formato del modelo (una fila por relación)."""
    filas = []

    # Pre-indexar para velocidad
    cruce_con_contacto = df_cruce[
        (df_cruce['MAIL PARA ENVIO'].notna()) | (df_cruce['CELULAR PARA ENVIO'].notna())
    ]

    for _, inu in df_inub.iterrows():
        cuit_inu  = inu['CUIT FINAL']
        apellido  = inu['APELLIDO']
        direccion = inu.get('DIRECCION_NORM', None)

        encontrados_cuits = set()

        # 1. MISMO CONTRIBUYENTE — todas las filas del CUIT en la base de cruce
        mismo_cuit = df_cruce[df_cruce['CUIT FINAL'] == cuit_inu]
        for _, r in mismo_cuit.iterrows():
            filas.append(_fila_relacion(
                inu, r, 'MISMO CONTRIBUYENTE', 1.0,
                'Registro propio del inubicable'
            ))

        # 2. MISMO APELLIDO + MISMA DIRECCIÓN
        if pd.notna(direccion) and direccion:
            mismo_ap_dir = cruce_con_contacto[
                (cruce_con_contacto['APELLIDO'] == apellido) &
                (cruce_con_contacto['DIRECCION_NORM'] == direccion) &
                (cruce_con_contacto['CUIT FINAL'] != cuit_inu)
            ]
            for _, r in mismo_ap_dir.iterrows():
                if r['CUIT FINAL'] in encontrados_cuits: continue
                encontrados_cuits.add(r['CUIT FINAL'])
                filas.append(_fila_relacion(
                    inu, r, 'MISMO APELLIDO + MISMA DIRECCION', 0.9,
                    'Apellido y direccion coinciden — probable familiar conviviente',
                    f"Apellido '{apellido}' y domicilio idénticos al del inubicable."
                ))

        # 3. MISMO APELLIDO (otra dirección)
        mismo_ap = cruce_con_contacto[
            (cruce_con_contacto['APELLIDO'] == apellido) &
            (cruce_con_contacto['CUIT FINAL'] != cuit_inu) &
            (~cruce_con_contacto['CUIT FINAL'].isin(encontrados_cuits))
        ].head(max_apellido)
        for _, r in mismo_ap.iterrows():
            encontrados_cuits.add(r['CUIT FINAL'])
            filas.append(_fila_relacion(
                inu, r, 'MISMO APELLIDO', 0.7,
                'Probable familiar (mismo apellido)',
                f"Comparte apellido '{apellido}' — posible vínculo familiar."
            ))

        # 4. MISMA DIRECCIÓN (otro apellido)
        if pd.notna(direccion) and direccion:
            misma_dir = cruce_con_contacto[
                (cruce_con_contacto['DIRECCION_NORM'] == direccion) &
                (cruce_con_contacto['APELLIDO'] != apellido) &
                (cruce_con_contacto['CUIT FINAL'] != cuit_inu) &
                (~cruce_con_contacto['CUIT FINAL'].isin(encontrados_cuits))
            ].head(max_direccion)
            for _, r in misma_dir.iterrows():
                encontrados_cuits.add(r['CUIT FINAL'])
                filas.append(_fila_relacion(
                    inu, r, 'MISMA DIRECCION', 0.5,
                    'Vecino o colindante (misma direccion)',
                    f"Vive en el mismo domicilio que el inubicable."
                ))

        # Si no se encontró nada
        if len(mismo_cuit) == 0 and not encontrados_cuits:
            filas.append(_fila_sin_match(inu))

    return pd.DataFrame(filas, columns=COLUMNAS_EXPORT)


def card_alternativa(alt, prioridad):
    labels = {
        1: ("p1", "Mismo apellido + misma dirección"),
        2: ("p2", "Mismo apellido — probable familiar"),
        3: ("p3", "Misma dirección — vecino / colindante"),
    }
    cls, titulo = labels[prioridad]
    tel  = f"📱 {alt['CELULAR PARA ENVIO']}" if pd.notna(alt['CELULAR PARA ENVIO']) else ""
    mail = f"📧 {alt['MAIL PARA ENVIO']}"    if pd.notna(alt['MAIL PARA ENVIO'])    else ""
    contacto = "  ·  ".join(filter(None, [tel, mail]))
    return f"""
<div class="alt-card {cls}">
    <span class="alt-tag {cls}">{titulo}</span>
    <div class="alt-name">{alt['DENOMINACION FINAL']}</div>
    <div class="alt-contact">{contacto}</div>
</div>
"""

# ============================================================
# UI
# ============================================================

st.markdown(CSS, unsafe_allow_html=True)

# ── Header con instrucciones ──
header_html = (
    '<div class="app-header">'
    '<div class="app-header-top">'
    f'{LOGO_SVG}'
    '<div class="app-header-text">'
    '<h1>Buscador de Inubicables</h1>'
    '<p>Procuraduría Fiscal &nbsp;·&nbsp; Sistema de gestión de contactos &nbsp;·&nbsp; Uso interno</p>'
    '</div>'
    '</div>'
    '<div class="steps-row">'
    '<div class="step"><div class="step-num">1</div><div class="step-text"><b>Base cargada automáticamente</b> del servidor</div></div>'
    '<div class="step"><div class="step-num">2</div><div class="step-text">Seleccionar <b>municipalidad</b> en el panel lateral</div></div>'
    '<div class="step"><div class="step-num">3</div><div class="step-text">Cargar <b>inubicables</b> *(opcional — en «Cambiar archivos»)*</div></div>'
    '<div class="step"><div class="step-num">4</div><div class="step-text"><b>Buscar o generar relaciones</b></div></div>'
    '</div>'
    '</div>'
)
st.markdown(header_html, unsafe_allow_html=True)

# ── Auto-carga: si hay una sola base disponible, cargarla directamente ──
_bases_disponibles = listar_bases()
if 'df_cruce' not in st.session_state and len(_bases_disponibles) == 1:
    with st.spinner(f"⏳ Cargando {_bases_disponibles[0].name}..."):
        _, df_cruce_n = cargar_datos(None, str(_bases_disponibles[0]))
        if df_cruce_n is not None:
            st.session_state.df_cruce    = df_cruce_n
            st.session_state.df_inub     = None
            st.session_state._base_activa = _bases_disponibles[0].name
            st.session_state._server_loaded = True
    st.rerun()

# ── Sidebar ──
with st.sidebar:
    # ── Usuario logueado ──
    iniciales = "".join(p[0] for p in usuario_actual["name"].split()[:2]).upper() or "?"
    st.markdown(
        f'<div class="user-pill">'
        f'<div class="user-avatar">{iniciales}</div>'
        f'<div class="user-info">'
        f'<div class="user-name">{usuario_actual["name"]}</div>'
        f'<div class="user-role">{usuario_actual["role"]}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )
    if st.button("🚪 Cerrar sesión", use_container_width=True, key="btn_logout"):
        auth.logout()

    st.markdown("---")

    # ── Selector de base de objetos ──
    st.markdown("### 🗂️ Base de objetos")

    _bases_servidor = listar_bases()   # archivos en bases/ (solo local)
    _bases_subidas  = st.session_state.get('_bases_subidas', {})  # {nombre: bytes} (web)

    # En web (sin carpeta bases/) mostrar uploader para subir bases
    if not _bases_servidor:
        _nuevo = st.file_uploader(
            "📤 Subir base Excel:",
            type=['xlsx', 'xls'],
            key="up_base_nueva",
        )
        if _nuevo is not None:
            _bases_subidas[_nuevo.name] = _nuevo.getvalue()
            st.session_state['_bases_subidas'] = _bases_subidas

    # Lista combinada: servidor + subidas
    _opciones = (
        [{'origen': 'server', 'nombre': p.name, 'path': str(p)} for p in _bases_servidor]
        + [{'origen': 'upload', 'nombre': n} for n in _bases_subidas]
    )

    if _opciones:
        _nombres     = [o['nombre'] for o in _opciones]
        _base_prev   = st.session_state.get('_base_activa', _nombres[0])
        _base_idx    = _nombres.index(_base_prev) if _base_prev in _nombres else 0
        _base_sel    = st.selectbox("📁 Seleccionar archivo:", _nombres, index=_base_idx)
        _sel_opt     = next(o for o in _opciones if o['nombre'] == _base_sel)
        _cambio_base = _base_sel != st.session_state.get('_base_activa')

        if _cambio_base or 'df_cruce' not in st.session_state:
            if st.button("🔄 Cargar esta base", use_container_width=True, type="primary"):
                with st.spinner(f"Cargando {_base_sel}..."):
                    if _sel_opt['origen'] == 'server':
                        _, df_cruce_n = cargar_datos(None, _sel_opt['path'])
                    else:
                        _, df_cruce_n = cargar_datos(None, io.BytesIO(_bases_subidas[_base_sel]))
                    if df_cruce_n is not None:
                        st.session_state.df_cruce        = df_cruce_n
                        st.session_state.df_inub         = None
                        st.session_state._base_activa    = _base_sel
                        st.session_state._server_loaded  = True
                        st.session_state['_muni_filtro'] = 'Todas'
                        st.session_state['_tipo_filtro'] = []
                st.rerun()
        else:
            st.caption(f"📡 Cargado: *{_base_sel}*")

    st.markdown("---")

    # ── Resumen de datos ──
    if 'df_cruce' in st.session_state:
        df_c = st.session_state.df_cruce
        df_i = st.session_state.get('df_inub')
        st.markdown(f"**Objetos:** {len(df_c):,}")
        if df_i is not None:
            st.markdown(f"**Inubicables:** {len(df_i):,}")
            if len(df_c) > 0:
                pct = len(df_i) / len(df_c) * 100
                st.progress(min(pct / 100, 1.0), text=f"{pct:.1f}% sobre base")
        else:
            st.caption("Modo búsqueda individual")
        st.markdown("---")

    # ── Configuración de archivos (expander) ──
    with st.expander("⚙️ Cambiar archivos / Cargar inubicables"):
        st.markdown("**📄 Archivo de inubicables** *(opcional)*")
        st.caption("Para procesar todos los inubicables en lote")
        file_inub = st.file_uploader(
            "file_inub", type=['xlsx', 'xls'],
            label_visibility="collapsed", key="up_inub"
        )

        st.markdown("")
        st.markdown("**🗂️ Otra base de objetos** *(reemplaza la del servidor)*")
        file_cruce = st.file_uploader(
            "file_cruce", type=['xlsx', 'xls'],
            label_visibility="collapsed", key="up_cruce"
        )

        cargar = st.button("🔄 Cargar / Actualizar", use_container_width=True, type="primary")
        ruta_inub  = None
        ruta_cruce = None

    st.markdown("---")
    st.markdown(
        f"<div style='color:rgba(255,255,255,0.35);font-size:0.68rem;'>"
        f"v2.3 &nbsp;·&nbsp; {datetime.now().strftime('%d/%m/%Y')}</div>",
        unsafe_allow_html=True
    )

# ── Cargar datos ──
if cargar:
    fuente_inub  = file_inub  if file_inub  is not None else (ruta_inub or None)
    fuente_cruce = file_cruce if file_cruce is not None else ruta_cruce

    if not fuente_cruce:
        st.sidebar.error("Falta cargar el **detalle total de objetos** (obligatorio).")
    else:
        with st.spinner("Cargando datos..."):
            df_inub_n, df_cruce_n = cargar_datos(fuente_inub, fuente_cruce)
            if df_cruce_n is not None:
                st.session_state.df_inub  = df_inub_n     # puede ser None
                st.session_state.df_cruce = df_cruce_n
                st.success("✅ Datos cargados correctamente")
                import time; time.sleep(0.7)
                st.rerun()

# Sin cruce, frenar
if 'df_cruce' not in st.session_state:
    _tiene_bases = listar_bases() or st.session_state.get('_bases_subidas')
    if _tiene_bases:
        st.info("👈 Seleccioná una base en el panel lateral y hacé clic en **Cargar esta base**.")
    else:
        st.info("👈 Subí el archivo Excel de **detalle de objetos** desde el panel lateral y hacé clic en **Cargar esta base**.")
    st.stop()

df_cruce_full = st.session_state.df_cruce
df_cruce      = df_cruce_full
df_inub       = st.session_state.get('df_inub')   # puede ser None

df = df_cruce
inubicables  = df_inub if df_inub is not None else None
con_contacto = df_cruce[~df_cruce['SIN_CONTACTO']]

deuda_cruce = df_cruce['Deuda Corriente Actualizada'].sum()
deuda_inub  = inubicables['Deuda Corriente Actualizada'].sum() if (inubicables is not None and 'Deuda Corriente Actualizada' in inubicables.columns) else 0
pct_inub    = (len(inubicables) / len(df_cruce) * 100) if (inubicables is not None and len(df_cruce) > 0) else 0
total_objetos = int(inubicables['CANT_OBJETOS'].sum()) if (inubicables is not None and 'CANT_OBJETOS' in inubicables.columns) else None

# ── Métricas ──
if inubicables is not None:
    cards_html = (
        '<div class="cards-row">'
        f'<div class="metric-card"><div class="metric-label">Base de cruce</div>'
        f'<div class="metric-value">{len(df_cruce):,}</div>'
        f'<div class="metric-sub">registros disponibles</div></div>'
        f'<div class="metric-card green"><div class="metric-label">Con contacto</div>'
        f'<div class="metric-value">{len(con_contacto):,}</div>'
        f'<div class="metric-sub">posibles fuentes de contacto</div></div>'
        f'<div class="metric-card red"><div class="metric-label">Inubicables a buscar</div>'
        f'<div class="metric-value">{len(inubicables):,}</div>'
        f'<div class="metric-sub">{pct_inub:.1f}% sobre base de cruce</div></div>'
        f'<div class="metric-card amber"><div class="metric-label">'
        f'{"Cant. objetos" if total_objetos is not None else "Deuda inubicables"}</div>'
        f'<div class="metric-value">'
        f'{(f"{total_objetos:,}" if total_objetos is not None else f"${deuda_inub / 1_000_000:.1f}M")}</div>'
        f'<div class="metric-sub">'
        f'{(f"deuda: ${deuda_inub / 1_000_000:.1f}M") if total_objetos is not None else f"de ${deuda_cruce / 1_000_000:.1f}M total"}</div></div>'
        '</div>'
    )
else:
    sin_cont = df_cruce[df_cruce['SIN_CONTACTO']]
    cards_html = (
        '<div class="cards-row">'
        f'<div class="metric-card"><div class="metric-label">Base de cruce</div>'
        f'<div class="metric-value">{len(df_cruce):,}</div>'
        f'<div class="metric-sub">registros disponibles</div></div>'
        f'<div class="metric-card green"><div class="metric-label">Con contacto</div>'
        f'<div class="metric-value">{len(con_contacto):,}</div>'
        f'<div class="metric-sub">{(len(con_contacto)/len(df_cruce)*100 if len(df_cruce) else 0):.1f}% del total</div></div>'
        f'<div class="metric-card red"><div class="metric-label">Sin contacto</div>'
        f'<div class="metric-value">{len(sin_cont):,}</div>'
        f'<div class="metric-sub">{(len(sin_cont)/len(df_cruce)*100 if len(df_cruce) else 0):.1f}% del total</div></div>'
        f'<div class="metric-card amber"><div class="metric-label">Deuda total</div>'
        f'<div class="metric-value">${deuda_cruce / 1_000_000:.1f}M</div>'
        f'<div class="metric-sub">en la base de cruce</div></div>'
        '</div>'
    )
st.markdown(cards_html, unsafe_allow_html=True)

# ── Tabs ──
if inubicables is not None:
    tab_persona, tab1, tab2, tab3 = st.tabs([
        "👤  Buscar persona",
        "🔎  Buscar inubicable",
        "📊  Estadísticas",
        "📋  Lista completa",
    ])
else:
    (tab_persona,) = st.tabs(["👤  Buscar persona"])
    tab1 = tab2 = tab3 = None


# ============================================================
# TAB 0 — BUSCAR PERSONA INDIVIDUAL (sólo cruce)
# ============================================================
with tab_persona:
    st.caption(
        "Buscá una persona dentro del **detalle total de objetos** y mirá sus relacionados "
        "(mismo CUIT, mismo apellido + dirección, mismo apellido, misma dirección)."
    )

    cp1, cp2 = st.columns([3, 1])
    with cp1:
        nombre_p = st.text_input(
            "nombre_p", label_visibility="collapsed",
            placeholder="Buscar por nombre  (ej: MARTINEZ, GONZALEZ…)",
            key="busca_persona_nombre"
        )
    with cp2:
        cuit_p = st.text_input(
            "cuit_p", label_visibility="collapsed",
            placeholder="O por CUIT",
            key="busca_persona_cuit"
        )

    # Buscar coincidencias en df_cruce y agrupar por CUIT
    if nombre_p:
        match = df_cruce[df_cruce['DENOMINACION FINAL'].str.contains(nombre_p.upper(), na=False)]
    elif cuit_p:
        try:
            match = df_cruce[df_cruce['CUIT FINAL'] == int(cuit_p)]
        except ValueError:
            match = df_cruce.head(0)
    else:
        match = df_cruce.head(0)

    if (nombre_p or cuit_p) and len(match) == 0:
        st.warning("No se encontraron resultados.")
    elif len(match) > 0:
        # Una persona = un CUIT único (puede tener varios objetos = filas)
        personas = (match.groupby('CUIT FINAL')
                         .agg({
                             'DENOMINACION FINAL': 'first',
                             'DOMICILIO_CATASTRO': 'first',
                             'APELLIDO': 'first',
                             'DIRECCION_NORM': 'first',
                             'Deuda Corriente Actualizada': 'sum',
                             'MAIL PARA ENVIO': 'first',
                             'CELULAR PARA ENVIO': 'first',
                         })
                         .reset_index())
        # Cantidad de objetos = cuantas filas tiene el CUIT en el cruce
        personas['CANT_OBJETOS'] = personas['CUIT FINAL'].map(df_cruce['CUIT FINAL'].value_counts())

        st.caption(f"{len(personas)} persona(s) encontrada(s)")

        for _, p in personas.head(15).iterrows():
            sin_cont_emoji = "🔴" if (pd.isna(p['MAIL PARA ENVIO']) and pd.isna(p['CELULAR PARA ENVIO'])) else "🟢"
            with st.expander(
                f"{sin_cont_emoji}  **{p['DENOMINACION FINAL']}**  "
                f"— CUIT: {p['CUIT FINAL']}  "
                f"— Deuda: ${p['Deuda Corriente Actualizada']:,.0f}  "
                f"— {int(p['CANT_OBJETOS'])} objetos"
            ):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**CUIT:** `{p['CUIT FINAL']}`")
                    st.markdown(f"**Nombre:** {p['DENOMINACION FINAL']}")
                    st.markdown(f"**Cantidad de objetos:** {int(p['CANT_OBJETOS'])}")
                with c2:
                    dom = p['DOMICILIO_CATASTRO'] if pd.notna(p['DOMICILIO_CATASTRO']) else '— sin dato —'
                    st.markdown(f"**Dirección:** {dom}")
                    st.markdown(f"**Deuda total:** ${p['Deuda Corriente Actualizada']:,.2f}")
                    if pd.notna(p['CELULAR PARA ENVIO']):
                        st.markdown(f"**📱 Celular propio:** {p['CELULAR PARA ENVIO']}")
                    if pd.notna(p['MAIL PARA ENVIO']):
                        st.markdown(f"**📧 Email propio:** {p['MAIL PARA ENVIO']}")

                st.markdown(
                    '<div class="section-title">Personas relacionadas</div>',
                    unsafe_allow_html=True
                )

                # Construir un "inu" sintético para usar generar_relacionados
                inu_sint = pd.DataFrame([{
                    'CUIT FINAL':                  p['CUIT FINAL'],
                    'DENOMINACION FINAL':          p['DENOMINACION FINAL'],
                    'Deuda Corriente Actualizada': p['Deuda Corriente Actualizada'],
                    'APELLIDO':                    p['APELLIDO'],
                    'DIRECCION_NORM':              p['DIRECCION_NORM'],
                    'DOMICILIO_CATASTRO':          p['DOMICILIO_CATASTRO'],
                    'CANT_OBJETOS':                p['CANT_OBJETOS'],
                    'OBJETOS_TXT':                 '',
                }])

                rels = generar_relacionados(inu_sint, df_cruce_full, max_apellido=15, max_direccion=15)
                # Sacar las filas "MISMO CONTRIBUYENTE" y "SIN RELACIONADOS" para el visual
                rels_visual = rels[~rels['tipo_relacion_ia'].isin(['MISMO CONTRIBUYENTE', 'SIN RELACIONADOS'])]

                if len(rels_visual) == 0:
                    st.warning("⚠️ No se encontraron personas relacionadas con datos de contacto.")
                else:
                    # Mapeo a card_alternativa: necesitamos un dict tipo cruce row
                    html = ""
                    for _, r in rels_visual.iterrows():
                        prioridad = {
                            'MISMO APELLIDO + MISMA DIRECCION': 1,
                            'MISMO APELLIDO': 2,
                            'MISMA DIRECCION': 3,
                        }.get(r['tipo_relacion_ia'], 2)
                        alt_dict = {
                            'DENOMINACION FINAL': r['nombre_relacionado'],
                            'CELULAR PARA ENVIO': r['telefono_cel'] if r['telefono_cel'] else float('nan'),
                            'MAIL PARA ENVIO':    r['email1']       if r['email1']       else float('nan'),
                        }
                        html += card_alternativa(alt_dict, prioridad)
                    st.markdown(html, unsafe_allow_html=True)

                # Botón para descargar Excel sólo de esta persona
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                buf = io.BytesIO()
                rels.to_excel(buf, index=False, engine='openpyxl')
                st.download_button(
                    label=f"📥 Descargar relacionados de {p['DENOMINACION FINAL']}",
                    data=buf.getvalue(),
                    file_name=f"Relacionados_{p['CUIT FINAL']}_{ts}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key=f"dl_{p['CUIT FINAL']}_{ts}",
                )


# ============================================================
# TABS DE INUBICABLES (sólo si está cargado el archivo)
# ============================================================
if inubicables is not None and tab1 is not None:
    # ── TAB 1 — BUSCAR INUBICABLE ──
    with tab1:
        col_n, col_c = st.columns([3, 1])
        with col_n:
            nombre_busca = st.text_input(
                "nombre", label_visibility="collapsed",
                placeholder="Buscar por nombre  (ej: MARTINEZ, LOPEZ…)"
            )
        with col_c:
            cuit_busca = st.text_input(
                "cuit", label_visibility="collapsed",
                placeholder="O por CUIT"
            )

        if nombre_busca:
            resultados = inubicables[
                inubicables['DENOMINACION FINAL'].str.contains(nombre_busca.upper(), na=False)
            ]
        elif cuit_busca:
            try:
                resultados = inubicables[inubicables['CUIT FINAL'] == int(cuit_busca)]
            except ValueError:
                resultados = inubicables.head(0)
        else:
            resultados = inubicables.head(0)

        if (nombre_busca or cuit_busca) and len(resultados) == 0:
            st.warning("No se encontraron resultados.")
        elif len(resultados) > 0:
            st.caption(f"{len(resultados)} resultado(s) encontrado(s)")

            for _, row in resultados.head(20).iterrows():
                obj_str = f" — {int(row['CANT_OBJETOS'])} objetos" if 'CANT_OBJETOS' in row and pd.notna(row.get('CANT_OBJETOS')) else ""
                with st.expander(
                    f"**{row['DENOMINACION FINAL']}** "
                    f"— CUIT: {row['CUIT FINAL']} "
                    f"— Deuda: ${row['Deuda Corriente Actualizada']:,.0f}"
                    f"{obj_str}"
                ):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**CUIT:** `{row['CUIT FINAL']}`")
                        st.markdown(f"**Nombre:** {row['DENOMINACION FINAL']}")
                        if 'CANT_OBJETOS' in row and pd.notna(row.get('CANT_OBJETOS')):
                            st.markdown(f"**Cantidad de objetos:** {int(row['CANT_OBJETOS'])}")
                    with c2:
                        domicilio = row.get('DOMICILIO_CATASTRO', '— sin datos en base de cruce —')
                        st.markdown(f"**Dirección:** {domicilio if pd.notna(domicilio) else '— sin datos en base de cruce —'}")
                        st.markdown(f"**Deuda:** ${row['Deuda Corriente Actualizada']:,.2f}")
                        if 'ULTIMO_ESTADO' in row and pd.notna(row.get('ULTIMO_ESTADO')):
                            st.markdown(f"**Último estado:** {row['ULTIMO_ESTADO']}")

                    st.markdown(
                        '<div class="section-title">Alternativas de contacto</div>',
                        unsafe_allow_html=True
                    )

                    direccion = row.get('DIRECCION_NORM', None)
                    alts = buscar_alternativas(df_cruce_full, row['APELLIDO'], direccion if pd.notna(direccion) else "___NO_MATCH___")
                    html_alts = ""
                    for p in [1, 2, 3]:
                        for _, alt in alts[f'grupo{p}'].head(2).iterrows():
                            html_alts += card_alternativa(alt, p)

                    if html_alts:
                        st.markdown(html_alts, unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ No se encontraron alternativas de contacto.")

    # ── TAB 2 — ESTADÍSTICAS ──
    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-title">Deuda por contactabilidad</div>', unsafe_allow_html=True)
            df_chart = pd.DataFrame({
                'Estado': ['Con contacto', 'Inubicables'],
                'Deuda ($M)': [
                    con_contacto['Deuda Corriente Actualizada'].sum() / 1_000_000,
                    deuda_inub / 1_000_000,
                ]
            }).set_index('Estado')
            st.bar_chart(df_chart, color="#2e6db4")

        with col2:
            st.markdown('<div class="section-title">Top 10 deudores inubicables</div>', unsafe_allow_html=True)
            top10 = (
                inubicables
                .nlargest(10, 'Deuda Corriente Actualizada')
                [['DENOMINACION FINAL', 'Deuda Corriente Actualizada']]
                .copy()
            )
            top10.columns = ['Deudor', 'Deuda ($)']
            top10['Deuda ($)'] = top10['Deuda ($)'].apply(lambda x: f"${x:,.0f}")
            top10 = top10.reset_index(drop=True)
            top10.index += 1
            st.dataframe(top10, use_container_width=True)

    # ── TAB 3 — LISTA COMPLETA ──
    with tab3:
        col1, col2, col3 = st.columns(3)
        with col1:
            deuda_min = st.number_input("Deuda mínima ($):", value=0, step=1000)
        with col2:
            deuda_max = st.number_input(
                "Deuda máxima ($):",
                value=int(inubicables['Deuda Corriente Actualizada'].max()),
                step=1000
            )
        with col3:
            ordenar_por = st.selectbox("Ordenar por:", ["Deuda ↓", "Deuda ↑", "Nombre A-Z"])

        resultado = inubicables[
            (inubicables['Deuda Corriente Actualizada'] >= deuda_min) &
            (inubicables['Deuda Corriente Actualizada'] <= deuda_max)
        ].copy()

        if ordenar_por == "Deuda ↓":
            resultado = resultado.sort_values('Deuda Corriente Actualizada', ascending=False)
        elif ordenar_por == "Deuda ↑":
            resultado = resultado.sort_values('Deuda Corriente Actualizada', ascending=True)
        else:
            resultado = resultado.sort_values('DENOMINACION FINAL')

        cols_show = ['CUIT FINAL', 'DENOMINACION FINAL']
        if 'DOMICILIO_CATASTRO' in resultado.columns: cols_show.append('DOMICILIO_CATASTRO')
        if 'CANT_OBJETOS' in resultado.columns:       cols_show.append('CANT_OBJETOS')
        cols_show.append('Deuda Corriente Actualizada')

        mostrar = resultado[cols_show].copy()
        nuevos = {'CUIT FINAL': 'CUIT', 'DENOMINACION FINAL': 'Deudor',
                  'DOMICILIO_CATASTRO': 'Dirección', 'CANT_OBJETOS': 'Objetos',
                  'Deuda Corriente Actualizada': 'Deuda ($)'}
        mostrar = mostrar.rename(columns=nuevos).reset_index(drop=True)

        st.dataframe(mostrar, use_container_width=True, height=380)
        st.caption(f"{len(resultado):,} registros")

        st.markdown('<div class="section-title">📤 Exportar relacionados</div>', unsafe_allow_html=True)
        st.caption(
            "Genera un Excel con una fila por cada relación encontrada "
            "(mismo contribuyente · mismo apellido + dirección · mismo apellido · misma dirección)."
        )

        if 'relacionados' not in st.session_state:
            st.session_state.relacionados = None

        col_g, col_d = st.columns([1, 1])
        ts_lote = datetime.now().strftime('%Y%m%d_%H%M%S')

        with col_g:
            if st.button("🔍 Generar relacionados", type="primary", use_container_width=True):
                with st.spinner(f"Procesando {len(resultado):,} inubicables..."):
                    st.session_state.relacionados = generar_relacionados(resultado, df_cruce_full)
                st.success(f"✅ Se generaron {len(st.session_state.relacionados):,} filas de relaciones.")

        with col_d:
            if st.session_state.relacionados is not None and len(st.session_state.relacionados) > 0:
                buf_lote = io.BytesIO()
                st.session_state.relacionados.to_excel(buf_lote, index=False, engine='openpyxl')
                st.download_button(
                    label="📥 Descargar Excel de relacionados",
                    data=buf_lote.getvalue(),
                    file_name=f"Relacionados_Inubicables_{ts_lote}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

        if st.session_state.relacionados is not None and len(st.session_state.relacionados) > 0:
            st.markdown("**Vista previa:**")
            st.dataframe(
                st.session_state.relacionados.head(50),
                use_container_width=True,
                height=300
            )

# ── Footer ──
st.markdown(
    f'<div class="app-footer">'
    f'Procuraduría Fiscal &nbsp;·&nbsp; Sistema de gestión de inubicables &nbsp;·&nbsp; Uso interno'
    f'<br>Sesión: <b>{usuario_actual["name"]}</b> &nbsp;·&nbsp; '
    f'v2.2 &nbsp;·&nbsp; {datetime.now().strftime("%d/%m/%Y %H:%M")}'
    f'</div>',
    unsafe_allow_html=True,
)
