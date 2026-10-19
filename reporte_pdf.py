"""Memoria de cálculo HIDROSA: desarrollo verificable y ordenado, exportado a PDF.

Módulo exclusivamente de presentación. Todos los resultados provienen de
motor_hidraulico.py a través del contexto que entrega app.py.
"""
import io
import math
import os
import re
from datetime import date
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Drawing, Line, PolyLine, Polygon, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)

BASE = os.path.dirname(os.path.abspath(__file__))
try:
    for name, path in (("H-Lato", "Lato-Regular.ttf"),
                       ("H-Lato-Bold", "Lato-Bold.ttf"),
                       ("H-Barlow", "BarlowCondensed-Bold.ttf")):
        pdfmetrics.registerFont(TTFont(name, os.path.join(BASE, "fuentes", path)))
    REG, BOLD, TITLE = "H-Lato", "H-Lato-Bold", "H-Barlow"
except Exception:
    REG, BOLD, TITLE = "Helvetica", "Helvetica-Bold", "Helvetica-Bold"

AZUL = colors.HexColor('#102A43')
CIAN = colors.HexColor('#087E8B')
BLANCO = colors.white
GRIS = colors.HexColor('#536779')
FONDO = colors.HexColor('#F2F7FA')
BORDE = colors.HexColor('#DBE6ED')
RESULT = colors.HexColor('#E8F5F5')

TIT = ParagraphStyle('ht', fontName=TITLE, fontSize=25, leading=27, textColor=BLANCO)
SUB = ParagraphStyle('hs', fontName=REG, fontSize=9, leading=12, textColor=colors.HexColor('#D5EEF0'))
H2 = ParagraphStyle('hh2', fontName=TITLE, fontSize=17, leading=20, textColor=AZUL, spaceBefore=12, spaceAfter=5, keepWithNext=True)
H3 = ParagraphStyle('hh3', fontName=BOLD, fontSize=10.8, leading=15, textColor=CIAN, spaceBefore=7, spaceAfter=4, keepWithNext=True)
TX = ParagraphStyle('htxt', fontName=REG, fontSize=9.1, leading=13.5, textColor=AZUL, spaceAfter=4)
TX_SM = ParagraphStyle('htxtsmall', parent=TX, fontSize=8.2, leading=11.5)
EQ = ParagraphStyle('heq', fontName=REG, fontSize=9.1, leading=14, textColor=AZUL)
KEY = ParagraphStyle('hkey', fontName=BOLD, fontSize=8.5, leading=12, textColor=GRIS)
VAL = ParagraphStyle('hval', fontName=REG, fontSize=8.5, leading=12, textColor=AZUL)
RES = ParagraphStyle('hres', fontName=BOLD, fontSize=9.6, leading=14, textColor=AZUL)
CAP = ParagraphStyle('hcap', fontName=REG, fontSize=8, leading=12, textColor=GRIS)


def pa(t, style=TX):
    return Paragraph(escape(str(t)).replace('\n', '<br/>'), style)


def n(v, d=4):
    """Más decimales en sustituciones para evitar ocultar la precisión."""
    if v is None:
        return '—'
    v = float(v)
    if 0 < abs(v) < 10 ** (-d):
        return f'{v:.7g}'
    return f'{v:.{d}f}'


def xeq(nombre, formula, sustitucion=None, resultado=None):
    """Tabla didáctica: ecuación -> sustitución -> resultado."""
    filas = []
    if formula:
        filas.append((pa('Fórmula', KEY), pa(formula, EQ)))
    if sustitucion:
        filas.append((pa('Sustitución', KEY), pa(sustitucion, EQ)))
    if resultado:
        filas.append((pa('Resultado', KEY), pa(resultado, RES)))
    t = Table([list(f) for f in filas], colWidths=[2.55 * cm, 14.45 * cm], hAlign='LEFT')
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (0, -1), FONDO),
        ('LINEBELOW', (0, 0), (-1, -2), .35, BORDE),
        ('LINEBEFORE', (0, 0), (0, -1), 2, CIAN),
        ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return [pa(nombre, H3), t, Spacer(1, 3)]


def tabla(datos, anchos=None, cabecera=True):
    ancho = sum(anchos) if anchos else 17 * cm
    if anchos is None:
        anchos = [ancho / len(datos[0])] * len(datos[0])
    rows = [[pa(v, KEY if (cabecera and i == 0) else VAL) for v in row] for i, row in enumerate(datos)]
    tb = Table(rows, colWidths=anchos, hAlign='LEFT', repeatRows=1 if cabecera else 0)
    style = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -1), .45, BORDE),
        ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]
    if cabecera:
        style.append(('BACKGROUND', (0, 0), (-1, 0), FONDO))
    for i in range(2 if cabecera else 1, len(rows), 2):
        style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FAFCFD')))
    tb.setStyle(TableStyle(style))
    return tb


def banda_resultado(texto):
    tb = Table([[pa(texto, RES)]], colWidths=[17 * cm], hAlign='LEFT')
    tb.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), RESULT),
        ('LINEBEFORE', (0, 0), (0, 0), 3.5, CIAN),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    return tb


def seccion_dibujo(c, width=442, height=200):
    info = c['dibujo']
    vertices = info.get('linea') or []
    if len(vertices) < 2:
        return pa('No se dispone de geometría para graficar.', CAP)
    xs = [pt[0] for pt in vertices]
    zs = [pt[1] for pt in vertices] + [info['top'], info['nivel']]
    xmin, xmax = min(xs), max(xs)
    zmin, zmax = min(zs), max(zs)
    if xmax <= xmin: xmax = xmin + 1
    if zmax <= zmin: zmax = zmin + 1
    scale = min((width - 60) / (xmax - xmin), (height - 48) / (zmax - zmin))
    to_x = lambda x: 30 + (x - xmin) * scale
    to_y = lambda z: 18 + (z - zmin) * scale
    fig = Drawing(width, height)
    fig.hAlign = 'CENTER'
    for polygon in info.get('agua', []):
        if len(polygon) < 3:
            continue
        fig.add(Polygon([t for point in polygon for t in (to_x(point[0]), to_y(point[1]))],
                        fillColor=colors.HexColor('#A9E1EC'), strokeColor=None))
    fig.add(PolyLine([v for p in vertices for v in (to_x(p[0]), to_y(p[1]))],
                     strokeColor=AZUL, strokeWidth=2.5))
    if zmin <= info['top'] <= zmax:
        guide = Line(to_x(xmin), to_y(info['top']), to_x(xmax), to_y(info['top']),
                     strokeColor=CIAN, strokeWidth=1)
        guide.strokeDashArray = [5, 3]
        fig.add(guide)
    xm = (to_x(xmin) + to_x(xmax)) / 2
    if info['nivel'] > zmin and info['nivel'] < zmax:
        fig.add(String(xm, to_y((zmin + info['nivel'])/2),
                       f"y = {c['y']:.3f} m", textAnchor='middle',
                       fillColor=AZUL, fontName=BOLD, fontSize=9))
    fig.add(String(xm, height - 10, f"H = {c['H']:.3f} m", textAnchor='middle',
                   fillColor=GRIS, fontName=REG, fontSize=8))
    return fig


def generar(c):
    """Construye la memoria sin modificar ni recalcular el motor hidráulico."""
    out = io.BytesIO()
    doc = SimpleDocTemplate(
        out, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.5 * cm, bottomMargin=1.65 * cm,
        title='HIDROSA | Memoria de cálculo hidráulico',
        author='HIDROSA',
    )
    story = []
    section_count = 0
    def h(text):
        nonlocal section_count
        section_count += 1
        text = re.sub(r'^\d+\.\s*', '', text)
        story.append(pa(f'{section_count}. {text}', H2))
        story.append(HRFlowable(width='100%', thickness=.8, color=BORDE, spaceAfter=7))
    def add_eq(name, formula, sustitucion=None, resultado=None):
        story.extend(xeq(name, formula, sustitucion, resultado))
    def info(text):
        story.append(pa(text))

    p = c.get('parametros') or {}
    y, Q, S = c['y'], c['Q'], c['S']
    A, Pm, T, R, V, F = (c[k] for k in ('A', 'P', 'T', 'R', 'V', 'F'))
    ncoef, met, inc, sec = (c[k] for k in ('n', 'metodo', 'inc', 'tipo'))
    b, z, g = p.get('b', 0), p.get('z', 0), 9.81
    tipo_in = {'tirante normal':'Tirante normal (y)', 'caudal':'Caudal (Q)',
               'pendiente':'Pendiente longitudinal (S)', 'tirante crítico':'Tirante crítico (yc)'}.get(inc, inc)

    cab = Table([[pa('HIDROSA', TIT)],
                 [pa('ANÁLISIS, CÁLCULO Y DISEÑO DE CANALES ABIERTOS', SUB)],
                 [pa('MEMORIA DE CÁLCULO   |   ' + c['titulo'], SUB)]], colWidths=[17 * cm])
    cab.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), AZUL),
        ('LINEBELOW', (0, -1), (-1, -1), 3.5, CIAN),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 11),
    ]))
    story += [cab, Spacer(1, 8), pa(f'Fecha de emisión: {date.today():%d/%m/%Y}  |  Unidades: Sistema Internacional (SI)', CAP)]

    # I. Datos de partida: distinguir variables introducidas de incógnitas.
    h('1. Datos de entrada y objetivo')
    filas = [['Concepto', 'Dato o criterio'], ['Operación', c['titulo']],
             ['Tipo de sección', sec], ['Parámetros geométricos', c.get('dims', '').lstrip(', ') or 'Perfil definido geométricamente'],
             ['Método de flujo uniforme', met]]
    if inc not in ('caudal',): filas.append(['Caudal suministrado Q', f'{n(Q, 6)} m³/s'])
    if inc not in ('pendiente', 'tirante crítico'): filas.append(['Pendiente suministrada S', f'{n(S, 7)} m/m = {n(100 * S, 5)} %'])
    if inc not in ('tirante normal', 'tirante crítico'): filas.append(['Tirante suministrado y', f'{n(y, 5)} m'])
    if inc == 'tirante crítico':
        info('La pendiente calculada en este procedimiento corresponde a la pendiente crítica que conduciría el caudal Q con y = yc en flujo uniforme.')
    filas.append(['Variable por determinar', tipo_in])
    story.append(tabla(filas, [7 * cm, 10 * cm]))

    # II. Dimensionamiento si es aplicable.
    if c.get('diseno'):
        d = c['diseno']
        h('2. Dimensionamiento de la sección')
        info('Se aplica la relación geométrica del criterio elegido y se determina el tirante que satisface la ecuación de caudal.')
        add_eq('Relación de diseño', 'b/y = f × (√(1 + z²) − z)',
               f"b/y = {d['f']} × (√(1 + {n(z, 4)}²) − {n(z, 4)}) = {n(d['m'], 6)}")
        add_eq('Ancho de solera resultante', 'b = (b/y) × y',
               f"b = {n(d['m'], 6)} × {n(d['y'], 6)}", f"b = {n(d['b'], 6)} m")
        info('Criterio de diseño: ' + str(d['crit']) + '. El caudal se verifica con la geometría dimensionada.')

    # III. Geometría completa con números.
    h('3. Cálculo de elementos geométricos')
    if sec == 'Rectangular':
        add_eq('Área mojada A', 'A = b × y', f'A = {n(b)} × {n(y)}', f'A = {n(A, 6)} m²')
        add_eq('Perímetro mojado P', 'P = b + 2y', f'P = {n(b)} + 2 × {n(y)}', f'P = {n(Pm, 6)} m')
        add_eq('Espejo de agua T', 'T = b', f'T = {n(b)}', f'T = {n(T, 6)} m')
    elif sec == 'Trapezoidal':
        add_eq('Área mojada A', 'A = y × (b + z×y)',
               f'A = {n(y)} × ({n(b)} + {n(z)} × {n(y)})', f'A = {n(A, 6)} m²')
        add_eq('Perímetro mojado P', 'P = b + 2y×√(1 + z²)',
               f'P = {n(b)} + 2 × {n(y)} × √(1 + {n(z)}²)', f'P = {n(Pm, 6)} m')
        add_eq('Espejo de agua T', 'T = b + 2z×y',
               f'T = {n(b)} + 2 × {n(z)} × {n(y)}', f'T = {n(T, 6)} m')
    elif sec == 'Triangular':
        add_eq('Área mojada A', 'A = z×y²', f'A = {n(z)} × {n(y)}²', f'A = {n(A, 6)} m²')
        add_eq('Perímetro mojado P', 'P = 2y×√(1 + z²)',
               f'P = 2 × {n(y)} × √(1 + {n(z)}²)', f'P = {n(Pm, 6)} m')
        add_eq('Espejo de agua T', 'T = 2z×y', f'T = 2 × {n(z)} × {n(y)}', f'T = {n(T, 6)} m')
    elif sec == 'Circular':
        D = p['D']; theta = 2 * math.acos(max(-1, min(1, 1-2*y/D)))
        add_eq('Ángulo mojado θ', 'θ = 2 arccos(1 − 2y/D)',
               f'θ = 2 arccos(1 − 2 × {n(y, 6)}/{n(D, 6)})', f'θ = {n(theta, 7)} rad')
        add_eq('Área mojada A', 'A = (D²/8) × (θ − sen θ)',
               f'A = ({n(D, 5)}²/8) × ({n(theta, 7)} − sen({n(theta, 7)}))', f'A = {n(A, 6)} m²')
        add_eq('Perímetro mojado P', 'P = D×θ/2',
               f'P = {n(D, 5)} × {n(theta, 7)}/2', f'P = {n(Pm, 6)} m')
        add_eq('Espejo de agua T', 'T = D×sen(θ/2)',
               f'T = {n(D, 5)} × sen({n(theta, 7)}/2)', f'T = {n(T, 6)} m')
    elif sec == 'Parabólica':
        T0, H0 = p['T0'], p['H0']
        x = T/2; a = H0 / (T0/2)**2
        add_eq('Espejo de agua T', 'T = T0 × √(y/H0)',
               f'T = {n(T0, 5)} × √({n(y, 5)}/{n(H0, 5)})', f'T = {n(T, 6)} m')
        add_eq('Área mojada A', 'A = (2/3)×T×y',
               f'A = (2/3) × {n(T, 6)} × {n(y, 6)}', f'A = {n(A, 6)} m²')
        add_eq('Perímetro mojado P', 'P = 2[(x/2)√(1 + 4a²x²) + asenh(2ax)/(4a)]',
               f'x = T/2 = {n(x, 6)} m; a = H0/(T0/2)² = {n(a, 6)} m⁻¹',
               f'P = {n(Pm, 6)} m')
    else:
        info('La sección se construye con los puntos/tramos suministrados. Se suman áreas y longitudes mojadas; el ancho superficial se obtiene de la intersección con el nivel del agua.')
        puntos = p.get('perfil_puntos')
        if puntos:
            story.append(tabla([['Punto', 'X (m)', 'Cota (m)']] + [[str(i), n(px, 5), n(py, 5)] for i, (px, py) in enumerate(puntos, 1)],
                               [3 * cm, 7 * cm, 7 * cm]))
        add_eq('Área mojada A', 'A = suma de áreas mojadas por tramo/subárea',
               'Integración o suma de polígonos bajo el nivel del agua', f'A = {n(A, 6)} m²')
        add_eq('Perímetro mojado P', 'P = suma de longitudes mojadas',
               'Longitud de los segmentos en contacto con el agua', f'P = {n(Pm, 6)} m')
        add_eq('Ancho del espejo T', 'T = suma de anchos de superficie libre',
               'Intersecciones del perfil con la superficie del agua', f'T = {n(T, 6)} m')
    add_eq('Radio hidráulico R', 'R = A/P',
           f'R = {n(A, 6)}/{n(Pm, 6)}', f'R = {n(R, 6)} m')
    add_eq('Profundidad hidráulica Dh', 'Dh = A/T',
           f'Dh = {n(A, 6)}/{n(T, 6)}', f'Dh = {n(A/T, 6)} m')

    # IV. Rugosidad: equivalente o subáreas.
    h('4. Coeficiente de rugosidad')
    if c.get('sub'):
        info('Modelo con división en subáreas. Cada subárea conduce su caudal con su propia geometría y rugosidad. Qtotal = ΣQᵢ.')
        filas = [['Subárea / tramos', 'A (m²)', 'P (m)', 'R (m)', 'n', 'Q (m³/s)']]
        for it in c['sub']:
            filas.append([it['nombre'] + ' - ' + it['tramos'], n(it['A'], 4), n(it['P'], 4),
                          n(it['R'], 5), n(it['n'], 5), n(it['Q'], 6)])
        story.append(tabla(filas, [5.1 * cm, 2.3 * cm, 2.3 * cm, 2.3 * cm, 2 * cm, 3 * cm]))
        add_eq('Caudal total mediante subsecciones', 'Q = ΣQᵢ',
               ' + '.join(n(it['Q'], 6) for it in c['sub']), f'Q = {n(sum(it["Q"] for it in c["sub"]), 6)} m³/s')
        info('El n equivalente que figura en los resultados se presenta como parámetro global de referencia; el caudal se obtiene de la suma de subáreas.')
    else:
        items = c.get('horton') or []
        if items:
            info('Horton-Einstein: combinación de rugosidades ponderadas por el perímetro mojado de cada material.')
            filas = [['Componente', 'Pᵢ (m)', 'nᵢ', 'Pᵢ × nᵢ^(3/2)']]
            for nombre, per, nr in items:
                filas.append([nombre, n(per, 5), n(nr, 5), n(per * nr ** 1.5, 7)])
            story.append(tabla(filas, [6 * cm, 3.1 * cm, 3.1 * cm, 4.8 * cm]))
            tot = sum(per * nr**1.5 for _, per, nr in items)
            per_tot = sum(per for _, per, _ in items)
            add_eq('Rugosidad equivalente', 'nₑ = [Σ(Pᵢ × nᵢ^(3/2))/ΣPᵢ]^(2/3)',
                   f'nₑ = ({n(tot, 8)}/{n(per_tot, 6)})^(2/3)', f'nₑ = {n(c["n_base"], 6)}')
        else:
            info('Un solo material: se toma directamente el coeficiente de rugosidad del formulario.')
            info(f'Material: {c.get("material", "Sin especificar")}. Rugosidad de base n = {n(c["n_base"], 6)}.')
        if c.get('cowan'):
            n0, n1, n2, n3, n4, m5 = c['cowan']
            add_eq('Corrección de Cowan', 'n = (n0 + n1 + n2 + n3 + n4) × m5',
                   f'n = ({n(n0, 5)} + {n(n1, 5)} + {n(n2, 5)} + {n(n3, 5)} + {n(n4, 5)}) × {n(m5, 5)}',
                   f'n = {n(ncoef, 6)}')
    story.append(banda_resultado(f'Rugosidad adoptada: n = {n(ncoef, 6)}  |  {c["origen"]}'))

    # V. Método y resolución de la incógnita.
    h('5. Ecuación hidráulica y resolución')
    pp = p.get('metodo_param', 0)
    if met == 'Manning':
        base_eq = 'Q = (1/n) × A × R^(2/3) × √S'
        term = f'(1/{n(ncoef, 6)}) × {n(A, 6)} × {n(R, 6)}^(2/3) × √{n(S, 8)}'
        desc_c = 'C = R^(1/6)/n (equivalencia entre Manning y Chezy)'
    else:
        base_eq = 'Q = C × A × √(R×S)'
        term = f'{n(c["C"], 6)} × {n(A, 6)} × √({n(R, 6)} × {n(S, 8)})'
        desc_c = {'Chezy': 'C = coeficiente introducido por el usuario',
                  'Bazin': 'C = 87/[1 + γ/√R]',
                  'Ganguillet-Kutter': 'C = [23 + 0.00155/S + 1/n]/[1 + (23 + 0.00155/S)n/√R]'}[met]
    if c.get('sub'):
        formula = ('Qᵢ = (1/nᵢ) × Aᵢ × Rᵢ^(2/3) × √S' if met == 'Manning'
                   else 'Qᵢ = Cᵢ × Aᵢ × √(Rᵢ×S)')
        add_eq('Ecuación por subárea', formula,
               f'S = {n(S, 8)} m/m; Q = ΣQᵢ', f'Q = {n(Q, 6)} m³/s')
        info('Las propiedades Aᵢ, Pᵢ, Rᵢ, nᵢ y Qᵢ se presentan en la tabla de subáreas del paso 4.')
    else:
        if met != 'Manning':
            add_eq('Coeficiente hidráulico C', desc_c,
                   ('γ = ' + n(pp, 6) if met == 'Bazin' else
                    'C ingresado = ' + n(pp, 6) if met == 'Chezy' else
                    f'S = {n(S, 8)}, R = {n(R, 6)}, n = {n(ncoef, 6)}'),
                   f'C = {n(c["C"], 6)}')
        else:
            info(desc_c)
        add_eq(f'Ley de {met}', base_eq, f'Q = {term}', f'Q = {n(Q, 6)} m³/s')

    if inc == 'tirante normal':
        info('Se resuelve iterativamente f(y) = Qcalculado(y) − Qdato = 0, actualizando A(y), P(y), R(y) y n(y) en cada iteración. Método: bisección.')
        add_eq('Condición de convergencia', 'Qcalculado(y) = Qdato',
               f'Qcalculado({n(y, 7)} m) = {n(Q, 6)} m³/s', f'y = {n(y, 7)} m')
        its = p.get('iteraciones') or []
        if its:
            info(f'Bisección: {len(its)} iteraciones. El error indicado es la amplitud del intervalo de búsqueda antes de cada actualización (m).')
            filas = [['Iteración', 'y ensayado (m)', 'Intervalo (m)']]
            for k in its:
                filas.append([str(k['i']), n(k['y'], 7), n(k['error'], 7)])
            story.append(tabla(filas, [3.5 * cm, 7 * cm, 6.5 * cm]))
    elif inc == 'pendiente' or (inc == 'tirante crítico'):
        if met == 'Manning' and not c.get('sub'):
            add_eq('Despeje de pendiente (Manning)', 'S = [Q×n/(A×R^(2/3))]²',
                   f'S = [{n(Q, 6)} × {n(ncoef, 6)}/({n(A, 6)} × {n(R, 6)}^(2/3))]²',
                   f'{"Pendiente crítica Sc" if inc == "tirante crítico" else "Pendiente S"} = {n(S, 8)} m/m = {n(100*S, 6)} %')
        else:
            info('Pendiente obtenida numéricamente al imponer Qcalculado(S) = Qdato, por bisección.')
            add_eq('Ecuación de cierre', 'f(S) = Qcalculado(S) − Qdato = 0',
                   f'Qcalculado({n(S, 8)}) = {n(Q, 6)} m³/s', f'S = {n(S, 8)} m/m = {n(100*S, 6)} %')
    elif inc == 'caudal':
        story.append(banda_resultado(f'Caudal calculado con el tirante y la pendiente proporcionados: Q = {n(Q, 6)} m³/s'))
    if c.get('diseno'):
        info('En diseño de sección, el tirante y la solera se obtienen resolviendo la ecuación de caudal con la relación b/y impuesta por el criterio geométrico.')

    # VI. Velocidad y Froude, explícitamente ligados a Q(S) cuando corresponda.
    h('6. Velocidad y número de Froude')
    add_eq('Velocidad media V', 'V = Q/A',
           f'V = {n(Q, 6)}/{n(A, 6)}', f'V = {n(V, 6)} m/s')
    add_eq('Número de Froude Fr', 'Fr = V/√(g × Dh), con Dh = A/T',
           f'Fr = {n(V, 6)}/√(9.81 × {n(A/T, 6)})', f'Fr = {n(F, 6)}  →  Régimen {c["reg"].lower()}')
    if inc in ('caudal', 'tirante normal'):
        info(f'La pendiente S = {n(S, 8)} m/m interviene en el cálculo de Q con {met}; el número de Froude utiliza la velocidad resultante y la profundidad hidráulica.')
    info('Interpretación: Fr &lt; 1 = subcrítico; Fr = 1 = crítico; Fr &gt; 1 = supercrítico.'.replace('&lt;', '<').replace('&gt;', '>'))

    # VII. Estado crítico y energía específica.
    h('7. Estado crítico y energía específica')
    yc, Ac, Tc = c['yc'], p.get('Ac'), p.get('Tc')
    add_eq('Criterio de flujo crítico', 'Q²/g = Ac³/Tc',
           f'Q²/g = {n(Q, 6)}²/9.81 = {n(Q**2/g, 7)} m⁵;   Ac³/Tc = {n(Ac, 6)}³/{n(Tc, 6)} = {n(Ac**3/Tc, 7)} m⁵' if Ac and Tc else None,
           f'Tirante crítico yc = {n(yc, 7)} m')
    if inc == 'tirante crítico':
        info('En este procedimiento se ha utilizado y = yc para obtener la pendiente crítica Sc mediante la ecuación de flujo uniforme.')
    if c.get('energia'):
        add_eq('Energía específica E', 'E = y + V²/(2g)',
               f'E = {n(y, 6)} + {n(V, 6)}²/(2 × 9.81)', f'E = {n(c["E"], 7)} m')
        add_eq('Energía mínima Ec', 'Ec = yc + (Q/Ac)²/(2g)',
               f'Ec = {n(yc, 6)} + ({n(Q, 6)}/{n(Ac, 6)})²/(2 × 9.81)' if Ac else None,
               f'Ec = {n(c["Ec"], 7)} m')
        if c.get('y2') is None:
            info('No se encuentra tirante alterno dentro de la altura disponible de esta geometría.')
        else:
            add_eq('Tirante alterno', 'E(y₂) = E(y₁)',
                   f'E({n(c["y2"], 6)}) = E({n(y, 6)}) = {n(c["E"], 6)} m',
                   f'y₂ = {n(c["y2"], 7)} m')

    # VIII. Comprobaciones.
    h('8. Verificaciones y borde libre')
    add_eq('Verificación de velocidad', 'Vmin ≤ V ≤ Vmax',
           f'{n(c["vmin"], 3)} ≤ {n(V, 6)} ≤ {n(c["vmax"], 3)} m/s', c['msg_v'])
    info(f'Método de borde libre: {c["metodo_bl"]}. {c["crit"]}')
    metodo_bl = c['metodo_bl']
    if metodo_bl.startswith('Máximo'):
        divisor = 5 if 'y/5' in c['bl_formula'] else 3
        bl_eq, bl_num = f'BL = y/{divisor}', f'BL = {n(y, 6)}/{divisor}'
    elif metodo_bl.startswith('USBR'):
        Cbl = c['BL']**2/y
        bl_eq, bl_num = 'BL = √(C×y)', f'BL = √({n(Cbl, 5)} × {n(y, 6)})'
    elif metodo_bl == 'Valor manual':
        bl_eq, bl_num = 'BL = valor especificado', f'BL = {n(c["BL"], 6)} m (dato)'
    else:
        bl_eq, bl_num = 'BL = valor de la tabla según el criterio seleccionado',                         f'Para Q = {n(Q, 6)} m³/s, se adopta BL = {n(c["BL"], 6)} m'
    add_eq('Borde libre requerido BL', bl_eq, bl_num, f'BL = {n(c["BL"], 6)} m')
    if c.get('altura') is not None:
        disponible = c['altura'] - y
        add_eq('Borde libre disponible', 'BLdisponible = Haltura − y',
               f'BLdisponible = {n(c["altura"], 6)} − {n(y, 6)}',
               f'BLdisponible = {n(disponible, 6)} m; '+ ('CUMPLE' if disponible >= c['BL'] - 1e-9 else 'NO CUMPLE'))
    else:
        add_eq('Altura hidráulica estimada', 'H = y + BL',
               f'H = {n(y, 6)} + {n(c["BL"], 6)}', f'H = {n(c["H"], 6)} m')
    if c.get('aviso'):
        story.append(banda_resultado('Observación: ' + c['aviso']))

    # IX. Resumen y dibujo de la sección.
    h('9. Resumen de resultados')
    rows = [['Parámetro', 'Valor']]
    for nombre, valores in c['grupos']:
        rows.append([nombre.upper(), ''])
        rows.extend([[key, str(value)] for key, value in valores])
    story.append(tabla(rows, [9 * cm, 8 * cm]))
    h('10. Esquema de la sección hidráulica')
    story.append(seccion_dibujo(c))
    story.append(pa('Esquema referencial de geometría y nivel del agua. Para dimensiones exactas, consultar los resultados numéricos.', CAP))

    def footer(canvas, pdf_doc):
        canvas.saveState()
        canvas.setStrokeColor(BORDE)
        canvas.line(2 * cm, 1.42 * cm, 19 * cm, 1.42 * cm)
        canvas.setFont(REG, 8)
        canvas.setFillColor(GRIS)
        canvas.drawString(2 * cm, 1.05 * cm, 'HIDROSA  |  Memoria de cálculo hidráulico')
        canvas.drawRightString(19 * cm, 1.05 * cm, f'Página {pdf_doc.page}')
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out.getvalue()
