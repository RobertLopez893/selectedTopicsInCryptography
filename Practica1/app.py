import streamlit as st

from elliptic_curves import find_a_b, find_by_bits, rational_points, add_points, double_point

st.set_page_config(page_title="Práctica 1 - ECC", page_icon="🔐", layout="centered")

st.title("🔐 Práctica 1: Elliptic Curves")
st.markdown("**Alumno:** López Reyes José Roberto | **Grupo:** 7CM1")
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Curvas Válidas",
    "Generar por Bits",
    "Puntos Racionales",
    "Sumar Puntos",
    "Doblar Punto"
])

with tab1:
    st.header("Encontrar curvas válidas")
    st.write("Calcula todas las parejas $(a, b)$ que forman una curva elíptica no singular sobre $\mathbb{Z}_p$.")

    p_tab1 = st.number_input("Ingresa un número primo $p$ (> 3):", value=5, step=1, key="p_tab1")

    if st.button("Buscar Curvas", key="btn_tab1", type="primary"):
        with st.spinner("Buscando..."):
            curvas = find_a_b(p_tab1)
            if curvas:
                st.success(f"¡Se encontraron {len(curvas)} curvas posibles!")
                with st.expander("Ver todas las combinaciones $(a, b)$"):
                    st.write(curvas)
            else:
                st.error("Verifica que el número ingresado sea un primo mayor a 3.")


with tab2:
    st.header("Generar Parámetros Seguros")
    st.write("Genera un módulo primo $p$ del tamaño especificado y encuentra una curva válida.")

    bits = st.number_input("Tamaño en bits (ej. 128, 256, 1024):", value=128, step=8, key="bits_tab2")

    if st.button("Generar", key="btn_tab2", type="primary"):
        with st.spinner(f"Generando primo de {bits} bits..."):
            try:
                p_gen, coefs = find_by_bits(bits)
                st.success("¡Parámetros generados con éxito!")
                st.write("**Módulo primo generado ($p$):**")
                st.code(p_gen)
                st.write(f"**Coeficientes:** $a = {coefs[0]}$, $b = {coefs[1]}$")
            except Exception as e:
                st.error(f"Error al generar: {e}. Asegúrate de tener instalada la librería pycryptodome.")

with tab3:
    st.header("Puntos Racionales")
    st.write("Calcula todos los puntos que pertenecen a la curva usando residuos cuadráticos.")

    col1, col2, col3 = st.columns(3)
    p_tab3 = col1.number_input("Primo $p$", value=17, step=1, key="p_tab3")
    a_tab3 = col2.number_input("Coef $a$", value=2, step=1, key="a_tab3")
    b_tab3 = col3.number_input("Coef $b$", value=2, step=1, key="b_tab3")

    if st.button("Calcular Puntos", key="btn_tab3", type="primary"):
        with st.spinner("Calculando..."):
            points = rational_points(p_tab3, a_tab3, b_tab3)
            if points:
                st.success(f"Se encontraron {len(points)} puntos racionales (incluyendo el punto al infinito).")
                with st.expander("Ver lista de puntos"):
                    st.write(points)

with tab4:
    st.header("Suma de Puntos ($P + Q$)")
    n_tab4 = st.number_input("Módulo $p$", value=17, step=1, key="n_tab4")

    col4, col5 = st.columns(2)
    with col4:
        st.subheader("Punto $P$")
        x1_t4 = st.number_input("$x_1$", value=5, step=1, key="x1_t4")
        y1_t4 = st.number_input("$y_1$", value=1, step=1, key="y1_t4")

    with col5:
        st.subheader("Punto $Q$")
        x2_t4 = st.number_input("$x_2$", value=0, step=1, key="x2_t4")
        y2_t4 = st.number_input("$y_2$", value=6, step=1, key="y2_t4")

    if st.button("Sumar $P + Q$", key="btn_tab4", type="primary"):
        P = (x1_t4, y1_t4, 1)
        Q = (x2_t4, y2_t4, 1)
        resultado = add_points(P, Q, n_tab4)
        st.success("Resultado de la suma:")
        st.latex(f"P + Q = {resultado}")

with tab5:
    st.header("Doblar un Punto ($2P$)")

    col6, col7 = st.columns(2)
    n_tab5 = col6.number_input("Módulo $p$", value=17, step=1, key="n_tab5")
    a_tab5 = col7.number_input("Coeficiente $a$", value=2, step=1, key="a_tab5")

    st.subheader("Punto $P$")
    col8, col9 = st.columns(2)
    x1_t5 = col8.number_input("$x_1$", value=5, step=1, key="x1_t5")
    y1_t5 = col9.number_input("$y_1$", value=1, step=1, key="y1_t5")

    if st.button("Doblar $P$", key="btn_tab5", type="primary"):
        P = (x1_t5, y1_t5, 1)
        resultado = double_point(P, n_tab5, a_tab5)
        st.success("Resultado del doble:")
        st.latex(f"2P = {resultado}")
