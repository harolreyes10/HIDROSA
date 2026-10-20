import math
from html import escape
import pandas as pd
import plotly.graph_objects as go
import modulo_energia
import reporte_pdf
import streamlit as st
import motor_hidraulico as mh

from interfaz_nueva import configurar_interfaz, barra_navegacion, titulo_panel, menu_principal, OPERACIONES
from guia_uso import mostrar_guia_uso

st.set_page_config(page_title="HIDROSA | Hidráulica", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")
MAR, ORO, TUR = "#102A43", "#F59E0B", "#12A5B2"
configurar_interfaz()

# Tablas de referencia y comparación: solo presentación (sin cambios en el motor).
ESTILO_TABLAS = """<style>
.hd-tabla-wrap {width:100%;max-width:100%;overflow-x:auto;border:1px solid #D6E5ED;
  border-radius:12px;background:#FFFFFF;margin:10px 0 14px;
  box-shadow:0 3px 14px rgba(16,42,67,.045);}
.hd-tabla-wrap table.cw.hd-tabla {width:100%;min-width:440px;table-layout:fixed;
  border-collapse:separate;border-spacing:0;font-size:13px;line-height:1.42;}
.hd-tabla-wrap .hd-tabla thead th {padding:11px 10px;background:#14364C;color:#fff;
  font-size:12px;letter-spacing:.015em;text-align:left;font-weight:700;
  vertical-align:middle;border:0;white-space:normal;}
.hd-tabla-wrap .hd-tabla thead th:first-child{padding-left:14px}
.hd-tabla-wrap .hd-tabla td {padding:10px 10px;border:0;border-bottom:1px solid #E8EFF3;
  color:#243F52;vertical-align:middle;overflow-wrap:break-word;background:#fff;}
.hd-tabla-wrap .hd-tabla tr:last-child td{border-bottom:0}
.hd-tabla-wrap .hd-tabla tbody tr:hover>td:not(.g){background:#F5FAFC}
.hd-tabla-wrap .hd-tabla td.g{background:#F0F6F8!important;font-weight:750;
  color:#17374A;border-right:1px solid #DFEAF0;vertical-align:middle;padding:12px 14px;}
.hd-tabla-wrap .hd-tabla td.f {text-align:center;font-weight:700;background:#FAFCFD;
  border-right:1px solid #E8EFF3;}
.hd-tabla-wrap .hd-tabla .hd-factor {display:inline-block;font-weight:750;
  border:1px solid #C8E7E8;background:#E9F7F7;color:#086873;border-radius:6px;
  padding:3px 7px;white-space:nowrap;}
.hd-tabla-wrap .hd-tabla td.v {text-align:right;font-weight:750;font-variant-numeric:tabular-nums;
  color:#116C78;white-space:normal;}
.hd-tabla-wrap .hd-tabla tr.hd-inicio>td {border-top:2px solid #CEDFE6;}
.hd-tabla-wrap .hd-tabla tr.hd-inicio:first-child>td {border-top:0}
.hd-tabla-wrap .hd-tabla td.na{color:#73899B;font-weight:500;font-size:12px;text-align:center}
.hd-tabla-wrap .hd-tabla .hd-no-aplica{font-weight:500;color:#73899B}
.hd-tabla-wrap .hd-tabla .hd-unidad{display:block;color:#CAE2ED;font-weight:500;
  font-size:10px;line-height:1.2;margin-top:2px;}
.hd-tabla-wrap .hd-tabla.hd-cowan col:nth-child(1){width:34%}
.hd-tabla-wrap .hd-tabla.hd-cowan col:nth-child(2){width:11%}
.hd-tabla-wrap .hd-tabla.hd-cowan col:nth-child(3){width:35%}
.hd-tabla-wrap .hd-tabla.hd-cowan col:nth-child(4){width:20%}
.hd-tabla-wrap .hd-tabla.hd-referencia col:nth-child(1){width:36%}
.hd-tabla-wrap .hd-tabla.hd-referencia col:nth-child(2){width:35%}
.hd-tabla-wrap .hd-tabla.hd-referencia col:nth-child(3){width:29%}
.hd-tabla-wrap .hd-tabla.hd-comparacion{min-width:480px;font-size:12.5px;}
.hd-tabla-wrap .hd-tabla.hd-comparacion col:nth-child(1){width:29%}
.hd-tabla-wrap .hd-tabla.hd-comparacion col:nth-child(2){width:13%}
.hd-tabla-wrap .hd-tabla.hd-comparacion col:nth-child(3){width:17%}
.hd-tabla-wrap .hd-tabla.hd-comparacion col:nth-child(4){width:41%}
.hd-tabla-wrap .hd-tabla.hd-comparacion tbody tr:nth-child(even):not(.sel)>td{background:#FAFCFD}
.hd-tabla-wrap .hd-tabla.hd-comparacion tbody tr.sel>td {
  background:#E5F6F5!important;color:#123B48;font-weight:700;
  border-bottom:1px solid #BDE1DF;}
.hd-tabla-wrap .hd-tabla.hd-comparacion tbody tr.sel>td:first-child {
  box-shadow:inset 4px 0 #087E8B;}
.hd-tabla-wrap .hd-tabla .hd-elegido {display:inline-block;background:#087E8B;color:#fff;
  border-radius:5px;font-size:10px;line-height:1.2;font-weight:700;
  padding:3px 6px;margin:3px 0 0;white-space:nowrap;}
@media(max-width:600px){.hd-tabla-wrap .hd-tabla thead th{font-size:11px;padding:9px 8px}
  .hd-tabla-wrap .hd-tabla td{font-size:12px;padding:8px 8px}}

/* HIDROSA: lectura por factor, sin celdas combinadas ni columnas estrechas. */
.hd-cowan-grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,270px),1fr));gap:13px;
  margin:9px 0 17px;align-items:stretch;}
.hd-cowan-card {background:#FFFFFF;border:1px solid #CEDDE6;border-radius:12px;
  overflow:hidden;box-shadow:0 3px 14px rgba(15,43,65,.045);min-width:0;}
.hd-cowan-head {display:flex;gap:10px;align-items:center;background:#E8F3F7;
  border-bottom:1px solid #CCDFE8;padding:11px 13px;}
.hd-cowan-tag {display:inline-flex;align-items:center;justify-content:center;min-width:44px;
  padding:5px 10px;border-radius:7px;color:white;background:#0B6178;font-weight:850;font-size:15px;}
.hd-cowan-name {font-weight:780;font-size:12.5px;line-height:1.35;color:#12344C;}
.hd-cowan-tbl {width:100%;border-collapse:collapse;font-size:12.4px;table-layout:auto;}
.hd-cowan-tbl th {font-size:10.5px;font-weight:700;text-transform:uppercase;letter-spacing:.045em;
  color:#6B8093;background:#F6FAFC;text-align:left;padding:7px 12px;border-bottom:1px solid #E2EDF2;}
.hd-cowan-tbl th:last-child {text-align:right;}
.hd-cowan-tbl td {padding:10px 12px;vertical-align:middle;border-bottom:1px solid #EAF0F4;
  color:#203E52;overflow-wrap:break-word;}
.hd-cowan-tbl tr:last-child td{border-bottom:none;}
.hd-cowan-tbl tr:nth-child(even) td{background:#F9FBFC;}
.hd-cowan-tbl td:last-child{color:#056B83;text-align:right;white-space:nowrap;
  font-weight:800;font-variant-numeric:tabular-nums;}
.hd-bl-cards {display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:12px;margin:10px 0 14px;}
.hd-bl-card {min-width:0;border:1px solid #D6E4ED;background:#FFFFFF;border-radius:12px;
  box-shadow:0 2px 12px rgba(16,42,67,.045);overflow:hidden;}
.hd-bl-card.selected {border:2px solid #0A91A6;box-shadow:0 0 0 2px #E2F6F9;}
.hd-bl-head{display:flex;gap:6px;align-items:flex-start;justify-content:space-between;
  background:#F1F7FA;padding:11px 12px;min-height:54px;}
.hd-bl-card.selected .hd-bl-head{background:#E1F5F7;}
.hd-bl-name {font-size:12.5px;line-height:1.35;color:#16394F;font-weight:790;}
.hd-bl-mark {display:inline-flex;background:#087E8B;border-radius:5px;padding:4px 7px;
  font-weight:800;color:white;font-size:10px;white-space:nowrap;}
.hd-bl-metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;padding:11px 12px 9px;}
.hd-bl-metric{border:1px solid #E2EAF0;border-radius:8px;padding:8px 9px;background:white;}
.hd-bl-lbl{font-size:10.5px;font-weight:650;color:#678090;display:block;margin-bottom:4px;}
.hd-bl-val{color:#0E607B;font-size:17px;line-height:1.2;font-weight:820;
  font-variant-numeric:tabular-nums;overflow-wrap:anywhere;}
.hd-bl-val.na{color:#8497A3;font-size:13px;}
.hd-bl-criterio{border-top:1px solid #E6EDF1;padding:9px 12px 11px;color:#4E6979;
  font-size:11.7px;line-height:1.48;overflow-wrap:break-word;}
.hd-bl-criterio b{color:#203F53;}
@media(max-width:760px){.hd-cowan-grid,.hd-bl-cards{grid-template-columns:minmax(0,1fr);}}
</style>"""
st.markdown(ESTILO_TABLAS, unsafe_allow_html=True)


def _tabla_cabecera(clase, anchos, etiquetas):
    colgroup = "<colgroup>" + "<col>" * anchos + "</colgroup>"
    cols = "".join(f"<th scope='col'>{escape(t)}</th>" for t in etiquetas)
    return f"<div class='hd-tabla-wrap'><table class='cw hd-tabla {clase}'>{colgroup}<thead><tr>{cols}</tr></thead><tbody>"


def tabla_cowan():
    """Presentación por bloques de los factores de Cowan, sin alterar la tabla fuente."""
    bloques = []
    for grupo, factor, items in mh.TABLA_COWAN:
        filas = "".join(
            f"<tr><td>{escape(cond)}</td><td>{escape(val)}</td></tr>"
            for cond, val in items
        )
        bloques.append(
            "<section class='hd-cowan-card'>"
            "<div class='hd-cowan-head'>"
            f"<span class='hd-cowan-tag'>{escape(factor)}</span>"
            f"<span class='hd-cowan-name'>{escape(grupo)}</span></div>"
            "<table class='hd-cowan-tbl'><thead><tr>"
            "<th scope='col'>Condición</th><th scope='col'>Valor de referencia</th>"
            f"</tr></thead><tbody>{filas}</tbody></table></section>"
        )
    return "<div class='hd-cowan-grid'>" + "".join(bloques) + "</div>"


CONFIG = {"scrollZoom": True, "displaylogo": False, "modeBarButtonsToRemove": ["zoom2d", "select2d", "lasso2d"]}


def dibujar(s, y, H, mats, ns=None):
    """Sección simple dibujada por nodos, con relleno celeste del agua."""
    hb, z = s.b / 2, s.z
    if s.tipo == "Rectangular":
        pts = [(-hb, H), (-hb, 0.0), (hb, 0.0), (hb, H)]
        agua = [(-hb, y), (-hb, 0.0), (hb, 0.0), (hb, y)]
    elif s.tipo == "Triangular":
        hw = z * y
        xl = z * H
        pts = [(-xl, H), (0.0, 0.0), (xl, H)]
        agua = [(-hw, y), (0.0, 0.0), (hw, y)]
    else:  # Trapezoidal
        hw = hb + z * y
        xl = hb + z * H
        pts = [(-xl, H), (-hb, 0.0), (hb, 0.0), (xl, H)]
        agua = [(-hw, y), (-hb, 0.0), (hb, 0.0), (hw, y)]

    xs = [q[0] for q in pts]
    zs = [q[1] for q in pts]
    x0, x1 = min(xs), max(xs)
    ancho = max(x1 - x0, 1e-6)
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[q[0] for q in agua] + [agua[0][0]],
        y=[q[1] for q in agua] + [agua[0][1]],
        fill="toself", mode="lines",
        fillcolor="rgba(79,179,169,.40)",
        line=dict(color="#008DC0", width=2.0),
        hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=xs, y=zs, mode="lines", line=dict(color=MAR, width=2.6),
        hoverinfo="skip", showlegend=False,
    ))

    nodos = pts
    etiquetas = [f"P{i}" for i in range(1, len(nodos) + 1)]
    centro = (x0 + x1) / 2
    posiciones = []
    for x, zz in nodos:
        if zz <= 1e-9:
            posiciones.append("bottom left" if x < centro else "bottom right")
        elif x < centro - .08 * ancho:
            posiciones.append("top left")
        elif x > centro + .08 * ancho:
            posiciones.append("top right")
        else:
            posiciones.append("top center")
    fig.add_trace(go.Scatter(
        x=[q[0] for q in nodos], y=[q[1] for q in nodos],
        mode="markers+text", text=etiquetas, textposition=posiciones,
        textfont=dict(color=MAR, size=11), marker=dict(color=MAR, size=8),
        hoverinfo="skip", showlegend=False,
    ))

    gris = "#718096"
    fig.add_trace(go.Scatter(
        x=[x0, x1], y=[H, H], mode="lines",
        line=dict(color=gris, width=1.2, dash="dash"), hoverinfo="skip", showlegend=False,
    ))
    xagua0 = min(q[0] for q in agua if abs(q[1] - y) < 1e-9)
    xagua1 = max(q[0] for q in agua if abs(q[1] - y) < 1e-9)
    fig.add_trace(go.Scatter(
        x=[xagua0, xagua1], y=[y, y], mode="lines",
        line=dict(color="#008DC0", width=3.2), hoverinfo="skip", showlegend=False,
    ))
    fig.add_annotation(x=(xagua0 + xagua1) / 2, y=y, text="Nivel de agua", showarrow=False,
                       yshift=-16, font=dict(color="#00739B", size=11), bgcolor="rgba(255,255,255,0.9)")
    fig.add_annotation(x=(xagua0 + xagua1) / 2, y=y, text=f"T = {s.T(y):.3f} m", showarrow=False,
                       yshift=13, font=dict(color=MAR, size=12), bgcolor="rgba(255,255,255,.85)")
    xd = x1 + .055 * ancho
    fig.add_shape(type="line", x0=xd, x1=xd, y0=0.0, y1=y, line=dict(color=MAR, width=1.3))
    for zp in (y, 0.0):
        fig.add_annotation(x=xd, y=zp, ax=xd, ay=y / 2, axref="x", ayref="y", text="", showarrow=True,
                           arrowhead=2, arrowsize=1, arrowwidth=1.3, arrowcolor=MAR)
    fig.add_annotation(x=xd, y=y / 2, text=f"y = {y:.3f} m", showarrow=False,
                       xanchor="left", xshift=7, font=dict(color=MAR, size=12))
    fig.add_annotation(x=x1, y=H, text=f"y + BL = {H:.3f} m", showarrow=False,
                       xanchor="left", xshift=6, font=dict(color=MAR, size=11))
    fig.add_annotation(x=x0, y=H, text=f"Altura de la sección = {H:.3f} m", showarrow=False,
                       xanchor="left", yshift=12, font=dict(color=MAR, size=11))
    if s.tipo != "Triangular" and s.b > 0:
        fig.add_annotation(x=0, y=0.0, text=f"b = {s.b:.3f} m", showarrow=False,
                           yshift=-20, font=dict(color=MAR, size=11), bgcolor="rgba(255,255,255,.85)")

    fig.update_layout(title="Visualización dinámica de la sección", height=500,
                      plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)",
                      showlegend=False, dragmode="pan", margin=dict(l=40, r=60, t=60, b=50),
                      font=dict(color=MAR),
                      xaxis=dict(title="Distancia horizontal (m)", gridcolor="#E4EBF1"),
                      yaxis=dict(title="Elevación (m)", gridcolor="#E4EBF1", scaleanchor="x"))
    return fig


if "pag" not in st.session_state:
    st.session_state.pag = "menu"
    st.session_state.modulo = None

# ---------------- Portada ----------------
def _recortar_banda(poly, za, zb):
    """Parte de un polígono convexo con za <= z <= zb."""
    if math.isfinite(zb): poly = _recortar(poly, zb)
    if math.isfinite(za) and len(poly) >= 3:
        poly = [(x, -z) for x, z in _recortar([(x, -z) for x, z in poly], -za)]
    return poly


def _tira(s, i, L):
    (x1, z1), (x2, z2) = s.pts[i], s.pts[i + 1]
    if min(z1, z2) >= L: return None
    a, b_ = (x1, z1), (x2, z2)
    if z1 > L: a = (x1 + (L - z1) / (z2 - z1) * (x2 - x1), L)
    if z2 > L: b_ = (x1 + (L - z1) / (z2 - z1) * (x2 - x1), L)
    return [a, b_, (b_[0], L), (a[0], L)]


def dibujar_poli(s, y, H, ns=None, indices_nodo=None):
    """Dibujo nodal: contorno por nodos, nivel de agua y relleno celeste."""
    # Se emplea la geometría original: no se modifican los puntos de cálculo.
    pts = s.pts
    xs = [p[0] for p in pts]
    zs = [p[1] for p in pts]
    L = s.zmin + y
    top = s.zmin + H
    x0, x1 = xs[0], xs[-1]
    ancho = max(x1 - x0, 1e-6)
    fig = go.Figure()

    # Contorno del canal: un solo trazo fino (sin colores ni etiquetas T1, T2...).
    fig.add_trace(go.Scatter(
        x=xs, y=zs, mode="lines", line=dict(color=MAR, width=2.6),
        hoverinfo="skip", showlegend=False,
    ))

    # Los arcos y las parábolas se discretizan internamente para calcular.
    # Al dibujar, solo se rotulan los extremos y las uniones de tramos reales.
    if indices_nodo is None:
        indices_nodo = range(len(pts))
    ids = sorted({int(k) for k in indices_nodo if 0 <= int(k) < len(pts)} | {0, len(pts) - 1})
    nodos = [pts[k] for k in ids]
    etiquetas = [f"P{i}" for i in range(1, len(nodos) + 1)]
    zspan = max(zs) - min(zs)
    centro = (x0 + x1) / 2
    posiciones = []
    for x, z in nodos:
        # Mantiene los rótulos fuera del perfil siempre que es posible.
        if z <= s.zmin + max(zspan * .04, 1e-6):
            posiciones.append("bottom left" if x < centro else "bottom right")
        elif x < centro - .08 * ancho:
            posiciones.append("top left")
        elif x > centro + .08 * ancho:
            posiciones.append("top right")
        else:
            posiciones.append("top center")
    fig.add_trace(go.Scatter(
        x=[p[0] for p in nodos], y=[p[1] for p in nodos],
        mode="markers+text", text=etiquetas, textposition=posiciones,
        textfont=dict(color=MAR, size=11 if len(nodos) <= 22 else 9),
        marker=dict(color=MAR, size=8 if len(nodos) <= 22 else 6),
        customdata=[[f"({p[0]:.3f}, {p[1]:.3f})"] for p in nodos],
        hovertemplate="%{text}: %{customdata[0]} m<extra></extra>",
        showlegend=False,
    ))

    # Marcas de cotas: conservan la información hidráulica del gráfico anterior.
    gris = "#718096"
    fig.add_trace(go.Scatter(
        x=[x0, x1], y=[top, top], mode="lines",
        line=dict(color=gris, width=1.2, dash="dash"),
        hoverinfo="skip", showlegend=False,
    ))
    # Superficie libre del agua y relleno celeste.
    # Se obtiene el polígono sumergido recortando el perfil por debajo de la cota L.
    tol_nivel = max(1e-10, (max(zs) - min(zs)) * 1e-10)
    agua_pts = []
    for (xa, za), (xb, zb) in zip(pts[:-1], pts[1:]):
        a_dentro = za <= L + tol_nivel
        b_dentro = zb <= L + tol_nivel
        if a_dentro:
            if not agua_pts or abs(agua_pts[-1][0] - xa) > tol_nivel or abs(agua_pts[-1][1] - za) > tol_nivel:
                agua_pts.append((xa, za))
        if a_dentro != b_dentro:
            fraccion = 0.0 if abs(zb - za) <= tol_nivel else (L - za) / (zb - za)
            fraccion = min(1.0, max(0.0, fraccion))
            xi = xa + fraccion * (xb - xa)
            agua_pts.append((xi, L))
    if len(agua_pts) >= 2:
        xagua0, xagua1 = agua_pts[0][0], agua_pts[-1][0]
        poligono_agua = list(agua_pts)
        if abs(poligono_agua[-1][1] - L) > tol_nivel:
            poligono_agua.append((xagua1, L))
        poligono_agua.append((xagua0, L))
        fig.add_trace(go.Scatter(
            x=[p[0] for p in poligono_agua], y=[p[1] for p in poligono_agua],
            fill="toself", mode="lines", fillcolor="rgba(79,179,169,.40)",
            line=dict(color="#008DC0", width=1.8), hoverinfo="skip", showlegend=False,
        ))
        if abs(xagua1 - xagua0) > 1e-10:
            fig.add_trace(go.Scatter(
                x=[xagua0, xagua1], y=[L, L], mode="lines",
                line=dict(color="#008DC0", width=3.3),
                hoverinfo="skip", showlegend=False,
            ))
            fig.add_annotation(
                x=(xagua0 + xagua1) / 2, y=L, text="Nivel de agua",
                showarrow=False, yshift=-16,
                font=dict(color="#00739B", size=11),
                bgcolor="rgba(255,255,255,0.9)",
            )
    fig.add_annotation(
        x=centro, y=L, text=f"T = {s.T(y):.3f} m", showarrow=False,
        yshift=13, font=dict(color=MAR, size=12), bgcolor="rgba(255,255,255,.85)",
    )
    xd = x1 + .055 * ancho
    fig.add_shape(type="line", x0=xd, x1=xd, y0=s.zmin, y1=L,
                  line=dict(color=MAR, width=1.3))
    for zp in (L, s.zmin):
        fig.add_annotation(x=xd, y=zp, ax=xd, ay=s.zmin + y / 2,
                           axref="x", ayref="y", text="", showarrow=True,
                           arrowhead=2, arrowsize=1, arrowwidth=1.3, arrowcolor=MAR)
    fig.add_annotation(x=xd, y=s.zmin + y / 2,
                       text=f"y = {y:.3f} m", showarrow=False,
                       xanchor="left", xshift=7, font=dict(color=MAR, size=12))
    fig.add_annotation(x=x1, y=top, text=f"y + BL = {H:.3f} m",
                       showarrow=False, xanchor="left", xshift=6,
                       font=dict(color=MAR, size=11))
    ztop = min(pts[0][1], pts[-1][1])
    fig.add_trace(go.Scatter(
        x=[x0, x1], y=[ztop, ztop], mode="lines",
        line=dict(color=gris, width=1.1, dash="dot"),
        hoverinfo="skip", showlegend=False,
    ))
    fig.add_annotation(x=x0, y=ztop,
                       text=f"Altura de la sección = {s.altura:.3f} m",
                       showarrow=False, xanchor="left", yshift=12,
                       font=dict(color=MAR, size=11))
    fig.update_layout(
        title="Visualización dinámica de la sección", height=500,
        plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False, dragmode="pan",
        margin=dict(l=40, r=60, t=60, b=50), font=dict(color=MAR),
        xaxis=dict(title="Distancia horizontal (m)", gridcolor="#E4EBF1"),
        yaxis=dict(title="Elevación (m)", gridcolor="#E4EBF1", scaleanchor="x"),
    )
    return fig


TABLA_BL = [
    ("Máximo Villón (por tirante)", [("Canal sin revestir", "y/3"), ("Canal revestido", "y/5")]),
    ("USBR (Bureau of Reclamation)", [("Q ≤ 0.6 m³/s", "√(0.46·y)"), ("Q ≤ 85 m³/s", "√(0.76·y)")]),
    ("Villón por caudal", [("Q ≤ 0.5 m³/s", "0.30 m"), ("Q > 0.5 m³/s", "0.40 m")]),
    ("Villón por ancho de solera", [("b ≤ 0.8 m", "0.40 m"), ("0.8 < b ≤ 1.5 m", "0.50 m"), ("1.5 < b ≤ 3.0 m", "0.60 m"), ("3.0 < b ≤ 20 m", "1.00 m")]),
    ("ANA, Tabla 11 (por caudal)", [("Q ≤ 0.05 m³/s", "Revestido 0.075 m  /  Sin revestir 0.10 m"), ("0.05 < Q ≤ 0.25", "Revestido 0.10 m  /  Sin revestir 0.20 m"),
                                    ("0.25 < Q ≤ 0.50", "Revestido 0.20 m  /  Sin revestir 0.40 m"), ("0.50 < Q ≤ 1.00", "Revestido 0.25 m  /  Sin revestir 0.50 m"),
                                    ("Q > 1.00 m³/s", "Revestido 0.30 m  /  Sin revestir 0.60 m")]),
]


def tabla_bl():
    """Tabla guía de borde libre: mismo contenido, formato compacto y adaptable."""
    filas = []
    for grupo, items in TABLA_BL:
        for i, (cond, val) in enumerate(items):
            inicio = " class='hd-inicio'" if i == 0 else ""
            grupo_ = f"<td class='g' rowspan='{len(items)}'>{escape(grupo)}</td>" if i == 0 else ""
            filas.append(f"<tr{inicio}>{grupo_}<td>{escape(cond)}</td><td class='v'>{escape(val)}</td></tr>")
    return (_tabla_cabecera("hd-referencia", 3, ("Método", "Condición", "Borde libre"))
            + "".join(filas) + "</tbody></table></div>")


TIPOS_TRAMO = ["Vertical", "Talud", "Horizontal", "Arco circular", "Parábola (fondo)", "Recta (longitud y ángulo)"]
DEF_TRAMO = {"Vertical": (1.0, 0.0), "Talud": (1.0, 1.0), "Horizontal": (1.0, 0.0), "Arco circular": (0.5, 180.0), "Parábola (fondo)": (1.0, 0.3), "Recta (longitud y ángulo)": (1.0, 0.0)}


def construir_tramos(filas):
    """Convierte los tramos (vertical, talud, horizontal, arco, parábola o recta) en los puntos de una poligonal."""
    pts, ms, ns_, junc, seg_tr, errs = [(0.0, 0.0)], [], [], [], [], []
    for t, r in enumerate(filas, 1):
        x, y = pts[-1]; tp, a, b = r["tp"], r["a"], r["b"]; sg = -1 if r.get("sent", "Desciende") == "Desciende" else 1
        if tp == "Vertical": nuevos = [(x, y + sg * a)]
        elif tp == "Talud": nuevos = [(x + b * a, y + sg * a)]
        elif tp == "Horizontal": nuevos = [(x + a, y)]
        elif tp == "Recta (longitud y ángulo)": nuevos = [(x + a * math.cos(math.radians(b)), y + a * math.sin(math.radians(b)))]
        elif tp == "Arco circular":
            conc = r.get("forma", "Cóncavo (fondo)").startswith("Cónc")
            t0, ph = (-b / 2, b) if conc else (b / 2, -b)       # cóncavo: parte bajando y termina subiendo
            N, sgn = max(6, int(b / 6) + 1), (1 if ph >= 0 else -1)
            nuevos = []
            for k in range(1, N + 1):
                a_ = math.radians(t0 + ph * k / N)
                nuevos.append((x + sgn * a * (math.sin(a_) - math.sin(math.radians(t0))), y - sgn * a * (math.cos(a_) - math.cos(math.radians(t0)))))
        else:                                                    # parábola de fondo: ancho total a, profundidad b
            nuevos = [(x + a * k / 24, y - b + b * (2 * k / 24 - 1) ** 2) for k in range(1, 25)]
        for q in nuevos:
            pts.append(q); ms.append(r["mat"]); ns_.append(r["n"]); seg_tr.append(t)
        junc.append(len(pts) - 1)
    if any(pts[i + 1][0] < pts[i][0] - 1e-9 for i in range(len(pts) - 1)):
        errs.append("La sección debe avanzar de izquierda a derecha: revisa que ningún tramo vuelva hacia atrás.")
    return pts, ms, ns_, junc[:-1], seg_tr, errs


def tabla_compuesta():
    """Tramos editables, cada uno con su forma, su material y su n."""
    clave = "filas_cmp"
    MATL, CON = list(mh.MATERIALES), "Concreto (acabado con llana)"
    if clave not in st.session_state:
        base = [("Vertical", 1.0, 0.0, "Desciende"), ("Arco circular", 0.5, 180.0, "Desciende"), ("Vertical", 1.0, 0.0, "Asciende")]
        st.session_state[clave] = [dict(id=i, tp=b[0], tp_prev=b[0], a=b[1], b=b[2], sent=b[3], forma="Cóncavo (fondo)", mat=CON, n=0.013) for i, b in enumerate(base)]
    filas = st.session_state[clave]
    st.caption("Describe el contorno de izquierda a derecha, tramo por tramo, empezando arriba a la izquierda. Cada tramo continúa donde termina el anterior.")
    for i, r in enumerate(filas):
        with st.container(border=True):
            c1, c2 = st.columns([8, 2], vertical_alignment="bottom")
            r["tp"] = c1.selectbox(f"Tramo {i + 1}", TIPOS_TRAMO, index=TIPOS_TRAMO.index(r["tp"]), key=f"{clave}_tp_{r['id']}")
            if r.get("tp_prev") != r["tp"]:
                r["a"], r["b"] = DEF_TRAMO[r["tp"]]; r["tp_prev"] = r["tp"]
            c2.button("🗑", key=f"{clave}_del_{r['id']}", on_click=_eliminar, args=(clave, r["id"]), disabled=len(filas) <= 2, help="Eliminar este tramo")
            k = f"{clave}_{r['tp'][:4]}_%s_{r['id']}"
            u1, u2 = st.columns(2)
            nb = lambda col, etq, v, key, lo=0.01, hi=None, st_=0.1, fm="%.3f": col.number_input(etq, min_value=lo, max_value=hi, value=min(max(float(v), lo), hi if hi else 1e9), step=st_, format=fm, key=key)
            if r["tp"] == "Vertical":
                r["a"] = nb(u1, "Altura (m)", r["a"], k % "a")
                r["sent"] = u2.selectbox("Sentido", ["Desciende", "Asciende"], index=["Desciende", "Asciende"].index(r["sent"]), key=k % "s")
            elif r["tp"] == "Talud":
                r["a"] = nb(u1, "Desnivel vertical (m)", r["a"], k % "a"); r["b"] = nb(u2, "Talud z (H:V)", r["b"], k % "b", lo=0.0)
                r["sent"] = st.selectbox("Sentido", ["Desciende", "Asciende"], index=["Desciende", "Asciende"].index(r["sent"]), key=k % "s")
            elif r["tp"] == "Horizontal":
                r["a"] = nb(u1, "Ancho (m)", r["a"], k % "a")
            elif r["tp"] == "Arco circular":
                r["a"] = nb(u1, "Radio (m)", r["a"], k % "a"); r["b"] = nb(u2, "Ángulo del arco (°)", r["b"], k % "b", lo=10.0, hi=180.0, st_=5.0, fm="%.1f")
                r["forma"] = st.selectbox("Curvatura", ["Cóncavo (fondo)", "Convexo"], index=["Cóncavo (fondo)", "Convexo"].index(r["forma"]), key=k % "f")
                st.caption("Cóncavo: curva hacia abajo, como un fondo circular (180° es un semicírculo). Convexo: curva hacia arriba, como una joroba.")
            elif r["tp"] == "Parábola (fondo)":
                r["a"] = nb(u1, "Ancho total (m)", r["a"], k % "a"); r["b"] = nb(u2, "Profundidad (m)", r["b"], k % "b")
            else:
                r["a"] = nb(u1, "Longitud (m)", r["a"], k % "a"); r["b"] = nb(u2, "Ángulo (°)", r["b"], k % "b", lo=-90.0, hi=90.0, st_=5.0, fm="%.1f")
            m1, m2 = st.columns([3, 2])
            r["mat"] = m1.selectbox("Material del tramo", MATL, index=MATL.index(r["mat"]), key=f"{clave}_m_{r['id']}", on_change=_cambio_material, args=(clave, r["id"]))
            kn = f"{clave}_n_{r['id']}"
            r["n"] = m2.number_input("n", min_value=0.001, step=0.001, format="%.3f", key=kn, **({} if kn in st.session_state else {"value": float(r["n"])}))
    b1, b2 = st.columns(2)
    b1.button("➕ Agregar tramo", key=clave + "_add", on_click=_agregar, args=(clave,), width="stretch")
    b2.button("↺ Restablecer ejemplo", key=clave + "_reset", on_click=_restablecer, args=(clave,), width="stretch")
    pts_, _, _, junc_, _, _ = construir_tramos(filas)
    st.caption("Puntos finales de cada tramo (x, y): " + "  →  ".join(f"T{i + 1} ({pts_[j][0]:.2f}, {pts_[j][1]:.2f})" for i, j in enumerate(junc_ + [len(pts_) - 1])))
    return _salida_cmp(filas)


def _salida_cmp(filas):
    pts, ms, ns_, junc, seg_tr, errs = construir_tramos(filas)
    return pts, ms, ns_, errs, junc, seg_tr


def _recortar(poly, L):
    """Parte del polígono (convexo) que queda por debajo de la cota L."""
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        if p[1] <= L: out.append(p)
        if (p[1] <= L) != (q[1] <= L):
            t = (L - p[1]) / (q[1] - p[1]); out.append((p[0] + t * (q[0] - p[0]), L))
    return out


def perfil_cerrado(s, n=160):
    if isinstance(s, mh.Circular):
        R = s.D / 2
        return [(R * math.sin(-math.pi + 2 * math.pi * k / n), R - R * math.cos(-math.pi + 2 * math.pi * k / n)) for k in range(n + 1)]
    return [(-s.T0 / 2 + s.T0 * k / n, s.a * (-s.T0 / 2 + s.T0 * k / n) ** 2) for k in range(n + 1)]


def dibujar_cerrada(s, y, H, mats):
    """Sección circular o parabólica con agua, y nodos de referencia."""
    per, circ = perfil_cerrado(s), isinstance(s, mh.Circular)
    ancho = s.D / 2 if circ else s.T0 / 2
    agua = _recortar(per, y)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[p[0] for p in agua] + [agua[0][0]], y=[p[1] for p in agua] + [agua[0][1]], fill="toself", mode="lines",
                             fillcolor="rgba(79,179,169,.40)", line=dict(color=TUR, width=2), hoverinfo="skip", showlegend=False))
    xs, zs = [p[0] for p in per], [p[1] for p in per]
    fig.add_trace(go.Scatter(x=xs, y=zs, mode="lines", line=dict(color=MAR, width=2.6), hoverinfo="skip", showlegend=False))

    # Nodos de referencia
    if circ:
        R = s.D / 2
        nodos = [(-R, R), (0.0, 0.0), (R, R), (0.0, s.D)]
        posiciones = ["middle left", "bottom center", "middle right", "top center"]
    else:
        nodos = [(-s.T0 / 2, s.H), (0.0, 0.0), (s.T0 / 2, s.H)]
        posiciones = ["top left", "bottom center", "top right"]
    etiquetas = [f"P{i}" for i in range(1, len(nodos) + 1)]
    fig.add_trace(go.Scatter(
        x=[p[0] for p in nodos], y=[p[1] for p in nodos], mode="markers+text",
        text=etiquetas, textposition=posiciones, textfont=dict(color=MAR, size=11),
        marker=dict(color=MAR, size=8), hoverinfo="skip", showlegend=False,
    ))

    fig.add_trace(go.Scatter(x=[-ancho, ancho], y=[H, H], mode="lines", line=dict(color="#718096", width=1.2, dash="dash"), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(x=[-s.T(y)/2, s.T(y)/2], y=[y, y], mode="lines", line=dict(color="#008DC0", width=3.2), hoverinfo="skip", showlegend=False))
    fig.add_annotation(x=0, y=y, text="Nivel de agua", showarrow=False, yshift=-16, font=dict(color="#00739B", size=11), bgcolor="rgba(255,255,255,0.9)")
    fig.add_annotation(x=0, y=y, text=f"T = {s.T(y):.3f} m", showarrow=False, yshift=13, font=dict(color=MAR, size=12), bgcolor="rgba(255,255,255,.85)")
    xd = ancho + .10 * max(ancho, 1e-6)
    fig.add_shape(type="line", x0=xd, x1=xd, y0=0.0, y1=y, line=dict(color=MAR, width=1.3))
    for zp in (y, 0.0):
        fig.add_annotation(x=xd, y=zp, ax=xd, ay=y / 2, axref="x", ayref="y", text="", showarrow=True,
                           arrowhead=2, arrowsize=1, arrowwidth=1.3, arrowcolor=MAR)
    fig.add_annotation(x=xd, y=y / 2, text=f"y = {y:.3f} m", showarrow=False,
                       xanchor="left", xshift=7, font=dict(color=MAR, size=12))
    fig.add_annotation(x=ancho, y=H, text=f"y + BL = {H:.3f} m", xanchor="left", xshift=6,
                       showarrow=False, font=dict(color=MAR, size=11))
    fig.add_trace(go.Scatter(x=[-ancho, ancho], y=[s.altura, s.altura], mode="lines", line=dict(color=MAR, width=1.5, dash="dot"), hoverinfo="skip", showlegend=False))
    fig.add_annotation(x=-ancho, y=s.altura if not circ else s.D,
                       text=(f"D = {s.D:.3f} m" if circ else f"Altura de la sección = {s.altura:.3f} m"),
                       xanchor="left", yshift=14, showarrow=False, font=dict(color=MAR, size=11))
    fig.update_layout(title="Visualización dinámica de la sección", height=500, plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                      dragmode="pan", margin=dict(l=40, r=60, t=60, b=50), font=dict(color=MAR),
                      xaxis=dict(title="Distancia horizontal (m)", gridcolor="#E4EBF1"), yaxis=dict(title="Elevación (m)", gridcolor="#E4EBF1", scaleanchor="x"))
    return fig


def dib(s, y, H, mats, ns, indices_nodo=None):
    if isinstance(s, (mh.Circular, mh.Parabolica)): return dibujar_cerrada(s, y, H, mats)
    return dibujar_poli(s, y, H, indices_nodo=indices_nodo) if isinstance(s, mh.Poligonal) else dibujar(s, y, H, mats, ns)


def _agregar(clave):
    f = st.session_state[clave]; u = dict(f[-1]); u["id"] = max(r["id"] for r in f) + 1
    if clave == "filas_xy": u["a"] = u["a"] + 0.5
    f.append(u)


def _eliminar(clave, ident):
    st.session_state[clave] = [r for r in st.session_state[clave] if r["id"] != ident]


def _restablecer(clave):
    st.session_state.pop(clave, None)


def _cambio_material(clave, ident):
    st.session_state[f"{clave}_n_{ident}"] = mh.MATERIALES[st.session_state[f"{clave}_m_{ident}"]][0]


def tabla_seccion(tipo):
    """Sección por filas editables (punto o tramo, con su material y n). Devuelve (puntos, materiales, n por tramo, errores)."""
    xy = tipo == "Por coordenadas (X, Y)"
    clave, minimo = ("filas_xy", 3) if xy else ("filas_ang", 2)
    MATL, CON = list(mh.MATERIALES), "Concreto (acabado con llana)"
    if clave not in st.session_state:
        base = [(0.0, 1.0), (0.5, 0.0), (1.5, 0.0), (2.0, 1.0)] if xy else [(1.414, -45.0), (1.0, 0.0), (1.414, 45.0)]
        st.session_state[clave] = [dict(id=i, a=p[0], b=p[1], mat=CON, n=0.013) for i, p in enumerate(base)]
    filas = st.session_state[clave]
    st.caption("Ingresa los puntos de izquierda a derecha. El material y el n de cada fila son los del tramo que sigue a ese punto." if xy else
               "Ingresa los tramos de izquierda a derecha, desde el punto (0, 0). El ángulo va de −90° a 90°: positivo sube y negativo baja.")
    for i, r in enumerate(filas):
        with st.container(border=True):
            c1, c2, c3 = st.columns([5, 5, 2], vertical_alignment="bottom")
            k = f"{clave}_%s_{r['id']}"
            if xy:
                r["a"] = c1.number_input(f"X (m) | punto {i + 1}", value=float(r["a"]), step=0.1, format="%.2f", key=k % "a")
                r["b"] = c2.number_input("Y (m)", value=float(r["b"]), step=0.1, format="%.2f", key=k % "b")
            else:
                r["a"] = c1.number_input(f"Longitud (m) | tramo {i + 1}", min_value=0.01, value=max(float(r["a"]), 0.01), step=0.1, format="%.3f", key=k % "a")
                r["b"] = c2.number_input("Ángulo (°)", min_value=-90.0, max_value=90.0, value=float(r["b"]), step=5.0, format="%.1f", key=k % "b")
            c3.button("🗑", key=k % "del", on_click=_eliminar, args=(clave, r["id"]), disabled=len(filas) <= minimo, help="Eliminar esta fila")
            if xy and i == len(filas) - 1:
                st.caption("Último punto: no inicia ningún tramo.")
            else:
                m1, m2 = st.columns([3, 2])
                r["mat"] = m1.selectbox("Material del tramo", MATL, index=MATL.index(r["mat"]), key=k % "m", on_change=_cambio_material, args=(clave, r["id"]))
                r["n"] = m2.number_input("n", min_value=0.001, step=0.001, format="%.3f", key=k % "n", **({} if (k % "n") in st.session_state else {"value": float(r["n"])}))
    b1, b2 = st.columns(2)
    b1.button("➕ Agregar punto" if xy else "➕ Agregar tramo", key=clave + "_add", on_click=_agregar, args=(clave,), width="stretch")
    b2.button("↺ Restablecer ejemplo", key=clave + "_reset", on_click=_restablecer, args=(clave,), width="stretch")
    errs = []
    if xy:
        pts = [(r["a"], r["b"]) for r in filas]; ms = [r["mat"] for r in filas[:-1]]; ns_ = [r["n"] for r in filas[:-1]]
    else:
        x = yy = 0.0; pts = [(0.0, 0.0)]
        for r in filas:
            x += r["a"] * math.cos(math.radians(r["b"])); yy += r["a"] * math.sin(math.radians(r["b"])); pts.append((x, yy))
        ms = [r["mat"] for r in filas]; ns_ = [r["n"] for r in filas]
    if any(pts[i + 1][0] < pts[i][0] - 1e-9 for i in range(len(pts) - 1)):
        errs.append("Los puntos deben ir de izquierda a derecha (X creciente).")
    return pts, ms, ns_, errs


# -------- Navegación: barra superior y menú desplegable por procedimiento --------
TITULOS = {clave: titulo for clave, titulo, *_ in OPERACIONES}
if st.session_state.get("pag") == "app" and st.session_state.get("modulo") not in TITULOS:
    st.session_state.pag = "menu"
# La guía se abre una sola vez por sesión, sin reemplazar la portada ni los menús.
if "hd_guia_inicial_mostrada" not in st.session_state:
    st.session_state.hd_guia_inicial_mostrada = True
    mostrar_guia_uso()

# Acceso opcional para volver a consultar las instrucciones desde cualquier ventana.
with st.sidebar:
    if st.button("📘 Guía de uso", key="hd_guia_reabrir", width="stretch"):
        mostrar_guia_uso()

barra_navegacion(st.session_state.get("modulo") if st.session_state.pag == "app" else None)
if st.session_state.pag == "menu":
    menu_principal()
    st.stop()
modulo = st.session_state.modulo

# ---------------- Área de trabajo ----------------
st.markdown(f"### {TITULOS[modulo]}")
st.markdown('<div class="mast">Ventana de cálculo · unidades del Sistema Internacional · los resultados se actualizan al modificar los datos.</div>', unsafe_allow_html=True)
izq, centro, der = st.columns([1.04, 1.24, 1.08], gap="medium")

seg_tr_ = None
Dc, Tpar, Hpar = 1.0, 1.0, 0.6
pts_ = ms_ = ns_ = None
err_poly = []
POLI = False
SUBAREAS = False
cortes_ = []
cortes_h_ = []
corte_pm = False
n_u = nf = nw = nwi = nwd = 0.013
k1 = k2 = k3 = k4 = 0.0
k5 = 1.0

with izq:
    if modulo == "compuesta":
        _op = {"Tirante normal": "Tirante normal (y)", "Caudal": "Caudal (Q)", "Pendiente": "Pendiente (S)", "Tirante crítico": "Tirante crítico (yc)"}
        inc = _op[st.selectbox("¿Qué calcular?", list(_op))]
    else:
        inc = {"uniforme_Q": "Caudal (Q)", "uniforme_S": "Pendiente (S)", "critico": "Tirante crítico (yc)",
               "energia": "Pendiente (S)"}.get(modulo, "Tirante normal (y)")
    titulo_panel(1, "Geometría de la sección")
    if modulo == "compuesta":
        tipo = "Sección compuesta"
        modo_ing = st.segmented_control("Construcción del perfil", ["Por tramos (rectas, arcos y parábolas)", "Por coordenadas (X, Y)"], default="Por tramos (rectas, arcos y parábolas)")
        # En Streamlit Cloud el selector puede devolver None antes de la primera interacción.
        # Conservar el valor predeterminado sin alterar los métodos ni las fórmulas hidráulicas.
        if modo_ing is None:
            modo_ing = "Por tramos (rectas, arcos y parábolas)"
    else:
        tipo = st.selectbox("Sección transversal", ["Rectangular", "Trapezoidal", "Triangular"] if modulo == "diseno" else
                            ["Rectangular", "Trapezoidal", "Triangular", "Circular", "Parabólica", "Por coordenadas (X, Y)", "Por ángulos y tramos"], key="tipo_seccion")
    POLI = tipo in ("Por coordenadas (X, Y)", "Por ángulos y tramos", "Sección compuesta")
    FORMA = tipo in ("Circular", "Parabólica")
    geo_a, geo_b = st.columns(2)
    b = geo_a.number_input("Solera b · m", min_value=0.0, value=0.8, step=0.1, format="%.3f", key="b_geom") if (tipo != "Triangular" and modulo != "diseno" and not POLI and not FORMA) else 0.0
    z = geo_b.number_input("Talud z · H:V", min_value=0.0, value=1.0, step=0.25, format="%.3f", key="z_geom") if (tipo != "Rectangular" and not POLI and not FORMA) else 0.0
    if tipo == "Rectangular": st.caption("Geometría: b, con paredes verticales.")
    elif tipo == "Triangular": st.caption("Geometría: z; la solera es nula (b = 0).")
    elif tipo == "Trapezoidal": st.caption("Geometría: b y z. El talud se expresa horizontal:vertical.")
    if tipo == "Circular":
        Dc = st.number_input("Diámetro D (m)", 0.0, value=1.0, step=0.1, format="%.3f")
    if tipo == "Parabólica":
        Tpar = st.number_input("Espejo de agua T (m), a la altura H", 0.0, value=1.0, step=0.1, format="%.3f")
        Hpar = st.number_input("Altura de la sección H (m)", 0.0, value=0.6, step=0.1, format="%.3f")
        if Tpar > 0 and Hpar > 0: st.caption(f"Foco de la parábola: k = T²/(16·H) = {Tpar ** 2 / (16 * Hpar):.3f} m")
    if POLI:
        junc = None
        if modulo == "compuesta" and modo_ing.startswith("Por tramos"):
            pts_, ms_, ns_, err_poly, junc, seg_tr_ = tabla_compuesta()
        else:
            pts_, ms_, ns_, err_poly = tabla_seccion("Por coordenadas (X, Y)" if modulo == "compuesta" else tipo)
        if modulo == "compuesta":
            cand = junc if junc is not None else list(range(1, len(pts_) - 1))
            titulo_panel(2, "Modelo de subáreas")
            SUBAREAS = st.radio("Método de cálculo", ["Horton-Einstein (un solo n equivalente)", "División en subáreas (cada una con su n, Q = ΣQᵢ)"]).startswith("División")
            if SUBAREAS and not err_poly:
                forma = st.radio("Forma de dividir", ["Automática", "Manual"], horizontal=True)
                if forma == "Automática":
                    crit_c = st.selectbox("Criterio de corte", ["Cambio de material (n)", "Cambio de pendiente de las paredes", "En cada unión de tramos (o punto)"])
                    cortes_ = mh.cortes_auto(pts_, ns_, ms_, crit_c, cand if junc is not None else None)
                else:
                    etq = {k: (f"Unión de los tramos {j + 1} y {j + 2} (x = {pts_[k][0]:.2f} m)" if junc is not None else f"Punto {k + 1} (x = {pts_[k][0]:.2f} m)") for j, k in enumerate(cand)}
                    cortes_ = st.multiselect("Cortes verticales: puntos donde se corta", cand, format_func=lambda k: etq[k])
                    zs_ = [q[1] for q in pts_]
                    st.caption(f"Cortes horizontales: la cota (Y) de la sección va de {min(zs_):.2f} a {max(zs_):.2f} m.")
                    sel_h = st.multiselect("Cortes horizontales: a la cota de estos puntos", cand, format_func=lambda k: f"Punto {k + 1} (cota = {pts_[k][1]:.2f} m)")
                    extra_h = st.text_input("Otras cotas de corte horizontal (m), separadas por coma", value="")
                    otras = []
                    for tk in extra_h.replace(";", ",").split(","):
                        try: otras.append(float(tk))
                        except ValueError: pass
                    cortes_h_ = sorted({pts_[k][1] for k in sel_h} | set(otras))
                corte_pm = st.checkbox("Contar los cortes como perímetro mojado", value=False)
                st.caption(f"Se forman hasta {(len(cortes_) + 1) * (len(cortes_h_) + 1)} subárea(s). Los cortes verticales pasan por los puntos indicados y los horizontales siguen la cota indicada.")
    crit_d = None
    if modulo == "diseno":
        if tipo == "Triangular": st.caption("En sección triangular la máxima eficiencia se logra con z = 1 (θ = 45°); no hay ancho de solera que dimensionar.")
        else: crit_d = st.selectbox("Criterio de diseño", list(mh.FACTORES))

    titulo_panel(2 if modulo != "compuesta" else 3, "Material y rugosidad")
    MAT = list(mh.MATERIALES)

    def material(etq, defecto, clave):
        mt = st.selectbox(etq, MAT, index=MAT.index(defecto), key="m_" + clave)
        return mt, st.number_input(f"n de {etq.lower().replace('material de ', '')}", 0.0, value=mh.MATERIALES[mt][0], step=0.001,
                                   format="%.3f", key=f"n_{clave}_{mt}")
    op = ["Un solo material", "Fondo y paredes distintos", "Fondo y cada pared distintos"] if tipo != "Triangular" \
        else ["Un solo material", "Cada pared distinta"]
    modo_txt = st.radio("Materiales del canal", op) if not (POLI or FORMA) else op[0]
    modo = 0 if modo_txt == op[0] else (1 if modo_txt == "Fondo y paredes distintos" else 2)
    if tipo == "Triangular" and modo == 1: modo = 2
    CON = "Concreto (acabado con llana)"
    mf = mi = md = CON
    if POLI:
        modo = 3
        st.caption("Los materiales y los n de cada tramo se toman de la tabla de la sección.")
    elif modo == 0:
        mf, n_u = material("Material del canal", CON, "u"); mi = md = mf
    else:
        if tipo != "Triangular":
            mf, nf = material("Material del fondo", CON, "f")
        if modo == 1:
            mi, nw = material("Material de las paredes", "Mampostería de piedra", "w"); md = mi; nwi = nwd = nw
        else:
            mi, nwi = material("Material de la pared izquierda", "Mampostería de piedra", "i")
            md, nwd = material("Material de la pared derecha", "Tierra", "d")
        if tipo == "Triangular": mf = mi
        st.caption("Se combinan con Horton-Einstein, ponderando por perímetro mojado.")
    st.caption("Los n sugeridos son valores típicos referenciales; puedes escribir el que necesites.")
    cow_on = st.checkbox("Hay irregularidades (Cowan)")
    if cow_on:
        st.markdown(tabla_cowan(), unsafe_allow_html=True)
        st.caption("Tabla de guía: puedes escribir cualquier valor, aunque esté fuera del rango.")
        a, c_, d = st.columns(3)
        k1 = a.number_input("n1", value=0.0, step=0.001, format="%.3f"); k2 = c_.number_input("n2", value=0.0, step=0.001, format="%.3f")
        k3 = d.number_input("n3", value=0.0, step=0.001, format="%.3f")
        e, f_ = st.columns(2)
        k4 = e.number_input("n4", value=0.0, step=0.001, format="%.3f"); k5 = f_.number_input("m5", value=1.0, step=0.01, format="%.3f")

    titulo_panel(3 if modulo != "compuesta" else 4, "Condiciones hidráulicas")
    Q = S = y = None
    if inc != "Caudal (Q)":
        q1, q2 = st.columns([2, 1])
        Qv = q1.number_input("Caudal Q", 0.0, value=300.0, format="%.3f")
        Q = Qv * (0.001 if q2.selectbox("Unidad Q", ["L/s", "m³/s"]) == "L/s" else 1)
    if inc not in ("Pendiente (S)", "Tirante crítico (yc)"):
        s1, s2 = st.columns([2, 1])
        Sv = s1.number_input("Pendiente S", 0.0, value=1.5, format="%.4f")
        S = Sv / {"%": 100, "m/m": 1, "‰": 1000}[s2.selectbox("Unidad S", ["%", "m/m", "‰"])]
    if inc not in ("Tirante normal (y)", "Tirante crítico (yc)"):
        y = st.number_input("Tirante y (m)", 0.0, value=0.2, format="%.3f")

    metodo_sol, p_met = "Manning", 0.0
    with st.expander("Método de solución", expanded=False):
        metodo_sol = st.selectbox("Fórmula", ["Manning", "Chezy", "Bazin", "Ganguillet-Kutter"], key="msol")
        if metodo_sol == "Chezy": p_met = st.number_input("Coeficiente C de Chezy", 0.0, value=50.0, format="%.2f")
        if metodo_sol == "Bazin": p_met = st.number_input("Coeficiente γ de Bazin", 0.0, value=0.16, format="%.3f")
        if metodo_sol.startswith("Gang"): st.caption("Fórmula de Kutter válida para S ≥ 0.0005 (Villón).")
    if modulo == "energia":
        en_on = True
        st.caption("Curva E–y incluida en este procedimiento.")
    else:
        en_on = st.checkbox("Incluir energía específica y curva E–y", value=True, key="en_on")
    with st.expander("Verificación de velocidad y borde libre", expanded=False):
        v1, v2 = st.columns(2)
        vmin = v1.number_input("Vmín (m/s)", 0.0, value=0.6, format="%.2f")
        vmax = v2.number_input("Vmáx (m/s)", 0.0, value=3.0, format="%.2f")
        ops_bl = mh.METODOS_BL if tipo in ("Rectangular", "Trapezoidal") else [m_ for m_ in mh.METODOS_BL if m_ != "Villón por ancho de solera"]
        metodo = st.selectbox("Método de borde libre", ops_bl)
        bl_man = 0.3
        if metodo == "Valor manual":
            bl_man = st.number_input("Borde libre BL (m)", 0.0, value=0.3, step=0.05, format="%.3f")
        with st.popover("Consultar tabla de borde libre"):
            st.markdown(tabla_bl(), unsafe_allow_html=True)
    st.caption("Puedes cambiar de cálculo desde la barra superior sin perder los datos del formulario.")

# ---------------- Cálculo ----------------
if modulo == "diseno":
    b = 0.5   # provisional: el ancho se dimensiona más abajo
if POLI and not err_poly and SUBAREAS:
    s = mh.Compuesta(pts_, ns_, ms_, cortes_, corte_pm, (lambda n0: mh.cowan(n0, k1, k2, k3, k4, k5)) if cow_on else None, seg_tr_, cortes_h_)
elif POLI and not err_poly:
    s = mh.Poligonal(pts_, ns_, ms_)
elif tipo == "Circular":
    s = mh.Circular(max(Dc, 1e-6))
elif tipo == "Parabólica":
    s = mh.Parabolica(max(Tpar, 1e-6), max(Hpar, 1e-6))
else:
    s = mh.Seccion("Rectangular" if POLI else tipo, b, z)
errs = list(err_poly)
if tipo == "Circular" and Dc <= 0: errs.append("El diámetro debe ser mayor que 0.")
if tipo == "Parabólica" and (Tpar <= 0 or Hpar <= 0): errs.append("El espejo de agua T y la altura H deben ser mayores que 0.")
if tipo != "Triangular" and not POLI and not FORMA and b <= 0: errs.append("El ancho de solera debe ser mayor que 0.")
if inc != "Caudal (Q)" and Q <= 0: errs.append("El caudal debe ser mayor que 0.")
if inc not in ("Pendiente (S)", "Tirante crítico (yc)") and S <= 0: errs.append("La pendiente debe ser mayor que 0.")
if inc not in ("Tirante normal (y)", "Tirante crítico (yc)") and y <= 0: errs.append("El tirante debe ser mayor que 0.")


def partes(yy):
    if POLI: return s.partes(yy)
    p = [(s.b, nf)] if s.b > 0 else []
    return p + ([(s.paredes(yy), nw)] if modo == 1 else [(s.lado(yy), nwi), (s.lado(yy), nwd)])


n_base = (lambda yy: n_u) if modo == 0 else (lambda yy: mh.horton(partes(yy)))
nfun = (lambda yy: mh.cowan(n_base(yy), k1, k2, k3, k4, k5)) if cow_on else n_base
mats = (mf, mi, md)
ns = None if modo in (0, 3) else (nf, nwi, nwd)

# Tres paneles simultáneos, no pestañas que escondan el resultado.
tab_sec = centro.container(border=True)
tab_res = der.container(border=True)
tab_en = st.expander("Curva de energía específica E–y", expanded=(modulo == "energia")) if en_on else None
tab_proc = st.expander("Memoria de cálculo · desarrollo paso a paso", expanded=False)

if errs:
    with tab_sec:
        for e in errs: st.error(e)
        yp = y if y else 0.5
        if s.b > 0 or s.z > 0:
            st.plotly_chart(dib(s, yp, yp * 1.3, mats, ns), theme=None, config=CONFIG)
    st.stop()

it = None
if modulo == "diseno" and tipo != "Triangular":
    m_d = mh.FACTORES[crit_d] * (math.sqrt(1 + z * z) - z)

    def _q_dis(yy):
        global s
        s = mh.Seccion(tipo, m_d * yy, z)
        return mh.q_flujo(s, nfun, S, yy, metodo_sol, p_met) - Q
    hi_ = 1.0
    while _q_dis(hi_) < 0 and hi_ < 1e4: hi_ *= 2
    y_d, _ = mh.biseccion(_q_dis, 1e-6, hi_)
    b = m_d * y_d
    s = mh.Seccion(tipo, b, z)
if inc == "Tirante normal (y)": y, it = mh.tirante_normal(s, nfun, S, Q, metodo_sol, p_met)
elif inc == "Caudal (Q)": Q = mh.q_flujo(s, nfun, S, y, metodo_sol, p_met)
elif inc == "Tirante crítico (yc)":
    y = mh.tirante_critico(s, Q)
    S = mh.pendiente(s, nfun, Q, y, metodo_sol, p_met)
else: S = mh.pendiente(s, nfun, Q, y, metodo_sol, p_met)

if (inc == "Tirante normal (y)" and Q > mh.q_flujo(s, nfun, S, y, metodo_sol, p_met) * (1 + 1e-4)) or \
        (inc == "Tirante crítico (yc)" and getattr(s, "ymax", None) and s.A(y) ** 3 / s.T(y) < Q ** 2 / mh.G * (1 - 1e-4)):
    with tab_sec:
        st.error("El caudal supera la capacidad de la sección: no existe un tirante dentro de su altura que lo conduzca.")
        st.plotly_chart(dib(s, y, y, mats, ns,
                            indices_nodo=([0] + junc + [len(s.pts) - 1] if POLI and junc is not None else None)),
                        theme=None, config=CONFIG)
    st.stop()
if getattr(s, "altura", None) is not None and y > s.altura + 1e-9:
    with tab_sec:
        st.error(f"El tirante ({y:.3f} m) supera la altura de la sección ({s.altura:.3f} m): el agua se desbordaría.")
        st.plotly_chart(dib(s, y, y, mats, ns,
                            indices_nodo=([0] + junc + [len(s.pts) - 1] if POLI and junc is not None else None)),
                        theme=None, config=CONFIG)
    st.stop()
A, P, T = s.A(y), s.P(y), s.T(y)
rotulo_y = ("Tirante crítico yc" if inc == "Tirante crítico (yc)"
            else "Tirante normal y" if inc == "Tirante normal (y)" else "Tirante y (dato)")
R, V, n = A / P, Q / A, nfun(y)
if SUBAREAS:
    n = A * R ** (2 / 3) * math.sqrt(S) / Q                 # n equivalente (Manning) de toda la sección
ORIGEN = "División en subáreas, n equivalente" if SUBAREAS else ("Valor directo" if modo == 0 else "Horton-Einstein") + (" + Cowan" if cow_on else "")
F, yc = mh.froude(s, Q, y), mh.tirante_critico(s, Q)
reg, msg_reg = mh.regimen(F)
est, msg_v = mh.verificar_velocidad(V, vmin, vmax)
rev = all(mt in ("Concreto (acabado con llana)", "Concreto (sin acabado)", "Mampostería de piedra") for mt in (s.mats if POLI else mats))
C = mh.c_usbr(Q)
bt = s.b if tipo in ("Rectangular", "Trapezoidal") else 0.0
BL, f_bl, crit = mh.borde_libre(metodo, y, Q, rev, bl_man, bt)
comp = mh.comparar_bl(y, Q, rev, bt)
E = y + V ** 2 / (2 * mh.G)
Ec = mh.energia(s, Q, yc)
y2 = mh.y_alterno(s, Q, y)
y2t = f"{y2:.3f} m" if y2 is not None else "No existe"
FIJA = getattr(s, "altura", None) is not None          # sección con altura propia: el borde libre disponible es altura − y
BLd = (s.altura - y) if FIJA else None
origen = ("" if modo == 0 else " (Horton)") + (" (Cowan)" if cow_on else "")

with tab_sec:
    titulo_panel(1, "Sección hidráulica")
    st.caption("Rueda: zoom · Arrastrar: desplazar · Doble clic: restablecer")
    st.plotly_chart(dib(s, y, y + BL, mats, ns,
                        indices_nodo=([0] + junc + [len(s.pts) - 1] if POLI and junc is not None else None)),
                    theme=None, config=CONFIG)
    if FIJA: st.caption("Línea azul punteada: borde superior de la sección. Línea dorada: nivel y + borde libre requerido.")

def tarjetas(items):
    for i in range(0, len(items), 3):
        cols = st.columns(3)
        for col, (t, v) in zip(cols, items[i:i + 3]):
            col.metric(t, v)


with tab_res:
    titulo_panel(2, "Resultados del cálculo")
    pdf_slot = st.container()
    st.markdown('<div class="grupo" style="margin-top:6px">Resultado principal</div>', unsafe_allow_html=True)
    tarjetas([(rotulo_y, f"{y:.3f} m"), ("Caudal Q", f"{Q:.3f} m³/s"), ("Pendiente crítica Sc" if inc == "Tirante crítico (yc)" else "Pendiente S", f"{S:.3f} m/m")] + ([("Ancho de solera b", f"{s.b:.3f} m")] if (modulo == "diseno" and tipo != "Triangular") else []))
    st.markdown('<div class="grupo">Geometría del flujo</div>', unsafe_allow_html=True)
    tarjetas([("Área A", f"{A:.3f} m²"), ("Perímetro mojado P", f"{P:.3f} m"), ("Espejo de agua T", f"{T:.3f} m"),
              ("Radio hidráulico R", f"{R:.3f} m"), ("Profundidad hidráulica A/T", f"{A / T:.3f} m")])
    st.markdown('<div class="grupo">Rugosidad</div>', unsafe_allow_html=True)
    tarjetas([("n usada", f"{n:.3f}"), ("Origen", ORIGEN)])
    st.markdown('<div class="grupo">Velocidad y régimen</div>', unsafe_allow_html=True)
    tarjetas([("Velocidad V", f"{V:.3f} m/s"), ("Número de Froude F", f"{F:.3f}"), ("Régimen", reg),
              ("Tirante crítico yc", f"{yc:.3f} m")])
    st.write("")
    (st.success if est == "ok" else st.warning)(msg_v)
    av = mh.validar_pendiente(S)
    if av: st.warning(av)
    st.info(msg_reg)
    if en_on:
        st.markdown('<div class="grupo">Energía específica</div>', unsafe_allow_html=True)
        tarjetas([("Energía específica E", f"{E:.3f} m"), ("Energía mínima Emín", f"{Ec:.3f} m"), ("Tirante alterno y₂", y2t)])
    st.markdown('<div class="grupo">Borde libre</div>', unsafe_allow_html=True)
    if FIJA:
        tarjetas([("BL requerido (método elegido)", f"{BL:.3f} m"), ("BL disponible = altura − y", f"{BLd:.3f} m"), ("Altura de la sección", f"{s.altura:.3f} m")])
        if isinstance(s, mh.Circular): st.caption(f"Relación y/D = {y / s.D:.3f}")
        (st.success if BLd >= BL - 1e-9 else st.warning)(
            f"Cumple: el borde libre disponible ({BLd:.3f} m) es mayor o igual al requerido ({BL:.3f} m)." if BLd >= BL - 1e-9 else
            f"No cumple: el borde libre disponible ({BLd:.3f} m) es menor que el requerido ({BL:.3f} m). Conviene aumentar la altura de la sección o reducir el tirante.")
    else:
        tarjetas([("Borde libre BL", f"{BL:.3f} m"), ("Altura total H = y + BL", f"{y + BL:.3f} m"), ("BL como % de y", f"{100 * BL / y:.1f} %")])
    st.caption("Criterio aplicado: " + crit)
    if metodo.startswith("USBR") and Q > 85: st.warning("El caudal supera los 85 m³/s: el USBR queda fuera de su rango.")
    st.markdown("##### Comparación de métodos de borde libre")
    fichas_bl = []
    for m_, b_, c_ in comp:
        elegido = m_ == metodo
        valor_bl = "No aplica" if b_ is None else f"{b_:.3f} m"
        valor_h = "—" if b_ is None else f"{y + b_:.3f} m"
        clase = "na" if b_ is None else ""
        marca = "<span class='hd-bl-mark'>✓ Elegido</span>" if elegido else ""
        fichas_bl.append(
            f"<section class='hd-bl-card {'selected' if elegido else ''}'>"
            f"<header class='hd-bl-head'><span class='hd-bl-name'>{escape(m_)}</span>{marca}</header>"
            "<div class='hd-bl-metrics'>"
            "<div class='hd-bl-metric'><span class='hd-bl-lbl'>Borde libre · BL</span>"
            f"<span class='hd-bl-val {clase}'>{escape(valor_bl)}</span></div>"
            "<div class='hd-bl-metric'><span class='hd-bl-lbl'>Altura total · H = y + BL</span>"
            f"<span class='hd-bl-val {clase}'>{escape(valor_h)}</span></div></div>"
            f"<div class='hd-bl-criterio'><b>Criterio:</b> {escape(c_)}</div></section>"
        )
    st.markdown("<div class='hd-bl-cards'>" + "".join(fichas_bl) + "</div>", unsafe_allow_html=True)
    st.caption("El método seleccionado se identifica con la marca «✓ Elegido».")


if en_on:
    with tab_en:
        st.caption("Curva E–y: se representa el mínimo de energía en el tirante crítico.")
        st.plotly_chart(modulo_energia.curva(s, Q, y, yc, y2), theme=None, config=CONFIG)
        if y2 is None:
            st.info(f"Para E = {E:.3f} m no existe un tirante alterno dentro de la altura de la sección (la energía supera la que tiene con la sección llena). El mínimo de energía ocurre en el tirante crítico yc = {yc:.3f} m.")
        else:
            st.info(f"Para E = {E:.3f} m existen dos tirantes: y = {y:.3f} m ({reg.lower()}) y y₂ = {y2:.3f} m "
                    f"({'supercrítico' if y2 < yc else 'subcrítico'}). El mínimo de energía ocurre en el tirante crítico yc = {yc:.3f} m.")


def _paso(num, titulo):
    st.markdown(f'<div class="paso"><span class="num">{num}</span>{titulo}</div>', unsafe_allow_html=True)


def _res(txt, tono=""):
    st.markdown(f'<div class="res {tono}">{txt}</div>', unsafe_allow_html=True)


with tab_proc:
    st.markdown('<div class="grupo" style="margin-top:6px">Memoria de cálculo</div>', unsafe_allow_html=True)

    if modulo == "diseno" and tipo != "Triangular":
        with st.container(border=True):
            _paso("D", "Dimensionamiento de la sección")
            st.latex(r"\frac{b}{y}=f\,(\sqrt{1+z^2}-z)\qquad f=2\ (\mathrm{MEH}),\ 4\ (\mathrm{MI}),\ 3\ (\text{intermedia})")
            st.latex(rf"\frac{{b}}{{y}}={mh.FACTORES[crit_d]}\,(\sqrt{{1+{z:.3f}^2}}-{z:.3f})={m_d:.3f}")
            st.caption("Se busca el tirante y para el que Q(y, b = m·y) iguale al caudal de diseño, por bisección, con el método y la rugosidad elegidos.")
            _res(f"y = {y_d:.3f} m | b = {s.b:.3f} m ({crit_d})")
    with st.container(border=True):
        _paso(1, "Datos del problema")
        st.markdown(f"- Sección **{tipo.lower()}**" + (f", b = {s.b:.3f} m" if s.b > 0 else "") + (f", z = {s.z:.3f}" if s.z > 0 else "") + (f", D = {Dc:.3f} m" if tipo == "Circular" else "") + (f", T = {Tpar:.3f} m, H = {Hpar:.3f} m" if tipo == "Parabólica" else "")
                    + f"\n- Caudal Q = {Q:.3f} m³/s (en SI) | Pendiente S = {S:.4f} m/m\n- Incógnita: {inc.split(' (')[0].lower()}")

    with st.container(border=True):
        _paso(2, "Rugosidad")
        if SUBAREAS:
            st.markdown("Cada subárea tiene su propio n (Horton dentro de la subárea" + (", corregido con Cowan" if cow_on else "") + "). Los cortes " + ("sí" if corte_pm else "no") + " cuentan como perímetro mojado.")
            _d = mh.detalle_subareas(s, y, S, metodo_sol, p_met)
            st.table(pd.DataFrame([(d["nombre"], d["tramos"], f"{d['A']:.3f}", f"{d['P']:.3f}", f"{d['n']:.3f}", f"{d['R']:.3f}") for d in _d],
                                  columns=["Subárea", "Tramos", "A (m²)", "P (m)", "n", "R (m)"]).set_index("Subárea"))
        if modo == 0 and not cow_on:
            st.markdown(f"Material: **{mats[0]}**, con n tomado directamente.")
        if modo and not SUBAREAS:
            if POLI:
                det = s.detalle(y); nombres = [d[0] for d in det]; pts = [(d[1], d[2]) for d in det]
            else:
                nombres = (["Fondo"] if s.b > 0 else []) + (["Paredes"] if modo == 1 else ["Pared izquierda", "Pared derecha"])
                pts = partes(y)
            suma, Pt = sum(p * nn ** 1.5 for p, nn in pts), sum(p for p, _ in pts)
            st.latex(r"n_e=\left(\frac{\sum P_i\,n_i^{3/2}}{P}\right)^{2/3}")
            st.table(pd.DataFrame([(nm, f"{p:.3f}", f"{nn:.3f}", f"{p * nn ** 1.5:.4f}") for nm, (p, nn) in zip(nombres, pts)],
                                  columns=["Parte", "Pᵢ (m)", "nᵢ", "Pᵢ·nᵢ^1.5"]).set_index("Parte"))
            st.latex(rf"n_e=\left(\frac{{{suma:.4f}}}{{{Pt:.3f}}}\right)^{{2/3}}={n_base(y):.3f}")
        if cow_on and not SUBAREAS:
            st.latex(r"n=(n_0+n_1+n_2+n_3+n_4)\,m_5")
            st.latex(rf"n=({n_base(y):.3f}+{k1:.3f}+{k2:.3f}+{k3:.3f}+{k4:.3f})\times{k5:.3f}={n:.3f}")
        _res(f"n equivalente (Manning) = {n:.3f}" if SUBAREAS else f"n = {n:.3f}" + ("" if modo == 0 and not cow_on else (" (Horton-Einstein)" if modo and not cow_on else (" (Horton + Cowan)" if modo else " (Cowan)"))))

    with st.container(border=True):
        _paso(3, f"Ecuación de {metodo_sol}")
        Cc_ = mh.coef(metodo_sol, R, S, n, p_met)
        if SUBAREAS:
            st.latex(r"Q=\sum_i Q_i\qquad " + (r"Q_i=\frac{1}{n_i}\,A_i\,R_i^{2/3}\,S^{1/2}" if metodo_sol == "Manning" else r"Q_i=C_i\,A_i\,\sqrt{R_i\,S}"))
            st.table(pd.DataFrame([(d["nombre"], f"{d['Q']:.3f}", f"{100 * d['Q'] / Q:.1f} %") for d in _d], columns=["Subárea", "Qᵢ (m³/s)", "% del caudal"]).set_index("Subárea"))
            st.latex(rf"\sum Q_i={sum(d['Q'] for d in _d):.3f}\ \mathrm{{m^3/s}}")
        else:
            FORM = {"Manning": r"C=\frac{R^{1/6}}{n}", "Chezy": r"C=\text{dato}", "Bazin": r"C=\frac{87}{1+\gamma/\sqrt{R}}",
                    "Ganguillet-Kutter": r"C=\frac{23+\frac{0.00155}{S}+\frac{1}{n}}{1+\left(23+\frac{0.00155}{S}\right)\frac{n}{\sqrt{R}}}"}
            if metodo_sol == "Manning":
                st.latex(r"Q=\frac{1}{n}\,A\,R^{2/3}\,S^{1/2}")
                st.latex(rf"{Q:.3f}=\frac{{1}}{{{n:.3f}}}\,({A:.3f})\,({R:.3f})^{{2/3}}\,({S:.4f})^{{1/2}}")
            else:
                st.latex(FORM[metodo_sol] + r"\qquad Q=C\,A\,\sqrt{R\,S}")
                st.latex(rf"C={Cc_:.3f}\qquad {Q:.3f}={Cc_:.3f}\,({A:.3f})\sqrt{{({R:.3f})({S:.4f})}}")
        if inc == "Tirante crítico (yc)":
            st.caption("Primero se halla el tirante crítico con Q²/g = Ac³/Tc; luego la pendiente crítica con la ecuación anterior.")
            _res(f"Tirante crítico yc = {y:.3f} m  |  Pendiente crítica Sc = {S:.4f} m/m")
        elif inc == "Pendiente (S)": _res(f"S = {S:.4f} m/m")
        elif it:
            st.caption("El tirante se halla por bisección, hasta que el intervalo sea menor que 0.000001 m.")
            _res(f"y = {y:.3f} m | {len(it)} iteraciones")
        else: _res(f"Q = {Q:.3f} m³/s")
        if it:
            with st.popover("Ver tabla de iteraciones"):
                st.dataframe(pd.DataFrame(it).rename(columns={"i": "Iteración", "y": "y (m)", "error": "Error (m)"}).set_index("Iteración")
                             .style.format({"y (m)": "{:.6f}", "Error (m)": "{:.2e}"}), width="stretch")

    with st.container(border=True):
        _paso(4, "Elementos geométricos")
        if tipo == "Circular":
            th = 2 * math.acos(max(-1.0, min(1.0, 1 - 2 * y / Dc)))
            g = rf"\theta=2\arccos\left(1-\frac{{2y}}{{D}}\right)={th:.3f}\ \mathrm{{rad}}\\A=\frac{{D^2}}{{8}}(\theta-\sin\theta)={A:.3f}\ \mathrm{{m^2}}\\P=\frac{{D\,\theta}}{{2}}={P:.3f}\ \mathrm{{m}}\\T=D\sin\frac{{\theta}}{{2}}={T:.3f}\ \mathrm{{m}}"
        elif tipo == "Parabólica":
            g = rf"T=T_0\sqrt{{y/H}}={T:.3f}\ \mathrm{{m}}\\A=\frac{{2}}{{3}}\,T\,y={A:.3f}\ \mathrm{{m^2}}\\P=2\left[\frac{{x}}{{2}}\sqrt{{1+4a^2x^2}}+\frac{{\operatorname{{asinh}}(2ax)}}{{4a}}\right]={P:.3f}\ \mathrm{{m}}\qquad x=\frac{{T}}{{2}},\ a=\frac{{H}}{{(T_0/2)^2}}"
        elif POLI:
            g = rf"A=\sum A_i={A:.3f}\ \mathrm{{m^2}}\\P=\sum P_i={P:.3f}\ \mathrm{{m}}\\T=\sum T_i={T:.3f}\ \mathrm{{m}}"
        elif tipo == "Rectangular":
            g = rf"A=b\,y={b:.3f}\times{y:.3f}={A:.3f}\ \mathrm{{m^2}}\\P=b+2y={b:.3f}+2({y:.3f})={P:.3f}\ \mathrm{{m}}\\T=b={T:.3f}\ \mathrm{{m}}"
        elif tipo == "Trapezoidal":
            g = rf"A=(b+zy)\,y=({b:.3f}+{z:.3f}\times{y:.3f})\times{y:.3f}={A:.3f}\ \mathrm{{m^2}}\\P=b+2y\sqrt{{1+z^2}}={P:.3f}\ \mathrm{{m}}\\T=b+2zy={T:.3f}\ \mathrm{{m}}"
        else:
            g = rf"A=z\,y^2={z:.3f}\times{y:.3f}^2={A:.3f}\ \mathrm{{m^2}}\\P=2y\sqrt{{1+z^2}}={P:.3f}\ \mathrm{{m}}\\T=2zy={T:.3f}\ \mathrm{{m}}"
        g += rf"\\R=\frac{{A}}{{P}}=\frac{{{A:.3f}}}{{{P:.3f}}}={R:.3f}\ \mathrm{{m}}\\\bar y=\frac{{A}}{{T}}={A / T:.3f}\ \mathrm{{m}}"
        st.latex(r"\begin{gathered}" + g + r"\end{gathered}")

    with st.container(border=True):
        _paso(5, "Velocidad y número de Froude")
        st.latex(rf"V=\frac{{Q}}{{A}}=\frac{{{Q:.3f}}}{{{A:.3f}}}={V:.3f}\ \mathrm{{m/s}}")
        st.latex(rf"F=\frac{{V}}{{\sqrt{{g\,A/T}}}}=\frac{{{V:.3f}}}{{\sqrt{{9.81\times{A / T:.3f}}}}}={F:.3f}")
        _res(f"F = {F:.3f} → régimen {reg.lower()}", "ok")
        st.caption(msg_reg)

    with st.container(border=True):
        _paso(6, "Tirante crítico" + (" y energía específica" if en_on else ""))
        st.latex(r"\frac{Q^2}{g}=\frac{A_c^3}{T_c}")
        if en_on:
            st.latex(rf"E=y+\frac{{V^2}}{{2g}}={y:.3f}+\frac{{{V:.3f}^2}}{{2(9.81)}}={E:.3f}\ \mathrm{{m}}")
            _res(f"Tirante crítico yc = {yc:.3f} m  |  Energía E = {E:.3f} m  |  Tirante alterno y₂ = {y2t}")
        else:
            _res(f"Tirante crítico yc = {yc:.3f} m")

    with st.container(border=True):
        _paso(7, "Verificación de velocidad")
        st.latex(rf"{vmin:.2f}\ \le\ V={V:.3f}\ \le\ {vmax:.2f}\ \mathrm{{m/s}}")
        _res(msg_v, "ok" if est == "ok" else "mal")

    with st.container(border=True):
        _paso(8, "Borde libre")
        if metodo.startswith("USBR"):
            st.latex(rf"BL=\sqrt{{C\,y}}=\sqrt{{{C}\times{y:.3f}}}={BL:.3f}\ \mathrm{{m}}")
        elif metodo.startswith("Máximo"):
            d = 5 if rev else 3
            st.latex(rf"BL=\frac{{y}}{{{d}}}=\frac{{{y:.3f}}}{{{d}}}={BL:.3f}\ \mathrm{{m}}")
        if not (metodo.startswith("USBR") or metodo.startswith("Máximo")):
            st.markdown(f"**{f_bl}**")
        st.caption(crit)
        _res(f"BL = {BL:.3f} m | H = y + BL = {y + BL:.3f} m")


# ---------------- Reporte PDF ----------------
def datos_dibujo(s, y, H):
    if isinstance(s, (mh.Circular, mh.Parabolica)):
        per = perfil_cerrado(s)
        return dict(linea=per, agua=[_recortar(per, y)], top=H, nivel=y)
    if isinstance(s, mh.Poligonal):
        L, agua = s.zmin + y, []
        for i in range(len(s.pts) - 1):
            (x1, z1), (x2, z2) = s.pts[i], s.pts[i + 1]
            if min(z1, z2) < L:
                a, b_ = (x1, z1), (x2, z2)
                if z1 > L: a = (x1 + (L - z1) / (z2 - z1) * (x2 - x1), L)
                if z2 > L: b_ = (x1 + (L - z1) / (z2 - z1) * (x2 - x1), L)
                agua.append([a, b_, (b_[0], L), (a[0], L)])
        return dict(linea=s.pts, agua=agua, top=s.zmin + H, nivel=L)
    hb = s.b / 2; xl = hb + s.z * H; hw = hb + s.z * y
    return dict(linea=[(-xl, H), (-hb, 0), (hb, 0), (xl, H)], agua=[[(-hb, 0), (hb, 0), (hw, y), (-hw, y)]], top=H, nivel=y)


if modo:
    if POLI: det = s.detalle(y)
    else: det = [(a_, p_, n_) for a_, (p_, n_) in zip((["Fondo"] if s.b > 0 else []) + (["Paredes"] if modo == 1 else ["Pared izquierda", "Pared derecha"]), partes(y))]
else: det = []
H = y + BL
grupos = [("Resultado principal", [(rotulo_y, f"{y:.3f} m"), ("Caudal Q", f"{Q:.3f} m³/s"), ("Pendiente crítica Sc" if inc == "Tirante crítico (yc)" else "Pendiente S", f"{S:.3f} m/m")] + ([("Ancho de solera b", f"{s.b:.3f} m")] if (modulo == "diseno" and tipo != "Triangular") else [])),
          ("Geometría del flujo", [("Área A", f"{A:.3f} m²"), ("Perímetro mojado P", f"{P:.3f} m"), ("Espejo de agua T", f"{T:.3f} m"), ("Radio hidráulico R", f"{R:.3f} m"), ("Profundidad hidráulica A/T", f"{A / T:.3f} m")]),
          ("Rugosidad", [("n usada", f"{n:.3f}"), ("Origen", ORIGEN)]),
          ("Velocidad y régimen", [("Velocidad V", f"{V:.3f} m/s"), ("Número de Froude F", f"{F:.3f}"), ("Régimen", reg), ("Tirante crítico yc", f"{yc:.3f} m")]),
          *([("Energía específica", [("Energía específica E", f"{E:.3f} m"), ("Energía mínima Emín", f"{Ec:.3f} m"), ("Tirante alterno y₂", y2t)])] if en_on else []),
          ("Borde libre", [("BL requerido", f"{BL:.3f} m"), ("BL disponible = altura − y", f"{BLd:.3f} m"), ("Altura de la sección", f"{s.altura:.3f} m")] if FIJA else [("Borde libre BL", f"{BL:.3f} m"), ("Altura total H = y + BL", f"{H:.3f} m"), ("BL como % de y", f"{100 * BL / y:.1f} %")])]
ctx = dict(titulo=TITULOS[modulo], tipo=tipo, dims=(f", b = {s.b:.3f} m" if s.b > 0 else "") + (f", z = {s.z:.3f}" if s.z > 0 else "") + (f", D = {Dc:.3f} m" if tipo == "Circular" else "") + (f", T = {Tpar:.3f} m, H = {Hpar:.3f} m" if tipo == "Parabólica" else ""), Q=Q, S=S, inc=inc.split(" (")[0].lower(),
           horton=det, n_base=n_base(y), cowan=(n_base(y), k1, k2, k3, k4, k5) if cow_on else None, material=mats[0] if mats else "", n=n,
           origen=ORIGEN, metodo=metodo_sol, C=Cc_, iter=len(it) if it else 0,
           y=y, A=A, P=P, T=T, R=R, V=V, F=F, reg=reg, msg_reg=msg_reg, E=E, Ec=Ec, y2=y2, y2t=y2t, yc=yc, vmin=vmin, vmax=vmax, msg_v=msg_v, bl_formula=f_bl, crit=crit, BL=BL, H=H,
           altura=(s.altura if FIJA else None), aviso=mh.validar_pendiente(S), sub=(mh.detalle_subareas(s, y, S, metodo_sol, p_met) if SUBAREAS else None), energia=en_on, metodo_bl=metodo, comp_bl=comp, grupos=grupos, dibujo=datos_dibujo(s, y, H),
           diseno=dict(crit=crit_d, f=mh.FACTORES[crit_d], m=m_d, y=y_d, b=s.b) if (modulo == "diseno" and tipo != "Triangular") else None,
           parametros=dict(b=s.b, z=s.z, Ac=s.A(yc), Tc=s.T(yc),
                           perfil_puntos=pts_ if POLI else None, D=Dc if tipo == "Circular" else None, T0=Tpar if tipo == "Parabólica" else None,
                           H0=Hpar if tipo == "Parabólica" else None, metodo_param=p_met,
                           iteraciones=it or []))
with pdf_slot:
    st.download_button("📄 Descargar reporte en PDF", data=reporte_pdf.generar(ctx), file_name="HIDROSA_memoria_calculo.pdf", mime="application/pdf")

    






