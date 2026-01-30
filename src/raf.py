import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler

def historical_signal(Ticker, target_date=None, window_size=30, top_k=5):
    try:
        # 1. DOWNLOAD DATA 
        df = yf.download(Ticker, period="5y", interval="1d", progress=False)
        
        # Fix MultiIndex Column Bug
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 2. RETURN CALCULATION
        df['Return'] = df['Close'].pct_change()
        df = df.dropna()

        values = df['Close'].values
        returns = df['Return'].values

        if len(values) < window_size * 2:
            return 0.0

        # 3. PREPARE TARGET PATTERN
        target_pattern = values[-window_size:]
        
        history_values = values[:-window_size]
        
        # Scaling 
        scaler = MinMaxScaler()
        target_scaled = scaler.fit_transform(target_pattern.reshape(-1, 1)).flatten()
        
        found_returns = []

        # 4. SCANNING HISTORY
        limit = len(history_values) - window_size
        
        for i in range(0, limit):
            history_slice = history_values[i : i + window_size]
            history_scaled = scaler.transform(history_slice.reshape(-1, 1)).flatten()
            
            # CORELATION CHECK
            try:
                corr = np.corrcoef(target_scaled, history_scaled)[0, 1]
            except:
                corr = 0

            if corr > 0.80:
                next_day_idx = i + window_size
                
                if next_day_idx < len(returns) - window_size:
                    found_returns.append(returns[next_day_idx])

        # 5. RAF CALCULATION              
        if len(found_returns) > 0:
            return np.mean(found_returns)
        else:
            return 0.0

    except Exception as e:
        print(f"Error RAF: {e}")
        return 0.0