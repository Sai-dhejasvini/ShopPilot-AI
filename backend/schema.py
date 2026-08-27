"""
ShopPilot AI - Core Pydantic Schemas & Data Contracts
Defines rigid data models for products, user requirements, ranking results, and tools.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class Product(BaseModel):
    """Product schema conforming to the target dataset specification."""

    product_id: str = Field(..., description="Unique product identifier")
    product_name: str = Field(..., description="Full descriptive name of the product")
    category: str = Field(..., description="Primary product category")
    subcategory: str = Field(
        default="General", description="Subcategory or specific item type"
    )
    brand: str = Field(..., description="Brand or manufacturer")
    price: float = Field(..., ge=0.0, description="Price in INR (₹)")
    rating: float = Field(..., ge=0.0, le=5.0, description="Customer rating out of 5.0")
    review_count: int = Field(
        ..., ge=0, description="Total number of verified customer reviews"
    )
    description: str = Field(
        default="", description="Product overview and feature summary"
    )
    features: List[str] = Field(
        default_factory=list,
        description="List of key technical specifications / features",
    )
    availability: bool = Field(
        default=True, description="True if in stock, False otherwise"
    )

    # Optional extended fields
    discount_percentage: Optional[float] = Field(
        default=0.0, ge=0.0, le=100.0, description="Discount percentage if available"
    )
    original_price: Optional[float] = Field(
        default=None, description="Original MRP in INR"
    )


class ExtractedRequirement(BaseModel):
    """Structured requirement extracted by LLM from free-form user query."""

    category: Optional[str] = Field(
        default=None, description="Target product category (e.g. Laptop, Smartphone)"
    )
    min_price: Optional[float] = Field(
        default=None, ge=0.0, description="Minimum budget in INR"
    )
    max_price: Optional[float] = Field(
        default=None, ge=0.0, description="Maximum budget in INR"
    )
    brand_preference: List[str] = Field(
        default_factory=list, description="Preferred brand names"
    )
    required_features: List[str] = Field(
        default_factory=list,
        description="Key features extracted (e.g. '16GB RAM', 'OLED display')",
    )
    min_rating: Optional[float] = Field(
        default=None, ge=0.0, le=5.0, description="Minimum acceptable rating"
    )
    priority: Optional[str] = Field(
        default=None,
        description="Primary purchasing priority (e.g. 'battery life', 'performance')",
    )
    use_case: Optional[str] = Field(
        default=None,
        description="Target user intent (e.g. 'Programming', 'Gaming', 'Office work')",
    )

    @field_validator("max_price")
    @classmethod
    def validate_budget_bounds(cls, v: Optional[float], info) -> Optional[float]:
        min_p = info.data.get("min_price")
        if v is not None and min_p is not None and v < min_p:
            raise ValueError(
                f"max_price ({v}) cannot be less than min_price ({min_p})"
            )
        return v


class ScoreBreakdown(BaseModel):
    """Detailed, explainable score breakdown for transparent recommendation."""

    budget_fit_score: float = Field(
        ..., ge=0.0, le=1.0, description="Normalized score for price adherence"
    )
    rating_score: float = Field(
        ..., ge=0.0, le=1.0, description="Normalized score based on customer ratings"
    )
    feature_match_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized score for matching requested features",
    )
    popularity_score: float = Field(
        ..., ge=0.0, le=1.0, description="Normalized score based on review volume"
    )
    availability_score: float = Field(
        ..., ge=0.0, le=1.0, description="Normalized score for in-stock status"
    )
    final_score: float = Field(
        ..., ge=0.0, le=1.0, description="Weighted composite score"
    )
    explanation: str = Field(
        ..., description="Human-readable reason explaining this product's rank"
    )


class RankedProduct(BaseModel):
    """Product paired with its explainable scoring breakdown."""

    product: Product
    rank: int = Field(..., ge=1, description="Rank position (1 = best recommendation)")
    scores: ScoreBreakdown


class AgentToolCall(BaseModel):
    """Structured representation of an agent's selected action."""

    tool_name: str = Field(..., description="Name of the tool to invoke")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Validated arguments for the tool"
    )
    thought_process: str = Field(
        ..., description="Step-by-step reasoning behind selecting this tool"
    )


class GrowthInsight(BaseModel):
    """Commerce/Growth intelligence insight generated from aggregate data."""

    insight_type: str = Field(
        ..., description="Category of insight (e.g. Trend, Demand Gap, Price Sweetspot)"
    )
    title: str = Field(..., description="Brief headline summarizing the finding")
    description: str = Field(..., description="Detailed analytical description")
    metric_value: Optional[str] = Field(
        default=None, description="Quantified metric or percentage"
    )
    actionable_recommendation: str = Field(
        ..., description="Recommended strategic commerce/catalog action"
    )


class ChatRequest(BaseModel):
    """Incoming user chat message request."""

    message: str = Field(..., min_length=1, description="User's natural language input")
    session_id: Optional[str] = Field(
        default="default_session", description="Session ID for conversational memory"
    )


class ChatResponse(BaseModel):
    """Structured response from the agent to the UI."""

    reply: str
    session_id: str
    tools_used: List[AgentToolCall] = Field(default_factory=list)
    products: List[RankedProduct] = Field(default_factory=list)
    comparison: Optional[Dict[str, Any]] = None
    insights: Optional[List[GrowthInsight]] = None
