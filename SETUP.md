# 🚀 Quick Setup Guide

## Step 1: Get OpenWeather API Key

1. Visit [OpenWeather](https://openweathermap.org/api)
2. Sign up for a free account
3. Get your API key from the dashboard
4. Copy the key for the next step

## Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env file and add your OpenWeather API key

# Start the backend server
python app.py
```

**Or use the quick start script:**
```bash
python start_backend.py
```

## Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

**Or use the quick start script:**
```bash
python start_frontend.py
```

## Step 4: Test the Application

1. Open your browser and go to `http://localhost:3000`
2. Click on the map to select a location
3. Or click "Use My Location" for GPS detection
4. Wait for the prediction to appear

## 🔧 Troubleshooting

### Backend Issues
- **Port 5000 already in use**: Change the port in `app.py`
- **Model not found**: Ensure `model.pkl` exists in `mega_project copy` directory
- **API key errors**: Check your OpenWeather API key is correctly set

### Frontend Issues
- **Port 3000 already in use**: The app will automatically try the next available port
- **CORS errors**: Make sure the backend is running on port 5000
- **Map not loading**: Check your internet connection

### Testing Without API Key
The app will work with default weather values if you don't have an API key yet, but predictions will be less accurate.

## 📞 Need Help?

Check the main [README.md](README.md) for detailed documentation.
