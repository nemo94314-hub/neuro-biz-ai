import re
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def analyze_answers(answers):
    """
    Анализирует ответы из интервью и возвращает структурированный отчёт.
    """
    # 1. Сбор всех текстов
    all_text = " ".join([a for a in answers if a])
    if not all_text.strip():
        return {"error": "Нет данных для анализа."}
    
    # 2. Извлечение ключевых слов (топ-10)
    vectorizer = CountVectorizer(max_features=10, stop_words='russian')
    X = vectorizer.fit_transform([all_text])
    keywords = vectorizer.get_feature_names_out()
    
    # 3. Определение основных тем (LDA)
    lda = LatentDirichletAllocation(n_components=3, random_state=42)
    lda.fit(X)
    topics = []
    for topic_idx, topic in enumerate(lda.components_):
        top_words = [keywords[i] for i in topic.argsort()[-5:]]
        topics.append(f"Тема {topic_idx+1}: {', '.join(top_words)}")
    
    # 4. Статистика
    total_words = len(all_text.split())
    avg_answer_length = total_words / len(answers) if answers else 0
    
    # 5. Повторяющиеся слова
    word_counts = Counter(all_text.split())
    repeated_words = [word for word, count in word_counts.items() if count > 5]
    
    # 6. Рекомендации (на основе тем и ключевых слов)
    suggestions = []
    combined = " ".join(topics) + " " + " ".join(keywords)
    combined_lower = combined.lower()
    if "маркетинг" in combined_lower or "продажи" in combined_lower:
        suggestions.append("📌 Вы часто упоминаете маркетинг и продажи — возможно, стоит систематизировать ваши каналы привлечения.")
    if "команд" in combined_lower or "сотрудник" in combined_lower:
        suggestions.append("📌 Вы говорите о команде — подумайте о создании базы знаний для сотрудников.")
    if "документ" in combined_lower or "бухгалтер" in combined_lower:
        suggestions.append("📌 У вас есть опыт с документами — можно автоматизировать их создание через ИИ.")
    if "клиент" in combined_lower:
        suggestions.append("📌 Клиенты — ваш приоритет. Рассмотрите внедрение системы сбора обратной связи.")
    if not suggestions:
        suggestions.append("✅ Ваш бизнес сбалансирован. Продолжайте в том же духе!")
    
    return {
        "keywords": keywords.tolist(),
        "topics": topics,
        "total_words": total_words,
        "avg_answer_length": round(avg_answer_length, 1),
        "repeated_words": repeated_words[:10],
        "suggestions": suggestions
    }
