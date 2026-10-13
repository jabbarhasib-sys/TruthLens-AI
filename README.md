<div align="center">

# 🔍 TruthLens AI

### Real-Time AI-Powered Fact Verification Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald?style=for-the-badge)](LICENSE)

**TruthLens AI** is an end-to-end misinformation detection platform that verifies news claims and images in real time. It aggregates signals from multiple fact-checking APIs, AI deepfake detection, linguistic analysis, and LLM reasoning to produce a transparent, weighted **Trust Score** (0–100) with a detailed audit trail.

[Features](#-features) · [Architecture](#-architecture) · [Quick Start](#-quick-start) · [API Reference](#-api-reference) · [Trust Engine](#-trust-engine) · [Environment Variables](#-environment-variables)

</div>

---

## ✨ Features

### 📰 News Claim Verification
- **Multi-source fact checking** via Google Fact Check Tools API, NewsAPI, MediaStack, and GDELT
- **LLM reasoning** powered by Groq (Llama 3.1 70B) — generates structured Markdown analysis reports
- **Claim decomposition** — complex claims are broken into atomic sub-claims for independent verification
- **URL article scraping** — paste a link and TruthLens extracts and verifies the article content
- **Linguistic heuristics** — sensationalist language, absolute claim markers, and credible source attribution detection
- **Medical & political misinformation pattern matching** using regex pattern libraries
- **Named entity extraction** — identifies organizations, statistics, and attribution signals

### 🖼️ Image Authenticity Analysis
- **AI deepfake detection** via Hive Moderation AI (ai_generated / manipulated / original classification)
- **EXIF metadata forensics** — camera make/model, GPS geolocation, capture timestamp, editing software detection
- **Google Cloud Vision SafeSearch** spoof analysis and web detection
- **Perceptual hash (dHash) caching** — instantly recall results for viral images without re-running the pipeline
- **Filename heuristic analysis** — detects suspicious/manipulated naming conventions

### 🧠 Trust Engine v3
- **Weighted scoring model** — 20+ individual signals contribute to a final 0–100 Trust Score
- **Emotional tone analysis** — fear-inducing language, outrage bait, propaganda phrases, ALL-CAPS, exclamation overuse
- **Confidence intervals** — score ± margin that tightens with more corroborating API signals
- **Risk classification** — `LOW` / `MEDIUM` / `HIGH` / `CRITICAL` with full scoring breakdown

### 🔐 Authentication & Reports
- JWT-based auth (signup / login / OAuth2 password flow)
- Per-user analysis history stored in SQLite (upgradeable to PostgreSQL)
- Shareable report IDs (UUID-based permalink system)
- PDF export ready (print-optimised CSS)

### 🚀 Performance & Reliability
- **Redis caching** with in-memory fallback — prevents redundant API calls
- **Async httpx client pool** — persistent TCP connections, no per-request overhead
- **Exponential back-off retry** on all external APIs (429, 500, 502, 503, 504)
- **Graceful mock/sandbox mode** — full feature parity even without API keys

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js 15)                 │
│   Dark glassmorphism UI · Tailwind CSS · shadcn/ui           │
└───────────────────────────┬──────────────────────────────────┘
                            │ REST API (JSON)
┌───────────────────────────▼──────────────────────────────────┐
│                    FastAPI Backend (Python 3.11+)             │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ News Service │  │ Image Service│  │ Trust Engine v3    │  │
│  │             │  │              │  │                    │  │
│  │ - NewsAPI   │  │ - Hive AI    │  │ - Weighted scoring │  │
│  │ - MediaStack│  │ - GCV Vision │  │ - Tone analysis    │  │
│  │ - GDELT     │  │ - EXIF parser│  │ - Confidence ±     │  │
│  │ - URL scraper│ │ - dHash cache│  │ - Entity signals   │  │
│  └──────┬──────┘  └──────┬───────┘  └─────────┬──────────┘  │
│         │                │                     │             │
│  ┌──────▼────────────────▼─────────────────────▼──────────┐  │
│  │              Shared Services                           │  │
│  │  GroqService · FactcheckService · CacheService        │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────┐  ┌───────────────────────────────────┐    │
│  │  SQLite DB   │  │  Redis (optional) / In-Memory     │    │
│  │  (Analysis,  │  │  Cache (fallback, 500-entry LRU)  │    │
│  │   User)      │  └───────────────────────────────────┘    │
│  └──────────────┘                                           │
└──────────────────────────────────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
  Google Fact Check    Groq Llama 3.1     Hive Moderation
  NewsAPI / GDELT      (LLM Reasoning)    Google Vision API
  MediaStack
```

---

## 📁 Project Structure

```
TruthLens AI/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routers (news, image, reports, health, users)
│   │   ├── core/           # Config, security, logging
│   │   ├── models/         # SQLAlchemy ORM models (Analysis, User)
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic
│   │   │   ├── trust_engine.py      # Weighted scoring engine
│   │   │   ├── groq_service.py      # Groq LLM integration
│   │   │   ├── factcheck_service.py # Google Fact Check API
│   │   │   ├── news_service.py      # News aggregation pipeline
│   │   │   ├── image_service.py     # Image forensics pipeline
│   │   │   ├── entity_service.py    # Named entity extraction
│   │   │   └── url_scraper.py       # Article URL scraping
│   │   └── utils/
│   │       ├── helpers.py           # CacheService (Redis + in-memory)
│   │       ├── exif.py              # EXIF metadata extractor
│   │       └── seed.py              # Database seeding script
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js App Router pages
│   │   ├── components/     # Shared UI components (shadcn/ui + custom)
│   │   └── lib/            # API client, utilities
│   └── package.json
├── docs/                   # Extended documentation
├── tests/                  # Test suite
├── .env.example            # Environment variable template
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 20+** and **pnpm**
- API keys (optional — all services have sandbox/mock fallbacks)

### 1. Clone the repository

```bash
git clone https://github.com/jabbarhasib-sys/TruthLens-AI.git
cd TruthLens-AI
```

### 2. Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env and add your API keys (see Environment Variables section)

# Seed the database with demo data
python -m app.utils.seed

# Start the API server
uvicorn app.main:app --reload --port 8000
```

API docs available at: **http://localhost:8000/docs**

### 3. Frontend setup

```bash
cd frontend

# Install dependencies
pnpm install

# Start the development server
pnpm dev
```

Frontend available at: **http://localhost:3000**

### 4. Demo Credentials (after seeding)

| Role  | Email                  | Password |
|-------|------------------------|----------|
| Admin | admin@truthlens.ai     | 123456   |
| User  | judge@hackathon.com    | 123456   |

---

## 🔑 Environment Variables

Create a `.env` file inside the `backend/` directory:

```env
# ── Core ─────────────────────────────────────────────────────
DATABASE_URL=sqlite:///./truthlens.db
JWT_SECRET=your-super-secret-jwt-key-change-in-production

# ── LLM (Groq) — Required for AI reasoning ───────────────────
# Get free key: https://console.groq.com
GROQ_API_KEY=gsk_...

# ── Fact Checking (Google) ────────────────────────────────────
# Enable at: https://console.cloud.google.com → Fact Check Tools API
GOOGLE_API_KEY=AIza...

# ── Image Analysis ────────────────────────────────────────────
# Google Cloud Vision (service account JSON path)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
# Hive Moderation AI: https://thehive.ai
HIVE_API_KEY=...

# ── News Sources ──────────────────────────────────────────────
# NewsAPI: https://newsapi.org
NEWS_API_KEY=...
# MediaStack: https://mediastack.com
MEDIASTACK_API_KEY=...

# ── Cache (optional) ──────────────────────────────────────────
# Leave empty to use the built-in in-memory cache
REDIS_URL=redis://localhost:6379/0
```

> **Note:** All API keys are optional. TruthLens AI runs in sandbox mode with realistic mock responses when keys are not configured, making it fully demonstrable without any API costs.

---

## 🌐 API Reference

Base URL: `http://localhost:8000/api`

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/signup` | Register a new user |
| `POST` | `/auth/login` | Login with email/password → JWT |
| `POST` | `/auth/login-oauth` | OAuth2 password form login |

### Verification

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/verify/news` | Verify a news claim or article URL |
| `POST` | `/verify/image` | Analyze an image for deepfakes/manipulation |

#### `POST /verify/news` — Request Body
```json
{
  "claim": "Scientists confirm that lemon juice cures COVID-19.",
  "url": "https://optional-article-url.com"
}
```

#### `POST /verify/image` — Form Data
```
file: <image file upload>
```

#### Response (both endpoints)
```json
{
  "id": "uuid-report-id",
  "trust_score": 12.5,
  "risk_level": "CRITICAL",
  "confidence_low": 8.0,
  "confidence_high": 17.0,
  "tone_analysis": {
    "overall_tone": "Fear-Inducing",
    "tone_labels": ["Fear-Inducing", "Outrage Bait"],
    "signals": []
  },
  "scoring_breakdown": {
    "deductions": [],
    "bonuses": []
  },
  "fact_checks": [],
  "news_reports": [],
  "ai_reasoning": "### TruthLens AI Verification Report\n..."
}
```

### Reports & Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/reports` | List user's analysis history |
| `GET` | `/reports/{id}` | Fetch a specific report by UUID |
| `GET` | `/health` | Liveness probe + integration status |

#### `GET /health` — Response
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "cache": "connected",
  "active_integrations": {
    "groq": true,
    "google_search": false,
    "newsapi": true,
    "mediastack": false,
    "hive_deepfake": true
  }
}
```

---

## 🧠 Trust Engine

The Trust Engine v3 calculates a weighted **Trust Score (0–100)** from 20+ independent signals.

### Score Interpretation

| Score | Risk Level | Meaning |
|-------|------------|---------|
| 75–100 | 🟢 **LOW** | Credible — corroborated by reputable sources |
| 50–74 | 🟡 **MEDIUM** | Uncertain — limited or mixed signals |
| 25–49 | 🟠 **HIGH** | Suspicious — multiple red flags detected |
| 0–24 | 🔴 **CRITICAL** | Likely misinformation — strong evidence of falsehood |

### News Scoring Signals

| Signal | Direction | Weight |
|--------|-----------|--------|
| False fact-check rating | ⬇️ Deduction | −45 pts |
| True fact-check rating | ⬆️ Bonus | +25 pts |
| Medical misinformation pattern | ⬇️ Deduction | −20 pts per match |
| Sensationalist language | ⬇️ Deduction | −6 pts per phrase (capped) |
| Political misinformation pattern | ⬇️ Deduction | −15 pts |
| No news coverage found | ⬇️ Deduction | −20 pts |
| 5+ independent news sources | ⬆️ Bonus | +20 pts |
| Credible source citation | ⬆️ Bonus | +8 pts |
| Propaganda phrases | ⬇️ Deduction | −8 pts |
| Fear/outrage language | ⬇️ Deduction | −5 to −6 pts |

### Image Scoring Signals

| Signal | Direction | Weight |
|--------|-----------|--------|
| Hive: AI-generated (>30%) | ⬇️ Deduction | −55 × probability |
| Hive: Manipulated (>30%) | ⬇️ Deduction | −45 × probability |
| Google Vision: Spoof VERY_LIKELY | ⬇️ Deduction | −25 pts |
| Editing software in EXIF | ⬇️ Deduction | −20 pts |
| No EXIF metadata | ⬇️ Deduction | −12 pts |
| Hive: Original (>75%) | ⬆️ Bonus | +15 pts |
| Full camera EXIF (make + model) | ⬆️ Bonus | +15 pts |
| GPS geolocation embedded | ⬆️ Bonus | +8 pts |

### Confidence Intervals

Every score includes a ±margin confidence interval. The margin **narrows** as more API signals agree, and **widens** in mock/sandbox mode or when data is sparse.

---

## 🛠️ Tech Stack

### Backend
| Layer | Technology |
|-------|-----------|
| Framework | FastAPI 0.110+ |
| Language | Python 3.11+ |
| LLM | Groq API (Llama 3.1 70B Versatile) |
| Database ORM | SQLAlchemy 2.0 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| HTTP Client | httpx (async, persistent pool) |
| Cache | Redis + in-memory LRU fallback |
| Auth | JWT (PyJWT) + bcrypt |
| Image Processing | Pillow, Google Cloud Vision |
| Deepfake Detection | Hive Moderation AI |
| Fact Check | Google Fact Check Tools API |
| News Aggregation | NewsAPI, MediaStack, GDELT |

### Frontend
| Layer | Technology |
|-------|-----------|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS + shadcn/ui |
| Design | Glassmorphism dark theme, emerald brand palette |
| Fonts | Geist via Google Fonts |

---

## 🧪 Running Tests

```bash
cd backend

# Run E2E API tests
python e2e_test.py

# Or with pytest
pytest tests/
```

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Branching and commit conventions
- Code style (ruff, black for Python; ESLint for TypeScript)
- Pull request checklist

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 🔒 Security

Found a vulnerability? Please review [SECURITY.md](SECURITY.md) for responsible disclosure guidelines. Do **not** open a public issue for security vulnerabilities.

---

<div align="center">

Built with ❤️ by **[@jabbarhasib-sys](https://github.com/jabbarhasib-sys)**

⭐ Star this repo if TruthLens AI helped you fight misinformation!

</div>
