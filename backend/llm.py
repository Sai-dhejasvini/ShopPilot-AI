"""
ShopPilot AI - LLM Integration & Structured Extraction Layer
Provides provider-agnostic LLM extraction (Anthropic, OpenAI, Gemini, Mock)
with strict Pydantic JSON schema enforcement and zero-hallucination grounded synthesis.
"""

import json
import os
import re
from typing import List, Optional, Dict, Any
from backend.config import config
from backend.schema import ExtractedRequirement, RankedProduct, Product


class LLMClient:
    """
    Unified LLM Client supporting Anthropic Claude, OpenAI, Google Gemini,
    and a robust offline/deterministic Mock Mode.
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or config.llm_provider

    def extract_requirements(self, user_query: str) -> ExtractedRequirement:
        """
        Parses unstructured text into a validated ExtractedRequirement schema.
        """
        # If mock mode or API key missing, use deterministic heuristic parser
        if self.provider == "mock" or not self._has_valid_api_key():
            return self._deterministic_extract(user_query)

        try:
            if self.provider == "anthropic":
                return self._extract_anthropic(user_query)
            elif self.provider == "openai":
                return self._extract_openai(user_query)
            elif self.provider == "gemini":
                return self._extract_gemini(user_query)
            else:
                return self._deterministic_extract(user_query)
        except Exception:
            # Safe fallback to deterministic parser on API or parsing error
            return self._deterministic_extract(user_query)

    def synthesize_response(
        self,
        user_query: str,
        ranked_products: List[RankedProduct],
        trade_offs: Optional[str] = None,
    ) -> str:
        """
        Synthesizes a grounded, natural language response based exclusively
        on retrieved products and calculated scores (Strict Zero Hallucination).
        """
        if not ranked_products:
            return (
                "I couldn't find products in our verified catalog matching all your requirements. "
                "Try increasing your budget or relaxing specific feature constraints."
            )

        top = ranked_products[0]
        top_name = top.product.product_name
        top_price = f"{config.currency_symbol}{top.product.price:,.0f}"
        top_rating = f"{top.product.rating}★"

        if len(ranked_products) == 1:
            return (
                f"Based on your requirements, I recommend the **{top_name}** ({top_price}, {top_rating}). "
                f"{top.scores.explanation}"
            )

        summary_lines = [
            f"I found **{len(ranked_products)} matching products** based on your criteria:",
            f"1. **{top_name}** ({top_price}, {top_rating}) — Rank #1: {top.scores.explanation}",
        ]

        for p in ranked_products[1:]:
            summary_lines.append(
                f"- **{p.product.product_name}** ({config.currency_symbol}{p.product.price:,.0f}, {p.product.rating}★) — {p.scores.explanation}"
            )

        if trade_offs:
            summary_lines.append(f"\n**Comparison Trade-offs:**\n{trade_offs}")

        return "\n".join(summary_lines)

    def _has_valid_api_key(self) -> bool:
        if self.provider == "anthropic" and config.anthropic_api_key:
            return True
        if self.provider == "openai" and config.openai_api_key:
            return True
        if self.provider == "gemini" and config.gemini_api_key:
            return True
        return False

    def _deterministic_extract(self, query: str) -> ExtractedRequirement:
        """
        High-precision deterministic rule-based extractor for mock/offline use
        and safe API fallback.
        """
        q_lower = query.lower()

        # 1. Category Detection
        category = None
        if any(w in q_lower for w in ["laptop", "notebook", "macbook", "pc"]):
            category = "Laptop"
        elif any(w in q_lower for w in ["phone", "smartphone", "iphone", "mobile", "galaxy", "pixel"]):
            category = "Smartphone"
        elif any(w in q_lower for w in ["headphone", "earphone", "earbuds", "audio", "airpods", "anc", "sound"]):
            category = "Audio"
        elif any(w in q_lower for w in ["watch", "smartwatch", "wearable", "band", "fitbit"]):
            category = "Wearables"
        elif any(w in q_lower for w in ["monitor", "mouse", "keyboard", "ssd", "accessory", "display"]):
            category = "Accessories"

        # 2. Budget Detection (e.g. 'under 70,000', 'under 70k', '< 50000', 'between 30k and 60k')
        min_price = None
        max_price = None

        # Look for 'under 70k' or 'under 70000' or 'below 70k'
        under_match = re.search(r"(?:under|below|less than|within|<|<=)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(k|lakh|l)?", q_lower)
        if under_match:
            val_str = under_match.group(1).replace(",", "")
            multiplier = under_match.group(2)
            val = float(val_str)
            if multiplier == "k":
                val *= 1000
            elif multiplier in ("lakh", "l"):
                val *= 100000
            max_price = val

        between_match = re.search(r"(?:between|from)\s*(?:₹|rs\.?|inr)?\s*(\d+k?)\s*(?:and|to)\s*(?:₹|rs\.?|inr)?\s*(\d+k?)", q_lower)
        if between_match:
            p1_str = between_match.group(1)
            p2_str = between_match.group(2)
            p1 = float(p1_str.replace("k", "")) * (1000 if "k" in p1_str else 1)
            p2 = float(p2_str.replace("k", "")) * (1000 if "k" in p2_str else 1)
            min_price = min(p1, p2)
            max_price = max(p1, p2)

        # 3. Brand Detection
        known_brands = [
            "Apple", "Samsung", "Lenovo", "ASUS", "HP", "Dell", "Acer", "OnePlus",
            "Google", "Xiaomi", "Realme", "Sony", "Bose", "Sennheiser", "JBL",
            "boAt", "Garmin", "Amazfit", "Noise", "Fitbit", "LG", "Logitech", "Keychron"
        ]
        detected_brands = [b for b in known_brands if re.search(rf"\b{re.escape(b)}\b", query, re.IGNORECASE)]

        # 4. Feature Extraction (e.g. 16GB RAM, OLED, RTX, 512GB, ANC, Battery)
        features = []
        feature_patterns = [
            r"\b(?:\d+GB\s*RAM|\d+GB\s*SSD|\d+TB\s*SSD)\b",
            r"\b(?:RTX\s*\d+|OLED|AMOLED|IPS|Retina|ANC|Active Noise Cancelling|Bluetooth|Wireless|M1|M2|M3|Snapdragon|Tensor)\b",
            r"\b(?:battery life|lightweight|touchscreen|4K|120Hz|144Hz|180Hz|ProMotion)\b"
        ]
        for pat in feature_patterns:
            matches = re.findall(pat, query, re.IGNORECASE)
            for m in matches:
                if m.strip() not in features:
                    features.append(m.strip())

        # 5. Use Case Detection
        use_case = None
        if "programming" in q_lower or "coding" in q_lower or "developer" in q_lower:
            use_case = "Programming"
        elif "gaming" in q_lower or "games" in q_lower:
            use_case = "Gaming"
        elif "student" in q_lower or "college" in q_lower:
            use_case = "College / Student"
        elif "office" in q_lower or "business" in q_lower or "work" in q_lower:
            use_case = "Business / Office"

        # 6. Priority Detection
        priority = None
        if "battery" in q_lower:
            priority = "battery life"
        elif "performance" in q_lower or "speed" in q_lower or "fast" in q_lower:
            priority = "performance"
        elif "display" in q_lower or "screen" in q_lower:
            priority = "display quality"
        elif "camera" in q_lower:
            priority = "camera quality"

        return ExtractedRequirement(
            category=category,
            min_price=min_price,
            max_price=max_price,
            brand_preference=detected_brands,
            required_features=features,
            use_case=use_case,
            priority=priority,
        )

    def _extract_anthropic(self, query: str) -> ExtractedRequirement:
        import anthropic
        client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        prompt = f"""Extract shopping requirements from the user query as JSON conforming to this schema:
        {{
            "category": "Laptop | Smartphone | Audio | Wearables | Accessories | null",
            "min_price": float or null,
            "max_price": float or null,
            "brand_preference": list of strings,
            "required_features": list of strings,
            "min_rating": float or null,
            "priority": string or null,
            "use_case": string or null
        }}
        User Query: "{query}"
        Respond with ONLY the JSON object.
        """
        message = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        content = message.content[0].text
        data = json.loads(content)
        return ExtractedRequirement(**data)

    def _extract_openai(self, query: str) -> ExtractedRequirement:
        from openai import OpenAI
        client = OpenAI(api_key=config.openai_api_key)
        prompt = f"""Extract structured shopping requirements into JSON:
        Query: "{query}"
        """
        response = client.beta.chat.completions.parse(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a shopping assistant requirement extractor."},
                {"role": "user", "content": prompt},
            ],
            response_format=ExtractedRequirement,
        )
        return response.choices[0].message.parsed

    def _extract_gemini(self, query: str) -> ExtractedRequirement:
        from google import genai
        client = genai.Client(api_key=config.gemini_api_key)
        prompt = f"Extract shopping requirement JSON for: {query}"
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            contents=prompt,
            config={"response_mime_type": "application/json", "response_schema": ExtractedRequirement},
        )
        return ExtractedRequirement.model_validate_json(response.text)


# Global LLM client instance
llm_client = LLMClient()
