# How to Run Both Projects

## Task 1: Algorithmic Trading Bot

### Task 1 - Step 1: Navigate to Project
```powershell
cd "d:\Coding\Python-Projects\Task1-Algorithmic-Trading"
```

### Task 1 - Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Task 1 - Step 3: Run the Project
```powershell
python demo.py
```

---

## Task 2: Samsung Phone Advisor

### Task 2 - Step 1: Navigate to Project
```powershell
cd "d:\Coding\Python-Projects\Task2-Samsung-Phone-Advisor"
```

### Task 2 - Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Task 2 - Step 3: Start the API Server
```powershell
python api.py
```

### Task 2 - Step 4: Open Web Interface
Open browser and go to:
```
http://127.0.0.1:8000/docs
```

### Task 2 - Step 5: Test the API
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