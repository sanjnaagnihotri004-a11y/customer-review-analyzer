"""
app/main.py
───────────
The main Streamlit application for Customer Review Analyzer.

FEATURES:
  - Authentication Gate: Sign In & User Registration with hashed passwords.
  - Interactive NLP Analyzer: Tokenization, lemmatization, and sentiment polarity classification.
  - Visualizations: High-resolution Frequency Bar Charts, Dual Word Clouds, and Spring-Layout Word Graphs.
  - Review History: Persistent database storage in PostgreSQL with user isolation.
  - Sample Review Presets: Instant one-click testing with positive, negative, and mixed reviews.
"""

import sys
from pathlib import Path

# Ensure the root project directory is on sys.path so Python can find 'services', 'core', and 'models'
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import re
from collections import Counter
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import networkx as nx

# Core business logic and database services
from services.db import SessionLocal, init_db
from services.auth import authenticate_user, create_user, get_user_by_email
from services.review_service import create_review, get_user_reviews
from core.preprocessing import preprocess_text
from core.sentiment import classify_words, analyze_sentiment
from core.logger import logger

# ────────────────────────────────────────────
# PAGE CONFIGURATION (Must be the first Streamlit command)
# ────────────────────────────────────────────
st.set_page_config(
    page_title="Customer Review Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database schema safely on startup
try:
    init_db()
except Exception as err:
    st.sidebar.error("⚠️ Database connection failed. Please ensure Docker Desktop is running.")

# ────────────────────────────────────────────
# CUSTOM CSS STYLING
# ────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Global Typography and Card Spacing */
    .stApp {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    h1, h2, h3 {
        color: #1e293b;
        font-weight: 700;
    }
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 18px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #0f172a;
        font-weight: 800;
    }
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    /* Text Input Area */
    .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        font-size: 15px;
        line-height: 1.6;
    }
    .stTextArea textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.session_state["user_id"] = None

if "preset_text" not in st.session_state:
    st.session_state["preset_text"] = ""

# Backward compatibility alias
classify_sentiment = classify_words


# ════════════════════════════════════════════
#  AUTHENTICATION PORTAL (Login & Register)
# ════════════════════════════════════════════
def show_login_page():
    st.markdown(
        """
        <div style="text-align: center; margin-top: 30px; margin-bottom: 25px;">
            <h1 style="font-size: 2.4rem; color: #1e3a8a; margin-bottom: 8px;">📊 Customer Review Analyzer</h1>
            <p style="color: #64748b; font-size: 1.1rem; max-width: 600px; margin: 0 auto;">
                Industry-grade Natural Language Processing platform for customer sentiment extraction, keyword analytics, and word relation mapping.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_pad1, col_form, col_pad2 = st.columns([1, 2, 1])

    with col_form:
        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])

        # ---- TAB 1: LOGIN ----
        with tab_login:
            st.write("Enter your credentials to access your workspace.")
            with st.form("login_form"):
                email = st.text_input("📧 Email", placeholder="user@example.com")
                password = st.text_input("🔑 Password", type="password")
                submit_login = st.form_submit_button("Sign In", type="primary", use_container_width=True)

            if submit_login:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    try:
                        db = SessionLocal()
                        try:
                            user = authenticate_user(db, email.strip(), password)
                            if user is not None:
                                st.session_state["logged_in"] = True
                                st.session_state["user_email"] = user.email
                                st.session_state["user_id"] = user.id
                                st.success("Authentication successful! Loading workspace...")
                                st.rerun()
                            else:
                                st.error("Invalid email or password. Please try again.")
                        finally:
                            db.close()
                    except Exception as e:
                        st.error(f"⚠️ Could not reach the database. Ensure Docker Desktop is running. ({e})")

        # ---- TAB 2: REGISTER ----
        with tab_register:
            st.write("Register a new account to begin saving review analyses.")
            with st.form("register_form"):
                reg_email = st.text_input("📧 New Account Email", placeholder="newuser@example.com")
                reg_password = st.text_input("🔑 New Password", type="password")
                reg_confirm = st.text_input("🔒 Confirm Password", type="password")
                submit_register = st.form_submit_button("Create Account", use_container_width=True)

            if submit_register:
                if not reg_email or not reg_password:
                    st.error("All fields are required.")
                elif reg_password != reg_confirm:
                    st.error("Passwords do not match. Please re-enter.")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    try:
                        db = SessionLocal()
                        try:
                            existing = get_user_by_email(db, reg_email.strip())
                            if existing:
                                st.warning("An account with that email already exists. Please Sign In.")
                            else:
                                new_user = create_user(db, reg_email.strip(), reg_password)
                                st.success(f"Account for {new_user.email} created successfully! You can now sign in.")
                        finally:
                            db.close()
                    except Exception as e:
                        st.error(f"⚠️ Could not connect to the database. ({e})")


# ════════════════════════════════════════════
#  MAIN APPLICATION (Authenticated)
# ════════════════════════════════════════════
def show_main_app():
    # ---- SIDEBAR ----
    with st.sidebar:
        st.markdown(f"### 👤 Profile\n**{st.session_state['user_email']}**")
        st.caption("Active Session: Authenticated User")
        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            logger.info(f"User logged out: {st.session_state['user_email']}")
            st.session_state["logged_in"] = False
            st.session_state["user_email"] = None
            st.session_state["user_id"] = None
            st.session_state["preset_text"] = ""
            st.rerun()

        st.divider()
        st.markdown(
            """
            **About Platform:**
            - 🧠 NLP Powered by **spaCy**
            - 📚 Lexicon by **NLTK**
            - 🐘 Database: **PostgreSQL**
            - 🐳 Architecture: **Docker Compose**
            """
        )

    # ---- HEADER ----
    st.title("📊 Customer Review Intelligence Analyzer")
    st.caption("Extract actionable customer sentiment, detect polarity keywords, and map concept networks.")

    # ---- NAVIGATION TABS ----
    tab_analyze, tab_history = st.tabs(["✍️ Analyze Review", "📜 Review History"])

    # ────────────────────────────────────────────
    # TAB 1: ANALYZE REVIEW
    # ────────────────────────────────────────────
    with tab_analyze:
        st.subheader("Input Customer Feedback")

        # Preset Sample Buttons for Quick Testing
        st.write("Or load a sample review:")
        sample_col1, sample_col2, sample_col3 = st.columns(3)
        with sample_col1:
            if st.button("🌟 Positive Review Sample", use_container_width=True):
                st.session_state["preset_text"] = (
                    "The screen and display quality are extraordinary and breathtaking! "
                    "Battery life is magnificent, build quality is sturdy, and customer support was wonderful. "
                    "Overall an incredible, fantastic purchase that I genuinely love."
                )
                st.rerun()
        with sample_col2:
            if st.button("⚠️ Negative Review Sample", use_container_width=True):
                st.session_state["preset_text"] = (
                    "Extremely disappointing purchase. The power adapter was defective and broke on day two. "
                    "Performance is terribly slow, heating is awful, and warranty support was useless and rude. "
                    "A completely horrible experience."
                )
                st.rerun()
        with sample_col3:
            if st.button("⚖️ Mixed Review Sample", use_container_width=True):
                st.session_state["preset_text"] = (
                    "The camera produces gorgeous, brilliant photos with vibrant colors. "
                    "However, the battery drain is annoying, charging is sluggish, and the software has frustrating glitches."
                )
                st.rerun()

        # Review Text Area
        review_text = st.text_area(
            "✍️ Review Text:",
            value=st.session_state["preset_text"],
            height=150,
            placeholder="Type or paste customer review text here to analyze...",
        )

        col_run, col_clear = st.columns([1, 5])
        with col_run:
            analyze_btn = st.button("🚀 Analyze & Save", type="primary", use_container_width=True)
        with col_clear:
            if st.button("🧹 Clear Input"):
                st.session_state["preset_text"] = ""
                st.rerun()

        # Execute Analysis
        if analyze_btn and review_text.strip():
            with st.spinner("Processing text and extracting sentiment entities..."):
                tokens = preprocess_text(review_text)
                sentiment_report = analyze_sentiment(tokens)

                # Persist to database
                db = SessionLocal()
                try:
                    saved_rec = create_review(
                        db=db,
                        user_id=st.session_state["user_id"],
                        raw_text=review_text.strip(),
                        sentiment_data=sentiment_report,
                    )
                    st.success(f"✅ Review analyzed and saved to database! (Record ID: #{saved_rec.id})")
                except Exception as e:
                    st.warning(f"Could not save review to database: {e}")
                finally:
                    db.close()

            # Display High-Level Summary Metrics
            st.divider()
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                label = sentiment_report["label"]
                delta_color = "normal" if label == "Positive" else ("inverse" if label == "Negative" else "off")
                st.metric("Overall Sentiment", label)
            with m2:
                st.metric("Positive Keywords", sentiment_report["positive_count"])
            with m3:
                st.metric("Negative Keywords", sentiment_report["negative_count"])
            with m4:
                st.metric("Net Polarity Score", sentiment_report["score"])

            pos = sentiment_report["positive_words"]
            neg = sentiment_report["negative_words"]

            st.divider()
            # Visualizations Section
            viz1, viz2, viz3 = st.columns(3)

            # 1. Bar Chart
            with viz1:
                st.subheader("📈 Keyword Distribution")
                freq = {"Positive": len(pos), "Negative": len(neg)}
                fig, ax = plt.subplots(figsize=(4.5, 3.8), dpi=100)
                bars = ax.bar(freq.keys(), freq.values(), color=["#2563eb", "#dc2626"], width=0.5)
                ax.set_ylabel("Count", fontsize=10)
                ax.set_title("Polarity Frequency", fontsize=11, fontweight="bold")
                ax.grid(axis="y", linestyle="--", alpha=0.3)
                # Display count labels on bars
                for bar in bars:
                    yval = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.1, int(yval), ha="center", va="bottom", fontsize=10)
                plt.tight_layout()
                st.pyplot(fig)

            # 2. Word Clouds
            with viz2:
                st.subheader("☁️ Sentiment Word Clouds")
                wc_pos = WordCloud(
                    width=320, height=280,
                    background_color="white", colormap="Blues"
                ).generate(" ".join(pos) if pos else "none")
                wc_neg = WordCloud(
                    width=320, height=280,
                    background_color="white", colormap="Reds"
                ).generate(" ".join(neg) if neg else "none")

                fig, (ax_pos, ax_neg) = plt.subplots(1, 2, figsize=(7.5, 3.8), dpi=100)
                ax_pos.imshow(wc_pos, interpolation="bilinear")
                ax_pos.axis("off")
                ax_pos.set_title("Positive Entities", color="#2563eb", fontsize=11, fontweight="bold")
                ax_neg.imshow(wc_neg, interpolation="bilinear")
                ax_neg.axis("off")
                ax_neg.set_title("Negative Entities", color="#dc2626", fontsize=11, fontweight="bold")
                plt.tight_layout()
                st.pyplot(fig)

            # 3. Word Relation Network Graph
            with viz3:
                st.subheader("🔗 Concept Network")
                sentences = review_text.split(".")
                G = nx.Graph()
                for sentence in sentences:
                    s_lemmas = preprocess_text(sentence)
                    s_pos, s_neg = classify_words(s_lemmas)
                    for i in range(len(s_pos)):
                        for j in range(i + 1, len(s_pos)):
                            G.add_edge(s_pos[i], s_pos[j], color="#2563eb")
                    for i in range(len(s_neg)):
                        for j in range(i + 1, len(s_neg)):
                            G.add_edge(s_neg[i], s_neg[j], color="#dc2626")

                if len(G.nodes()) > 0:
                    pos_layout = nx.spring_layout(G, k=1.2, iterations=40, seed=42)
                    edge_colors = [G[u][v]["color"] for u, v in G.edges()]
                    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
                    nx.draw(
                        G, pos_layout, with_labels=True,
                        node_color="#f1f5f9", node_size=1500,
                        font_size=9, font_weight="bold",
                        edge_color=edge_colors, width=1.8, ax=ax
                    )
                    ax.set_title("Word Co-occurrence", fontsize=11, fontweight="bold")
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("No co-occurring sentiment keywords found to plot network graph.")

        elif analyze_btn and not review_text.strip():
            st.warning("Please type or select a review sample before analyzing.")

    # ────────────────────────────────────────────
    # TAB 2: REVIEW HISTORY
    # ────────────────────────────────────────────
    with tab_history:
        st.subheader("📜 Review History & Past Analyses")
        st.caption("All reviews previously analyzed by your account, retrieved from PostgreSQL.")

        if st.button("🔄 Refresh History", use_container_width=False):
            st.rerun()

        db = SessionLocal()
        try:
            records = get_user_reviews(db, user_id=st.session_state["user_id"])
            if not records:
                st.info("No saved reviews found. Switch to the 'Analyze Review' tab to process your first review!")
            else:
                total_reviews = len(records)
                pos_reviews = sum(1 for r in records if (r.sentiment or {}).get("label") == "Positive")
                neg_reviews = sum(1 for r in records if (r.sentiment or {}).get("label") == "Negative")
                neu_reviews = total_reviews - pos_reviews - neg_reviews

                # Summary Metrics for History
                h_col1, h_col2, h_col3, h_col4 = st.columns(4)
                with h_col1:
                    st.metric("Total Reviews Analyzed", total_reviews)
                with h_col2:
                    st.metric("Positive Reviews", pos_reviews)
                with h_col3:
                    st.metric("Negative Reviews", neg_reviews)
                with h_col4:
                    st.metric("Neutral Reviews", neu_reviews)

                st.divider()

                # Table view
                table_rows = []
                for rec in records:
                    s_data = rec.sentiment or {}
                    table_rows.append({
                        "ID": f"#{rec.id}",
                        "Timestamp": rec.created_at.strftime("%Y-%m-%d %H:%M") if rec.created_at else "N/A",
                        "Review Snippet": (rec.raw_text[:75] + "...") if len(rec.raw_text) > 75 else rec.raw_text,
                        "Sentiment": s_data.get("label", "Unknown"),
                        "Net Score": s_data.get("score", 0),
                        "Positive Words": ", ".join(s_data.get("positive_words", [])),
                        "Negative Words": ", ".join(s_data.get("negative_words", [])),
                    })
                st.dataframe(table_rows, use_container_width=True, height=350)
        except Exception as e:
            st.error(f"Could not load review history: {e}")
        finally:
            db.close()


# ════════════════════════════════════════════
#  APPLICATION ROUTING GATE
# ════════════════════════════════════════════
if st.session_state["logged_in"]:
    show_main_app()
else:
    show_login_page()
