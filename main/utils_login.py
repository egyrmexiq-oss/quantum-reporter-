import streamlit as st
import time
import streamlit.components.v1 as components # Necesario para el Spline

from fpdf import FPDF
from datetime import datetime

def crear_pdf_reporte(contenido, agente):
    class PDF(FPDF):
        def header(self):
            # Logo o Título
            self.set_font('Arial', 'B', 16)
            self.cell(0, 10, 'Quantum Reporter - Informe Confidencial', 0, 1, 'C')
            self.ln(5)
            
            # Subtítulo con fecha y agente
            self.set_font('Arial', 'I', 10)
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.cell(0, 10, f'Fecha: {fecha} | Agente Investigador: {agente}', 0, 1, 'C')
            self.line(10, 35, 200, 35) # Línea separadora
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()} - Generado por Quantum Reporter AI', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Título del Reporte
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "ANÁLISIS DE INTELIGENCIA", 0, 1)
    pdf.ln(2)
    
    # Cuerpo del Texto
    pdf.set_font("Arial", size=11)
    
    # Limpieza de caracteres para FPDF (Evita errores con emojis o símbolos raros)
    # Reemplazamos los asteriscos de Markdown por nada o puntos para que se lea mejor
    texto_limpio = contenido.replace('**', '').replace('__', '')
    
    # Codificación segura para español (acentos, ñ)
    texto_seguro = texto_limpio.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 7, txt=texto_seguro)
    
    return pdf.output(dest='S').encode('latin-1')

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
    st.markdown("## 🔐 Quantum Reporter")
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
