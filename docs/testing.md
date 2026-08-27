# Testing Strategy & Quality Assurance — ShopPilot AI

## 1. Overview
The testing suite contains **41 automated tests** implemented with `pytest` covering all system modules:

## 2. Test Matrix
- `tests/test_architecture.py` (5 tests): Path configs, ranking weight normalization ($=1.0$), Pydantic validation.
- `tests/test_data_loader.py` (4 tests): Ingestion, schema verification, missing column exceptions, diagnostics.
- `tests/test_preprocessing.py` (5 tests): Currency parsing, rating range bounds, feature parsing, stock mapping, pipeline integrity.
- `tests/test_search.py` (7 tests): Category filtering, budget bounds, brand matching, regex feature search, stock filtering, empty results.
- `tests/test_ranking.py` (3 tests): Mathematical score boundaries ($0.0 \to 1.0$), sort ordering, recommender integration.
- `tests/test_llm.py` (3 tests): Extraction across categories, Pydantic JSON compliance, grounded explanation synthesis.
- `tests/test_agent.py` (6 tests): Tool execution, comparison logic, product detail lookup, agentic routing.
- `tests/test_memory.py` (2 tests): Multi-turn session memory recording and follow-up query re-evaluation.
- `tests/test_api.py` (6 tests): Healthcheck, `/api/chat`, `/api/search`, `/api/compare`, `/api/products`, `/api/analytics`.
