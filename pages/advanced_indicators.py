"""
Advanced Technical Indicators Page
Implements 10+ advanced indicators not included in main AI page
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Import backend modules
from src.data_loader import load_stock_data
from src.symbol_utils import normalize_symbol
from ui.components import create_info_card, create_metric_card, get_theme_colors


def calculate_ichimoku(df, tenkan=9, kijun=26, senkou_b=52):
    """Calculate Ichimoku Cloud components"""
    df = df.copy()
    
    # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2
    high_9 = df['High'].rolling(window=tenkan).max()
    low_9 = df['Low'].rolling(window=tenkan).min()
    df['Tenkan_sen'] = (high_9 + low_9) / 2
    
    # Kijun-sen (Base Line): (26-period high + 26-period low)/2
    high_26 = df['High'].rolling(window=kijun).max()
    low_26 = df['Low'].rolling(window=kijun).min()
    df['Kijun_sen'] = (high_26 + low_26) / 2
    
    # Senkou Span A (Leading Span A): (Tenkan-sen + Kijun-sen)/2, projected 26 periods ahead
    df['Senkou_Span_A'] = ((df['Tenkan_sen'] + df['Kijun_sen']) / 2).shift(kijun)
    
    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2, projected 26 periods ahead  
    high_52 = df['High'].rolling(window=senkou_b).max()
    low_52 = df['Low'].rolling(window=senkou_b).min()
    df['Senkou_Span_B'] = ((high_52 + low_52) / 2).shift(kijun)
    
    # Chikou Span (Lagging Span): Current closing price projected 26 periods back
    df['Chikou_Span'] = df['Close'].shift(-kijun)
    
    return df


def calculate_vortex_indicator(df, period=14):
    """Calculate Vortex Indicator (VI+ and VI-)"""
    df = df.copy()
    
    # Calculate True Range
    df['TR'] = df[['High', 'Low', 'Close']].apply(
        lambda x: max(x['High'] - x['Low'], 
                     abs(x['High'] - df['Close'].shift(1).loc[x.name]) if pd.notna(df['Close'].shift(1).loc[x.name]) else 0,
                     abs(x['Low'] - df['Close'].shift(1).loc[x.name]) if pd.notna(df['Close'].shift(1).loc[x.name]) else 0),
        axis=1
    )
    
    # Vortex Movement
    df['VM_plus'] = abs(df['High'] - df['Low'].shift(1))
    df['VM_minus'] = abs(df['Low'] - df['High'].shift(1))
    
    # Sum over period
    df['VM_plus_sum'] = df['VM_plus'].rolling(window=period).sum()
    df['VM_minus_sum'] = df['VM_minus'].rolling(window=period).sum()
    df['TR_sum'] = df['TR'].rolling(window=period).sum()
    
    # Calculate VI+ and VI-
    df['VI_plus'] = df['VM_plus_sum'] / df['TR_sum']
    df['VI_minus'] = df['VM_minus_sum'] / df['TR_sum']
    
    return df


def calculate_elder_ray(df, period=13):
    """Calculate Elder Ray Index (Bull and Bear Power)"""
    df = df.copy()
    
    # Calculate EMA
    df['EMA'] = df['Close'].ewm(span=period, adjust=False).mean()
    
    # Bull Power = High - EMA
    df['Bull_Power'] = df['High'] - df['EMA']
    
    # Bear Power = Low - EMA
    df['Bear_Power'] = df['Low'] - df['EMA']
    
    return df


def calculate_kama(df, period=10, fast_ema=2, slow_ema=30):
    """Calculate Kaufman Adaptive Moving Average"""
    df = df.copy()
    
    # Calculate Change
    change = abs(df['Close'] - df['Close'].shift(period))
    
    # Calculate Volatility (sum of absolute price changes)
    volatility = df['Close'].diff().abs().rolling(window=period).sum()
    
    # Efficiency Ratio (ER) - handle division by zero
    df['ER'] = change / volatility
    df['ER'] = df['ER'].replace([np.inf, -np.inf], 0)  # Replace infinity with 0
    df['ER'] = df['ER'].fillna(0)  # Replace NaN with 0
    
    # Smoothing Constant (SC)
    fast_sc = 2 / (fast_ema + 1)
    slow_sc = 2 / (slow_ema + 1)
    df['SC'] = (df['ER'] * (fast_sc - slow_sc) + slow_sc) ** 2
    df['SC'] = df['SC'].fillna(slow_sc ** 2)  # Use slowest smoothing if NaN
    
    # KAMA calculation
    kama = []
    for i in range(len(df)):
        if i == 0 or pd.isna(df['SC'].iloc[i]):
            kama.append(df['Close'].iloc[i])
        else:
            prev_kama = kama[i-1]
            sc = df['SC'].iloc[i]
            close = df['Close'].iloc[i]
            
            # Calculate new KAMA value
            new_kama = prev_kama + sc * (close - prev_kama)
            
            # Ensure it's not NaN
            if pd.isna(new_kama):
                kama.append(prev_kama)
            else:
                kama.append(new_kama)
    
    df['KAMA'] = kama
    
    # Fill any remaining NaN values with the close price
    df['KAMA'] = df['KAMA'].fillna(df['Close'])
    
    return df


def calculate_tsi(df, long_period=25, short_period=13, signal_period=13):
    """Calculate True Strength Index"""
    df = df.copy()
    
    # Price change
    price_change = df['Close'].diff()
    
    # Double smoothing
    pc_smooth1 = price_change.ewm(span=long_period, adjust=False).mean()
    pc_smooth2 = pc_smooth1.ewm(span=short_period, adjust=False).mean()
    
    abs_pc_smooth1 = abs(price_change).ewm(span=long_period, adjust=False).mean()
    abs_pc_smooth2 = abs_pc_smooth1.ewm(span=short_period, adjust=False).mean()
    
    # TSI
    df['TSI'] = 100 * (pc_smooth2 / abs_pc_smooth2)
    
    # Signal line
    df['TSI_Signal'] = df['TSI'].ewm(span=signal_period, adjust=False).mean()
    
    return df


def calculate_bop(df):
    """Calculate Balance of Power"""
    df = df.copy()
    
    # BOP = (Close - Open) / (High - Low)
    df['BOP'] = (df['Close'] - df['Open']) / (df['High'] - df['Low'])
    df['BOP'] = df['BOP'].fillna(0)  # Handle division by zero
    
    return df


def calculate_pvt(df):
    """Calculate Price Volume Trend"""
    df = df.copy()
    
    # PVT = Previous PVT + (Volume * (Close - Previous Close) / Previous Close)
    price_change_pct = df['Close'].pct_change()
    df['PVT'] = (price_change_pct * df['Volume']).fillna(0).cumsum()
    
    return df


def calculate_mass_index(df, ema_period=9, sum_period=25):
    """Calculate Mass Index"""
    df = df.copy()
    
    # High-Low range
    high_low = df['High'] - df['Low']
    
    # Single EMA
    ema1 = high_low.ewm(span=ema_period, adjust=False).mean()
    
    # Double EMA
    ema2 = ema1.ewm(span=ema_period, adjust=False).mean()
    
    # Mass Index = Sum of (EMA1 / EMA2) over sum_period
    df['Mass_Index'] = (ema1 / ema2).rolling(window=sum_period).sum()
    
    return df


def calculate_dpo(df, period=20):
    """Calculate Detrended Price Oscillator"""
    df = df.copy()
    
    # DPO = Close - SMA(period/2 + 1 periods ago)
    sma = df['Close'].rolling(window=period).mean()
    shift_period = int(period / 2) + 1
    df['DPO'] = df['Close'] - sma.shift(shift_period)
    
    return df


def render_advanced_indicators():
    """Render advanced indicators page"""
    
    theme_colors = get_theme_colors()
    
    st.markdown(f"""
    <div style='background: {theme_colors['gradient_bg']}; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>
        <h1 style='color: white; margin: 0;'>🔬 Advanced Technical Indicators</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 10px 0 0 0;'>
            Professional trading indicators: Ichimoku, Vortex, Elder Ray, KAMA, TSI, and more
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Symbol input
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        symbol = st.text_input("📈 Enter Stock Symbol", value="TCS", help="Enter NSE stock symbol (e.g., RELIANCE, TCS, INFY)")
    
    with col2:
        days = st.selectbox("📅 Historical Data", options=[30, 60, 90, 180, 365], index=2, help="Number of days of historical data")
    
    with col3:
        if st.button("🔍 Analyze", use_container_width=True, type="primary"):
            st.session_state.adv_analyze_clicked = True
    
    if not st.session_state.get('adv_analyze_clicked', False):
        create_info_card(
            "Advanced Indicators",
            "Enter a stock symbol and click 'Analyze' to view advanced technical indicators including Ichimoku Cloud, Vortex Indicator, Elder Ray Index, and more.",
            "🔬",
            "info"
        )
        return
    
    # Load data
    with st.spinner(f"📊 Loading data for {symbol}..."):
        try:
            symbol = normalize_symbol(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days+100)  # Extra data for calculations
            
            stock_data = load_stock_data(symbol, start_date, end_date)
            
            if stock_data is None or len(stock_data) < 50:
                st.error("❌ Unable to load sufficient data. Please try another symbol.")
                return
            
            # Calculate all advanced indicators
            stock_data = calculate_ichimoku(stock_data)
            stock_data = calculate_vortex_indicator(stock_data)
            stock_data = calculate_elder_ray(stock_data)
            stock_data = calculate_kama(stock_data)
            stock_data = calculate_tsi(stock_data)
            stock_data = calculate_bop(stock_data)
            stock_data = calculate_pvt(stock_data)
            stock_data = calculate_mass_index(stock_data)
            stock_data = calculate_dpo(stock_data)
            
            latest = stock_data.iloc[-1]
            current_price = latest['Close']
            
            st.success(f"✅ Loaded {len(stock_data)} days of data for {symbol}")
            
            # Display current price
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                price_change = latest['Close'] - stock_data.iloc[-2]['Close']
                price_change_pct = (price_change / stock_data.iloc[-2]['Close']) * 100
                st.metric("Current Price", f"₹{latest['Close']:.2f}", f"{price_change_pct:+.2f}%")
            
            with col2:
                st.metric("High", f"₹{latest['High']:.2f}")
            
            with col3:
                st.metric("Low", f"₹{latest['Low']:.2f}")
            
            with col4:
                st.metric("Volume", f"{latest['Volume']:,.0f}")
            
            # ═══════════════════════════════════════════════════════════
            # ICHIMOKU CLOUD
            # ═══════════════════════════════════════════════════════════
            st.markdown("---")
            st.markdown("### ☁️ Ichimoku Cloud - All-in-One Indicator")
            
            col1, col2 = st.columns([3, 1])
            
            with col2:
                # Ichimoku signals
                tenkan = latest.get('Tenkan_sen', current_price)
                kijun = latest.get('Kijun_sen', current_price)
                senkou_a = latest.get('Senkou_Span_A', current_price)
                senkou_b = latest.get('Senkou_Span_B', current_price)
                
                # Determine signal
                if current_price > max(senkou_a, senkou_b) and tenkan > kijun:
                    ichi_signal = "🟢 Strong Bullish"
                    ichi_color = "#48bb78"
                    ichi_desc = "Price above cloud, bullish crossover"
                elif current_price < min(senkou_a, senkou_b) and tenkan < kijun:
                    ichi_signal = "🔴 Strong Bearish"
                    ichi_color = "#f56565"
                    ichi_desc = "Price below cloud, bearish crossover"
                elif current_price > max(senkou_a, senkou_b):
                    ichi_signal = "🟢 Bullish"
                    ichi_color = "#48bb78"
                    ichi_desc = "Price above cloud"
                elif current_price < min(senkou_a, senkou_b):
                    ichi_signal = "🔴 Bearish"
                    ichi_color = "#f56565"
                    ichi_desc = "Price below cloud"
                else:
                    ichi_signal = "🟡 Neutral (In Cloud)"
                    ichi_color = "#ed8936"
                    ichi_desc = "Price inside cloud - consolidation"
                
                st.markdown(f"""
                <div style='background: {theme_colors['card_bg']}; padding: 20px; border-radius: 10px; border-left: 4px solid {ichi_color};'>
                    <h4 style='margin: 0; color: {theme_colors['text']};'>Ichimoku Signal</h4>
                    <h2 style='margin: 10px 0; color: {ichi_color};'>{ichi_signal}</h2>
                    <p style='margin: 0; color: {theme_colors['text_secondary']};'>{ichi_desc}</p>
                    <hr style='margin: 15px 0; border: 0; border-top: 1px solid {theme_colors['text_secondary']};'>
                    <p style='margin: 5px 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>
                        <strong>Tenkan-sen:</strong> ₹{tenkan:.2f}<br>
                        <strong>Kijun-sen:</strong> ₹{kijun:.2f}<br>
                        <strong>Senkou A:</strong> ₹{senkou_a:.2f}<br>
                        <strong>Senkou B:</strong> ₹{senkou_b:.2f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col1:
                # Ichimoku chart
                fig = go.Figure()
                
                chart_data = stock_data.tail(60)
                
                # Price
                fig.add_trace(go.Scatter(
                    x=chart_data.index, y=chart_data['Close'],
                    name='Close Price', line=dict(color='#667eea', width=2)
                ))
                
                # Tenkan-sen
                fig.add_trace(go.Scatter(
                    x=chart_data.index, y=chart_data['Tenkan_sen'],
                    name='Tenkan-sen (9)', line=dict(color='#f093fb', dash='dash')
                ))
                
                # Kijun-sen
                fig.add_trace(go.Scatter(
                    x=chart_data.index, y=chart_data['Kijun_sen'],
                    name='Kijun-sen (26)', line=dict(color='#f5576c', dash='dash')
                ))
                
                # Senkou Span A (Cloud)
                fig.add_trace(go.Scatter(
                    x=chart_data.index, y=chart_data['Senkou_Span_A'],
                    name='Senkou Span A', line=dict(color='#48bb78', width=0),
                    fillcolor='rgba(72, 187, 120, 0.2)', fill='tonexty', showlegend=True
                ))
                
                # Senkou Span B (Cloud)
                fig.add_trace(go.Scatter(
                    x=chart_data.index, y=chart_data['Senkou_Span_B'],
                    name='Senkou Span B', line=dict(color='#f56565', width=0),
                    fillcolor='rgba(245, 101, 101, 0.2)', showlegend=True
                ))
                
                fig.update_layout(
                    title='Ichimoku Cloud Analysis',
                    yaxis_title='Price (₹)',
                    height=450,
                    hovermode='x unified',
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # ═══════════════════════════════════════════════════════════
            # VORTEX INDICATOR
            # ═══════════════════════════════════════════════════════════
            st.markdown("---")
            st.markdown("### 🌀 Vortex Indicator - Trend Detection")
            
            col1, col2, col3 = st.columns(3)
            
            vi_plus = latest.get('VI_plus', 1)
            vi_minus = latest.get('VI_minus', 1)
            
            with col1:
                if vi_plus > vi_minus and vi_plus > 1.0:
                    vortex_signal = "🟢 Strong Uptrend"
                    vortex_color = "#48bb78"
                elif vi_minus > vi_plus and vi_minus > 1.0:
                    vortex_signal = "🔴 Strong Downtrend"
                    vortex_color = "#f56565"
                elif vi_plus > vi_minus:
                    vortex_signal = "🟢 Uptrend"
                    vortex_color = "#48bb78"
                else:
                    vortex_signal = "🔴 Downtrend"
                    vortex_color = "#f56565"
                
                st.markdown(f"""
                <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; border-left: 4px solid {vortex_color};'>
                    <h5 style='margin: 0; color: {theme_colors['text']};'>Vortex Signal</h5>
                    <h3 style='margin: 8px 0; color: {vortex_color};'>{vortex_signal}</h3>
                    <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>
                        VI+: {vi_plus:.3f} | VI-: {vi_minus:.3f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Elder Ray
                bull_power = latest.get('Bull_Power', 0)
                bear_power = latest.get('Bear_Power', 0)
                
                if bull_power > 0 and bear_power > 0:
                    elder_signal = "🟢 Bulls in Control"
                    elder_color = "#48bb78"
                elif bull_power < 0 and bear_power < 0:
                    elder_signal = "🔴 Bears in Control"
                    elder_color = "#f56565"
                else:
                    elder_signal = "🟡 Balanced"
                    elder_color = "#ed8936"
                
                st.markdown(f"""
                <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; border-left: 4px solid {elder_color};'>
                    <h5 style='margin: 0; color: {theme_colors['text']};'>Elder Ray Index</h5>
                    <h3 style='margin: 8px 0; color: {elder_color};'>{elder_signal}</h3>
                    <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>
                        Bull: {bull_power:.2f} | Bear: {bear_power:.2f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                # Balance of Power
                bop = latest.get('BOP', 0)
                
                if bop > 0.5:
                    bop_signal = "🟢 Buyers Dominate"
                    bop_color = "#48bb78"
                elif bop < -0.5:
                    bop_signal = "🔴 Sellers Dominate"
                    bop_color = "#f56565"
                else:
                    bop_signal = "🟡 Balanced"
                    bop_color = "#ed8936"
                
                st.markdown(f"""
                <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; border-left: 4px solid {bop_color};'>
                    <h5 style='margin: 0; color: {theme_colors['text']};'>Balance of Power</h5>
                    <h3 style='margin: 8px 0; color: {bop_color};'>{bop_signal}</h3>
                    <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>
                        BOP: {bop:.3f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Vortex + Elder Ray Chart
            col1, col2 = st.columns(2)
            
            with col1:
                fig_vortex = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                                          subplot_titles=('Price', 'Vortex Indicator'))
                
                chart_data = stock_data.tail(60)
                
                fig_vortex.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Close'],
                                               name='Close', line=dict(color='#667eea')), row=1, col=1)
                
                fig_vortex.add_trace(go.Scatter(x=chart_data.index, y=chart_data['VI_plus'],
                                               name='VI+', line=dict(color='#48bb78')), row=2, col=1)
                
                fig_vortex.add_trace(go.Scatter(x=chart_data.index, y=chart_data['VI_minus'],
                                               name='VI-', line=dict(color='#f56565')), row=2, col=1)
                
                fig_vortex.update_layout(height=400, showlegend=True)
                st.plotly_chart(fig_vortex, use_container_width=True)
            
            with col2:
                fig_elder = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                                         subplot_titles=('Price', 'Elder Ray (Bull/Bear Power)'))
                
                fig_elder.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Close'],
                                              name='Close', line=dict(color='#667eea')), row=1, col=1)
                
                fig_elder.add_trace(go.Bar(x=chart_data.index, y=chart_data['Bull_Power'],
                                          name='Bull Power', marker_color='#48bb78'), row=2, col=1)
                
                fig_elder.add_trace(go.Bar(x=chart_data.index, y=chart_data['Bear_Power'],
                                          name='Bear Power', marker_color='#f56565'), row=2, col=1)
                
                fig_elder.update_layout(height=400, showlegend=True)
                st.plotly_chart(fig_elder, use_container_width=True)
            
            # ═══════════════════════════════════════════════════════════
            # ADAPTIVE & MOMENTUM INDICATORS
            # ═══════════════════════════════════════════════════════════
            st.markdown("---")
            st.markdown("### 📊 Adaptive & Momentum Indicators")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # KAMA
                kama = latest.get('KAMA', current_price)
                
                # Handle NaN values
                if pd.isna(kama) or kama == 0:
                    kama = current_price
                
                if current_price > kama:
                    kama_signal = "🟢 Above KAMA"
                    kama_color = "#48bb78"
                else:
                    kama_signal = "🔴 Below KAMA"
                    kama_color = "#f56565"
                
                st.markdown(f"""
                <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; border-left: 4px solid {kama_color};'>
                    <h5 style='margin: 0; color: {theme_colors['text']};'>KAMA (Adaptive MA)</h5>
                    <h3 style='margin: 8px 0; color: {kama_color};'>{kama_signal}</h3>
                    <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>
                        Value: ₹{kama:.2f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # TSI
                tsi = latest.get('TSI', 0)
                tsi_signal_line = latest.get('TSI_Signal', 0)
                
                if tsi > tsi_signal_line and tsi > 0:
                    tsi_signal = "🟢 Strong Bullish"
                    tsi_color = "#48bb78"
                elif tsi < tsi_signal_line and tsi < 0:
                    tsi_signal = "🔴 Strong Bearish"
                    tsi_color = "#f56565"
                elif tsi > 0:
                    tsi_signal = "🟢 Bullish"
                    tsi_color = "#48bb78"
                else:
                    tsi_signal = "🔴 Bearish"
                    tsi_color = "#f56565"
                
                st.markdown(f"""
                <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; border-left: 4px solid {tsi_color};'>
                    <h5 style='margin: 0; color: {theme_colors['text']};'>True Strength Index</h5>
                    <h3 style='margin: 8px 0; color: {tsi_color};'>{tsi_signal}</h3>
                    <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>
                        TSI: {tsi:.2f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                # Mass Index
                mass_idx = latest.get('Mass_Index', 20)
                
                if mass_idx > 27:
                    mass_signal = "⚠️ Reversal Bulge"
                    mass_color = "#f56565"
                    mass_desc = "Potential trend reversal"
                elif mass_idx > 26.5:
                    mass_signal = "🟡 High Volatility"
                    mass_color = "#ed8936"
                    mass_desc = "Watch for reversal"
                else:
                    mass_signal = "🟢 Normal Range"
                    mass_color = "#48bb78"
                    mass_desc = "Trend intact"
                
                st.markdown(f"""
                <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; border-left: 4px solid {mass_color};'>
                    <h5 style='margin: 0; color: {theme_colors['text']};'>Mass Index</h5>
                    <h3 style='margin: 8px 0; color: {mass_color};'>{mass_signal}</h3>
                    <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>
                        Value: {mass_idx:.2f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # KAMA + TSI Charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig_kama = go.Figure()
                chart_data = stock_data.tail(60)
                
                fig_kama.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Close'],
                                             name='Close', line=dict(color='#667eea')))
                
                fig_kama.add_trace(go.Scatter(x=chart_data.index, y=chart_data['KAMA'],
                                             name='KAMA', line=dict(color='#48bb78', width=2)))
                
                fig_kama.update_layout(title='KAMA vs Price', height=350)
                st.plotly_chart(fig_kama, use_container_width=True)
            
            with col2:
                fig_tsi = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                                       subplot_titles=('Price', 'TSI'))
                
                fig_tsi.add_trace(go.Scatter(x=chart_data.index, y=chart_data['Close'],
                                            name='Close', line=dict(color='#667eea')), row=1, col=1)
                
                fig_tsi.add_trace(go.Scatter(x=chart_data.index, y=chart_data['TSI'],
                                            name='TSI', line=dict(color='#9f7aea')), row=2, col=1)
                
                fig_tsi.add_trace(go.Scatter(x=chart_data.index, y=chart_data['TSI_Signal'],
                                            name='Signal', line=dict(color='#ed8936', dash='dash')), row=2, col=1)
                
                fig_tsi.update_layout(height=350)
                st.plotly_chart(fig_tsi, use_container_width=True)
            
            # ═══════════════════════════════════════════════════════════
            # VOLUME & CYCLE INDICATORS
            # ═══════════════════════════════════════════════════════════
            st.markdown("---")
            st.markdown("### 💹 Volume & Cycle Indicators")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Price Volume Trend
                pvt = latest.get('PVT', 0)
                pvt_prev = stock_data.iloc[-5].get('PVT', 0)
                
                if pvt > pvt_prev:
                    pvt_signal = "🟢 Accumulation"
                    pvt_color = "#48bb78"
                else:
                    pvt_signal = "🔴 Distribution"
                    pvt_color = "#f56565"
                
                st.markdown(f"""
                <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; border-left: 4px solid {pvt_color};'>
                    <h5 style='margin: 0; color: {theme_colors['text']};'>Price Volume Trend</h5>
                    <h3 style='margin: 8px 0; color: {pvt_color};'>{pvt_signal}</h3>
                    <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>
                        PVT: {pvt:,.0f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Detrended Price Oscillator
                dpo = latest.get('DPO', 0)
                
                if dpo > 0:
                    dpo_signal = "🟢 Above Trend"
                    dpo_color = "#48bb78"
                    dpo_desc = "Short-term overbought"
                else:
                    dpo_signal = "🔴 Below Trend"
                    dpo_color = "#f56565"
                    dpo_desc = "Short-term oversold"
                
                st.markdown(f"""
                <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; border-left: 4px solid {dpo_color};'>
                    <h5 style='margin: 0; color: {theme_colors['text']};'>Detrended Price Osc.</h5>
                    <h3 style='margin: 8px 0; color: {dpo_color};'>{dpo_signal}</h3>
                    <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>
                        DPO: {dpo:.2f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # PVT + DPO Charts
            fig_vol = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                                   subplot_titles=('Price Volume Trend', 'Detrended Price Oscillator'))
            
            chart_data = stock_data.tail(60)
            
            fig_vol.add_trace(go.Scatter(x=chart_data.index, y=chart_data['PVT'],
                                        name='PVT', line=dict(color='#667eea'), fill='tonexty'), row=1, col=1)
            
            fig_vol.add_trace(go.Bar(x=chart_data.index, y=chart_data['DPO'],
                                    name='DPO', marker_color='#9f7aea'), row=2, col=1)
            
            fig_vol.update_layout(height=500)
            st.plotly_chart(fig_vol, use_container_width=True)
            
            # ═══════════════════════════════════════════════════════════
            # SUMMARY & RECOMMENDATIONS
            # ═══════════════════════════════════════════════════════════
            st.markdown("---")
            st.markdown("### 📋 Advanced Indicators Summary")
            
            summary_data = {
                'Indicator': [
                    'Ichimoku Cloud',
                    'Vortex Indicator',
                    'Elder Ray Index',
                    'Balance of Power',
                    'KAMA',
                    'True Strength Index',
                    'Mass Index',
                    'Price Volume Trend',
                    'Detrended Price Osc.'
                ],
                'Signal': [
                    ichi_signal,
                    vortex_signal,
                    elder_signal,
                    bop_signal,
                    kama_signal,
                    tsi_signal,
                    mass_signal,
                    pvt_signal,
                    dpo_signal
                ],
                'Value': [
                    f"Price vs Cloud",
                    f"VI+: {vi_plus:.3f}, VI-: {vi_minus:.3f}",
                    f"Bull: {bull_power:.2f}, Bear: {bear_power:.2f}",
                    f"BOP: {bop:.3f}",
                    f"₹{kama:.2f}",
                    f"TSI: {tsi:.2f}",
                    f"MI: {mass_idx:.2f}",
                    f"{pvt:,.0f}",
                    f"{dpo:.2f}"
                ]
            }
            
            df_summary = pd.DataFrame(summary_data)
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"❌ Error analyzing data: {e}")
            import traceback
            st.code(traceback.format_exc())


# Main render function
if __name__ == "__main__" or "render" in dir():
    render_advanced_indicators()
