import streamlit as st
import google.generativeai as genai
from PIL import Image
from fpdf import FPDF
from datetime import datetime
import utils_login as login 

# ==========================================
# 1. CONFIGURACIÓN E IMPORTACIONES
# ==========================================
st.set_page_config(
    page_title="Quantum Reporter Chat", 
    page_icon="🕵️‍♂️", 
    layout="wide",
    initial_sidebar_state="expanded" 
)

# Configurar API
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("Falta la API Key en secrets.toml")
    st.stop()

# ==========================================
# 2. ESTILOS Y PDF (ESTÉTICA MEJORADA)
# ==========================================
def inyectar_estilo_quantum():
    st.markdown("""
        <style>
        /* Fondo General */
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        
        /* Globos de Chat */
        .stChatMessage { 
            border: 1px solid #30363d; 
            border-radius: 10px; 
            padding: 10px; 
            background-color: #161b22; 
        }
        
        /* Barra Lateral */
        section[data-testid="stSidebar"] { 
            background-color: #0E1117; 
            border-right: 1px solid #30363d; 
        }

        /* --- NUEVO: MARCO PARA LA CAJA DE EVIDENCIAS --- */
        .stTextArea textarea {
            background-color: #161b22 !important; /* Fondo un poco más claro que la base */
            border: 1px solid #484f59 !important; /* Borde gris visible */
            border-radius: 8px !important;
            color: #FAFAFA !important;
        }
        
        /* Efecto al hacer clic en la caja (Focus) */
        .stTextArea textarea:focus {
            border: 1px solid #00d4ff !important; /* Borde AZUL al escribir */
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
        }
        
        /* Títulos de la Sidebar */
        [data-testid="stSidebar"] h3 {
            border-bottom: 2px solid #00d4ff;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
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
    
    for mensaje in historial:
        if mensaje["role"] == "user" or mensaje["role"] == "model":
            role = "REPORTERO" if mensaje["role"] == "model" else "INVESTIGADOR"
            
            pdf.set_font("Arial", "B", 10)
            if role == "REPORTERO":
                pdf.set_text_color(0, 0, 128)
            else:
                pdf.set_text_color(0, 100, 0)
            
            pdf.cell(0, 10, txt=f"[{role}]", ln=True)
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", size=10)
            
            texto = mensaje["content"]
            texto_seguro = texto.encode('latin-1', 'replace').decode('latin-1')
            
            pdf.multi_cell(0, 6, txt=texto_seguro)
            pdf.ln(3)
        
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 3. SEGURIDAD VISUAL 
# ==========================================
usuario = login.validar_acceso()

if not usuario:
    st.stop() 

# ==========================================
# 4. CEREBRO Y EVIDENCIA
# ==========================================

with st.sidebar:
    st.markdown("### 🗄️ Sala de Evidencias")
    st.caption("Los documentos cargados aquí serán la 'Verdad Base'.")
    
    # Aquí es donde se aplicará el nuevo estilo del borde
    evidencia_texto = st.text_area("Pegar Texto Base / Cable:", height=250, placeholder="Pega aquí el reporte, noticia o datos...")
    
    uploaded_file = st.file_uploader("Subir Imagen Evidencia", type=["jpg", "png", "jpeg"])
    
    imagen_pil = None
    if uploaded_file:
        imagen_pil = Image.open(uploaded_file)
        st.image(imagen_pil, caption="Evidencia Visual Activa", use_container_width=True)

    st.markdown("---")
    
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        pdf_bytes = crear_pdf_reporte(st.session_state.messages, usuario)
        st.download_button("📄 Descargar Bitácora PDF", pdf_bytes, "Reporte_Investigacion.pdf", "application/pdf")
    
    if st.button("🗑️ Nueva Investigación"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# GEM PROMPT (TU CEREBRO)
# ---------------------------------------------------------
GEM_PROMPT = """
Eres Quantum Reporter, un periodista de investigación de élite.
Tu objetivo es analizar la información proporcionada con rigor, ética y profundidad.
Si el usuario proporciona datos erróneos (como fechas), usa tu conocimiento general para sugerir correcciones amablemente.
Estructura tus respuestas de forma periodística (Titular, Lead, Cuerpo).
No inventes información que no esté en la evidencia, pero usa tu contexto histórico para enriquecer el análisis.
"""
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Quantum Reporter 🕵️‍♂️")
st.caption(f"Agente Activo: {usuario}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe tu instrucción de investigación..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analizando evidencias..."):
            try:
                input_parts = []
                input_parts.append(GEM_PROMPT)
                
                if evidencia_texto:
                    input_parts.append(f"\n[EVIDENCIA DOCUMENTAL PRINCIPAL]:\n{evidencia_texto}\n")
                if imagen_pil:
                    input_parts.append(imagen_pil)
                    input_parts.append("\n[NOTA: Analiza la imagen adjunta como parte de la evidencia]\n")

                history_context = "\n[HISTORIAL DE CHAT RECIENTE]:\n"
                for msg in st.session_state.messages[-5:]: 
                    history_context += f"{msg['role'].upper()}: {msg['content']}\n"
                input_parts.append(history_context)
                
                input_parts.append(f"\n[SOLICITUD ACTUAL]: {prompt}")

                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(input_parts)
                
                text_response = response.text
                st.markdown(text_response)
                
                st.session_state.messages.append({"role": "model", "content": text_response})

            except Exception as e:
                st.error(f"Error técnico: {str(e)}")
                if "429" in str(e): st.warning("Tráfico alto. Espera unos segundos.")
