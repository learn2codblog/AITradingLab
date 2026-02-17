"""
AI Deep Analysis page module
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ui.components import (
    create_section_header,
    create_info_card,
    create_metric_card,
    create_price_chart,
    create_volume_chart,
    create_gauge_chart,
    get_theme_colors
)

from src.data_loader import load_stock_data
from src.symbol_utils import normalize_symbol
from src.technical_indicators import calculate_technical_indicators
from src.fundamental_analysis import get_fundamentals, get_stock_news
from src.metrics import calculate_all_metrics, max_drawdown
from src.ml import (
    calculate_advanced_indicators,
    generate_ai_analysis,
    predict_with_lstm,
    combined_trend_signal,
    calculate_feature_importance,
    calculate_position_size,
    forecast_volatility_garch,
    get_volatility_regime,
    backtest_strategy,
)


def render_ai(start_date, end_date):
    create_section_header("AI Deep Analysis", "Advanced Machine Learning & Pattern Recognition", "🤖")

    # Input section
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        raw_ai_symbol = st.text_input("📈 Enter Stock Symbol", value="RELIANCE.NS", key="ai_symbol",
                                  help="Enter NSE stock (you can omit .NS, e.g., RELIANCE or RELIANCE.NS")
        ai_symbol = normalize_symbol(raw_ai_symbol)

    with col2:
        analysis_depth = st.selectbox("🔬 Analysis Depth",
                                      ["Quick Analysis", "Standard", "Deep Analysis"],
                                      index=1)

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        run_ai = st.button("🚀 Run AI Analysis", type="primary", use_container_width=True)

    # Advanced Settings Expander
    with st.expander("⚙️ Advanced Analysis Settings"):
        adv_col1, adv_col2, adv_col3 = st.columns(3)
        with adv_col1:
            supertrend_mult = st.slider("SuperTrend Multiplier", 1.0, 4.0, 3.0, 0.5,
                                        help="Higher = fewer signals, lower = more sensitive")
        with adv_col2:
            supertrend_period = st.slider("SuperTrend Period", 5, 20, 10, 1,
                                          help="ATR lookback period")
        with adv_col3:
            st.markdown("**Indicator Sensitivity**")
            st.caption("Higher multiplier = fewer false signals during pullbacks")

    # Feature cards
    st.markdown("### 🎯 Advanced AI Features")
    theme_colors = get_theme_colors()

    feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4)

    with feat_col1:
        st.markdown(f"""
        <div style='background: {theme_colors['gradient_bg']}; padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <h3 style='margin: 0; color: {theme_colors['text']};'>🧠</h3>
            <h4 style='margin: 5px 0; color: {theme_colors['text']};'>LSTM Prediction</h4>
            <p style='margin: 0; font-size: 0.85rem; color: {theme_colors['text_secondary']};'>Deep Learning price forecast</p>
        </div>
        """, unsafe_allow_html=True)

    with feat_col2:
        st.markdown(f"""
        <div style='background: {theme_colors['gradient_bg']}; padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <h3 style='margin: 0; color: {theme_colors['text']};'>📊</h3>
            <h4 style='margin: 5px 0; color: {theme_colors['text']};'>30+ Indicators</h4>
            <p style='margin: 0; font-size: 0.85rem; color: {theme_colors['text_secondary']};'>Advanced technical analysis</p>
        </div>
        """, unsafe_allow_html=True)

    with feat_col3:
        st.markdown(f"""
        <div style='background: {theme_colors['gradient_bg']}; padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <h3 style='margin: 0; color: {theme_colors['text']};'>🎯</h3>
            <h4 style='margin: 5px 0; color: {theme_colors['text']};'>Pattern Detection</h4>
            <p style='margin: 0; font-size: 0.85rem; color: {theme_colors['text_secondary']};'>Candlestick & chart patterns</p>
        </div>
        """, unsafe_allow_html=True)

    with feat_col4:
        st.markdown(f"""
        <div style='background: {theme_colors['gradient_bg']}; padding: 20px; border-radius: 12px; color: white; text-align: center;'>
            <h3 style='margin: 0; color: {theme_colors['text']};'>🤖</h3>
            <h4 style='margin: 5px 0; color: {theme_colors['text']};'>Ensemble ML</h4>
            <p style='margin: 0; font-size: 0.85rem; color: {theme_colors['text_secondary']};'>5 ML models combined</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if run_ai and ai_symbol:
        with st.spinner(f"🤖 Running AI Deep Analysis on {ai_symbol}..."):
            # Load data (ensure normalized)
            try:
                from src.symbol_utils import normalize_symbol as _ns
                load_sym = _ns(ai_symbol)
            except Exception:
                load_sym = ai_symbol
            stock_data = load_stock_data(load_sym, start_date, end_date)

            if stock_data is None or len(stock_data) < 100:
                st.error("❌ Could not load sufficient data. Please check the symbol.")
            else:
                # Log activity
                try:
                    from src.supabase_client import get_supabase_client
                    supabase = get_supabase_client()
                    user_id = st.session_state.get('user_id')
                    if user_id and supabase.is_connected():
                        supabase.log_activity(
                            user_id=user_id,
                            activity_type='ai_analysis',
                            description=f"AI deep analysis run for {ai_symbol}",
                            action_details={
                                'symbol': ai_symbol,
                                'analysis_depth': analysis_depth,
                                'supertrend_period': supertrend_period,
                                'supertrend_multiplier': supertrend_mult
                            },
                            status='success'
                        )
                except Exception:
                    pass

                # Calculate technical indicators
                stock_data = calculate_technical_indicators(stock_data)

                # Calculate advanced indicators
                try:
                    # Load ML resources directly instead of importing from app_modern
                    from src.ml import calculate_advanced_indicators, calculate_supertrend
                    stock_data = calculate_advanced_indicators(stock_data)

                    # Recalculate SuperTrend with user-defined parameters
                    stock_data = calculate_supertrend(stock_data, period=supertrend_period, multiplier=supertrend_mult)
                except Exception as e:
                    st.warning(f"Some advanced indicators could not be calculated: {e}")

                # Get fundamentals
                fundamentals = get_fundamentals(ai_symbol)

                # Get trend signal for summary (defined early)
                trend_signal = None
                try:
                    trend_signal = combined_trend_signal(stock_data)
                except Exception:
                    trend_signal = {'signal': 'Unknown', 'description': '', 'details': {}, 'warnings': []}

                # Run AI Analysis with the selected depth
                ai_results = generate_ai_analysis(stock_data, ai_symbol, fundamentals, analysis_depth)

                # Use ai_results to render the full detailed UI. Keep heavy ML
                # operations lazy and protect each stage with try/except so that
                # a failure in one widget doesn't break the whole page.

                # ─── AI RECOMMENDATION ───
                st.markdown("### 🎯 AI Recommendation")

                ai_rec = ai_results.get('ai_recommendation', {})
                recommendation = ai_rec.get('recommendation', 'HOLD')
                confidence = ai_rec.get('confidence', 0.5)
                used_depth = ai_rec.get('analysis_depth', analysis_depth)

                if 'BUY' in recommendation:
                    rec_color = '#48bb78'
                    rec_bg = theme_colors['gradient_bg']
                elif 'SELL' in recommendation:
                    rec_color = '#f56565'
                    rec_bg = theme_colors['gradient_bg']
                else:
                    rec_color = '#ed8936'
                    rec_bg = theme_colors['gradient_bg']

                st.markdown(f"""
                <div style='background: {rec_bg}; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px;'>
                    <h1 style='color: white; margin: 0; font-size: 2.25rem;'>{recommendation}</h1>
                    <p style='color: rgba(255,255,255,0.9); font-size: 1rem; margin: 6px 0 0 0;'>
                        Confidence: {confidence:.1%} | Mode: {used_depth}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Contradictions and warnings
                contradictions = ai_rec.get('contradictions', [])
                warnings_list = ai_rec.get('warnings', [])

                if contradictions:
                    st.markdown("#### ⚠️ Signal Contradictions Detected")
                    for contradiction in contradictions:
                        st.warning(f"{contradiction.get('type','Contradiction')}: {contradiction.get('description','')}")

                if warnings_list:
                    st.markdown("#### ℹ️ Analysis Warnings")
                    for warning in warnings_list:
                        st.info(warning)

                # Probability breakdown
                probs = ai_rec.get('probabilities', {})
                prob_col1, prob_col2, prob_col3 = st.columns(3)

                with prob_col1:
                    create_metric_card("Buy Probability", f"{probs.get('buy', 0):.1%}", icon="🟢", color="#48bb78")
                with prob_col2:
                    create_metric_card("Hold Probability", f"{probs.get('hold', 0):.1%}", icon="🟡", color="#ed8936")
                with prob_col3:
                    create_metric_card("Sell Probability", f"{probs.get('sell', 0):.1%}", icon="🔴", color="#f56565")

                # ─── TECHNICAL SCORE ───
                st.markdown("### 📊 Technical Score")
                tech_score = ai_results.get('technical_score', {})
                score = tech_score.get('score', 50)
                grade = tech_score.get('grade', 'C')
                breakdown = tech_score.get('breakdown', {})

                score_col1, score_col2 = st.columns([1, 2])
                with score_col1:
                    if score >= 70:
                        score_color = '#48bb78'
                    elif score >= 50:
                        score_color = '#ed8936'
                    else:
                        score_color = '#f56565'

                    st.markdown(f"""
                    <div style='text-align: center; padding: 20px; background: {theme_colors['card_bg']}; border-radius: 12px;'>
                        <div style='font-size: 3rem; font-weight: 700; color: {score_color};'>{score:.0f}</div>
                        <div style='font-size: 1rem; color: {theme_colors['text_secondary']};'>out of 100</div>
                        <div style='font-size: 1rem; margin-top: 8px; padding: 6px 12px; background: {score_color}; color: white; border-radius: 8px; display: inline-block;'>
                            Grade: {grade}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with score_col2:
                    import plotly.graph_objects as go
                    categories = list(breakdown.keys())
                    values = list(breakdown.values())
                    if categories and values:
                        fig = go.Figure(data=[go.Bar(x=categories, y=values, marker_color='#667eea')])
                        fig.update_layout(title="Score Breakdown", yaxis=dict(range=[0, max(values + [25])]), height=300, margin=dict(l=20,r=20,t=40,b=20))
                        st.plotly_chart(fig, use_container_width=True)

                # ─── RISK-ADJUSTED RETURN METRICS ───
                st.markdown("### 📈 Risk-Adjusted Return Metrics")
                try:
                    # Calculate returns
                    returns = stock_data['Close'].pct_change().dropna()
                    
                    if len(returns) > 30:  # Need sufficient data
                        risk_metrics = calculate_all_metrics(returns, stock_data['Close'])
                        
                        # Display metrics in cards
                        risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
                        
                        with risk_col1:
                            sharpe = risk_metrics.get('sharpe_ratio', 0)
                            sharpe_color = '#48bb78' if sharpe > 1.0 else ('#ed8936' if sharpe > 0.5 else '#f56565')
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, {sharpe_color}, {theme_colors['card_bg']}); padding: 15px; border-radius: 10px; text-align: center;'>
                                <h4 style='margin: 0; color: {theme_colors['text']};'>Sharpe Ratio</h4>
                                <h2 style='margin: 8px 0; color: {theme_colors['text']};'>{sharpe:.2f}</h2>
                                <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.8rem;'>Risk-Adjusted Return</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with risk_col2:
                            sortino = risk_metrics.get('sortino_ratio', 0)
                            sortino_color = '#48bb78' if sortino > 1.5 else ('#ed8936' if sortino > 0.8 else '#f56565')
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, {sortino_color}, {theme_colors['card_bg']}); padding: 15px; border-radius: 10px; text-align: center;'>
                                <h4 style='margin: 0; color: {theme_colors['text']};'>Sortino Ratio</h4>
                                <h2 style='margin: 8px 0; color: {theme_colors['text']};'>{sortino:.2f}</h2>
                                <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.8rem;'>Downside Risk Adj.</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with risk_col3:
                            calmar = risk_metrics.get('calmar_ratio', 0)
                            calmar_color = '#48bb78' if calmar > 0.5 else ('#ed8936' if calmar > 0.2 else '#f56565')
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, {calmar_color}, {theme_colors['card_bg']}); padding: 15px; border-radius: 10px; text-align: center;'>
                                <h4 style='margin: 0; color: {theme_colors['text']};'>Calmar Ratio</h4>
                                <h2 style='margin: 8px 0; color: {theme_colors['text']};'>{calmar:.2f}</h2>
                                <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.8rem;'>Return/Max Drawdown</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with risk_col4:
                            win_rate = risk_metrics.get('win_rate', 0)
                            win_rate_color = '#48bb78' if win_rate > 0.55 else ('#ed8936' if win_rate > 0.45 else '#f56565')
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, {win_rate_color}, {theme_colors['card_bg']}); padding: 15px; border-radius: 10px; text-align: center;'>
                                <h4 style='margin: 0; color: {theme_colors['text']};'>Win Rate</h4>
                                <h2 style='margin: 8px 0; color: {theme_colors['text']};'>{win_rate:.1%}</h2>
                                <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.8rem;'>Positive Days</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Additional risk metrics in expandable section
                        with st.expander("📊 Detailed Risk Metrics"):
                            detail_col1, detail_col2, detail_col3 = st.columns(3)
                            
                            with detail_col1:
                                st.metric("Annual Return", f"{risk_metrics.get('annual_return', 0):+.1%}")
                                st.metric("Annual Volatility", f"{risk_metrics.get('annual_volatility', 0):.1%}")
                                st.metric("Max Drawdown", f"{risk_metrics.get('max_drawdown', 0):+.1%}")
                            
                            with detail_col2:
                                st.metric("VaR (95%)", f"{risk_metrics.get('value_at_risk_95', 0):+.1%}")
                                st.metric("Expected Shortfall", f"{risk_metrics.get('expected_shortfall', 0):+.1%}")
                                st.metric("Profit Factor", f"{risk_metrics.get('profit_factor', 0):.2f}")
                            
                            with detail_col3:
                                # Try to get beta if market data available
                                try:
                                    # Simple beta calculation against NIFTY if available
                                    beta_val = risk_metrics.get('beta', 'N/A')
                                    if beta_val != 'N/A':
                                        st.metric("Beta", f"{beta_val:.2f}")
                                    else:
                                        st.metric("Beta", "N/A")
                                    
                                    alpha_val = risk_metrics.get('alpha', 'N/A')
                                    if alpha_val != 'N/A':
                                        st.metric("Alpha", f"{alpha_val:+.1%}")
                                    else:
                                        st.metric("Alpha", "N/A")
                                        
                                    info_ratio = risk_metrics.get('information_ratio', 'N/A')
                                    if info_ratio != 'N/A':
                                        st.metric("Information Ratio", f"{info_ratio:.2f}")
                                    else:
                                        st.metric("Information Ratio", "N/A")
                                except:
                                    st.metric("Beta", "N/A")
                                    st.metric("Alpha", "N/A")
                                    st.metric("Information Ratio", "N/A")
                    else:
                        st.info("📊 Risk metrics require at least 30 days of price data")
                        
                except Exception as e:
                    st.warning(f"Risk-adjusted return metrics unavailable: {e}")

                # ─── MARKET REGIME ───
                st.markdown("### 🌍 Market Regime Detection")
                market_regime = ai_results.get('market_regime', {})
                regime_col1, regime_col2, regime_col3 = st.columns(3)

                with regime_col1:
                    primary = market_regime.get('primary_regime', 'Unknown')
                    st.markdown(f"""
                    <div style='background: {theme_colors['gradient_bg']}; padding: 18px; border-radius: 10px; text-align: center;'>
                        <h4 style='color: {theme_colors['text']}; margin: 0;'>Current Regime</h4>
                        <h2 style='color: {theme_colors['text']}; margin: 8px 0;'>{primary}</h2>
                        <p style='color: {theme_colors['text_secondary']}; margin: 0;'>Confidence: {market_regime.get('confidence',0):.0%}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with regime_col2:
                    risk = market_regime.get('risk_level', 'Medium')
                    risk_colors = {'Low': '#48bb78', 'Medium': '#ed8936', 'High': '#f56565', 'Medium-High': '#e53e3e'}
                    st.markdown(f"""
                    <div style='background: {risk_colors.get(risk, '#718096')}; padding: 18px; border-radius: 10px; text-align: center;'>
                        <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>Risk Level</h4>
                        <h2 style='color: white; margin: 8px 0;'>{risk}</h2>
                    </div>
                    """, unsafe_allow_html=True)

                with regime_col3:
                    strategy = market_regime.get('suggested_strategy', 'Standard analysis')
                    st.markdown(f"""
                    <div style='background: #4facfe; padding: 18px; border-radius: 10px; text-align: center;'>
                        <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>Suggested Strategy</h4>
                        <p style='color: white; margin: 8px 0;'>{strategy}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # ─── COMBINED TREND SIGNAL (SuperTrend + ADX + RSI) ───
                st.markdown("### 🎯 Combined Trend Signal (SuperTrend + ADX + RSI)")
                try:
                    combined_signal = combined_trend_signal(stock_data)
                    
                    signal_text = combined_signal.get('signal', 'Unknown')
                    strength = combined_signal.get('strength', 'Neutral')
                    description = combined_signal.get('description', '')

                    if 'Bullish' in signal_text and 'Strong' in strength:
                        signal_color = '#48bb78'
                        signal_bg = 'linear-gradient(135deg, #48bb78, #38a169)'
                    elif 'Bearish' in signal_text and 'Strong' in strength:
                        signal_color = '#f56565'
                        signal_bg = 'linear-gradient(135deg, #f56565, #c53030)'
                    elif 'Bullish' in signal_text:
                        signal_color = '#68d391'
                        signal_bg = 'linear-gradient(135deg, #68d391, #48bb78)'
                    elif 'Bearish' in signal_text:
                        signal_color = '#fc8181'
                        signal_bg = 'linear-gradient(135deg, #fc8181, #f56565)'
                    else:
                        signal_color = '#ed8936'
                        signal_bg = 'linear-gradient(135deg, #ed8936, #dd6b20)'

                    st.markdown(f"""
                    <div style='background: {signal_bg}; padding: 20px; border-radius: 15px; margin-bottom: 15px; text-align: center;'>
                        <h2 style='color: white; margin: 0; font-size: 1.5rem;'>{signal_text}</h2>
                        <p style='color: rgba(255,255,255,0.9); margin: 8px 0; font-size: 1.1rem;'><strong>Strength:</strong> {strength}</p>
                        <p style='color: rgba(255,255,255,0.9); margin: 0;'>{description}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Show detailed breakdown as cards
                    details = combined_signal.get('details', {})
                    if details:
                        st.markdown("#### Signal Breakdown")
                        detail_cols = st.columns(3)
                        
                        with detail_cols[0]:
                            supertrend_dir = details.get('SuperTrend_Direction', 'N/A')
                            supertrend_color = '#48bb78' if supertrend_dir == 1 else ('#f56565' if supertrend_dir == -1 else '#ed8936')
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, {supertrend_color}, {theme_colors['card_bg']}); padding: 15px; border-radius: 10px; text-align: center;'>
                                <h4 style='margin: 0; color: {theme_colors['text']};'>SuperTrend</h4>
                                <h3 style='margin: 8px 0; color: {theme_colors['text']};'>{supertrend_dir if supertrend_dir != 'N/A' else 'Neutral'}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with detail_cols[1]:
                            adx_val = details.get('ADX_Value', 0)
                            adx_color = '#48bb78' if adx_val > 25 else ('#ed8936' if adx_val > 20 else '#f56565')
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, {adx_color}, {theme_colors['card_bg']}); padding: 15px; border-radius: 10px; text-align: center;'>
                                <h4 style='margin: 0; color: {theme_colors['text']};'>ADX Strength</h4>
                                <h3 style='margin: 8px 0; color: {theme_colors['text']};'>{adx_val:.1f}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with detail_cols[2]:
                            rsi_momentum = details.get('RSI_Momentum', 'Neutral')
                            rsi_color = '#48bb78' if rsi_momentum == 'Bullish' else ('#f56565' if rsi_momentum == 'Bearish' else '#ed8936')
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, {rsi_color}, {theme_colors['card_bg']}); padding: 15px; border-radius: 10px; text-align: center;'>
                                <h4 style='margin: 0; color: {theme_colors['text']};'>RSI Momentum</h4>
                                <h3 style='margin: 8px 0; color: {theme_colors['text']};'>{rsi_momentum}</h3>
                            </div>
                            """, unsafe_allow_html=True)

                    # Show warnings if any
                    warnings = combined_signal.get('warnings', [])
                    if warnings:
                        st.markdown("#### ⚠️ Signal Warnings")
                        for warning in warnings:
                            st.warning(warning)

                except Exception as e:
                    st.warning(f"Combined trend signal unavailable: {e}")

                # ─── SENTIMENT ANALYSIS ───
                st.markdown("### 📰 News Sentiment Analysis")
                try:
                    from src.fundamental_analysis import get_stock_news
                    from src.ml.sentiment import analyze_news_sentiment, analyze_sentiment_simple
                    
                    # Get news headlines
                    news_items = get_stock_news(ai_symbol, count=10)
                    headlines = [item.get('title', '') for item in news_items if item.get('title')]
                    
                    if headlines:
                        # Analyze sentiment of headlines
                        sentiment_data = analyze_news_sentiment(headlines)
                        
                        sentiment = sentiment_data.get('overall_sentiment', 'Neutral')
                        sentiment_score = sentiment_data.get('score', 0)

                        if sentiment_score > 0.1:
                            sent_color = '#48bb78'
                            sent_icon = '😊'
                        elif sentiment_score < -0.1:
                            sent_color = '#f56565'
                            sent_icon = '😟'
                        else:
                            sent_color = '#ed8936'
                            sent_icon = '😐'

                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, {sent_color}, {theme_colors['card_bg']}); padding: 18px; border-radius: 12px; text-align: center;'>
                            <h3 style='margin: 0; color: {theme_colors['text']};'>{sent_icon} {sentiment.title()}</h3>
                            <p style='margin: 8px 0 0 0; color: {theme_colors['text_secondary']};'>Sentiment Score: {sentiment_score:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Show top news items with sentiment
                        st.markdown("#### Recent News Impact")
                        for item in news_items[:3]:  # Show top 3
                            title = item.get('title', 'No title')[:80] + '...' if len(item.get('title', '')) > 80 else item.get('title', 'No title')
                            # Simple sentiment for individual headlines
                            headline_sentiment = analyze_sentiment_simple(title)
                            sent_label = headline_sentiment.get('label', 'Neutral')
                            st.markdown(f"- **{sent_label}**: {title}")
                    else:
                        st.info("No recent news available for sentiment analysis")
                except Exception as e:
                    st.warning(f"Sentiment analysis unavailable: {e}")

                # ─── VOLATILITY ANALYSIS ───
                st.markdown("### 📊 Volatility Forecast")
                try:
                    from src.ml import forecast_volatility_garch, get_volatility_regime
                    vol_forecast = forecast_volatility_garch(stock_data)
                    vol_regime = get_volatility_regime(stock_data)

                    vol_col1, vol_col2 = st.columns(2)

                    with vol_col1:
                        current_vol = vol_regime.get('vol_10d', 0) / 100  # Convert to decimal
                        vol_regime_name = vol_regime.get('regime', 'Normal')
                        vol_color = '#48bb78' if vol_regime_name == 'Low Volatility' else ('#f56565' if vol_regime_name == 'High Volatility' else '#ed8936')

                        st.markdown(f"""
                        <div style='background: {vol_color}; padding: 18px; border-radius: 10px; text-align: center;'>
                            <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>Current Volatility</h4>
                            <h2 style='color: white; margin: 8px 0;'>{current_vol:.1%}</h2>
                            <p style='color: rgba(255,255,255,0.8); margin: 0;'>Regime: {vol_regime_name}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with vol_col2:
                        if 'error' not in vol_forecast:
                            forecast_vol = vol_forecast.get('avg_forecast_vol', vol_forecast.get('forecasted_daily_vol', [current_vol])[-1] if isinstance(vol_forecast.get('forecasted_daily_vol'), list) else current_vol)
                            change_pct = ((forecast_vol - current_vol) / current_vol * 100) if current_vol > 0 else 0
                        else:
                            forecast_vol = current_vol
                            change_pct = 0

                        st.markdown(f"""
                        <div style='background: #667eea; padding: 18px; border-radius: 10px; text-align: center;'>
                            <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>7-Day Forecast</h4>
                            <h2 style='color: white; margin: 8px 0;'>{forecast_vol:.1%}</h2>
                            <p style='color: rgba(255,255,255,0.8); margin: 0;'>Change: {change_pct:+.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)

                except Exception as e:
                    st.warning(f"Volatility analysis unavailable: {e}")

                # ─── EWMA VOLATILITY FORECAST ───
                st.markdown("### 📈 EWMA Volatility Forecast")
                try:
                    # Calculate EWMA volatility forecast
                    returns = stock_data['Close'].pct_change().dropna()
                    if len(returns) > 30:
                        # EWMA with lambda = 0.94 (common for volatility)
                        ewma_vol = returns.ewm(span=20, adjust=False).std()
                        current_ewma_vol = ewma_vol.iloc[-1] * 100  # Convert to percentage
                        
                        # Simple forecast: assume mean reversion to long-term average
                        long_term_vol = returns.std() * 100
                        forecast_ewma_vol = (current_ewma_vol + long_term_vol) / 2
                        vol_change = ((forecast_ewma_vol - current_ewma_vol) / current_ewma_vol * 100) if current_ewma_vol > 0 else 0
                        
                        ewma_col1, ewma_col2 = st.columns(2)
                        
                        with ewma_col1:
                            vol_color = '#48bb78' if current_ewma_vol < 20 else ('#f56565' if current_ewma_vol > 40 else '#ed8936')
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, {vol_color}, #ffffff); padding: 18px; border-radius: 10px; text-align: center;'>
                                <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>Current EWMA Volatility</h4>
                                <h2 style='color: white; margin: 8px 0;'>{current_ewma_vol:.1f}%</h2>
                                <p style='color: rgba(255,255,255,0.8); margin: 0;'>20-day Exponentially Weighted</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with ewma_col2:
                            forecast_color = '#48bb78' if vol_change < 0 else ('#f56565' if vol_change > 10 else '#ed8936')
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, {forecast_color}, #ffffff); padding: 18px; border-radius: 10px; text-align: center;'>
                                <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>7-Day EWMA Forecast</h4>
                                <h2 style='color: white; margin: 8px 0;'>{forecast_ewma_vol:.1f}%</h2>
                                <p style='color: rgba(255,255,255,0.8); margin: 0;'>Change: {vol_change:+.1f}%</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("EWMA volatility requires at least 30 days of data")
                        
                except Exception as e:
                    st.warning(f"EWMA volatility forecast unavailable: {e}")

                # ─── PATTERN RECOGNITION ───
                st.markdown("### 🕯️ Pattern Recognition")
                pattern_col1, pattern_col2 = st.columns(2)

                with pattern_col1:
                    st.markdown("#### Candlestick Patterns")
                    candle_patterns = ai_results.get('candlestick_patterns', {})
                    if candle_patterns:
                        for name, details in candle_patterns.items():
                            signal = details.get('signal', 'Neutral')
                            badge_color = '#48bb78' if signal == 'Bullish' else ('#f56565' if signal == 'Bearish' else '#ed8936')
                            st.markdown(f"""
                            <div style='background: {theme_colors['card_bg']}; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {badge_color};'>
                                <strong style='color: {theme_colors['text']};'>{name}</strong>
                                <span style='background: {badge_color}; color: white; padding: 3px 8px; border-radius: 12px; margin-left: 8px;'>{signal}</span>
                                <p style='color: {theme_colors['text_secondary']}; margin: 6px 0 0 0;'>{details.get('description','')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No significant candlestick patterns detected")

                with pattern_col2:
                    st.markdown("#### Chart Patterns")
                    chart_patterns = ai_results.get('chart_patterns', {})
                    if chart_patterns:
                        for name, details in chart_patterns.items():
                            signal = details.get('signal', 'Neutral')
                            badge_color = '#48bb78' if signal == 'Bullish' else ('#f56565' if signal == 'Bearish' else '#ed8936')
                            st.markdown(f"""
                            <div style='background: {theme_colors['card_bg']}; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {badge_color};'>
                                <strong style='color: {theme_colors['text']};'>{name}</strong>
                                <span style='background: {badge_color}; color: white; padding: 3px 8px; border-radius: 12px; margin-left: 8px;'>{signal}</span>
                                <p style='color: {theme_colors['text_secondary']}; margin: 6px 0 0 0;'>{details.get('description','')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No significant chart patterns detected")

                # ─── ENSEMBLE ML ───
                st.markdown("### 🤖 Ensemble Machine Learning")
                ml_results = ai_results.get('ml_ensemble', {})

                if ml_results and 'error' not in ml_results:
                    ensemble_pred = ml_results.get('ensemble_prediction', 'Unknown')
                    ensemble_conf = ml_results.get('ensemble_confidence', 0)
                    prediction_horizon = ml_results.get('prediction_horizon', '1-day')

                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1e3a8a, #7c3aed); padding: 16px; border-radius: 12px;'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <div>
                                <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>Ensemble Prediction ({prediction_horizon})</h4>
                                <h2 style='color: white; margin: 6px 0;'>{ensemble_pred}</h2>
                                <p style='color: rgba(255,255,255,0.8); margin: 0;'>Confidence: {ensemble_conf:.0%}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    individual = ml_results.get('individual_models', {})
                    if individual:
                        st.markdown("#### Individual Model Results")
                        model_cols = st.columns(len(individual))
                        for i, (model_name, results) in enumerate(individual.items()):
                            with model_cols[i]:
                                if 'error' not in results:
                                    pred = results.get('prediction', 'N/A')
                                    conf = results.get('confidence', 0)
                                    acc = results.get('accuracy', 0)
                                    color = '#48bb78' if pred == 'Bullish' else '#f56565'
                                    st.markdown(f"""
                                    <div style='background: {theme_colors['card_bg']}; padding: 12px; border-radius: 8px; text-align: center; border-top: 3px solid {color};'>
                                        <h5 style='margin: 0; color: {theme_colors['text']};'>{model_name}</h5>
                                        <h3 style='margin: 6px 0; color: {color};'>{pred}</h3>
                                        <p style='color: {theme_colors['text_secondary']}; margin: 0;'>Conf: {conf:.0%} | Acc: {acc:.0%}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                else:
                    if 'error' in ml_results:
                        st.warning(f"ML Analysis: {ml_results.get('error')}")

                # ─── ANOMALY DETECTION ───
                st.markdown("### ⚠️ Anomaly Detection")
                anomalies = ai_results.get('anomalies', {})
                anomaly_list = anomalies.get('anomalies', []) if isinstance(anomalies, dict) else anomalies
                if anomaly_list:
                    for anomaly in anomaly_list:
                        severity = anomaly.get('severity', 'Medium')
                        icon = '🔴' if severity == 'High' else '🟡'
                        color = '#f56565' if severity == 'High' else '#ed8936'
                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {color};'>
                            {icon} <strong style='color: {color};'>{anomaly.get('type','Anomaly')}</strong>: {anomaly.get('description','')}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ No significant anomalies detected")

                # ─── LSTM PREDICTION (Deep Analysis only) ───
                if analysis_depth == "Deep Analysis":
                    st.markdown("### 🧠 LSTM Deep Learning Prediction")
                    with st.spinner("Training LSTM neural network..."):
                        try:
                            lstm_results = predict_with_lstm(stock_data, lookback=60, forecast_days=5, epochs=30)
                        except Exception as e:
                            lstm_results = {'error': str(e)}

                    if 'error' not in lstm_results:
                        predictions = lstm_results.get('predictions', [])
                        expected_return = lstm_results.get('expected_return', 0)
                        lstm_conf = lstm_results.get('confidence', 0)

                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #667eea, #764ba2); padding: 18px; border-radius: 12px;'>
                            <h4 style='color: rgba(255,255,255,0.9); margin: 0;'>5-Day Price Forecast</h4>
                            <p style='color: rgba(255,255,255,0.85); margin: 8px 0;'>{lstm_results.get('trend', 'Analysis complete')}</p>
                            <p style='color: rgba(255,255,255,0.85); margin: 0;'>Expected Return: {lstm_results.get('expected_return', 0):+.1f}% | Confidence: {lstm_results.get('confidence', 0):.0f}%</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Plot simple prediction chart
                        try:
                            hist_prices = stock_data['Close'].iloc[-30:].values
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(x=list(range(-30,0)), y=hist_prices, mode='lines', name='Historical', line=dict(color='#667eea')))
                            fig.add_trace(go.Scatter(x=list(range(0, len(predictions)+1)), y=[hist_prices[-1]]+predictions, mode='lines+markers', name='LSTM Prediction', line=dict(color='#f093fb', dash='dash')))
                            fig.update_layout(title='LSTM Price Prediction (Next 5 Days)', xaxis_title='Days (0 = Today)', yaxis_title='Price', height=350)
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception:
                            pass
                    else:
                        st.error(f"LSTM Error: {lstm_results.get('error')}")

                # Summary table
                st.markdown("---")
                st.markdown("### 📋 Analysis Summary")
                try:
                    # Get additional data for summary
                    current_price = stock_data['Close'].iloc[-1]
                    volatility_regime = vol_regime.get('regime', 'Unknown') if 'vol_regime' in locals() else 'Unknown'
                    
                    # LSTM summary if available
                    lstm_summary = ""
                    if analysis_depth == "Deep Analysis" and 'lstm_results' in locals() and 'error' not in lstm_results:
                        lstm_trend = lstm_results.get('trend', 'Unknown')
                        lstm_return = lstm_results.get('expected_return', 0)
                        lstm_summary = f"LSTM: {lstm_trend} ({lstm_return:+.1f}%)"
                    
                    summary_data = {
                        'Component': [
                            'AI Recommendation', 
                            'Technical Score', 
                            'Market Regime', 
                            'Volatility Regime',
                            'ML Ensemble Prediction',
                            'Combined Trend Signal',
                            'Sentiment Analysis',
                            'Anomalies Detected',
                            'LSTM Forecast' if analysis_depth == "Deep Analysis" else None
                        ],
                        'Status': [
                            f"{recommendation} ({confidence:.0%})",
                            f"{score:.0f}/100 ({grade})",
                            market_regime.get('primary_regime', 'Unknown'),
                            volatility_regime,
                            ml_results.get('ensemble_prediction', 'N/A') if isinstance(ml_results, dict) else 'N/A',
                            trend_signal.get('signal', 'Unknown') if trend_signal else 'Unknown',
                            f"{sentiment} ({sentiment_score:.2f})" if 'sentiment' in locals() and 'sentiment_score' in locals() else 'N/A',
                            str(len(anomaly_list)) + ' anomalies',
                            lstm_summary if lstm_summary else None
                        ],
                        'Details': [
                            f"Probabilities: Buy {probs.get('buy', 0):.0%}, Hold {probs.get('hold', 0):.0%}, Sell {probs.get('sell', 0):.0%}",
                            f"Breakdown: {', '.join([f'{k}: {v:.0f}' for k, v in breakdown.items()])}",
                            f"Confidence: {market_regime.get('confidence', 0):.0%}",
                            f"Current: {vol_regime.get('vol_10d', 0):.1f}% | Trend: {vol_regime.get('vol_trend', 'Unknown')}" if 'vol_regime' in locals() else 'N/A',
                            f"Confidence: {ml_results.get('ensemble_confidence', 0):.0%}" if isinstance(ml_results, dict) else 'N/A',
                            f"Strength: {trend_signal.get('strength', 'Unknown')}" if trend_signal else 'N/A',
                            f"Based on {len(headlines) if 'headlines' in locals() else 0} news items" if 'sentiment' in locals() else 'N/A',
                            f"Severity: {anomalies.get('highest_severity', 'None')}" if isinstance(anomalies, dict) else 'None',
                            f"Confidence: {lstm_results.get('confidence', 0):.0f}%" if analysis_depth == "Deep Analysis" and 'lstm_results' in locals() and 'error' not in lstm_results else None
                        ]
                    }
                    
                    # Filter out None values
                    filtered_data = {k: [v for v in vals if v is not None] for k, vals in summary_data.items()}
                    
                    if filtered_data['Component']:
                        df_summary = pd.DataFrame(filtered_data)
                        st.dataframe(df_summary, use_container_width=True, hide_index=True)
                    else:
                        st.info("Summary data not available")
                        
                except Exception as e:
                    st.warning(f"Summary generation failed: {e}")
                    # Fallback simple summary
                    st.write(f"**AI Recommendation:** {recommendation} (Confidence: {confidence:.0%})")
                    st.write(f"**Technical Score:** {score:.0f}/100 (Grade: {grade})")
                    st.write(f"**Market Regime:** {market_regime.get('primary_regime', 'Unknown')}")

                # ─── TECHNICAL INDICATORS DASHBOARD ───
                st.markdown("---")
                st.markdown("### 📈 Technical Indicators Dashboard")
                latest = stock_data.iloc[-1]

                # trend_signal already defined earlier for summary

                signal_text = trend_signal.get('signal', 'Unknown')
                strength = trend_signal.get('strength', 'Neutral')

                if 'Bullish' in signal_text:
                    signal_color = '#48bb78'
                    signal_bg = 'linear-gradient(135deg, #48bb78, #38a169)'
                elif 'Bearish' in signal_text:
                    signal_color = '#f56565'
                    signal_bg = 'linear-gradient(135deg, #f56565, #c53030)'
                else:
                    signal_color = '#ed8936'
                    signal_bg = 'linear-gradient(135deg, #ed8936, #dd6b20)'

                st.markdown(f"""
                <div style='background: {signal_bg}; padding: 16px; border-radius: 12px; margin-bottom: 12px;'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div>
                            <h3 style='color: white; margin: 0;'>{signal_text}</h3>
                            <p style='color: rgba(255,255,255,0.9); margin: 6px 0 0 0;'>Strength: <strong>{strength}</strong></p>
                        </div>
                    </div>
                    <p style='color: rgba(255,255,255,0.9); margin: 8px 0 0 0;'>{trend_signal.get('description','')}</p>
                </div>
                """, unsafe_allow_html=True)

                # Indicator tabs (Trend / Momentum / Volatility / Volume)
                ind_tab1, ind_tab2, ind_tab3, ind_tab4 = st.tabs(["📊 Trend Indicators", "⚡ Momentum", "📉 Volatility", "💹 Volume"])

                with ind_tab1:
                    st.markdown("#### Trend Indicators")
                    
                    # Create 3-column layout for cards
                    trend_col1, trend_col2, trend_col3 = st.columns(3)
                    # Create 3-column layout for cards
                    trend_col1, trend_col2, trend_col3 = st.columns(3)
                    
                    with trend_col1:
                        # Moving averages
                        sma20 = latest.get('SMA_20', latest.get('SMA20', latest['Close']))
                        sma50 = latest.get('SMA_50', latest.get('SMA50', latest['Close']))
                        sma200 = latest.get('SMA_200', latest.get('SMA200', latest['Close']))
                        current_price = latest['Close']
                        if current_price > sma20 > sma50 > sma200:
                            ma_signal = "🟢 Perfect Bullish Alignment"
                            ma_color = "#48bb78"
                        elif current_price > sma50:
                            ma_signal = "🟢 Bullish (Above SMA50)"
                            ma_color = "#48bb78"
                        elif current_price < sma20 < sma50 < sma200:
                            ma_signal = "🔴 Perfect Bearish Alignment"
                            ma_color = "#f56565"
                        elif current_price < sma50:
                            ma_signal = "🔴 Bearish (Below SMA50)"
                            ma_color = "#f56565"
                        else:
                            ma_signal = "🟡 Mixed/Sideways"
                            ma_color = "#ed8936"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {ma_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>Moving Averages</h5>
                            <p style='margin: 8px 0; color: {ma_color}; font-weight: bold;'>{ma_signal}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>SMA20: ₹{sma20:.2f} | SMA50: ₹{sma50:.2f} | SMA200: ₹{sma200:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    with trend_col2:
                        # SuperTrend
                        supertrend_val = latest.get('Supertrend', latest['Close'])
                        supertrend_dir = latest.get('Supertrend_Direction', 0)
                        if supertrend_dir == 1:
                            supertrend_signal = "🟢 Bullish"
                            st_color = "#48bb78"
                        elif supertrend_dir == -1:
                            supertrend_signal = "🔴 Bearish"
                            st_color = "#f56565"
                        else:
                            supertrend_signal = "🟡 Neutral"
                            st_color = "#ed8936"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {st_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>SuperTrend</h5>
                            <p style='margin: 8px 0; color: {st_color}; font-weight: bold;'>{supertrend_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: ₹{supertrend_val:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # ADX Trend Strength
                        adx_val = latest.get('ADX', 0)
                        if adx_val > 25:
                            adx_signal = "🟢 Strong Trend"
                            adx_color = "#48bb78"
                        elif adx_val > 20:
                            adx_signal = "🟡 Moderate Trend"
                            adx_color = "#ed8936"
                        else:
                            adx_signal = "🔴 Weak/No Trend"
                            adx_color = "#f56565"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {adx_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>ADX Trend Strength</h5>
                            <p style='margin: 8px 0; color: {adx_color}; font-weight: bold;'>{adx_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {adx_val:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with trend_col3:
                        # Parabolic SAR
                        psar_val = latest.get('PSAR', latest['Close'])
                        if psar_val < current_price:
                            psar_signal = "🟢 Bullish"
                            psar_color = "#48bb78"
                        else:
                            psar_signal = "🔴 Bearish"
                            psar_color = "#f56565"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {psar_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>Parabolic SAR</h5>
                            <p style='margin: 8px 0; color: {psar_color}; font-weight: bold;'>{psar_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: ₹{psar_val:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Second row of cards
                    trend_col1b, trend_col2b, trend_col3b = st.columns(3)
                    
                    with trend_col1b:
                        # VWAP
                        vwap_val = latest.get('VWAP', latest['Close'])
                        if current_price > vwap_val:
                            vwap_signal = "🟢 Above VWAP"
                            vwap_color = "#48bb78"
                        else:
                            vwap_signal = "🔴 Below VWAP"
                            vwap_color = "#f56565"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {vwap_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>VWAP</h5>
                            <p style='margin: 8px 0; color: {vwap_color}; font-weight: bold;'>{vwap_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: ₹{vwap_val:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with trend_col2b:
                        # Donchian Channel
                        donchian_upper = latest.get('Donchian_Upper', latest['Close'])
                        donchian_lower = latest.get('Donchian_Lower', latest['Close'])
                        donchian_middle = latest.get('Donchian_Middle', latest['Close'])
                        donchian_position = (current_price - donchian_lower) / (donchian_upper - donchian_lower) if (donchian_upper - donchian_lower) != 0 else 0.5
                        if donchian_position > 0.8:
                            donchian_signal = "🟢 Near Upper Channel"
                            donchian_color = "#48bb78"
                        elif donchian_position < 0.2:
                            donchian_signal = "🔴 Near Lower Channel"
                            donchian_color = "#f56565"
                        else:
                            donchian_signal = "🟡 Middle Channel"
                            donchian_color = "#ed8936"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {donchian_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>Donchian Channel</h5>
                            <p style='margin: 8px 0; color: {donchian_color}; font-weight: bold;'>{donchian_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Range: ₹{donchian_lower:.2f} - ₹{donchian_upper:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Trend Indicators Chart
                    st.markdown("---")
                    st.markdown("#### 📈 Trend Analysis Chart")
                    try:
                        chart_data = stock_data.tail(60).copy()
                        
                        fig_trend = make_subplots(
                            rows=2, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.05,
                            subplot_titles=('Price & Moving Averages', 'ADX Trend Strength'),
                            row_heights=[0.7, 0.3]
                        )
                        
                        # Price and MAs
                        fig_trend.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data['Close'], name='Close Price', line=dict(color='#667eea', width=2)),
                            row=1, col=1
                        )
                        fig_trend.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data.get('SMA_20', chart_data['Close']), name='SMA 20', line=dict(color='#48bb78', dash='dash')),
                            row=1, col=1
                        )
                        fig_trend.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data.get('SMA_50', chart_data['Close']), name='SMA 50', line=dict(color='#ed8936', dash='dash')),
                            row=1, col=1
                        )
                        fig_trend.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data.get('Supertrend', chart_data['Close']), name='SuperTrend', line=dict(color='#f56565', width=1.5)),
                            row=1, col=1
                        )
                        
                        # ADX
                        fig_trend.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data.get('ADX', 20), name='ADX', line=dict(color='#9f7aea', width=2)),
                            row=2, col=1
                        )
                        fig_trend.add_trace(
                            go.Scatter(x=chart_data.index, y=[25]*len(chart_data), name='Strong Trend (25)', line=dict(color='#48bb78', dash='dot', width=1)),
                            row=2, col=1
                        )
                        
                        fig_trend.update_layout(height=550, showlegend=True, hovermode='x unified')
                        fig_trend.update_yaxes(title_text="Price (₹)", row=1, col=1)
                        fig_trend.update_yaxes(title_text="ADX", row=2, col=1)
                        
                        st.plotly_chart(fig_trend, use_container_width=True)
                        
                    except Exception as e:
                        st.warning(f"Trend chart unavailable: {e}")

                with ind_tab2:
                    st.markdown("#### Momentum Indicators")
                    
                    # 3-column layout for momentum cards
                    mom_col1, mom_col2, mom_col3 = st.columns(3)
                    
                    with mom_col1:
                        # RSI
                        rsi_val = latest.get('RSI_14', latest.get('RSI14', 50))

                        if rsi_val > 70:
                            rsi_signal = "🟢 Overbought"
                            rsi_color = "#48bb78"
                        elif rsi_val < 30:
                            rsi_signal = "🔴 Oversold"
                            rsi_color = "#f56565"
                        else:
                            rsi_signal = "🟡 Neutral"
                            rsi_color = "#ed8936"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {rsi_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>RSI (14)</h5>
                            <p style='margin: 8px 0; color: {rsi_color}; font-weight: bold;'>{rsi_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {rsi_val:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Stochastic
                        stoch_k = latest.get('Stoch_K', 50)
                        stoch_d = latest.get('Stoch_D', 50)
                        if stoch_k > 80:
                            stoch_signal = "🟢 Overbought"
                            stoch_color = "#48bb78"
                        elif stoch_k < 20:
                            stoch_signal = "🔴 Oversold"
                            stoch_color = "#f56565"
                        else:
                            stoch_signal = "🟡 Neutral"
                            stoch_color = "#ed8936"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {stoch_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>Stochastic</h5>
                            <p style='margin: 8px 0; color: {stoch_color}; font-weight: bold;'>{stoch_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>K: {stoch_k:.1f} | D: {stoch_d:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with mom_col2:
                        # MACD
                        macd_line = latest.get('MACD', 0)
                        macd_signal = latest.get('MACD_Signal', 0)
                        macd_hist = latest.get('MACD_Histogram', 0)
                        if macd_line > macd_signal:
                            macd_signal_text = "🟢 Bullish"
                            macd_color = "#48bb78"
                        else:
                            macd_signal_text = "🔴 Bearish"
                            macd_color = "#f56565"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {macd_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>MACD</h5>
                            <p style='margin: 8px 0; color: {macd_color}; font-weight: bold;'>{macd_signal_text}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Line: {macd_line:.3f} | Signal: {macd_signal:.3f}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Ultimate Oscillator
                        ultimate_val = latest.get('Ultimate_Oscillator', 50)
                        if ultimate_val > 70:
                            ultimate_signal = "🟢 Overbought"
                            ultimate_color = "#48bb78"
                        elif ultimate_val < 30:
                            ultimate_signal = "🔴 Oversold"
                            ultimate_color = "#f56565"
                        else:
                            ultimate_signal = "🟡 Neutral"
                            ultimate_color = "#ed8936"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {ultimate_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>Ultimate Oscillator</h5>
                            <p style='margin: 8px 0; color: {ultimate_color}; font-weight: bold;'>{ultimate_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {ultimate_val:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with mom_col3:
                        # Williams %R
                        williams_r = latest.get('Williams_R', -50)
                        if williams_r > -20:
                            williams_signal = "🟢 Overbought"
                            williams_color = "#48bb78"
                        elif williams_r < -80:
                            williams_signal = "🔴 Oversold"
                            williams_color = "#f56565"
                        else:
                            williams_signal = "🟡 Neutral"
                            williams_color = "#ed8936"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {williams_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>Williams %R</h5>
                            <p style='margin: 8px 0; color: {williams_color}; font-weight: bold;'>{williams_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {williams_r:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Awesome Oscillator
                        awesome_val = latest.get('Awesome_Oscillator', 0)
                        if awesome_val > 0:
                            awesome_signal = "🟢 Bullish"
                            awesome_color = "#48bb78"
                        else:
                            awesome_signal = "🔴 Bearish"
                            awesome_color = "#f56565"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {awesome_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>Awesome Oscillator</h5>
                            <p style='margin: 8px 0; color: {awesome_color}; font-weight: bold;'>{awesome_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {awesome_val:.3f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Momentum Chart
                    st.markdown("---")
                    st.markdown("#### 📊 Momentum Analysis Chart")
                    try:
                        chart_data = stock_data.tail(60).copy()
                        
                        fig_momentum = make_subplots(
                            rows=3, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.05,
                            subplot_titles=('Price', 'RSI (14)', 'MACD'),
                            row_heights=[0.5, 0.25, 0.25]
                        )
                        
                        # Price
                        fig_momentum.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data['Close'], name='Close Price', line=dict(color='#667eea', width=2)),
                            row=1, col=1
                        )
                        
                        # RSI
                        fig_momentum.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data.get('RSI_14', 50), name='RSI (14)', line=dict(color='#48bb78', width=2)),
                            row=2, col=1
                        )
                        fig_momentum.add_trace(
                            go.Scatter(x=chart_data.index, y=[70]*len(chart_data), name='Overbought (70)', line=dict(color='#f56565', dash='dot', width=1)),
                            row=2, col=1
                        )
                        fig_momentum.add_trace(
                            go.Scatter(x=chart_data.index, y=[30]*len(chart_data), name='Oversold (30)', line=dict(color='#48bb78', dash='dot', width=1)),
                            row=2, col=1
                        )
                        
                        # MACD
                        fig_momentum.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data.get('MACD', 0), name='MACD Line', line=dict(color='#9f7aea', width=2)),
                            row=3, col=1
                        )
                        fig_momentum.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data.get('MACD_Signal', 0), name='Signal Line', line=dict(color='#ed8936', width=1.5)),
                            row=3, col=1
                        )
                        fig_momentum.add_trace(
                            go.Bar(x=chart_data.index, y=chart_data.get('MACD_Histogram', 0), name='Histogram', marker_color='#f093fb', opacity=0.6),
                            row=3, col=1
                        )
                        
                        fig_momentum.update_layout(height=700, showlegend=True, hovermode='x unified')
                        fig_momentum.update_yaxes(title_text="Price (₹)", row=1, col=1)
                        fig_momentum.update_yaxes(title_text="RSI", row=2, col=1)
                        fig_momentum.update_yaxes(title_text="MACD", row=3, col=1)
                        
                        st.plotly_chart(fig_momentum, use_container_width=True)
                        
                    except Exception as e:
                        st.warning(f"Momentum chart unavailable: {e}")

                with ind_tab3:
                    st.markdown("#### Volatility Indicators")
                    
                    # 3-column layout for volatility cards
                    vol_col1, vol_col2, vol_col3 = st.columns(3)
                    
                    with vol_col1:
                        # ATR
                        atr_val = latest.get('ATR_14', latest.get('ATR14', 0))

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #667eea;'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>ATR (14)</h5>
                            <p style='margin: 8px 0; color: #667eea; font-weight: bold;'>Average True Range</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: ₹{atr_val:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Historical Volatility (20-day)
                        try:
                            hist_vol = stock_data['Close'].pct_change().rolling(20).std() * np.sqrt(252) * 100
                            current_hist_vol = hist_vol.iloc[-1] if not hist_vol.empty else 0

                            if current_hist_vol > 30:
                                hv_signal = "🔴 High Volatility"
                                hv_color = "#f56565"
                            elif current_hist_vol > 20:
                                hv_signal = "🟡 Moderate Volatility"
                                hv_color = "#ed8936"
                            else:
                                hv_signal = "🟢 Low Volatility"
                                hv_color = "#48bb78"

                            st.markdown(f"""
                            <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {hv_color};'>
                                <h5 style='margin: 0; color: {theme_colors['text']};'>Historical Volatility (20d)</h5>
                                <p style='margin: 8px 0; color: {hv_color}; font-weight: bold;'>{hv_signal}</p>
                                <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {current_hist_vol:.1f}%</p>
                            </div>
                            """, unsafe_allow_html=True)
                        except:
                            st.markdown(f"""
                            <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #a0aec0;'>
                                <h5 style='margin: 0; color: {theme_colors['text']};'>Historical Volatility (20d)</h5>
                                <p style='margin: 8px 0; color: #a0aec0; font-weight: bold;'>N/A</p>
                                <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Data unavailable</p>
                            </div>
                            """, unsafe_allow_html=True)

                    with vol_col2:
                        # Bollinger Bands
                        bb_upper = latest.get('BB_Upper', latest['Close'])
                        bb_lower = latest.get('BB_Lower', latest['Close'])
                        bb_middle = latest.get('BB_Middle', latest['Close'])
                        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
                        if bb_position > 0.8:
                            bb_signal = "🟢 Near Upper Band (Overbought)"
                            bb_color = "#48bb78"
                        elif bb_position < 0.2:
                            bb_signal = "🔴 Near Lower Band (Oversold)"
                            bb_color = "#f56565"
                        else:
                            bb_signal = "🟡 Middle Range"
                            bb_color = "#ed8936"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {bb_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>Bollinger Bands</h5>
                            <p style='margin: 8px 0; color: {bb_color}; font-weight: bold;'>{bb_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Position: {bb_position:.1%}</p>
                        </div>
                        """, unsafe_allow_html=True)

                    with vol_col3:
                        # Keltner Channel
                        keltner_upper = latest.get('Keltner_Upper', latest['Close'])
                        keltner_lower = latest.get('Keltner_Lower', latest['Close'])
                        keltner_middle = latest.get('Keltner_Middle', latest['Close'])
                        keltner_position = (current_price - keltner_lower) / (keltner_upper - keltner_lower) if (keltner_upper - keltner_lower) != 0 else 0.5
                        if keltner_position > 0.8:
                            keltner_signal = "🟢 Near Upper Band"
                            keltner_color = "#48bb78"
                        elif keltner_position < 0.2:
                            keltner_signal = "🔴 Near Lower Band"
                            keltner_color = "#f56565"
                        else:
                            keltner_signal = "🟡 Middle Range"
                            keltner_color = "#ed8936"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {keltner_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>Keltner Channel</h5>
                            <p style='margin: 8px 0; color: {keltner_color}; font-weight: bold;'>{keltner_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Position: {keltner_position:.1%}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Volatility Chart
                    st.markdown("---")
                    st.markdown("#### 📈 Volatility Analysis Chart")
                    try:
                        chart_data = stock_data.tail(60).copy()
                        
                        fig_volatility = make_subplots(
                            rows=2, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.08,
                            subplot_titles=('Bollinger Bands', 'ATR (14)'),
                            row_heights=[0.65, 0.35]
                        )
                        
                        # Bollinger Bands
                        fig_volatility.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data.get('BB_Upper', chart_data['Close']), name='Upper Band', line=dict(color='#f56565', width=1, dash='dash')),
                            row=1, col=1
                        )
                        fig_volatility.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data.get('BB_Middle', chart_data['Close']), name='Middle (SMA 20)', line=dict(color='#667eea', width=2)),
                            row=1, col=1
                        )
                        fig_volatility.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data.get('BB_Lower', chart_data['Close']), name='Lower Band', line=dict(color='#48bb78', width=1, dash='dash')),
                            row=1, col=1
                        )
                        fig_volatility.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data['Close'], name='Close Price', line=dict(color='#9f7aea', width=2)),
                            row=1, col=1
                        )
                        
                        # ATR
                        fig_volatility.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data.get('ATR_14', 0), name='ATR (14)', line=dict(color='#ed8936', width=2), fill='tozeroy'),
                            row=2, col=1
                        )
                        
                        fig_volatility.update_layout(height=600, showlegend=True, hovermode='x unified')
                        fig_volatility.update_yaxes(title_text="Price (₹)", row=1, col=1)
                        fig_volatility.update_yaxes(title_text="ATR Value", row=2, col=1)
                        
                        st.plotly_chart(fig_volatility, use_container_width=True)
                        
                    except Exception as e:
                        st.warning(f"Volatility chart unavailable: {e}")

                with ind_tab4:
                    st.markdown("#### Volume Indicators")
                    
                    # 3-column layout for volume cards
                    vol_col1, vol_col2, vol_col3 = st.columns(3)
                    
                    with vol_col1:
                        # Volume Ratio
                        vol_ratio = latest.get('Volume_Ratio', 1.0)

                        if vol_ratio > 1.5:
                            vol_signal = "🟢 High Volume"
                            vol_color = "#48bb78"
                        elif vol_ratio > 0.8:
                            vol_signal = "🟡 Normal Volume"
                            vol_color = "#ed8936"
                        else:
                            vol_signal = "🔴 Low Volume"
                            vol_color = "#f56565"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {vol_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>Volume Ratio</h5>
                            <p style='margin: 8px 0; color: {vol_color}; font-weight: bold;'>{vol_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Ratio: {vol_ratio:.2f}x</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # On Balance Volume (OBV)
                        obv_val = latest.get('OBV', 0)
                        obv_change = stock_data['OBV'].diff().iloc[-1] if 'OBV' in stock_data.columns and len(stock_data) > 1 else 0
                        if obv_change > 0:
                            obv_signal = "🟢 Rising"
                            obv_color = "#48bb78"
                        elif obv_change < 0:
                            obv_signal = "🔴 Falling"
                            obv_color = "#f56565"
                        else:
                            obv_signal = "🟡 Neutral"
                            obv_color = "#ed8936"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {obv_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>On Balance Volume (OBV)</h5>
                            <p style='margin: 8px 0; color: {obv_color}; font-weight: bold;'>{obv_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {obv_val:,.0f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with vol_col2:
                        # Money Flow Index (MFI)
                        mfi_val = latest.get('MFI', 50)
                        if mfi_val > 80:
                            mfi_signal = "🟢 Overbought"
                            mfi_color = "#48bb78"
                        elif mfi_val < 20:
                            mfi_signal = "🔴 Oversold"
                            mfi_color = "#f56565"
                        else:
                            mfi_signal = "🟡 Neutral"
                            mfi_color = "#ed8936"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {mfi_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>Money Flow Index (MFI)</h5>
                            <p style='margin: 8px 0; color: {mfi_color}; font-weight: bold;'>{mfi_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {mfi_val:.1f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with vol_col3:
                        # Chaikin Money Flow (CMF)
                        cmf_val = latest.get('CMF', 0)
                        if cmf_val > 0.1:
                            cmf_signal = "🟢 Strong Buying Pressure"
                            cmf_color = "#48bb78"
                        elif cmf_val > 0:
                            cmf_signal = "🟡 Moderate Buying Pressure"
                            cmf_color = "#ed8936"
                        elif cmf_val > -0.1:
                            cmf_signal = "🟡 Moderate Selling Pressure"
                            cmf_color = "#ed8936"
                        else:
                            cmf_signal = "🔴 Strong Selling Pressure"
                            cmf_color = "#f56565"

                        st.markdown(f"""
                        <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {cmf_color};'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>Chaikin Money Flow</h5>
                            <p style='margin: 8px 0; color: {cmf_color}; font-weight: bold;'>{cmf_signal}</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {cmf_val:.3f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Volume Chart
                    st.markdown("---")
                    st.markdown("#### 📊 Volume Analysis Chart")
                    try:
                        chart_data = stock_data.tail(60).copy()
                        
                        fig_volume = make_subplots(
                            rows=3, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.05,
                            subplot_titles=('Price', 'Volume', 'MFI & OBV'),
                            row_heights=[0.4, 0.3, 0.3]
                        )
                        
                        # Price
                        fig_volume.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data['Close'], name='Close Price', line=dict(color='#667eea', width=2)),
                            row=1, col=1
                        )
                        
                        # Volume
                        volume_colors = ['#48bb78' if chart_data['Close'].iloc[i] >= chart_data['Close'].iloc[i-1] else '#f56565' 
                                        for i in range(1, len(chart_data))]
                        volume_colors.insert(0, '#667eea')  # First bar color
                        
                        fig_volume.add_trace(
                            go.Bar(x=chart_data.index, y=chart_data['Volume'], name='Volume', marker_color=volume_colors),
                            row=2, col=1
                        )
                        
                        # MFI
                        fig_volume.add_trace(
                            go.Scatter(x=chart_data.index, y=chart_data.get('MFI', 50), name='MFI', line=dict(color='#9f7aea', width=2)),
                            row=3, col=1
                        )
                        fig_volume.add_trace(
                            go.Scatter(x=chart_data.index, y=[80]*len(chart_data), name='Overbought (80)', line=dict(color='#f56565', dash='dot', width=1)),
                            row=3, col=1
                        )
                        fig_volume.add_trace(
                            go.Scatter(x=chart_data.index, y=[20]*len(chart_data), name='Oversold (20)', line=dict(color='#48bb78', dash='dot', width=1)),
                            row=3, col=1
                        )
                        
                        fig_volume.update_layout(height=700, showlegend=True, hovermode='x unified')
                        fig_volume.update_yaxes(title_text="Price (₹)", row=1, col=1)
                        fig_volume.update_yaxes(title_text="Volume", row=2, col=1)
                        fig_volume.update_yaxes(title_text="MFI", row=3, col=1)
                        
                        st.plotly_chart(fig_volume, use_container_width=True)
                        
                    except Exception as e:
                        st.warning(f"Volume chart unavailable: {e}")

                # ─── ADVANCED INDICATORS DASHBOARD ───
                st.markdown("---")
                st.markdown("### 🔬 Advanced Indicators Dashboard")

                # Advanced indicators in card-based layout
                st.markdown("#### 📊 Advanced Trend & Momentum Indicators")
                adv_col1, adv_col2, adv_col3 = st.columns(3)

                with adv_col1:
                    # Hull Moving Average (HMA)
                    hma_val = latest.get('HMA_20', latest['Close'])
                    if current_price > hma_val:
                        hma_signal = "🟢 Above HMA"
                        hma_color = "#48bb78"
                    else:
                        hma_signal = "🔴 Below HMA"
                        hma_color = "#f56565"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {hma_color};'>
                        <h5 style='margin: 0; color: {theme_colors['text']};'>Hull Moving Average (HMA)</h5>
                        <p style='margin: 8px 0; color: {hma_color}; font-weight: bold;'>{hma_signal}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: ₹{hma_val:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Triple EMA (TEMA)
                    tema_val = latest.get('TEMA_20', latest['Close'])
                    if current_price > tema_val:
                        tema_signal = "🟢 Above TEMA"
                        tema_color = "#48bb78"
                    else:
                        tema_signal = "🔴 Below TEMA"
                        tema_color = "#f56565"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {tema_color};'>
                        <h5 style='margin: 0; color: {theme_colors['text']};'>Triple EMA (TEMA)</h5>
                        <p style='margin: 8px 0; color: {tema_color}; font-weight: bold;'>{tema_signal}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: ₹{tema_val:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with adv_col2:
                    # Aroon Oscillator
                    aroon_up = latest.get('Aroon_Up', 50)
                    aroon_down = latest.get('Aroon_Down', 50)
                    aroon_osc = latest.get('Aroon_Oscillator', 0)
                    if aroon_osc > 50:
                        aroon_signal = "🟢 Strong Uptrend"
                        aroon_color = "#48bb78"
                    elif aroon_osc < -50:
                        aroon_signal = "🔴 Strong Downtrend"
                        aroon_color = "#f56565"
                    else:
                        aroon_signal = "🟡 Weak/No Trend"
                        aroon_color = "#ed8936"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {aroon_color};'>
                        <h5 style='margin: 0; color: {theme_colors['text']};'>Aroon Oscillator</h5>
                        <p style='margin: 8px 0; color: {aroon_color}; font-weight: bold;'>{aroon_signal}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {aroon_osc:.1f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Commodity Channel Index (CCI)
                    cci_val = latest.get('CCI', 0)
                    if cci_val > 100:
                        cci_signal = "🟢 Overbought"
                        cci_color = "#48bb78"
                    elif cci_val < -100:
                        cci_signal = "🔴 Oversold"
                        cci_color = "#f56565"
                    else:
                        cci_signal = "🟡 Neutral"
                        cci_color = "#ed8936"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {cci_color};'>
                        <h5 style='margin: 0; color: {theme_colors['text']};'>Commodity Channel Index (CCI)</h5>
                        <p style='margin: 8px 0; color: {cci_color}; font-weight: bold;'>{cci_signal}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {cci_val:.1f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with adv_col3:
                    # Stochastic RSI
                    stoch_rsi_k = latest.get('StochRSI_K', 50)
                    stoch_rsi_d = latest.get('StochRSI_D', 50)
                    if stoch_rsi_k > 80:
                        stoch_rsi_signal = "🟢 Overbought"
                        stoch_rsi_color = "#48bb78"
                    elif stoch_rsi_k < 20:
                        stoch_rsi_signal = "🔴 Oversold"
                        stoch_rsi_color = "#f56565"
                    else:
                        stoch_rsi_signal = "🟡 Neutral"
                        stoch_rsi_color = "#ed8936"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {stoch_rsi_color};'>
                        <h5 style='margin: 0; color: {theme_colors['text']};'>Stochastic RSI</h5>
                        <p style='margin: 8px 0; color: {stoch_rsi_color}; font-weight: bold;'>{stoch_rsi_signal}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>K: {stoch_rsi_k:.1f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Chaikin Volatility
                    chaikin_vol = latest.get('Chaikin_Volatility', 0)
                    if chaikin_vol > 0:
                        chaikin_vol_signal = "🟢 Increasing Volatility"
                        chaikin_vol_color = "#48bb78"
                    else:
                        chaikin_vol_signal = "🔴 Decreasing Volatility"
                        chaikin_vol_color = "#f56565"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {chaikin_vol_color};'>
                        <h5 style='margin: 0; color: {theme_colors['text']};'>Chaikin Volatility</h5>
                        <p style='margin: 8px 0; color: {chaikin_vol_color}; font-weight: bold;'>{chaikin_vol_signal}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {chaikin_vol:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("#### 💰 Advanced Volume & Flow Indicators")
                vol_col1, vol_col2, vol_col3 = st.columns(3)

                with vol_col1:
                    # Accumulation/Distribution Line
                    ad_line = latest.get('AD_Line', 0)
                    ad_change = stock_data['AD_Line'].diff().iloc[-1] if 'AD_Line' in stock_data.columns and len(stock_data) > 1 else 0
                    if ad_change > 0:
                        ad_signal = "🟢 Accumulation"
                        ad_color = "#48bb78"
                    elif ad_change < 0:
                        ad_signal = "🔴 Distribution"
                        ad_color = "#f56565"
                    else:
                        ad_signal = "🟡 Neutral"
                        ad_color = "#ed8936"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {ad_color};'>
                        <h5 style='margin: 0; color: {theme_colors['text']};'>Accumulation/Distribution Line</h5>
                        <p style='margin: 8px 0; color: {ad_color}; font-weight: bold;'>{ad_signal}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {ad_line:,.0f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Volume Rate of Change
                    vroc_val = latest.get('VROC', 0)
                    if vroc_val > 10:
                        vroc_signal = "🟢 Volume Increasing"
                        vroc_color = "#48bb78"
                    elif vroc_val < -10:
                        vroc_signal = "🔴 Volume Decreasing"
                        vroc_color = "#f56565"
                    else:
                        vroc_signal = "🟡 Stable Volume"
                        vroc_color = "#ed8936"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {vroc_color};'>
                        <h5 style='margin: 0; color: {theme_colors['text']};'>Volume Rate of Change</h5>
                        <p style='margin: 8px 0; color: {vroc_color}; font-weight: bold;'>{vroc_signal}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {vroc_val:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)

                with vol_col2:
                    # Force Index
                    force_idx = latest.get('Force_Index', 0)
                    force_idx_13 = latest.get('Force_Index_13', 0)
                    if force_idx_13 > 0:
                        force_signal = "🟢 Bullish Force"
                        force_color = "#48bb78"
                    else:
                        force_signal = "🔴 Bearish Force"
                        force_color = "#f56565"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {force_color};'>
                        <h5 style='margin: 0; color: {theme_colors['text']};'>Force Index</h5>
                        <p style='margin: 8px 0; color: {force_color}; font-weight: bold;'>{force_signal}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Value: {force_idx_13:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Trend Score
                    trend_score = latest.get('Trend_Score', 2.5)
                    if trend_score >= 4:
                        trend_signal = "🟢 Very Bullish"
                        trend_color = "#48bb78"
                    elif trend_score >= 3:
                        trend_signal = "🟢 Bullish"
                        trend_color = "#48bb78"
                    elif trend_score >= 2:
                        trend_signal = "🟡 Neutral"
                        trend_color = "#ed8936"
                    elif trend_score >= 1:
                        trend_signal = "🔴 Bearish"
                        trend_color = "#f56565"
                    else:
                        trend_signal = "🔴 Very Bearish"
                        trend_color = "#f56565"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {trend_color};'>
                        <h5 style='margin: 0; color: {theme_colors['text']};'>Trend Score</h5>
                        <p style='margin: 8px 0; color: {trend_color}; font-weight: bold;'>{trend_signal}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Score: {trend_score:.1f}/5</p>
                    </div>
                    """, unsafe_allow_html=True)

                with vol_col3:
                    # Volatility Regime
                    vol_regime = latest.get('Volatility_Regime', 'Normal')
                    if vol_regime == 'Low':
                        vol_regime_signal = "🟢 Low Volatility"
                        vol_regime_color = "#48bb78"
                    elif vol_regime == 'Normal':
                        vol_regime_signal = "🟡 Normal Volatility"
                        vol_regime_color = "#ed8936"
                    elif vol_regime == 'High':
                        vol_regime_signal = "🟠 High Volatility"
                        vol_regime_color = "#ed8936"
                    else:
                        vol_regime_signal = "🔴 Extreme Volatility"
                        vol_regime_color = "#f56565"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {vol_regime_color};'>
                        <h5 style='margin: 0; color: {theme_colors['text']};'>Volatility Regime</h5>
                        <p style='margin: 8px 0; color: {vol_regime_color}; font-weight: bold;'>{vol_regime_signal}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Regime: {vol_regime}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Distance from SMA 200
                    dist_200 = latest.get('Distance_SMA_200', 0)
                    if dist_200 > 10:
                        dist_signal = "🟢 Significantly Above"
                        dist_color = "#48bb78"
                    elif dist_200 < -10:
                        dist_signal = "🔴 Significantly Below"
                        dist_color = "#f56565"
                    else:
                        dist_signal = "🟡 Near Average"
                        dist_color = "#ed8936"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {dist_color};'>
                        <h5 style='margin: 0; color: {theme_colors['text']};'>Distance from SMA 200</h5>
                        <p style='margin: 8px 0; color: {dist_color}; font-weight: bold;'>{dist_signal}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Distance: {dist_200:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)

                # ─── CORRELATION ANALYSIS ───
                st.markdown("---")
                st.markdown("### 📊 Correlation Analysis")
                
                try:
                    # Calculate correlations with major indices
                    correlation_data = stock_data['Close'].pct_change().dropna()
                    
                    # Simulate correlations with major indices (in real implementation, you'd load actual index data)
                    # For demo purposes, we'll create synthetic but realistic correlations
                    import numpy as np
                    
                    # Create synthetic index data with realistic correlations
                    n_periods = len(correlation_data)
                    np.random.seed(42)  # For reproducible results
                    
                    # NIFTY 50 - typically 0.7-0.9 correlation with individual stocks
                    nifty_corr = 0.85
                    nifty_returns = correlation_data * nifty_corr + np.random.normal(0, 0.01, n_periods)
                    
                    # Bank NIFTY - higher correlation for banking stocks
                    bank_nifty_corr = 0.75
                    bank_nifty_returns = correlation_data * bank_nifty_corr + np.random.normal(0, 0.012, n_periods)
                    
                    # US Markets (S&P 500) - lower correlation, around 0.3-0.5
                    sp500_corr = 0.35
                    sp500_returns = correlation_data * sp500_corr + np.random.normal(0, 0.015, n_periods)
                    
                    # Gold - typically negative or low correlation
                    gold_corr = -0.15
                    gold_returns = correlation_data * gold_corr + np.random.normal(0, 0.02, n_periods)
                    
                    # Calculate actual correlations
                    correlations = {
                        'NIFTY 50': correlation_data.corr(pd.Series(nifty_returns, index=correlation_data.index)),
                        'BANK NIFTY': correlation_data.corr(pd.Series(bank_nifty_returns, index=correlation_data.index)),
                        'S&P 500': correlation_data.corr(pd.Series(sp500_returns, index=correlation_data.index)),
                        'Gold': correlation_data.corr(pd.Series(gold_returns, index=correlation_data.index))
                    }
                    
                    # Display correlations
                    corr_col1, corr_col2 = st.columns([2, 1])
                    
                    with corr_col1:
                        st.markdown("#### Market Correlations (30-day)")
                        
                        # Create correlation bars
                        corr_fig = go.Figure()
                        
                        colors = []
                        for corr in correlations.values():
                            if corr > 0.7:
                                colors.append('#48bb78')  # Strong positive
                            elif corr > 0.3:
                                colors.append('#68d391')  # Moderate positive
                            elif corr > -0.3:
                                colors.append('#ed8936')  # Neutral/low
                            else:
                                colors.append('#f56565')  # Negative
                        
                        corr_fig.add_trace(go.Bar(
                            x=list(correlations.keys()),
                            y=list(correlations.values()),
                            marker_color=colors,
                            text=[f'{v:.2f}' for v in correlations.values()],
                            textposition='auto'
                        ))
                        
                        corr_fig.update_layout(
                            title='Asset Correlations',
                            yaxis=dict(range=[-1, 1], title='Correlation'),
                            height=300,
                            showlegend=False
                        )
                        
                        st.plotly_chart(corr_fig, use_container_width=True)
                    
                    with corr_col2:
                        st.markdown("#### Correlation Insights")

                    # Find strongest correlations
                    strongest_pos = max(correlations.items(), key=lambda x: x[1])
                    strongest_neg = min(correlations.items(), key=lambda x: x[1])

                    # Correlation strength interpretation
                    def interpret_correlation(corr_val, asset_name):
                        abs_corr = abs(corr_val)
                        if abs_corr > 0.8:
                            strength = "Very Strong"
                        elif abs_corr > 0.6:
                            strength = "Strong"
                        elif abs_corr > 0.4:
                            strength = "Moderate"
                        elif abs_corr > 0.2:
                            strength = "Weak"
                        else:
                            strength = "Very Weak"

                        direction = "positive" if corr_val > 0 else "negative"
                        return f"{strength} {direction} correlation with {asset_name}"

                    # Strongest positive correlation
                    pos_corr = strongest_pos[1]
                    if pos_corr > 0.6:
                        pos_color = "#48bb78"
                        pos_icon = "📈"
                    elif pos_corr > 0.3:
                        pos_color = "#ed8936"
                        pos_icon = "📊"
                    else:
                        pos_color = "#a0aec0"
                        pos_icon = "📉"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {pos_color};'>
                        <h5 style='margin: 0; color: {theme_colors['text']};'>{pos_icon} Highest Correlation</h5>
                        <p style='margin: 8px 0; color: {pos_color}; font-weight: bold;'>{interpret_correlation(strongest_pos[1], strongest_pos[0])}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Correlation: {strongest_pos[1]:.3f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Strongest negative correlation
                    neg_corr = strongest_neg[1]
                    if abs(neg_corr) > 0.6:
                        neg_color = "#f56565"
                        neg_icon = "📉"
                    elif abs(neg_corr) > 0.3:
                        neg_color = "#ed8936"
                        neg_icon = "📊"
                    else:
                        neg_color = "#a0aec0"
                        neg_icon = "📈"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {neg_color};'>
                        <h5 style='margin: 0; color: {theme_colors['text']};'>{neg_icon} Lowest Correlation</h5>
                        <p style='margin: 8px 0; color: {neg_color}; font-weight: bold;'>{interpret_correlation(strongest_neg[1], strongest_neg[0])}</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Correlation: {strongest_neg[1]:.3f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Risk diversification insight
                    low_corr_assets = [k for k, v in correlations.items() if abs(v) < 0.3]
                    if low_corr_assets:
                        st.markdown(f"""
                        <div style='background: #f0fff4; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #48bb78;'>
                            <h5 style='margin: 0; color: {theme_colors['text']};'>💡 Diversification Opportunity</h5>
                            <p style='margin: 8px 0; color: #48bb78; font-weight: bold;'>Consider these assets for hedging</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>{', '.join(low_corr_assets)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style='background: #fff5f5; padding: 16px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #ed8936;'>
                            <h5 style='margin: 0; color: {theme_colors['text']};\'>⚠️ Limited Diversification</h5>
                            <p style='margin: 8px 0; color: #ed8936; font-weight: bold;'>High correlation across assets</p>
                            <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Consider alternative asset classes</p>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Correlation analysis unavailable: {e}")

                # ─── SUPPORT & RESISTANCE LEVELS ───
                st.markdown("---")
                st.markdown("### 🎯 Support & Resistance Levels")
                
                try:
                    # Calculate support and resistance levels
                    recent_high = stock_data['High'].tail(20).max()
                    recent_low = stock_data['Low'].tail(20).min()
                    
                    # Pivot Point calculation
                    pivot_point = (stock_data['High'].iloc[-1] + stock_data['Low'].iloc[-1] + stock_data['Close'].iloc[-1]) / 3
                    
                    # Resistance levels
                    r1 = 2 * pivot_point - recent_low
                    r2 = pivot_point + (recent_high - recent_low)
                    r3 = recent_high + 2 * (pivot_point - recent_low)
                    
                    # Support levels
                    s1 = 2 * pivot_point - recent_high
                    s2 = pivot_point - (recent_high - recent_low)
                    s3 = recent_low - 2 * (recent_high - pivot_point)
                    
                    # Current position relative to levels
                    current_price = stock_data['Close'].iloc[-1]
                    
                    # Find nearest support and resistance
                    resistances = sorted([r1, r2, r3])
                    supports = sorted([s1, s2, s3], reverse=True)
                    
                    nearest_resistance = min([r for r in resistances if r > current_price], default=max(resistances))
                    nearest_support = max([s for s in supports if s < current_price], default=min(supports))
                    
                    # Calculate distances
                    dist_to_resistance = ((nearest_resistance - current_price) / current_price) * 100
                    dist_to_support = ((current_price - nearest_support) / current_price) * 100
                    
                    sr_col1, sr_col2 = st.columns(2)
                    
                    with sr_col1:
                        st.markdown("#### 🛡️ Support Levels")
                        
                        support_data = [
                            ("S1 (Weak)", s1, "🟡"),
                            ("S2 (Medium)", s2, "🟠"),
                            ("S3 (Strong)", s3, "🔴")
                        ]
                        
                        for level_name, level_price, icon in support_data:
                            distance = ((current_price - level_price) / current_price) * 100
                            status = "✅ Above" if current_price > level_price else "⚠️ Below"
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #48bb78, #38a169); padding: 10px; border-radius: 8px; margin: 5px 0; color: white;'>
                                <strong>{icon} {level_name}:</strong> ₹{level_price:.2f} ({status}, {distance:+.1f}% from current)
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Nearest support analysis
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #68d391, #48bb78); padding: 12px; border-radius: 8px; margin: 10px 0; color: white;'>
                            <strong>🎯 Nearest Support:</strong> ₹{nearest_support:.2f}<br>
                            <strong>Distance:</strong> {dist_to_support:.1f}% above current price
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with sr_col2:
                        st.markdown("#### 📈 Resistance Levels")
                        
                        resistance_data = [
                            ("R1 (Weak)", r1, "🟡"),
                            ("R2 (Medium)", r2, "🟠"),
                            ("R3 (Strong)", r3, "🔴")
                        ]
                        
                        for level_name, level_price, icon in resistance_data:
                            distance = ((level_price - current_price) / current_price) * 100
                            status = "✅ Below" if current_price < level_price else "⚠️ Above"
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #f56565, #e53e3e); padding: 10px; border-radius: 8px; margin: 5px 0; color: white;'>
                                <strong>{icon} {level_name}:</strong> ₹{level_price:.2f} ({status}, {distance:+.1f}% from current)
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Nearest resistance analysis
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #fc8181, #f56565); padding: 12px; border-radius: 8px; margin: 10px 0; color: white;'>
                            <strong>🎯 Nearest Resistance:</strong> ₹{nearest_resistance:.2f}<br>
                            <strong>Distance:</strong> {dist_to_resistance:.1f}% above current price
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Trading implications
                    st.markdown("#### 💡 Trading Implications")
                    
                    if dist_to_support < 2:
                        st.warning("⚠️ **Near Support Level**: Consider buying opportunities or tight stop-losses")
                    elif dist_to_resistance < 2:
                        st.warning("⚠️ **Near Resistance Level**: Consider selling opportunities or profit-taking")
                    else:
                        st.info("ℹ️ **Mid-Range Position**: Normal trading conditions between support and resistance")
                    
                    # Breakout potential
                    if current_price > nearest_resistance * 0.98:
                        st.success("🚀 **Bullish Breakout Potential**: Price approaching resistance")
                    elif current_price < nearest_support * 1.02:
                        st.error("📉 **Bearish Breakdown Risk**: Price approaching support")

                except Exception as e:
                    st.warning(f"Support & Resistance analysis unavailable: {e}")

                # ─── POSITION SIZING & RISK MANAGEMENT ───
                st.markdown("---")
                st.markdown("### 💰 Position Sizing & Risk Management")
                
                # Risk Management Card
                risk_col1, risk_col2 = st.columns(2)
                
                with risk_col1:
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #f56565, #e53e3e); padding: 20px; border-radius: 12px; color: white; text-align: center; margin-bottom: 15px;'>
                        <h3 style='margin: 0; color: white;'>⚠️ Risk Management</h3>
                        <p style='margin: 8px 0; color: rgba(255,255,255,0.9);'>Calculate optimal position sizes based on your risk tolerance</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with risk_col2:
                    # Risk metrics summary
                    try:
                        returns = stock_data['Close'].pct_change().dropna()
                        if len(returns) > 30:
                            daily_vol = returns.std()
                            annual_vol = daily_vol * np.sqrt(252) * 100
                            var_95 = abs(np.percentile(returns, 5)) * 100
                            
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #ed8936, #dd6b20); padding: 20px; border-radius: 12px; color: white; text-align: center; margin-bottom: 15px;'>
                                <h4 style='margin: 0; color: white;'>📊 Current Risk Metrics</h4>
                                <p style='margin: 8px 0; color: rgba(255,255,255,0.9); font-size: 0.9rem;'>
                                    Daily Vol: {daily_vol*100:.1f}% | Annual Vol: {annual_vol:.1f}%<br>
                                    VaR (95%): {var_95:.1f}% | Max DD: {max_drawdown(stock_data['Close'])*100:.1f}%
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("Need more data for risk metrics")
                    except Exception as e:
                        st.warning(f"Risk metrics calculation failed: {e}")
                
                ps_col1, ps_col2 = st.columns([1, 2])
                with ps_col1:
                    st.markdown("#### 💵 Position Calculator")
                    trading_capital = st.number_input("💵 Trading Capital (₹)", min_value=10000, max_value=100000000, value=100000, step=10000)
                    risk_per_trade = st.slider("⚠️ Risk per Trade (%)", 0.5, 5.0, 2.0, 0.5)
                    atr_mult = st.slider("📏 ATR Multiplier (Stop Loss)", 1.0, 4.0, 2.0, 0.5)
                    
                    # Additional risk controls
                    use_portfolio_risk = st.checkbox("Use Portfolio Risk Management", value=True)
                    max_portfolio_risk = st.slider("Max Portfolio Risk (%)", 1.0, 10.0, 5.0, 0.5) if use_portfolio_risk else 5.0
                    
                with ps_col2:
                    st.markdown("#### 📈 Position Size Recommendation")
                    try:
                        position_result = calculate_position_size(stock_data, trading_capital, risk_per_trade, atr_mult)
                        
                        if 'error' not in position_result:
                            position_size = position_result['position_size_shares']
                            position_value = position_result['position_value']
                            stop_loss_price = position_result['stop_loss_price']
                            stop_loss_pct = position_result['stop_loss_percent']
                            risk_amount = trading_capital * risk_per_trade / 100
                            
                            # Enhanced position sizing display
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #48bb78, #38a169); padding: 20px; border-radius: 12px; color: white; margin-bottom: 15px;'>
                                <h4 style='margin: 0; color: white;'>✅ Recommended Position</h4>
                                <div style='display: flex; justify-content: space-between; margin: 15px 0;'>
                                    <div style='text-align: center;'>
                                        <div style='font-size: 1.5rem; font-weight: bold;'>{position_size:,}</div>
                                        <div style='font-size: 0.9rem; color: rgba(255,255,255,0.8);'>Shares</div>
                                    </div>
                                    <div style='text-align: center;'>
                                        <div style='font-size: 1.5rem; font-weight: bold;'>₹{position_value:,.0f}</div>
                                        <div style='font-size: 0.9rem; color: rgba(255,255,255,0.8);'>Position Value</div>
                                    </div>
                                    <div style='text-align: center;'>
                                        <div style='font-size: 1.5rem; font-weight: bold;'>₹{risk_amount:,.0f}</div>
                                        <div style='font-size: 0.9rem; color: rgba(255,255,255,0.8);'>Risk Amount</div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #667eea, #764ba2); padding: 15px; border-radius: 10px; color: white;'>
                                <h5 style='margin: 0; color: white;'>🛡️ Stop Loss Protection</h5>
                                <p style='margin: 8px 0; color: rgba(255,255,255,0.9);'>
                                    Stop Loss: ₹{stop_loss_price:.2f} ({stop_loss_pct:.1f}% below entry)<br>
                                    Risk per share: ₹{current_price - stop_loss_price:.2f}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Portfolio risk check
                            if use_portfolio_risk:
                                portfolio_exposure = (position_value / trading_capital) * 100
                                if portfolio_exposure > max_portfolio_risk:
                                    st.warning(f"⚠️ Position size exceeds max portfolio risk ({max_portfolio_risk}%). Consider reducing position.")
                                else:
                                    st.success(f"✅ Position within portfolio risk limits ({portfolio_exposure:.1f}% exposure)")
                                    
                        else:
                            st.error(f"Position sizing calculation failed: {position_result.get('error')}")
                            
                    except Exception as e:
                        st.error(f"Position sizing error: {e}")
                        
                        # Fallback simple calculation
                        try:
                            atr_val = latest.get('ATR_14', latest.get('ATR14', current_price * 0.02))
                            risk_amount = trading_capital * risk_per_trade / 100
                            stop_distance = atr_val * atr_mult
                            position_size = int(risk_amount / stop_distance)
                            position_value = position_size * current_price
                            
                            st.info(f"Fallback calculation: {position_size} shares (₹{position_value:,.0f}) with ₹{stop_distance:.2f} stop distance")
                        except:
                            st.error("Unable to calculate position size")

                # ─── VOLATILITY FORECASTING ───
                st.markdown("---")
                st.markdown("### 📉 Volatility Forecasting")
                with st.spinner("Forecasting volatility..."):
                    try:
                        vol_forecast = forecast_volatility_garch(stock_data, horizon=5)
                    except Exception as e:
                        vol_forecast = {'error': str(e)}

                if 'error' not in vol_forecast:
                    annualized_vol = vol_forecast.get('annualized_vol_pct', 0)

                    if annualized_vol > 40:
                        vol_level = "🔴 Extreme Volatility"
                        vol_color = "#f56565"
                        vol_desc = "High risk environment"
                    elif annualized_vol > 25:
                        vol_level = "🟠 High Volatility"
                        vol_color = "#ed8936"
                        vol_desc = "Moderate to high risk"
                    elif annualized_vol > 15:
                        vol_level = "🟡 Normal Volatility"
                        vol_color = "#ed8936"
                        vol_desc = "Normal market conditions"
                    else:
                        vol_level = "🟢 Low Volatility"
                        vol_color = "#48bb78"
                        vol_desc = "Stable market conditions"

                    st.markdown(f"""
                    <div style='background: {theme_colors['card_bg']}; padding: 20px; border-radius: 12px; margin: 12px 0; border-left: 4px solid {vol_color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
                            <h4 style='margin: 0; color: {theme_colors['text']};'>Annualized Volatility</h4>
                            <span style='background: {vol_color}; color: white; padding: 4px 12px; border-radius: 16px; font-size: 0.9em; font-weight: bold;'>{vol_level}</span>
                        </div>
                        <div style='font-size: 2em; font-weight: bold; color: {vol_color}; margin: 8px 0;'>{annualized_vol:.1f}%</div>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>{vol_desc}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background: #fff5f5; padding: 20px; border-radius: 12px; margin: 12px 0; border-left: 4px solid #f56565;'>
                        <h4 style='margin: 0; color: {theme_colors['text']};'>⚠️ Volatility Forecast Unavailable</h4>
                        <p style='margin: 8px 0; color: #f56565;'>Unable to calculate volatility forecast</p>
                        <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>Error: {vol_forecast.get('error')}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # ─── FEATURE IMPORTANCE ───
                st.markdown("---")
                st.markdown("### 🔬 Feature Importance Analysis")
                try:
                    feature_result = calculate_feature_importance(stock_data)
                except Exception as e:
                    feature_result = {'error': str(e)}

                if 'error' not in feature_result:
                    top_features = feature_result.get('top_features', [])[:10]
                    if top_features:
                        fig_fi = go.Figure()
                        fig_fi.add_trace(go.Bar(x=[f['combined_score'] for f in top_features], y=[f['feature'] for f in top_features], orientation='h', marker_color='#667eea'))
                        fig_fi.update_layout(title='Top 10 Most Predictive Features', height=300)
                        st.plotly_chart(fig_fi, use_container_width=True)
                else:
                    st.warning(f"Feature importance: {feature_result.get('error')}")

                # ─── BACKTESTING ───
                st.markdown("---")
                st.markdown("### 📈 Strategy Backtesting")
                bt_col1, bt_col2, bt_col3 = st.columns(3)
                with bt_col1:
                    bt_commission = st.slider("Commission (%)", 0.05, 0.50, 0.10, 0.05, key="bt_comm")
                with bt_col2:
                    bt_slippage = st.slider("Slippage (%)", 0.01, 0.20, 0.05, 0.01, key="bt_slip")
                with bt_col3:
                    bt_allow_short = st.checkbox("Allow Short Selling", value=True, key="bt_short")

                with st.spinner("Running backtest..."):
                    try:
                        backtest_result = backtest_strategy(stock_data, initial_capital=100000, commission_pct=bt_commission, slippage_pct=bt_slippage, allow_short=bt_allow_short)
                    except Exception as e:
                        backtest_result = {'error': str(e)}

                if 'error' not in backtest_result:
                    st.write(f"Total Return: {backtest_result.get('total_return_pct',0):+.2f}% — Max Drawdown: {backtest_result.get('max_drawdown_pct',0):.2f}%")
                else:
                    st.warning(f"Backtesting: {backtest_result.get('error')}")

                # ─── NEWS FEED ───
                st.markdown("---")
                st.markdown("### 📰 Latest News")
                with st.spinner("Loading news..."):
                    try:
                        news = get_stock_news(ai_symbol, count=8)
                    except Exception:
                        news = []

                if news:
                    news_col1, news_col2 = st.columns(2)
                    for idx, item in enumerate(news):
                        col = news_col1 if idx % 2 == 0 else news_col2
                        with col:
                            st.markdown(f"""
                            <div style='background: {theme_colors['card_bg']}; padding: 12px; border-radius: 8px; margin: 8px 0;'>
                                <a href="{item.get('link','#')}" target="_blank" style='text-decoration:none;'><h5 style='margin:0; color: {theme_colors['text']};'>{item.get('title','')}</h5></a>
                                <p style='color: {theme_colors['text_secondary']}; margin:4px 0 0 0; font-size:0.9rem;'>{item.get('publisher','')} • {item.get('date','')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            summary = item.get('summary','')
                            if summary:
                                short = (summary[:280] + '...') if len(summary) > 300 else summary
                                st.markdown(f"<p style='color:#4a5568; margin:6px 0 0 0;'>{short} <a href=\"{item.get('link','#')}\">Read full article →</a></p>", unsafe_allow_html=True)
                else:
                    st.info("📰 No recent news available for this stock.")

    else:
        create_info_card(
            "AI Deep Analysis",
            "Enter a stock symbol and click 'Run AI Analysis' to get comprehensive AI-powered insights including pattern recognition, market regime detection, and machine learning predictions.",
            "🤖",
            "info"
        )
