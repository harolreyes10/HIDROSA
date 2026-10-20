"""Capa de presentación HIDROSA 2.0.

Contiene exclusivamente estilos y navegación. Los cálculos están en motor_hidraulico.py.
"""
import streamlit as st

AZUL = '#102A43'
CIAN = '#087E8B'
GRIS = '#5B7083'

OPERACIONES = [
    ('uniforme_y', 'Tirante normal', 'Determina y conocidos Q, S y la sección.', 'Flujo uniforme', '01'),
    ('uniforme_Q', 'Caudal', 'Determina Q conocidos y, S y la sección.', 'Flujo uniforme', '02'),
    ('uniforme_S', 'Pendiente', 'Calcula S conocidos Q, y y la sección.', 'Flujo uniforme', '03'),
    ('critico', 'Tirante crítico', 'Estado crítico, Froude y pendiente crítica.', 'Flujo crítico', '04'),
    ('energia', 'Energía específica', 'Curva de energía, yc y tirante alterno.', 'Flujo crítico', '05'),
    ('diseno', 'Diseño de sección', 'Eficiencia hidráulica y dimensionamiento.', 'Diseño', '06'),
    ('compuesta', 'Sección compuesta', 'Materiales variables y división en subáreas.', 'Secciones especiales', '07'),
]

GRUPOS = ['Flujo uniforme', 'Flujo crítico', 'Diseño', 'Secciones especiales']

ESTILOS = r'''<style>
:root { --azul:#102A43; --tinta:#1D3548; --cian:#087E8B; --celeste:#E7F5F6;
       --borde:#DCE6ED; --gris:#61788A; --fondo:#F3F7FA; }
.stApp {background:var(--fondo); color:var(--tinta)}
[data-testid="stHeader"] {background:rgba(243,247,250,.96)}
.block-container {max-width:1800px;padding-top:1.15rem;padding-bottom:3.5rem}
#MainMenu{visibility:hidden}
header + div {scroll-margin-top:1rem}
.hdr {display:flex;align-items:center;gap:14px;color:#fff;
      padding:16px 22px;border-radius:14px 14px 0 0;background:linear-gradient(105deg,#102A43,#174461 75%,#126977)}
.hdr .logo{display:flex;align-items:center;justify-content:center;width:44px;height:44px;
           flex:0 0 44px;background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.3);
           border-radius:12px;font-size:23px}
.hdr .brand{font-weight:800;font-size:23px;letter-spacing:.035em;line-height:1.1;color:white}
.hdr .sub{color:#B8DDE2;font-size:12px;font-weight:500;letter-spacing:.04em;margin-top:5px}
.hdr .version{margin-left:auto;white-space:nowrap;color:#C7EBEF;font-size:12px;
              border:1px solid #598E9F;border-radius:30px;padding:6px 10px}
.nav-capa {height:4px;background:#15B8BC;border-radius:0 0 6px 6px;margin-bottom:10px}
[data-testid="stPopover"] button {border-radius:9px !important;font-weight:650 !important}
[data-testid="stPopoverBody"] button {font-weight:500 !important}
.stButton button[kind="primary"] {background:#087E8B!important;color:white!important;border:1px solid #087E8B!important}
.stButton button[kind="primary"] p{color:white!important}
.stButton button:hover {border-color:#087E8B!important;color:#087E8B!important}
.stButton button[kind="primary"]:hover{color:white!important;background:#075d68!important}
[data-testid="stPopover"] button:hover {border-color:#087E8B!important}
[data-testid="stVerticalBlockBorderWrapper"] {border-color:var(--borde)!important;border-radius:12px!important;background:#fff}
[data-testid="stMetric"] {background:#F6FAFC;border:1px solid #E1EAF0;border-radius:10px;padding:9px 12px}
[data-testid="stMetricLabel"] p {color:#526C7F;font-size:12px}
[data-testid="stMetricValue"] {color:#102A43;font-weight:800;font-size:clamp(17px,1.4vw,23px)}
[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input {border-radius:8px}
[data-testid="stWidgetLabel"] p{font-size:.85rem;font-weight:550;color:#334E60}
.stSelectbox, .stNumberInput, .stRadio{margin-bottom:0}
h1,h2,h3 {color:#102A43;letter-spacing:-.02em}
hr {border-color:#DCE6ED}
.ficha-titulo{display:flex;align-items:center;gap:8px;font-size:16px;letter-spacing:.01em;
              font-weight:750;color:#102A43;margin:6px 0 14px}
.ficha-titulo span{display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;
                   border-radius:8px;background:#E2F4F4;color:#087E8B;font-size:12px;font-weight:800}
.paso{display:flex;align-items:center;gap:10px;font-size:17px;font-weight:700;color:#102A43;margin-bottom:8px}
.paso .num{background:#E7F5F6;color:#087E8B;width:26px;height:26px;border-radius:8px;
           display:inline-flex;align-items:center;justify-content:center;font-size:13px}
.res{background:#F0F9FA;border-left:4px solid #087E8B;border-radius:6px;padding:10px 13px;
     color:#102A43;font-weight:700;margin:10px 0 3px}
.res.ok{background:#EAF6F0;border-left-color:#23A26D}
.res.mal{background:#FFF1F1;border-left-color:#D25A55}
.grupo{font-size:16px;color:#102A43;font-weight:750;margin:16px 0 10px;padding-bottom:7px;
       border-bottom:1px solid #DCE6ED}
table.cw{width:100%;border-collapse:collapse;font-size:12px;background:#fff}
table.cw th {background:#102A43;color:white;padding:8px 8px;text-align:center}
table.cw td{padding:7px 8px;border-bottom:1px solid #E0E7ED;color:#284355}
table.cw td.g{font-weight:700;background:#F2F6F9}
table.cw td.f{text-align:center;font-weight:700}
table.cw td.v{text-align:center;font-weight:700}
table.cw td.na{text-align:center;color:#8799A6}
table.cw tr.sel td{background:#E7F5F6;font-weight:700}
.mast{font-size:13px;color:#526C7F;margin-top:10px;margin-bottom:12px}
.mast b{color:#102A43}
.recuadro{border:1px solid #DCE6ED;background:#fff;border-radius:12px;padding:16px 18px;margin-bottom:10px}
.recuadro .n{font-size:12px;color:#087E8B;font-weight:800}
.recuadro .t{font-size:17px;color:#102A43;font-weight:800;margin:6px 0}
.recuadro .d{font-size:13px;color:#61788A;min-height:34px}
.pista{background:#EAF6F7;border:1px solid #CDE7E9;padding:10px 12px;border-radius:9px;color:#284355;
       font-size:12px;margin:4px 0 14px}
[data-testid="stExpander"] details{background:white;border-color:#DCE6ED;border-radius:9px}
.stPlotlyChart {border-radius:10px;overflow:hidden}
@media(max-width: 800px){.hdr{padding:14px}.hdr .brand{font-size:19px}.hdr .version{display:none}}


/* HIDROSA - Contraste coherente incluso cuando el navegador pide tema oscuro.
   No modifica la posición de los controles ni la lógica de cálculo. */
:root { color-scheme: light; }
.stApp {background:#F3F7FA!important;color:#102A43!important;color-scheme:light;}

/* Navegación superior: fondo oscuro, texto e iconos blancos. */
.stApp [data-testid="stPopover"] > button {
  background:#111820!important; color:#FFFFFF!important;
  border:1px solid #344B5B!important;
}
.stApp [data-testid="stPopover"] > button *,
.stApp [data-testid="stPopover"] > button p,
.stApp [data-testid="stPopover"] > button svg {
  color:#FFFFFF!important;
}
.stApp [data-testid="stPopover"] > button:hover {
  background:#17475A!important; border-color:#19A6B0!important;
}

/* Botones estándar, incluida la opción Inicio cuando no está seleccionada. */
.stApp [data-testid="stButton"] button[kind="secondary"],
.stApp [data-testid="stDownloadButton"] button {
  background:#FFFFFF!important; color:#14364C!important;
  border:1px solid #C8D9E2!important;
}
.stApp [data-testid="stButton"] button[kind="secondary"] *,
.stApp [data-testid="stDownloadButton"] button * {color:#14364C!important;}
.stApp [data-testid="stButton"] button[kind="secondary"]:hover,
.stApp [data-testid="stDownloadButton"] button:hover {
  background:#E6F5F7!important; border-color:#087E8B!important;
}
.stApp [class*="st-key-nav_home"] button,
.stApp [class*="st-key-nav_home"] button:hover {
  background:#111820!important;color:#FFFFFF!important;
  border-color:#344B5B!important;
}
.stApp [class*="st-key-nav_home"] button * {color:#FFFFFF!important;}

/* Materiales y otras opciones radio: texto siempre oscuro y visible. */
.stApp [data-testid="stRadio"] [role="radiogroup"] label,
.stApp [data-testid="stRadio"] [role="radiogroup"] label *,
.stApp [data-testid="stCheckbox"] label,
.stApp [data-testid="stCheckbox"] label * {
  color:#17384D!important;
}
.stApp [data-testid="stRadio"] [role="radiogroup"] label:hover,
.stApp [data-testid="stCheckbox"] label:hover {color:#087E8B!important;}

/* Listas desplegables: superficie blanca y valores legibles, incluido el menú. */
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  background:#FFFFFF!important; border-color:#B5CDD9!important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] *,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] * {
  color:#102A43!important;
}
.stApp [data-testid="stSelectbox"] [data-baseweb="select"] input,
.stApp [data-testid="stMultiSelect"] [data-baseweb="select"] input {
  color:#102A43!important;caret-color:#087E8B!important;
}
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="popover"] [role="option"] {
  background:#FFFFFF!important;color:#102A43!important;
}
[data-baseweb="popover"] [role="option"] * {color:#102A43!important;}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [role="option"][aria-selected="true"] {
  background:#E4F4F6!important;
}

/* Alternador 'Por tramos / Por coordenadas' y demás controles segmentados. */
.stApp [data-testid="stSegmentedControl"] button {
  background:#FFFFFF!important;color:#17384D!important;
  border-color:#C0D6E0!important;
}
.stApp [data-testid="stSegmentedControl"] button * {color:inherit!important;}
.stApp [data-testid="stSegmentedControl"] button[aria-pressed="true"],
.stApp [data-testid="stSegmentedControl"] button[aria-checked="true"],
.stApp [data-testid="stSegmentedControl"] button[data-state="active"] {
  background:#087E8B!important;color:#FFFFFF!important;
  border-color:#087E8B!important;
}

/* Campos numéricos: mantener el diseño oscuro original con texto blanco. */
.stApp [data-testid="stNumberInput"] input {
  background:#25262F!important;color:#FFFFFF!important;
  -webkit-text-fill-color:#FFFFFF!important;
}
.stApp [data-testid="stNumberInput"] button {
  background:#25262F!important;color:#FFFFFF!important;
}
.stApp [data-testid="stNumberInput"] button * {color:#FFFFFF!important;}

/* Textos de ayuda, pestañas y paneles claros. */
.stApp [data-testid="stWidgetLabel"] p {color:#294A60!important;}
.stApp [data-testid="stCaptionContainer"] p {color:#587286!important;}
.stApp [data-testid="stTabs"] button {color:#17384D!important;}
.stApp [data-testid="stExpander"] summary,
.stApp [data-testid="stExpander"] summary * {color:#17384D!important;}
.stApp [data-testid="stTextInput"] input,
.stApp [data-testid="stTextArea"] textarea {
  background:#FFFFFF!important;color:#102A43!important;
  -webkit-text-fill-color:#102A43!important;
}

/* Enlace de foco para navegación por teclado: visible en ambos fondos. */
.stApp button:focus-visible,
.stApp input:focus-visible {outline:2px solid #12A5B2!important;outline-offset:2px;}

</style>'''


def configurar_interfaz():
    st.markdown(ESTILOS, unsafe_allow_html=True)


def elegir(modulo):
    st.session_state.modulo = modulo
    st.session_state.pag = 'app'


def inicio():
    st.session_state.pag = 'menu'


def barra_navegacion(modulo=None):
    st.markdown('''<div class="hdr"><div class="logo">≋</div><div>
       <div class="brand">HIDROSA</div>
       <div class="sub">ANÁLISIS, CÁLCULO Y DISEÑO DE CANALES ABIERTOS</div>
       </div><div class="version">EDICIÓN 2.0 · SI</div></div>
       <div class="nav-capa"></div>''', unsafe_allow_html=True)
    c = st.columns([.85,1.3,1.2,1.0,1.48])
    if c[0].button('⌂  Inicio', key='nav_home', use_container_width=True, type='primary' if modulo is None else 'secondary'):
        inicio(); st.rerun()
    for cont, grupo in zip(c[1:], GRUPOS):
        elegidas = [o for o in OPERACIONES if o[3] == grupo]
        actual = any(o[0] == modulo for o in elegidas)
        with cont.popover(('●  ' if actual else '▤  ') + grupo, use_container_width=True):
            st.caption('Selecciona un procedimiento')
            for clave, titulo, desc, _, _ in elegidas:
                if st.button(titulo + ('  ✓' if clave == modulo else ''), key='nav_'+clave, use_container_width=True):
                    elegir(clave); st.rerun()
    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)


def titulo_panel(numero, titulo):
    st.markdown(f'<div class="ficha-titulo"><span>{numero:02}</span>{titulo}</div>', unsafe_allow_html=True)


def menu_principal():
    """Pantalla Inicio: solo el logotipo; la barra de navegación se conserva intacta."""
    from pathlib import Path

    logo = Path(__file__).resolve().parent / 'assets' / 'logo_hidrosa.png'
    _, centro, _ = st.columns([1, 1.8, 1], gap='small')
    with centro:
        st.image(str(logo), use_container_width=True)
