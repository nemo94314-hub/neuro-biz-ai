import streamlit as st
import requests

# ============================================
# 🌙 ТЁМНАЯ ТЕМА ДЛЯ ЧАТА
# ============================================
st.markdown(
    """
    <style>
        .stApp {
            background-color: #0a0e27;
            color: #ffffff;
        }
        .stTextInput > div > div > input {
            background-color: #1a1e4a;
            color: #ffffff;
            border: 1px solid #6c63ff;
            border-radius: 8px;
        }
        .stButton > button {
            background: linear-gradient(135deg, #6c63ff, #00d4ff);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 8px 20px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .stButton > button:hover {
            transform: scale(1.02);
            box-shadow: 0 0 20px rgba(108, 99, 255, 0.4);
        }
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff;
        }
        .stChatMessage {
            background-color: #12163a !important;
            border-radius: 12px !important;
            padding: 12px !important;
            margin-bottom: 8px !important;
            border: 1px solid #6c63ff !important;
        }
        .stChatMessage.user {
            background-color: #1a1e4a !important;
        }
        .stChatMessage.assistant {
            background-color: #0f1a3a !important;
            border-color: #00d4ff !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Neuro Biz AI — Чат", layout="centered")
st.image("assets/logo.svg", width=200)
st.title("💬 Чат с локальной моделью")
st.caption("Выберите модель и задайте вопрос")

# --- Настройки ---
OLLAMA_URL = "http://localhost:11434/api/generate"

AVAILABLE_MODELS = [
    "llama3.2",
    "qwen2.5:0.5b",
    "qwen2.5:1.5b",
    "mistral",
    "phi3:mini",
    "gemma2:2b"
]

with st.sidebar:
    st.image("assets/logo.svg", width=150)
    st.header("⚙️ Настройки чата")
    selected_model = st.selectbox("Выберите модель:", AVAILABLE_MODELS, index=0)
    st.caption(f"Текущая модель: **{selected_model}**")
    if st.button("🗑️ Очистить историю"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

def query_ollama(prompt, model):
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json().get("response", "Нет ответа")
    except requests.exceptions.ConnectionError:
        return "❌ Сервер Ollama не запущен. Запустите `ollama serve`."
    except Exception as e:
        return f"❌ Ошибка: {e}"

if prompt := st.chat_input("Ваш вопрос:"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner(f"Думаю ({selected_model})..."):
            response = query_ollama(prompt, selected_model)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
