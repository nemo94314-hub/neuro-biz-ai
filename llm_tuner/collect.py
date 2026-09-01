import os
import click
from datetime import datetime
from typing import List, Dict
from .utils import save_jsonl, format_chat_template

DEFAULT_QUESTIONS = [
    "Опишите вашу бизнес-модель. Как вы создаёте ценность для клиентов и получаете прибыль?",
    "Какие маркетинговые каналы вы используете для привлечения клиентов? Какой из них самый эффективный и почему?",
    "Расскажите о вашем документообороте: какие договоры, акты, счета вы используете чаще всего? Как вы их создаёте и храните?",
    "Как вы ведёте бухгалтерский и налоговый учёт? Какие программы или сервисы используете?",
    "Какие юридические аспекты вашего бизнеса требуют особого внимания (регистрация, лицензии, интеллектуальная собственность, трудовые договоры)?",
    "Как вы управляете персоналом? Какие процессы подбора, адаптации, мотивации и оценки сотрудников у вас выстроены?",
    "Опишите ваш типичный рабочий день руководителя: с какими задачами вы сталкиваетесь, какие решения принимаете?",
    "Какие метрики и KPI вы отслеживаете для контроля эффективности бизнеса? Как часто вы их анализируете?",
    "Какие IT-инструменты и автоматизация помогают вам в работе (CRM, ERP, чат-боты, нейросети)? Что бы вы хотели внедрить?",
    "Какие планы развития у вашего бизнеса на ближайшие 1-3 года? Какие новые продукты или рынки вы рассматриваете?"
]

def run_interview(questions: List[str], output_path: str) -> None:
    print("\n" + "="*60)
    print("   ИНТЕРВЬЮ ДЛЯ ОБУЧЕНИЯ БИЗНЕС-НЕЙРОСЕТИ")
    print("="*60)
    print("\nОтвечайте максимально развернуто. Для пропуска вопроса введите 'skip', для выхода — 'exit'.\n")
    
    data = []
    
    for idx, question in enumerate(questions, 1):
        print(f"\n[{idx}/{len(questions)}] {question}")
        print("-" * 40)
        response = input("> ").strip()
        
        if response.lower() == 'exit':
            print("\nИнтервью прервано.")
            break
        if response.lower() == 'skip':
            continue
        if response:
            data.append(format_chat_template(question, response))
    
    if data:
        system_prompt = {
            "messages": [
                {"role": "system", "content": "Ты — AI-ассистент, обученный на знаниях и опыте эксперта в бизнесе."},
                {"role": "user", "content": "Расскажи о себе"},
                {"role": "assistant", "content": "Я — AI-ассистент, обученный на интервью с руководителем бизнеса."}
            ]
        }
        data.insert(0, system_prompt)
        save_jsonl(output_path, data)
        print(f"\n✅ Сохранено {len(data)} примеров в {output_path}")
    else:
        print("\n❌ Не было собрано ни одного ответа.")

@click.command()
@click.option('--output', '-o', default='data/train.jsonl', help='Путь для сохранения датасета')
def collect(output):
    """Сбор данных через интервью."""
    run_interview(DEFAULT_QUESTIONS, output)
