# 🧪 Project Testing & Verification Guide

This guide helps you verify that the AI E-Learning Analytics Platform is functioning correctly.

---

## 🔍 System Requirements Check

### 1. Python Version
```bash
python --version
```
✅ **Expected:** Python 3.13.x or higher

### 2. Disk Space
```bash
# Windows
dir
# Check available space is > 5GB

# Linux/Mac
df -h .
```
✅ **Expected:** At least 5GB free space

### 3. RAM Check
```bash
# Windows PowerShell
Get-WmiObject -Class Win32_ComputerSystem | Select-Object Name, TotalPhysicalMemory

# Linux
free -h

# Mac
vm_stat | grep node
```
✅ **Expected:** At least 8GB RAM

---

## 🔧 Dependency Verification

### 1. Python Virtual Environment
```bash
# Check if venv exists
ls -la venv
# or Windows: dir venv

# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Should show (venv) prompt
echo "If you see (venv) in prompt, you're good!"
```
✅ **Expected:** `(venv)` appears in terminal prompt

### 2. Core Dependencies
```bash
# Run this Python script to test all imports
python -c "
import sys
print('=== Dependency Check ===')
try:
    import tensorflow as tf
    print(f'✓ TensorFlow {tf.__version__}')
except ImportError as e:
    print(f'✗ TensorFlow: {e}')

try:
    import flask
    print(f'✓ Flask {flask.__version__}')
except ImportError as e:
    print(f'✗ Flask: {e}')

try:
    import pandas as pd
    print(f'✓ Pandas {pd.__version__}')
except ImportError as e:
    print(f'✗ Pandas: {e}')

try:
    import numpy as np
    print(f'✓ NumPy {np.__version__}')
except ImportError as e:
    print(f'✗ NumPy: {e}')

try:
    from sklearn import __version__
    print(f'✓ Scikit-learn {__version__}')
except ImportError as e:
    print(f'✗ Scikit-learn: {e}')

try:
    import pymongo
    print(f'✓ PyMongo installed')
except ImportError as e:
    print(f'✗ PyMongo: {e}')

print('=== Check Complete ===')
"
```
✅ **Expected:** All dependencies show with ✓

### 3. Verify Individual Packages
```bash
pip list | grep -E "tensorflow|flask|pandas|numpy|scikit|pymongo"
```
✅ **Expected:** All packages listed with version numbers

---

## 🗄️ Database Verification

### 1. MongoDB Connection Test
```bash
# Start MongoDB if not running
mongosh --eval "db.adminCommand('ping')"
```
✅ **Expected:** 
```
{ ok: 1 }
```

### 2. MongoDB Atlas Test (if using cloud)
Edit `.env` with your Atlas connection string and run:
```bash
python -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv('MONGO_URI')
client = MongoClient(uri)
try:
    client.admin.command('ping')
    print('✓ MongoDB Atlas connection successful')
except Exception as e:
    print(f'✗ MongoDB connection failed: {e}')
"
```
✅ **Expected:** `✓ MongoDB connection successful`

---

## 📊 Data Files Verification

### Check Required Files Exist
```bash
# Check raw data
ls -la Backend/data/raw/student_activity.csv

# Check processed data  
ls -la Backend/data/processed/cleaned_data.csv

# Check trained model
ls -la Backend/models/lstm_model.h5
ls -la Backend/models/scaler.pkl

# Check output files
ls -la Backend/outputs/predictions/results.csv
ls -la Backend/outputs/training_summary.json
```
✅ **Expected:** All files exist and have reasonable sizes

### Verify Data Format
```bash
# Check CSV format
python -c "
import pandas as pd

# Load raw data
df_raw = pd.read_csv('Backend/data/raw/student_activity.csv')
print(f'Raw data: {len(df_raw)} rows, {len(df_raw.columns)} columns')
print(f'Columns: {list(df_raw.columns)}')

# Load processed data
df_proc = pd.read_csv('Backend/data/processed/cleaned_data.csv')
print(f'Processed data: {len(df_proc)} rows, {len(df_proc.columns)} columns')

# Load predictions
df_pred = pd.read_csv('Backend/outputs/predictions/results.csv')
print(f'Predictions: {len(df_pred)} rows, {len(df_pred.columns)} columns')
"
```
✅ **Expected:**
```
Raw data: 323 rows, 12 columns
Processed data: 323 rows, 12 columns
Predictions: 25 rows, multiple columns
```

---

## 🤖 Model Verification

### 1. Load Pre-trained LSTM Model
```bash
python -c "
import tensorflow as tf
import os

model_path = 'Backend/models/lstm_model.h5'
if os.path.exists(model_path):
    model = tf.keras.models.load_model(model_path)
    print('✓ LSTM model loaded successfully')
    print(f'  Model summary:')
    model.summary()
else:
    print('✗ Model file not found')
"
```
✅ **Expected:** Model loads and shows summary

### 2. Load Scaler
```bash
python -c "
import pickle
import os

scaler_path = 'Backend/models/scaler.pkl'
if os.path.exists(scaler_path):
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    print('✓ Scaler loaded successfully')
else:
    print('✗ Scaler file not found')
"
```
✅ **Expected:** Scaler loads without errors

### 3. Test Prediction Pipeline
```bash
cd Backend
python -c "
import sys
sys.path.insert(0, 'src')
from predict import StudentPredictor

try:
    predictor = StudentPredictor()
    predictor.load_model()
    predictor.load_scaler()
    print('✓ Predictor initialized successfully')
except Exception as e:
    print(f'✗ Predictor error: {e}')
"
cd ..
```
✅ **Expected:** `✓ Predictor initialized successfully`

---

## 🌐 Flask Application Test

### 1. Test Flask Import
```bash
python -c "
import sys
import os
sys.path.insert(0, 'Backend')
try:
    from app import app
    print('✓ Flask app imports successfully')
    print(f'  Template folder: {app.template_folder}')
    print(f'  Static folder: {app.static_folder}')
except Exception as e:
    print(f'✗ Flask import error: {e}')
"
```
✅ **Expected:** `✓ Flask app imports successfully`

### 2. Start Flask App (Test Mode)
```bash
# Run in new terminal, keep for 30 seconds, then Ctrl+C
python Backend\app.py
```
✅ **Expected:**
```
 * Running on http://127.0.0.1:5000
```

### 3. Test API Endpoints
```bash
# In another terminal while Flask is running:

# Test dashboard (should return HTML)
curl http://127.0.0.1:5000/

# Test login page
curl http://127.0.0.1:5000/login

# Test predictions page
curl http://127.0.0.1:5000/predictions
```
✅ **Expected:** HTML responses (200 status code)

---

## 🎯 Frontend Verification

### Check Template Files
```bash
ls -la Frontend/templates/
```
✅ **Expected:** All HTML files exist:
- dashboard.html
- analytics.html  
- predictions.html
- login.html
- register.html
- 404.html
- 500.html

### Check Static Assets
```bash
ls -la Frontend/static/css/
ls -la Frontend/static/js/
```
✅ **Expected:**
```
Frontend/static/css/
  style.css

Frontend/static/js/
  charts.js
```

---

## 👤 Authentication Test

### Test User Registration
1. Start Flask: `python Backend\app.py`
2. Open: `http://127.0.0.1:5000`
3. Click "Register"
4. Fill in form:
   - Name: Test User
   - Email: test@example.com
   - Password: TestPassword123
   - Confirm: TestPassword123
5. Click Register

✅ **Expected:** Redirects to dashboard after successful registration

### Test User Login
1. Click Logout (if still logged in)
2. Click Login
3. Enter credentials:
   - Email: test@example.com
   - Password: TestPassword123
4. Click Login

✅ **Expected:** Logs in and displays dashboard

### Test Duplicate Registration
1. Try registering same email again

✅ **Expected:** Shows error "Email already registered"

---

## 📈 Dashboard Functionality Test

### Verify Dashboard Components
After logging in, check for:

- [ ] Student statistics displayed
- [ ] Engagement chart visible
- [ ] Score distribution chart visible
- [ ] Navigation sidebar works
- [ ] Can navigate to Analytics page
- [ ] Can navigate to Predictions page

✅ **Expected:** All components visible and clickable

### Test Analytics Page
1. Click "Analytics" in sidebar
2. Verify:
   - [ ] Training metrics chart visible
   - [ ] Loss curve displayed
   - [ ] MAE curve displayed
   - [ ] Performance metrics shown

✅ **Expected:** All charts and metrics visible

### Test Predictions Page
1. Click "Predictions" in sidebar
2. Verify:
   - [ ] Risk assessment table visible
   - [ ] Risk level distribution chart visible
   - [ ] High-risk students highlighted
   - [ ] Recommendations shown

✅ **Expected:** All predictions displayed correctly

---

## ⚙️ Configuration Test

### Verify .env Configuration
```bash
python -c "
from dotenv import load_dotenv
import os

load_dotenv()
print('=== Environment Variables ===')
print(f'MONGO_URI: {os.getenv(\"MONGO_URI\", \"Not set\")}')
print(f'MONGO_DB_NAME: {os.getenv(\"MONGO_DB_NAME\", \"Not set\")}')
print(f'FLASK_ENV: {os.getenv(\"FLASK_ENV\", \"Not set\")}')
print(f'FLASK_DEBUG: {os.getenv(\"FLASK_DEBUG\", \"Not set\")}')
print('=== All variables loaded ===')
"
```
✅ **Expected:** All variables shown correctly

---

## 📋 Complete Verification Checklist

Use this to track your verification:

```
System Requirements:
  [ ] Python 3.13+
  [ ] 8GB+ RAM
  [ ] 5GB+ free disk space

Dependencies:
  [ ] Virtual environment activated
  [ ] TensorFlow installed
  [ ] Flask installed
  [ ] Pandas, NumPy installed
  [ ] PyMongo installed

Database:
  [ ] MongoDB running
  [ ] Connection verified

Data:
  [ ] Raw data exists
  [ ] Processed data exists
  [ ] Model file exists
  [ ] Scaler file exists
  [ ] Predictions exist

Model:
  [ ] LSTM model loads
  [ ] Scaler loads
  [ ] Predictor works

Flask:
  [ ] App imports
  [ ] Flask starts
  [ ] Endpoints respond

Frontend:
  [ ] Templates exist
  [ ] Static files exist
  [ ] CSS loads
  [ ] JavaScript loads

Authentication:
  [ ] Can register
  [ ] Can login
  [ ] Can logout
  [ ] Duplicate registration blocked

Dashboard:
  [ ] Dashboard displays
  [ ] Analytics page works
  [ ] Predictions page works
  [ ] Charts render

Configuration:
  [ ] .env file exists
  [ ] Variables loaded
  [ ] MongoDB URI correct
```

---

## ✅ All Tests Passing?

If all checks pass, your system is **100% ready**! 🎉

Run the application:
```bash
python Backend\app.py
```

Then visit: `http://127.0.0.1:5000`

---

## 🐛 If Tests Fail

1. **Check error messages carefully** - they often indicate the exact issue
2. **See README.md → Troubleshooting** section for common issues
3. **Verify dependencies:** `pip install -r requirements.txt`
4. **Restart all services** (MongoDB, Flask)
5. **Clear Python cache:** `find . -type d -name __pycache__ -exec rm -r {} +`
6. **Reinstall TensorFlow:** `pip install --upgrade tensorflow`

---

## 📧 Report Issues

If something doesn't work after following this guide:
1. Note the exact error message
2. Include your Python version
3. Include your OS (Windows/Linux/Mac)
4. Check README.md troubleshooting section
