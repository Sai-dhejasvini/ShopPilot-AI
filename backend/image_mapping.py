"""
ShopPilot AI - Product Image Mapping
Provides a mapping mechanism to attach safe, local professional images
to products based on brand, category, and model.
"""

from typing import Optional

def get_image_url_for_product(product_id: str, brand: str, category: str, subcategory: str, product_name: str) -> str:
    """Returns the local asset path for a given product."""
    b = brand.lower()
    c = category.lower()
    n = product_name.lower()
    
    # 1. Laptops
    if c == "laptop":
        if "apple" in b or "macbook" in n:
            return "/static/assets/images/macbook.jpg"
        if "asus" in b:
            return "/static/assets/images/asus_rog.jpg"
        if "lenovo" in b:
            return "/static/assets/images/lenovo_laptop.jpg"
        if "hp" in b:
            return "/static/assets/images/hp_laptop.jpg"
        if "dell" in b or "acer" in b or "xiaomi" in b or "samsung" in b:
            return "/static/assets/images/dell_laptop.jpg"
        return "/static/assets/images/laptop_fallback.jpg"
        
    # 2. Smartphones
    if c == "smartphone":
        if "apple" in b or "iphone" in n:
            return "/static/assets/images/iphone.jpg"
        if "google" in b or "pixel" in n:
            return "/static/assets/images/pixel.jpg"
        if "samsung" in b:
            return "/static/assets/images/galaxy_s.jpg"
        return "/static/assets/images/smartphone_fallback.jpg"
        
    # 3. Audio
    if c == "audio":
        if "over-ear" in subcategory.lower() or "on-ear" in subcategory.lower():
            return "/static/assets/images/overear_headphones.jpg"
        if "earbud" in subcategory.lower() or "in-ear" in subcategory.lower() or "tws" in subcategory.lower() or "airpods" in n:
            return "/static/assets/images/tws_earbuds.jpg"
        return "/static/assets/images/audio_fallback.jpg"
        
    # 4. Wearables
    if c == "wearables":
        if "apple" in b:
            return "/static/assets/images/apple_watch.jpg"
        if "samsung" in b or "garmin" in b or "amazfit" in b or "oneplus" in b or "noise" in b or "fitbit" in b:
            return "/static/assets/images/round_smartwatch.jpg"
        return "/static/assets/images/wearable_fallback.jpg"
        
    # 5. Accessories
    if c == "accessories":
        if "monitor" in subcategory.lower():
            return "/static/assets/images/monitor.jpg"
        if "keyboard" in n.lower():
            return "/static/assets/images/keyboard.jpg"
        if "mouse" in n.lower():
            return "/static/assets/images/mouse.jpg"
        if "ssd" in n.lower() or "drive" in n.lower():
            return "/static/assets/images/ssd.jpg"
        return "/static/assets/images/accessories_fallback.jpg"
        
    # Ultimate Fallback
    return "/static/assets/images/accessories_fallback.jpg"
