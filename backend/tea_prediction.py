import os
import pickle
import numpy as np
import requests
import math
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ================= HUGGING FACE API CONFIGURATION =================
HUGGINGFACE_API_KEY = "hf_BXYl2JdJ7b8pkzFMmYQAWGdyb3FYX91E64SPXwTx8d7IAJt8rgrL"
HUGGINGFACE_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

# ================= TEA MODEL LOADING =================
print("🍵 Loading Tea Prediction Model...")

tea_model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
tea_model = None

# Patch platform module to avoid WMI error on Python 3.13
import platform
original_machine = platform.machine
def patched_machine():
    try:
        return original_machine()
    except OSError:
        return "AMD64"
platform.machine = patched_machine

try:
    with open(tea_model_path, 'rb') as f:
        tea_model = pickle.load(f)
    print(f"✅ Tea Model loaded: {tea_model_path}")
    print(f"   Tea Model expects {tea_model.n_features_in_} features")
except Exception as e:
    print(f"❌ Tea Model load error: {e}")
    tea_model = None

# ================= AI SUGGESTIONS =================
# Using rule-based suggestions for reliability

def generate_tea_image(suggestion_text, location):
    """Generate tea-related images using OpenAI DALL-E"""
    try:
        print("🎨 Generating AI image...")
        # Create a prompt based on the suggestion
        prompt = f"""
        Professional agricultural photograph of tea plantation with {suggestion_text.lower()}.
        Location: {location['latitude']:.2f}°N, {location['longitude']:.2f}°E.
        Style: Realistic, high-quality, educational agricultural photography.
        Natural lighting, showing tea plants and farming practices.
        """
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        image_url = response.data[0].url
        print("✅ AI image generated successfully")
        return {
            "status": "success",
            "image_url": image_url,
            "fallback_image": None
        }
        
    except Exception as e:
        print(f"❌ Image generation error: {e}")
        return {
            "status": "error",
            "image_url": None,
            "fallback_image": f"🍵 Tea plantation at {location['latitude']:.2f}°N, {location['longitude']:.2f}°E"
        }

def get_tea_suggestions(prediction_value, location, weather_data, month):
    """Generate dynamic context-aware tea growing suggestions"""
    print(f"🤖 Generating dynamic tea suggestions...")
    location_name = f"{location['latitude']:.2f}°N, {location['longitude']:.2f}°E"
    temp = weather_data.get('temperature', 25)
    humidity = weather_data.get('humidity', 70)
    
    suggestions = []
    
    # Generate suggestions based on prediction value, weather, and location
    if prediction_value < 15:
        # Low production - focus on improvement
        suggestions.append(f"Current prediction of {prediction_value:.1f} kg/hectare indicates soil nutrient deficiency. Apply organic compost and balanced NPK fertilizer (20:20:20) at 150kg/ha to boost tea plant health.")
        suggestions.append(f"With temperature at {temp:.1f}°C and {humidity:.0f}% humidity, implement micro-irrigation to maintain optimal soil moisture. Tea plants require consistent moisture for healthy growth.")
        suggestions.append(f"Conduct soil pH testing - tea thrives in pH 4.5-5.5. If pH is above 5.5, apply sulfur or aluminum sulfate to acidify soil for better nutrient uptake.")
        suggestions.append(f"Schedule light pruning to remove dead and diseased branches. This improves air circulation and stimulates new growth, essential for low-yielding tea bushes.")
        suggestions.append(f"Monitor for red spider mite and tea mosquito bug common in {month}th month. Apply neem-based organic pesticides at 2ml/liter for eco-friendly pest control.")
    elif prediction_value < 25:
        # Medium production - focus on optimization
        suggestions.append(f"Prediction of {prediction_value:.1f} kg/hectare shows good potential. Apply nitrogen fertilizer (urea) at 100kg/ha during active growth to enhance leaf production and quality.")
        suggestions.append(f"Current {temp:.1f}°C temperature is ideal for tea. Implement shade management using Grevillea trees to regulate temperature and reduce heat stress during peak afternoon hours.")
        suggestions.append(f"With {humidity:.0f}% humidity, ensure proper drainage to prevent root rot. Install contour drains on slopes to manage water flow during heavy rainfall periods.")
        suggestions.append(f"Schedule medium pruning to maintain bush height at 60-75cm. This optimal height facilitates easy harvesting and promotes lateral branching for increased yield.")
        suggestions.append(f"Implement integrated nutrient management - combine chemical fertilizers with vermicompost at 5 tonnes/ha to improve soil structure and microbial activity.")
    else:
        # High production - focus on maintenance and quality
        suggestions.append(f"Excellent prediction of {prediction_value:.1f} kg/hectare! Maintain current fertilization schedule. Apply potassium-rich fertilizer to enhance leaf quality and tea flavor profile.")
        suggestions.append(f"At {temp:.1f}°C, ensure adequate irrigation during dry spells. Use drip irrigation to deliver 4-6 liters per plant daily for consistent high-quality leaf production.")
        suggestions.append(f"High humidity ({humidity:.0f}%) increases disease risk. Implement proper spacing (1.2m x 0.75m) and regular weeding to improve air circulation and prevent fungal infections.")
        suggestions.append(f"Schedule harvesting at 7-10 day intervals during peak season. Pluck two leaves and a bud for premium quality tea that commands better market prices.")
        suggestions.append(f"Monitor market trends and consider value addition. Process fresh leaves into orthodox or CTC tea based on market demand to maximize revenue from high production.")
    
    # Add location-specific advice
    if location['latitude'] > 25:
        suggestions[0] = suggestions[0].replace("tea plants", "high-altitude tea plants").replace("tea thrives", "high-altitude tea thrives")
        suggestions.append(f"Your location at {location_name} is ideal for premium tea. High altitude produces slow-growing leaves with concentrated flavor - market as specialty tea.")
    
    # Return suggestions without images
    suggestions_list = []
    for i, suggestion in enumerate(suggestions[:5]):
        suggestions_list.append({
            "text": suggestion
        })
    
    print(f"✅ Dynamic suggestions generated: {len(suggestions_list)} recommendations")
    return {
        "status": "success",
        "suggestions": suggestions_list
    }

def get_rule_based_suggestions(prediction_value, location, weather_data, month):
    """Fallback rule-based suggestions"""
    print(f"🤖 Using rule-based tea suggestions (fallback)...")
    
    # Rule-based suggestions based on prediction value
    suggestions = []
    if prediction_value < 15:
        suggestions = [
            "Conduct comprehensive soil testing to identify nutrient deficiencies",
            "Implement organic matter application to improve soil structure",
            "Ensure proper drainage to prevent waterlogging",
            "Apply balanced NPK fertilizer based on soil test results",
            "Monitor pest activity and implement integrated pest management"
        ]
    elif prediction_value < 25:
        suggestions = [
            "Optimize irrigation schedule based on weather conditions",
            "Apply nitrogen fertilizer during active growth periods",
            "Implement mulching to conserve soil moisture",
            "Regular pruning to maintain bush health and productivity",
            "Monitor for common tea pests and diseases"
        ]
    else:
        suggestions = [
            "Maintain current fertilization schedule for optimal yield",
            "Continue regular irrigation during dry periods",
            "Implement shade management for temperature control",
            "Schedule harvesting at peak maturity for best quality",
            "Monitor market conditions for optimal selling timing"
        ]
    
    # Add tea images
    tea_images = [
        "https://images.unsplash.com/photo-1556807668-9c27f0095a76?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1592419044706-39796d40f98c?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1596395817764-7923b0644d6b?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1596484552834-6a58f850e0a3?w=400&h=300&fit=crop",
        "https://images.unsplash.com/photo-1596484636767-5a839c70e3a5?w=400&h=300&fit=crop"
    ]
    
    suggestions_with_images = []
    for i, suggestion in enumerate(suggestions[:5]):
        suggestions_with_images.append({
            "text": suggestion,
            "image": tea_images[i % len(tea_images)]
        })
    
    return {
        "status": "success",
        "suggestions": suggestions_with_images
    }

# ================= WEATHER API AND FEATURE CALCULATION =================
def get_weather_data(lat, lon):
    """Get real weather data from OpenWeatherMap API"""
    try:
        # Use a free weather API or provide your API key here
        api_key = "73a6f3c63d70a1c1ecf94336697cd132"  # OpenWeatherMap API key
        
        if api_key == "YOUR_OPENWEATHERMAP_API_KEY":
            print("⚠️  Weather API key not configured - using calculated values")
            return None
        
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        
        print(f"🌐 Calling Weather API: {url}")
        response = requests.get(url, timeout=10)
        print(f"🌐 Weather API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"🌐 Weather API Response Data: {data}")
            weather = {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'rainfall': data.get('rain', {}).get('1h', 0) * 24,  # Convert hourly to daily
                'wind_speed': data['wind']['speed'],
                'pressure': data['main']['pressure'],
                'solar_radiation': 15 + (data.get('clouds', {}).get('all', 50) / 100) * 10
            }
            print(f"✅ Real weather data fetched for {lat}, {lon}: T={weather['temperature']}°C, H={weather['humidity']}%, W={weather['wind_speed']}m/s")
            return weather
        else:
            print(f"❌ Weather API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Weather API exception: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_dataset_features(lat, lon, month, weather_data):
    """Calculate features matching the actual dataset structure (18 columns)"""
    import math

    # Use real weather data if available, otherwise use calculated values
    if weather_data:
        temperature = weather_data.get('temperature', 25.0)
        precipitation = weather_data.get('rainfall', 5.0)
        humidity = weather_data.get('humidity', 70.0)
        wind_speed = weather_data.get('wind_speed', 10.0)
        solar_radiation = weather_data.get('solar_radiation', 15.0)
        print(f"🌤️  Using REAL weather data: T={temperature}°C, H={humidity}%, R={precipitation}mm/day")
    else:
        print("⚠️  Weather API not available, using calculated values")
        # Calculate realistic weather based on location and month
        temperature = 25 + (month - 6) * 2 + (lat * 0.1)  # Seasonal variation
        precipitation = 5 + (month % 12) * 2  # Monthly variation
        humidity = 60 + (month % 12) * 3  # Monthly variation
        wind_speed = 8 + (month % 12)  # Monthly variation
        solar_radiation = 15 + (month % 12) * 2  # Monthly variation
        print(f"🌤️  Using CALCULATED weather data: T={temperature}°C, H={humidity}%, R={precipitation}mm/day")
    
    # Elevation based on latitude (dataset has 120-140m range)
    elevation = 120 + abs(lat) * 2 + (month % 12) * 2
    
    # Month cyclical encoding (as in dataset)
    month_rad = (month - 1) * (2 * math.pi / 12)
    month_sin = math.sin(month_rad)
    month_cos = math.cos(month_rad)
    
    # Heat Index (simplified formula)
    heat_index = temperature + (humidity / 100) * 10
    
    # Feature interactions (as in dataset)
    temp_humidity = temperature * humidity
    rainfall_humidity = precipitation * humidity
    temp_solar = temperature * solar_radiation
    
    # Historical production values (use reasonable estimates based on dataset)
    # Dataset ranges: 20-40 metric tons
    prev_month_production = 25 + (month % 12) * 1.5
    prev_2month_production = 23 + (month % 12) * 1.3
    rolling_3month_avg = 24 + (month % 12) * 1.4
    
    # State encoding (based on longitude - dataset has 0-6)
    # Map longitude ranges to state codes
    if lon < 89:
        state_encoded = 0
    elif lon < 90:
        state_encoded = 1
    elif lon < 91:
        state_encoded = 2
    elif lon < 92:
        state_encoded = 3
    else:
        state_encoded = 4
    
    features = {
        'Temperature_C': temperature,
        'Precipitation_mm_day': precipitation,
        'Humidity_Percent': humidity,
        'Solar_Radiation_MJ_m2_day': solar_radiation,
        'Latitude': lat,
        'Longitude': lon,
        'Elevation_m': elevation,
        'Month_Sin': month_sin,
        'Month_Cos': month_cos,
        'Heat_Index': heat_index,
        'Temp_Humidity': temp_humidity,
        'Rainfall_Humidity': rainfall_humidity,
        'Temp_Solar': temp_solar,
        'Prev_Month_Production': prev_month_production,
        'Prev_2Month_Production': prev_2month_production,
        'Rolling_3Month_Avg': rolling_3month_avg,
        'State_Encoded': state_encoded
    }
    
    return features

# ================= TEA PREDICTION ENDPOINT =================
@app.route('/tea-predict', methods=['POST'])
def tea_predict():
    try:
        print("\n🍵 === TEA PREDICTION ENDPOINT ===")
        
        # Validate Tea Model is loaded
        if tea_model is None:
            return jsonify({
                'error': 'Tea prediction model not loaded',
                'status': 'error'
            }), 500
        
        # Get input data
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No input data provided',
                'status': 'error'
            }), 400
        
        print(f"📊 Received data keys: {list(data.keys())}")
        
        # Extract location and time data
        lat = float(data.get('latitude', 0))
        lon = float(data.get('longitude', 0))
        month = int(data.get('month', 6))
        
        print(f"🌍 Location: {lat}, {lon}")
        print(f"📅 Month: {month}")
        
        # Get weather data
        print("🌤️ Fetching weather data...")
        weather_data = get_weather_data(lat, lon)
        
        # Calculate dataset features (18 columns from actual dataset)
        print("🧮 Calculating dataset features...")
        calculated_features = calculate_dataset_features(lat, lon, month, weather_data)
        
        print(f"🌤️ Weather Data: {weather_data}")
        print(f"🧮 Dataset Features: {calculated_features}")
        
        # Define the 18 features in correct order (matching dataset columns)
        dataset_features = [
            'Temperature_C', 'Precipitation_mm_day', 'Humidity_Percent', 'Solar_Radiation_MJ_m2_day',
            'Latitude', 'Longitude', 'Elevation_m', 'Month_Sin', 'Month_Cos', 'Heat_Index',
            'Temp_Humidity', 'Rainfall_Humidity', 'Temp_Solar', 'Prev_Month_Production',
            'Prev_2Month_Production', 'Rolling_3Month_Avg', 'State_Encoded'
        ]
        
        # Create feature array in correct order
        features = []
        for feature in dataset_features:
            features.append(float(calculated_features[feature]))
        
        features = np.array(features).reshape(1, -1)
        
        print(f"🔢 Tea Model Input Shape: {features.shape}")
        print(f"🔢 Tea Model Input Features: {features[0]}")
        
        # Validate feature count (should be 17 for model, excluding target variable)
        if features.shape[1] != 17:
            return jsonify({
                'error': f'Feature shape mismatch for tea model: expected 17, got {features.shape[1]}',
                'status': 'error'
            }), 400
        
        # Make prediction using tea model
        prediction = tea_model.predict(features)
        print(f"🍵 Tea Model Prediction: {prediction}")
        
        # Get AI-powered suggestions
        print("🤖 Generating AI suggestions...")
        location_data = {'latitude': lat, 'longitude': lon}
        ai_suggestions = get_tea_suggestions(float(prediction[0]), location_data, weather_data or {}, month)
        
        response = {
            'status': 'success',
            'model_used': 'tea_prediction',
            'features_count': features.shape[1],
            'prediction': float(prediction[0]),
            'location': {
                'latitude': lat,
                'longitude': lon,
                'month': month
            },
            'weather_data': weather_data,
            'calculated_features': calculated_features,
            'all_features': {feature: calculated_features[feature] for feature in dataset_features},
            'feature_details': {
                'weather_primary': ['Temperature_C', 'Precipitation_mm_day', 'Humidity_Percent', 'Solar_Radiation_MJ_m2_day'],
                'location': ['Latitude', 'Longitude', 'Elevation_m', 'State_Encoded'],
                'temporal': ['Month_Sin', 'Month_Cos'],
                'derived_indices': ['Heat_Index'],
                'feature_interactions': ['Temp_Humidity', 'Rainfall_Humidity', 'Temp_Solar'],
                'historical_production': ['Prev_Month_Production', 'Prev_2Month_Production', 'Rolling_3Month_Avg']
            },
            'ai_suggestions': ai_suggestions
        }
        
        print(f"✅ Tea prediction completed: {prediction[0]}")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Tea prediction error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

# ================= HEALTH CHECK ENDPOINT =================
@app.route('/health', methods=['GET'])
def health_check():
    response = {
        'status': 'healthy',
        'service': 'tea_prediction',
        'model': {
            'tea_model': {
                'loaded': tea_model is not None,
                'features_expected': 17 if tea_model else None
            }
        },
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(response)

# ================= MAIN APPLICATION =================
if __name__ == '__main__':
    print("🍵 Starting Tea Prediction Server...")
    print("🌐 Server starting on http://127.0.0.1:5002")
    print("🌐 Tea Prediction endpoint: POST /tea-predict")
    try:
        app.run(debug=True, host='0.0.0.0', port=5002)
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        print("🔧 Try running: python tea_prediction.py")
        print("🔧 Or check if port 5002 is already in use")
