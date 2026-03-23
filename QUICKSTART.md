# ⚡ Quick Start Guide

Get the AI E-Learning Analytics Platform running in **5 minutes**!

## Prerequisites Checklist

- [ ] Python 3.13+ installed (`python --version`)
- [ ] MongoDB installed locally or accessible
- [ ] Project files downloaded/cloned
- [ ] ~2GB free disk space

## 🎯 5-Minute Setup

### Step 1: Run Automated Setup (2 minutes)

**Windows (PowerShell):**
```powershell
cd "d:\AI based E-Learning Analytics Platform"
.\setup.ps1
```

**Linux/Mac (Terminal):**
```bash
cd ~/AI-E-Learning-Analytics-Platform
chmod +x setup.sh
./setup.sh
```

> *This creates virtual environment and installs all dependencies*

### Step 2: Start MongoDB (1 minute)

**Windows:**
- MongoDB auto-starts as a Windows Service
- Verify: Open any terminal and run:
  ```bash
  mongosh --eval "db.adminCommand('ping')"
  ```
  Should show: `{ ok: 1 }`

**Linux:**
```bash
sudo systemctl start mongod
```

**Mac:**
```bash
brew services start mongodb-community
```

**Docker (if installed):**
```bash
docker run -d -p 27017:27017 mongo:latest
```

### Step 3: Run Flask App (1 minute)

```bash
# Virtual environment should already be activated from setup.ps1
python Backend\app.py
```

Should output:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Step 4: Access Dashboard (1 minute)

1. Open browser: **http://127.0.0.1:5000**
2. Click **"Register"**
3. Create account (provide name, email, password)
4. Login with your credentials
5. Explore the AI-powered dashboard!

---

## ✅ Verification

### Check Everything Works

```bash
# Test Python & TensorFlow
python -c "import tensorflow as tf; print(f'TensorFlow {tf.__version__}')"

# Test MongoDB connection
mongosh --eval "db.adminCommand('ping')"

# Test Flask app
python Backend\app.py
# Should start without errors
```

### Expected Output

| Component | Expected Output |
|-----------|-----------------|
| Python | `3.13.x` |
| TensorFlow | `2.20.0` |
| MongoDB | `{ ok: 1 }` |
| Flask | `Running on http://127.0.0.1:5000` |
| Dashboard | Login page loads in browser |

---

## 🚨 Common Issues & Quick Fixes

### Issue: MongoDB connection refused

**Solution 1:** Start MongoDB
```bash
# Windows: Check Services (services.msc) or run:
net start MongoDB

# Linux:
sudo systemctl start mongod

# Mac:
brew services start mongodb-community
```

**Solution 2:** Use MongoDB Atlas (Cloud)
- Go to https://www.mongodb.com/cloud/atlas
- Create free account and cluster
- Get connection string
- Update `.env` file: `MONGO_URI=<your_atlas_url>`

### Issue: "Module not found" errors

**Solution:** Make sure virtual environment is activated
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

Then check prompt shows `(venv)` before continuing.

### Issue: Port 5000 already in use

**Solution:** Use different port
```bash
# Edit Backend\app.py, change:
# app.run(port=5000)
# to:
app.run(port=5001)
```

Then access: `http://127.0.0.1:5001`

### Issue: "No module named tensorflow"

**Solution:** Reinstall TensorFlow
```bash
pip install --upgrade tensorflow
```

---

## 📊 Project Structure Overview

```
AI-E-Learning-Analytics/
├── Backend/                 # AI Model & API
│   ├── app.py             # Flask web server
│   ├── src/               # Model training & prediction
│   ├── models/            # Pre-trained LSTM model ✓
│   └── data/              # Sample student data
├── Frontend/              # Web Interface
│   ├── templates/         # HTML pages
│   └── static/            # CSS & JavaScript
├── .env                   # Configuration (auto-created)
├── setup.ps1 / setup.sh   # Automated setup script
└── requirements.txt       # Python dependencies
```

---

## 🎓 Main Features After Login

### 1. **Dashboard**
- Real-time student statistics
- Interactive engagement charts
- Performance trends

### 2. **Analytics**
- LSTM model training metrics
- Loss & accuracy curves
- Weekly performance analysis

### 3. **Predictions**
- AI-powered risk assessments
- Student risk levels (Low/Medium/High)
- Personalized recommendations

---

## 🔧 Next Steps

### To Train Your Own Model
```bash
python Backend\main.py
```
*(Takes 10-20 minutes, pre-trained model already included)*

### To Access on Other Computers
```bash
python Backend\app.py --host 0.0.0.0 --port 5000
# Then visit: http://<your-ip>:5000 from other machines
```

### To Deploy to Production
See [README.md](README.md) → "Deployment & Production" section

---

## 📞 Need Help?

1. **Check Troubleshooting:** [README.md](README.md#-troubleshooting)
2. **Verify MongoDB:** `mongosh --eval "db.adminCommand('ping')"`
3. **Check Python:** `python --version` (must be 3.13+)
4. **Review Logs:** Check terminal output for error messages

---

## ✨ Success Indicators

You're all set when you see:

1. ✓ Setup script completes without errors
2. ✓ MongoDB responds with `{ ok: 1 }`
3. ✓ Flask starts on `http://127.0.0.1:5000`
4. ✓ Login page loads in browser
5. ✓ Can create account and login
6. ✓ Dashboard displays student data and charts

**Congratulations! Your AI E-Learning Analytics Platform is ready to use! 🎉**
