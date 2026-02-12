"""
Reusable UI Components for Modern Interface
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def create_metric_card(label, value, delta=None, icon="📊", color="#667eea"):
    """Create a styled metric card with proper display"""
    # Create a custom HTML card that displays everything properly
    delta_html = ""
    if delta:
        delta_color = "#48bb78" if str(delta).startswith("+") or float(str(delta).replace("%", "").replace("+", "").replace("-", "")) > 0 else "#f56565"
        delta_html = f"<div style='font-size: 0.9rem; color: {delta_color}; margin-top: 5px;'>{delta}</div>"

    st.markdown(f"""
    <div style='
        text-align: center;
        padding: 20px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-top: 4px solid {color};
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    '>
        <div style='font-size: 2.5rem; margin-bottom: 8px;'>{icon}</div>
        <div style='font-size: 0.85rem; color: #718096; font-weight: 600; margin-bottom: 8px; text-transform: uppercase;'>{label}</div>
        <div style='font-size: 1.8rem; font-weight: 700; color: #2d3748; word-wrap: break-word;'>{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def create_signal_badge(signal_type, text):
    """Create a styled signal badge"""
    colors = {
        'bullish': '#c6f6d5',
        'bearish': '#fed7d7',
        'neutral': '#e2e8f0',
        'buy': '#9ae6b4',
        'sell': '#fc8181',
        'hold': '#fbd38d'
    }

    text_colors = {
        'bullish': '#22543d',
        'bearish': '#742a2a',
        'neutral': '#2d3748',
        'buy': '#22543d',
        'sell': '#742a2a',
        'hold': '#744210'
    }

    bg_color = colors.get(signal_type.lower(), '#e2e8f0')
    text_color = text_colors.get(signal_type.lower(), '#2d3748')

    return f"""
    <span style='
        background: {bg_color};
        color: {text_color};
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin: 5px;
    '>{text}</span>
    """


def create_info_card(title, content, icon="ℹ️", type="info"):
    """Create an information card with styling"""
    colors = {
        'info': '#bee3f8',
        'success': '#c6f6d5',
        'warning': '#feebc8',
        'error': '#fed7d7'
    }

    border_colors = {
        'info': '#3182ce',
        'success': '#38a169',
        'warning': '#d69e2e',
        'error': '#e53e3e'
    }

    bg = colors.get(type, colors['info'])
    border = border_colors.get(type, border_colors['info'])

    st.markdown(f"""
    <div style='
        background: {bg};
        border-left: 5px solid {border};
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
    '>
        <h3 style='margin:0; color: #2d3748;'>{icon} {title}</h3>
        <p style='margin: 10px 0 0 0; color: #4a5568;'>{content}</p>
    </div>
    """, unsafe_allow_html=True)


def create_section_header(title, subtitle=None, icon="📊"):
    """Create a styled section header"""
    st.markdown(f"""
    <div style='
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    '>
        <h1 style='margin:0; color: white;'>{icon} {title}</h1>
        {f"<p style='margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;'>{subtitle}</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def create_price_chart(data, title="Price Chart"):
    """Create an interactive price chart with Plotly"""
    fig = go.Figure()

    # Add candlestick if OHLC available
    if all(col in data.columns for col in ['Open', 'High', 'Low', 'Close']):
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Price'
        ))
    else:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='#667eea', width=2)
        ))

    # Add moving averages if available
    if 'SMA20' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['SMA20'],
            mode='lines',
            name='SMA 20',
            line=dict(color='#f093fb', width=1, dash='dash')
        ))

    if 'SMA50' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['SMA50'],
            mode='lines',
            name='SMA 50',
            line=dict(color='#f5576c', width=1, dash='dash')
        ))

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Price (₹)',
        template='plotly_white',
        hovermode='x unified',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def create_volume_chart(data, title="Volume Chart"):
    """Create a volume chart"""
    colors = ['red' if data['Close'].iloc[i] < data['Open'].iloc[i] else 'green'
              for i in range(len(data))]

    fig = go.Figure(data=[go.Bar(
        x=data.index,
        y=data['Volume'],
        marker_color=colors,
        name='Volume'
    )])

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Volume',
        template='plotly_white',
        height=300
    )

    return fig


def create_comparison_chart(data_dict, title="Comparison Chart"):
    """Create a comparison chart for multiple stocks"""
    fig = go.Figure()

    for symbol, data in data_dict.items():
        # Normalize to percentage returns
        normalized = (data['Close'] / data['Close'].iloc[0] - 1) * 100
        fig.add_trace(go.Scatter(
            x=data.index,
            y=normalized,
            mode='lines',
            name=symbol,
            line=dict(width=2)
        ))

    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Return (%)',
        template='plotly_white',
        hovermode='x unified',
        height=500,
        showlegend=True
    )

    return fig


def create_gauge_chart(value, title, min_val=0, max_val=100, threshold_low=30, threshold_high=70):
    """Create a gauge chart for metrics like RSI"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [min_val, threshold_low], 'color': "#c6f6d5"},
                {'range': [threshold_low, threshold_high], 'color': "#feebc8"},
                {'range': [threshold_high, max_val], 'color': "#fed7d7"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))

    fig.update_layout(height=300)
    return fig


def create_heatmap(data, title="Correlation Heatmap"):
    """Create a correlation heatmap"""
    fig = go.Figure(data=go.Heatmap(
        z=data.values,
        x=data.columns,
        y=data.index,
        colorscale='RdBu',
        zmid=0
    ))

    fig.update_layout(
        title=title,
        height=500,
        template='plotly_white'
    )

    return fig


def create_progress_card(title, current, target, icon="🎯"):
    """Create a progress card showing progress towards a target"""
    percentage = min((current / target * 100) if target > 0 else 0, 100)

    st.markdown(f"""
    <div style='
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    '>
        <h3 style='margin:0; color: #2d3748;'>{icon} {title}</h3>
        <div style='margin: 15px 0;'>
            <div style='
                background: #e2e8f0;
                border-radius: 10px;
                height: 10px;
                overflow: hidden;
            '>
                <div style='
                    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                    height: 100%;
                    width: {percentage}%;
                    transition: width 0.3s ease;
                '></div>
            </div>
        </div>
        <p style='margin: 10px 0 0 0; color: #4a5568;'>
            {current:.2f} / {target:.2f} ({percentage:.1f}%)
        </p>
    </div>
    """, unsafe_allow_html=True)


def create_table_with_styling(df, highlight_column=None):
    """Create a styled dataframe with conditional formatting"""
    if highlight_column and highlight_column in df.columns:
        styled_df = df.style.background_gradient(
            subset=[highlight_column],
            cmap='RdYlGn'
        )
        return styled_df
    return df

