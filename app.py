import streamlit as st
import json
import os
import subprocess
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
from llm_tuner.collect import DEFAULT_QUESTIONS as BASE_QUESTIONS
from llm_tuner.utils import save_jsonl, format_chat_template
from analyzer import analyze_answers, generate_analysis_pdf
from graph import build_knowledge_graph, draw_graph
from speech import transcribe_audio

# ============================================
# 🌙 ТЁМНАЯ ТЕМА (CSS)
# ============================================
st.markdown(
    """
    <style>
        /* Основной фон */
        .stApp {
            background-color: #0a0e27;
            color: #ffffff;
        }
        /* Боковая панель */
        .css-1d391kg {
            background-color: #12163a;
        }
        /* Текст в полях ввода */
        .stTextInput > div > div > input {
            background-color: #1a1e4a;
            color: #ffffff;
            border: 1px solid #6c63ff;
            border-radius: 8px;
        }
        /* Текстовые области */
        .stTextArea > div > div > textarea {
            background-color: #1a1e4a;
            color: #ffffff;
            border: 1px solid #6c63ff;
            border-radius: 8px;
        }
        /* Кнопки */
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
        /* Заголовки */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff;
        }
        /* Текст в боковой панели */
        .css-1aumxhk {
            color: #aab;
        }
        /* Метрики */
        .stMetric {
            background-color: #12163a;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #6c63ff;
        }
        /* Сообщения об успехе/ошибке */
        .stAlert {
            background-color: #1a1e4a !important;
            color: #ffffff !important;
            border-left: 4px solid #6c63ff !important;
        }
        .stRadio > div {
            color: #ffffff;
        }
        /* Маленькие тексты */
        .stCaption {
            color: #aaa !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================
# 🔐 БЕЗОПАСНОСТЬ И МОНЕТИЗАЦИЯ
# ============================================

# --- 1. ПАРОЛЬ ДЛЯ РАЗРАБОТЧИКОВ ---
ADMIN_PASSWORD = "ваш_пароль_здесь"

if "auth" not in st.session_state:
    st.session_state.auth = False
if "role" not in st.session_state:
    st.session_state.role = None

# --- 2. ЛИЦЕНЗИОННЫЕ КЛЮЧИ ---
VALID_KEYS = os.getenv("LICENSE_KEYS", "").split(",")
if not VALID_KEYS or VALID_KEYS == [""]:
    VALID_KEYS = ["ключ1", "ключ2", "ключ3"]

def check_license(key):
    return key in VALID_KEYS

if "license_valid" not in st.session_state:
    st.session_state.license_valid = False
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False

# --- 3. ЭКРАН ВХОДА ---
if not st.session_state.auth:
    st.set_page_config(page_title="Neuro Biz AI", layout="centered", page_icon="🧠")
    st.image("assets/logo.svg", width=200)
    st.title("🧠 Neuro Biz AI")
    st.markdown("**Введите пароль разработчика или лицензионный ключ**")

    option = st.radio("Выберите тип доступа:", ["🔑 Лицензионный ключ", "🛠️ Пароль разработчика"])

    if option == "🛠️ Пароль разработчика":
        password_input = st.text_input("Пароль разработчика", type="password")
        if st.button("Войти как разработчик"):
            if password_input == ADMIN_PASSWORD:
                st.session_state.auth = True
                st.session_state.role = "admin"
                log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Вход разработчика\n"
                with open("access.log", "a", encoding="utf-8") as log_file:
                    log_file.write(log_entry)
                st.success("✅ Добро пожаловать, разработчик!")
                st.rerun()
            else:
                st.error("❌ Неверный пароль!")

    else:
        key_input = st.text_input("Лицензионный ключ", type="password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Активировать лицензию"):
                if check_license(key_input):
                    st.session_state.auth = True
                    st.session_state.role = "user"
                    st.session_state.license_valid = True
                    st.session_state.demo_mode = False
                    log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Активирована лицензия\n"
                    with open("access.log", "a", encoding="utf-8") as log_file:
                        log_file.write(log_entry)
                    st.success("✅ Лицензия активирована!")
                    st.rerun()
                else:
                    st.error("❌ Неверный ключ!")
        with col2:
            if st.button("🎯 Демо-режим (2 вопроса)"):
                st.session_state.auth = True
                st.session_state.role = "user"
                st.session_state.license_valid = False
                st.session_state.demo_mode = True
                log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Запущен демо-режим\n"
                with open("access.log", "a", encoding="utf-8") as log_file:
                    log_file.write(log_entry)
                st.rerun()

    st.stop()

# --- 4. ЛОГИРОВАНИЕ ---
role_label = "Админ" if st.session_state.role == "admin" else "Пользователь"
log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — Запуск приложения (роль: {role_label})\n"
with open("access.log", "a", encoding="utf-8") as log_file:
    log_file.write(log_entry)

# ============================================
# ОСНОВНОЙ КОД ПРИЛОЖЕНИЯ
# ============================================

st.set_page_config(page_title="Neuro Biz AI", layout="centered", page_icon="🧠")
st.image("assets/logo.svg", width=280)
st.title("🧠 Neuro Biz AI")
st.caption("Создайте своего ИИ-ассистента и получите аналитику бизнеса")

# --- Режим ---
questions = BASE_QUESTIONS.copy()
if st.session_state.demo_mode and st.session_state.role != "admin":
    questions = questions[:2]
    st.info("ℹ️ Демо-режим: доступны только 2 вопроса. Полный доступ по лицензии.")
elif st.session_state.role == "admin":
    st.success("🛠️ Режим разработчика — все функции доступны")

# --- Инициализация ---
if 'questions' not in st.session_state:
    st.session_state.questions = questions
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'answers' not in st.session_state:
    st.session_state.answers = [""] * len(st.session_state.questions)
if 'finished' not in st.session_state:
    st.session_state.finished = False
if 'editing' not in st.session_state:
    st.session_state.editing = False
if 'logs' not in st.session_state:
    st.session_state.logs = []

if st.session_state.demo_mode and st.session_state.role != "admin":
    st.session_state.editing = False

# --- Боковая панель ---
with st.sidebar:
    st.image("assets/logo.svg", width=150)
    st.header("⚙️ Управление")

    if st.session_state.role == "admin":
        st.success("🛠️ Режим разработчика")
    elif st.session_state.demo_mode:
        st.warning("Демо-режим")
    else:
        st.success("✅ Полный доступ")

    st.caption(f"🔒 Сеанс: {datetime.now().strftime('%H:%M:%S')}")

    # --- Админ-панель ---
    if st.session_state.role == "admin":
        st.subheader("🛠️ Админ-панель")
        if st.button("📋 Посмотреть логи"):
            if os.path.exists("access.log"):
                with open("access.log", "r", encoding="utf-8") as f:
                    st.text_area("Логи", f.read(), height=200)
            else:
                st.info("Логов пока нет.")
        if st.button("🗑️ Очистить логи"):
            if os.path.exists("access.log"):
                os.remove("access.log")
                st.success("Логи удалены")
                st.rerun()
        if st.button("🔄 Сбросить датасет"):
            if os.path.exists("data/train.jsonl"):
                os.remove("data/train.jsonl")
                st.success("Датасет удалён")
                st.rerun()

    # --- Редактор вопросов ---
    if not st.session_state.demo_mode or st.session_state.role == "admin":
        if st.checkbox("Редактировать вопросы", value=st.session_state.editing):
            st.session_state.editing = True
            st.subheader("Редактор вопросов")
            new_questions = []
            for i, q in enumerate(st.session_state.questions):
                new_q = st.text_input(f"Вопрос {i+1}", value=q)
                new_questions.append(new_q)
            if st.button("Сохранить изменения"):
                st.session_state.questions = new_questions
                st.session_state.answers = [""] * len(new_questions)
                st.session_state.index = 0
                st.success("✅ Вопросы обновлены")
                st.rerun()
            new_q = st.text_input("Добавить новый вопрос")
            if st.button("➕ Добавить вопрос") and new_q:
                st.session_state.questions.append(new_q)
                st.session_state.answers.append("")
                st.success("✅ Вопрос добавлен")
                st.rerun()
            if st.button("🗑️ Удалить последний вопрос") and len(st.session_state.questions) > 1:
                st.session_state.questions.pop()
                st.session_state.answers.pop()
                st.success("✅ Последний вопрос удалён")
                st.rerun()
        else:
            st.session_state.editing = False

    # --- Статистика ---
    answered = sum(1 for a in st.session_state.answers if a.strip())
    total = len(st.session_state.questions)
    st.metric("📊 Прогресс", f"{answered}/{total}")
    if total > 0:
        st.progress(answered / total)

    # --- Сброс ---
    if st.button("🗑️ Сбросить все ответы"):
        st.session_state.answers = [""] * len(st.session_state.questions)
        st.session_state.index = 0
        st.session_state.finished = False
        st.success("✅ Все ответы удалены.")
        st.rerun()

    # --- Экспорт ---
    if not st.session_state.demo_mode or st.session_state.role == "admin":
        st.subheader("📤 Экспорт")
        if st.button("📥 Скачать CSV"):
            df = pd.DataFrame({
                "Вопрос": st.session_state.questions,
                "Ответ": st.session_state.answers
            })
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("⬇️ Скачать CSV", data=csv, file_name="answers.csv", mime="text/csv")
        if st.button("📄 Скачать PDF"):
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            y = height - 50
            c.drawString(50, y, "Отчёт по интервью")
            y -= 30
            for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
                if y < 50:
                    c.showPage()
                    y = height - 50
                c.drawString(50, y, f"{i+1}. {q[:80]}")
                y -= 20
                c.drawString(50, y, f"   Ответ: {a[:100]}")
                y -= 30
            c.save()
            st.download_button("⬇️ Скачать PDF", data=buffer.getvalue(), file_name="answers.pdf", mime="application/pdf")
    else:
        st.info("Экспорт доступен только в полной версии.")

    st.markdown("---")
    if st.button("💬 Перейти в чат"):
        st.switch_page("pages/1_Чат.py")

    # --- Обучение ---
    if not st.session_state.demo_mode or st.session_state.role == "admin":
        st.subheader("🚀 Обучение")
        if st.button("Запустить обучение (CPU)"):
            st.session_state.logs = []
            st.session_state.logs.append("Начинаем обучение...")
            try:
                process = subprocess.Popen(
                    ["python", "-m", "llm_tuner.cli", "train", "--epochs", "1", "--batch-size", "1"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                for line in process.stdout:
                    st.session_state.logs.append(line)
                    st.rerun()
                process.wait()
                st.session_state.logs.append("✅ Обучение завершено!")
            except Exception as e:
                st.session_state.logs.append(f"❌ Ошибка: {e}")
            st.rerun()
    else:
        st.info("Обучение доступно только в полной версии.")

    if st.session_state.logs:
        st.subheader("📋 Логи обучения")
        for line in st.session_state.logs[-20:]:
            st.text(line)

# --- Основная часть интервью ---
if st.session_state.editing:
    st.info("Включён режим редактирования вопросов. Настройте вопросы в боковой панели.")
else:
    if not st.session_state.finished:
        progress = (st.session_state.index + 1) / len(st.session_state.questions)
        st.progress(progress)
        st.write(f"Вопрос {st.session_state.index + 1} из {len(st.session_state.questions)}")

        question = st.session_state.questions[st.session_state.index]
        st.markdown(f"**{question}**")

        response = st.text_area(
            "Ваш ответ:",
            value=st.session_state.answers[st.session_state.index],
            height=150,
            key=f"answer_{st.session_state.index}"
        )

        if f"answer_{st.session_state.index}" in st.session_state:
            st.session_state.answers[st.session_state.index] = st.session_state[f"answer_{st.session_state.index}"]

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            if st.button("◀ Назад", disabled=(st.session_state.index == 0)):
                st.session_state.index -= 1
                st.rerun()
        with col2:
            if st.button("Далее ▶", disabled=(st.session_state.index == len(st.session_state.questions)-1)):
                st.session_state.index += 1
                st.rerun()
        with col3:
            if st.button("💾 Сохранить текущий"):
                st.success("✅ Ответ сохранён!")
        with col4:
            if st.button("✅ Завершить интервью"):
                st.session_state.finished = True
                st.rerun()
    else:
        st.success("🎉 Интервью завершено!")
        with st.expander("📝 Все ответы"):
            for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
                st.write(f"**{i+1}. {q}**")
                st.write(a)

        # --- СОХРАНЕНИЕ ДАТАСЕТА ---
        if not st.session_state.demo_mode or st.session_state.role == "admin":
            if st.button("💾 Сохранить датасет (train.jsonl)"):
                data = []
                for q, ans in zip(st.session_state.questions, st.session_state.answers):
                    if ans.strip():
                        data.append(format_chat_template(q, ans))
                if data:
                    data.insert(0, {
                        "messages": [
                            {"role": "system", "content": "Ты — AI-ассистент, обученный на бизнес-опыте."},
                            {"role": "user", "content": "Расскажи о себе"},
                            {"role": "assistant", "content": "Я — AI-ассистент, обученный на интервью с руководителем."}
                        ]
                    })
                    os.makedirs("data", exist_ok=True)
                    save_jsonl("data/train.jsonl", data)
                    st.success(f"✅ Сохранено {len(data)} примеров")
                else:
                    st.warning("Нет заполненных ответов.")
        else:
            st.info("Сохранение доступно только в полной версии.")

        # --- КНОПКА АНАЛИЗА ---
        if st.button("🔍 Проанализировать ответы"):
            if any(a.strip() for a in st.session_state.answers):
                report = analyze_answers(st.session_state.answers)
                if "error" in report:
                    st.warning(report["error"])
                else:
                    st.subheader("📊 Анализ интервью")
                    st.write("**Ключевые слова:**", ", ".join(report["keywords"]))
                    st.write("**Основные темы:**")
                    for topic in report["topics"]:
                        st.write(f"- {topic}")
                    st.write(f"**Всего слов:** {report['total_words']}")
                    st.write(f"**Средняя длина ответа:** {report['avg_answer_length']} слов")
                    if report["repeated_words"]:
                        st.write("**Повторяющиеся идеи:**", ", ".join(report["repeated_words"]))
                    if report["suggestions"]:
                        st.subheader("💡 Рекомендации")
                        for suggestion in report["suggestions"]:
                            st.write(suggestion)

                    # --- КНОПКА СКАЧАТЬ АНАЛИЗ PDF ---
                    if st.button("📄 Скачать анализ в PDF"):
                        pdf_buffer = generate_analysis_pdf(report)
                        st.download_button(
                            label="⬇️ Скачать PDF-отчёт",
                            data=pdf_buffer,
                            file_name="analysis_report.pdf",
                            mime="application/pdf"
                        )
            else:
                st.warning("Нет ответов для анализа. Пройдите интервью.")

        # --- КНОПКА ГРАФА ЗНАНИЙ ---
        if st.button("🌐 Показать граф знаний"):
            report = analyze_answers(st.session_state.answers)
            if "error" not in report and report["keywords"]:
                from graph import build_knowledge_graph, draw_graph
                G = build_knowledge_graph(st.session_state.answers, report["keywords"])
                st.subheader("🌐 Граф знаний вашего бизнеса")
                st.caption("Связи между ключевыми темами (толщина линии = частота совместного упоминания)")
                draw_graph(G)
            else:
                st.warning("Недостаточно данных для построения графа.")

        # --- ГОЛОСОВОЙ ВВОД ---
        st.subheader("🎤 Голосовое интервью")
        st.caption("Загрузите аудиозапись (WAV) с ответами. Программа распознает речь и добавит текст в датасет.")
        audio_file = st.file_uploader("Выберите аудиофайл (WAV)", type=["wav"])
        if audio_file is not None:
            with st.spinner("Распознавание речи..."):
                transcribed_text = transcribe_audio(audio_file)
            st.text_area("Распознанный текст", transcribed_text, height=150)
            if st.button("➕ Добавить текст в ответы"):
                if transcribed_text and "Не удалось" not in transcribed_text and "Ошибка" not in transcribed_text:
                    st.session_state.answers.append(transcribed_text)
                    st.success("✅ Текст добавлен в датасет как дополнительный ответ!")
                else:
                    st.warning("Не удалось распознать речь или текст пуст.")

        # --- ЭКСПОРТ PDF (уже есть) ---
        st.subheader("📄 Скачать отчёт PDF")
        if st.button("Создать PDF"):
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            y = height - 50
            c.drawString(50, y, "Отчёт по интервью")
            y -= 30
            for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
                if y < 50:
                    c.showPage()
                    y = height - 50
                c.drawString(50, y, f"{i+1}. {q[:80]}")
                y -= 20
                c.drawString(50, y, f"   Ответ: {a[:100]}")
                y -= 30
            c.save()
            st.download_button(
                "⬇️ Скачать PDF",
                data=buffer.getvalue(),
                file_name="answers.pdf",
                mime="application/pdf"
            )
