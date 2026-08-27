# Agentic Workflow & Tool Calling State Machine — ShopPilot AI

## 1. Agent Design Principles
ShopPilot AI is a goal-oriented autonomous agent. Rather than treating an LLM as an answer generator, the LLM functions as a **reasoner and tool dispatcher**.

## 2. Tool Inventory
1. `search_products(category, min_price, max_price, brands, min_rating, required_features, top_n)`
2. `filter_products(products, constraints)`
3. `rank_products(products, requirements, weights)`
4. `get_product_details(product_id)`
5. `compare_products(product_ids)`
6. `generate_growth_insight(metric_type)`

## 3. Tool Calling Workflow
```mermaid
flowchart TD
    A["User Request"] --> B["Check Session Memory"]
    B --> C["LLM Intent Analysis"]
    C --> D{"Tool Selection"}
    D -->|"Discovery"| E["search_products() -> rank_products()"]
    D -->|"Comparison"| F["compare_products()"]
    D -->|"Product Specs"| G["get_product_details()"]
    D -->|"Analytics"| H["generate_growth_insight()"]
    E --> I["Grounded Synthesis"]
    F --> I
    G --> I
    H --> I
    I --> J["Return ChatResponse"]
```
