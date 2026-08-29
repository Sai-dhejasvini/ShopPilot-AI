# Testing Strategy & Quality Assurance — ShopPilot AI

## 1. Overview
The testing suite contains **51 automated tests** implemented with `pytest` and measured using `pytest-cov`, covering all system modules:

## 2. Test Matrix
- `tests/test_architecture.py` (5 tests): Path configs, ranking weight normalization ($=1.0$), Pydantic validation.
- `tests/test_data_loader.py` (4 tests): Ingestion, schema verification, missing column exceptions, diagnostics.
- `tests/test_preprocessing.py` (5 tests): Currency parsing, rating range bounds, feature parsing, stock mapping, pipeline integrity.
- `tests/test_search.py` (7 tests): Category filtering, budget bounds, brand matching, regex feature search, stock filtering, empty results.
- `tests/test_ranking.py` (3 tests): Mathematical score boundaries ($0.0 \to 1.0$), sort ordering, recommender integration.
- `tests/test_llm.py` (3 tests): Extraction across categories, Pydantic JSON compliance, grounded explanation synthesis.
- `tests/test_agent.py` (16 tests): Deterministic tool execution (`search_products`, `filter_products`, `rank_products`, `get_extreme_product`, `get_multi_criteria_extrema`, `rank_for_gaming`, `rank_for_value`, `compare_products`, `get_product_details`, `generate_growth_insight`), follow-up extrema routing (cheapest, most expensive, highest rating, most reviews, multi-criteria, gaming, value, extreme comparison), and candidate memory preservation.
- `tests/test_memory.py` (2 tests): Multi-turn session memory recording and follow-up query re-evaluation.
- `tests/test_api.py` (6 tests): Healthcheck, `/api/chat`, `/api/search`, `/api/compare`, `/api/products`, `/api/analytics`.

## 3. Measured Coverage & Test Pass Rate
- **Test Pass Rate:** 51 / 51 Passed (100% pass rate)
- **Measured Code Coverage:** **85%** total coverage across backend modules (core engine modules `database.py`, `config.py`, `schema.py`, `analytics.py`, `data_loader.py`, `preprocessing.py`, `ranking.py` exceed 90-100%).
