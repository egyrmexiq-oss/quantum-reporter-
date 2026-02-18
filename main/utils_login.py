import streamlit as st
import time
import streamlit.components.v1 as components # Necesario para el Spline

def validar_acceso():
    """
    Maneja el login con seguridad anti-fuerza bruta + Estética Quantum.
    """
    
    # 1. Inicializar variables de seguridad
    if "intentos_fallidos" not in st.session_state:
        st.session_state.intentos_fallidos = 0
    if "login_bloqueado" not in st.session_state:
        st.session_state.login_bloqueado = False

    # 2. Verificar bloqueo
    if st.session_state.login_bloqueado:
        st.error("⛔ ACCESO BLOQUEADO: Demasiados intentos fallidos.")
        st.caption("Por seguridad, el sistema se ha cerrado temporalmente. Recarga la página (F5).")
        st.stop()

    # 3. Verificar si ya hay usuario logueado (Si sí, retornamos rápido)
    if "usuario_activo" in st.session_state and st.session_state.usuario_activo:
        return st.session_state.usuario_activo

    # ============================================
    # 🎨 4. INTERFAZ VISUAL (AQUÍ ESTÁ LA MAGIA)
    # ============================================
    
    # A) Título
    st.markdown("## 🔐 Quantum Supplements")
    st.caption("Solicita acceso por SMS o WhatsApp")

    # B) Onda Senoidal (Spline) - Integrada en el Login
    try:
        components.iframe("https://my.spline.design/claritystream-Vcf5uaN9MQgIR4VGFA5iU6Es/", height=350)
    except:
        pass

    # C) Audio Ambiental - Integrado en el Login
    st.audio("https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3", loop=True, autoplay=True)

    # ============================================
    # 📝 5. FORMULARIO DE ACCESO
    # ============================================
    with st.form("form_login"):
        clave_input = st.text_input("Ingresa tu Clave de Acceso:", type="password")
        submit = st.form_submit_button("Inicializar Sistema")

        if submit:
            # Retraso artificial (Tarpit)
            time.sleep(1) 
            
            clave_limpia = clave_input.strip()
            # Buscamos en la sección [access_keys] de secrets.toml
            claves_validas = st.secrets.get("access_keys", {})
            
            if clave_limpia in claves_validas:
                # ÉXITO
                rol = claves_validas[clave_limpia]
                st.session_state.usuario_activo = rol
                st.session_state.intentos_fallidos = 0
                st.success(f"Acceso Concedido: {rol}")
                time.sleep(0.5)
                st.rerun()
            else:
                # FALLO
                st.session_state.intentos_fallidos += 1
                restantes = 3 - st.session_state.intentos_fallidos
                
                if restantes <= 0:
                    st.session_state.login_bloqueado = True
                    st.error("⛔ Has excedido el número de intentos.")
                    st.rerun()
                else:
                    st.warning(f"Clave incorrecta. Intentos restantes: {restantes}")
                    time.sleep(st.session_state.intentos_fallidos) 
                    
    return None
