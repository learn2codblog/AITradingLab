"""
Deep Learning page module for AI Trading Lab PRO+
Provides advanced neural network models for price prediction with educational guidance
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from ui.components import create_section_header, get_theme_colors
from src.data_loader import load_stock_data
from src.symbol_utils import normalize_symbol


def render_deep_learning():
    """Render the Deep Learning page with educational content and multiple AI models."""
    theme_colors = get_theme_colors()
    
    # Header with gradient
    st.markdown(f"""
    <div style='background: {theme_colors['gradient_bg']}; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>
        <h1 style='color: white; margin: 0;'>🧠 Deep Learning Price Prediction</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 10px 0 0 0;'>
            Advanced Neural Networks for Stock Price Forecasting with AI-Powered Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Educational introduction section
    render_educational_intro(theme_colors)
    
    # Main configuration section with detailed explanations
    st.markdown("### ⚙️ Model Configuration")
    
    config_col1, config_col2 = st.columns([2, 1])
    
    with config_col1:
        symbol = st.text_input(
            "📈 Stock Symbol", 
            value="TCS", 
            help="Enter NSE stock symbol (e.g., TCS, INFY, RELIANCE)"
        )
    
    with config_col2:
        forecast_days = st.number_input(
            "📅 Forecast Days", 
            min_value=1, 
            max_value=30, 
            value=5, 
            help="Number of days to predict ahead (1-30 days)"
        )
    
    # Model selection with detailed descriptions
    st.markdown("#### 🤖 Choose Your AI Model")
    
    model_tabs = st.tabs(["🚀 LSTM (Fast)", "🔬 LSTM (Deep)", "⚡ GRU", "🎯 Bidirectional LSTM", "🧩 Hybrid Model"])
    
    with model_tabs[0]:
        render_model_info(
            "LSTM (Fast) - Recommended for Beginners",
            "Long Short-Term Memory is a type of neural network designed to remember patterns over time.",
            pros=["Fast training (1-2 minutes)", "Good for short-term predictions", "Lower computational requirements"],
            cons=["May miss complex patterns", "Best for trends, not volatility"],
            use_case="Daily trading decisions, quick analysis"
        )
        model_type = "LSTM (Fast)" if st.button("Select LSTM (Fast)", key="lstm_fast", use_container_width=True) else None
    
    with model_tabs[1]:
        render_model_info(
            "LSTM (Deep) - Advanced Analysis",
            "Deep LSTM with multiple layers can capture more complex market patterns and relationships.",
            pros=["Captures complex patterns", "Better for multi-factor analysis", "Higher accuracy potential"],
            cons=["Slower training (3-5 minutes)", "Requires more data", "Risk of overfitting"],
            use_case="Swing trading, medium-term predictions"
        )
        if model_type is None:
            model_type = "LSTM (Deep)" if st.button("Select LSTM (Deep)", key="lstm_deep", use_container_width=True) else None
    
    with model_tabs[2]:
        render_model_info(
            "GRU - Efficient Alternative",
            "Gated Recurrent Unit is faster than LSTM with similar performance for many tasks.",
            pros=["Faster than LSTM", "Good pattern recognition", "Less overfitting"],
            cons=["May underperform on very long sequences", "Fewer parameters to tune"],
            use_case="Intraday to short-term predictions"
        )
        if model_type is None:
            model_type = "GRU" if st.button("Select GRU", key="gru", use_container_width=True) else None
    
    with model_tabs[3]:
        render_model_info(
            "Bidirectional LSTM - Best Accuracy",
            "Processes data in both directions to understand context better, highest accuracy but slowest.",
            pros=["Highest accuracy potential", "Best pattern recognition", "Understands full context"],
            cons=["Slowest training (5-7 minutes)", "Requires most data", "High computational cost"],
            use_case="Position trading, long-term investment decisions"
        )
        if model_type is None:
            model_type = "Bidirectional LSTM" if st.button("Select Bidirectional LSTM", key="bilstm", use_container_width=True) else None
    
    with model_tabs[4]:
        render_model_info(
            "Hybrid Model - Experimental",
            "Combines LSTM with CNN for pattern extraction and attention mechanism for focus.",
            pros=["Innovative approach", "Captures multiple patterns", "Attention on important features"],
            cons=["Experimental", "Longest training time", "Requires careful tuning"],
            use_case="Research, testing new strategies"
        )
        if model_type is None:
            model_type = "Hybrid Model" if st.button("Select Hybrid Model", key="hybrid", use_container_width=True) else None
    
    # If no model selected yet, default to LSTM (Fast)
    if model_type is None:
        model_type = "LSTM (Fast)"
        st.info(f"ℹ️ Currently selected: **{model_type}** (default)")
    else:
        st.success(f"✅ Selected: **{model_type}**")
    
    # Advanced settings with educational tooltips
    with st.expander("⚙️ Advanced Model Settings (Optional)", expanded=False):
        st.markdown("**These settings control how the model learns. Default values work well for most cases.**")
        
        adv_col1, adv_col2, adv_col3 = st.columns(3)
        
        with adv_col1:
            lookback = st.slider(
                "Lookback Period (Days)", 
                min_value=30, 
                max_value=120, 
                value=60,
                help="How many days of past data to use for learning. More days = more context but slower training."
            )
            st.caption("📖 30 days: Fast, recent trends | 60 days: Balanced | 120 days: Full context")
        
        with adv_col2:
            epochs = st.slider(
                "Training Epochs", 
                min_value=10, 
                max_value=100, 
                value=50,
                help="Number of times the model sees the data. More epochs = better learning but risk of overfitting."
            )
            st.caption("📖 10-30: Fast testing | 50: Recommended | 100: Deep training")
        
        with adv_col3:
            confidence = st.checkbox(
                "Show Confidence Intervals", 
                value=True,
                help="Display prediction uncertainty range. Wider range = less certain."
            )
            st.caption("📖 Shows prediction reliability")
        
        st.markdown("---")
        st.markdown("**Feature Selection - What data should the model learn from?**")
        
        feature_col1, feature_col2 = st.columns(2)
        
        with feature_col1:
            use_volume = st.checkbox("📊 Volume Data", value=True, help="Trading volume patterns")
            use_technical = st.checkbox("📈 Technical Indicators", value=True, help="RSI, MACD, ADX, etc.")
        
        with feature_col2:
            use_volatility = st.checkbox("💹 Volatility Metrics", value=True, help="ATR, Bollinger Bands")
            use_momentum = st.checkbox("🚀 Momentum Indicators", value=True, help="ROC, Stochastic")
    
    # Educational risk warning
    st.markdown("---")
    st.warning("""
    ⚠️ **Important Disclaimer:**
    - Deep learning models predict based on historical patterns and may not account for sudden market events
    - Past performance does not guarantee future results
    - Use predictions as ONE input in your decision-making process, not the sole factor
    - Always combine with fundamental analysis, news, and risk management
    - Never invest more than you can afford to lose
    """)
    
    # Feature importance settings
    show_features = st.checkbox(
        "📊 Show Feature Importance Analysis", 
        value=True,
        help="See which factors (price, volume, indicators) the model considers most important"
    )
    
    # Training button with clear CTA
    st.markdown("---")
    if st.button("🚀 Train Model & Generate Predictions", use_container_width=True, type="primary"):
        # Determine features based on user selection
        features_to_use = ['Close']
        if use_volume:
            features_to_use.append('Volume')
        if use_technical:
            features_to_use.extend(['RSI_14', 'MACD', 'ADX'])
        if use_volatility:
            features_to_use.extend(['BB_Upper', 'BB_Lower', 'ATR_14'])
        if use_momentum:
            features_to_use.extend(['ROC', 'Stoch_K'])
        
        with st.spinner(f"🔄 Training {model_type} model... This may take 1-5 minutes depending on complexity."):
            try:
                # Load data
                symbol_norm = normalize_symbol(symbol)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=lookback + 200)
                
                df = load_stock_data(symbol_norm, start_date, end_date)
                
                if df is None or len(df) < lookback:
                    st.error(f"❌ Unable to load sufficient data for {symbol}. Need at least {lookback} days of historical data.")
                    st.info("💡 Try: Using a different stock symbol or reducing the lookback period")
                    return
                
                # Import and run prediction
                from src.advanced_ai import predict_with_lstm, calculate_advanced_indicators
                
                # Calculate indicators for features
                st.info("📊 Calculating technical indicators...")
                df = calculate_advanced_indicators(df)
                
                # Configure model parameters based on selection
                if model_type == "LSTM (Fast)":
                    model_size = 'small'
                    training_note = "Fast model with 2 layers - good for quick analysis"
                elif model_type == "LSTM (Deep)":
                    model_size = 'large'
                    training_note = "Deep model with 4 layers - captures complex patterns"
                elif model_type == "GRU":
                    model_size = 'medium'
                    training_note = "GRU architecture - efficient and fast"
                elif model_type == "Bidirectional LSTM":
                    model_size = 'xlarge'
                    training_note = "Bidirectional processing - highest accuracy"
                else:  # Hybrid
                    model_size = 'hybrid'
                    training_note = "Hybrid architecture with CNN and attention layers"
                
                st.info(f"🧠 {training_note}")
                
                # Train and predict
                prediction = predict_with_lstm(
                    df,
                    lookback=lookback,
                    forecast_days=forecast_days,
                    epochs=epochs,
                    features=features_to_use,
                    model_size=model_size,
                    n_mc_samples=30 if confidence else 1
                )
                
                if prediction and 'status' in prediction and prediction['status'] == 'success':
                    # Display results
                    display_prediction_results(
                        prediction, 
                        symbol, 
                        theme_colors, 
                        confidence, 
                        show_features,
                        model_type,
                        features_to_use
                    )
                else:
                    st.error("❌ Model training failed. Please try adjusting parameters or using a different stock.")
                    st.info("""
                    💡 **Troubleshooting Tips:**
                    - Reduce the number of epochs (try 20-30)
                    - Use fewer features (uncheck some options)
                    - Try a simpler model (LSTM Fast or GRU)
                    - Ensure the stock symbol is correct
                    """)
                    
            except ImportError as e:
                st.error("❌ Deep learning libraries not installed!")
                st.code("pip install tensorflow keras scikit-learn", language="bash")
                st.info("💡 Install the required libraries and restart the application")
            except Exception as e:
                st.error(f"❌ Error during training: {str(e)}")
                st.info("""
                💡 **Common Issues:**
                - Stock data unavailable: Try a different symbol
                - Insufficient data: Reduce lookback period
                - Memory error: Use LSTM (Fast) model
                - Training stuck: Reduce epochs to 20-30
                """)


def render_educational_intro(theme_colors: dict):
    """Render educational introduction about deep learning for stock prediction."""
    
    with st.expander("📚 What is Deep Learning Price Prediction? (Click to learn)", expanded=True):
        st.markdown("""
        ### 🎯 What This Page Does
        
        This page uses **Artificial Intelligence (AI)** to predict future stock prices based on historical patterns. 
        Think of it as teaching a computer to recognize patterns in past price movements and use them to forecast 
        what might happen next.
        
        ### 🔬 How It Works
        
        1. **Data Collection**: Gathers historical price, volume, and technical indicators
        2. **Pattern Learning**: The AI model studies patterns over the lookback period (e.g., 60 days)
        3. **Training**: The model learns relationships between features (price, volume, indicators)
        4. **Prediction**: Uses learned patterns to forecast future prices
        5. **Confidence Intervals**: Shows uncertainty range around predictions
        
        ### ✅ Benefits & Use Cases
        
        **When to Use Deep Learning Predictions:**
        - 📈 **Short to Medium-term Trading**: Predict price movements for next 1-30 days
        - 🎯 **Entry/Exit Planning**: Identify potential entry and exit points
        - 📊 **Trend Confirmation**: Validate your analysis with AI insights
        - 🔄 **Swing Trading**: Plan trades based on predicted price swings
        - 📉 **Risk Assessment**: Understand potential price ranges with confidence intervals
        
        **Real-World Applications:**
        - A swing trader uses 5-day predictions to plan weekly trades
        - An investor checks 30-day forecasts before making position entries
        - A day trader uses confidence intervals to set stop-loss levels
        - A portfolio manager combines AI predictions with fundamental analysis
        
        ### ⚠️ Limitations & What AI CANNOT Do
        
        **Important Considerations:**
        - ❌ **Cannot predict black swan events**: Sudden news, policy changes, market crashes
        - ❌ **Not 100% accurate**: Markets are influenced by countless factors
        - ❌ **Historical patterns may not repeat**: Past performance ≠ future results
        - ❌ **Cannot replace due diligence**: Always research before investing
        - ❌ **Short-term noise**: Very short predictions (1-2 days) can be unreliable
        
        ### 🎓 Making Informed Decisions
        
        **Best Practices:**
        1. ✅ Use predictions as **ONE input**, not the only factor
        2. ✅ Combine with **fundamental analysis** (company financials, industry trends)
        3. ✅ Watch **market news** and events that AI can't predict
        4. ✅ Use **confidence intervals** to understand prediction reliability
        5. ✅ Start with **small positions** when testing predictions
        6. ✅ Always use **stop-loss** orders to protect capital
        7. ✅ **Backtest** your strategy before real trading
        
        **Decision Framework:**
        ```
        AI Prediction (Bullish) + Strong Fundamentals + Positive News = 🟢 Strong Buy Signal
        AI Prediction (Bullish) + Weak Fundamentals + Negative News = 🟡 Hold/Cautious
        AI Prediction (Bearish) + Strong Fundamentals = 🟡 Wait and Watch
        AI Prediction (Bearish) + Weak Fundamentals = 🔴 Avoid/Exit
        ```
        
        ### 💡 Quick Start Guide
        
        **For Beginners:**
        1. Start with **LSTM (Fast)** model
        2. Use **default settings** (60-day lookback, 50 epochs)
        3. Predict **5-7 days** ahead (not too short, not too long)
        4. Check **confidence intervals** - wider = less certain
        5. Compare predictions with **current market sentiment**
        
        **For Advanced Users:**
        1. Try **LSTM (Deep)** or **Bidirectional LSTM** for better accuracy
        2. Experiment with **feature selection** to see what works
        3. Use **longer lookback periods** (90-120 days) for better context
        4. Compare **multiple model predictions** to find consensus
        5. Analyze **feature importance** to understand model decisions
        
        ### 📊 Understanding Model Types
        
        | Model | Speed | Accuracy | Best For | Training Time |
        |-------|-------|----------|----------|---------------|
        | LSTM (Fast) | ⚡⚡⚡ | ⭐⭐⭐ | Quick analysis | 1-2 min |
        | LSTM (Deep) | ⚡⚡ | ⭐⭐⭐⭐ | Detailed analysis | 3-5 min |
        | GRU | ⚡⚡⚡ | ⭐⭐⭐⭐ | Balanced | 2-3 min |
        | Bidirectional | ⚡ | ⭐⭐⭐⭐⭐ | Best accuracy | 5-7 min |
        | Hybrid | ⚡ | ⭐⭐⭐⭐ | Experimental | 7-10 min |
        
        ---
        **💬 Remember**: AI is a powerful tool, but YOU make the final decision. Use it wisely! 
        """)


def render_model_info(title: str, description: str, pros: list, cons: list, use_case: str):
    """Render model information card with pros, cons, and use cases."""
    
    st.markdown(f"**{title}**")
    st.caption(description)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**✅ Pros:**")
        for pro in pros:
            st.markdown(f"- {pro}")
    
    with col2:
        st.markdown("**❌ Cons:**")
        for con in cons:
            st.markdown(f"- {con}")
    
    st.markdown(f"**🎯 Best For:** {use_case}")
    st.markdown("---")


def display_prediction_results(prediction: dict, symbol: str, theme_colors: dict, 
                               show_confidence: bool, show_features: bool, 
                               model_type: str, features_used: list):
    """Display comprehensive LSTM prediction results with educational insights."""
    
    st.success(f"✅ {model_type} training complete! Model is ready.")
    
    # Model performance metrics
    st.markdown("### 📊 Model Performance Metrics")
    st.caption("These metrics tell you how well the model learned from historical data")
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        rmse = prediction.get('rmse', 0)
        st.metric("RMSE (₹)", f"{rmse:.2f}")
        st.caption("Lower = Better. Average prediction error")
    
    with metric_col2:
        mae = prediction.get('mae', 0)
        st.metric("MAE (₹)", f"{mae:.2f}")
        st.caption("Mean absolute error in rupees")
    
    with metric_col3:
        r2 = prediction.get('r2_score', 0)
        st.metric("R² Score", f"{r2:.3f}")
        if r2 > 0.8:
            st.caption("🟢 Excellent fit")
        elif r2 > 0.6:
            st.caption("🟡 Good fit")
        else:
            st.caption("🔴 Weak fit - be cautious")
    
    with metric_col4:
        accuracy = prediction.get('direction_accuracy', 0)
        st.metric("Direction Accuracy", f"{accuracy:.1f}%")
        if accuracy > 60:
            st.caption("🟢 Good directional prediction")
        else:
            st.caption("🟡 Use with caution")
    
    # Interpretation guide
    with st.expander("📖 How to Interpret These Metrics", expanded=False):
        st.markdown("""
        **RMSE & MAE (Error Metrics):**
        - These show the average prediction error in rupees
        - Lower values = more accurate predictions
        - Compare with stock's daily price range to gauge significance
        - Example: If RMSE = ₹20 and stock trades ₹1800-₹1850 daily, that's ~1% error (good!)
        
        **R² Score (Model Fit):**
        - Measures how well model explains price variations (0 to 1 scale)
        - > 0.8: Excellent - model captured patterns well
        - 0.6-0.8: Good - reasonable fit
        - < 0.6: Weak - be cautious, predictions may be unreliable
        
        **Direction Accuracy:**
        - Percentage of times model correctly predicted if price goes up or down
        - > 60%: Good - better than random chance
        - 50-60%: Fair - usable but combine with other analysis
        - < 50%: Poor - model struggling, try different parameters
        """)
    
    # Price prediction forecast chart
    st.markdown("### 📈 Price Prediction Forecast")
    
    # Create dual-panel chart
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        subplot_titles=('Price Forecast', 'Prediction Confidence'),
        vertical_spacing=0.1
    )
    
    # Historical prices
    if 'historical_dates' in prediction and 'historical_prices' in prediction:
        fig.add_trace(go.Scatter(
            x=prediction['historical_dates'][-60:],  # Show last 60 days
            y=prediction['historical_prices'][-60:],
            name='Historical Price',
            line=dict(color='#667eea', width=2),
            hovertemplate='%{x}<br>Price: ₹%{y:.2f}<extra></extra>'
        ), row=1, col=1)
    
    # Forecast prices
    if 'forecast_dates' in prediction and 'forecast_prices' in prediction:
        fig.add_trace(go.Scatter(
            x=prediction['forecast_dates'],
            y=prediction['forecast_prices'],
            name='Predicted Price',
            line=dict(color='#48bb78', width=3, dash='dash'),
            hovertemplate='%{x}<br>Predicted: ₹%{y:.2f}<extra></extra>'
        ), row=1, col=1)
        
        # Add confidence intervals
        if show_confidence and 'forecast_upper' in prediction and 'forecast_lower' in prediction:
            # Upper bound
            fig.add_trace(go.Scatter(
                x=prediction['forecast_dates'],
                y=prediction['forecast_upper'],
                name='Upper Bound',
                line=dict(color='rgba(72,187,120,0.3)', width=1, dash='dot'),
                showlegend=False,
                hovertemplate='Upper: ₹%{y:.2f}<extra></extra>'
            ), row=1, col=1)
            
            # Lower bound
            fig.add_trace(go.Scatter(
                x=prediction['forecast_dates'],
                y=prediction['forecast_lower'],
                name='Lower Bound',
                line=dict(color='rgba(72,187,120,0.3)', width=1, dash='dot'),
                fill='tonexty',
                fillcolor='rgba(72,187,120,0.2)',
                showlegend=True,
                hovertemplate='Lower: ₹%{y:.2f}<extra></extra>'
            ), row=1, col=1)
            
            # Confidence width visualization
            confidence_width = [
                ((prediction['forecast_upper'][i] - prediction['forecast_lower'][i]) / 
                 prediction['forecast_prices'][i] * 100)
                for i in range(len(prediction['forecast_prices']))
            ]
            
            fig.add_trace(go.Bar(
                x=prediction['forecast_dates'],
                y=confidence_width,
                name='Uncertainty (%)',
                marker_color='#f6ad55',
                hovertemplate='%{x}<br>Uncertainty: %{y:.1f}%<extra></extra>'
            ), row=2, col=1)
    
    fig.update_layout(
        title=f"{symbol} - {model_type} Prediction",
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        xaxis2_title="Date",
        yaxis2_title="Uncertainty %",
        height=700,
        hovermode='x unified',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Prediction analysis and interpretation
    st.markdown("### 🔍 Prediction Analysis")
    
    if 'forecast_prices' in prediction and len(prediction['forecast_prices']) > 0:
        current_price = prediction['historical_prices'][-1]
        predicted_price = prediction['forecast_prices'][-1]
        price_change = predicted_price - current_price
        price_change_pct = (price_change / current_price) * 100
        
        analysis_col1, analysis_col2, analysis_col3 = st.columns(3)
        
        with analysis_col1:
            st.metric(
                "Current Price",
                f"₹{current_price:.2f}",
                help="Last available price in historical data"
            )
        
        with analysis_col2:
            st.metric(
                f"Predicted Price (Day {len(prediction['forecast_prices'])})",
                f"₹{predicted_price:.2f}",
                delta=f"{price_change_pct:+.2f}%",
                delta_color="normal"
            )
        
        with analysis_col3:
            trend = "📈 Bullish" if price_change > 0 else "📉 Bearish"
            confidence_level = "High" if r2 > 0.8 else "Medium" if r2 > 0.6 else "Low"
            st.metric(
                "Prediction Trend",
                trend,
                delta=f"Confidence: {confidence_level}"
            )
        
        # Trading suggestion based on prediction
        st.markdown("#### 💡 AI-Based Trading Suggestion")
        
        if price_change_pct > 5 and r2 > 0.7:
            suggestion = "🟢 **Strong Buy Signal**"
            details = f"Model predicts {price_change_pct:.1f}% upside with good confidence (R²={r2:.2f})"
        elif price_change_pct > 2 and r2 > 0.6:
            suggestion = "🟢 **Buy Signal**"
            details = f"Model shows {price_change_pct:.1f}% potential upside"
        elif price_change_pct < -5 and r2 > 0.7:
            suggestion = "🔴 **Strong Sell Signal**"
            details = f"Model predicts {abs(price_change_pct):.1f}% downside with good confidence"
        elif price_change_pct < -2 and r2 > 0.6:
            suggestion = "🔴 **Sell Signal**"
            details = f"Model shows {abs(price_change_pct):.1f}% potential downside"
        else:
            suggestion = "🟡 **Hold/Neutral**"
            details = "Model predicts limited price movement or low confidence"
        
        st.info(f"{suggestion}\n\n{details}")
        
        st.warning("""
        ⚠️ **Action Items Before Trading:**
        1. ✅ Check latest company news and announcements
        2. ✅ Review fundamental metrics (P/E, earnings, debt)
        3. ✅ Analyze market sentiment and sector trends
        4. ✅ Set appropriate stop-loss (suggested: -5% to -8%)
        5. ✅ Consider position sizing (don't go all-in!)
        6. ✅ Compare with other technical indicators
        """)
    
    # Detailed forecast table
    if 'forecast_dates' in prediction and 'forecast_prices' in prediction:
        st.markdown("### 📋 Detailed Daily Forecast")
        
        forecast_data = []
        for i, (date, price) in enumerate(zip(prediction['forecast_dates'], prediction['forecast_prices'])):
            change = ((price - prediction['forecast_prices'][i-1]) / prediction['forecast_prices'][i-1] * 100) if i > 0 else 0
            
            row = {
                'Day': i + 1,
                'Date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date),
                'Predicted Price': f"₹{price:.2f}",
                'Daily Change': f"{change:+.2f}%"
            }
            
            if show_confidence and 'forecast_upper' in prediction and 'forecast_lower' in prediction:
                row['Range'] = f"₹{prediction['forecast_lower'][i]:.2f} - ₹{prediction['forecast_upper'][i]:.2f}"
                uncertainty = ((prediction['forecast_upper'][i] - prediction['forecast_lower'][i]) / price * 100)
                row['Uncertainty'] = f"{uncertainty:.1f}%"
            
            forecast_data.append(row)
        
        forecast_df = pd.DataFrame(forecast_data)
        st.dataframe(forecast_df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = forecast_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Forecast as CSV",
            data=csv,
            file_name=f"{symbol}_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Feature importance analysis
    if show_features and 'feature_importance' in prediction:
        st.markdown("### 📊 Feature Importance Analysis")
        st.caption("Which factors influenced the model's predictions the most?")
        
        importance_data = prediction['feature_importance']
        
        # Create bar chart
        fig_importance = go.Figure(go.Bar(
            x=list(importance_data.values()),
            y=list(importance_data.keys()),
            orientation='h',
            marker_color='#667eea',
            text=[f"{v:.1%}" for v in importance_data.values()],
            textposition='auto',
        ))
        
        fig_importance.update_layout(
            title="Feature Importance - What Drives the Predictions?",
            xaxis_title="Importance Score",
            yaxis_title="Feature",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig_importance, use_container_width=True)
        
        with st.expander("📖 Understanding Feature Importance"):
            st.markdown("""
            **What does this mean?**
            - Features with higher scores have more influence on predictions
            - The model relies more heavily on these factors when forecasting
            - If price/close is dominant: Model is trend-following
            - If volume is high: Trading activity matters
            - If technical indicators are high: Pattern-based prediction
            
            **How to use this:**
            - Focus on monitoring high-importance features
            - If volume is important but current volume is low → predictions less reliable
            - If RSI is important → watch for overbought/oversold conditions
            - Helps you understand the "why" behind predictions
            """)
    
    # Model confidence summary
    st.markdown("### 🎯 Prediction Confidence Summary")
    
    confidence_col1, confidence_col2 = st.columns(2)
    
    with confidence_col1:
        st.markdown("**✅ Confidence Boosters:**")
        boosters = []
        if r2 > 0.7:
            boosters.append("• High R² score - good model fit")
        if accuracy > 60:
            boosters.append("• Direction accuracy above 60%")
        if prediction.get('rmse', 999) / current_price < 0.02:
            boosters.append("• Low error relative to price")
        
        if boosters:
            for booster in boosters:
                st.markdown(booster)
        else:
            st.markdown("• Limited confidence boosters")
    
    with confidence_col2:
        st.markdown("**⚠️ Confidence Concerns:**")
        concerns = []
        if r2 < 0.6:
            concerns.append("• R² score below 0.6 - weak fit")
        if accuracy < 55:
            concerns.append("• Low direction accuracy")
        if show_confidence and 'forecast_upper' in prediction:
            avg_uncertainty = np.mean([
                (prediction['forecast_upper'][i] - prediction['forecast_lower'][i]) / 
                prediction['forecast_prices'][i] * 100
                for i in range(len(prediction['forecast_prices']))
            ])
            if avg_uncertainty > 10:
                concerns.append(f"• High uncertainty ({avg_uncertainty:.1f}% avg)")
        
        if concerns:
            for concern in concerns:
                st.markdown(concern)
        else:
            st.markdown("• No major concerns detected")
    
    # Final recommendation
    st.markdown("---")
    st.markdown("### 🎓 Final Recommendation")
    
    if r2 > 0.7 and accuracy > 60:
        st.success("""
        ✅ **High Confidence Prediction**
        - Model performance is strong
        - Predictions can be used as a primary input
        - Still combine with fundamental analysis and news
        - Set stop-loss orders to manage risk
        """)
    elif r2 > 0.5 and accuracy > 55:
        st.info("""
        ℹ️ **Moderate Confidence Prediction**
        - Model shows reasonable performance
        - Use predictions as a secondary confirmation
        - Give more weight to fundamentals and market conditions
        - Be conservative with position sizing
        """)
    else:
        st.warning("""
        ⚠️ **Low Confidence Prediction**
        - Model performance is weak for this stock
        - Do NOT rely primarily on these predictions
        - Consider: Different stock, more data, simpler model
        - If trading, use very small position sizes
        """)
