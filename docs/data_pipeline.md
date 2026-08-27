# Data Pipeline & Cleaning Specification — ShopPilot AI

## 1. Raw Dataset Schema
The raw dataset (`data/raw/ecommerce_products.csv`) contains 57 catalog records with intentional real-world noise:
- Rupee symbols (`₹ 1,09,990`), commas, whitespace
- Out-of-bounds ratings (e.g. `6.2`) and negative prices (`₹ -1500`)
- Duplicate product records and duplicate IDs
- Varied availability representations (`"In Stock"`, `"True"`, `"Out of Stock"`)

## 2. Preprocessing & Sanitization Pipeline
The pipeline in `backend/preprocessing.py` performs:
1. **Price Normalization:** Strips currency symbols and commas, validates non-negative floats.
2. **Rating Enforcement:** Clamps ratings to $0.0 \le \text{rating} \le 5.0$; drops corrupt ratings.
3. **Feature Tokenization:** Normalizes features into structured Python lists and JSON arrays.
4. **Deduplication:** Removes duplicate rows and resolves duplicate `product_id`s.
5. **Database Sync:** Populates indexed SQLite table `products`.

## 3. Pipeline Audit Report
- Initial Raw Rows: **57**
- Exact Duplicates Removed: **1**
- Invalid Records Dropped: **2**
- Final Usable Rows: **54**
- Category Coverage: **Laptops, Smartphones, Audio, Wearables, Accessories**
