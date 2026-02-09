import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.data_loader import load_stock_data
from src.fundamental_analysis import get_fundamentals, get_news_sentiment, get_analyst_ratings
from src.technical_indicators import calculate_technical_indicators
from src.feature_engineering import engineer_advanced_features, select_best_features
from src.models import train_random_forest, train_xgboost, train_gradient_boosting, build_lstm_model, build_dense_model
from src.metrics import sharpe_ratio, backtest_strategy, max_drawdown
from src.portfolio_optimizer import optimize_portfolio
from src.price_targets import calculate_entry_target_prices, get_nifty50_constituents, screening_is_buy_signal
from src.price_targets_enhanced import calculate_multi_timeframe_levels, generate_buy_sell_explanation, get_nifty50_by_sector, get_all_nifty50
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix, roc_auc_score
from tensorflow.keras.callbacks import EarlyStopping

# ────────────────────────────────────────────────
#  SIDEBAR
# ────────────────────────────────────────────────
st.set_page_config(page_title="AI Trading Lab PRO+", layout="wide")
st.title("🚀 AI Trading Lab PRO+ – ML/DL/Fundamentals/Portfolio/MultiTimeframe")

with st.sidebar:
    st.header("Settings")
    symbol = st.text_input("Main Stock Symbol", "RELIANCE.NS").upper().strip()
    symbols_compare = st.text_area(
        "Portfolio Stocks (comma separated)",
        "RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS"
    )
    index_symbol = st.text_input("Benchmark Index", "^NSEI")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", pd.to_datetime("2010-01-01"))
    with col2:
        end_date = st.date_input("End Date", pd.to_datetime("today"))
    future_days = st.slider("Prediction Horizon (days)", 1, 30, 5)
    model_type = st.selectbox("Model", ["RandomForest", "XGBoost"])
    confidence_thresh = st.slider("Confidence Threshold for Signals", 0.5, 0.95, 0.6)
    
    st.divider()
    st.subheader("🎯 Screening Options")
    
    # Screener Type
    screener_type = st.radio("Select Screener", ["Nifty 50 (All)", "By Sector"])
    
    if screener_type == "By Sector":
        nifty50_sectors = get_nifty50_by_sector()
        selected_sector = st.selectbox("Choose Sector", list(nifty50_sectors.keys()))
    
    st.divider()
    
    # Action buttons
    run_button = st.button("Run Full Analysis", type="primary")
    fundamental_btn = st.button("Run Fundamental Analysis")
    technical_btn = st.button("Run Technical Analysis")
    portfolio_btn = st.button("Run Portfolio Analysis")
    nifty50_btn = st.button("🎯 Nifty 50 Screener", type="secondary")
    portfolio_size = st.number_input("Portfolio Size (use first N symbols)", min_value=1, max_value=50, value=5)
    allow_small_dataset = st.checkbox("Allow small dataset (proceed with warning)", value=False)
