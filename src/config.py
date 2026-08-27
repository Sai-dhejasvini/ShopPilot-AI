"""
ShopPilot AI - Central Configuration Module
Defines path constants, ranking weights, and environment settings.
"""

from dataclasses import dataclass, field
import os
from pathlib import Path
from dotenv import load_dotenv

# Project Root Directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env file from project root
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class PathConfig:
    """Centralized path configurations for datasets and artifacts."""

    ROOT_DIR: Path = PROJECT_ROOT
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RAW_DATA_DIR: Path = PROJECT_ROOT / "data" / "raw"
    PROCESSED_DATA_DIR: Path = PROJECT_ROOT / "data" / "processed"
    RAW_DATA_FILE: Path = PROJECT_ROOT / "data" / "raw" / "ecommerce_products.csv"
    PROCESSED_DATA_FILE: Path = (
        PROJECT_ROOT / "data" / "processed" / "products_cleaned.csv"
    )
    ANALYTICS_LOG_FILE: Path = (
        PROJECT_ROOT / "data" / "processed" / "analytics_logs.json"
    )


@dataclass(frozen=True)
class RankingWeights:
    """Configurable weights for the multi-attribute ranking engine."""

    budget: float = float(os.getenv("WEIGHT_BUDGET", "0.30"))
    rating: float = float(os.getenv("WEIGHT_RATING", "0.25"))
    feature: float = float(os.getenv("WEIGHT_FEATURE", "0.25"))
    popularity: float = float(os.getenv("WEIGHT_POPULARITY", "0.10"))
    availability: float = float(os.getenv("WEIGHT_AVAILABILITY", "0.10"))

    def validate_weights(self) -> bool:
        """Ensure sum of weights is approximately 1.0."""
        total = (
            self.budget
            + self.rating
            + self.feature
            + self.popularity
            + self.availability
        )
        return abs(total - 1.0) < 1e-4


@dataclass(frozen=True)
class AppConfig:
    """Master Application Configuration."""

    paths: PathConfig = field(default_factory=PathConfig)
    ranking: RankingWeights = field(default_factory=RankingWeights)
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock").lower()
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    currency_symbol: str = os.getenv("CURRENCY_SYMBOL", "₹")
    default_top_n: int = int(os.getenv("DEFAULT_TOP_N", "5"))


# Global configuration instance
config = AppConfig()
