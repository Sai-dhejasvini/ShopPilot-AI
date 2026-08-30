# ShopPilot AI — An Autonomous AI Agent for Smarter Commerce

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063.svg)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-51%20passed-success.svg)](https://docs.pytest.org/)
[![Coverage](https://img.shields.io/badge/coverage-85%25-informational.svg)](https://pytest-cov.readthedocs.io/)

**Portfolio Project — AI Growth & Agentic Commerce**

| | |
|---|---|
| **Author** | [Sai Dhejasvini](https://github.com/Sai-dhejasvini) |
| **Repository** | [Sai-dhejasvini/ShopPilot-AI](https://github.com/Sai-dhejasvini/ShopPilot-AI) |
| **Contact** | saidhejasvini@gmail.com |
| **Live Demo** | [shoppilot-ai-kqk5.onrender.com](https://shoppilot-ai-kqk5.onrender.com/) |

> The app is hosted on Render's free tier, so it may take a few seconds to wake up after a period of inactivity.

**Try it with queries like:**
- `Show me laptops under ₹70,000`
- `Show me the cheapest laptop`
- `Show me the most expensive smartphone`
- `Which one is best for gaming?`
- `Compare the cheapest and highest-rated laptop`

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Project Structure](#project-structure)
5. [Getting Started](#getting-started)
6. [Deployment](#deployment)
7. [Testing & Coverage](#testing--coverage)
8. [Performance Benchmarks](#performance-benchmarks)
9. [Example Queries](#example-queries)
10. [Grounding & Reliability](#grounding--reliability)
11. [Technology Stack](#technology-stack)
12. [Limitations & Future Scope](#limitations--future-scope)
13. [License](#license)

---

## Overview

**ShopPilot AI** is an autonomous, AI-powered commerce web application that bridges natural-language shopping intent with deterministic e-commerce recommendations. Instead of forcing users to manually configure filters, it lets them describe what they want in plain language.

The system combines:

- LLM-based requirement extraction
- Deterministic Python and SQLite catalog operations
- Explainable, multi-factor product ranking
- Autonomous agentic tool orchestration
- Conversational session memory
- Product comparison and commerce analytics
- A modern, responsive web interface

Unlike a naive LLM shopping assistant, ShopPilot AI never allows the language model to invent product information. Language understanding is strictly separated from factual catalog operations:

```
User Query
   │
   ▼
LLM Layer — Requirement Extraction (text → validated Pydantic JSON)
   │
   ▼
Deterministic Python / SQLite Engine (verified catalog search & filtering)
   │
   ▼
Explainable Ranking Engine (multi-factor product scoring)
   │
   ▼
Agentic Orchestrator (search → filter → rank → compare → insights)
   │
   ▼
LLM Layer — Grounded Response Synthesis
   │
   ▼
Web Interface (HTML5 / CSS3 / JavaScript / FastAPI)
```

The LLM cannot query the raw database directly or fabricate catalog data. If the catalog lacks sufficient information to answer a request, the system responds honestly:

> *"I don't have enough information to determine that."*

---

## Key Features

### 1. Grounded AI Responses
Language-model reasoning is separated from data operations — the LLM extracts requirements, while Python and SQLite handle the actual catalog logic. This prevents fabricated product names, prices, specifications, ratings, or inventory data.

### 2. Explainable Multi-Factor Product Ranking
Recommendations are scored across several measurable factors:

| Factor | Description |
|---|---|
| **Budget Fit** | How well price matches the requested budget, using price-distance and decay logic |
| **Customer Rating** | Ratings normalized into a comparable satisfaction score |
| **Feature Match** | Matches requested attributes — RAM, GPU, display, storage, battery, processor, etc. |
| **Popularity** | Review volume as a secondary popularity signal |
| **Stock Availability** | Whether the product is currently in stock |

The result is an explainable recommendation, not an opaque LLM guess.

### 3. Autonomous Agentic Tool Calling
The agent orchestrates deterministic tools based on user intent:

```
search_products()
filter_products()
rank_products()
compare_products()
get_product_details()
generate_growth_insight()
```

### 4. Context-Aware Conversational Memory
The agent supports multi-turn conversations and preserves the relevant candidate set for follow-up questions:

```
User: Show me laptops under ₹70,000.
AI:   Here are the best matching laptops...

User: Which one is cheapest?
AI:   The cheapest option is...

User: Which one has the best rating?
AI:   The highest-rated option is...
```

### 5. Global Extreme Product Queries
Explicit extrema requests are resolved against the correct catalog scope:

- `Show me the cheapest laptop` → globally cheapest laptop
- `Show me the most expensive laptop` → globally most expensive laptop
- `Show me the cheapest smartphone` / `Show me the most expensive smartphone` → same, scoped to smartphones

Follow-ups like `Which one is the most expensive?` operate on the prior candidate set when context indicates that's the intent.

### 6. Side-by-Side Product Comparison
```
Compare the cheapest and highest-rated laptop
```
The system identifies the relevant products and generates a grounded, spec-level comparison.

### 7. AI Growth & Commerce Analytics
An analytics layer surfaces commerce intelligence: category distributions, budget clusters, catalog characteristics, demand gaps, potential inventory opportunities, and product trends — extending the project beyond a shopping chatbot into a lightweight commerce intelligence system.

### 8. Modern SaaS User Interface
Responsive layout, AI assistant interface, product discovery, product cards, comparison view, analytics dashboard, quick-prompt chips, and tool-execution indicators — built with CSS Grid/Flexbox.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                     FRONTEND WEB APPLICATION                         │
│                    HTML5 / CSS3 / JavaScript                         │
│  Landing Page · AI Assistant · Product Catalog · Comparison ·        │
│  Dashboard                                                            │
└───────────────────────────────┬────────────────────────────────────┘
                                 │ HTTP / JSON REST APIs
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       FASTAPI BACKEND                                 │
│                       backend/main.py                                 │
│  /api/chat  /api/search  /api/recommend  /api/compare                │
│  /api/analytics  /health                                              │
└───────────────────────────────┬────────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  AGENTIC ORCHESTRATION LAYER                          │
│  Requirement Extraction · Intent Detection · Session Memory ·         │
│  Tool Selection · Search/Filter/Rank/Compare ·                        │
│  Grounded Response Synthesis                                          │
└───────────────────────────────┬────────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│               DETERMINISTIC PYTHON + SQLITE CORE                      │
│  Search Engine   → backend/search.py                                  │
│  Ranking Engine  → backend/ranking.py                                 │
│  Analytics       → backend/analytics.py                               │
│  Database        → backend/database.py                                │
│  Data Loading    → backend/data_loader.py                             │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
ShopPilot-AI/
├── backend/
│   ├── __init__.py
│   ├── config.py
│   ├── schema.py
│   ├── database.py
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── search.py
│   ├── ranking.py
│   ├── recommender.py
│   ├── llm.py
│   ├── tools.py
│   ├── agent.py
│   ├── memory.py
│   ├── analytics.py
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
├── data/
│   ├── raw/
│   │   ├── ecommerce_products.csv
│   │   └── generate_raw_data.py
│   └── processed/
│       └── products_cleaned.csv
│
├── tests/
│   ├── __init__.py
│   ├── test_architecture.py
│   ├── test_data_loader.py
│   ├── test_preprocessing.py
│   ├── test_search.py
│   ├── test_ranking.py
│   ├── test_llm.py
│   ├── test_agent.py
│   ├── test_memory.py
│   ├── test_api.py
│   └── benchmark_performance.py
│
├── docs/
│   ├── architecture.md
│   ├── data_pipeline.md
│   ├── agent_workflow.md
│   ├── testing.md
│   └── project_report.md
│
├── .env.example
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Sai-dhejasvini/ShopPilot-AI.git
cd ShopPilot-AI
```

### 2. Create a virtual environment
```bash
python -m venv venv
```
- **Windows:** `venv\Scripts\activate`
- **macOS / Linux:** `source venv/bin/activate`

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```
For deterministic local development without a paid API key, set:
```
LLM_PROVIDER=mock
```

### 5. Initialize / process the catalog
```bash
python -m backend.preprocessing
```

### 6. Start the application
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Deployment

ShopPilot AI is deployed on **Render** as a FastAPI web service.

**Live app:** https://shoppilot-ai-kqk5.onrender.com/

Typical Render configuration:

| Setting | Value |
|---|---|
| Language | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |

The deployed service serves both the frontend and backend through the same FastAPI application.

---

## Testing & Coverage

Run the full test suite:
```bash
pytest --cov=backend --cov-report=term-missing tests/ -v
```

Coverage includes architecture, data loading, preprocessing, search, ranking, LLM requirement extraction, agent routing, conversational memory, and API endpoints.

**Documented run:** 51 passed · 85% total coverage

| Module | Coverage |
|---|---|
| `backend/__init__.py` | 100% |
| `backend/config.py` | 100% |
| `backend/schema.py` | 98% |
| `backend/analytics.py` | 97% |
| `backend/database.py` | 97% |
| `backend/memory.py` | 94% |
| `backend/data_loader.py` | 93% |
| `backend/ranking.py` | 93% |
| `backend/preprocessing.py` | 91% |
| `backend/agent.py` | 85% |
| `backend/main.py` | 85% |
| `backend/search.py` | 83% |
| `backend/tools.py` | 77% |
| `backend/recommender.py` | 70% |
| `backend/llm.py` | 60% |
| **Total** | **85%** |

---

## Performance Benchmarks

Benchmarks use 100 iterations per operation, measured with the mock LLM configuration.

| Stage | Mean | Median | P95 |
|---|---|---|---|
| Deterministic Search Engine | 0.025 ms | 0.021 ms | 0.037 ms |
| Ranking & Scoring Engine | 1.231 ms | 0.928 ms | 2.780 ms |
| End-to-End Agent Processing | 12.908 ms | 12.537 ms | 16.327 ms |

Run the benchmark yourself:
```bash
python -m tests.benchmark_performance
```

---

## Example Queries

| Intent | Example Query | Expected Behavior |
|---|---|---|
| Shopping Discovery | "I need a laptop under ₹70,000 for programming with 16GB RAM" | Searches and ranks matching products |
| Cheapest Product | "Show me the cheapest laptop" | Finds the minimum-priced laptop |
| Most Expensive Product | "Show me the most expensive laptop" | Finds the maximum-priced laptop |
| Cheapest Smartphone | "Show me the cheapest smartphone" | Finds the minimum-priced smartphone |
| Most Expensive Smartphone | "Show me the most expensive smartphone" | Finds the maximum-priced smartphone |
| Highest Rating | "Which one has the highest rating?" | Finds the highest-rated candidate |
| Most Reviews | "Which one has the most reviews?" | Finds the candidate with the most reviews |
| Gaming | "Which one is best for gaming?" | Ranks products using gaming-related features |
| Best Value | "Which one is the best value for money?" | Balances price, rating, and features |
| Comparison | "Compare the cheapest and highest-rated laptop" | Identifies and compares relevant products |
| Follow-up | "Which one is cheapest?" | Uses the active conversational candidate set |
| Analytics | "Show me catalog demand gaps and trends" | Generates commerce insights |

**Deterministic routing examples:**

- **Global extreme query** — `Show me the most expensive laptop` is interpreted as an explicit category + extrema request and searched against the full catalog scope.
- **Conversational follow-up** — After `Show me laptops under ₹70,000`, asking `Which one is cheapest?` operates on the previously generated candidate set.
- **Category override** — After a broad `Show me expensive products` query, asking `Show me the most expensive laptop` is treated as a new global category search rather than being restricted to the prior mixed-category set.

---

## Grounding & Reliability

```
LLM → Extract Intent → Python/SQLite → Verified Catalog Data
    → Ranking/Filtering → LLM → Grounded Explanation
```

The language model is never the source of truth for prices, inventory, ratings, or specifications — that responsibility belongs entirely to the deterministic catalog layer.

---

## Technology Stack

**Frontend:** HTML5 · CSS3 · JavaScript (ES6) · CSS Grid · Flexbox

**Backend:** Python · FastAPI · Pydantic v2 · SQLite · Uvicorn

**AI / Agent Layer:** LLM requirement extraction · grounded response synthesis · agentic orchestration · tool calling · conversational memory

**Data & Analytics:** CSV catalog · SQLite · deterministic search · explainable ranking · commerce analytics

**Testing:** Pytest · Pytest-Cov · automated API tests · agent routing tests · performance benchmarks

**Deployment:** GitHub · Render

---

## Limitations & Future Scope

- **Vector / hybrid semantic search** — the current architecture prioritizes deterministic keyword and regex search for strict explainability. Future versions could add ChromaDB, FAISS, local embedding models, or hybrid semantic + keyword retrieval.
- **Multi-vendor live commerce APIs** — integration with live vendor APIs for real-time pricing, inventory, vendor comparison, and delivery information.
- **Live LLM providers** — the architecture already supports configurable providers; future deployments can connect paid providers via environment variables and API keys.
- **Advanced commerce intelligence** — personalized recommendations, user preference learning, price trend prediction, inventory forecasting, automated promotion recommendations, vendor performance analytics, and demand forecasting.

---

## Author

**Sai Dhejasvini**
Domain: AI Growth & Agentic Commerce

- GitHub: [@Sai-dhejasvini](https://github.com/Sai-dhejasvini)
- Repository: [ShopPilot-AI](https://github.com/Sai-dhejasvini/ShopPilot-AI)
- Email: saidhejasvini@gmail.com

---

## License

This project is open-source and licensed under the [MIT License](LICENSE).

---

### Try ShopPilot AI

**Live demo:** https://shoppilot-ai-kqk5.onrender.com/
**Repository:** https://github.com/Sai-dhejasvini/ShopPilot-AI
