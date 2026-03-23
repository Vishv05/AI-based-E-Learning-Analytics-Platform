# 🎓 AI-Based E-Learning Analytics Platform

**Short Description:**
AI based E-Learning Analytics Platform is a comprehensive AI-powered system that analyzes student performance, predicts outcomes using deep learning (LSTM), identifies at-risk learners, and provides actionable insights through interactive dashboards to improve educational results.

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.20-orange.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A comprehensive AI-powered analytics platform for e-learning systems that leverages deep learning (LSTM) to predict student performance, identify at-risk learners, and provide actionable insights through interactive dashboards.

---

## � **START HERE** - Quick Start (5 minutes)

```powershell
# 1. Windows PowerShell - Automated Setup
.\setup.ps1

# 2. Start MongoDB (auto-starts on Windows)
mongosh --eval "db.adminCommand('ping')"

# 3. Run the Flask app
python Backend\app.py

# 4. Open browser
# http://127.0.0.1:5000
# Register → Login → Explore Dashboard
```

**Linux/Mac users:** Replace `setup.ps1` with `./setup.sh`

---

## �📋 Table of Contents

- [Quick Start](#-start-here---quick-start-5-minutes)
- [Overview](#-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Deployment](#-deployment--production)
- [System Requirements](#-system-requirements)
- [Model Architecture](#-model-architecture)
- [Dashboard Screenshots](#-dashboard-screenshots)
- [API Endpoints](#-api-endpoints)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

### 📖 Additional Documentation

**For first-time users, read these files in order:**
1. **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
2. **[README.md](README.md)** - Full documentation
3. **[TESTING.md](TESTING.md)** - Verify everything works

---

## 🎯 Overview

This project implements a complete AI-driven analytics solution for online learning platforms. It tracks student behavior, analyzes engagement patterns, and uses Long Short-Term Memory (LSTM) neural networks to predict future performance and identify students at risk of dropping out.

### Key Capabilities

- **📊 Real-time Analytics**: Track student engagement, quiz scores, time spent, and course progress
- **🤖 AI Predictions**: LSTM-based forecasting of student performance
- **⚠️ Risk Assessment**: Automated identification of at-risk students
- **📈 Interactive Dashboards**: Beautiful, responsive visualizations using Chart.js
- **🎯 Actionable Insights**: Data-driven recommendations for intervention

---

## ✨ Features

### 1. **Advanced Analytics Dashboard**
   - Total students enrolled
   - Average engagement metrics
   - Course completion rates
   - Performance trends over time
   - Interactive charts and graphs

### 2. **LSTM-Based Prediction Engine**
   - Deep learning model with Bidirectional LSTM layers
   - Sequence-based learning behavior modeling
   - Engagement score prediction (0-10 scale)
   - Dropout risk assessment

### 3. **Student Risk Classification**
   - **Low Risk** (8.0-10): Excellent performance
   - **Medium-Low Risk** (6.5-7.9): On track
   - **Medium Risk** (5.0-6.4): Needs attention
   - **High Risk** (<5.0): At risk of dropout

### 4. **Beautiful Modern UI**
   - Gradient color schemes
   - Smooth animations and transitions
   - Responsive design (mobile-friendly)
   - Professional cards and charts
   - Sidebar navigation

### 5. **Data Visualization**
   - Progress tracking over time
   - Score distribution analysis
   - Engagement heatmaps
   - Training metrics visualization
   - Prediction vs actual comparisons

---

## 🛠️ Technology Stack

### Backend
- **Python 3.13+**: Core programming language
- **TensorFlow 2.20**: Deep learning framework
- **Keras**: High-level neural networks API
- **NumPy**: Numerical computations
- **Pandas**: Data manipulation and analysis
- **Scikit-learn**: Data preprocessing and metrics
- **Flask**: Web application framework

### Frontend
- **HTML5**: Structure and semantics
- **CSS3**: Modern styling with gradients and animations
- **JavaScript**: Interactive functionality
- **Bootstrap 5**: Responsive layout framework
- **Chart.js 4.3**: Interactive data visualizations
- **Font Awesome 6**: Icon library

### Data & Visualization
- **Matplotlib**: Static plot generation
- **Seaborn**: Statistical visualizations
- **Chart.js**: Interactive web charts

---

## 📁 Project Structure

```
D:\lstm_project\
│
├── Backend\
│   ├── src\ (data_preprocessing, lstm_model, train, predict)
│   ├── data\ (raw & processed student data)
│   ├── models\ (lstm_model.h5, scaler.pkl)
│   ├── outputs\ (graphs, predictions, training_summary.json)
│   ├── app.py (Flask web app)
│   └── main.py (complete pipeline)
├── Frontend\
│   ├── templates\ (dashboard, analytics, prediction)
│   └── static\ (CSS, JavaScript, charts)
├── venv\ (virtual environment)
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

### Prerequisites

- Python 3.13 or higher (required for the bundled TensorFlow 2.20 cp313 wheel)
- pip (Python package installer)
- 8GB RAM minimum (for model training)
- Windows/Linux/macOS

### Step-by-Step Setup

1. **Clone or Download the Project**
   ```bash
   cd D:\lstm_project
   ```

2. **Automated Setup (Recommended)**
   
   **Windows (PowerShell):**
   ```bash
   .\setup.ps1
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   *The setup script will:*
   - ✓ Create a virtual environment
   - ✓ Install all dependencies
   - ✓ Verify TensorFlow installation

3. **Manual Setup** (if automated setup doesn't work)
   
   Create Virtual Environment:
   ```bash
   python -m venv venv
   ```

   Activate Virtual Environment:
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

   Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Verify Installation:
   ```bash
   python -c "import tensorflow as tf; print(tf.__version__)"
   ```

4. **Setup MongoDB** (Required for Authentication)
   
   MongoDB is required for user authentication (login/register). Choose one of the options below:

   **Option A: Local MongoDB Installation (Windows)**
   - Download MongoDB Community Edition from: https://www.mongodb.com/try/download/community
   - Run the installer and choose "Install MongoDB as a Service"
   - MongoDB will start automatically and listen on `mongodb://localhost:27017`
   - Verify connection: Open Command Prompt and run:
     ```bash
     mongosh --eval "db.adminCommand('ping')"
     ```

   **Option B: MongoDB Atlas (Cloud)**
   - Create a free account at: https://www.mongodb.com/cloud/atlas
   - Create a cluster and get your connection string
   - Update `.env` file with your Atlas connection string:
     ```
     MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
     ```

   **Option C: MongoDB Docker Container (if Docker is installed)**
   ```bash
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

5. **Configure Environment Variables**
   - A `.env` file has been auto-created with default settings
   - Edit it only if you're using MongoDB Atlas or a custom configuration:
   ```bash
   # .env file in project root
   MONGO_URI=mongodb://localhost:27017
   MONGO_DB_NAME=elearning_analytics
   FLASK_ENV=development
   ```

---

## ⚙️ Configuration

### Environment Variables

The project uses a `.env` file for configuration. A default `.env` file has been created with the following settings:

```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017        # Local MongoDB
MONGO_DB_NAME=elearning_analytics          # Database name

# Flask Configuration
FLASK_ENV=development                       # development or production
FLASK_DEBUG=False                          # Set to True for debug mode
SECRET_KEY=ai-elearning-analytics-2026     # Session encryption key
```

### Customizing Configuration

**For MongoDB Atlas (Cloud):**
Edit `.env` and update `MONGO_URI`:
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

**For Production:**
Edit `.env` and change:
```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secure-random-key-here
```

**File Structure After Setup:**
```
D:\AI based E-Learning Analytics Platform\
├── .env                          ← Environment variables (auto-created)
├── .env.example                  ← Template for .env
├── .gitignore                    ← Git ignore rules
├── README.md
├── requirements.txt
├── Backend\
│   ├── app.py                    ← Flask application (main entry point)
│   ├── main.py                   ← Complete pipeline runner
│   ├── src\
│   │   ├── data_preprocessing.py
│   │   ├── lstm_model.py
│   │   ├── train.py
│   │   └── predict.py
│   ├── data\
│   │   ├── raw\
│   │   │   └── student_activity.csv
│   │   └── processed\
│   │       └── cleaned_data.csv
│   ├── models\
│   │   ├── lstm_model.h5         ← Trained model (ready to use)
│   │   └── scaler.pkl
│   └── outputs\
│       ├── predictions\
│       │   └── results.csv
│       ├── graphs\
│       └── training_summary.json
├── Frontend\
│   ├── templates\
│   │   ├── dashboard.html
│   │   ├── analytics.html
│   │   ├── predictions.html
│   │   ├── login.html
│   │   └── register.html
│   └── static\
│       ├── css\
│       │   └── style.css
│       └── js\
│           └── charts.js
└── venv\
    └── (virtual environment)
```

---

### Quick Start (Fastest Way) ⚡

**Basic 5-minute setup:**

1. **Start MongoDB**
   ```bash
   # MongoDB should auto-start on Windows
   # Verify: mongosh --eval "db.adminCommand('ping')"
   ```

2. **Activate virtual environment**
   ```bash
   venv\Scripts\activate
   ```

3. **Run the Flask app**
   ```bash
   python Backend\app.py
   ```

4. **Open browser and register**
   - Visit: `http://127.0.0.1:5000`
   - Click "Register" and create an account
   - Login and explore the dashboard

---

### Option 1: Complete Pipeline (Recommended for First Run)

Run the entire pipeline (preprocessing → training → predictions):

```bash
python Backend\main.py
```

**What this does:**
- ✅ Preprocesses raw student data
- ✅ Splits data into train/test sets
- ✅ Trains the LSTM model (may take 10-20 minutes)
- ✅ Saves the trained model to `Backend\models\lstm_model.h5`
- ✅ Generates predictions for all students
- ✅ Creates visualizations and graphs
- ✅ Saves results to `Backend\outputs\`

---

### Option 2: Step-by-Step Execution

**Step 1: Data Preprocessing Only**
```bash
python Backend\src\data_preprocessing.py
```
*Output: `Backend\data\processed\cleaned_data.csv`*

**Step 2: Train the LSTM Model**
```bash
python Backend\src\train.py
```
*Output: `Backend\models\lstm_model.h5` + training graphs*

**Step 3: Generate Predictions**
```bash
python Backend\src\predict.py
```
*Output: `Backend\outputs\predictions\results.csv`*

**Step 4: Launch Web Application**
```bash
python Backend\app.py
```

---

### Option 3: Just Run the Flask Dashboard

If you already have a trained model:

```bash
python Backend\app.py
```

The Flask app will:
- Load the pre-trained LSTM model
- Serve the interactive dashboard
- Provide API endpoints for predictions
- Display analytics and visualizations

---

### Running with Custom Configuration

#### Change Flask Port
Edit `Backend\app.py` or run with:
```bash
# Windows - via Flask CLI
set FLASK_APP=Backend\app.py
flask run --port 8000
```

#### Train with Different Hyperparameters
Edit `Backend\src\train.py` before running:
```python
# Modify these parameters:
epochs = 100
batch_size = 32
sequence_length = 3
validation_split = 0.2
```

#### Generate Predictions for Specific Students
Edit `Backend\src\predict.py` and specify student IDs:
```python
student_ids = [1, 2, 3, 4, 5]  # Modify this list
```

---

### Access the Dashboard

Once the Flask app is running, open your browser and navigate to:

```
http://127.0.0.1:5000
```

**Available pages:**
- 🏠 **Dashboard** (`/`) - Overview and statistics
- 📊 **Analytics** (`/analytics`) - Training metrics and trends
- 🎯 **Predictions** (`/predictions`) - Risk assessments and recommendations
- 📈 **Student Progress** (`/`) - Individual student metrics

---

### Useful Commands

**Check if dependencies are installed:**
```bash
pip list | findstr tensorflow flask pandas numpy
```

**Reinstall all requirements:**
```bash
pip install --upgrade -r requirements.txt
```

**Check Python version:**
```bash
python --version
```

**View TensorFlow version:**
```bash
python -c "import tensorflow as tf; print(tf.__version__)"
```

**Check if GPU is available (optional):**
```bash
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

---

### Docker (Optional)

If you want to containerize the application:

```bash
# Build Docker image (if Dockerfile exists)
docker build -t elearning-analytics .

# Run container
docker run -p 5000:5000 elearning-analytics
```

---

## 🧠 Model Architecture

### LSTM Network Configuration

```python
Model: Sequential
_________________________________________________________________
Layer (type)                Output Shape              Param #   
=================================================================
bidirectional_lstm_1        (None, 3, 256)            140,544
dropout_1                   (None, 3, 256)            0
lstm_2                      (None, 64)                82,176
dropout_2                   (None, 64)                0
dense_1                     (None, 32)                2,080
dropout_3                   (None, 32)                0
dense_2                     (None, 16)                528
output                      (None, 1)                 17
=================================================================
Total params: 225,345
Trainable params: 225,345
```

### Key Features

- **Bidirectional LSTM**: Captures patterns in both forward and backward directions
- **Dropout Regularization**: Prevents overfitting (30% dropout rate)
- **Adam Optimizer**: Adaptive learning rate optimization
- **Early Stopping**: Prevents overtraining
- **Learning Rate Reduction**: Dynamic LR adjustment

### Training Parameters

- **Sequence Length**: 3 weeks of historical data
- **Batch Size**: 32
- **Max Epochs**: 100 (with early stopping)
- **Loss Function**: Mean Squared Error (MSE)
- **Metrics**: MAE, RMSE

---

## 📊 Data Format

### Input Features (8 features per time step)

1. **login_count**: Number of logins per week
2. **time_spent_hours**: Hours spent on platform
3. **quiz_score**: Quiz performance (0-100)
4. **assignment_score**: Assignment performance (0-100)
5. **forum_posts**: Forum participation count
6. **video_completion_rate**: Video watching completion (0-1)
7. **course_progress**: Overall progress percentage (0-100)
8. **engagement_score**: Composite engagement metric (0-10)

### Sample Data Row

```csv
student_id,week,login_count,time_spent_hours,quiz_score,assignment_score,forum_posts,video_completion_rate,course_progress,engagement_score
1,1,5,12.5,75,80,3,0.85,15,7.2
```

---

## 🌐 API Endpoints

### Dashboard APIs

- **GET** `/api/student-progress` - Student progress over time
- **GET** `/api/engagement-trends` - Weekly engagement trends
- **GET** `/api/quiz-scores` - Quiz score distribution
- **GET** `/api/statistics` - General statistics

### Analytics APIs

- **GET** `/api/training-metrics` - LSTM training metrics
- **GET** `/api/risk-distribution` - Risk level distribution

### Prediction APIs

- **POST** `/api/predict-student` - Predict for specific student
  ```json
  {
    "student_id": 1
  }
  ```

---

## 📈 Performance Metrics

### Typical Model Performance

- **Test Loss (MSE)**: ~0.0045
- **Test MAE**: ~0.0520
- **Test RMSE**: ~0.0671

### Prediction Accuracy

The model achieves high accuracy in predicting student engagement scores, with predictions typically within ±0.5 points on a 10-point scale.

---

## 🎨 Dashboard Features

### 1. Main Dashboard
- Real-time student statistics
- Interactive progress charts
- Engagement trend analysis
- Score distribution visualization

### 2. Analytics Page
- LSTM training metrics
- Loss and MAE curves
- Weekly performance analysis
- Feature correlation insights

### 3. Predictions Page
- AI-generated risk assessments
- Risk level distribution
- High-risk student alerts
- Detailed recommendations

---

## 🔧 Customization

### Modifying Model Parameters

Edit `src/lstm_model.py`:
```python
model.build_model(
    lstm_units=[128, 64],      # Layer sizes
    dropout_rate=0.3,          # Dropout rate
    learning_rate=0.001        # Initial LR
)
```

### Changing Sequence Length

Edit training scripts:
```python
train_model(
    epochs=100,
    batch_size=32,
    sequence_length=5  # Change from 3 to 5 weeks
)
```

### Adding New Features

1. Update `student_activity.csv` with new columns
2. Modify `feature_columns` in `data_preprocessing.py`
3. Retrain the model

---

## 🐛 Troubleshooting

### MongoDB Issues

**Issue**: "Connection refused" or "mongodb://localhost:27017 is unavailable"
- **Solution**: Start MongoDB service
  - **Windows**: MongoDB should start automatically. Check Services (services.msc)
  - **Linux**: `sudo systemctl start mongod`
  - **Mac**: `brew services start mongodb-community`

**Issue**: "Cannot connect to MongoDB Atlas"
- **Solution**: Check your connection string in `.env` file
  - Verify username and password are correct
  - Ensure IP address is whitelisted in MongoDB Atlas (Settings → Network Access)
  - Check if database user has proper permissions

**Issue**: Authentication failed with "Email already registered"
- **Solution**: MongoDB database already has user data
  - Clear the database: Run `mongosh` and execute:
    ```javascript
    use elearning_analytics
    db.users.deleteMany({})
    ```
  - Or use a different database name in `.env`

### Common Issues

**Issue**: TensorFlow installation fails
- **Solution**: Upgrade pip: `pip install --upgrade pip`
- **Solution**: Use CPU-only version: `pip install tensorflow-cpu`

**Issue**: Model not found error
- **Solution**: Train the model first: `python Backend\src\train.py`

**Issue**: Port 5000 already in use
- **Solution**: Change port in `Backend\app.py`: `app.run(port=5001)`

**Issue**: Out of memory during training
- **Solution**: Reduce batch size in `Backend\src\train.py`: `batch_size=16`

**Issue**: "Module not found" errors when running Flask app
- **Solution**: Ensure you're in the project root directory and venv is activated
  ```bash
  cd "d:\AI based E-Learning Analytics Platform"
  venv\Scripts\activate
  python Backend\app.py
  ```

---

## 🌐 Deployment & Production

### Local Network Access

To access the Flask app from other machines on your network:

1. Find your machine's IP address:
   ```bash
   ipconfig
   # Look for IPv4 Address (e.g., 192.168.x.x)
   ```

2. Run Flask with network binding:
   ```bash
   python Backend\app.py --host 0.0.0.0 --port 5000
   ```

3. Access from another machine:
   ```
   http://192.168.x.x:5000
   ```

### Production Deployment (Using Gunicorn)

For production, use Gunicorn instead of Flask's development server:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --workers 4 --threads 2 -b 0.0.0.0:5000 "Backend.app:app"
```

### Docker Deployment

Create a `Dockerfile` for containerization:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "Backend/app.py"]
```

Build and run:
```bash
docker build -t elearning-analytics .
docker run -p 5000:5000 -e MONGO_URI=mongodb://host.docker.internal:27017 elearning-analytics
```

---

## 📊 System Requirements

### Minimum Requirements
- **CPU**: Intel i5 or equivalent
- **RAM**: 8GB minimum (4GB for inference only, 16GB+ recommended for training)
- **Storage**: 5GB free space
- **Python**: 3.13+
- **MongoDB**: 4.0+ (local or cloud)

### Recommended for Model Training
- **CPU**: Intel i7/i9 or AMD Ryzen 7+
- **GPU**: NVIDIA GPU with CUDA support (optional, significantly faster)
- **RAM**: 16GB+
- **Storage**: 20GB SSD

### Disk Space Breakdown
- Python environment: ~2.5GB
- TensorFlow framework: ~1.2GB
- Project files & data: ~500MB
- Model outputs & graphs: ~200MB
- **Total**: ~4.5GB

---

- [ ] Real-time data streaming integration
- [ ] Multi-model ensemble predictions
- [ ] Automated email alerts for at-risk students
- [ ] Student clustering analysis
- [ ] Course recommendation engine
- [ ] Mobile application
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/Azure)

---

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- TensorFlow and Keras teams for the deep learning framework
- Flask community for the web framework
- Chart.js for beautiful visualizations
- Bootstrap for responsive design components

---

## 📧 Contact

For questions, suggestions, or collaboration opportunities:

- **Project**: AI E-Learning Analytics Platform
- **Author**: Your Name
- **Email**: your.email@example.com
- **GitHub**: @yourusername

---

## 🌟 Star History

If you find this project helpful, please consider giving it a ⭐!

---

**Built with ❤️ using Python, TensorFlow, and Flask**

*Last Updated: February 2026*

---

## 🚀 Migration Tool

### Tool: `migrate_sqlite_users_to_mongo.py`

This script migrates user data from SQLite to MongoDB.

#### Usage

```bash
python Backend/tools/migrate_sqlite_users_to_mongo.py
```

#### Features

- Migrates user data from SQLite to MongoDB
- Preserves user metadata
- Supports bulk operations
- Logs migration progress

---

## 📧 Contact

For questions, suggestions, or collaboration opportunities:

- **Project**: AI E-Learning Analytics Platform
- **Author**: Your Name
- **Email**: your.email@example.com
- **GitHub**: @yourusername

---

## 🌟 Star History

If you find this project helpful, please consider giving it a ⭐!

---

**Built with ❤️ using Python, TensorFlow, and Flask**

*Last Updated: February 2026*
>>>>>>> 55103ca (Initial commit: AI based E-Learning Analytics Platform)
