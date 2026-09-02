import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import re

def build_knowledge_graph(answers, keywords):
    """
    Строит граф знаний на основе ответов и ключевых слов.
    """
    # Создаём граф
    G = nx.Graph()
    
    # Добавляем узлы (ключевые слова)
    for word in keywords:
        G.add_node(word)
    
    # Собираем все слова из ответов
    all_words = []
    for ans in answers:
        words = re.findall(r'\b[a-zA-Zа-яА-ЯёЁ]+\b', ans.lower())
        all_words.extend(words)
    
    # Строим связи: если два слова встречаются в одном предложении
    for ans in answers:
        sentences = re.split(r'[.!?]', ans)
        for sent in sentences:
            sent_words = set(re.findall(r'\b[a-zA-Zа-яА-ЯёЁ]+\b', sent.lower()))
            sent_words = [w for w in sent_words if w in keywords]
            for i, w1 in enumerate(sent_words):
                for w2 in sent_words[i+1:]:
                    if G.has_edge(w1, w2):
                        G[w1][w2]['weight'] += 1
                    else:
                        G.add_edge(w1, w2, weight=1)
    
    return G

def draw_graph(G):
    """
    Рисует граф с помощью matplotlib.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    pos = nx.spring_layout(G, seed=42)
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    
    nx.draw_networkx_nodes(G, pos, node_size=800, node_color='#6c63ff', ax=ax)
    nx.draw_networkx_edges(G, pos, width=weights, edge_color='#00d4ff', alpha=0.7, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=12, font_color='white', ax=ax)
    
    ax.set_facecolor('#0a0e27')
    fig.patch.set_facecolor('#0a0e27')
    st.pyplot(fig)
