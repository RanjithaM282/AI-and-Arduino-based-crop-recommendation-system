"""
Hardware Sensor Data API
Endpoints for receiving real-time sensor data from IoT devices
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()
    
    # Create sensor data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            latitude REAL,
            longitude REAL,
            temperature REAL,
            humidity REAL,
            soil_moisture REAL,
            rainfall REAL,
            light_intensity REAL,
            soil_ph REAL,
            battery_level REAL,
            data_json TEXT
        )
    ''')
    
    # Create devices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id TEXT PRIMARY KEY,
            name TEXT,
            location_name TEXT,
            latitude REAL,
            longitude REAL,
            last_seen DATETIME,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    """Receive sensor data from IoT devices"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['timestamp', 'location', 'sensors']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract data
        timestamp = datetime.fromtimestamp(data['timestamp'])
        location = data['location']
        sensors = data['sensors']
        device_id = data.get('device_id', 'unknown')
        
        # Store in database
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_data 
            (device_id, timestamp, latitude, longitude, temperature, humidity, 
             soil_moisture, rainfall, light_intensity, soil_ph, battery_level, data_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            device_id,
            timestamp,
            location.get('lat'),
            location.get('lng'),
            sensors.get('temperature'),
            sensors.get('humidity'),
            sensors.get('soil_moisture'),
            sensors.get('rainfall'),
            sensors.get('light_intensity'),
            sensors.get('soil_ph'),
            sensors.get('battery_level'),
            json.dumps(data)
        ))
        
        # Update device last seen
        cursor.execute('''
            INSERT OR REPLACE INTO devices (id, last_seen)
            VALUES (?, ?)
        ''', (device_id, datetime.now()))
        
        conn.commit()
        conn.close()
        
        # Trigger real-time prediction if needed
        trigger_prediction_if_needed(device_id, data)
        
        return jsonify({'status': 'success', 'message': 'Data received'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensor-data/latest', methods=['GET'])
def get_latest_sensor_data():
    """Get latest sensor data for all devices"""
    try:
        device_id = request.args.get('device_id')
        
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()
        
        if device_id:
            cursor.execute('''
                SELECT * FROM sensor_data 
                WHERE device_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (device_id,))
        else:
            cursor.execute('''
                SELECT s.* FROM sensor_data s
                INNER JOIN (
                    SELECT device_id, MAX(timestamp) as max_timestamp
                    FROM sensor_data
                    GROUP BY device_id
                ) latest ON s.device_id = latest.device_id 
                AND s.timestamp = latest.max_timestamp
                ORDER BY s.timestamp DESC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        columns = ['id', 'device_id', 'timestamp', 'latitude', 'longitude', 
                  'temperature', 'humidity', 'soil_moisture', 'rainfall', 
                  'light_intensity', 'soil_ph', 'battery_level', 'data_json']
        
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        return jsonify({'data': data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sensor-data/history', methods=['GET'])
def get_sensor_data_history():
    """Get historical sensor data"""
    try:
        device_id = request.args.get('device_id')
        hours = int(request.args.get('hours', 24))
        
        start_time = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM sensor_data 
            WHERE device_id = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        ''', (device_id, start_time))
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'device_id', 'timestamp', 'latitude', 'longitude', 
                  'temperature', 'humidity', 'soil_moisture', 'rainfall', 
                  'light_intensity', 'soil_ph', 'battery_level', 'data_json']
        
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        return jsonify({'data': data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get list of all registered devices"""
    try:
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.*, s.temperature, s.humidity, s.battery_level
            FROM devices d
            LEFT JOIN sensor_data s ON d.id = s.device_id
            LEFT JOIN sensor_data s2 ON s.device_id = s2.device_id AND s.timestamp < s2.timestamp
            WHERE s2.timestamp IS NULL
            ORDER BY d.last_seen DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        devices = []
        for row in rows:
            devices.append({
                'id': row[0],
                'name': row[1],
                'location_name': row[2],
                'latitude': row[3],
                'longitude': row[4],
                'last_seen': row[5],
                'status': row[6],
                'current_temperature': row[7],
                'current_humidity': row[8],
                'battery_level': row[9]
            })
        
        return jsonify({'devices': devices}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def trigger_prediction_if_needed(device_id, sensor_data):
    """Trigger prediction when new sensor data arrives"""
    try:
        # Extract relevant data for prediction
        sensors = sensor_data['sensors']
        location = sensor_data['location']
        
        # Call existing prediction endpoint
        prediction_data = {
            'latitude': location['lat'],
            'longitude': location['lng'],
            'temperature': sensors.get('temperature', 25),
            'humidity': sensors.get('humidity', 60),
            'rainfall': sensors.get('rainfall', 0),
            'month': datetime.now().month,
            'year': datetime.now().year
        }
        
        # This would call your existing prediction logic
        # For now, we'll just log it
        print(f"Triggering prediction for device {device_id} with data: {prediction_data}")
        
    except Exception as e:
        print(f"Error triggering prediction: {e}")

def cleanup_old_data():
    """Clean up old sensor data (keep last 30 days)"""
    while True:
        try:
            cutoff_time = datetime.now() - timedelta(days=30)
            
            conn = sqlite3.connect('sensor_data.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM sensor_data 
                WHERE timestamp < ?
            ''', (cutoff_time,))
            
            conn.commit()
            conn.close()
            
            print(f"Cleaned up data older than {cutoff_time}")
            
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
        
        # Run cleanup daily
        time.sleep(86400)

if __name__ == '__main__':
    init_db()
    
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_old_data, daemon=True)
    cleanup_thread.start()
    
    app.run(host='0.0.0.0', port=5001, debug=True)
