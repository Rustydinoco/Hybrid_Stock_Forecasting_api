import xgboost as xgb
import os 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'models', 'xgb_hybrid_raf.JSON')

def load_model():
    if not os.path.exists(MODEL_DIR):
        raise FileNotFoundError(f"Model file not found at {MODEL_DIR}")
    
    model = xgb.XGBRegressor()
    model.load_model(MODEL_DIR)
    return model

print("Loading trained model...")
trained_model = load_model()
print("Model loaded successfully.")