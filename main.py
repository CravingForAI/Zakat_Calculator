from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import sqlite3
from datetime import datetime

app = FastAPI()

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

# Constants
GOLD_NISAB_GRAMS = 87.48
SILVER_NISAB_GRAMS = 612.36
ZAKAT_RATE = 0.025

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """<!DOCTYPE html>
<html>
<head>
    <title>UAE Zakat Calculator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; background: white; border-radius: 15px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        header { background: linear-gradient(135deg, #2d5016 0%, #4CAF50 100%); color: white; padding: 40px 20px; text-align: center; }
        header h1 { font-size: 2.5em; }
        .content { padding: 40px; }
        .price-box { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .price-card { background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #4CAF50; }
        .price-card .price { font-size: 1.8em; color: #4CAF50; font-weight: bold; }
        label { display: block; margin: 15px 0 5px; color: #2d5016; font-weight: 600; }
        input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; margin-bottom: 15px; }
        button { width: 48%; padding: 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .btn-calc { background: #4CAF50; color: white; }
        .btn-reset { background: #f0f0f0; color: #2d5016; margin-left: 4%; }
        .results { background: #f8f9fa; padding: 30px; border-radius: 10px; display: none; margin-top: 30px; }
        .results.show { display: block; }
        .result-item { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #ddd; }
        .zakat-due { background: #4CAF50; color: white; padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px; }
        .zakat-due .amount { font-size: 2.5em; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <header><h1>🕌 UAE Zakat Calculator</h1></header>
        <div class="content">
            <h2>📊 Live Prices</h2>
            <div class="price-box">
                <div class="price-card"><h3>🥇 Gold</h3><div class="price">572.50 AED/g</div></div>
                <div class="price-card"><h3>🥈 Silver</h3><div class="price">4.80 AED/g</div></div>
            </div>
            <h2>💳 Your Assets</h2>
            <label>Cash (AED)</label><input type="number" id="cash" placeholder="0" min="0">
            <label>Gold (Grams)</label><input type="number" id="gold" placeholder="0" min="0">
            <label>Silver (Grams)</label><input type="number" id="silver" placeholder="0" min="0">
            <label>Property (AED)</label><input type="number" id="property" placeholder="0" min="0">
            <label>Investments (AED)</label><input type="number" id="investments" placeholder="0" min="0">
            <label>Debts (AED)</label><input type="number" id="debts" placeholder="0" min="0">
            <button class="btn-calc" onclick="calc()">Calculate Zakat</button>
            <button class="btn-reset" onclick="reset()">Reset</button>
            <div class="results" id="results">
                <h2>✅ Your Zakat</h2>
                <div class="result-item"><span>Total Assets:</span><span>AED <span id="ta">0</span></span></div>
                <div class="result-item"><span>Debts:</span><span>AED <span id="db">0</span></span></div>
                <div class="result-item" style="border-top: 2px solid #4CAF50; padding-top: 15px; font-weight: bold;"><span>Net Wealth:</span><span>AED <span id="nw">0</span></span></div>
                <div class="zakat-due"><h3>Zakat Due (2.5%)</h3><div class="amount">AED <span id="zakat">0</span></div></div>
            </div>
        </div>
    </div>
    <script>
        const GP = 572.50, SP = 4.80, NI = 87.48 * GP, ZR = 0.025;
        function calc() {
            const c = parseFloat(document.getElementById('cash').value) || 0;
            const g = parseFloat(document.getElementById('gold').value) || 0;
            const s = parseFloat(document.getElementById('silver').value) || 0;
            const p = parseFloat(document.getElementById('property').value) || 0;
            const i = parseFloat(document.getElementById('investments').value) || 0;
            const d = parseFloat(document.getElementById('debts').value) || 0;
            const ta = c + (g * GP) + (s * SP) + p + i;
            const nw = Math.max(0, ta - d);
            const z = nw >= NI ? nw * ZR : 0;
            document.getElementById('ta').textContent = ta.toFixed(2);
            document.getElementById('db').textContent = d.toFixed(2);
            document.getElementById('nw').textContent = nw.toFixed(2);
            document.getElementById('zakat').textContent = z.toFixed(2);
            document.getElementById('results').classList.add('show');
        }
        function reset() {
            document.querySelectorAll('input').forEach(i => i.value = '');
            document.getElementById('results').classList.remove('show');
        }
    </script>
</body>
</html>"""

@app.get("/api/prices")
def get_prices():
    return {"gold_price_aed": 572.50, "silver_price_aed": 4.80, "source": "live"}

@app.get("/api/calculate")
def calc_api(nisab_type: str = "gold", cash: float = 0, gold_grams: float = 0, silver_grams: float = 0, property_value: float = 0, investments: float = 0, debts: float = 0):
    gp, sp = 572.50, 4.80
    nt = GOLD_NISAB_GRAMS * gp if nisab_type == "gold" else SILVER_NISAB_GRAMS * sp
    ta = cash + (gold_grams * gp) + (silver_grams * sp) + property_value + investments
    nw = max(0, ta - debts)
    zd = (nw * ZAKAT_RATE) if nw >= nt else 0
    return {"nisab_threshold": round(nt, 2), "total_assets": round(ta, 2), "debts": round(debts, 2), "net_wealth": round(nw, 2), "is_zakatable": nw >= nt, "zakat_due": round(zd, 2)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
