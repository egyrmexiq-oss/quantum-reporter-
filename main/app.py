import streamlit as st
import google.generativeai as genai
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# ⚙️ CONFIGURACIÓN DE PÁGINA
# ==========================================
# ==========================================
# 🔐 1. LOGIN DE SEGURIDAD
# ==========================================
st.set_page_config(page_title="Quantum Acsess Supplements", page_icon="💊")
if "usuario_activo" not in st.session_state: st.session_state.usuario_activo = None

# ==========================================
# 🔐 1. LOGIN DE SEGURIDAD
# ==========================================
if "usuario_activo" not in st.session_state: st.session_state.usuario_activo = None

if not st.session_state.usuario_activo:
    st.markdown("## 🔐 Quantum Supplements")
    
    # Animación 3D
    try: st.components.v1.iframe("https://my.spline.design/claritystream-Vcf5uaN9MQgIR4VGFA5iU6Es/", height=400)
    except: pass
    
    # Música
    st.audio("https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3", loop=True, autoplay=True)
    
    # 👇 AQUÍ ESTÁ EL MENSAJE NUEVO
    st.info("🔑 Para ingresar, usa la clave: **DEMO**")
    
    c = st.text_input("Clave de Acceso:", type="password")
    if st.button("Entrar"):
        # NOTA: Asegúrate de tener "DEMO" en tus 'secrets' o permite la entrada aquí
        # Modifiqué esto para que acepte "DEMO" directamente o busque en secrets
        if c.strip() == "DEMO" or (c.strip() in st.secrets["access_keys"]):
            # Si entra con DEMO, le ponemos un nombre genérico
            nombre = "Visitante" if c.strip() == "DEMO" else st.secrets["access_keys"][c.strip()]
            st.session_state.usuario_activo = nombre
            st.rerun()
        else: st.error("Acceso Denegado")
    st.stop()

# ==========================================
# 💎 2. CARGA DE DATOS
# ==========================================
try: genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except: st.error("Falta API Key")

URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTzh0kFdEwymIqv7sNd7dFpWCg09GtGipbYe0PMsKc_hzRbDoNLBHUk54ROdIceVGGZlYGeYM5HMgH0/pub?output=csv"
URL_FORMULARIO = "https://docs.google.com/forms/d/e/1FAIpQLSdQBMZymJhY1mdEfKavnPpYnypaQ67S5Fp8AJ54L5n2P-Fvqg/viewform?usp=header"

@st.cache_data(ttl=60)
def cargar_medicos():
    try:
        df = pd.read_csv(URL_GOOGLE_SHEET)
        df.columns = [c.strip().lower() for c in df.columns]
        mapa = {}
        for col in df.columns:
            if "nombre" in col: mapa[col] = "nombre"
            elif "especialidad" in col: mapa[col] = "especialidad"
            elif "descripci" in col: mapa[col] = "descripcion"
            elif "tel" in col: mapa[col] = "telefono"
            elif "ciudad" in col: mapa[col] = "ciudad"
            elif "aprobado" in col: mapa[col] = "aprobado"
        df = df.rename(columns=mapa)
        if 'aprobado' in df.columns:
            return df[df['aprobado'].astype(str).str.upper().str.contains('SI')].to_dict(orient='records')
        return []
    except: return []

TODOS_LOS_MEDICOS = cargar_medicos()

# Preparación de la IA
if TODOS_LOS_MEDICOS:
    ciudades = sorted(list(set(str(m.get('ciudad', 'General')).title() for m in TODOS_LOS_MEDICOS)))
    ciudades.insert(0, "Todas las Ubicaciones")
    
    info_medicos = [f"ID: {m.get('nombre')} | Esp: {m.get('especialidad')} | Cd: {m.get('ciudad')}" for m in TODOS_LOS_MEDICOS]
    TEXTO_DIRECTORIO = "\n".join(info_medicos)
    
    INSTRUCCION_EXTRA = f"""
    ERES EL "SENIOR ADVISOR DE QUANTUM SUPPLEMENTS". Tu especialidad es la suplementación estratégica, 
    el biohacking y la optimización del rendimiento humano (físico y mental).

    1. OBJETIVOS CLAROS: Si el usuario es vago, pregunta si busca enfoque, longevidad, sueño o energía.
    2. SINERGIAS: Explica cómo ciertos suplementos funcionan mejor juntos.
    3. SEGURIDAD: Advierte sobre no exceder dosis y consultar especialistas.
    4. RECOMENDACIÓN: Busca en esta lista: {{TEXTO_DIRECTORIO}} y recomienda al experto ideal.
    """
else:
    ciudades = ["Mundo"]
    INSTRUCCION_EXTRA = "Actúa como médico general."

# ==========================================
# 📱 3. BARRA LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    try: st.image("Logo_quantum.png", use_container_width=True)
    except: st.header("QUANTUM")
    
    st.success(f"Hola, {st.session_state.usuario_activo}")
    
    # Contador de Visitas
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #262730; padding: 10px; border-radius: 5px; text-align: center;">
        <span style="color: white; font-weight: bold;">📊 Visitas:</span>
        <img src="https://api.visitorbadge.io/api/visitors?path=quantum-health-ai.com&label=&countColor=%2300C2FF&style=flat&labelStyle=none" style="height: 20px;" />
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚙️ Ajustes")
    nivel = st.radio("Nivel de Respuesta:", ["Básica", "Media", "Experta"])
    
    if st.button("🗑️ Limpiar Chat"): st.session_state.mensajes = []; st.rerun()
    if st.button("🔒 Salir"): st.session_state.usuario_activo = None; st.rerun()

    st.markdown("---")
    st.markdown("### 👨‍⚕️ Directorio")
    if TODOS_LOS_MEDICOS:
        filtro = st.selectbox("📍 Ciudad:", ciudades)
        lista = TODOS_LOS_MEDICOS if filtro == "Todas las Ubicaciones" else [m for m in TODOS_LOS_MEDICOS if str(m.get('ciudad')).title() == filtro]
        
        if lista:
            if "idx" not in st.session_state: st.session_state.idx = 0
            m = lista[st.session_state.idx % len(lista)]
            
            # Tarjeta HTML
            tarjeta = (
                f'<div style="background-color: #262730; padding: 15px; border-radius: 10px; border: 1px solid #444; margin-bottom: 10px;">'
                f'<h4 style="margin:0; color:white;">{m.get("nombre","Dr.")}</h4>'
                f'<div style="color:#00C2FF; font-weight:bold;">{m.get("especialidad")}</div>'
                f'<small style="color:#bbb;">{m.get("ciudad")}</small>'
                f'<div style="font-size: 0.9em; margin-top: 5px;">📞 {m.get("telefono","--")}</div>'
                f'</div>'
            )
            st.markdown(tarjeta, unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            if c1.button("⬅️"): st.session_state.idx -= 1; st.rerun()
            if c2.button("➡️"): st.session_state.idx += 1; st.rerun()
        else: st.info("Sin resultados.")

    st.markdown("---")
    st.link_button("📝 Regístrate como Médico", URL_FORMULARIO)
    
    # ==========================================
    # 📰 SISTEMA EXPERTO PARA LA PRENSA
    # ==========================================
    st.markdown("---")
    st.markdown("### 📰 Sistema de Prensa")
    if st.button("🎯 Generar Contenido"):
        st.session_state.modo_prensa = True
        st.rerun()

# ==========================================
# 💬 4. CHAT PRINCIPAL
# ==========================================

# Inicializar estado del modo prensa
if "modo_prensa" not in st.session_state:
    st.session_state.modo_prensa = False

# ==========================================
# 📰 SISTEMA EXPERTO PARA LA PRENSA
# ==========================================
if st.session_state.modo_prensa:
    st.markdown('<h1 style="text-align: center; color: #00C2FF;">📰 Sistema Experto para la Prensa</h1>', unsafe_allow_html=True)
    st.caption("Generador de Contenido Profesional para Medios")
    
    if st.button("⬅️ Volver al Chat Principal"):
        st.session_state.modo_prensa = False
        st.rerun()
    
    st.markdown("---")
    
    # Selector de tipo de contenido
    tipo_contenido = st.selectbox(
        "Tipo de Contenido:",
        [
            "Comunicado de Prensa - Profesional Individual",
            "Artículo de Salud - Tema General",
            "Perfil Profesional para Medios",
            "Nota de Prensa - Directorio Médico"
        ]
    )
    
    if tipo_contenido == "Comunicado de Prensa - Profesional Individual":
        if TODOS_LOS_MEDICOS:
            nombres_medicos = [m.get('nombre', 'Sin nombre') for m in TODOS_LOS_MEDICOS]
            medico_seleccionado = st.selectbox("Seleccionar Profesional:", nombres_medicos)
            
            datos_medico = next((m for m in TODOS_LOS_MEDICOS if m.get('nombre') == medico_seleccionado), None)
            
            if datos_medico:
                col1, col2 = st.columns(2)
                with col1:
                    enfoque = st.text_input("Enfoque del comunicado:", placeholder="Ej: Nueva consulta, logro profesional")
                with col2:
                    tono = st.selectbox("Tono:", ["Profesional", "Informativo", "Inspiracional"])
                
                if st.button("🚀 Generar Comunicado"):
                    with st.spinner("Generando contenido profesional..."):
                        try:
                            prompt_prensa = f"""
                            Actúa como un experto redactor de comunicados de prensa médicos.
                            
                            Genera un comunicado de prensa profesional con la siguiente información:
                            
                            PROFESIONAL:
                            - Nombre: {datos_medico.get('nombre', 'N/A')}
                            - Especialidad: {datos_medico.get('especialidad', 'N/A')}
                            - Ciudad: {datos_medico.get('ciudad', 'N/A')}
                            - Teléfono: {datos_medico.get('telefono', 'N/A')}
                            - Descripción: {datos_medico.get('descripcion', 'N/A')}
                            
                            DIRECTRICES:
                            - Enfoque: {enfoque if enfoque else 'Presentación profesional general'}
                            - Tono: {tono}
                            - Formato estándar de comunicado de prensa
                            - Incluir encabezado con fecha y lugar
                            - Estructura: Titular, subtítulo, cuerpo (3-4 párrafos), información de contacto
                            - Longitud: 300-400 palabras
                            - Usar lenguaje profesional y periodístico
                            - Destacar credenciales y experiencia
                            
                            Genera SOLO el comunicado, sin explicaciones adicionales.
                            """
                            
                            modelo = genai.GenerativeModel('gemini-2.5-flash')
                            respuesta = modelo.generate_content(prompt_prensa)
                            
                            st.markdown("### 📄 Comunicado Generado")
                            st.markdown("---")
                            st.markdown(respuesta.text)
                            st.markdown("---")
                            
                            # Opción de descarga
                            st.download_button(
                                label="📥 Descargar Comunicado",
                                data=respuesta.text,
                                file_name=f"comunicado_{datos_medico.get('nombre', 'medico').replace(' ', '_')}.txt",
                                mime="text/plain"
                            )
                            
                        except Exception as e:
                            st.error(f"Error al generar el contenido: {e}")
        else:
            st.warning("No hay profesionales registrados en el directorio.")
    
    elif tipo_contenido == "Artículo de Salud - Tema General":
        tema = st.text_input("Tema del artículo:", placeholder="Ej: Suplementación deportiva, longevidad")
        
        # Mapeo más robusto de longitudes
        longitud_opciones = {
            "Corto (300 palabras)": 300,
            "Medio (600 palabras)": 600,
            "Largo (1000 palabras)": 1000
        }
        
        col1, col2 = st.columns(2)
        with col1:
            longitud = st.selectbox("Longitud:", list(longitud_opciones.keys()))
        with col2:
            incluir_expertos = st.checkbox("Incluir referencias a expertos del directorio", value=True)
        
        if st.button("🚀 Generar Artículo"):
            with st.spinner("Generando artículo..."):
                try:
                    expertos_ref = ""
                    if incluir_expertos and TODOS_LOS_MEDICOS:
                        # Seleccionar algunos expertos relevantes
                        expertos_ref = "\n\nPuedes mencionar a estos expertos del directorio si son relevantes:\n"
                        for m in TODOS_LOS_MEDICOS[:3]:
                            expertos_ref += f"- {m.get('nombre')}, {m.get('especialidad')}, {m.get('ciudad')}\n"
                    
                    palabras = longitud_opciones.get(longitud, 600)
                    
                    prompt_articulo = f"""
                    Actúa como un periodista especializado en salud y bienestar.
                    
                    Escribe un artículo periodístico sobre: {tema}
                    
                    ESPECIFICACIONES:
                    - Longitud aproximada: {palabras} palabras
                    - Estructura: Título atractivo, introducción, desarrollo (3-4 secciones), conclusión
                    - Tono: Profesional pero accesible
                    - Incluir datos científicos cuando sea relevante
                    - Formato periodístico estándar
                    - Usar subtítulos para organizar el contenido
                    {expertos_ref}
                    
                    Genera SOLO el artículo, sin explicaciones adicionales.
                    """
                    
                    modelo = genai.GenerativeModel('gemini-2.5-flash')
                    respuesta = modelo.generate_content(prompt_articulo)
                    
                    st.markdown("### 📰 Artículo Generado")
                    st.markdown("---")
                    st.markdown(respuesta.text)
                    st.markdown("---")
                    
                    st.download_button(
                        label="📥 Descargar Artículo",
                        data=respuesta.text,
                        file_name=f"articulo_{tema.replace(' ', '_')[:30]}.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Error al generar el contenido: {e}")
    
    elif tipo_contenido == "Perfil Profesional para Medios":
        if TODOS_LOS_MEDICOS:
            nombres_medicos = [m.get('nombre', 'Sin nombre') for m in TODOS_LOS_MEDICOS]
            medico_seleccionado = st.selectbox("Seleccionar Profesional:", nombres_medicos)
            
            datos_medico = next((m for m in TODOS_LOS_MEDICOS if m.get('nombre') == medico_seleccionado), None)
            
            if datos_medico:
                # Mapeo más robusto de formatos
                formato_opciones = {
                    "Bio Corta (100 palabras)": 100,
                    "Bio Media (250 palabras)": 250,
                    "Bio Completa (500 palabras)": 500
                }
                
                formato = st.radio("Formato:", list(formato_opciones.keys()))
                
                if st.button("🚀 Generar Perfil"):
                    with st.spinner("Generando perfil profesional..."):
                        try:
                            palabras = formato_opciones.get(formato, 250)
                            
                            prompt_perfil = f"""
                            Actúa como un redactor de biografías profesionales para medios de comunicación.
                            
                            Crea un perfil profesional basado en:
                            
                            DATOS:
                            - Nombre: {datos_medico.get('nombre', 'N/A')}
                            - Especialidad: {datos_medico.get('especialidad', 'N/A')}
                            - Ciudad: {datos_medico.get('ciudad', 'N/A')}
                            - Descripción: {datos_medico.get('descripcion', 'N/A')}
                            
                            FORMATO:
                            - Longitud: aproximadamente {palabras} palabras
                            - Estilo: Tercera persona, profesional
                            - Destacar credenciales, experiencia y áreas de especialización
                            - Apropiado para kits de prensa y medios
                            
                            Genera SOLO el perfil, sin explicaciones adicionales.
                            """
                            
                            modelo = genai.GenerativeModel('gemini-2.5-flash')
                            respuesta = modelo.generate_content(prompt_perfil)
                            
                            st.markdown("### 👤 Perfil Profesional")
                            st.markdown("---")
                            st.markdown(respuesta.text)
                            st.markdown("---")
                            
                            st.download_button(
                                label="📥 Descargar Perfil",
                                data=respuesta.text,
                                file_name=f"perfil_{datos_medico.get('nombre', 'medico').replace(' ', '_')}.txt",
                                mime="text/plain"
                            )
                            
                        except Exception as e:
                            st.error(f"Error al generar el contenido: {e}")
        else:
            st.warning("No hay profesionales registrados en el directorio.")
    
    elif tipo_contenido == "Nota de Prensa - Directorio Médico":
        enfoque = st.text_area(
            "Enfoque de la nota:",
            placeholder="Ej: Lanzamiento del directorio, expansión a nuevas ciudades, hito de profesionales registrados",
            height=100
        )
        
        if st.button("🚀 Generar Nota de Prensa"):
            with st.spinner("Generando nota de prensa..."):
                try:
                    estadisticas = f"""
                    Estadísticas del directorio:
                    - Total de profesionales: {len(TODOS_LOS_MEDICOS)}
                    - Ciudades cubiertas: {len(set(str(m.get('ciudad', 'General')) for m in TODOS_LOS_MEDICOS))}
                    - Especialidades: {len(set(str(m.get('especialidad', 'General')) for m in TODOS_LOS_MEDICOS))}
                    """
                    
                    prompt_nota = f"""
                    Actúa como un redactor de notas de prensa corporativas.
                    
                    Genera una nota de prensa sobre el directorio médico de Quantum Supplements.
                    
                    CONTEXTO:
                    Quantum Supplements es una plataforma de asesoría en suplementación y biohacking
                    con un directorio de profesionales de la salud.
                    
                    {estadisticas}
                    
                    ENFOQUE: {enfoque if enfoque else 'Presentación general del directorio'}
                    
                    ESTRUCTURA:
                    - Titular principal
                    - Subtítulo
                    - Fecha y lugar (usar formato: Ciudad, Fecha - )
                    - Lead (párrafo inicial con lo más importante)
                    - Desarrollo (2-3 párrafos)
                    - Información corporativa
                    - Contacto
                    
                    Tono: Profesional, corporativo
                    Longitud: 400-500 palabras
                    
                    Genera SOLO la nota, sin explicaciones adicionales.
                    """
                    
                    modelo = genai.GenerativeModel('gemini-2.5-flash')
                    respuesta = modelo.generate_content(prompt_nota)
                    
                    st.markdown("### 📰 Nota de Prensa")
                    st.markdown("---")
                    st.markdown(respuesta.text)
                    st.markdown("---")
                    
                    st.download_button(
                        label="📥 Descargar Nota",
                        data=respuesta.text,
                        file_name="nota_prensa_quantum_directorio.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Error al generar el contenido: {e}")
    
    st.stop()

# ==========================================
# CHAT PRINCIPAL NORMAL
# ==========================================
st.markdown('<h1 style="text-align: center; color: #00C2FF;">Quantum AI Health</h1>', unsafe_allow_html=True)
st.caption(f"Asistente Médico Inteligente - Nivel {nivel}")

if "mensajes" not in st.session_state: 
    st.session_state.mensajes = [{"role": "assistant", "content": "Hola, soy Quantum. ¿Cómo te sientes hoy?"}]

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Escribe tus síntomas o dudas aquí..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    
    try:
        full_prompt = f"Eres Quantum (Nivel: {nivel}). {INSTRUCCION_EXTRA}. Usuario: {prompt}."
        # Usamos el modelo que TÚ tienes disponible según tu lista
        res = genai.GenerativeModel('gemini-2.5-flash').generate_content(full_prompt)
        st.session_state.mensajes.append({"role": "assistant", "content": res.text})
        st.rerun()
    except Exception as e: st.error(f"Error: {e}")
        # --- CÓDIGO TEMPORAL DE DIAGNÓSTICO ---
#if st.button("🕵️ Ver Modelos Disponibles"):
    #try:
        #st.write("Consultando a Google...")
        #for m in genai.list_models():
            #if 'generateContent' in m.supported_generation_methods:
                #st.code(f"Nombre: {m.name}")
    #except Exception as e:
        #st.error(f"Error: {e}")