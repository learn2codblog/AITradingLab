"""
Portfolio Manager page module for AI Trading Lab PRO+
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ui.components import create_section_header, get_theme_colors
from ui.portfolio_builder import (
    create_portfolio_builder,
    create_advanced_portfolio_builder,
    show_portfolio_recommendations
)


def render_portfolio_manager():
    """Render the Portfolio Manager page with full functionality."""
    theme_colors = get_theme_colors()
    
    st.markdown(f"""
    <div style='background: {theme_colors['gradient_bg']}; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>
        <h1 style='color: white; margin: 0;'>💼 Portfolio Manager</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 10px 0 0 0;'>
            Build, Optimize, and Track Your Investment Portfolio
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Portfolio builder tabs
    tabs = st.tabs(["📊 Quick Builder", "💎 Advanced Builder", "🎯 AI Recommendations", "📈 Performance"])
    
    with tabs[0]:
        portfolio_items = create_portfolio_builder()
    
    with tabs[1]:
        create_advanced_portfolio_builder()
    
    with tabs[2]:
        st.markdown("### 🎯 AI-Powered Portfolio Recommendations")
        portfolio_items = st.session_state.get('portfolio_items', {})
        
        if portfolio_items:
            show_portfolio_recommendations(portfolio_items)
        else:
            st.info("📋 Add stocks to your portfolio to get AI recommendations")
    
    with tabs[3]:
        st.markdown("### 📈 Portfolio Performance Analysis")
        show_portfolio_performance()


def show_portfolio_performance():
    """Display portfolio performance metrics."""
    adv_portfolio = st.session_state.get('advanced_portfolio', {})
    
    if not adv_portfolio:
        st.info("📋 Add stocks in Advanced Builder tab to track performance")
        return
    
    total_investment = sum(
        p['buy_price'] * p['quantity']
        for p in adv_portfolio.values()
        if p.get('buy_price', 0) > 0
    )
    
    total_current = sum(
        p['current_price'] * p['quantity']
        for p in adv_portfolio.values()
        if p.get('current_price', 0) > 0
    )
    
    if total_investment > 0:
        total_gain = total_current - total_investment
        total_gain_pct = (total_gain / total_investment) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Investment", f"₹{total_investment:,.0f}")
        with col2:
            st.metric("Current Value", f"₹{total_current:,.0f}")
        with col3:
            st.metric("Total Gain/Loss", f"₹{total_gain:,.0f}", f"{total_gain_pct:+.2f}%")
        
        # Performance chart
        perf_data = []
        for symbol, data in adv_portfolio.items():
            if data.get('buy_price', 0) > 0 and data.get('current_price', 0) > 0:
                gain = (data['current_price'] - data['buy_price']) * data['quantity']
                perf_data.append({'Stock': symbol, 'Gain/Loss': gain})
        
        if perf_data:
            df_perf = pd.DataFrame(perf_data)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=df_perf['Stock'],
                    y=df_perf['Gain/Loss'],
                    marker_color=['#48bb78' if x > 0 else '#f56565' for x in df_perf['Gain/Loss']]
                )
            ])
            
            fig.update_layout(
                title="Individual Stock Performance",
                xaxis_title="Stock",
                yaxis_title="Gain/Loss (₹)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)