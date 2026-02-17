"""
Portfolio Manager page module for AI Trading Lab PRO+
Persistent portfolio storage with Supabase
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
    
    # Get current user from session
    user_id = st.session_state.get('user_id')
    user_email = st.session_state.get('user_email')
    
    if not user_id:
        st.error("Please login to use Portfolio Manager")
        return
    
    st.markdown(f"""
    <div style='background: {theme_colors['gradient_bg']}; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>
        <h1 style='color: white; margin: 0;'>💼 Portfolio Manager</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 10px 0 0 0;'>
            Build, Optimize, and Track Your Investment Portfolio
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load saved portfolios from Supabase
    from src.supabase_client import get_supabase_client
    supabase = get_supabase_client()
    
    # Portfolio management section
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 💾 Your Saved Portfolios")
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            try:
                from src.supabase_client import get_supabase_client
                supabase = get_supabase_client()
                if user_id and supabase.is_connected():
                    supabase.log_activity(
                        user_id=user_id,
                        activity_type='portfolio_refresh',
                        description="Portfolio list refreshed",
                        status='success'
                    )
            except Exception:
                pass
            st.rerun()
    
    # Fetch saved portfolios
    saved_portfolios = supabase.get_user_portfolios(user_id)
    
    if saved_portfolios:
        # Display saved portfolios
        portfolio_names = [p['portfolio_name'] for p in saved_portfolios]
        selected_portfolio = st.selectbox(
            "Select a saved portfolio to load",
            portfolio_names,
            key="portfolio_selector"
        )
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📂 Load Portfolio", use_container_width=True):
                portfolio = supabase.get_portfolio_by_name(user_id, selected_portfolio)
                if portfolio:
                    import json
                    st.session_state.portfolio_items = json.loads(portfolio['config_data'])
                    st.success(f"✅ Loaded: {selected_portfolio}")
                    try:
                        if user_id and supabase.is_connected():
                            supabase.log_activity(
                                user_id=user_id,
                                activity_type='portfolio_load',
                                description=f"Loaded portfolio {selected_portfolio}",
                                action_details={'portfolio_name': selected_portfolio},
                                status='success'
                            )
                    except Exception:
                        pass
                    st.rerun()

        with col2:
            if st.button("🗑️ Delete Portfolio", use_container_width=True):
                if supabase.delete_portfolio(user_id, selected_portfolio):
                    st.success(f"✅ Deleted: {selected_portfolio}")
                    try:
                        if user_id and supabase.is_connected():
                            supabase.log_activity(
                                user_id=user_id,
                                activity_type='portfolio_delete',
                                description=f"Deleted portfolio {selected_portfolio}",
                                action_details={'portfolio_name': selected_portfolio},
                                status='success'
                            )
                    except Exception:
                        pass
                    st.rerun()
                else:
                    st.error("Failed to delete portfolio")

        with col3:
            if st.button("📥 Export JSON", use_container_width=True):
                portfolio = supabase.get_portfolio_by_name(user_id, selected_portfolio)
                if portfolio:
                    import json
                    portfolio_json = json.dumps(json.loads(portfolio['config_data']), indent=2)
                    try:
                        if user_id and supabase.is_connected():
                            supabase.log_activity(
                                user_id=user_id,
                                activity_type='portfolio_export',
                                description=f"Exported portfolio {selected_portfolio}",
                                action_details={'portfolio_name': selected_portfolio},
                                status='success'
                            )
                    except Exception:
                        pass
                    st.download_button(
                        label="Download Portfolio",
                        data=portfolio_json,
                        file_name=f"{selected_portfolio}.json",
                        mime="application/json",
                        key="download_portfolio_json"
                    )

        with col4:
            if st.button("📋 Duplicate", use_container_width=True):
                portfolio = supabase.get_portfolio_by_name(user_id, selected_portfolio)
                if portfolio:
                    import json
                    st.session_state.portfolio_items = json.loads(portfolio['config_data'])
                    st.session_state.new_portfolio_name = f"{selected_portfolio} (Copy)"
                    st.success("Copied! Change name and save as new")
                    try:
                        if user_id and supabase.is_connected():
                            supabase.log_activity(
                                user_id=user_id,
                                activity_type='portfolio_duplicate',
                                description=f"Duplicated portfolio {selected_portfolio}",
                                action_details={'portfolio_name': selected_portfolio},
                                status='success'
                            )
                    except Exception:
                        pass
                    st.rerun()
    else:
        st.info("📭 No saved portfolios yet. Create one below!")
    
    # Portfolio builder tabs
    tabs = st.tabs(["📊 Quick Builder", "💎 Advanced Builder", "🎯 AI Recommendations", "📈 Performance"])
    
    with tabs[0]:
        st.markdown("### 🏗️ Create or Edit Portfolio")
        portfolio_items = create_portfolio_builder()
        
        # Save portfolio section
        st.markdown("---")
        col1, col2 = st.columns([2, 1])
        with col1:
            portfolio_name = st.text_input(
                "Portfolio name (e.g., 'My Growth Portfolio')",
                value=st.session_state.get('new_portfolio_name', ''),
                key="portfolio_name_input"
            )
        with col2:
            if st.button("💾 Save Portfolio", use_container_width=True, type="primary"):
                if not portfolio_name.strip():
                    st.error("Please enter a portfolio name")
                elif not st.session_state.portfolio_items:
                    st.error("Portfolio is empty. Add some stocks first!")
                else:
                    result = supabase.save_portfolio_config(
                        user_id=user_id,
                        portfolio_name=portfolio_name.strip(),
                        config_data=st.session_state.portfolio_items
                    )
                    if result:
                        st.success(f"✅ Portfolio saved: {portfolio_name}")
                        try:
                            if user_id and supabase.is_connected():
                                supabase.log_activity(
                                    user_id=user_id,
                                    activity_type='portfolio_save',
                                    description=f"Saved portfolio {portfolio_name}",
                                    action_details={'portfolio_name': portfolio_name.strip()},
                                    status='success'
                                )
                        except Exception:
                            pass
                        st.session_state.new_portfolio_name = ""
                        st.rerun()
                    else:
                        st.error("Failed to save portfolio")
    
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