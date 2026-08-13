import os
import pickle
import socket
import sys
import numpy as np
import threading
import time
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ================= CROP MODEL LOADING =================
print("🌱 Crop Recommendation System (ML-Based)")
print("   Loading trained machine learning model for crop recommendation")

crop_model_path = os.path.join(os.path.dirname(__file__), '..', 'crop_recommendation_model', 'crop_model.pkl')
crop_model = None

# Feature order the model was trained on (see crop_recommendation_model/train_crop_model.py).
# Soil moisture is collected from the Arduino but is not a model feature: the training
# data records rainfall, not soil moisture, so it is used for irrigation advice only.
MODEL_FEATURES = ['nitrogen', 'phosphorus', 'potassium', 'ph', 'temperature', 'humidity']
REQUIRED_INPUTS = MODEL_FEATURES + ['soil_moisture']
MAX_RECOMMENDATIONS = 5

try:
    with open(crop_model_path, 'rb') as f:
        crop_model = pickle.load(f)
    print(f"✅ Crop ML Model loaded: {crop_model_path}")
    print(f"   Model type: {type(crop_model)}")
    if not hasattr(crop_model, 'classes_') or not hasattr(crop_model, 'predict_proba'):
        raise ValueError(
            'Loaded model is not a classifier with crop labels. '
            'Retrain it with crop_recommendation_model/train_crop_model.py'
        )
    print(f"   Crops known to the model: {list(crop_model.classes_)}")
    if hasattr(crop_model, 'n_features_in_'):
        print(f"   Model expects {crop_model.n_features_in_} features")
except Exception as e:
    print(f"❌ Crop ML Model load error: {e}")
    print("   System will not function without the ML model!")
    crop_model = None

def suitability_label(score):
    """Bucket a model probability into a human readable suitability rating"""
    if score >= 0.7:
        return 'Good'
    if score >= 0.4:
        return 'Moderate'
    return 'Poor'

# ================= AI SUGGESTIONS =================
# Using rule-based suggestions for reliability

def get_crop_fertilizer_suggestions(crop_name, soil_data, environmental_data):
    """Generate fertilizer and crop management suggestions using rule-based approach"""
    print(f"🤖 Using rule-based crop suggestions for {crop_name}...")
    
    nitrogen = soil_data.get('nitrogen', 50)
    phosphorus = soil_data.get('phosphorus', 35)
    potassium = soil_data.get('potassium', 52)
    ph = soil_data.get('ph', 6.5)
    temperature = environmental_data.get('temperature', 25)
    humidity = environmental_data.get('humidity', 60)
    
    # Rule-based suggestions based on soil conditions
    suggestions = []
    
    if nitrogen < 40:
        suggestions.append(f"Apply nitrogen-rich fertilizer to boost {crop_name} growth")
    if phosphorus < 30:
        suggestions.append(f"Add phosphorus fertilizer to support root development in {crop_name}")
    if potassium < 40:
        suggestions.append(f"Supplement potassium for improved {crop_name} disease resistance")
    if ph < 6.0:
        suggestions.append(f"Apply lime to raise soil pH for optimal {crop_name} growth")
    elif ph > 7.5:
        suggestions.append(f"Apply sulfur to lower soil pH for {crop_name}")
    
    if temperature > 30:
        suggestions.append(f"Implement shade or mulching to protect {crop_name} from heat stress")
    if humidity < 40:
        suggestions.append(f"Increase irrigation frequency due to low humidity conditions")
    
    # Add general suggestions if we don't have enough
    if len(suggestions) < 5:
        suggestions.extend([
            f"Monitor soil moisture levels regularly for {crop_name}",
            f"Conduct soil testing before major fertilizer applications",
            f"Follow local agricultural extension guidelines for {crop_name}",
            f"Adjust fertilizer based on {crop_name} growth stage",
            f"Implement crop rotation to maintain soil health"
        ])
    
    return {
        "status": "success",
        "suggestions": suggestions[:5]  # Limit to 5 suggestions
    }

# ================= ARDUINO SENSOR DATA =================
arduino_data = {
    'temperature': None,
    'humidity': None,
    'soil_moisture': None
}

arduino_connection_status = {
    'connected': False,
    'message': 'Not initialized',
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

        # Find available COM ports
        available_ports = serial.tools.list_ports.comports()
        print(f"Available COM ports: {[p.device for p in available_ports]}")

        if not available_ports:
            arduino_connection_status['connected'] = False
            arduino_connection_status['message'] = 'No COM ports available'
            print("❌ No COM ports available")
            return

        # Look for COM3 first, but try all ports
        ports_to_try = []

        for port_info in available_ports:
            if port_info.device == 'COM3':
                ports_to_try.insert(0, port_info.device)
            else:
                ports_to_try.append(port_info.device)

        print(f"🔌 Will try ports in order: {ports_to_try}")

        # Connect using the Arduino's actual baud rate
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

                # Opening Serial resets most Arduino Uno boards.
                time.sleep(3)

                # Clear anything already waiting
                ser.reset_input_buffer()

                arduino_connection_status['connected'] = True
                arduino_connection_status['message'] = (
                    f'Arduino connected successfully on {port} at 9600 baud'
                )
                arduino_connection_status['port'] = port

                print(f"✅ Arduino connected successfully on {port} at 9600 baud")
                break

            except PermissionError as e:
                print(f"⚠️  {port} is busy (Permission denied). Another program may be using it.")
                print(f"   Close Arduino IDE Serial Monitor or other serial applications and try again.")
                if ser is not None:
                    try:
                        ser.close()
                    except Exception:
                        pass
                ser = None
                connected_port = None
                continue  # Try next port

            except Exception as e:
                print(f"❌ Failed to open {port}: {e}")
                if ser is not None:
                    try:
                        ser.close()
                    except Exception:
                        pass
                ser = None
                connected_port = None
                continue  # Try next port

        # No connection
        if ser is None or connected_port is None:
            arduino_connection_status['connected'] = False
            arduino_connection_status['message'] = (
                'Failed to connect to Arduino on any available port'
            )
            print("❌ Failed to connect to Arduino on any available port")
            return

        print("📡 Starting continuous Arduino data reading...")

        # Continuously read Arduino JSON data
        while True:

            try:
                if ser.in_waiting > 0:

                    line = ser.readline().decode('utf-8', errors='ignore').strip()

                    if line:
                        print(f"📥 Raw Arduino data: {line}")

                        try:
                            data = json.loads(line)

                            # Only update valid sensor fields
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
                            # Try to parse simple format: "Temperature: 28.30 C"
                            if ':' in line:
                                try:
                                    # Remove units and extract value
                                    parts = line.split(':')
                                    if len(parts) >= 2:
                                        key = parts[0].strip().lower().replace(' ', '_')
                                        value_part = parts[1].strip()
                                        
                                        # Extract numeric value (remove units like C, %)
                                        import re
                                        value_match = re.search(r'[\d.]+', value_part)
                                        if value_match:
                                            value = float(value_match.group())
                                            
                                            # Map Arduino keys to our data structure
                                            if 'temperature' in key:
                                                arduino_data['temperature'] = value
                                                print(f"✅ Temperature updated: {value}")
                                            elif 'humidity' in key:
                                                arduino_data['humidity'] = value
                                                print(f"✅ Humidity updated: {value}")
                                            elif 'soil_moisture' in key:
                                                arduino_data['soil_moisture'] = value
                                                print(f"✅ Soil Moisture updated: {value}")
                                            
                                            arduino_connection_status['connected'] = True
                                            arduino_connection_status['message'] = 'Arduino connected and receiving real data'
                                            arduino_connection_status['last_update'] = datetime.now().isoformat()
                                except Exception as parse_error:
                                    print(f"⚠️ Failed to parse simple format: {parse_error}")
                            else:
                                print(f"⚠️ Ignoring unparseable Arduino line: {line}")

                time.sleep(0.1)

            except Exception as read_error:

                print(f"❌ Arduino read error: {read_error}")

                arduino_connection_status['connected'] = False
                arduino_connection_status['message'] = (
                    f'Arduino connection lost: {str(read_error)}'
                )

                try:
                    ser.close()
                except Exception:
                    pass

                ser = None

                # Try reconnecting
                while ser is None:

                    try:
                        print(f"🔄 Trying to reconnect to {connected_port}...")

                        ser = serial.Serial(
                            port=connected_port,
                            baudrate=9600,
                            timeout=2,
                            write_timeout=2,
                            xonxoff=False,
                            rtscts=False,
                            dsrdtr=False
                        )

                        time.sleep(3)
                        ser.reset_input_buffer()

                        arduino_connection_status['connected'] = True
                        arduino_connection_status['message'] = (
                            f'Arduino reconnected on {connected_port}'
                        )
                        arduino_connection_status['port'] = connected_port

                        print(f"✅ Arduino reconnected on {connected_port}")

                    except Exception as reconnect_error:

                        print(f"❌ Reconnection failed: {reconnect_error}")

                        arduino_connection_status['connected'] = False
                        arduino_connection_status['message'] = (
                            'Arduino reconnection failed'
                        )

                        time.sleep(3)

    except Exception as e:

        print(f"❌ Arduino thread error: {e}")

        arduino_connection_status['connected'] = False
        arduino_connection_status['message'] = (
            f'Arduino initialization error: {str(e)}'
        )

    finally:

        if ser is not None:
            try:
                ser.close()
            except Exception:
                pass

        print("🔌 Arduino connection closed")

def init_arduino():
    try:
        # Start periodic Arduino reading
        print("Starting Arduino periodic reading...")
        threading.Thread(target=read_arduino, daemon=True).start()
        print("Arduino reading thread started")

    except Exception as e:
        print(f"Arduino initialization error: {e}")

# ================= CROP RECOMMENDATION ENDPOINT =================
@app.route('/crop-recommend', methods=['POST'])
def crop_recommend():
    try:
        print("\n🌱 === CROP RECOMMENDATION ENDPOINT (ML-BASED) ===")
        
        # Validate ML model is loaded
        if crop_model is None:
            return jsonify({
                'error': 'ML model not loaded. Cannot make predictions without trained model.',
                'status': 'error',
                'arduino_status': arduino_connection_status
            }), 500
        
        # Get input data
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No input data provided',
                'status': 'error'
            }), 400
        
        print(f"📊 Received data keys: {list(data.keys())}")
        
        # Validate all inputs are present
        missing_features = [f for f in REQUIRED_INPUTS if f not in data]
        if missing_features:
            return jsonify({
                'error': f'Missing required features for crop recommendation: {missing_features}',
                'required_features': REQUIRED_INPUTS,
                'received_features': list(data.keys()),
                'status': 'error',
                'arduino_status': arduino_connection_status
            }), 400
        
        # Validate Arduino data is available (no simulation allowed)
        if arduino_data.get('temperature') is None or \
           arduino_data.get('humidity') is None or \
           arduino_data.get('soil_moisture') is None:
            return jsonify({
                'error': 'Arduino sensor data not available. Real Arduino connection required - no simulation allowed.',
                'arduino_status': arduino_connection_status,
                'status': 'error'
            }), 400
        
        # Create feature array in the order the model was trained on
        features = np.array(
            [float(data.get(feature)) for feature in MODEL_FEATURES]
        ).reshape(1, -1)
        
        print(f"🔢 ML Model Input Shape: {features.shape}")
        print(f"🔢 ML Model Input Features: {features[0]}")
        
        # Validate feature count matches model expectations
        if hasattr(crop_model, 'n_features_in_'):
            if features.shape[1] != crop_model.n_features_in_:
                return jsonify({
                    'error': f'Feature shape mismatch: model expects {crop_model.n_features_in_}, got {features.shape[1]}',
                    'status': 'error',
                    'arduino_status': arduino_connection_status
                }), 400
        
        # Make prediction using ML model
        print("🤖 Making prediction with ML model...")
        probabilities = crop_model.predict_proba(features)[0]
        crop_classes = [str(c) for c in crop_model.classes_]

        ranked = sorted(
            zip(crop_classes, probabilities), key=lambda pair: pair[1], reverse=True
        )[:MAX_RECOMMENDATIONS]
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
        print(f"✅ ML Model Recommended Crop: {top_crop} ({crop_recommendations[0]['score']:.2%})")
        
        # Generate AI fertilizer suggestions for recommended crop
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
            'model_type': str(type(crop_model).__name__),
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
        
        print(f"✅ Crop recommendation completed: {top_crop}")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Crop recommendation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'status': 'error',
            'arduino_status': arduino_connection_status
        }), 500

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
        return jsonify({
            'error': str(e),
            'status': 'error',
            'arduino_status': arduino_connection_status
        }), 500

# ================= HEALTH CHECK ENDPOINT =================
@app.route('/health', methods=['GET'])
def health_check():
    response = {
        'status': 'healthy',
        'service': 'crop_recommendation',
        'model': {
            'type': 'machine_learning',
            'model_type': str(type(crop_model).__name__) if crop_model else 'Not loaded',
            'loaded': crop_model is not None,
            'features_expected': MODEL_FEATURES,
            'crops': [str(c) for c in crop_model.classes_] if crop_model is not None else []
        },
        'arduino_status': arduino_connection_status,
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(response)

# ================= MAIN APPLICATION =================
def port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('127.0.0.1', port)) == 0


if __name__ == '__main__':
    print("🌱 Starting Crop Recommendation Server...")
    if port_in_use(5001):
        print("❌ Port 5001 is already in use - another backend is still running.")
        print("🔧 Stop it first, otherwise the browser keeps talking to the old server.")
        print("🔧 Windows: taskkill /F /IM python.exe   |  Linux/Mac: pkill -f crop_recommendation.py")
        sys.exit(1)
    init_arduino()
    print("🌐 Server starting on http://127.0.0.1:5001")
    print("🌐 Crop Recommendation endpoint: POST /crop-recommend")
    print("🌐 Arduino Sensor endpoint: GET /sensor")
    try:
        app.run(debug=False, host='0.0.0.0', port=5001)
    except Exception as e:
        print(f"❌ Server startup error: {e}")
        print("🔧 Try running: python crop_recommendation.py")
        print("🔧 Or check if port 5001 is already in use")
