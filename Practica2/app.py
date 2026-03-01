import streamlit as st
import time

from dlp_ec import fold_point, dlp_sol

st.set_page_config(page_title="Práctica 2 - ECC", page_icon="🔐", layout="centered")

st.title("🔐 Práctica 2: DLP Over Elliptic Curves")
st.markdown("**Alumno:** López Reyes José Roberto | **Grupo:** 7CM1")
st.markdown("---")

tab_kp, tab_dlp = st.tabs(["Calculadora de Puntos ($kP$)", "Romper DLP (Fuerza Bruta)"])

with tab_kp:
    st.header("Cálculo de $kP$")
    st.write("Calcula el producto escalar de un punto en la curva $E: y^2 = x^3 + ax + b \pmod p$.")

    col1, col2, col3 = st.columns(3)
    p_kp = col1.number_input("Módulo $p$", value=17, step=1, key="p_kp")
    a_kp = col2.number_input("Coeficiente $a$", value=2, step=1, key="a_kp")
    b_kp = col3.number_input("Coeficiente $b$", value=2, step=1, key="b_kp")

    st.subheader("Punto $P$")
    col4, col5, col6 = st.columns(3)
    x_kp = col4.number_input("Coordenada $x$", value=5, step=1, key="x_kp")
    y_kp = col5.number_input("Coordenada $y$", value=1, step=1, key="y_kp")
    z_kp = col6.number_input("Coordenada $z$", value=1, step=1, key="z_kp")

    k_val = st.number_input("Escalar $k$ (Debe ser > 2)", value=3, step=1)

    if st.button("Calcular $kP$", type="primary"):
        P_punto = (x_kp, y_kp, z_kp)

        with st.spinner("Calculando punto..."):
            resultado = fold_point(a_kp, b_kp, p_kp, P_punto, k_val)

            if resultado == (-1, -1, -1):
                st.error("Error en el cálculo. Verifica que la curva no sea singular y que $k > 2$.")
            else:
                st.success("¡Cálculo exitoso!")
                st.latex(f"{k_val}P = {resultado}")

with tab_dlp:
    st.header("Resolución de ECDLP")
    st.write("Encuentra el valor de $k$ tal que $P = kG$ usando fuerza bruta.")

    col7, col8, col9 = st.columns(3)
    p_dlp = col7.number_input("Módulo $p$", value=1048583, step=1, key="p_dlp")
    a_dlp = col8.number_input("Coeficiente $a$", value=1, step=1, key="a_dlp")
    b_dlp = col9.number_input("Coeficiente $b$", value=1, step=1, key="b_dlp")

    st.subheader("Generador $G$")
    col10, col11, col12 = st.columns(3)
    xg = col10.number_input("$x_G$", value=531691, step=1)
    yg = col11.number_input("$y_G$", value=384179, step=1)
    zg = col12.number_input("$z_G$", value=1, step=1)

    st.subheader("Punto Objetivo $P$")
    col13, col14, col15 = st.columns(3)
    xp = col13.number_input("$x_P$", value=1006535, step=1)
    yp = col14.number_input("$y_P$", value=412100, step=1)
    zp = col15.number_input("$z_P$", value=1, step=1)

    st.warning(
        "⚠️ **Aviso:** Si el módulo $p$ es muy grande (ej. inciso C en adelante), la interfaz de Streamlit podría quedarse cargando por un largo rato debido al ataque de fuerza bruta.")

    if st.button("Romper DLP", type="primary"):
        G_punto = (xg, yg, zg)
        P_punto = (xp, yp, zp)

        st.info("Revisa la terminal (consola) para ver los mensajes de progreso cada 100,000 iteraciones.")

        with st.spinner("Rompiendo criptografía con fuerza bruta... ⏳"):
            inicio = time.perf_counter()
            k_encontrada = dlp_sol(a_dlp, b_dlp, p_dlp, G_punto, P_punto)
            fin = time.perf_counter()

            tiempo_total = fin - inicio

            if k_encontrada:
                st.success(f"¡Logaritmo Discreto encontrado! 🎉")
                st.latex(f"k = {k_encontrada}")

                metrica1, metrica2 = st.columns(2)
                metrica1.metric("Tiempo de ejecución", f"{tiempo_total:.4f} s")
                rendimiento = k_encontrada / tiempo_total if tiempo_total > 0 else 0
                metrica2.metric("Rendimiento", f"{rendimiento:,.0f} op/s")
            else:
                st.error("No se encontró solución o se alcanzó el punto al infinito.")