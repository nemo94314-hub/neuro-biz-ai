import tkinter as tk
from tkinter import scrolledtext, messagebox
import json
import os

# Вопросы (копия из llm_tuner.collect)
DEFAULT_QUESTIONS = [
    "Расскажите о вашей компании и её основной бизнес-модели.",
    "Какие ключевые проблемы вы решаете для своих клиентов?",
    "Опишите ваш типичный рабочий день. С какими задачами вы сталкиваетесь чаще всего?",
    "Какие решения или подходы вы используете для решения этих задач?",
    "Что отличает вашу компанию от конкурентов?",
    "Какие метрики вы считаете самыми важными для вашего бизнеса?",
    "Опишите ситуацию, когда вы приняли сложное решение. Как вы к этому пришли?",
    "Какие инструменты или технологии вы используете в своей работе?",
    "Как вы мотивируете свою команду?",
    "Какие советы вы дали бы начинающему предпринимателю в вашей сфере?"
]

class InterviewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Интервью для бизнес-ИИ")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        self.current_index = 0
        self.answers = [""] * len(DEFAULT_QUESTIONS)

        # Заголовок
        self.title_label = tk.Label(root, text="🧠 Интервью для обучения бизнес-ИИ", font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)

        # Индикатор вопроса
        self.progress_label = tk.Label(root, text="", font=("Arial", 10))
        self.progress_label.pack()

        # Метка с вопросом
        self.question_label = tk.Label(root, text="", wraplength=650, font=("Arial", 12), justify="left")
        self.question_label.pack(pady=10, padx=10, anchor="w")

        # Текстовое поле для ответа (с прокруткой)
        self.answer_text = scrolledtext.ScrolledText(root, height=8, wrap=tk.WORD, font=("Arial", 11))
        self.answer_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Кнопки
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10, fill=tk.X, padx=10)

        self.btn_back = tk.Button(button_frame, text="◀ Назад", command=self.go_back, state=tk.DISABLED)
        self.btn_back.pack(side=tk.LEFT, padx=5)

        self.btn_next = tk.Button(button_frame, text="Далее ▶", command=self.go_next)
        self.btn_next.pack(side=tk.LEFT, padx=5)

        self.btn_save = tk.Button(button_frame, text="💾 Сохранить ответ", command=self.save_current)
        self.btn_save.pack(side=tk.LEFT, padx=5)

        self.btn_finish = tk.Button(button_frame, text="✅ Завершить", command=self.finish_interview)
        self.btn_finish.pack(side=tk.RIGHT, padx=5)

        # Панель для навигации по вопросам (переход к любому)
        nav_frame = tk.Frame(root)
        nav_frame.pack(pady=5, fill=tk.X, padx=10)
        tk.Label(nav_frame, text="Перейти к вопросу №").pack(side=tk.LEFT)
        self.spinbox = tk.Spinbox(nav_frame, from_=1, to=len(DEFAULT_QUESTIONS), width=5, command=self.go_to_question)
        self.spinbox.pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="Перейти", command=self.go_to_question).pack(side=tk.LEFT, padx=5)

        # Загружаем первый вопрос
        self.show_question()

    def show_question(self):
        """Отображает текущий вопрос и ответ."""
        idx = self.current_index
        self.progress_label.config(text=f"Вопрос {idx+1} из {len(DEFAULT_QUESTIONS)}")
        self.question_label.config(text=DEFAULT_QUESTIONS[idx])
        self.answer_text.delete("1.0", tk.END)
        self.answer_text.insert("1.0", self.answers[idx])
        self.update_buttons()

    def update_buttons(self):
        """Обновляет состояние кнопок Назад/Далее."""
        self.btn_back.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_index < len(DEFAULT_QUESTIONS)-1 else tk.DISABLED)

    def go_back(self):
        self.save_current()  # автосохранение перед переходом
        if self.current_index > 0:
            self.current_index -= 1
            self.show_question()

    def go_next(self):
        self.save_current()
        if self.current_index < len(DEFAULT_QUESTIONS)-1:
            self.current_index += 1
            self.show_question()

    def save_current(self):
        """Сохраняет текст из поля в текущий ответ."""
        self.answers[self.current_index] = self.answer_text.get("1.0", tk.END).strip()
        messagebox.showinfo("Сохранено", "Ответ сохранён!")

    def go_to_question(self):
        """Переход к вопросу по номеру."""
        try:
            num = int(self.spinbox.get()) - 1
            if 0 <= num < len(DEFAULT_QUESTIONS):
                self.save_current()
                self.current_index = num
                self.show_question()
        except ValueError:
            pass

    def finish_interview(self):
        """Завершает интервью, сохраняет все ответы."""
        self.save_current()
        # Показываем все ответы в отдельном окне
        review = "\n\n".join([f"{i+1}. {DEFAULT_QUESTIONS[i]}\nОтвет: {self.answers[i]}" 
                              for i in range(len(DEFAULT_QUESTIONS)) if self.answers[i]])
        if not review:
            messagebox.showwarning("Нет ответов", "Вы не ввели ни одного ответа.")
            return

        # Диалог подтверждения сохранения
        if messagebox.askyesno("Завершить", "Все ответы будут сохранены в файл.\nПродолжить?"):
            self.save_to_file()

    def save_to_file(self):
        """Сохраняет ответы в data/train.jsonl."""
        # Создаём папку data, если её нет
        os.makedirs("data", exist_ok=True)
        
        # Формируем датасет
        from llm_tuner.utils import format_chat_template, save_jsonl
        data = []
        for q, ans in zip(DEFAULT_QUESTIONS, self.answers):
            if ans.strip():
                data.append(format_chat_template(q, ans))
        if data:
            # Добавляем системный промпт
            data.insert(0, {
                "messages": [
                    {"role": "system", "content": "Ты — AI-ассистент, обученный на знаниях бизнес-эксперта."},
                    {"role": "user", "content": "Расскажи о себе"},
                    {"role": "assistant", "content": "Я — AI-ассистент, обученный на интервью с руководителем."}
                ]
            })
            save_jsonl("data/train.jsonl", data)
            messagebox.showinfo("Успех", f"Сохранено {len(data)} примеров в data/train.jsonl")
            self.root.destroy()
        else:
            messagebox.showwarning("Нет данных", "Нет заполненных ответов.")

if __name__ == "__main__":
    root = tk.Tk()
    app = InterviewApp(root)
    root.mainloop()
