"""
ShopPilot AI - FastAPI Backend Application
Serves REST API endpoints for agentic chat, parametric search, explainable ranking,
product comparisons, growth analytics, and mounts the modern frontend web application.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Path as FastPath
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from backend.config import config
from backend.schema import (
    ChatRequest,
    ChatResponse,
    Product,
    RankedProduct,
    ExtractedRequirement,
)
from backend.agent import agent
from backend.search import search_engine
from backend.recommender import recommender
from backend.tools import compare_products
from backend.analytics import analytics_engine
from backend.database import db

# Initialize FastAPI app
app = FastAPI(
    title="ShopPilot AI - Autonomous AI Agent for Smarter Commerce",
    description="Backend API for intent extraction, deterministic search, explainable ranking, and agentic commerce.",
    version="1.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request Models
class SearchRequest(BaseModel):
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    brands: Optional[List[str]] = None
    min_rating: Optional[float] = None
    required_features: Optional[List[str]] = None
    availability_only: bool = True
    sort_by: str = "rating_desc"
    top_n: Optional[int] = 10


class CompareRequest(BaseModel):
    product_ids: List[str] = Field(..., min_length=1, description="List of product IDs to compare")


class RecommendRequest(BaseModel):
    requirements: ExtractedRequirement
    top_n: Optional[int] = 5


# API Endpoints
@app.get("/health")
def healthcheck():
    """Health check endpoint confirming server status and catalog count."""
    products = db.get_all_products()
    return {
        "status": "healthy",
        "app_name": "ShopPilot AI",
        "version": "1.0.0",
        "catalog_size": len(products),
        "llm_provider": config.llm_provider,
        "currency": config.currency_symbol,
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Main agent conversational endpoint.
    Understands user intent, extracts requirements, calls tools, and synthesizes grounded response.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="User message cannot be empty.")
    try:
        response = agent.process_message(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")


@app.post("/api/search")
def search_endpoint(request: SearchRequest):
    """Deterministic product search endpoint without LLM involvement."""
    results = search_engine.search(
        category=request.category,
        min_price=request.min_price,
        max_price=request.max_price,
        brands=request.brands,
        min_rating=request.min_rating,
        required_features=request.required_features,
        availability_only=request.availability_only,
        sort_by=request.sort_by,
        top_n=request.top_n,
    )
    return {
        "count": len(results),
        "products": [p.model_dump() for p in results],
    }


@app.post("/api/recommend")
def recommend_endpoint(request: RecommendRequest):
    """Multi-factor explainable recommendation endpoint."""
    ranked = recommender.recommend(
        requirement=request.requirements,
        top_n=request.top_n or 5,
    )
    return {
        "count": len(ranked),
        "ranked_products": [rp.model_dump() for rp in ranked],
    }


@app.post("/api/compare")
def compare_endpoint(request: CompareRequest):
    """Side-by-side product comparison and trade-off synthesis."""
    if not request.product_ids:
        raise HTTPException(status_code=400, detail="Product IDs list cannot be empty.")
    result = compare_products(request.product_ids)
    return result


@app.get("/api/products")
def get_products_endpoint(
    category: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
):
    """Retrieves full catalog or category slice."""
    if category:
        prods = search_engine.search(category=category, top_n=limit)
    else:
        prods = db.get_all_products()[:limit]
    return {
        "count": len(prods),
        "products": [p.model_dump() for p in prods],
    }


@app.get("/api/products/{product_id}")
def get_product_by_id_endpoint(product_id: str = FastPath(...)):
    """Retrieves single product details by ID."""
    prod = search_engine.get_by_id(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found.")
    return {"product": prod.model_dump()}


@app.get("/api/analytics")
def get_analytics_endpoint():
    """Returns business growth KPIs, category distribution, budget clusters, and catalog gaps."""
    return analytics_engine.get_growth_dashboard_metrics()


# Mount Static Frontend Files
frontend_path = config.paths.FRONTEND_DIR
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

    @app.get("/")
    def serve_frontend_root():
        index_file = frontend_path / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return JSONResponse({"message": "ShopPilot AI API running. Frontend index.html not found."})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=config.app_host, port=config.app_port, reload=True)
