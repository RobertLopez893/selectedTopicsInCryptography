import streamlit as st
from random import randint

# Importamos las funciones de tu archivo lógico
# Asegúrate de que tu archivo se llame dsa_logic.py
from dsa import gen_key_pair, gen_sign, verify_sign

st.set_page_config(page_title="Práctica 4 - DSA", page_icon="✍️", layout="centered")

st.title("✍️ Práctica 4: Digital Signature Algorithm (DSA)")
st.markdown("**Alumno:** López Reyes José Roberto | **Grupo:** 7CM1")
st.markdown("---")

# Creamos las tres pestañas de tu menú original
tab1, tab2, tab3 = st.tabs([
    "1. Proceso Automático Completo",
    "2. Generar Llaves y Firmar",
    "3. Verificación Manual"
])

# ==========================================
# PESTAÑA 1: Proceso Automático Completo
# ==========================================
with tab1:
    st.header("Simulación Completa de DSA")
    st.write("Esta opción genera las llaves, firma un mensaje aleatorio y verifica la firma en un solo paso.")

    if st.button("Ejecutar Proceso Completo", type="primary", key="btn_tab1"):
        with st.spinner("Generando llaves y firmando..."):
            # 1. Llaves
            d, p, q, g, beta = gen_key_pair()
            st.subheader("🔑 Par de Llaves Generado")
            st.write(f"**Llave Privada ($d$):** `{d}`")
            st.write(f"**Llave Pública ($p, q, g, \\beta$):**")
            st.code(f"p = {p}\nq = {q}\ng = {g}\nbeta = {beta}")

            # 2. Firma
            m = randint(1, q - 1)
            r, s = gen_sign(m, p, q, g, d)
            st.subheader("📝 Generación de Firma")
            st.write(f"Mensaje aleatorio generado ($m$): `{m}`")
            st.success(f"Firma resultante: $(r, s) = ({r}, {s})$")

            # 3. Verificación
            st.subheader("✅ Verificación")
            validation = verify_sign(p, q, g, beta, m, r, s)
            if validation:
                st.success("La firma es **VÁLIDA**.")
            else:
                st.error("La firma es **INVÁLIDA**.")

# ==========================================
# PESTAÑA 2: Generar Llaves y Firmar Mensaje
# ==========================================
with tab2:
    st.header("Firma de Mensaje Personalizado")
    st.write("Ingresa un mensaje (número entero). El sistema generará llaves nuevas y lo firmará.")

    m_input = st.number_input("Ingresa el mensaje $m$ (número entero positivo):", min_value=1, value=100, step=1)

    if st.button("Generar Llaves y Firmar", type="primary", key="btn_tab2"):
        with st.spinner("Procesando..."):
            d, p, q, g, beta = gen_key_pair()

            # Verificación del rango del mensaje
            if not 1 <= m_input <= q - 1:
                st.error(
                    f"Error: El mensaje $m$ debe estar entre 1 y {q - 1} (rango de $q$). Intenta con un número más pequeño o vuelve a generar.")
            else:
                st.subheader("🔑 Tus Llaves")
                st.write(f"**Llave Privada:** `{d}`")
                st.write(f"**Llave Pública:** $p={p}$, $q={q}$, $g={g}$, $\\beta={beta}$")

                r, s = gen_sign(m_input, p, q, g, d)
                if r is not None and s is not None:
                    st.subheader("📜 Firma Generada")
                    st.latex(f"r = {r}")
                    st.latex(f"s = {s}")
                    st.success("¡Firma generada exitosamente!")

# ==========================================
# PESTAÑA 3: Verificación de Firma Manual
# ==========================================
with tab3:
    st.header("Verificación de Firma Manual")
    st.write(
        "Ingresa los parámetros públicos, el mensaje y la firma para comprobar su autenticidad. (Se usan campos de texto para soportar números gigantes).")

    st.subheader("Parámetros Públicos")
    col1, col2 = st.columns(2)
    p_str = col1.text_input("Ingresa $p$:", value="23")
    q_str = col2.text_input("Ingresa $q$:", value="11")
    g_str = col1.text_input("Ingresa $g$:", value="4")
    beta_str = col2.text_input("Ingresa $\\beta$ (Llave pública):", value="18")

    st.subheader("Datos a Verificar")
    col3, col4, col5 = st.columns(3)
    m_str = col3.text_input("Mensaje ($m$):", value="5")
    r_str = col4.text_input("Firma ($r$):", value="9")
    s_str = col5.text_input("Firma ($s$):", value="3")

    if st.button("Verificar Firma", type="primary", key="btn_tab3"):
        try:
            # Convertimos a enteros de forma segura
            p_val = int(p_str)
            q_val = int(q_str)
            g_val = int(g_str)
            beta_val = int(beta_str)
            m_val = int(m_str)
            r_val = int(r_str)
            s_val = int(s_str)

            with st.spinner("Verificando matemáticas..."):
                validacion = verify_sign(p_val, q_val, g_val, beta_val, m_val, r_val, s_val)

                if validacion:
                    st.success("🎉 ¡Resultado: La firma es **VÁLIDA**!")
                else:
                    st.error("🚨 Resultado: La firma es **INVÁLIDA**.")

        except ValueError:
            st.error(
                "Error de formato: Asegúrate de ingresar únicamente números enteros válidos en todos los campos, sin espacios ni letras.")
