import random
from faker import Faker
import os

fake = Faker()

# Static Information
STATIC_POLICY = """
Return Policy: 7-day no-questions-asked. Refund in 5-7 business days.
Support: Mon-Sat, 9AM-6PM IST | support@techgear.com
"""

# Feature pools for generation
ADJECTIVES = ["Pro", "Ultra", "Max", "Lite", "Elite", "Prime", "X", "V2", "Plus", "Air"]
CATEGORIES = ["SmartWatch", "Wireless Earbuds", "Power Bank", "Bluetooth Speaker", "Fitness Tracker"]
FEATURES_POOL = [
    "Heart rate monitor", "GPS", "Water resistant 50m", "ANC", "24-hour battery", 
    "Fast charging 22.5W", "USB-C", "Bluetooth 5.3", "AMOLED Display", "Sleep Tracking",
    "SpO2 sensor", "Wireless charging", "Spatial Audio", "IP68 Rating", "Dual drivers"
]

def generate_product_name():
    category = random.choice(CATEGORIES)
    adj = random.choice(ADJECTIVES)
    suffix = random.choice(ADJECTIVES) if random.random() > 0.5 else ""
    return f"{adj} {category} {suffix}".strip()

def generate_price():
    return f"₹{random.randint(1500, 25000):,}"

def generate_features():
    num_features = random.randint(2, 4)
    features = random.sample(FEATURES_POOL, num_features)
    return ", ".join(features)

def generate_warranty():
    if random.random() > 0.7:
        return "2 years extended (₹1,999)"
    return "1 year standard"

def generate_synthetic_data(num_products=300):
    lines = []
    
    # 1. Add Static Policy at the top
    lines.append(STATIC_POLICY.strip())
    lines.append("-" * 20)
    
    # 2. Generate Products
    for _ in range(num_products):
        name = generate_product_name()
        price = generate_price()
        features = generate_features()
        warranty = generate_warranty()
        
        # Schema: Product: ... | Price: ... | Features: ... | Warranty: ...
        line = f"Product: {name}\nPrice: {price} | Features: {features}\nWarranty: {warranty}"
        lines.append(line)
        
    return lines

if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    print(f"Generating 300 synthetic products...")
    product_rows = generate_synthetic_data(300)
    
    full_content = "\n\n".join(product_rows)
    
    output_path = "data/knowledge_base.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_content)
        
    print(f"Successfully generated {len(product_rows)} items (including policy) and saved to {output_path}")
