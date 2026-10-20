# 📊 Customer Review Intelligence Analyzer

[![CI Pipeline](https://github.com/sanjnaagnihotri004-a11y/customer-review-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/sanjnaagnihotri004-a11y/customer-review-analyzer/actions)
![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.66+-FF4B4B?logo=streamlit)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![Tests](https://img.shields.io/badge/Pytest-12%20Passed-brightgreen?logo=pytest)
![License](https://img.shields.io/badge/License-MIT-green)

An enterprise-ready **Customer Review Intelligence Platform** built with **Python**, **Streamlit**, **spaCy**, **NLTK**, and **PostgreSQL**. The application extracts fine-grained sentiment polarity, discovers key descriptive entities, visualizes word co-occurrence networks, and securely records review history in a relational database.

---

## 🏛️ System Architecture

```mermaid
flowchart TD
    User([👤 User / Browser]) <--> |HTTP / WebSocket| UI[🖥️ Streamlit Web App - app/main.py]

    subgraph Authentication Gate
        UI <--> |Bcrypt Verification| Auth[🔐 services/auth.py]
    end

    subgraph Core NLP Engine
        UI --> |Raw Review Text| Preprocess[🧹 core/preprocessing.py - spaCy]
        Preprocess --> |Cleaned Lemmas| Sentiment[📈 core/sentiment.py - NLTK]
        Sentiment --> |Polarity Score & Keywords| UI
    end

    subgraph Data & Storage Layer
        UI <--> |SQLAlchemy ORM| ReviewService[💾 services/review_service.py]
        ReviewService <--> |SessionLocal| DB[(🐘 PostgreSQL Database)]
        Auth <--> |User Queries| DB
    end

    subgraph Observability
        UI & Auth & ReviewService -.-> |Logs & Rotation| Logger[📜 core/logger.py - Loguru]
        Logger -.-> LogFile[📁 logs/app.log]
    end
```

---

## ✨ Key Features

* **🔐 Enterprise Authentication**:
  * User registration and sign-in portal.
  * Passwords hashed using industry-standard **`bcrypt`** with unique salts.
  * Session state gating ensuring reviews are isolated per user.

* **🧠 Natural Language Processing (NLP)**:
  * Linguistic tokenization and lemmatization powered by **spaCy** (`en_core_web_sm`).
  * Non-alphabetic and stop-word filtering to extract meaningful entities.
  * Sentiment polarity classification using the curated **NLTK Opinion Lexicon**.

* **📊 Interactive Visualizations**:
  * **Polarity Frequency Chart**: Matplotlib bar charts with exact entity counts.
  * **Dual Sentiment Word Clouds**: Positive entities highlighted in blue, negative in red.
  * **Concept Network Graph**: NetworkX spring-layout co-occurrence graph showing semantic relationships between customer descriptors.

* **🐘 Persistent Review History**:
  * Backed by **PostgreSQL 15** with SQLAlchemy ORM.
  * Stores review text alongside sentiment breakdown in optimized `JSON` columns.
  * User review history dashboard with aggregate sentiment analytics.

* **📝 Structured Logging & Audit Trails**:
  * Powered by **Loguru** with console streaming and disk persistence (`logs/app.log`).
  * Automatic log rotation at **5 MB** and **7-day retention** to preserve storage.

* **🐳 Production Containerization & CI/CD**:
  * Multi-stage, lightweight Linux **`Dockerfile`**.
  * **Docker Compose** orchestration for one-command local or cloud deployment.
  * Automated **GitHub Actions CI Pipeline** running linters and tests on every `git push`.

---

## 📂 Project Directory Structure

```text
customer-review-analyzer/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI workflow (Automated Testing)
├── app/
│   └── main.py                  # Main Streamlit web application & UI tabs
├── core/
│   ├── config.py                # Pydantic Settings & environment validation
│   ├── logger.py                # Loguru logging setup with file rotation
│   ├── preprocessing.py         # Text cleaning, spaCy tokenization & lemmatization
│   └── sentiment.py             # NLTK opinion lexicon classification & scoring
├── models/
│   ├── user.py                  # SQLAlchemy User model (accounts & credentials)
│   └── review.py                # SQLAlchemy Review model (reviews & sentiment JSON)
├── services/
│   ├── auth.py                  # Bcrypt hashing, verification, user creation
│   ├── db.py                    # Engine initialization & SessionLocal generator
│   └── review_service.py        # Review CRUD operations & history retrieval
├── tests/
│   ├── test_auth.py             # Unit tests for password hashing & security
│   ├── test_preprocessing.py    # Unit tests for text cleaning & spaCy
│   └── test_sentiment.py        # Unit tests for polarity & edge cases
├── .dockerignore                # Excluded build artifacts for Docker
├── .env.example                 # Template environment variables
├── .gitignore                   # Excluded Git files (secrets, caches, logs)
├── docker-compose.yml           # Multi-container orchestration (Web + DB)
├── Dockerfile                   # Production Python 3.11 container definition
├── pytest.ini                   # Pytest configuration file
├── requirements.txt             # Pinned production dependencies
└── README.md                    # Project documentation
```

---

## 🚀 Quickstart Guide

### Option 1: Run with Docker Compose (Recommended)

Ensure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is running, then run:

```bash
# 1. Clone the repository
git clone https://github.com/sanjnaagnihotri004-a11y/customer-review-analyzer.git
cd customer-review-analyzer

# 2. Start the database and web app
docker-compose up --build
```

The application will be live at: **[http://localhost:8501](http://localhost:8501)**

---

### Option 2: Local Development Setup

If you prefer running Python directly on your system:

#### 1. Prerequisites
* Python 3.11+
* Docker Desktop (for running the PostgreSQL container)

#### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/sanjnaagnihotri004-a11y/customer-review-analyzer.git
cd customer-review-analyzer

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLP model assets
python -m spacy download en_core_web_sm
```

#### 3. Configure Environment Variables
Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql+psycopg2://review_user:review_pass@localhost:5432/reviewdb
SECRET_KEY=generate-a-random-secure-secret-key-for-cookie-signing
```

#### 4. Start PostgreSQL
```bash
docker-compose up -d db
```

#### 5. Launch the Application
```bash
streamlit run app/main.py
```

Open your browser to: **[http://localhost:8501](http://localhost:8501)**

---

## 🧪 Running Automated Tests

The test suite validates data preprocessing, sentiment scoring, and password hashing:

```bash
pytest
```

**Expected output:**
```text
tests/test_auth.py::test_hash_password_scrambles_plaintext PASSED        [  8%]
tests/test_auth.py::test_hash_password_unique_salts PASSED               [ 16%]
tests/test_auth.py::test_verify_password_correct PASSED                  [ 25%]
tests/test_auth.py::test_verify_password_incorrect PASSED                [ 33%]
tests/test_preprocessing.py::test_clean_text_removes_punctuation PASSED  [ 41%]
tests/test_preprocessing.py::test_clean_text_empty_input PASSED          [ 50%]
tests/test_preprocessing.py::test_preprocess_text_tokenizes_and_lemmatizes PASSED [ 58%]
tests/test_preprocessing.py::test_preprocess_text_empty PASSED           [ 66%]
tests/test_sentiment.py::test_classify_words PASSED                      [ 75%]
tests/test_sentiment.py::test_analyze_sentiment_positive PASSED          [ 83%]
tests/test_sentiment.py::test_analyze_sentiment_negative PASSED          [ 91%]
tests/test_sentiment.py::test_analyze_sentiment_neutral PASSED           [100%]

============================= 12 passed in 4.14s ==============================
```

---

## 🔒 Security Best Practices Implemented

* **Password Hashing**: Plaintext passwords are never stored; all credentials use salted `bcrypt` hashes.
* **Separation of Secrets**: Configuration is read through `pydantic-settings` from `.env`, which is strictly ignored by `.gitignore`.
* **Database Isolation**: Reviews are linked to `user_id`, preventing data leakage between authenticated users.
* **Connection Pooling**: Scoped SQLAlchemy sessions ensure connections are closed promptly to avoid leaks.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
