# 🧠 DailyBuddy

DailyBuddy is an **AI-powered personal assistant** that ingests your daily life data — text notes, images, and videos — and lets you retrieve it later using natural language. It uses a multi-agent architecture built on **Google Gemini**, with **PostgreSQL** for structured storage, **Pinecone** for vector/semantic search, and **FastAPI** for serving.

---

## ✨ Features

- 📝 **Multimodal ingestion** — extract structured data from text, images, and video using Gemini Vision/Video APIs
- 🤖 **Multi-agent architecture** — Coordinator, Extraction, Storage, and Retrieval agents work together
- 🗄️ **Hybrid storage** — PostgreSQL (structured data) + Pinecone (vector embeddings) + local file storage (raw media)
- 🔍 **Natural language retrieval** — ask questions and get answers via hybrid vector + SQL search
- ✅ **Confidence-based auto-storage** — only stores extracted facts above a confidence threshold (> 0.7)
- 📅 **ISO 8601 date normalization** for consistent timeline tracking
- 💻 **CLI interface** for interactive use, with FastAPI for API access

---

## 🛠️ Tech Stack

| Component       | Technology              |
|------------------|--------------------------|
| LLM / AI         | Google Gemini (`google-genai`) |
| API Framework    | FastAPI + Uvicorn        |
| ORM / Database   | SQLAlchemy + PostgreSQL (`psycopg2`) |
| Vector Search    | Pinecone                 |
| Config           | python-dotenv            |
| Validation       | Pydantic                 |
| Testing          | Pytest                   |
| Image Handling   | Pillow                   |

---

## 📁 Project Structure

```
daily_buddy/
├── src/
│   ├── main.py                  # Entry point — initializes agents & DB session
│   ├── cli.py                   # Interactive CLI
│   ├── agents/
│   │   ├── coordinator_agent.py # Routes requests between agents
│   │   ├── extraction_agent.py  # Extracts structured data via Gemini
│   │   ├── storage_agent.py     # Persists data to Postgres/Pinecone/local storage
│   │   └── retrieval_agent.py   # Handles natural language queries
│   └── database/
│       ├── models.py            # SQLAlchemy models
│       ├── init_db.py           # DB initialization
│       └── schema.sql           # Database schema
├── docs/                         # Detailed guides & quick start docs
├── .gemini/agents/                # Gemini agent persona definitions
├── storage/                       # Local raw media storage (ignored in git)
├── env.example                    # Example environment variables
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/IbrahimPopatiya/daily_buddy.git
cd daily_buddy
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `env.example` to `.env` and fill in your own values:

```bash
cp env.example .env
```

Required variables:

| Variable             | Description                                   |
|----------------------|-----------------------------------------------|
| `GOOGLE_CLOUD_PROJECT` | Your Google Cloud project ID                 |
| `GEMINI_API_KEY`       | API key for Google Gemini                    |
| `POSTGRES_URL`         | PostgreSQL connection string (e.g. `postgresql://user:password@localhost:5432/dailybuddy`) |
| `PINECONE_API_KEY`     | API key for Pinecone                         |
| `PINECONE_INDEX`       | Name of the Pinecone index (e.g. `dailybuddy`) |
| `GCS_BUCKET`           | (Optional) Google Cloud Storage bucket for media |
| `ENVIRONMENT`          | `development` or `production`                |

### 5. Initialize the database

```bash
python -m src.database.init_db
```

---

## 🚀 Running DailyBuddy

### Run the interactive CLI

```bash
python -m src.cli
```

### Run the main agent pipeline

```bash
python -m src.main
```

### Run the API server (FastAPI + Uvicorn)

```bash
uvicorn src.main:app --reload
```

> ℹ️ Note: ensure your FastAPI `app` instance is exposed in `src/main.py` (or update the module path above accordingly) before running this command.

---

## 🧩 Agent Roles

| Agent              | Responsibility                                              |
|---------------------|--------------------------------------------------------------|
| **Coordinator**     | Routes requests to specialized agents (`send_to_agent`, `memory_recall`) |
| **Extraction**      | Extracts structured info from multimodal inputs (Gemini Vision/Video) |
| **Storage**         | Persists & indexes data into Postgres + Pinecone + local storage |
| **Retrieval**       | Answers natural language queries via hybrid vector + SQL search |

---

## 🖼️ Screenshots

### Ask a Query
![Ask Query](public/ask_query.png)

### Save Image
![Image Save](public/image_save.png)

### Memories
![Memories](public/memories.png)

### Save Text
![Text Save](public/text_save.png)

---

## 📜 License

This project is for personal/educational use. Add a license of your choice.
