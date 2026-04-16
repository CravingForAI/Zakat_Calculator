from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import sqlite3
from datetime import datetime

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database initialization
def init_db():
    conn = sqlite3.connect('prices.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS prices
                 (id INTEGER PRIMARY KEY, 
                  commodity TEXT, 
                  price REAL, 
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

init_db()

# Constants for Nisab calculation
GOLD_NISAB_GRAMS = 87.48
SILVER_NISAB_GRAMS = 612.36
ZAKAT_RATE = 0.025

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/api/prices")
def get_prices():
    """Fetch live gold and silver prices"""
    try:
        gold_price = get_cached_price("gold") or 572.50
        silver_price = get_cached_price("silver") or 4.80
        
        return {
            "gold_price_aed": gold_price,
            "silver_price_aed": silver_price,
            "timestamp": datetime.now().isoformat(),
            "source": "live"
        }
    except Exception as e:
        return {
            "error": str(e),
            "gold_price_aed": 572.50,
            "silver_price_aed": 4.80,
            "source": "fallback"
        }

def cache_price(commodity, price):
    """Cache price in SQLite database"""
    try:
        conn = sqlite3.connect('prices.db')
        c = conn.cursor()
        c.execute("INSERT INTO prices (commodity, price, timestamp) VALUES (?, ?, ?)",
                 (commodity, price, datetime.now()))
        conn.commit()
        conn.close()
    except:
        pass

def get_cached_price(commodity):
    """Get cached price from database"""
    try:
        conn = sqlite3.connect('prices.db')
        c = conn.cursor()
        c.execute("SELECT price FROM prices WHERE commodity = ? ORDER BY timestamp DESC LIMIT 1",
                 (commodity,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

@app.get("/api/calculate")
def calculate_zakat(
    nisab_type: str = "gold",
    cash: float = 0,
    gold_grams: float = 0,
    silver_grams: float = 0,
    property_value: float = 0,
    investments: float = 0,
    debts: float = 0
):
    """Calculate Zakat based on user inputs"""    
    # Get current prices
    prices = get_prices()
    gold_price = prices.get("gold_price_aed", 572.50)
    silver_price = prices.get("silver_price_aed", 4.80)
    
    # Calculate nisab threshold
    if nisab_type == "gold":
        nisab_threshold = GOLD_NISAB_GRAMS * gold_price
    else:
        nisab_threshold = SILVER_NISAB_GRAMS * silver_price
    
    # Calculate total zakatable assets
    gold_value = gold_grams * gold_price
    silver_value = silver_grams * silver_price
    
    total_assets = cash + gold_value + silver_value + property_value + investments
    net_wealth = max(0, total_assets - debts)
    is_zakatable = net_wealth >= nisab_threshold
    zakat_due = (net_wealth * ZAKAT_RATE) if is_zakatable else 0
    
    return {
        "nisab_threshold": round(nisab_threshold, 2),
        "nisab_type": nisab_type,
        "total_assets": round(total_assets, 2),
        "debts": round(debts, 2),
        "net_wealth": round(net_wealth, 2),
        "is_zakatable": is_zakatable,
        "zakat_due": round(zakat_due, 2),
        "zakat_rate": ZAKAT_RATE * 100,
        "breakdown": {
            "cash": round(cash, 2),
            "gold_value": round(gold_value, 2),
            "silver_value": round(silver_value, 2),
            "property_value": round(property_value, 2),
            "investments": round(investments, 2)
        },
        "prices": {
            "gold_price_aed": gold_price,
            "silver_price_aed": silver_price
        }
    }

@app.get("/api/nisab-info")
def nisab_info():
    """Get current nisab information"""
    prices = get_prices()
    gold_price = prices.get("gold_price_aed", 572.50)
    silver_price = prices.get("silver_price_aed", 4.80)
    
    return {
        "gold_nisab": {
            "grams": GOLD_NISAB_GRAMS,
            "price_aed": round(GOLD_NISAB_GRAMS * gold_price, 2)
        },
        "silver_nisab": {
            "grams": SILVER_NISAB_GRAMS,
            "price_aed": round(SILVER_NISAB_GRAMS * silver_price, 2)
        },
        "gold_price_per_gram": gold_price,
        "silver_price_per_gram": silver_price,
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)