import streamlit as st
import google.generativeai as genai
from PIL import Image
import utils_login as login  # <--- Reutilizamos tu módulo de seguridad blindado

# ==========================================
# 📠 GENERADOR DE PDF
# ==========================================
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
    texto_limpio = contenido.replace('**', '').replace('__', '')
    
    # Codificación segura para español (acentos, ñ)
    texto_seguro = texto_limpio.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 7, txt=texto_seguro)
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(
    page_title="Quantum Reporter",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configuración de API Key (Usa las de prueba o producción según tu secrets.toml)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("Error: No se encontró la GOOGLE_API_KEY en los secretos.")
    st.stop()

# ==========================================
# 2. ESTILO VISUAL "QUANTUM" (El mismo look profesional)
# ==========================================
def inyectar_estilo_quantum():
    st.markdown("""
        <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        div.stButton > button {
            background-color: #002b36;
            color: #00d4ff;
            border: 1px solid #00d4ff;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            background-color: #00d4ff;
            color: #002b36;
            border-color: #FAFAFA;
            box-shadow: 0 0 15px #00d4ff;
        }
        h1, h2, h3 {
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 300; 
        }
        .reporte-box {
            background-color: #161b22;
            padding: 20px;
            border-left: 5px solid #00d4ff;
            border-radius: 5px;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

inyectar_estilo_quantum()

# ==========================================
# 3. ZONA DE SEGURIDAD (Login Modular)
# ==========================================
usuario = login.validar_acceso()
if not usuario:
    st.stop()

# ==========================================
# 🚀 AQUI COMIENZA QUANTUM REPORTER
# ==========================================

# Encabezado
col1, col2 = st.columns([1, 5])
with col1:
    st.markdown("# 🕵️‍♂️")
with col2:
    st.markdown("# Quantum Reporter")
    st.caption(f"Panel de Investigación Activo | Agente: **{usuario}**")

st.markdown("---")

# Instrucciones del Sistema (El Cerebro Periodístico)
SYSTEM_PROMPT = """
Eres Quantum Reporter, un periodista de investigación de élite.
Tu misión es analizar la información proporcionada (texto o imagen) con rigor científico y ética periodística.

NORMAS OBLIGATORIAS:
1. Cita las fuentes basándote SOLO si hay evidencia. Si no hay fuente, decláralo.
2. Usa fuentes de la prensa nacional e internacional y citalas.
3. No inventes datos (Cero alucinaciones).
3. Mantén un tono neutral, objetivo y profesional.
4. Estructura: Titular, Lead (Resumen), Análisis de Hechos, Conclusión.
5. AL FINAL: Genera un "PROMPT DE IMAGEN" detallado, en inglés, para generar una ilustración fotorrealista del tema.
"""

# Selección de Fuente
tipo_investigacion = st.radio("Selecciona el tipo de evidencia:", ["📝 Texto / Noticia", "📸 Imagen / Documento"], horizontal=True)

user_input = ""
imagen_procesar = None

if "Texto" in tipo_investigacion:
    user_input = st.text_area("Pega aquí el texto, noticia o cable a investigar:", height=200)

else:
    uploaded_file = st.file_uploader("Sube una imagen (Foto, Captura, Documento escaneado)", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        imagen_procesar = Image.open(uploaded_file)
        st.image(imagen_procesar, caption="Evidencia Cargada", width=400)
        user_input = st.text_input("Contexto adicional (Opcional):", placeholder="¿Qué quieres saber de esta imagen?")

# Botón de Acción
if st.button("🔍 Iniciar Investigación Profunda"):
    if not user_input and not imagen_procesar:
        st.warning("⚠️ Por favor ingresa texto o sube una evidencia visual.")
    else:
        with st.spinner("🕵️‍♂️ Analizando hechos, verificando fuentes y redactando reporte..."):
            try:
                # Configuración del Modelo (Usamos Gemini Pro Vision o Texto)
                model = genai.GenerativeModel('gemini-2.0-flash') # Modelo rápido y potente
                
                response = None
                
                # A) Análisis de Solo Texto
                if imagen_procesar is None:
                    prompt_completo = f"{SYSTEM_PROMPT}\n\nANALIZA ESTA INFORMACIÓN:\n{user_input}"
                    response = model.generate_content(prompt_completo)
                
                # B) Análisis de Imagen + Texto
                else:
                    prompt_completo = [SYSTEM_PROMPT, "ANALIZA ESTA IMAGEN Y EL CONTEXTO:", user_input if user_input else "Analiza todo lo visible.", imagen_procesar]
                    response = model.generate_content(prompt_completo)
                
                # Mostrar Resultado
                st.markdown("### 📠 Reporte Confidencial")
                st.markdown('<div class="reporte-box">', unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown('</div>', unsafe_allow_html=True)

                # --- GENERACIÓN DE PDF ---
                st.success("✅ Investigación completada.")
                
                # Creamos el PDF en memoria
                pdf_bytes = crear_pdf_reporte(response.text, usuario)
                
                # Botón de Descarga
                st.download_button(
                    label="📄 Descargar Informe Oficial (PDF)",
                    data=pdf_bytes,
                    file_name=f"Reporte_Quantum_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf"
                )
                
                # Botón de Copiar (Truco visual)
                st.caption("Fin del reporte. Verifica la información antes de publicar.")

            except Exception as e:
                st.error(f"❌ Error en la investigación: {str(e)}")
                if "429" in str(e):
                    st.warning("⏳ Límite de velocidad alcanzado (API Gratuita). Espera un momento.")

# Pie de página
st.markdown("---")
st.caption("Quantum Reporter v1.0 | Ethical AI Journalism")
