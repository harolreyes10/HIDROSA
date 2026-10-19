"""Ventana de ayuda inicial de HIDROSA.

No interviene en los cálculos, generación de figuras ni informes PDF.
"""
import streamlit as st


@st.dialog("Bienvenido a HIDROSA · Guía de uso", width="large")
def mostrar_guia_uso():
    st.markdown(
        '<div style="background:linear-gradient(100deg,#102A43,#11687A);padding:15px 18px;'
        'border-radius:11px;margin-bottom:13px;color:#fff">'
        '<div style="font-weight:800;font-size:22px;color:white">HIDROSA</div>'
        '<div style="font-size:12px;color:#CEEAF0;letter-spacing:.025em">'
        'ANÁLISIS, CÁLCULO Y DISEÑO DE CANALES ABIERTOS</div></div>',
        unsafe_allow_html=True,
    )
    st.write(
        "Esta guía explica cómo utilizar las funciones principales del programa. "
        "Puedes consultarla nuevamente desde **Guía de uso**, en la barra lateral."
    )

    paso_a_paso, operaciones, secciones, reporte = st.tabs([
        "Empezar", "Procedimientos", "Secciones y rugosidad", "Resultados y PDF"
    ])

    with paso_a_paso:
        st.markdown("**Flujo de trabajo recomendado**")
        st.markdown(
            "1. Abre un grupo desde los **menús superiores**.\n"
            "2. Elige qué deseas calcular: **tirante, caudal, pendiente, tirante crítico, energía o diseño**.\n"
            "3. Selecciona la **geometría del canal** e ingresa las dimensiones.\n"
            "4. Introduce los datos del flujo, la pendiente y los parámetros de **rugosidad** que pida la ventana.\n"
            "5. Revisa el **esquema de la sección**, los resultados y el procedimiento matemático.\n"
            "6. Descarga la **memoria de cálculo en PDF**."
        )
        st.info(
            "Los cálculos usan unidades del Sistema Internacional. "
            "Cuando corresponda, introduce la pendiente S en m/m: por ejemplo, "
            "S = 0.001 equivale a 0.1 %."
        )

    with operaciones:
        st.markdown("**Qué calcula cada opción de los menús superiores**")
        st.markdown(
            "- **Flujo uniforme → Tirante normal:** determina el tirante a partir de Q, S y la sección.\n"
            "- **Flujo uniforme → Caudal:** calcula Q a partir del tirante, la pendiente y la geometría.\n"
            "- **Flujo uniforme → Pendiente:** determina S conocidos Q, el tirante y la sección.\n"
            "- **Flujo crítico → Tirante crítico:** analiza la condición crítica y el régimen de flujo.\n"
            "- **Flujo crítico → Energía específica:** analiza E, la curva E–y y los tirantes característicos.\n"
            "- **Diseño → Diseño de sección:** dimensiona la geometría según el criterio elegido.\n"
            "- **Secciones especiales → Sección compuesta:** estudia perfiles por tramos o coordenadas, "
            "con materiales y rugosidades variables."
        )
        st.caption("Elige una operación según los datos conocidos y la incógnita del problema.")

    with secciones:
        st.markdown("**1. Selecciona la geometría**")
        st.write(
            "El formulario ofrece secciones rectangulares, trapezoidales, triangulares, "
            "circulares y parabólicas, además de perfiles definidos por coordenadas o tramos. "
            "Los campos de entrada cambian según la geometría seleccionada."
        )
        st.markdown("**2. Ingresa la rugosidad**")
        st.write(
            "Selecciona los materiales y el coeficiente de Manning n. "
            "Si corresponde, puedes aplicar las opciones de rugosidad compuesta, "
            "correcciones de Cowan o división en subáreas, según la ventana de cálculo."
        )
        st.markdown("**3. Comprueba el gráfico**")
        st.write(
            "El perfil muestra sus nodos (P1, P2, P3…), el contorno, "
            "el agua en celeste y las dimensiones hidráulicas disponibles. "
            "Asegúrate de que el nivel de agua y la geometría representen tu problema."
        )

    with reporte:
        st.markdown("**Consulta e interpreta los resultados**")
        st.markdown(
            "- **Área mojada (A):** superficie de la sección ocupada por agua.\n"
            "- **Perímetro mojado (P):** longitud del contorno en contacto con el agua.\n"
            "- **Radio hidráulico (R):** A/P.\n"
            "- **Espejo de agua (T):** ancho superficial del flujo.\n"
            "- **Velocidad (V) y Froude (Fr):** caracterización del flujo.\n"
            "- **Borde libre (BL):** distancia vertical disponible o requerida sobre el tirante."
        )
        st.markdown("**Exportar memoria de cálculo**")
        st.write(
            "Después de ingresar los datos válidos, revisa el desarrollo matemático "
            "y pulsa **«Descargar reporte en PDF»**. El archivo contiene los datos, "
            "el procedimiento y los resultados preparados por el programa."
        )
        st.warning(
            "Verifica las unidades, la selección de materiales y los criterios de diseño. "
            "Los resultados deben revisarse antes de aplicarlos en un proyecto real."
        )

    st.divider()
    izquierda, derecha = st.columns([1.4, 1])
    with izquierda:
        st.caption("Esta ventana se muestra una vez por sesión, al abrir la aplicación.")
    with derecha:
        if st.button("Comenzar a usar HIDROSA →", type="primary", width="stretch", key="hd_guia_comenzar"):
            st.rerun()
