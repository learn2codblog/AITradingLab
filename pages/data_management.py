# -*- coding: utf-8 -*-
"""
Data Management Dashboard - Show all saved user data
Watchlists, Backtest Results, Settings, Activity Log
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from src.supabase_client import get_supabase_client


def render_watchlist_manager():
    """Display and manage user's watchlist"""
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("Please login first")
        return
    
    supabase = get_supabase_client()
    
    st.markdown("### \U0001f4a0 Your Watchlist")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_symbol = st.text_input(
            "Add stock to watchlist",
            placeholder="e.g., INFY, TCS, RELIANCE",
            key="watchlist_symbol_input"
        )
    with col2:
        if st.button("➕ Add", use_container_width=True):
            if new_symbol.strip():
                if supabase.add_to_watchlist(user_id, new_symbol.strip().upper()):
                    st.success(f"✅ Added {new_symbol} to watchlist")
                    st.rerun()
    
    # Display watchlist
    watchlist = supabase.get_user_watchlist(user_id)
    
    if watchlist:
        st.markdown(f"**{len(watchlist)} stocks in your watchlist**")
        
        cols = st.columns(3)
        for idx, symbol in enumerate(watchlist):
            with cols[idx % 3]:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📊 {symbol}")
                with col2:
                    if st.button("🗑️", key=f"remove_{symbol}", use_container_width=True):
                        if supabase.remove_from_watchlist(user_id, symbol):
                            st.success(f"Removed {symbol}")
                            st.rerun()
    else:
        st.info("No stocks in watchlist yet")


def render_backtest_history():
    """Display user's backtest history with detailed metrics and views"""
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("Please login first")
        return
    
    supabase = get_supabase_client()
    
    st.markdown("### 📊 Backtest History")
    
    # Fetch backtest results
    backtest_results = supabase.get_user_backtest_results(user_id, limit=50)
    
    if backtest_results:
        # Summary stats
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        with summary_col1:
            st.metric("Total Backtests", len(backtest_results))
        with summary_col2:
            avg_return = sum([
                json.loads(r.get('result_data', '{}'))['metrics'].get('total_return', 0) 
                if isinstance(r.get('result_data'), str) else r.get('result_data', {}).get('metrics', {}).get('total_return', 0)
                for r in backtest_results
            ]) / len(backtest_results) if backtest_results else 0
            st.metric("Avg Return", f"{avg_return:.2f}%")
        with summary_col3:
            total_trades = sum([
                json.loads(r.get('result_data', '{}'))['metrics'].get('total_trades', 0)
                if isinstance(r.get('result_data'), str) else r.get('result_data', {}).get('metrics', {}).get('total_trades', 0)
                for r in backtest_results
            ])
            st.metric("Total Trades", total_trades)
        with summary_col4:
            winning_tests = sum([
                1 for r in backtest_results
                if (json.loads(r.get('result_data', '{}'))['metrics'].get('total_return', 0) > 0
                    if isinstance(r.get('result_data'), str) else 
                    r.get('result_data', {}).get('metrics', {}).get('total_return', 0) > 0)
            ])
            st.metric("Winning Strategies", f"{winning_tests}/{len(backtest_results)}")
        
        st.markdown("---")
        
        # Create dataframe for table view
        data = []
        for idx, result in enumerate(backtest_results):
            try:
                result_data = json.loads(result.get('result_data', '{}')) if isinstance(result.get('result_data'), str) else result.get('result_data', {})
                metrics = result_data.get('metrics', {})
                
                data.append({
                    'ID': idx + 1,
                    'Test Name': result['test_name'],
                    'Strategy': result_data.get('strategy', 'N/A'),
                    'Symbol': result_data.get('symbol', 'N/A'),
                    'Return (%)': f"{metrics.get('total_return', 0):.2f}",
                    'Sharpe Ratio': f"{metrics.get('sharpe_ratio', 0):.2f}",
                    'Win Rate (%)': f"{metrics.get('win_rate', 0)*100:.1f}",
                    'Total Trades': metrics.get('total_trades', 0),
                    'Max Drawdown (%)': f"{metrics.get('max_drawdown', 0):.2f}",
                    'Date': datetime.fromisoformat(result['created_at']).strftime('%Y-%m-%d %H:%M')
                })
            except Exception as e:
                continue
        
        if data:
            df = pd.DataFrame(data)
            
            # Display options
            view_mode = st.radio("View Mode", ["Table", "Detailed Cards"], horizontal=True, key="backtest_view_mode")
            
            if view_mode == "Table":
                st.dataframe(df, use_container_width=True, hide_index=True, height=400)
                
                # Export options
                export_col1, export_col2 = st.columns([3, 1])
                with export_col2:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Export CSV",
                        data=csv,
                        file_name=f"backtest_history_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            else:  # Detailed Cards view
                for idx, backtest in enumerate(backtest_results[:10]):  # Show max 10 in card view
                    try:
                        result_data = json.loads(backtest.get('result_data', '{}')) if isinstance(backtest.get('result_data'), str) else backtest.get('result_data', {})
                        metrics = result_data.get('metrics', {})
                        
                        with st.expander(f"🎯 {backtest['test_name']} - {metrics.get('total_return', 0):.2f}% Return", expanded=False):
                            card_col1, card_col2, card_col3 = st.columns(3)
                            
                            with card_col1:
                                st.markdown("**Strategy Info**")
                                st.write(f"**Strategy:** {result_data.get('strategy', 'N/A')}")
                                st.write(f"**Symbol:** {result_data.get('symbol', 'N/A')}")
                                st.write(f"**Date:** {datetime.fromisoformat(backtest['created_at']).strftime('%Y-%m-%d %H:%M')}")
                            
                            with card_col2:
                                st.markdown("**Performance Metrics**")
                                st.write(f"**Total Return:** {metrics.get('total_return', 0):.2f}%")
                                st.write(f"**Sharpe Ratio:** {metrics.get('sharpe_ratio', 0):.2f}")
                                st.write(f"**Win Rate:** {metrics.get('win_rate', 0)*100:.1f}%")
                            
                            with card_col3:
                                st.markdown("**Risk Metrics**")
                                st.write(f"**Max Drawdown:** {metrics.get('max_drawdown', 0):.2f}%")
                                st.write(f"**Total Trades:** {metrics.get('total_trades', 0)}")
                                st.write(f"**Profit Factor:** {metrics.get('profit_factor', 0):.2f}")
                            
                            # Delete button
                            if st.button(f"🗑️ Delete", key=f"delete_backtest_{idx}"):
                                if supabase.delete_backtest_result(user_id, backtest['test_name']):
                                    st.success(f"✅ Deleted backtest '{backtest['test_name']}'")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete backtest")
                    
                    except Exception as e:
                        st.error(f"Error displaying backtest: {str(e)}")
        else:
            st.info("No backtest results to display")
    else:
        st.info("📊 No backtest history yet. Run some backtests to see them here!")


def render_user_settings():
    """Display and manage user settings"""
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("Please login first")
        return
    
    supabase = get_supabase_client()
    
    st.markdown("### \u2699\ufe0f User Settings & Preferences")
    
    # Fetch current settings
    user_settings = supabase.get_user_settings(user_id)
    if user_settings and isinstance(user_settings.get('settings'), str):
        current_settings = json.loads(user_settings['settings'])
    else:
        current_settings = {}
    
    col1, col2 = st.columns(2)
    with col1:
        dark_mode = st.checkbox(
            "🌙 Dark Mode",
            value=current_settings.get('dark_mode', True)
        )
        notifications = st.checkbox(
            "\U0001f514 Enable Notifications",
            value=current_settings.get('notifications_enabled', True)
        )
    
    with col2:
        theme = st.selectbox(
            "Theme",
            ["Purple Gradient", "Blue Ocean", "Green Forest", "Dark Night"],
            index=["Purple Gradient", "Blue Ocean", "Green Forest", "Dark Night"].index(current_settings.get('theme', 'Purple Gradient'))
        )
        confidence_threshold = st.slider(
            "Minimum Confidence (%)",
            min_value=0,
            max_value=100,
            value=current_settings.get('confidence_threshold', 60),
            step=5
        )
    
    if st.button("💾 Save Settings", use_container_width=True, type="primary"):
        settings_to_save = {
            'dark_mode': dark_mode,
            'notifications_enabled': notifications,
            'theme': theme,
            'confidence_threshold': confidence_threshold
        }
        
        if supabase.save_user_settings(user_id, settings_to_save):
            st.success("✅ Settings saved successfully!")
            st.rerun()
        else:
            st.error("Failed to save settings")


def render_activity_log():
    """Display user's activity log"""
    user_id = st.session_state.get('user_id')
    if not user_id:
        st.error("Please login first")
        return
    
    supabase = get_supabase_client()
    
    st.markdown("### \U0001f4f3 Activity Log")
    
    # Fetch activities
    activities = supabase.get_user_activities(user_id, limit=50)
    
    if activities:
        # Create dataframe
        data = []
        for activity in activities:
            try:
                data.append({
                    'Activity': activity['activity_type'].replace('_', ' ').title(),
                    'Description': activity['description'],
                    'Status': activity.get('status', 'success'),
                    'Date': datetime.fromisoformat(activity['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                })
            except:
                continue
        
        if data:
            df = pd.DataFrame(data)
            
            # Color code by status
            def highlight_status(row):
                if row['Status'] == 'success':
                    return ['background-color: #d4edda'] * len(row)
                elif row['Status'] == 'failed':
                    return ['background-color: #f8d7da'] * len(row)
                else:
                    return [''] * len(row)
            
            st.dataframe(
                df.style.apply(highlight_status, axis=1),
                use_container_width=True,
                hide_index=True
            )
            
            # Activity stats
            col1, col2, col3 = st.columns(3)
            with col1:
                success_count = len([a for a in activities if a.get('status') == 'success'])
                st.metric("Successful Actions", success_count)
            with col2:
                failed_count = len([a for a in activities if a.get('status') == 'failed'])
                st.metric("Failed Actions", failed_count)
            with col3:
                st.metric("Total Activities", len(activities))
        else:
            st.info("No activity log to display")
    else:
        st.info("No activities yet")


def render_data_management():
    """Main data management dashboard"""
    st.markdown("## 💾 My Data & Preferences")
    
    tabs = st.tabs(["📦 Watchlist", "\U0001f4ca Backtest History", "\u2699\ufe0f Settings", "\U0001f4f3 Activity Log"])
    
    with tabs[0]:
        render_watchlist_manager()
    
    with tabs[1]:
        render_backtest_history()
    
    with tabs[2]:
        render_user_settings()
    
    with tabs[3]:
        render_activity_log()
