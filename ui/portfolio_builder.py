"""
Interactive Portfolio Builder Component
Provides drag-drop-like functionality and visual portfolio allocation
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def create_portfolio_builder():
    """
    Interactive portfolio builder with allocation widgets
    Returns: dict with portfolio configuration
    """
    st.markdown("### 🏗️ Interactive Portfolio Builder")
    
    # Initialize session state for portfolio
    if 'portfolio_items' not in st.session_state:
        st.session_state.portfolio_items = {}
    
    # Step 1: Add stocks to portfolio
    st.markdown("#### Step 1: Add Stocks to Your Portfolio")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_symbol = st.text_input(
            "Add stock symbol",
            placeholder="e.g., INFY.NS or NSE:INFY",
            key="portfolio_symbol_input"
        )
    
    with col2:
        if st.button("➕ Add", use_container_width=True):
                from src.symbol_utils import normalize_symbol
                normalized = normalize_symbol(new_symbol)
                if normalized and normalized not in st.session_state.portfolio_items:
                    st.session_state.portfolio_items[normalized] = {
                        'allocation': 0,
                        'quantity': 0,
                        'price': 0
                    }
                st.success(f"✅ Added {new_symbol.upper()}")
                st.rerun()
    
    # Step 2: Allocate percentages (auto-scale for 100%)
    if st.session_state.portfolio_items:
        st.markdown("#### Step 2: Allocate Portfolio Percentages")
        st.info(f"📊 Portfolio Allocation (Must sum to 100%)")
        
        portfolio_col, allocation_col = st.columns([1, 2])
        
        with portfolio_col:
            symbols = list(st.session_state.portfolio_items.keys())
            st.markdown("**Stock**")
            for symbol in symbols:
                st.markdown(f"**{symbol}**")
        
        with allocation_col:
            st.markdown("**Allocation %**")
            allocations = {}
            for symbol in symbols:
                # Validate and clamp stored allocation to avoid invalid slider values
                raw_alloc = st.session_state.portfolio_items[symbol].get('allocation', 0)
                try:
                    init_alloc = float(raw_alloc)
                except Exception:
                    init_alloc = 0.0
                if init_alloc < 0.0:
                    init_alloc = 0.0
                if init_alloc > 100.0:
                    init_alloc = 100.0

                try:
                    alloc = st.slider(
                        f"Allocation for {symbol}",
                        0.0, 100.0,
                        value=init_alloc,
                        step=1.0,
                        key=f"alloc_{symbol}",
                        label_visibility="collapsed"
                    )
                except Exception as e:
                    # If Streamlit refuses the slider for any reason, show an error and
                    # fall back to a number_input so the user can still set allocations.
                    st.error(f"Unable to render slider for {symbol}: {e}")
                    alloc = st.number_input(
                        f"Allocation for {symbol}",
                        min_value=0.0, max_value=100.0, value=init_alloc,
                        step=1.0, key=f"alloc_num_{symbol}"
                    )

                allocations[symbol] = alloc
        
        # Auto-normalize if sum != 100
        total_allocation = sum(allocations.values())
        
        if total_allocation > 0 and total_allocation != 100:
            st.warning(f"⚠️ Current Total: {total_allocation:.1f}% (Need 100%)")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Auto-Balance to 100%"):
                    for symbol in symbols:
                        allocations[symbol] = (allocations[symbol] / total_allocation) * 100
                    st.success("✅ Auto-balanced to 100%")
                    st.rerun()
        
        elif total_allocation == 100:
            st.success(f"✅ Perfect allocation: {total_allocation:.1f}%")
        
        # Update session state
        for symbol, alloc in allocations.items():
            st.session_state.portfolio_items[symbol]['allocation'] = alloc
        
        # Step 3: Display allocation summary
        st.markdown("#### Step 3: Portfolio Summary")
        
        summary_data = []
        for symbol, data in st.session_state.portfolio_items.items():
            summary_data.append({
                'Stock': symbol,
                'Allocation %': f"{data['allocation']:.1f}%",
                'Remove': symbol
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # Remove stocks
        col1, col2 = st.columns([3, 1])
        with col2:
            symbol_to_remove = st.selectbox(
                "Remove stock",
                options=symbols + [''],
                key="remove_symbol"
            )
            if symbol_to_remove and st.button("🗑️ Remove", use_container_width=True):
                del st.session_state.portfolio_items[symbol_to_remove]
                st.success(f"❌ Removed {symbol_to_remove}")
                st.rerun()
        
        # Visualization: Allocation pie chart
        st.markdown("#### Portfolio Allocation Visualization")
        
        alloc_data = {
            symbol: data['allocation']
            for symbol, data in st.session_state.portfolio_items.items()
            if data['allocation'] > 0
        }
        
        if alloc_data:
            fig = go.Figure(data=[
                go.Pie(
                    labels=list(alloc_data.keys()),
                    values=list(alloc_data.values()),
                    hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>',
                    textposition='inside',
                    textinfo='label+percent'
                )
            ])
            
            fig.update_layout(
                title="Portfolio Allocation Distribution",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Export portfolio
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("💾 Save Portfolio", use_container_width=True):
                portfolio_json = {
                    symbol: data['allocation']
                    for symbol, data in st.session_state.portfolio_items.items()
                }
                st.success("✅ Portfolio saved!")
                st.json(portfolio_json)
        
        return st.session_state.portfolio_items
    
    return {}


def create_advanced_portfolio_builder():
    """
    Advanced portfolio builder with quantity and price inputs
    """
    st.markdown("### 💎 Advanced Portfolio Builder")
    st.info("Set quantities and purchase prices for precise portfolio tracking")
    
    # Initialize advanced portfolio
    if 'advanced_portfolio' not in st.session_state:
        st.session_state.advanced_portfolio = {}
    
    # Add new position
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        symbol = st.text_input("Stock Symbol", placeholder="INFY.NS", key="adv_symbol")
    with col2:
        quantity = st.number_input("Quantity", min_value=1, value=10, key="adv_qty")
    with col3:
        if st.button("✅ Add Position"):
            if symbol:
                from src.symbol_utils import normalize_symbol
                normalized = normalize_symbol(symbol)
                key_symbol = normalized if normalized else symbol.upper()
                st.session_state.advanced_portfolio[key_symbol] = {
                    'quantity': quantity,
                    'buy_price': 0,
                    'current_price': 0,
                    'notes': ''
                }
                st.success(f"✅ Added {quantity} shares of {key_symbol}")
                st.rerun()
    
    # Manage positions
    if st.session_state.advanced_portfolio:
        st.markdown("#### Manage Positions")
        
        for symbol, position in st.session_state.advanced_portfolio.items():
            with st.expander(f"📍 {symbol} - {position['quantity']} shares"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    buy_price = st.number_input(
                        "Buy Price (₹)",
                        value=position['buy_price'],
                        key=f"buy_{symbol}"
                    )
                    st.session_state.advanced_portfolio[symbol]['buy_price'] = buy_price
                
                with col2:
                    current_price = st.number_input(
                        "Current Price (₹)",
                        value=position['current_price'],
                        key=f"current_{symbol}"
                    )
                    st.session_state.advanced_portfolio[symbol]['current_price'] = current_price
                
                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button(f"🗑️ Remove", key=f"remove_{symbol}"):
                        del st.session_state.advanced_portfolio[symbol]
                        st.rerun()
                
                # Calculate metrics
                if buy_price > 0 and current_price > 0:
                    qty = position['quantity']
                    gain_loss = (current_price - buy_price) * qty
                    gain_loss_pct = ((current_price - buy_price) / buy_price) * 100
                    total_investment = buy_price * qty
                    current_value = current_price * qty
                    
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    with metric_col1:
                        st.metric("Investment", f"₹{total_investment:,.0f}")
                    with metric_col2:
                        st.metric("Current Value", f"₹{current_value:,.0f}")
                    with metric_col3:
                        color = "🟢" if gain_loss > 0 else "🔴"
                        st.metric(
                            "Gain/Loss",
                            f"₹{gain_loss:,.0f}",
                            f"{gain_loss_pct:+.2f}% {color}"
                        )
                
                notes = st.text_area(
                    "Notes",
                    value=position['notes'],
                    key=f"notes_{symbol}",
                    height=80
                )
                st.session_state.advanced_portfolio[symbol]['notes'] = notes
        
        # Portfolio summary
        st.markdown("#### 📊 Portfolio Summary")
        
        total_investment = sum(
            p['buy_price'] * p['quantity']
            for p in st.session_state.advanced_portfolio.values()
            if p['buy_price'] > 0
        )
        
        total_current_value = sum(
            p['current_price'] * p['quantity']
            for p in st.session_state.advanced_portfolio.values()
            if p['current_price'] > 0
        )
        
        total_gain_loss = total_current_value - total_investment
        total_gain_loss_pct = (total_gain_loss / total_investment * 100) if total_investment > 0 else 0
        
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        
        with summary_col1:
            st.metric("Total Investment", f"₹{total_investment:,.0f}")
        with summary_col2:
            st.metric("Current Portfolio Value", f"₹{total_current_value:,.0f}")
        with summary_col3:
            color = "🟢" if total_gain_loss >= 0 else "🔴"
            st.metric(
                "Total Gain/Loss",
                f"₹{total_gain_loss:,.0f}",
                f"{total_gain_loss_pct:+.2f}% {color}"
            )

        # Analyze positions button
        if st.button("🔎 Analyze Positions"):
            st.info("Analyzing positions using recent market data...")
            for symbol, position in st.session_state.advanced_portfolio.items():
                try:
                    from src.data_loader import load_stock_data
                    from src.ml import calculate_advanced_indicators
                except Exception:
                    st.error("Analysis modules unavailable")
                    break

                df = load_stock_data(symbol, period='1y')
                if df is None or df.empty:
                    st.warning(f"No market data for {symbol}")
                    continue

                df_ind = calculate_advanced_indicators(df.copy())
                current_price = position.get('current_price') or float(df_ind['Close'].iloc[-1])
                supertrend_dir = int(df_ind['Supertrend_Direction'].iloc[-1]) if 'Supertrend_Direction' in df_ind.columns else 0
                adx = float(df_ind['ADX'].iloc[-1]) if 'ADX' in df_ind.columns else None

                # Simple rule-based recommendation
                if supertrend_dir == -1 and (adx is None or adx >= 20):
                    rec = 'Recommend SELL (trend turned bearish)'
                elif supertrend_dir == 1 and (adx is None or adx >= 20):
                    rec = 'Recommend HOLD (trend bullish)'
                else:
                    rec = 'Neutral — Monitor price action'

                st.write(f"{symbol}: {rec} — Current: ₹{current_price:.2f} | ADX: {adx}")


def create_mobile_responsive_portfolio():
    """
    Mobile-responsive portfolio view
    Adapts layout based on viewport width
    """
    st.markdown("### 📱 Responsive Portfolio View")
    
    # Detect if mobile
    is_mobile = st.session_state.get('is_mobile', False)
    
    portfolio = st.session_state.get('portfolio_items', {})
    
    if not portfolio:
        st.info("📋 No stocks in portfolio yet. Add stocks using the Portfolio Builder above.")
        return
    
    # Mobile-optimized layout
    if is_mobile:
        st.markdown("#### 📱 Mobile View (Optimized)")
        for symbol, data in portfolio.items():
            with st.container():
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown(f"**{symbol}**")
                with col2:
                    st.markdown(f"**{data['allocation']:.1f}%**")
    else:
        st.markdown("#### 🖥️ Desktop View")
        
        # Create responsive table
        portfolio_table = pd.DataFrame([
            {
                'Stock': symbol,
                'Allocation': f"{data['allocation']:.1f}%",
                'Amount (₹)': f"₹{data['allocation'] * 100000 / 100:,.0f}",  # Based on 100k portfolio
            }
            for symbol, data in portfolio.items()
        ])
        
        st.dataframe(portfolio_table, use_container_width=True, hide_index=True)


def show_portfolio_recommendations(portfolio_items: dict, analysis_data: dict = None):
    """
    Show AI-powered portfolio recommendations
    """
    st.markdown("### 🎯 Portfolio Recommendations")
    
    if not portfolio_items:
        st.info("Add stocks to get recommendations")
        return
    st.info("Analyzing portfolio — this may take a few seconds per stock.")

    analysis_results = {}

    for symbol in portfolio_items.keys():
        try:
            from src.data_loader import load_stock_data
            from src.ml import calculate_advanced_indicators, detect_market_regime
            from src.technical_indicators import get_trend
        except Exception:
            st.error("Required analysis modules unavailable")
            return

        df = load_stock_data(symbol, period='2y')
        if df is None or df.empty:
            analysis_results[symbol] = {'error': 'No data'}
            continue

        # Compute indicators (this will add Supertrend, ATR, ADX, etc.)
        try:
            df_ind = calculate_advanced_indicators(df.copy())
        except Exception:
            df_ind = df.copy()

        current_price = float(df_ind['Close'].iloc[-1])
        atr = float(df_ind['ATR_14'].iloc[-1]) if 'ATR_14' in df_ind.columns else None
        bb_lower = float(df_ind['BB_Lower'].iloc[-1]) if 'BB_Lower' in df_ind.columns else None
        bb_upper = float(df_ind['BB_Upper'].iloc[-1]) if 'BB_Upper' in df_ind.columns else None
        supertrend_dir = int(df_ind['Supertrend_Direction'].iloc[-1]) if 'Supertrend_Direction' in df_ind.columns else 0
        adx = float(df_ind['ADX'].iloc[-1]) if 'ADX' in df_ind.columns else None
        trend = get_trend(df_ind)

        # Risk and target calculations
        vol_pct = (atr / current_price * 100) if atr and current_price else None
        suggested_stop = current_price - (atr * 2) if atr else None
        suggested_buy = bb_lower * 1.01 if bb_lower else current_price * 0.995
        suggested_sell = bb_upper * 0.99 if bb_upper else current_price * 1.05

        # Recommendation logic
        if supertrend_dir == 1 and (adx is None or adx >= 20) and trend.lower().startswith('up'):
            action = 'Hold / Consider Buying'
        elif supertrend_dir == -1 and (adx is None or adx >= 20):
            action = 'Consider Selling'
        else:
            action = 'Neutral - Monitor'

        # Compose result
        analysis_results[symbol] = {
            'current_price': current_price,
            'atr': atr,
            'volatility_pct': vol_pct,
            'support': bb_lower,
            'resistance': bb_upper,
            'supertrend_dir': supertrend_dir,
            'adx': adx,
            'trend': trend,
            'suggested_buy': float(suggested_buy) if suggested_buy is not None else None,
            'suggested_sell': float(suggested_sell) if suggested_sell is not None else None,
            'suggested_stop': float(suggested_stop) if suggested_stop is not None else None,
            'action': action
        }

    # Display results
    for symbol, res in analysis_results.items():
        with st.expander(f"{symbol} — {res.get('action', '')}"):
            if 'error' in res:
                st.error(res['error'])
                continue

            cols = st.columns([2, 1, 1, 1])
            with cols[0]:
                st.markdown(f"**Current Price:** ₹{res['current_price']:.2f}")
                st.markdown(f"**Trend:** {res['trend']}")
                st.markdown(f"**Action:** {res['action']}")
            with cols[1]:
                st.markdown(f"**Support:** {res['support']:.2f}" if res['support'] else "**Support:** N/A")
                st.markdown(f"**Buy Suggest:** {res['suggested_buy']:.2f}" if res['suggested_buy'] else "**Buy Suggest:** N/A")
            with cols[2]:
                st.markdown(f"**Resistance:** {res['resistance']:.2f}" if res['resistance'] else "**Resistance:** N/A")
                st.markdown(f"**Sell Target:** {res['suggested_sell']:.2f}" if res['suggested_sell'] else "**Sell Target:** N/A")
            with cols[3]:
                st.markdown(f"**ATR:** {res['atr']:.2f}" if res['atr'] else "**ATR:** N/A")
                st.markdown(f"**Vol %:** {res['volatility_pct']:.2f}%" if res['volatility_pct'] else "**Vol %:** N/A")

    # Risk check summary
    high_risk = [s for s, r in analysis_results.items() if r.get('volatility_pct') and r['volatility_pct'] > 3]
    if high_risk:
        st.warning(f"High volatility detected for: {', '.join(high_risk)}")
    else:
        st.success("Portfolio risk: Acceptable based on ATR volatility")
