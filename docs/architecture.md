# Technical Architecture Document — ShopPilot AI

## 1. System Overview
ShopPilot AI is an autonomous, grounded AI commerce platform pairing an agentic LLM orchestration layer with a deterministic Python/SQLite data engine.

## 2. Core Architectural Decoupling
```
[User Request]
       │
       ▼
[FastAPI REST API Layer]
       │
       ▼
[Agent Orchestrator] <───> [Session Memory Manager]
       │
       ▼ (1. Intent & Structured Extraction)
[Pydantic Schema Validator]
       │
       ▼ (2. Validated Tool Calls)
[Deterministic Python & SQLite Engine]
   ├── SearchEngine (Parametric & Regex Filtering)
   └── RankingEngine (Multi-Factor Scoring & Decay Curves)
       │
       ▼ (3. Verified Catalog Products)
[Grounded LLM Synthesizer]
       │
       ▼ (4. Grounded AI Responses & UI Cards)
[Client Web Application]
```

## 3. Pydantic Data Contracts
All internal data exchanges are governed by strict Pydantic v2 schemas (`Product`, `ExtractedRequirement`, `ScoreBreakdown`, `RankedProduct`, `AgentToolCall`, `GrowthInsight`).

## 4. Grounded AI Response Principles
1. Product specifications, prices, stock, and ratings are loaded exclusively from SQLite records.
2. The LLM never invents candidate items.
3. Scoring is mathematically deterministic and computed in Python.
