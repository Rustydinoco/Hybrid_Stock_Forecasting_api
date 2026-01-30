import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(
    page_title="AI Stock Predictor Dashboard",
    layout="wide",
    page_icon=":chart_with_upwards_trend:"
)
# Dashboard Title and Description
st.title("AI Stock Predictor Dashboard")
st.markdown("Welcome to the AI Stock Predictor Dashboard! Use this interface to predict stock prices using our advanced machine learning model.")

# Sidebar for User Input
with st.sidebar:
    st.header("Input Parameters")
    ticker = st.text_input("Ticker Symbol", value="BBRI.JK")
    predict_button = st.button("Predict Stock Price")

    st.info("Enter the stock ticker symbol and select the number of days for prediction. Click 'Predict Stock Price' to get the forecast.")

#Main Prediction Logic
if predict_button:
    with st.spinner("Fetching data and making prediction ..."):
        try:
                response = requests.post(
                    "http://localhost:8000/predict",
                    json={"ticker": ticker, "days": 30}
                )
                response.raise_for_status()
                result = response.json()

                # Display Prediction Results
                st.subheader("Prediction Results")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Current Price", f"Rp {result['current_price']:,.0f}")
                
                with col2:
                    delta_val = f"{result['predicted_return']*100:.2f}%"
                    st.metric("Predicted Next Price", f"Rp {result['next_price']:,.0f}", delta=delta_val)
                
                with col3:
                    st.metric("Signal (RAF)", f"{result['raf_signal']:.5f}")
                
                with col4:
                    action = result['action']
                    if action in ["BUY", "STRONG BUY"]:
                        warna = "green"
                    elif "SELL" in action:
                        warna = "red"
                    else:
                        warna = "gray" # HOLD

                    st.markdown("Decision")

                    st.markdown(f":{warna}[**{action}**]")

                st.markdown("---")
                raf_signal = result['raf_signal']
                if raf_signal > 0:
                    st.success(f"The RAF signal is positive ({raf_signal:.5f}), indicating an uptrend based on history pattern.")
                elif raf_signal == 0:
                    st.info(f"The RAF signal is neutral ({raf_signal:.5f}), indicating no significant pattern match.")
                elif raf_signal < 0:    
                    st.error(f"The RAF signal is negative ({raf_signal:.5f}), indicating a downtrend based on history pattern.")
                # Visualization of Prediction
                st.subheader("Visualitation of Prediction")
                
                labels = ['current_price', 'next_Price']
                values = [result['current_price'], result['next_price']]
                
                if result['next_price'] > result['current_price']:
                    colors = ['#bdc3c7', '#2ecc71'] 
                else:
                    colors = ['#bdc3c7', '#e74c3c'] 

                # 3. Bikin Plot
                fig, ax = plt.subplots(figsize=(8, 4))
                
                # Bikin Bar Chart
                bars = ax.bar(labels, values, color=colors, width=0.5)
                
                # Tambahkan Label Angka di atas Bar (Biar gampang baca)
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'Rp {int(height):,}',
                            ha='center', va='bottom', fontsize=12, fontweight='bold')

                # Atur batas sumbu Y biar grafiknya gak "zoom in" terlalu parah
                # Kita kasih ruang atas bawah 2% biar bar-nya gak mentok
                min_y = min(values) * 0.98
                max_y = max(values) * 1.02
                ax.set_ylim(min_y, max_y)
                
                ax.set_title(f"Price Comparison: {ticker}", fontsize=14)
                ax.set_ylabel("Prices (Rp)")
                
                # Hilangkan border atas dan kanan biar bersih (Style ala jurnal)
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.grid(axis='y', linestyle='--', alpha=0.5)

                # 4. Tampilkan di Streamlit
                st.pyplot(fig)

                # --- DATA MENTAH ---
                with st.expander("JSON Data Result"):
                    st.json(result)
            
        except requests.exceptions.RequestException as e:
                st.error(f"Error fetching prediction: {e}")
else:
        st.write("Fill in the parameters and click 'Predict Stock Price' to see the results.")
    

