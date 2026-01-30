from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yfinance as yf
import numpy as np
import pandas as pd

# Import RAF function and trained model      
from src.raf import historical_signal
from src.loader import trained_model

app = FastAPI(title="Stock Price Predictor API")

class StockRequest(BaseModel):
    ticker: str = "BBRI.JK"
    days: int = 30

@app.get("/")
def home():
    return {"API is working": "Welcome to the Stock Price Predictor API"}

@app.post("/predict")
async def predict_stock(request: StockRequest):
    try:
        MODEL_WINDOW_SIZE = 30  
        # 1. DOWNLOAD DATA
        df = yf.download(request.ticker, period="5y", interval="1d", progress=False)

        # Fix MultiIndex Column Bug
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if df.empty:
            raise HTTPException(status_code=404, detail="Ticker symbol not found or no data available.")
        
        min_required = max(MODEL_WINDOW_SIZE, request.days) + 2  # +2 untuk keamanan
        if len(df) < min_required:
            raise HTTPException(status_code=400, detail="Not enough data to make predictions.")

        # 2. FEATURE ENGINEERING
        # Hitung Return
        df['Return'] = df['Close'].pct_change()
        df = df.dropna() # Hapus baris NaN

        # Ambil data harga Close
        prices = df['Close'].values
        
        # Ambil potongan data terakhir
        data_target = prices[-MODEL_WINDOW_SIZE:]

        # 3. CALL RAF FUNCTION
        raf_value = historical_signal(
            Ticker=request.ticker, 
            window_size=request.days
        )

        if len(data_target) != MODEL_WINDOW_SIZE:
            raise HTTPException(status_code=500, detail="Data preparation error.")
        
        # 4. INPUT PREPARATION
        # Scaling manual: (Harga - Harga Awal) / Harga Awal
        # Supaya nilainya kecil (0.0 sekian)
        base_price = data_target[0]
        scaled_features = (data_target - base_price) / base_price
        
        # Gabungkan: [30 Fitur Harga Scaled] + [1 Fitur RAF]
        # Total harus 31 fitur 
        final_features = list(scaled_features) + [raf_value]

        # 5. PREDICTION
        pred_return = trained_model.predict(np.array([final_features]))[0]

        # Hitung Harga Besok
        last_price = float(data_target[-1])
        next_price = last_price * (1 + pred_return)

        # Tentukan Aksi (Buy/Sell)
        action ="STRONG BUY" if pred_return > 0.01 else \
                "BUY" if pred_return > 0.005 else \
                "SELL" if pred_return < -0.005 else "HOLD"

        return {
            'ticker': request.ticker,
            'current_price': last_price,
            'predicted_return': float(pred_return),
            'next_price': float(next_price),
            'raf_signal': float(raf_value),
            'action': action
        }

    except Exception as e:
        print(f"Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))