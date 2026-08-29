# ⚡ ShopPilot AI — An Autonomous AI Agent for Smarter Commerce

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063.svg)](https://docs.pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests Passing](https://img.shields.io/badge/pytest-51%20passed%20(100%25%20pass%20rate)-success.svg)](https://docs.pytest.org/)
[![Coverage](https://img.shields.io/badge/coverage-85%25-informational.svg)](https://pytest-cov.readthedocs.io/)

> **Portfolio Project — AI Growth & Agentic Commerce**  
> **Author:** [Sai Dhejasvini](https://github.com/Sai-dhejasvini)  
> **GitHub Repository:** [Sai-dhejasvini/ShopPilot-AI](https://github.com/Sai-dhejasvini/ShopPilot-AI)  
> **Contact:** `saidhejasvini@gmail.com`

---

##  Executive Overview

**ShopPilot AI** is an internship-ready autonomous commerce web application designed to bridge the gap between natural language user intent and deterministic e-commerce transactions. 

Unlike traditional faceted search engines that force users to configure manual filters, or naive LLM wrappers that fabricate prices and non-existent inventory, **ShopPilot AI enforces architectural decoupling for grounded responses:**

```
USER QUERY
   ↓
LLM Layer — Requirement Extraction (Text → Validated Pydantic JSON)
   ↓
Deterministic Python / SQLite Engine (Filters & queries verified catalog)
   ↓
Explainable Ranking Engine (Transparent multi-factor scoring & decay curves)
   ↓
Agentic Orchestrator (Sequences Search, Filter, Rank, Compare, & Insights tools)
   ↓
LLM Layer — Grounded Synthesis (Summarizes ONLY factual Python/DB results)
   ↓
Modern Responsive Web Interface (HTML5 / CSS3 / ES6 / FastAPI)
```

The LLM is restricted from directly querying raw databases or inventing catalog items. If information is absent, the system explicitly responds: *"I don't have enough information to determine that."*

---

##  Key Features

1. ** Grounded AI Responses:** Architectural isolation prevents the LLM from inventing product specs, prices, or inventory.
2. ** Explainable Multi-Factor Scoring:** Every recommendation features an itemized score breakdown across:
   - **Budget Fit Score** ($S_{\text{budget}}$): Exponential decay for over-budget items; optimal scaling within range.
   - **Customer Rating Score** ($S_{\text{rating}}$): Normalized satisfaction index ($0.0 \to 1.0$).
   - **Feature Match Score** ($S_{\text{feature}}$): Regex/keyword match against RAM, GPU, display, storage, and battery.
   - **Popularity Score** ($S_{\text{popularity}}$): Log-scaled review count relative to 10k baseline.
   - **Stock Availability Score** ($S_{\text{availability}}$): In-stock fulfillment check.
3. ** Autonomous Agentic Tool Calling:** Sequences 6 discrete tools (`search_products`, `filter_products`, `rank_products`, `compare_products`, `get_product_details`, `generate_growth_insight`) based on user goals.
4. ** Context-Aware Conversational Memory:** Multi-turn context resolution allowing users to ask follow-up questions (e.g. *"Which of these has better battery life?"*) against previously discussed candidate sets.
5. ** Side-by-Side Product Comparison:** Automated tabular spec extraction and trade-off analysis (Value pick vs. Quality leader).
6. ** AI Growth & Commerce Analytics Dashboard:** Aggregates catalog distributions, budget clusters, and identifies unmet catalog demand gaps.
7. ** Modern SaaS UI/UX:** Clean, light SaaS design system built with responsive CSS Grid/Flexbox, real-time tool execution badges, and quick-prompt chips.

---

##  System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND WEB APPLICATION (HTML5 / CSS3 / ES6)                   │
│   Landing Page  •  AI Assistant Chat  •  Product Catalog  •  Comparison  •  Dashboard │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ HTTP / JSON REST APIs
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND API LAYER (`backend/main.py`)                   │
│   /api/chat   /api/search   /api/recommend   /api/compare   /api/analytics   /health   │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        AGENTIC ORCHESTRATION & TOOL CALLING                            │
│   - Intent & Requirement Extraction (Pydantic Schema)                                  │
│   - Session Memory & Multi-Turn Context Manager                                        │
│   - Autonomous Tool Selector:                                                          │
│     ├── `search_products()`         ├── `compare_products()`                           │
│     ├── `filter_products()`         ├── `get_product_details()`                        │
│     ├── `rank_products()`           └── `generate_growth_insight()`                    │
│   - Grounded Response Synthesizer (Grounded AI Responses)                              │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        DETERMINISTIC PYTHON & SQLITE CORE                              │
│   - Search Engine (`backend/search.py`): Parametric & Feature Regex Filtering          │
│   - Ranking Engine (`backend/ranking.py`): Explainable Multi-Factor Scoring            │
│   - Growth Analytics (`backend/analytics.py`): Business Intelligence & Demand Metrics  │
│   - Database Layer (`backend/database.py`): SQLite3 + Cleaned Catalog Cache            │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

##  Project Directory Structure

```text
ShopPilot-AI/
├── backend/
│   ├── __init__.py           # Package marker
│   ├── config.py             # Central path, weight, and environment configs
│   ├── schema.py             # Pydantic v2 data models
│   ├── database.py           # SQLite manager and interaction logger
│   ├── data_loader.py        # Dataset ingestion & schema validation
│   ├── preprocessing.py      # Cleaning pipeline (currency, ratings, deduplication)
│   ├── search.py             # Deterministic parametric search engine
│   ├── ranking.py            # Multi-factor explainable ranking engine
│   ├── recommender.py        # Search + Ranking orchestration
│   ├── llm.py                # Multi-provider LLM adapter (Anthropic, OpenAI, Gemini, Mock)
│   ├── tools.py              # Discrete agent tool functions (6 tools)
│   ├── agent.py              # Autonomous agent planning & execution
│   ├── memory.py             # Conversational session memory manager
│   ├── analytics.py          # AI growth & commerce intelligence engine
│   └── main.py               # FastAPI server and static frontend mount
├── frontend/
│   ├── index.html            # Single-page web application interface
│   ├── styles.css            # Light modern SaaS design system
│   └── script.js             # Client controller, API client, & chart renderers
├── data/
│   ├── raw/
│   │   ├── ecommerce_products.csv   # Raw e-commerce catalog dataset
│   │   └── generate_raw_data.py     # Reproducible catalog generator
│   └── processed/
│       └── products_cleaned.csv     # Cleaned catalog dataset
├── tests/
│   ├── __init__.py
│   ├── test_architecture.py  # Path, weight, and Pydantic validation tests
│   ├── test_data_loader.py   # Ingestion, schema validation, and missing file tests
│   ├── test_preprocessing.py # Currency parsing, rating bounds, deduplication tests
│   ├── test_search.py        # Category, budget, brand, and feature regex tests
│   ├── test_ranking.py       # Score bounds, weight customization, and sort tests
│   ├── test_llm.py           # Requirement extraction & synthesis tests
│   ├── test_agent.py         # 6-Tool execution and routing tests
│   ├── test_memory.py        # Multi-turn context resolution tests
│   ├── test_api.py           # FastAPI endpoint tests
│   └── benchmark_performance.py # 100-iteration performance benchmark
├── docs/
│   ├── architecture.md       # Detailed technical design document
│   ├── data_pipeline.md      # Data cleaning rules and schema audit
│   ├── agent_workflow.md     # Agent tool calling state machine
│   ├── testing.md            # Test matrix and coverage report
│   └── project_report.md     # Portfolio presentation report
├── .env.example              # Environment variables template
├── .gitignore                # Security controls excluding secrets and caches
├── requirements.txt          # Minimal dependencies
├── LICENSE                   # MIT License
└── README.md                 # Project documentation
```

---

##  Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/Sai-dhejasvini/ShopPilot-AI.git
cd ShopPilot-AI
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Defaults to `LLM_PROVIDER=mock` for deterministic local development without requiring paid API keys).*

### 4. Run Data Cleaning & Database Initialization
```bash
python -m backend.preprocessing
```

### 5. Start the Application Server
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
Open your browser at: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

##  Automated Testing & Measured Code Coverage

Execute the 51 automated tests and measure real code coverage:

```bash
pytest --cov=backend --cov-report=term-missing tests/ -v
```

**Measured Test Execution & Coverage:**
```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2
collected 51 items

tests/test_agent.py ................                                     [ 31%]
tests/test_api.py ......                                                 [ 43%]
tests/test_architecture.py .....                                         [ 52%]
tests/test_data_loader.py ....                                           [ 60%]
tests/test_llm.py ...                                                    [ 66%]
tests/test_memory.py ..                                                  [ 70%]
tests/test_preprocessing.py .....                                        [ 80%]
tests/test_ranking.py ...                                                [ 85%]
tests/test_search.py .......                                             [100%]

=============================== tests coverage ================================
Name                       Stmts   Miss  Cover
----------------------------------------------
backend\__init__.py            1      0   100%
backend\agent.py             255     38    85%
backend\analytics.py          31      1    97%
backend\config.py             42      0   100%
backend\data_loader.py        29      2    93%
backend\database.py           65      2    97%
backend\llm.py               127     51    60%
backend\main.py               86     13    85%
backend\memory.py             53      3    94%
backend\preprocessing.py     107     10    91%
backend\ranking.py           147     11    93%
backend\recommender.py        20      6    70%
backend\schema.py             64      1    98%
backend\search.py             58     10    83%
backend\tools.py              92     21    77%
----------------------------------------------
TOTAL                       1195    183    85%
======================= 51 passed, 1 warning in 9.14s ====================
```

---

##  Measured Performance Benchmarks

Run the benchmark script:
```bash
python -m tests.benchmark_performance
```

**Actual Measured Results (100 Iterations Each):**
- **Deterministic Search Engine:** Mean = `0.025 ms` (Median = `0.021 ms`, P95 = `0.037 ms`)
- **Ranking & Scoring Engine:** Mean = `1.231 ms` (Median = `0.928 ms`, P95 = `2.780 ms`)
- **End-to-End Agent Processing (Mock):** Mean = `12.908 ms` (Median = `12.537 ms`, P95 = `16.327 ms`)

---

## 💬 Example Queries & Deterministic Routing

| Intent | Query Example | Agent Tool Execution | Grounded Result Behavior |
|---|---|---|---|
| **Shopping Discovery** | *"I need a laptop under ₹70,000 for programming with 16GB RAM"* | `search_products` $\to$ `rank_products` | Ranked top matches with multi-factor breakdown |
| **Cheapest Option** | *"Which one is the cheapest?"* | `get_extreme_product(metric='price', direction='min')` | Selects minimum numeric price (e.g. Dell Inspiron at ₹53,490) |
| **Highest Rating** | *"Which one has the highest rating?"* | `get_extreme_product(metric='rating', direction='max')` | Selects maximum rating (e.g. Lenovo ThinkPad at 4.4★) |
| **Most Reviews** | *"Which one has the most reviews?"* | `get_extreme_product(metric='reviews', direction='max')` | Selects maximum review count (e.g. Lenovo IdeaPad at 3,200 reviews) |
| **Best for Gaming** | *"Which one is the best for gaming?"* | `rank_for_gaming` | Scores by GPU (RTX 4050/3050), 144Hz/120Hz display, and H-series CPU |
| **Best Value** | *"Which one is the best value for money?"* | `rank_for_value` | Balances competitive price with rating & specs |
| **Multi-Criteria Extrema** | *"Which one has lowest price and highest rating?"* | `get_multi_criteria_extrema` | Grounded breakdown distinguishing cheapest vs highest rated |
| **Compare Extremes** | *"Compare the cheapest and highest-rated laptop"* | `get_extreme_product` $\to$ `compare_products` | Deterministically compares cheapest & highest rated items |
| **Growth Intelligence** | *"Show me catalog demand gaps and trends"* | `generate_growth_insight` | Strategic inventory insights & demand curves |

---

##  Limitations & Future Scope

- **Vector / Hybrid Semantic Search:** Deterministic keyword and regex search is currently prioritized for strict explainability. Adding a local ChromaDB/FAISS vector index for soft aesthetic matching is a potential future extension.
- **Multi-Vendor Live APIs:** Live pricing and inventory scrapers can be connected to `backend/data_loader.py`.
- **Live LLM API Keys:** While offline mock mode is verified, connecting paid Anthropic Claude or OpenAI API keys in `.env` enables full LLM reasoning.

---

##  Author

- **Sai Dhejasvini**
- **GitHub:** [@Sai-dhejasvini](https://github.com/Sai-dhejasvini)
- **Email:** `saidhejasvini@gmail.com`
- **Domain:** AI Growth & Agentic Commerce

---

##  License
This project is open-source and licensed under the [MIT License](LICENSE).
