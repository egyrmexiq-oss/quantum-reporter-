import streamlit as st
import google.generativeai as genai
from PIL import Image
from fpdf import FPDF
from datetime import datetime
import utils_login as login 

# ==========================================
# 1. CONFIGURACIÓN E IMPORTACIONES
# ==========================================
st.set_page_config(page_title="Quantum Reporter Chat", page_icon="🕵️‍♂️", layout="wide")

# Configurar API
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("Falta la API Key en secrets.toml")
    st.stop()

# ==========================================
# 2. ESTILOS Y PDF
# ==========================================
def inyectar_estilo_quantum():
    st.markdown("""
        <style>
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        .stChatMessage { border: 1px solid #30363d; border-radius: 10px; padding: 10px; }
        </style>
    """, unsafe_allow_html=True)

inyectar_estilo_quantum()

def crear_pdf_reporte(historial, agente):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 14)
            self.cell(0, 10, 'Bitácora de Investigación - Quantum Reporter', 0, 1, 'C')
            self.ln(5)
    
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    # Imprimir solo el último análisis o todo el chat
    # Aquí imprimimos todo el intercambio para tener contexto
    for mensaje in historial:
        role = "REPORTERO" if mensaje["role"] == "model" else "INVESTIGADOR"
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 10, txt=f"[{role}]", ln=True)
        pdf.set_font("Arial", size=10)
        
        texto = mensaje["parts"][0] if isinstance(mensaje["parts"], list) else mensaje["parts"]
        texto_seguro = texto.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, txt=texto_seguro)
        pdf.ln(3)
        
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 3. SEGURIDAD
# ==========================================
usuario = login.validar_acceso()
if not usuario: st.stop()

# ==========================================
# 4. LÓGICA DEL CEREBRO (PROMPT)
# ==========================================

# Aquí está la MAGIA para que no sea tan estricto:
SYSTEM_INSTRUCTION = """
Eres Quantum Reporter, un periodista de investigación colaborador y perspicaz.
Tus instrucciones:
1. CONTEXTO: Usa la información que el usuario provee (texto o imágenes).
2. FLEXIBILIDAD: Si el usuario da un dato incorrecto (ej. fecha errónea), NO digas simplemente "no hay datos". BUSCA en tu conocimiento general y sugiere correcciones ("No encuentro registros en 1990, ¿quizás te refieres al evento de 1992?").
3. MEMORIA: Recuerda lo que hemos hablado en este chat.
4. FORMATO: Cuando des una conclusión final, usa estructura periodística (Titular, Lead, Cuerpo).
5. TONO: Profesional, objetivo, pero conversacional y útil.
"""

# ==========================================
# 5. INTERFAZ DE CHAT
# ==========================================

# A) Barra Lateral para Evidencias (Contexto Persistente)
with st.sidebar:
    st.title("🗄️ Sala de Evidencias")
    st.caption("Sube aquí los documentos base para que el Reportero los tenga siempre presentes.")
    
    evidencia_texto = st.text_area("Pegar Texto Base / Cable:", height=150)
    uploaded_file = st.file_uploader("Subir Imagen", type=["jpg", "png", "jpeg"])
    
    imagen_pil = None
    if uploaded_file:
        imagen_pil = Image.open(uploaded_file)
        st.image(imagen_pil, caption="Evidencia Visual", use_container_width=True)

    if st.button("🗑️ Borrar Memoria / Nueva Sesión"):
        st.session_state.chat_history = []
        st.rerun()

    # Botón PDF (Descarga toda la charla)
    if "chat_history" in st.session_state and len(st.session_state.chat_history) > 0:
        st.markdown("---")
        pdf_bytes = crear_pdf_reporte(st.session_state.chat_history, usuario)
        st.download_button("📄 Descargar Bitácora PDF", pdf_bytes, "Reporte_Investigacion.pdf", "application/pdf")

# B) Inicialización del Chat en Memoria
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# C) Configurar Modelo con Memoria
model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_INSTRUCTION)
chat = model.start_chat(history=st.session_state.chat_history)

# D) Mostrar Historial en Pantalla
st.markdown("### 💬 Canal Seguro con Reportero")

for message in st.session_state.chat_history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# E) INPUT DE USUARIO (La conversación)
if prompt := st.chat_input("Escribe tu instrucción o pregunta..."):
    
    # 1. Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Construir el mensaje completo (Prompt + Evidencia de la sidebar)
    #    Solo enviamos la evidencia si es la primera vez o si el usuario la acaba de cambiar,
    #    pero para simplificar, la adjuntamos como contexto oculto en este turno.
    
    contenido_mensaje = [prompt]
    if evidencia_texto:
        contenido_mensaje.append(f"\n[CONTEXTO DE EVIDENCIA: {evidencia_texto}]")
    if imagen_pil:
        contenido_mensaje.append(imagen_pil)

    # 3. Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("Analizando archivos y redactando..."):
            try:
                response = chat.send_message(contenido_mensaje)
                st.markdown(response.text)
                
                # Guardar en memoria de sesión para que no se borre al refrescar
                st.session_state.chat_history = chat.history
                
            except Exception as e:
                st.error(f"Error de conexión: {e}")
