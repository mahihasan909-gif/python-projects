# How to Run This Project

## Step 1: Navigate to Project
```powershell
cd "d:\Coding\Python-Projects\Task1-Algorithmic-Trading"
```

## Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

## Step 3: Run the Project
```powershell
python demo.py
```

## ✅ Expected Output
```
=== ALGORITHMIC TRADING RESULTS ===
Stock: AAPL
Golden Cross detected: BUY at $165.50
Death Cross detected: SELL at $180.75
Final Portfolio: $5,456.78 (+9.14%)
```
```

## � Alternative Commands
- `python trading_bot.py` - Run custom analysis
- Test different stocks by editing demo.py

---

# Task 2: Samsung Phone Advisor 📱

AI-powered Samsung phone recommendation system with RAG and Multi-Agent capabilities.

## 🚀 How to Run

### Step 1: Open Terminal
```powershell
cd "d:\Coding\Python-Projects\Task2-Samsung-Phone-Advisor"
```

### Step 2: Start the API Server
```powershell
python api.py
```

### Step 3: Open Web Interface
Open browser and go to:
```
http://127.0.0.1:8000/docs
```

### Step 4: Test the API
1. Click **POST /ask**
2. Click **"Try it out"**
3. Enter JSON query:
```json
{
  "question": "Compare Galaxy S23 Ultra and S22 Ultra",
  "use_rag": false,
  "use_multi_agent": false
}
```
4. Click **"Execute"**

## ✅ Expected Output
```json
{
  "answer": "📱 Detailed comparison with camera specs, display, battery, pricing...",
  "confidence": 0.7,
  "phones_found": 2,
  "success": true
}
```