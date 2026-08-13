#!/usr/bin/env python3
"""
Quick start script for the Tea Production Prediction Backend
"""
import os
import sys

def main():
    print("🚀 Starting Tea Production Prediction Backend...")
    
    # Check if model exists
    model_path = os.path.join(os.path.dirname(__file__), 'mega_project copy', 'model.pkl')
    if not os.path.exists(model_path):
        print(f"❌ Model not found at: {model_path}")
        print("Please ensure the model.pkl file exists in the mega_project copy directory")
        sys.exit(1)
    
    print(f"✅ Model found at: {model_path}")
    
    # Check for API key
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("⚠️  Warning: OpenWeather API key not configured")
        print("Set OPENWEATHER_API_KEY environment variable for full functionality")
        print("The app will work with default weather values for testing")
    else:
        print("✅ OpenWeather API key configured")
    
    # Start the Flask app
    try:
        from app import app
        print("🌐 Starting Flask server on http://localhost:5000")
        print("📊 Health check available at http://localhost:5000/health")
        print("🔮 Prediction endpoint at http://localhost:5000/predict")
        print("\n" + "="*50)
        print("Press Ctrl+C to stop the server")
        print("="*50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
