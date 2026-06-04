import streamlit as st
from google import genai
from google.genai import types
import os
import time
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

MODEL_CHAIN = [
    "models/gemini-2.5-flash",
    "models/gemini-2.5-flash-lite",
    "models/gemma-4-26b-a4b-it",
    "models/gemma-4-31b-it",
]
PRIMARY_MODEL = MODEL_CHAIN[0]

SYSTEM_INSTRUCTION = """
        Actúa como un asistente IA de medicina, empático y experto, del Hospital Central en Mendoza. Tu nombre de pila para las respuestas es "Lupe", asistente IA para lupus.
        Tu fuente de conocimiento es la información técnica provista en el contexto,
        PERO debes comunicarla como si fuera tu propio conocimiento profesional.

        REGLAS DE SEGURIDAD CRÍTICA (PRIORIDAD 1):
        - Si el usuario menciona síntomas de emergencia (dolor de pecho, dificultad para respirar, sangrado profuso, pensamientos suicidas), IGNORA el documento.
        - Tu única respuesta debe ser: "⚠️ Te recuerdo que soy un asistente IA, no puedo realizar diagnósticos ni resolver casos clínicos específicos. Te recomendaría consultarlo con un especialista."

        REGLAS DE INTERACCIÓN:
        1. NUNCA menciones "el documento", "el pdf", "el texto adjunto".
        2. Si encuentras la respuesta en el contexto, explícala de forma clara y accesible.
        3. Si la respuesta NO está en tu base de conocimientos, di:
           "Lo siento, no tengo información específica sobre ese caso particular. Te recomendaría consultarlo con un especialista."
        4. Mantén un tono cálido y profesional.
        5. Utilizar solo informacion provista en el contexto. En caso de que una pregunta sea sobre algo que no esté en el contexto, responder con "No tengo información sobre eso".
        """

CHAT_CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTION,
    temperature=0.2,
    max_output_tokens=8192,
)

st.set_page_config(page_title="Asistente Médico IA", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stStatusWidget {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_client():
    return genai.Client(api_key=api_key)


@st.cache_resource(show_spinner=False)
def upload_and_cache_pdf(file_path):
    client = get_client()
    file = client.files.upload(
        file=file_path,
        config=types.UploadFileConfig(mime_type="application/pdf"),
    )
    while file.state.name == "PROCESSING":
        time.sleep(1)
        file = client.files.get(name=file.name)
    return file


def create_chat(model_name, pdf_file, prior_history=None):
    client = get_client()
    bootstrap = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_uri(file_uri=pdf_file.uri, mime_type="application/pdf"),
                types.Part.from_text(text="Estudia este documento."),
            ],
        ),
        types.Content(
            role="model",
            parts=[types.Part.from_text(text="Entendido.")],
        ),
    ]
    history = bootstrap + (prior_history or [])
    return client.chats.create(
        model=model_name,
        config=CHAT_CONFIG,
        history=history,
    )


def switch_to_fallback(pdf_file, target_model):
    prior = list(st.session_state.chat_session.get_history()[2:])
    st.session_state.chat_session = create_chat(target_model, pdf_file, prior_history=prior)
    st.session_state.active_model = target_model


# --- INICIALIZACIÓN ---

if not api_key:
    st.error("❌ No se encontró la API Key en el archivo .env")
    st.stop()

pdf_path = "manual_medico.pdf"
if not os.path.exists(pdf_path):
    st.error(f"❌ Falta el archivo {pdf_path}")
    st.stop()

RATE_LIMIT = 3
RATE_WINDOW = 60  # seconds

def is_rate_limited():
    now = time.time()
    st.session_state.msg_timestamps = [t for t in st.session_state.msg_timestamps if now - t < RATE_WINDOW]
    if len(st.session_state.msg_timestamps) >= RATE_LIMIT:
        return True
    st.session_state.msg_timestamps.append(now)
    return False

# --- SIDEBAR ---

with st.sidebar:
    st.image("logo_HC.png", width=100)
    st.title("Servicio de Inmunología")
    st.markdown("---")

    st.markdown("### ⚠️ Aviso Legal")
    st.info(
        "Este asistente utiliza inteligencia artificial. "
        "La información es orientativa y no sustituye "
        "la consulta médica profesional."
    )

    if "chat_session" in st.session_state:
        if st.button("🗑️ Nueva Consulta"):
            for key in ("chat_session", "active_model"):
                st.session_state.pop(key, None)
            st.rerun()

        st.success("✅ Sistema Operativo")

st.title("🩺 Chatbot sobre Lupus del Hospital Central 💜")

# --- PDF LOAD ---

try:
    with st.spinner("Iniciando sistema de atención médica..."):
        pdf_file = upload_and_cache_pdf(pdf_path)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

if "active_model" not in st.session_state:
    st.session_state.active_model = PRIMARY_MODEL

if "chat_session" not in st.session_state:
    st.session_state.chat_session = create_chat(st.session_state.active_model, pdf_file)

if "msg_timestamps" not in st.session_state:
    st.session_state.msg_timestamps = []

history = st.session_state.chat_session.get_history()[2:]

if not history:
    st.info(
        "Aquí encontrarás información sobre el Lupus desarrollada y recopilada por el Servicio de Inmunología "
        "del Hospital Central de Mendoza. Es una herramienta con fines exclusivamente informativos, no puede "
        "realizar diagnósticos ni resolver casos clínicos específicos y no reemplaza el asesoramiento de tu médico."
    )

i = 0
while i < len(history):
    message = history[i]
    role = "user" if message.role == "user" else "assistant"
    chunks = []
    while i < len(history) and history[i].role == message.role:
        text = "".join(p.text for p in history[i].parts if not getattr(p, "thought", False) and p.text)
        if text:
            chunks.append(text)
        i += 1
    combined = "".join(chunks)
    if combined:
        with st.chat_message(role):
            st.markdown(combined)

if prompt := st.chat_input("Escribe tu consulta..."):
    if is_rate_limited():
        st.warning("Por favor, esperá un momento antes de enviar otra consulta.")
        st.stop()

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("_Procesando tu pregunta..._ ⏳")
            full_text = ""
            for chunk in st.session_state.chat_session.send_message_stream(prompt):
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)

    except Exception as error:
        active = st.session_state.active_model
        try:
            current_idx = MODEL_CHAIN.index(active)
        except ValueError:
            current_idx = len(MODEL_CHAIN) - 1

        response = None
        for next_model in MODEL_CHAIN[current_idx + 1:]:
            logging.warning("Modelo %s falló, intentando %s. Error: %s", active, next_model, error)
            try:
                switch_to_fallback(pdf_file, next_model)
                response = st.session_state.chat_session.send_message(prompt)
                active = next_model
                break
            except Exception as e:
                error = e
                active = next_model

        if response:
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.rerun()
        else:
            logging.error("Todos los modelos fallaron. Último error: %s", error)
            st.error("Lo siento, hubo un problema técnico. Por favor, intenta de nuevo en unos momentos.")
