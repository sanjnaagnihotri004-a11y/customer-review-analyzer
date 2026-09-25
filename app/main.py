import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import networkx as nx
import spacy
from collections import Counter
import re
import nltk
from nltk.corpus import opinion_lexicon

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Download opinion lexicon (only once)
nltk.download('opinion_lexicon')
positive_words = set(opinion_lexicon.positive())
negative_words = set(opinion_lexicon.negative())

# ---------------- UI HEADER ----------------
st.set_page_config(page_title="Customer Review Analyzer", layout="wide")

st.markdown(
    """
    <style>
    .main {
        background-color: #f9f9f9;
        padding: 20px;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        font-family: 'Segoe UI', sans-serif;
    }
    .stTextArea textarea {
        font-size: 16px;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Customer Review Analyzer")
st.write("Analyze customer reviews with sentiment classification, word clouds, and relationship graphs. Positive words are shown in **blue**, negative words in **red**.")

# ---------------- TEXT INPUT ----------------
text = st.text_area("✍️ Enter customer review:", height=200)

# ---------------- FUNCTIONS ----------------
def preprocess_text(text):
    clean_text = re.sub(r'[^\w\s]', '', text.lower())
    doc = nlp(clean_text)
    lemmas = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    return lemmas

def classify_sentiment(words):
    pos = [w for w in words if w in positive_words]
    neg = [w for w in words if w in negative_words]
    return pos, neg

# ---------------- LAYOUT ----------------
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📈 Sentiment Bar Chart"):
        lemmas = preprocess_text(text)
        pos, neg = classify_sentiment(lemmas)
        freq = {"Positive": len(pos), "Negative": len(neg)}
        fig, ax = plt.subplots(figsize=(6,5))
        ax.bar(freq.keys(), freq.values(), color=["blue","red"])
        ax.set_title("Sentiment Frequency")
        st.pyplot(fig)

with col2:
    if st.button("☁️ Sentiment Word Cloud"):
        lemmas = preprocess_text(text)
        pos, neg = classify_sentiment(lemmas)
        wc_pos = WordCloud(width=400, height=400, background_color="white", colormap="Blues").generate(" ".join(pos))
        wc_neg = WordCloud(width=400, height=400, background_color="white", colormap="Reds").generate(" ".join(neg))
        fig, (ax1, ax2) = plt.subplots(1,2, figsize=(12,6))
        ax1.imshow(wc_pos, interpolation="bilinear")
        ax1.axis("off")
        ax1.set_title("Positive Words (Blue)")
        ax2.imshow(wc_neg, interpolation="bilinear")
        ax2.axis("off")
        ax2.set_title("Negative Words (Red)")
        st.pyplot(fig)

with col3:
    if st.button("🔗 Sentiment Word Network"):
        sentences = text.split(".")
        G = nx.Graph()
        for sentence in sentences:
            lemmas = preprocess_text(sentence)
            pos, neg = classify_sentiment(lemmas)
            for i in range(len(pos)):
                for j in range(i+1, len(pos)):
                    G.add_edge(pos[i], pos[j], color="blue")
            for i in range(len(neg)):
                for j in range(i+1, len(neg)):
                    G.add_edge(neg[i], neg[j], color="red")
        pos_layout = nx.spring_layout(G, k=1.2, iterations=50)
        colors = [G[u][v]['color'] for u,v in G.edges()]
        fig, ax = plt.subplots(figsize=(12,12))
        nx.draw(G, pos_layout, with_labels=True, node_color="lightgray", node_size=2500,
                font_size=12, edge_color=colors, ax=ax)
        ax.set_title("Sentiment Word Network (Blue=Positive, Red=Negative)")
        st.pyplot(fig)



