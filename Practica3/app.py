import streamlit as st
import time

# Configuración de la página
st.set_page_config(page_title="Práctica 3 - ECDH", page_icon="🔐", layout="centered")

st.title("🔐 Práctica 3: Toy ECDH")
st.markdown("**Alumno:** López Reyes José Roberto | **Grupo:** 7CM1")
st.markdown("---")


def add_points(p, q, n):
    if p == (0, 1, 0):
        return q
    if q == (0, 1, 0):
        return p

    x1, x2, y1, y2 = p[0], q[0], p[1], q[1]

    if x1 == x2:
        if (y1 + y2) % n == 0:
            return (0, 1, 0)
        elif y1 == y2:
            return (0, 1, 0) #

    numerador = (y2 - y1) % n
    denominador_inverso = pow((x2 - x1) % n, -1, n)
    pendiente = (numerador * denominador_inverso) % n

    x3 = (pow(pendiente, 2, n) - x1 - x2) % n
    y3 = (pendiente * (x1 - x3) - y1) % n

    return (x3, y3, 1)

def double_point(p, n, a):
    if p == (0, 1, 0):
        return p

    x1, x2 = p[0], p[0]
    y1, y2 = p[1], p[1]

    if y1 == 0:
        return (0, 1, 0)

    pendiente = ((3 * pow(x1, 2, n) + a) % n) * pow((2 * y1), -1, n)

    x3 = (pow(pendiente, 2, n) - x1 - x2) % n
    y3 = (pendiente * (x1 - x3) - y1) % n

    return (x3, y3, 1)

def right_left_bin_ui(k, P, p, a):
    k_bin = bin(k)[2:]
    logs = [f"Binario (Right-to-Left): {k_bin}"]
    Q = (0, 1, 0)
    logs.append(f"Estado Inicial: Q = {Q}")

    for i in range(len(k_bin)):
        logs.append(f"\n--- Iteración {i} ---")
        if int(k_bin[len(k_bin) - 1 - i]) == 1:
            logs.append("Bit = 1 -> Se va a efectuar adición de puntos (Q + P).")
            Q = add_points(P, Q, p)
        P = double_point(P, p, a)
        logs.append(f"Q = {Q}")
        logs.append(f"P = {P}")

    return Q, logs

def left_right_bin_ui(k, P, p, a):
    k_bin = bin(k)[2:]
    logs = [f"Binario (Left-to-Right): {k_bin}"]
    Q = (0, 1, 0)
    logs.append(f"Estado Inicial: Q = {Q}")

    for i in range(len(k_bin)):
        logs.append(f"\n--- Iteración {i} ---")
        Q = double_point(Q, p, a)
        if int(k_bin[i]) == 1:
            logs.append("Bit = 1 -> Se va a efectuar adición de puntos (Q + P).")
            Q = add_points(P, Q, p)
        logs.append(f"Q = {Q}")
        logs.append(f"P = {P}")

    return Q, logs

tab_rl, tab_lr, tab_ecdh = st.tabs([
    "Right-to-Left Method",
    "Left-to-Right Method",
    "Simulación ECDH"
])

with tab_rl:
    st.header("Algoritmo 1: Right-to-Left Binary Method")
    st.write("Calcula $kP$ leyendo los bits de derecha a izquierda.")

    col1, col2, col3 = st.columns(3)
    p_rl = col1.number_input("Módulo $p$", value=17, step=1, key="p_rl")
    a_rl = col2.number_input("Coeficiente $a$", value=2, step=1, key="a_rl")
    k_rl = col3.number_input("Escalar $k$", value=15, step=1, key="k_rl")

    st.subheader("Punto $P$")
    col4, col5 = st.columns(2)
    x_rl = col4.number_input("Coordenada $x$", value=5, step=1, key="x_rl")
    y_rl = col5.number_input("Coordenada $y$", value=1, step=1, key="y_rl")

    if st.button("Calcular con Algoritmo 1", type="primary"):
        with st.spinner("Calculando..."):
            inicio = time.perf_counter()
            Q_res, logs = right_left_bin_ui(k_rl, (x_rl, y_rl, 1), p_rl, a_rl)
            fin = time.perf_counter()

            st.success("¡Cálculo exitoso!")
            st.latex(f"Q = {k_rl}P = {Q_res}")
            st.metric("Tiempo de ejecución", f"{fin - inicio:.6f} s")

            with st.expander("Ver desglose de iteraciones (Para el reporte)"):
                for log in logs:
                    st.text(log)

with tab_lr:
    st.header("Algoritmo 2: Left-to-Right Binary Method")
    st.write("Calcula $kP$ leyendo los bits de izquierda a derecha.")

    col6, col7, col8 = st.columns(3)
    p_lr = col6.number_input("Módulo $p$", value=17, step=1, key="p_lr")
    a_lr = col7.number_input("Coeficiente $a$", value=2, step=1, key="a_lr")
    k_lr = col8.number_input("Escalar $k$", value=15, step=1, key="k_lr")

    st.subheader("Punto $P$")
    col9, col10 = st.columns(2)
    x_lr = col9.number_input("Coordenada $x$", value=5, step=1, key="x_lr")
    y_lr = col10.number_input("Coordenada $y$", value=1, step=1, key="y_lr")

    if st.button("Calcular con Algoritmo 2", type="primary"):
        with st.spinner("Calculando..."):
            inicio = time.perf_counter()
            Q_res, logs = left_right_bin_ui(k_lr, (x_lr, y_lr, 1), p_lr, a_lr)
            fin = time.perf_counter()

            st.success("¡Cálculo exitoso!")
            st.latex(f"Q = {k_lr}P = {Q_res}")
            st.metric("Tiempo de ejecución", f"{fin - inicio:.6f} s")

            with st.expander("Ver desglose de iteraciones (Para el reporte)"):
                for log in logs:
                    st.text(log)

with tab_ecdh:
    st.header("Simulación de Intercambio de Llaves (ECDH)")
    st.write("Calcula tu llave pública o recupera el secreto compartido.")

    st.subheader("Parámetros Públicos")
    col11, col12, col13 = st.columns(3)
    p_ecdh = col11.number_input("Módulo $p$", value=17, step=1, key="p_ecdh")
    a_ecdh = col12.number_input("Coeficiente $a$", value=2, step=1, key="a_ecdh")
    b_ecdh = col13.number_input("Coeficiente $b$", value=2, step=1, key="b_ecdh")

    col14, col15 = st.columns(2)
    xg = col14.number_input("Generador $x_G$", value=5, step=1)
    yg = col15.number_input("Generador $y_G$", value=1, step=1)

    st.divider()

    opcion_ecdh = st.radio(
        "¿Qué deseas hacer?",
        ("1. Compute kG (Generar mi llave pública)", "2. Retrieve secret (Calcular secreto compartido)")
    )

    k_priv = st.number_input("Tu llave privada $k$", value=10, step=1)

    if opcion_ecdh == "1. Compute kG (Generar mi llave pública)":
        if st.button("Generar Llave Pública", type="primary"):
            with st.spinner("Computando kG..."):
                llave_pub, _ = right_left_bin_ui(k_priv, (xg, yg, 1), p_ecdh, a_ecdh)
                st.success("Esta es la llave pública que debes enviar a tu compañero:")
                st.latex(f"kG = {llave_pub}")

    else:
        st.subheader("Llave pública recibida del compañero")
        col16, col17, col18 = st.columns(3)
        x_rec = col16.number_input("Coordenada $x$", value=0, step=1)
        y_rec = col17.number_input("Coordenada $y$", value=6, step=1)
        z_rec = col18.number_input("Coordenada $z$", value=1, step=1)

        if st.button("Recuperar Secreto", type="primary"):
            with st.spinner("Calculando secreto compartido..."):
                secreto, _ = left_right_bin_ui(k_priv, (x_rec, y_rec, z_rec), p_ecdh, a_ecdh)
                st.success("¡Secreto compartido recuperado exitosamente!")
                st.latex(f"Secreto = {secreto}")
