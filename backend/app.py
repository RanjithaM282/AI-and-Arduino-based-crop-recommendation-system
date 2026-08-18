import os
import pickle
import socket
import sys
import numpy as np
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
from database.db import db, init_db
from models import Farmer, Farm
from ai_service import generate_ai_suggestions

load_dotenv()

app = Flask(__name__)
CORS(app)

database_url = os.getenv('DATABASE_URL', 'sqlite:///smart_farmer.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"🗄️  Database URL: {database_url.split('@')[1] if '@' in database_url else database_url}")

init_db(app)

# ================= CROP MODEL LOADING =================
print("🌱 Crop Recommendation System (ML-Based)")
print("   Loading trained machine learning model for crop recommendation")

crop_model_path = os.path.join(os.path.dirname(__file__), '..', 'crop_recommendation_model', 'crop_model.pkl')
crop_model = None

MODEL_FEATURES = ['nitrogen', 'phosphorus', 'potassium', 'ph', 'temperature', 'humidity']
REQUIRED_INPUTS = MODEL_FEATURES + ['soil_moisture']
MAX_RECOMMENDATIONS = 5

try:
    with open(crop_model_path, 'rb') as f:
        crop_model = pickle.load(f)
    print(f"✅ Crop ML Model loaded: {crop_model_path}")
    print(f"   Model type: {type(crop_model)}")
    if not hasattr(crop_model, 'classes_') or not hasattr(crop_model, 'predict_proba'):
        raise ValueError('Loaded model is not a classifier with crop labels.')
    print(f"   Crops known to the model: {list(crop_model.classes_)}")
    if hasattr(crop_model, 'n_features_in_'):
        print(f"   Model expects {crop_model.n_features_in_} features")
except Exception as e:
    print(f"❌ Crop ML Model load error: {e}")
    crop_model = None

def suitability_label(score):
    """Bucket a model probability into a human readable suitability rating"""
    if score >= 0.7:
        return 'Excellent'
    if score >= 0.5:
        return 'Good'
    if score >= 0.3:
        return 'Moderate'
    return 'Poor'

def get_crop_fertilizer_suggestions(crop_name, soil_data, environmental_data):
    """Generate real AI fertilizer and crop management suggestions."""
    system_prompt = (
        "You are an expert agronomist helping Indian farmers. "
        "Give practical fertilizer and crop management advice. Keep each suggestion under 30 words."
    )
    user_prompt = f"""
Recommended crop: {crop_name}
Nitrogen (mg/kg): {soil_data.get('nitrogen')}
Phosphorus (mg/kg): {soil_data.get('phosphorus')}
Potassium (mg/kg): {soil_data.get('potassium')}
Soil pH: {soil_data.get('ph')}
Temperature (C): {environmental_data.get('temperature')}
Humidity (%): {environmental_data.get('humidity')}
Soil moisture (%): {environmental_data.get('soil_moisture')}

Write exactly 5 numbered fertilizer and crop management recommendations for {crop_name}.
Include specific actions for the soil and climate values above.
"""
    return generate_ai_suggestions(system_prompt, user_prompt, max_items=5)

# ================= ARDUINO SENSOR DATA =================
arduino_data = {
    'temperature': None,
    'humidity': None,
    'soil_moisture': None,
    'timestamp': None
}

arduino_connection_status = {
    'connected': False,
    'message': 'Not connected',
    'port': None,
    'last_update': None
}

def read_arduino():
    global arduino_data, arduino_connection_status
    
    print("🔌 Arduino reading thread started")
    ser = None
    connected_port = None
    
    try:
        import serial
        import serial.tools.list_ports
        import json
        
        while True:
            try:
                available_ports = serial.tools.list_ports.comports()
                print(f"Available COM ports: {[p.device for p in available_ports]}")
                
                if not available_ports:
                    arduino_connection_status['connected'] = False
                    arduino_connection_status['message'] = 'No COM ports available'
                    time.sleep(5)
                    continue
                
                ports_to_try = []
                for port_info in available_ports:
                    if port_info.device == 'COM3':
                        ports_to_try.insert(0, port_info.device)
                    else:
                        ports_to_try.append(port_info.device)
                
                print(f"🔌 Will try ports in order: {ports_to_try}")
                
                for port in ports_to_try:
                    try:
                        print(f"🔌 Attempting to connect to {port} at 9600 baud...")
                        ser = serial.Serial(
                            port=port,
                            baudrate=9600,
                            timeout=2,
                            write_timeout=2,
                            xonxoff=False,
                            rtscts=False,
                            dsrdtr=False
                        )
                        connected_port = port
                        time.sleep(3)
                        ser.reset_input_buffer()
                        
                        arduino_connection_status['connected'] = True
                        arduino_connection_status['message'] = f'Arduino connected successfully on {port} at 9600 baud'
                        arduino_connection_status['port'] = port
                        print(f"✅ Arduino connected successfully on {port} at 9600 baud")
                        break
                    except PermissionError as e:
                        print(f"⚠️  {port} is busy (Permission denied).")
                        if ser is not None:
                            try:
                                ser.close()
                            except Exception:
                                pass
                        ser = None
                        connected_port = None
                        continue
                    except Exception as e:
                        print(f"❌ Failed to open {port}: {e}")
                        if ser is not None:
                            try:
                                ser.close()
                            except Exception:
                                pass
                        ser = None
                        connected_port = None
                        continue
                
                if ser is None or connected_port is None:
                    arduino_connection_status['connected'] = False
                    arduino_connection_status['message'] = 'Failed to connect to Arduino'
                    time.sleep(5)
                    continue
                
                while True:
                    try:
                        if ser.in_waiting > 0:
                            line = ser.readline().decode('utf-8', errors='ignore').strip()
                            if line:
                                try:
                                    data = json.loads(line)
                                    if 'temperature' in data:
                                        arduino_data['temperature'] = data['temperature']
                                    if 'humidity' in data:
                                        arduino_data['humidity'] = data['humidity']
                                    if 'soil_moisture' in data:
                                        arduino_data['soil_moisture'] = data['soil_moisture']
                                    arduino_connection_status['connected'] = True
                                    arduino_connection_status['message'] = 'Arduino connected and receiving real data'
                                    arduino_connection_status['last_update'] = datetime.now().isoformat()
                                    print(f"✅ Arduino data updated: {arduino_data}")
                                except json.JSONDecodeError:
                                    import re
                                    if ':' in line:
                                        parts = line.split(':')
                                        if len(parts) >= 2:
                                            key = parts[0].strip().lower().replace(' ', '_')
                                            value_part = parts[1].strip()
                                            value_match = re.search(r'[\d.]+', value_part)
                                            if value_match:
                                                value = float(value_match.group())
                                                if 'temperature' in key:
                                                    arduino_data['temperature'] = value
                                                elif 'humidity' in key:
                                                    arduino_data['humidity'] = value
                                                elif 'soil_moisture' in key:
                                                    arduino_data['soil_moisture'] = value
                                                arduino_connection_status['connected'] = True
                                                arduino_connection_status['message'] = 'Arduino connected and receiving real data'
                                                arduino_connection_status['last_update'] = datetime.now().isoformat()
                        time.sleep(0.1)
                    except Exception as read_error:
                        print(f"❌ Arduino read error: {read_error}")
                        arduino_connection_status['connected'] = False
                        try:
                            ser.close()
                        except Exception:
                            pass
                        ser = None
                        break
            except Exception as e:
                print(f"❌ Arduino thread error: {e}")
                arduino_connection_status['connected'] = False
                time.sleep(5)
    finally:
        if ser is not None:
            try:
                ser.close()
            except Exception:
                pass
        print("🔌 Arduino connection closed")

def init_arduino():
    try:
        print("Starting Arduino periodic reading...")
        threading.Thread(target=read_arduino, daemon=True).start()
        print("Arduino reading thread started")
    except Exception as e:
        print(f"Arduino initialization error: {e}")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Smart Farmer API is running',
        'model_loaded': crop_model is not None,
        'arduino_status': arduino_connection_status
    })

@app.route('/api/farmers', methods=['POST'])
def create_farmer():
    try:
        data = request.get_json()
        farmer = Farmer(
            name=data['name'],
            phone=data['phone'],
            state=data['state'],
            district=data['district'],
            taluk=data.get('taluk'),
            village=data.get('village'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        db.session.add(farmer)
        db.session.commit()
        return jsonify({'status': 'success', 'farmer': farmer.to_dict()}), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ================= CROP RECOMMENDATION ENDPOINT =================
@app.route('/crop-recommend', methods=['POST'])
def crop_recommend():
    try:
        print("\n🌱 === CROP RECOMMENDATION ENDPOINT (ML-BASED) ===")
        
        if crop_model is None:
            return jsonify({
                'error': 'ML model not loaded.',
                'status': 'error',
                'arduino_status': arduino_connection_status
            }), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided', 'status': 'error'}), 400
        
        missing_features = [f for f in REQUIRED_INPUTS if f not in data]
        if missing_features:
            return jsonify({
                'error': f'Missing required features: {missing_features}',
                'required_features': REQUIRED_INPUTS,
                'status': 'error',
                'arduino_status': arduino_connection_status
            }), 400
        
        features = np.array([float(data.get(feature)) for feature in MODEL_FEATURES]).reshape(1, -1)
        print(f"🔢 ML Model Input: {features[0]}")
        
        probabilities = crop_model.predict_proba(features)[0]
        crop_classes = [str(c) for c in crop_model.classes_]
        
        ranked = sorted(zip(crop_classes, probabilities), key=lambda pair: pair[1], reverse=True)[:MAX_RECOMMENDATIONS]
        ranked = [(name, score) for name, score in ranked if score > 0]
        
        crop_recommendations = [
            {
                'name': name.title(),
                'score': round(float(score), 4),
                'suitability': suitability_label(float(score))
            }
            for name, score in ranked
        ]
        
        top_crop = crop_recommendations[0]['name']
        print(f"✅ ML Model Recommended Crop: {top_crop}")
        
        soil_data = {
            'nitrogen': data.get('nitrogen'),
            'phosphorus': data.get('phosphorus'),
            'potassium': data.get('potassium'),
            'ph': data.get('ph')
        }
        environmental_data = {
            'temperature': data.get('temperature'),
            'humidity': data.get('humidity'),
            'soil_moisture': data.get('soil_moisture')
        }
        
        ai_suggestions = get_crop_fertilizer_suggestions(top_crop, soil_data, environmental_data)
        
        response = {
            'status': 'success',
            'model_used': 'machine_learning',
            'prediction': top_crop,
            'crop_recommendations': crop_recommendations,
            'top_recommendation': top_crop,
            'input_data': {
                'nitrogen_mg_kg': data.get('nitrogen'),
                'phosphorus_mg_kg': data.get('phosphorus'),
                'potassium_mg_kg': data.get('potassium'),
                'ph_value': data.get('ph'),
                'temperature_c': data.get('temperature'),
                'humidity_percent': data.get('humidity'),
                'soil_moisture_percent': data.get('soil_moisture')
            },
            'arduino_status': arduino_connection_status,
            'ai_suggestions': ai_suggestions
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Crop recommendation error: {e}")
        return jsonify({'error': str(e), 'status': 'error', 'arduino_status': arduino_connection_status}), 500

# ================= SENSOR DATA ENDPOINT =================
@app.route('/sensor', methods=['GET'])
def get_sensor_data():
    try:
        response = {
            'status': 'success',
            'arduino_data': arduino_data,
            'arduino_status': arduino_connection_status,
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error', 'arduino_status': arduino_connection_status}), 500

if __name__ == '__main__':
    print("🌱 Smart Farmer API starting...")
    init_arduino()
    app.run(host='0.0.0.0', port=5001, debug=True)
