"""
ShopPilot AI - Raw Dataset Generator
Generates a realistic Indian e-commerce catalog dataset with genuine technical specs,
realistic prices in INR, and intentional real-world data noise for cleaning in Phase 3.
"""

import csv
import os
from pathlib import Path

raw_dir = Path("C:/Users/s sai vaishnavi/.gemini/antigravity/scratch/ShopPilot-AI/data/raw")
raw_dir.mkdir(parents=True, exist_ok=True)
csv_path = raw_dir / "ecommerce_products.csv"

# Comprehensive product dataset
products = [
    # Laptops
    ("LAP001", "Apple MacBook Air M2 (16GB, 512GB SSD, Midnight)", "Laptop", "Ultrabook", "Apple", "₹ 1,09,990", "4.8", "2450", "Apple M2 8-core CPU, 10-core GPU, 13.6-inch Liquid Retina Display, 18hr battery life", "16GB RAM, 512GB SSD, M2 Chip, 13.6-inch Retina, 18hr battery, Backlit Keyboard", "In Stock"),
    ("LAP002", "Apple MacBook Pro M3 (18GB, 512GB SSD, Space Black)", "Laptop", "Workstation", "Apple", "1,69,900.00", "4.9", "890", "Apple M3 Pro chip, 14.2-inch Liquid Retina XDR, ProMotion 120Hz, 22hr battery", "18GB RAM, 512GB SSD, M3 Pro, 14.2-inch XDR, 120Hz ProMotion, 22hr battery", "In Stock"),
    ("LAP003", "ASUS ROG Zephyrus G14 (AMD Ryzen 9, RTX 4060, 16GB, 1TB)", "Laptop", "Gaming", "ASUS", "₹1,44,990", "4.7", "630", "AMD Ryzen 9 8945HS, NVIDIA RTX 4060 8GB, 14-inch 3K OLED 120Hz, 73Wh battery", "16GB RAM, 1TB SSD, RTX 4060, Ryzen 9, 3K OLED 120Hz, 10hr battery", "True"),
    ("LAP004", "Lenovo ThinkPad E14 Gen 5 (Intel Core i5-1335U, 16GB, 512GB)", "Laptop", "Business", "Lenovo", "62,990", "4.4", "1120", "Intel Core i5 13th Gen, 14-inch FHD IPS Antiglare, Aluminum chassis, Fingerprint reader", "16GB RAM, 512GB SSD, Core i5 13th Gen, FHD IPS, Backlit Keyboard, 12hr battery", "In Stock"),
    ("LAP005", "HP Pavilion Plus 14 (Intel Core i7-13700H, 16GB, 1TB SSD)", "Laptop", "Thin & Light", "HP", "₹ 79,990", "4.5", "740", "Intel Core i7 13th Gen, 14-inch 2.8K OLED Display, Eyesafe certified, Fast Charging", "16GB RAM, 1TB SSD, Core i7 13th Gen, 2.8K OLED, Intel Iris Xe, 9hr battery", "In Stock"),
    ("LAP006", "Acer Nitro V Gaming (Intel Core i5-13420H, RTX 4050, 16GB, 512GB)", "Laptop", "Gaming", "Acer", "68,990", "4.3", "1890", "Intel Core i5 13th Gen, NVIDIA RTX 4050 6GB, 15.6-inch 144Hz FHD, Dual-fan cooling", "16GB RAM, 512GB SSD, RTX 4050, Core i5, 144Hz FHD, RGB Keyboard", "In Stock"),
    ("LAP007", "Dell Inspiron 15 3530 (Intel Core i5-1335U, 16GB, 512GB SSD)", "Laptop", "Everyday", "Dell", "₹53,490 ", "4.2", "980", "Intel Core i5 13th Gen, 15.6-inch FHD 120Hz WVA display, ExpressCharge", "16GB RAM, 512GB SSD, Core i5 13th Gen, 120Hz Display, 7hr battery", "In Stock"),
    ("LAP008", "Lenovo IdeaPad Gaming 3 (AMD Ryzen 5 5600H, RTX 3050, 16GB, 512GB)", "Laptop", "Gaming", "Lenovo", "₹ 54,990", "4.3", "3200", "AMD Ryzen 5 5600H, NVIDIA RTX 3050 4GB, 15.6-inch 120Hz IPS, Rapid Charge", "16GB RAM, 512GB SSD, RTX 3050, Ryzen 5, 120Hz IPS, Blue Backlit", "In Stock"),
    ("LAP009", "ASUS Vivobook 15 (Intel Core i3-1215U, 8GB, 512GB SSD, Quiet Blue)", "Laptop", "Budget", "ASUS", "34,990", "4.1", "4100", "Intel Core i3 12th Gen, 15.6-inch FHD Anti-glare, Privacy shutter camera, 42Wh battery", "8GB RAM, 512GB SSD, Core i3 12th Gen, FHD Display, 6hr battery", "In Stock"),
    ("LAP010", "Dell XPS 13 Plus 9320 (Intel Core i7-1360P, 32GB, 1TB SSD)", "Laptop", "Premium", "Dell", "₹ 1,89,990", "4.6", "310", "Intel Core i7 13th Gen, 13.4-inch 3.5K OLED Touch, Capacitive Touch Bar, Zero-lattice keyboard", "32GB RAM, 1TB SSD, Core i7, 3.5K OLED Touch, 14hr battery, CNC Aluminum", "In Stock"),
    ("LAP011", "Samsung Galaxy Book4 Pro (Intel Core Ultra 7, 16GB, 512GB SSD)", "Laptop", "Ultrabook", "Samsung", "₹ 1,29,990", "4.7", "420", "Intel Core Ultra 7 155H with Intel AI Boost, 14-inch 3K Dynamic AMOLED 2X 120Hz", "16GB RAM, 512GB SSD, Intel Core Ultra 7, AMOLED 2X, AI Boost, 18hr battery", "In Stock"),
    ("LAP012", "HP Victus Gaming 16 (AMD Ryzen 7 7840HS, RTX 4060, 16GB, 1TB)", "Laptop", "Gaming", "HP", "89,990", "4.4", "1540", "AMD Ryzen 7 7840HS, NVIDIA RTX 4060 8GB, 16.1-inch 144Hz FHD IPS, OMEN Gaming Hub", "16GB RAM, 1TB SSD, RTX 4060, Ryzen 7, 144Hz IPS, 8hr battery", "In Stock"),
    ("LAP013", "Apple MacBook Air M1 (8GB, 256GB SSD, Space Grey)", "Laptop", "Budget Ultrabook", "Apple", "₹ 69,900", "4.7", "18400", "Apple M1 chip with 8-core CPU, 13.3-inch Retina Display, Fanless silent design", "8GB RAM, 256GB SSD, M1 Chip, Retina Display, 18hr battery, Fanless", "In Stock"),
    ("LAP014", "ASUS TUF Gaming A15 (AMD Ryzen 7 7735HS, RTX 4050, 16GB, 512GB)", "Laptop", "Gaming", "ASUS", "73,990", "4.4", "2250", "AMD Ryzen 7 7735HS, NVIDIA RTX 4050 6GB, 15.6-inch 144Hz FHD, Military-grade durability", "16GB RAM, 512GB SSD, RTX 4050, Ryzen 7, 144Hz FHD, 90Wh battery", "In Stock"),
    ("LAP015", "Xiaomi Notebook Pro 120G (Intel Core i5-12450H, 16GB, 512GB SSD)", "Laptop", "Productivity", "Xiaomi", "₹ 58,999", "4.2", "880", "Intel Core i5 12th Gen, NVIDIA MX550 2GB, 14-inch 2.5K 120Hz Display, CNC Machined", "16GB RAM, 512GB SSD, Core i5, NVIDIA MX550, 2.5K 120Hz, 8hr battery", "In Stock"),

    # Smartphones
    ("PHN001", "Apple iPhone 15 (128GB, Black)", "Smartphone", "Flagship", "Apple", "₹ 71,999", "4.7", "8450", "Dynamic Island, 48MP Main camera with 2x Telephoto, A16 Bionic chip, USB-C", "128GB Storage, 6GB RAM, A16 Bionic, 48MP Camera, Dynamic Island, USB-C, OLED", "In Stock"),
    ("PHN002", "Apple iPhone 15 Pro Max (256GB, Natural Titanium)", "Smartphone", "Flagship", "Apple", "1,49,900", "4.8", "3200", "A17 Pro chip, Titanium design, Action button, 48MP camera with 5x optical zoom, 120Hz ProMotion", "256GB Storage, 8GB RAM, A17 Pro, 5x Telephoto, 120Hz OLED, Titanium", "In Stock"),
    ("PHN003", "Samsung Galaxy S24 Ultra (512GB, Titanium Gray)", "Smartphone", "Flagship", "Samsung", "₹ 1,39,999", "4.8", "2900", "Galaxy AI, 200MP Quad Camera, Snapdragon 8 Gen 3, S-Pen included, 6.8-inch QHD+ 120Hz", "512GB Storage, 12GB RAM, Snapdragon 8 Gen 3, 200MP Camera, S-Pen, 5000mAh", "In Stock"),
    ("PHN004", "Samsung Galaxy S23 FE (128GB, Mint)", "Smartphone", "Premium Mid-range", "Samsung", "39,999", "4.3", "5600", "50MP Triple Camera with OIS, Exynos 2200, 6.4-inch Dynamic AMOLED 2X 120Hz, IP68", "128GB Storage, 8GB RAM, AMOLED 120Hz, 50MP OIS, IP68, Wireless Charging", "In Stock"),
    ("PHN005", "OnePlus 12 (256GB, Silky Black, 12GB RAM)", "Smartphone", "Flagship", "OnePlus", "₹ 64,999", "4.6", "4100", "Snapdragon 8 Gen 3, 4th Gen Hasselblad Camera, 5400mAh Battery, 100W SUPERVOOC charging", "256GB Storage, 12GB RAM, Snapdragon 8 Gen 3, Hasselblad 50MP, 100W Fast Charge, 5400mAh", "In Stock"),
    ("PHN006", "OnePlus Nord CE 4 (128GB, Celadon Marble, 8GB RAM)", "Smartphone", "Mid-range", "OnePlus", "₹24,999", "4.4", "9400", "Snapdragon 7 Gen 3, 100W SuperVOOC, 5500mAh battery, 50MP Sony LYT-600 with OIS", "128GB Storage, 8GB RAM, Snapdragon 7 Gen 3, 100W Charging, 5500mAh, 120Hz AMOLED", "In Stock"),
    ("PHN007", "Google Pixel 8 (128GB, Hazel)", "Smartphone", "Flagship", "Google", "₹ 62,999", "4.5", "2100", "Google Tensor G3, Best-in-class computational photography, 7 years OS updates, Actua OLED", "128GB Storage, 8GB RAM, Tensor G3, 50MP AI Camera, 7yr Updates, 120Hz OLED", "In Stock"),
    ("PHN008", "Google Pixel 7a (128GB, Charcoal)", "Smartphone", "Mid-range", "Google", "34,999", "4.3", "7300", "Google Tensor G2, 64MP Camera with Night Sight, Wireless Charging, IP67 water resistance", "128GB Storage, 8GB RAM, Tensor G2, 64MP Camera, Wireless Charging, IP67", "In Stock"),
    ("PHN009", "Xiaomi 14 (512GB, Jade Green, 12GB RAM)", "Smartphone", "Flagship", "Xiaomi", "₹ 69,999", "4.6", "1450", "Leica Summilux Optical Lens, Snapdragon 8 Gen 3, Compact 6.36-inch 120Hz LTPO OLED", "512GB Storage, 12GB RAM, Snapdragon 8 Gen 3, Leica 50MP, 90W Fast Charge", "In Stock"),
    ("PHN010", "Redmi Note 13 Pro+ 5G (256GB, Fusion Purple)", "Smartphone", "Mid-range", "Xiaomi", "₹ 29,999", "4.3", "12300", "200MP OIS Camera, Curved 1.5K AMOLED Display, 120W HyperCharge, IP68 water resistance", "256GB Storage, 8GB RAM, 200MP OIS, 120W HyperCharge, IP68, 120Hz Curved AMOLED", "In Stock"),
    ("PHN011", "Realme 12 Pro+ 5G (256GB, Submarine Blue)", "Smartphone", "Mid-range", "Realme", "28,999", "4.4", "6700", "64MP Periscope Portrait Camera, Snapdragon 7s Gen 2, Luxury watch design with vegan leather", "256GB Storage, 8GB RAM, 64MP Periscope Zoom, Snapdragon 7s Gen 2, 67W Charge", "In Stock"),
    ("PHN012", "Motorola Edge 50 Pro (256GB, Luxe Lavender)", "Smartphone", "Premium Mid-range", "Motorola", "₹ 31,999", "4.5", "4800", "Pantone Validated 1.5K 144Hz pOLED, Snapdragon 7 Gen 3, 125W TurboPower + 50W Wireless", "256GB Storage, 12GB RAM, 144Hz pOLED, 125W Fast Charge, 50W Wireless, IP68", "In Stock"),
    ("PHN013", "Nothing Phone (2) (128GB, Dark Grey, 8GB RAM)", "Smartphone", "Upper Mid-range", "Nothing", "36,999", "4.4", "3900", "Glyph Interface LED lighting, Snapdragon 8+ Gen 1, Nothing OS 2.5, Dual 50MP Sony sensors", "128GB Storage, 8GB RAM, Snapdragon 8+ Gen 1, Glyph Interface, Dual 50MP, 120Hz OLED", "In Stock"),
    ("PHN014", "POCO X6 Pro 5G (256GB, Racing Yellow, 8GB RAM)", "Smartphone", "Performance", "POCO", "₹ 23,999", "4.4", "15800", "MediaTek Dimensity 8300-Ultra, WildBoost Gaming 2.0, 1.5K 120Hz AMOLED, 67W Turbo Charge", "256GB Storage, 8GB RAM, Dimensity 8300 Ultra, 1.5K AMOLED, 67W Fast Charge, 5000mAh", "In Stock"),
    ("PHN015", "Samsung Galaxy A15 5G (128GB, Blue, 6GB RAM)", "Smartphone", "Budget", "Samsung", "16,499", "4.1", "8900", "50MP Triple Camera, 90Hz Super AMOLED Display, 5000mAh Battery, Knox Security", "128GB Storage, 6GB RAM, 90Hz Super AMOLED, 50MP Camera, 5000mAh", "In Stock"),

    # Audio & Headphones
    ("AUD001", "Sony WH-1000XM5 Wireless Noise Cancelling Headphones", "Audio", "Over-Ear Headphones", "Sony", "₹ 28,990", "4.7", "5800", "Industry-leading Active Noise Cancellation with Auto NC Optimizer, 30hr battery, Speak-to-chat", "Active Noise Cancellation, 30hr Battery, LDAC Hi-Res Audio, Multipoint Bluetooth, Fast Charge", "In Stock"),
    ("AUD002", "Bose QuietComfort 45 Bluetooth Wireless Headphones", "Audio", "Over-Ear Headphones", "Bose", "₹ 24,900", "4.6", "3100", "Acoustic Noise Cancelling, Quiet and Aware modes, TriPort acoustic architecture, 24hr battery", "Active Noise Cancellation, 24hr Battery, TriPort Audio, USB-C, Lightweight Comfort", "In Stock"),
    ("AUD003", "Apple AirPods Pro (2nd Generation with USB-C)", "Audio", "TWS Earbuds", "Apple", "23,990.00", "4.8", "12400", "Up to 2x more Active Noise Cancellation, Adaptive Audio, Personalized Spatial Audio, MagSafe USB-C", "Active Noise Cancellation, Spatial Audio, Transparency Mode, 30hr Battery Case, IP54, MagSafe", "In Stock"),
    ("AUD004", "Sony WF-1000XM5 Truly Wireless Earbuds", "Audio", "TWS Earbuds", "Sony", "₹ 21,990", "4.5", "1950", "Dual processor Active Noise Cancellation, Dynamic Driver X, Bone conduction sensors, AI call mic", "Active Noise Cancellation, LDAC Hi-Res, 24hr Battery, Wireless Charging, IPX4", "In Stock"),
    ("AUD005", "Sennheiser Momentum 4 Wireless Headphones", "Audio", "Over-Ear Headphones", "Sennheiser", "₹ 29,990", "4.7", "1420", "Audiophile-inspired 42mm transducer system, Unrivaled 60-hour battery life, Adaptive ANC", "60hr Battery Life, Adaptive Noise Cancellation, 42mm Transducer, AptX Adaptive", "In Stock"),
    ("AUD006", "OnePlus Buds Pro 2 (Obsidian Black)", "Audio", "TWS Earbuds", "OnePlus", "8,999", "4.4", "6300", "MelodyBoost Dual Drivers co-created with Dynaudio, 48dB Smart Adaptive ANC, Spatial Audio", "48dB ANC, Spatial Audio, Dynaudio Tuning, 39hr Battery, LHDC 4.0 Hi-Res", "In Stock"),
    ("AUD007", "JBL Live 660NC Wireless Over-Ear NC Headphones", "Audio", "Over-Ear Headphones", "JBL", "₹ 7,999", "4.3", "4800", "JBL Signature Sound with 40mm drivers, Adaptive Noise Cancelling, Up to 50 hours battery", "Active Noise Cancellation, 50hr Battery, JBL Signature Sound, Ambient Aware", "In Stock"),
    ("AUD008", "boAt Nirvana Ion Truly Wireless Earbuds", "Audio", "TWS Earbuds", "boAt", "1,999", "4.2", "28500", "Massive 120 hours total playback, Dual EQ modes (HiFi & Bass), Quad mics with ENx technology", "120hr Playback, Dual EQ Modes, Quad Mics ENC, Low Latency Beast Mode, IPX4", "In Stock"),
    ("AUD009", "Realme Buds Air 5 Pro (Sunrise City)", "Audio", "TWS Earbuds", "Realme", "₹ 4,499", "4.5", "9200", "50dB Active Noise Cancellation, 11mm Bass + 6mm Micro-planar tweeters, 40hr Battery, LDAC", "50dB Active Noise Cancellation, Dual Drivers, LDAC Hi-Res, 40hr Battery, 40ms Latency", "In Stock"),
    ("AUD010", "Marshall Major IV Wireless Bluetooth On-Ear Headphones", "Audio", "On-Ear Headphones", "Marshall", "₹ 11,999", "4.6", "2300", "Iconic Marshall custom-tuned dynamic drivers, 80+ solid hours of wireless playtime, Wireless charging", "80+ Hours Battery, Wireless Charging, Custom Tuned Audio, Foldable Classic Design", "In Stock"),

    # Wearables & Smartwatches
    ("WAT001", "Apple Watch Series 9 GPS (45mm, Midnight Aluminum)", "Wearables", "Smartwatch", "Apple", "₹ 44,900", "4.8", "4100", "S9 SiP chip, Double tap gesture, Brighter 2000-nit display, ECG app, Blood oxygen sensor", "S9 Chip, Double Tap Gesture, ECG, Blood Oxygen, 2000-nit OLED, 18hr Battery, Crash Detection", "In Stock"),
    ("WAT002", "Apple Watch SE (2nd Gen, GPS 44mm, Starlight)", "Wearables", "Smartwatch", "Apple", "₹ 27,900", "4.6", "6800", "Heart rate tracking, Crash Detection, Sleep Stages, Water resistant 50m, Retina Display", "Heart Rate Monitor, Crash Detection, Sleep Tracking, 50m Water Resistance, Retina OLED", "In Stock"),
    ("WAT003", "Samsung Galaxy Watch6 Bluetooth (44mm, Graphite)", "Wearables", "Smartwatch", "Samsung", "21,999", "4.5", "3400", "Advanced sleep coaching, Body composition analysis (BIA), Sapphire Crystal glass, Wear OS powered", "Sleep Coaching, BIA Body Analysis, Sapphire Glass, WearOS Apps, ECG, 5ATM Water Resistant", "In Stock"),
    ("WAT004", "Garmin Forerunner 265 Running Smartwatch", "Wearables", "Fitness Watch", "Garmin", "₹ 48,990", "4.8", "720", "Vibrant AMOLED touchscreen, Training readiness score, Morning report, Multi-band GPS, 13-day battery", "13-day Battery, Multi-band GPS, AMOLED Touchscreen, Training Readiness, VO2 Max, Heart Rate", "In Stock"),
    ("WAT005", "Amazfit GTR 4 Smartwatch (SuperSpeed Black)", "Wearables", "Smartwatch", "Amazfit", "₹ 16,999", "4.4", "4500", "Dual-band circularly-polarized GPS, 150+ Sports modes, 14-day battery life, Bluetooth phone calls", "14-day Battery, Dual-band GPS, 1.43-inch AMOLED, Bluetooth Calling, 150+ Sports Modes", "In Stock"),
    ("WAT006", "OnePlus Watch 2 (Radiant Steel, 46mm)", "Wearables", "Smartwatch", "OnePlus", "22,999", "4.6", "1800", "Dual-Engine Architecture with Snapdragon W5 + BES2700, Up to 100 hours battery life in Smart Mode", "100hr Battery in Smart Mode, WearOS 4, Snapdragon W5, Sapphire Crystal, Dual-frequency GPS", "In Stock"),
    ("WAT007", "Noise ColorFit Pro 5 Max Smart Watch (Jet Black)", "Wearables", "Smartwatch", "Noise", "₹ 4,499", "4.2", "16400", "1.96-inch AMOLED display, Post-training metrics (VO2 max, recovery time), Rapid SOS, BT calling", "1.96-inch AMOLED, Bluetooth Calling, VO2 Max, 7-day Battery, IP68 Water Resistant", "In Stock"),
    ("WAT008", "Fitbit Charge 6 Fitness Tracker (Obsidian / Black)", "Wearables", "Fitness Tracker", "Fitbit", "₹ 14,999", "4.3", "1900", "Built-in GPS, YouTube Music controls, Google Maps navigation, ECG app, 7-day battery life", "Built-in GPS, ECG App, Google Maps on wrist, 7-day Battery, Stress Management SpO2", "In Stock"),

    # PC Accessories & Monitors
    ("ACC001", "LG UltraGear 27-inch QHD Nano IPS Gaming Monitor (27GP850)", "Accessories", "Monitor", "LG", "₹ 29,999", "4.6", "3800", "27-inch 2560x1440 Nano IPS, 165Hz (OC 180Hz), 1ms GtG response time, NVIDIA G-Sync Compatible", "27-inch QHD 2K, Nano IPS, 180Hz Refresh Rate, 1ms GtG, HDR400, G-Sync Compatible", "In Stock"),
    ("ACC002", "Dell UltraSharp 27 4K USB-C Hub Monitor (U2723QE)", "Accessories", "Monitor", "Dell", "₹ 54,990", "4.8", "1250", "27-inch 4K UHD IPS Black technology, 2000:1 contrast ratio, 90W USB-C Power Delivery hub, RJ45", "27-inch 4K UHD, IPS Black, 90W USB-C Hub, 98% DCI-P3, Height Adjustable Stand", "In Stock"),
    ("ACC003", "Logitech MX Master 3S Wireless Performance Mouse", "Accessories", "Mouse", "Logitech", "8,995", "4.8", "14800", "Quiet clicks, 8000 DPI track-on-glass sensor, MagSpeed electromagnetic scrolling, USB-C recharge", "8000 DPI Sensor, Quiet Clicks, MagSpeed Wheel, 70-day Battery, Multi-Device Flow Bluetooth", "In Stock"),
    ("ACC004", "Keychron K2 V2 Wireless Mechanical Keyboard (Brown Switch)", "Accessories", "Keyboard", "Keychron", "₹ 7,499", "4.7", "3900", "75% compact layout, Gateron G Pro Mechanical switches, Mac & Windows layout, RGB backlit, Bluetooth 5.1", "75% Layout, Mechanical Brown Switches, RGB Backlit, Mac & Windows compatible, 4000mAh Battery", "In Stock"),
    ("ACC005", "Logitech MX Mechanical Wireless Illuminated Keyboard", "Accessories", "Keyboard", "Logitech", "₹ 15,995", "4.7", "2100", "Low-profile tactile mechanical switches, Smart illumination backlighting, Multi-OS connectivity", "Tactile Quiet Switches, Smart Backlit, Multi-Device Bluetooth, USB-C Fast Charge", "In Stock"),
    ("ACC006", "SanDisk Extreme 1TB Portable External SSD (Up to 1050MB/s)", "Accessories", "Storage", "SanDisk", "₹ 9,999", "4.6", "11200", "NVMe solid state performance with 1050MB/s read and 1000MB/s write speeds, IP65 water/dust resistance", "1TB NVMe SSD, 1050MB/s Speed, IP65 Water & Dust Resistant, 2m Drop Protection, USB-C", "In Stock"),

    # INTENTIONAL NOISY / DIRTY ROWS (for Phase 3 cleaning demonstration)
    ("LAP004", "Lenovo ThinkPad E14 Gen 5 (Intel Core i5-1335U, 16GB, 512GB)", "Laptop", "Business", "Lenovo", "62,990", "4.4", "1120", "Intel Core i5 13th Gen, 14-inch FHD IPS Antiglare, Aluminum chassis, Fingerprint reader", "16GB RAM, 512GB SSD, Core i5 13th Gen, FHD IPS, Backlit Keyboard, 12hr battery", "In Stock"), # DUPLICATE ROW
    ("PHN999", "  Generic Unbranded Dummy Phone 5G  ", "Smartphone", "Budget", "  Generic  ", "₹ -1500", "6.2", "-5", "", "", "Out of Stock"), # INVALID PRICE (<0), INVALID RATING (>5), NEGATIVE REVIEWS, EMPTY DESC
    ("AUD999", "Broken Sample Earphones", "Audio", "TWS", "Unknown", "N/A", "None", "0", "A broken item with missing price and rating", "None", "False"), # NULL / NON-NUMERIC PRICE & RATING
]

headers = [
    "product_id", "product_name", "category", "subcategory", "brand",
    "price", "rating", "review_count", "description", "features", "availability"
]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(products)

print(f"Generated raw dataset with {len(products)} records at {csv_path}")
