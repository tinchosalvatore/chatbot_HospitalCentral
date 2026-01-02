import streamlit as st
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

# 1. Cargar variables de entorno (.env)
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# Configura la página
st.set_page_config(page_title="Asistente Médico IA", page_icon="🩺")

# --- CSS HACK: Ocultar indicadores de carga y menús técnicos ---
st.markdown("""
    <style>
    .stStatusWidget {visibility: hidden;} /* Oculta el 'Running...' */
    #MainMenu {visibility: hidden;}       /* Oculta el menú hamburguesa */
    footer {visibility: hidden;}          /* Oculta el 'Made with Streamlit' */
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    # Usamos una imagen médica genérica o el logo del hospital si lo tuvieras
    st.image("https://cdn-icons-png.flaticon.com/512/3774/3774299.png", width=100)
    st.title("Asistente Virtual")
    st.markdown("---")
    
    st.markdown("### ⚠️ Aviso Legal")
    st.info(
        "Este asistente utiliza inteligencia artificial. "
        "La información es orientativa y no sustituye "
        "la consulta médica profesional."
    )
    
    # Botón para limpiar chat
    if st.button("🗑️ Nueva Consulta"):
        if "chat_session" in st.session_state:
            del st.session_state.chat_session
        st.rerun()

# --- TÍTULO PRINCIPAL ---
st.title("🩺 Chatbot Hospital Central")

# --- LÓGICA DE GEMINI ---
def configure_gemini(api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="models/gemini-flash-latest",
        generation_config={
            "temperature": 0.2,
            "max_output_tokens": 8192,
        },
        system_instruction="""
        Actúa como un asistente IA de medicina, empático y experto, del Hospital Central en Mendoza.
        Tu fuente de conocimiento es la información técnica provista en el contexto, 
        PERO debes comunicarla como si fuera tu propio conocimiento profesional.
        
        REGLAS DE SEGURIDAD CRÍTICA (PRIORIDAD 1):
        - Si el usuario menciona síntomas de emergencia (dolor de pecho, dificultad para respirar, sangrado profuso, pensamientos suicidas), IGNORA el documento.
        - Tu única respuesta debe ser: "⚠️ Esto parece una emergencia médica. Por favor, corta esta comunicación y llama inmediatamente al servicio de urgencias (911) o acude al hospital más cercano."

        REGLAS DE INTERACCIÓN:
        1. NUNCA menciones "el documento", "el pdf", "el texto adjunto".
        2. Si encuentras la respuesta en el contexto, explícala de forma clara y accesible.
        3. Si la respuesta NO está en tu base de conocimientos, di: 
           "Lo siento, no tengo información específica sobre ese caso particular. Te recomendaría consultarlo con un especialista."
        4. Mantén un tono cálido y profesional.
        5. Utilizar solo informacion provista en el contexto. En caso de que una pregunta sea sobre algo que no esté en el contexto, responder con "No tengo información sobre eso".
        """
    )

@st.cache_resource
def upload_and_cache_pdf(file_path):
    # Mensaje de carga profesional
    with st.spinner("Iniciando sistema de atención..."):
        file = genai.upload_file(file_path, mime_type="application/pdf")
        while file.state.name == "PROCESSING":
            time.sleep(1)
            file = genai.get_file(file.name)
        return file

# --- VERIFICACIONES E INICIALIZACIÓN ---

if not api_key:
    st.error("❌ No se encontró la API Key en el archivo .env")
    st.stop()

model = configure_gemini(api_key)

pdf_path = "manual_medico.pdf" 
if not os.path.exists(pdf_path):
    st.error(f"❌ Falta el archivo {pdf_path}")
    st.stop()

try:
    pdf_file = upload_and_cache_pdf(pdf_path)
    with st.sidebar:
        st.success("✅ Sistema Operativo")
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- GESTIÓN DE ESTADO DEL CHAT ---

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [pdf_file, "Estudia este documento."],
            },
            {
                "role": "model",
                "parts": ["Entendido."],
            },
        ]
    )

# --- INTERFAZ DE CHAT ---

# Mostrar historial
for message in st.session_state.chat_session.history[2:]:
    role = "user" if message.role == "user" else "assistant"
    # AL NO PONER 'avatar=', STREAMLIT USA LOS ICONOS NATIVOS SERIOS
    with st.chat_message(role): 
        st.markdown(message.parts[0].text)

# Input
if prompt := st.chat_input("Escribe tu consulta..."):
    with st.chat_message("user"): # Icono nativo de usuario
        st.markdown(prompt)
    
    try:
        response = st.session_state.chat_session.send_message(prompt)
        with st.chat_message("assistant"): # Icono nativo de asistente (AI)
            st.markdown(response.text)
    except Exception as e:
        st.error(f"Error de API: {e}")