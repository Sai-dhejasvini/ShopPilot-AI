"""
ShopPilot AI - Database Layer
Handles SQLite database initialization, indexing, and tabular querying.
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

from backend.config import config
from backend.schema import Product


class Database:
    """SQLite database manager for ShopPilot AI catalog and interaction logs."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.paths.SQLITE_DB_FILE
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns SQLite connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes tables and indexes."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id TEXT PRIMARY KEY,
                    product_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT NOT NULL,
                    brand TEXT NOT NULL,
                    price REAL NOT NULL CHECK (price >= 0),
                    rating REAL NOT NULL CHECK (rating >= 0.0 AND rating <= 5.0),
                    review_count INTEGER NOT NULL CHECK (review_count >= 0),
                    description TEXT,
                    features TEXT NOT NULL,
                    availability INTEGER NOT NULL DEFAULT 1,
                    discount_percentage REAL DEFAULT 0.0,
                    original_price REAL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_price ON products(price)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_rating ON products(rating)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interaction_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    extracted_category TEXT,
                    extracted_budget_max REAL,
                    extracted_features TEXT,
                    recommended_product_ids TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def populate_products(self, df: pd.DataFrame):
        """Populates or replaces the products table with cleaned catalog DataFrame."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products")
            
            for _, row in df.iterrows():
                features_str = row["features"]
                if isinstance(features_str, list):
                    features_str = json.dumps(features_str)

                cursor.execute("""
                    INSERT INTO products (
                        product_id, product_name, category, subcategory, brand,
                        price, rating, review_count, description, features,
                        availability, discount_percentage, original_price
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(row["product_id"]),
                    str(row["product_name"]),
                    str(row["category"]),
                    str(row.get("subcategory", "General")),
                    str(row["brand"]),
                    float(row["price"]),
                    float(row["rating"]),
                    int(row["review_count"]),
                    str(row.get("description", "")),
                    features_str,
                    1 if row["availability"] else 0,
                    float(row.get("discount_percentage", 0.0)),
                    float(row["original_price"]) if pd.notnull(row.get("original_price")) else None
                ))
            conn.commit()
        finally:
            conn.close()

    def get_all_products(self) -> List[Product]:
        """Retrieves all products as Pydantic models."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products ORDER BY rating DESC, review_count DESC")
            rows = cursor.fetchall()
            
            products = []
            for r in rows:
                features = r["features"]
                if isinstance(features, str):
                    try:
                        features = json.loads(features)
                    except Exception:
                        features = [f.strip() for f in features.split(",") if f.strip()]

                products.append(Product(
                    product_id=r["product_id"],
                    product_name=r["product_name"],
                    category=r["category"],
                    subcategory=r["subcategory"],
                    brand=r["brand"],
                    price=r["price"],
                    rating=r["rating"],
                    review_count=r["review_count"],
                    description=r["description"] or "",
                    features=features,
                    availability=bool(r["availability"]),
                    discount_percentage=r["discount_percentage"] or 0.0,
                    original_price=r["original_price"],
                ))
            return products
        finally:
            conn.close()

    def log_interaction(
        self,
        session_id: str,
        user_query: str,
        extracted_category: Optional[str] = None,
        extracted_budget_max: Optional[float] = None,
        extracted_features: Optional[List[str]] = None,
        recommended_product_ids: Optional[List[str]] = None
    ):
        """Logs user query and recommendation interaction for growth analytics."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interaction_logs (
                    session_id, user_query, extracted_category,
                    extracted_budget_max, extracted_features, recommended_product_ids
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                user_query,
                extracted_category,
                extracted_budget_max,
                json.dumps(extracted_features) if extracted_features else None,
                json.dumps(recommended_product_ids) if recommended_product_ids else None,
            ))
            conn.commit()
        finally:
            conn.close()


# Global database instance
db = Database()
