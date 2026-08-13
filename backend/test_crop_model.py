import pickle
import numpy as np
import os

print("🔍 Testing Crop Recommendation Model...")

# Load the model
model_path = os.path.join(os.path.dirname(__file__), '..', 'crop_recommendation_model', 'crop_model.pkl')
print(f"Model path: {model_path}")

try:
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print(f"✅ Model loaded successfully")
    print(f"   Model type: {type(model)}")
    print(f"   Model class: {model.__class__.__name__}")
    
    if hasattr(model, 'n_features_in_'):
        print(f"   Expected features: {model.n_features_in_}")
    if hasattr(model, 'classes_'):
        print(f"   Classes: {model.classes_}")
    if hasattr(model, 'feature_names_in_'):
        print(f"   Feature names: {model.feature_names_in_}")
    
    # Test prediction with sample data
    print("\n🧪 Testing prediction with sample data...")
    sample_features = [50, 35, 52, 6.75, 25, 60, 50]  # N, P, K, pH, temp, humidity, moisture
    features_array = np.array(sample_features).reshape(1, -1)
    print(f"   Input features: {sample_features}")
    print(f"   Input shape: {features_array.shape}")
    
    prediction = model.predict(features_array)
    print(f"   Prediction: {prediction}")
    
    if hasattr(model, 'predict_proba'):
        probabilities = model.predict_proba(features_array)
        print(f"   Probabilities: {probabilities}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
