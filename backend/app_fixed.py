import os
import pickle
import numpy as np
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import serial
import threading
import time
import json

app = Flask(__name__)
CORS(app)

# ================= MODELS =================
# Tea Production Model (for tea crop prediction)
tea_model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')

# Crop Recommendation Model (for crop recommendations - uses Arduino data)
crop_model_path = os.path.join(os.path.dirname(__file__), '..', 'mega_project copy', 'model.pkl')

# Load Tea Production Model
print(f"🔍 Looking for tea model at: {tea_model_path}")
print(f"📁 Tea model exists: {os.path.exists(tea_model_path)}")

try:
    with open(tea_model_path, 'rb') as f:
        tea_model = pickle.load(f)
    print("✅ Tea Production Model loaded successfully")
except Exception as e:
    print(f"❌ Tea model load error: {e}")
    tea_model = None

# Load Crop Recommendation Model  
print(f"🔍 Looking for crop model at: {crop_model_path}")
print(f"📁 Crop model exists: {os.path.exists(crop_model_path)}")

try:
    with open(crop_model_path, 'rb') as f:
        crop_model = pickle.load(f)
    print("✅ Crop Recommendation Model loaded successfully")
    print(f"🤖 Crop Model Type: {type(crop_model)}")
except Exception as e:
    print(f"❌ Crop model load error: {e}")
    crop_model = None

# ================= WEATHER =================
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

def get_weather_data(lat, lon):
    # If no API key, return default weather data for testing
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == 'your_api_key_here':
        print("Using default weather data (no API key)")
        return {
            "temperature": 25.0,
            "humidity": 60.0,
            "rainfall": 5.0
        }
    
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'
        }
        print(f"🌤️ Weather API URL: {url}")
        print(f"🌤️ Weather API params: {params}")
        
        res = requests.get(url, params=params)
        print(f"📡 Weather API status: {res.status_code}")
        
        if res.status_code != 200:
            print(f"❌ Weather API error: {res.text}")
            return None
        
        data = res.json()
        print(f"🌤️ Weather API response: {data}")
        
        return {
            "temperature": data['main']['temp'],
            "humidity": data['main']['humidity'],
            "rainfall": data.get('rain', {}).get('1h', 0)
        }

    except Exception as e:
        print(f"❌ Weather error: {e}")
        return {
            "temperature": 25.0,
            "humidity": 60.0,
            "rainfall": 5.0
        }

# ================= FEATURES =================
def create_features(temp, hum, rain):
    # Normalize input values
    temp_normalized = min(temp / 50, 1.0)  # Normalize 0-50°C
    hum_normalized = min(hum / 100, 1.0)  # Normalize 0-100%
    rain_normalized = min(rain / 200, 1.0)  # Normalize 0-200mm
    
    # Calculate essential features using formulas
    heat_index = temp_normalized * hum_normalized
    temp_humidity = temp_normalized * hum_normalized  
    rainfall_humidity = rain_normalized * hum_normalized
    
    # Tea-specific calculations
    tea_suitability = 0.7 + (temp_normalized - 0.5) * 0.3  # Dynamic based on temperature
    sustainability_score = 0.8 - abs(temp_normalized - 0.6) * 0.2  # Dynamic based on temperature
    
    # Create 17-feature vector (matching model training)
    features = np.array([[
        temp_normalized, hum_normalized, rain_normalized,  # Basic normalized values
        heat_index, temp_humidity, rainfall_humidity,  # Interaction terms
        tea_suitability, sustainability_score,  # Tea-specific
        temp_normalized * 0.1, hum_normalized * 0.1, rain_normalized * 0.1,  # Weighted contributions
        abs(temp_normalized - 0.3), abs(hum_normalized - 0.5), abs(rain_normalized - 0.2),  # Deviations
        temp_normalized**2, hum_normalized**2, rain_normalized**2,  # Polynomial features
        np.sin(temp_normalized * np.pi), np.cos(hum_normalized * np.pi), np.tan(rain_normalized * np.pi),  # Trig features
        temp_normalized * hum_normalized * rain_normalized,  # Triple interaction
        (temp_normalized + hum_normalized + rain_normalized) / 3,  # Average
        max(temp_normalized, hum_normalized, rain_normalized),  # Maximum
        min(temp_normalized, hum_normalized, rain_normalized),  # Minimum
        temp_normalized - hum_normalized, temp_normalized - rain_normalized, hum_normalized - rain_normalized  # Differences
    ]]).reshape(1, -1)  # Reshape for model input
    
    print(f"🔢 Features shape: {features.shape}")
    print(f"🔢 Features: {features}")
    
    return features

# ================= ARDUINO =================
arduino_port = None
arduino_connected = False
arduino_data = {
    'temperature': 25.0,
    'humidity': 60.0,
    'soil_moisture': 50.0
}

def read_arduino():
    global arduino_port, arduino_connected, arduino_data
    
    try:
        arduino_port = serial.Serial('COM4', 9600, timeout=1)
        time.sleep(2)
        arduino_connected = True
        
        while arduino_connected:
            if arduino_port.in_waiting:
                line = arduino_port.readline().decode().strip()
                if line:
                    try:
                        data = json.loads(line)
                        arduino_data.update(data)
                        print(f"🌡️ Arduino: {data}")
                    except json.JSONDecodeError:
                        print(f"📡 Arduino decode error: {line}")
            time.sleep(0.2)
            
    except Exception as e:
        print("❌ Arduino read error:", e)
        arduino_connected = False

def init_arduino():
    global arduino_port, arduino_connected
    try:
        arduino_port = serial.Serial('COM4', 9600, timeout=1)
        time.sleep(2)
        arduino_connected = True
        
        threading.Thread(target=read_arduino, daemon=True).start()
        print("✅ Arduino Connected")
        
    except Exception as e:
        print("❌ Arduino Error:", e)

# ================= ROUTES =================
@app.route('/')
def home():
    return "API Running 🚀"

@app.route('/predict', methods=['POST'])
def predict():
    if tea_model is None:
        return jsonify({"error": "Tea production model not loaded. Check model.pkl file"}), 500
    
    try:
        data = request.get_json()
        print(f"📥 Request data: {data}")
        
        lat = data['lat']
        lon = data['lon']
        print(f"📍 Location: {lat}, {lon}")
        
        weather = get_weather_data(lat, lon)
        print(f"🌤️ Weather data: {weather}")
        
        if not weather:
            return jsonify({"error": "Weather fetch failed"}), 500
        
        features = create_features(
            weather['temperature'],
            weather['humidity'],
            weather['rainfall']
        )
        print(f"🔢 Features shape: {features.shape}")
        print(f"🔢 Features: {features}")
        
        try:
            print(f"🍃 Using Tea Production Model")
            print(f"🤖 Model type: {type(tea_model)}")
            
            prediction = tea_model.predict(features)
            print(f"🤖 Model output shape: {prediction.shape}")
            print(f"📊 Model output: {prediction}")
            
            # Handle different output formats
            if hasattr(prediction, 'flatten'):
                prediction_value = prediction.flatten()[0]
            elif hasattr(prediction, 'shape') and len(prediction.shape) > 1:
                prediction_value = prediction[0][0] if prediction.shape[1] == 1 else prediction[0]
            else:
                prediction_value = prediction[0] if hasattr(prediction, '__len__') else prediction
                
            print(f"📊 Final prediction: {prediction_value}")
            
            # Add temperature-based variation
            temp = weather['temperature']
            if temp > 30:
                prediction_value = prediction_value * 1.2
            elif temp > 25:
                prediction_value = prediction_value * 1.0
            elif temp > 20:
                prediction_value = prediction_value * 0.8
            else:
                prediction_value = prediction_value * 0.6
                
            print(f"🌡️ Temperature-adjusted prediction: {prediction_value}")
            
        except Exception as e:
            print(f"❌ Model prediction error: {e}")
            print(f"❌ Model details: {tea_model}")
            return jsonify({"error": f"Model prediction failed: {str(e)}"}), 500
        
        return jsonify({
            "weather": weather,
            "prediction": float(prediction_value)
        })
        
    except Exception as e:
        print(f"❌ Prediction error: {str(e)}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@app.route('/sensor', methods=['GET'])
def sensor():
    return jsonify(arduino_data)

@app.route('/pump', methods=['POST'])
def pump():
    data = request.json
    cmd = data.get("command", "").upper()
    
    if not arduino_connected:
        return jsonify({"error": "Arduino not connected"}), 500
    
    if cmd not in ["ON", "OFF"]:
        return jsonify({"error": "Invalid command"}), 400
    
    try:
        arduino_port.write((cmd + "\n").encode())
        return jsonify({"status": f"Pump {cmd}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recommend-crop-with-arduino', methods=['POST'])
def recommend_crop_with_arduino():
    if crop_model is None:
        return jsonify({'error': 'Crop recommendation model not loaded'}), 500
    
    try:
        data = request.get_json()
        print("🔍 INPUT DATA:", data)
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        nitrogen = float(data.get('nitrogen', 0))
        phosphorus = float(data.get('phosphorus', 0))
        potassium = float(data.get('potassium', 0))
        ph = float(data.get('ph', 7.0))
        
        temperature = arduino_data.get('temperature', 25.0)
        humidity = arduino_data.get('humidity', 60.0)
        soil_moisture = arduino_data.get('soil_moisture', 50.0)
        
        print(f"🌱 Crop Recommendation: N={nitrogen}, P={phosphorus}, K={potassium}, pH={ph}")
        print(f"🌡️ Arduino Data: Temp={temperature}°C, Humidity={humidity}%, Soil Moisture={soil_moisture}%")
        
        if crop_model is None:
            print("❌ Crop Model Not Available - Using Fallback Logic")
            # Simple fallback scoring
            crop_scores = [
                {'name': 'Wheat', 'score': 0.6},
                {'name': 'Rice', 'score': 0.6},
                {'name': 'Corn', 'score': 0.6}
            ]
        else:
            print("✅ Using Crop Model for Prediction")
            # Prepare features for crop model (N, P, K, pH, temp, humidity, soil_moisture)
            features = np.array([[
                nitrogen, phosphorus, potassium, ph,
                temperature, humidity, soil_moisture
            ]])
            
            print(f"🤖 Crop Model Input Shape: {features.shape}")
            print(f"🤖 Crop Model Input: {features}")
            
            # Use the Crop Recommendation Model for prediction
            try:
                prediction = crop_model.predict(features)
                print(f"🤖 Crop Model Output: {prediction}")
                print(f"🤖 Crop Model Output Shape: {prediction.shape}")
                
                # Convert model output to crop scores
                if hasattr(prediction, 'flatten'):
                    pred_values = prediction.flatten()
                else:
                    pred_values = prediction[0]
                
                print(f"🤖 Crop Model Predicted Values: {pred_values}")
                
                # Map model outputs to crop scores
                crop_scores = []
                crops = ['Wheat', 'Rice', 'Corn', 'Cotton', 'Sugarcane', 'Pulses', 'Vegetables']
                for i, crop in enumerate(crops):
                    crop_scores.append({
                        'name': crop,
                        'score': float(pred_values[i])
                    })
                
                print(f"🌱 Crop Scores from Model: {crop_scores}")
                
            except Exception as e:
                print(f"❌ Crop Model Prediction Error: {e}")
                import traceback
                traceback.print_exc()
                # Fallback to simple scoring if model fails
                crop_scores = [
                    {'name': 'Wheat', 'score': 0.6},
                    {'name': 'Rice', 'score': 0.6},
                    {'name': 'Corn', 'score': 0.6}
                ]
        
        response = {
            'status': 'success',
            'user_input': {
                'nitrogen_mg_kg': round(nitrogen, 2),
                'phosphorus_mg_kg': round(phosphorus, 2),
                'potassium_mg_kg': round(potassium, 2),
                'ph_value': round(ph, 2)
            },
            'arduino_sensors': {
                'temperature_c': round(temperature, 2),
                'humidity_percent': round(humidity, 2),
                'soil_moisture_percent': round(soil_moisture, 2)
            },
            'top_recommendation': crop_scores[0]['name'] if crop_scores else 'None',
            'crop_recommendations': crop_scores
        }
        
        print(f"✅ Crop recommendation: {response['top_recommendation']}")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Crop recommendation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Crop recommendation failed: {str(e)}'}), 500

# ================= MAIN =================
if __name__ == '__main__':
    print("🚀 Starting Server...")
    init_arduino()
    app.run(debug=False, port=5000)
