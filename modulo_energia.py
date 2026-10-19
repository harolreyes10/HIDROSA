import plotly.graph_objects as go
import streamlit as st
import motor_hidraulico as mh

MAR, ORO, TUR = "#0a1a3a", "#e3b341", "#4fb3a9"
CONFIG = {"scrollZoom": True, "displaylogo": False, "modeBarButtonsToRemove": ["zoom2d", "select2d", "lasso2d"]}


def curva(s, Q, y1, yc, y2):
    """Curva E–y: mismo conjunto de puntos y límites, presentación técnica renovada."""
    top = max(3 * yc, 1.5 * (y1 or 0), 1.2 * (y2 or 0))
    ys = [top * i / 300 for i in range(1, 301)]
    Ec = mh.energia(s, Q, yc)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[mh.energia(s, Q, t) for t in ys], y=ys,
        mode="lines", line=dict(color="#067F99", width=3.5),
        name="Energía específica · E(y)",
        hovertemplate="E = %{x:.3f} m<br>y = %{y:.3f} m<extra>Curva E–y</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[0, 3 * Ec], y=[0, 3 * Ec], mode="lines",
        line=dict(color="#94A3B8", width=2, dash="dash"), name="Referencia · E = y",
        hovertemplate="E = %{x:.3f} m<br>y = %{y:.3f} m<extra>E = y</extra>",
    ))
    pts = [(Ec, yc, f"yc = {yc:.3f} m", "#D48215")]
    if y1 is not None:
        pts.append((mh.energia(s, Q, y1), y1, f"y₁ = {y1:.3f} m", "#1C5EBC"))
    if y2 is not None:
        pts.append((mh.energia(s, Q, y2), y2, f"y₂ = {y2:.3f} m", "#7C3AED"))
    for x, yy, t, c in pts:
        fig.add_trace(go.Scatter(
            x=[x], y=[yy], mode="markers+text",
            text=[t], textposition="middle right",
            textfont=dict(color=c, size=12, family="Arial"),
            marker=dict(size=12 if c != "#D48215" else 14, color=c,
                        line=dict(color="#FFFFFF", width=2)),
            hovertemplate=f"{t}<br>E = %{{x:.3f}} m<extra></extra>", showlegend=False,
        ))
    # Guías visuales al mínimo, sin alterar los valores ni los trazos de cálculo.
    fig.add_shape(type="line", x0=Ec, x1=Ec, y0=0, y1=yc,
                  line=dict(color="#D8A55F", width=1.3, dash="dot"))
    fig.add_shape(type="line", x0=0, x1=Ec, y0=yc, y1=yc,
                  line=dict(color="#D8A55F", width=1.3, dash="dot"))
    fig.update_layout(
        title=dict(text="Energía específica · Relación E–y", x=0.035, xanchor="left",
                   font=dict(size=17, color="#12354D")),
        height=500, plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)",
        dragmode="pan", hovermode="closest", font=dict(color="#27455A", size=12),
        legend=dict(orientation="h", x=0.01, y=1.08, xanchor="left", yanchor="bottom",
                    font=dict(size=11, color="#315169"), bgcolor="rgba(255,255,255,0)"),
        margin=dict(l=62, r=64, t=105, b=65),
        xaxis=dict(title="Energía específica, E (m)", range=[0, 3 * Ec],
                   gridcolor="#E9F0F4", zerolinecolor="#AEC2CE", showline=True,
                   linecolor="#B5C6D1", ticks="outside", tickcolor="#B5C6D1"),
        yaxis=dict(title="Tirante, y (m)", range=[0, top],
                   gridcolor="#E9F0F4", zerolinecolor="#AEC2CE", showline=True,
                   linecolor="#B5C6D1", ticks="outside", tickcolor="#B5C6D1"),
    )
    return fig


def datos_proyecto():
    """Datos generales del proyecto (se conservan al cambiar de cálculo)."""
    g = st.session_state.get("_proy", {})
    with st.expander("Datos del proyecto"):
        c1, c2 = st.columns(2); c3, c4 = st.columns(2)
        d = dict(nombre=c1.text_input("Proyecto", value=g.get("nombre", ""), key="w_proy_nombre"),
                 lugar=c2.text_input("Lugar", value=g.get("lugar", ""), key="w_proy_lugar"),
                 tramo=c3.text_input("Tramo", value=g.get("tramo", ""), key="w_proy_tramo"),
                 autor=c4.text_input("Elaborado por", value=g.get("autor", ""), key="w_proy_autor"))
    st.session_state["_proy"] = d
    return d


def render(modulo, dib=None):
    ss = st.session_state
    energia = modulo == "energia"
    st.markdown(f'<div class="barra-sup"><span class="titulo">LYCANAL PRO</span><small>{"Energía específica" if energia else "Tirante crítico"}</small></div>', unsafe_allow_html=True)
    datos_proyecto()
    izq, der = st.columns([1, 1.9], gap="large")
    with izq:
        st.markdown("### Sección")
        tipo = st.selectbox("Tipo", ["Rectangular", "Trapezoidal", "Triangular"])
        b = st.number_input("Ancho de solera b (m)", 0.0, value=0.3, step=0.1, format="%.3f") if tipo != "Triangular" else 0.0
        z = st.number_input("Talud z (H:V)", 0.0, value=1.0, step=0.25, format="%.3f") if tipo != "Rectangular" else 0.0
        st.markdown("### Datos hidráulicos")
        q1, q2 = st.columns([2, 1])
        Q = q1.number_input("Caudal Q", 0.0, value=0.3, format="%.3f") * (0.001 if q2.selectbox("Unidad Q", ["m³/s", "L/s"]) == "L/s" else 1)
        y = st.number_input("Tirante y (m)", 0.0, value=0.5, format="%.3f") if energia else None
        if st.button("← Menú de cálculos"):
            ss.pag = "menu"; st.rerun()
    errs = ([] if tipo == "Triangular" or b > 0 else ["El ancho de solera debe ser mayor que 0."]) + ([] if Q > 0 else ["El caudal debe ser mayor que 0."]) \
        + ([] if not energia or y > 0 else ["El tirante debe ser mayor que 0."])
    if errs:
        for e in errs: der.error(e)
        st.stop()
    s = mh.Seccion(tipo, b, z)
    yc = mh.tirante_critico(s, Q)
    Ac, Tc = s.A(yc), s.T(yc)
    Vc = Q / Ac; Ec = yc + Vc ** 2 / (2 * mh.G)
    y2 = mh.y_alterno(s, Q, y) if energia else None
    tab_sec, tab_curva, tab_res, tab_proc = der.tabs(["Sección", "Curva E–y", "Resultados", "Procedimiento"])
    with tab_sec:
        st.caption("🔍 Usa la rueda del mouse para hacer zoom, arrastra para desplazarte y doble clic para restablecer la vista.")
        st.plotly_chart(dib(s, yc, yc * 1.3, ("Concreto (acabado con llana)",) * 3, None), theme=None, config=CONFIG)
    with tab_curva:
        st.caption("🔍 Usa la rueda del mouse para hacer zoom, arrastra para desplazarte y doble clic para restablecer la vista.")
        st.plotly_chart(curva(s, Q, y, yc, y2), theme=None, config=CONFIG)
    def tarjetas(items):
        for i in range(0, len(items), 3):
            for col, (t, v) in zip(st.columns(3), items[i:i + 3]): col.metric(t, v)
    with tab_res:
        st.markdown('<div class="grupo" style="margin-top:6px">Estado crítico</div>', unsafe_allow_html=True)
        tarjetas([("Tirante crítico yc", f"{yc:.3f} m"), ("Área crítica Ac", f"{Ac:.3f} m²"), ("Espejo crítico Tc", f"{Tc:.3f} m"),
                  ("Velocidad crítica Vc", f"{Vc:.3f} m/s"), ("Energía mínima Emín", f"{Ec:.3f} m"), ("Froude", "1.000")])
        if energia:
            A, V = s.A(y), Q / s.A(y); F = mh.froude(s, Q, y); reg, msg = mh.regimen(F)
            st.markdown('<div class="grupo">Tirante dado y tirante alterno</div>', unsafe_allow_html=True)
            tarjetas([("Energía específica E", f"{mh.energia(s, Q, y):.3f} m"), ("Tirante alterno y₂", f"{y2:.3f} m"), ("Régimen", reg),
                      ("Velocidad V", f"{V:.3f} m/s"), ("Froude F", f"{F:.3f}")])
            st.write(""); st.info(msg)
    with tab_proc:
        st.latex(r"\frac{Q^2}{g}=\frac{A_c^3}{T_c}")
        st.latex(rf"\frac{{{Q:.3f}^2}}{{9.81}}=\frac{{{Ac:.3f}^3}}{{{Tc:.3f}}}\ \Rightarrow\ y_c={yc:.3f}\ \mathrm{{m}}")
        st.latex(rf"E_{{min}}=y_c+\frac{{V_c^2}}{{2g}}={yc:.3f}+\frac{{{Vc:.3f}^2}}{{2(9.81)}}={Ec:.3f}\ \mathrm{{m}}")
        if energia:
            st.latex(rf"E=y+\frac{{V^2}}{{2g}}={mh.energia(s, Q, y):.3f}\ \mathrm{{m}}\qquad E(y_1)=E(y_2)\Rightarrow y_2={y2:.3f}\ \mathrm{{m}}")

            