# Tea Production Prediction System

A full-stack Machine Learning web application that predicts tea production (in MKgs) based on real-time weather data and geographic location.

## 🌟 Features

- **Interactive Map**: Click anywhere on the map to select a location
- **GPS Location**: Automatic location detection using browser's geolocation
- **Real-time Weather**: Fetches current weather data from OpenWeather API
- **ML Prediction**: Uses a trained regression model to predict tea production
- **Professional UI**: Modern, responsive design with real-time feedback

## 🏗️ Architecture

```
├── backend/                 # Flask API server
│   ├── app.py              # Main API application
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variables template
├── frontend/               # React web application
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── App.css         # Styling
│   │   ├── index.js        # Entry point
│   │   └── index.css       # Global styles
│   ├── public/
│   │   └── index.html      # HTML template
│   └── package.json        # Node.js dependencies
└── mega_project copy/      # ML model and training data
    ├── model.pkl           # Trained ML model
    ├── my_data.csv         # Training dataset
    └── training.py         # Model training script
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- OpenWeather API key (free from [OpenWeather](https://openweathermap.org/api))

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenWeather API key
   ```

5. **Start the backend server:**
   ```bash
   python app.py
   ```

   The API will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

   The application will be available at `http://localhost:3000`

## 📡 API Endpoints

### POST /predict

Predicts tea production for given coordinates.

**Request:**
```json
{
  "latitude": 26.5,
  "longitude": 92.7
}
```

**Response:**
```json
{
  "location": {
    "latitude": 26.5,
    "longitude": 92.7
  },
  "weather": {
    "temperature": 22.5,
    "humidity": 65.0,
    "rainfall": 2.1
  },
  "prediction": {
    "expected_tea_production_mkgs": 35.67
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "api_key_configured": true
}
```

## 🧠 ML Model Features

The model uses the following engineered features:

- **Temperature_C**: Current temperature in Celsius
- **Precipitation_mm_day**: Daily rainfall in millimeters
- **Humidity_Percent**: Relative humidity percentage
- **Solar_Radiation_MJ_m2_day**: Solar radiation (default: 15.0)
- **Latitude**: Geographic latitude
- **Longitude**: Geographic longitude
- **Elevation_m**: Elevation in meters (default: 120.0)
- **Month_Sin/Month_Cos**: Cyclical month encoding
- **Heat_Index**: Temperature + 0.1 × Humidity
- **Temp_Humidity**: Temperature × Humidity
- **Rainfall_Humidity**: Rainfall × Humidity
- **Temp_Solar**: Temperature × Solar Radiation
- **Prev_Month_Production**: Previous month production (default: 30.0)
- **Prev_2Month_Production**: Production from 2 months ago (default: 30.0)
- **Rolling_3Month_Avg**: 3-month rolling average (default: 30.0)
- **State_Encoded**: State encoding (default: 0)

## 🌤️ Weather Data

The application fetches real-time weather data from OpenWeather API:

- **Temperature**: Current temperature in Celsius
- **Humidity**: Relative humidity percentage
- **Rainfall**: Precipitation data (1h or 3h averages)

If weather data is unavailable, the system uses default values to ensure predictions are always possible.

## 🎨 UI Components

### Interactive Map
- Powered by Leaflet.js and OpenStreetMap
- Click to select any location worldwide
- Shows selected coordinates
- Zoom and pan controls

### Location Selection
- **Map Click**: Click anywhere on the map
- **GPS Button**: Automatic location detection
- **Coordinate Display**: Shows selected lat/lng

### Results Display
- **Weather Card**: Current conditions at selected location
- **Prediction Card**: Expected tea production in MKgs
- **Loading States**: Visual feedback during API calls
- **Error Handling**: User-friendly error messages

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
OPENWEATHER_API_KEY=your_actual_api_key_here
```

### Model Path

The app automatically looks for the model at:
```
../mega_project copy/model.pkl
```

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend is running on port 5000
2. **Weather API Failures**: Check OpenWeather API key is valid
3. **Model Loading Errors**: Verify model.pkl exists and is accessible
4. **Location Not Working**: Enable browser location permissions

### Health Check

Test the backend health:
```bash
curl http://localhost:5000/health
```

## 📱 Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- OpenWeather API for weather data
- Leaflet.js for interactive maps
- React for the frontend framework
- Flask for the backend API
- scikit-learn for machine learning
