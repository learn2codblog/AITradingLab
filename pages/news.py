"""
General News page module for AI Trading Lab PRO+
Comprehensive news aggregation and sentiment analysis
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ui.components import create_section_header, create_info_card, get_theme_colors
from src.fundamental_analysis import get_news_sentiment
from src.news_provider import NewsProvider
import plotly.graph_objects as go

try:
    import yfinance as yf
except ImportError:
    yf = None


def render_general_news():
    """Render the General News page content."""
    theme_colors = get_theme_colors()
    
    st.markdown(f"""
    <div style='background: {theme_colors['gradient_bg']}; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;'>
        <h1 style='color: white; margin: 0;'>📰 Market News & Analysis</h1>
        <p style='color: rgba(255,255,255,0.9); margin: 10px 0 0 0;'>
            Stay Informed with Latest Market News, Company Updates & AI-Powered Sentiment Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

    # News categories
    news_tabs = st.tabs([
        "📈 Market News", 
        "📰 Company News", 
        "📊 Sentiment Analysis", 
        "🔍 News Search",
        "🔥 Trending Topics"
    ])

    with news_tabs[0]:
        render_market_news(theme_colors)

    with news_tabs[1]:
        render_company_news(theme_colors)

    with news_tabs[2]:
        render_sentiment_analysis(theme_colors)

    with news_tabs[3]:
        render_news_search(theme_colors)
    
    with news_tabs[4]:
        render_trending_topics(theme_colors)


def render_market_news(theme_colors: dict):
    """Render market news tab with filtering and categorization."""
    st.markdown("### 🏛️ Financial Market News Feed")
    
    # Filter options
    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 2])
    
    with filter_col1:
        category = st.selectbox(
            "📁 Category",
            ["All", "Finance", "Politics"],
            help="Filter news by category"
        )
    
    with filter_col2:
        days = st.slider(
            "📅 Days Back",
            1, 30, 7,
            help="Show news from last N days"
        )
    
    with filter_col3:
        sort_order = st.selectbox(
            "⏱️ Sort By",
            ["Latest First", "Oldest First"],
            help="Sort order"
        )
    
    # Get news from provider
    news = NewsProvider.get_latest_news(days=days, category=category)
    
    if sort_order == "Oldest First":
        news = list(reversed(news))
    
    # Display news count
    st.info(f"📊 Showing {len(news)} articles from the past {days} days")
    
    if not news:
        st.warning("No news found for selected filters")
        return
    
    # Display news articles
    for idx, article in enumerate(news, 1):
        render_news_card(article, idx, theme_colors)


def render_news_card(article: dict, index: int, theme_colors: dict):
    """Render individual news card with expandable content."""
    # Determine color by category
    category_colors = {
        "Finance": "#48bb78",
        "Politics": "#4299e1",
        "Announcements": "#ed8936"
    }
    
    category_emojis = {
        "Finance": "💰",
        "Politics": "🏛️",
        "Announcements": "📢"
    }
    
    border_color = category_colors.get(article['category'], "#718096")
    category_emoji = category_emojis.get(article['category'], "📰")
    
    # Format timestamp
    time_diff = datetime.now() - article['timestamp']
    if time_diff.seconds < 3600:
        time_str = f"{time_diff.seconds // 60} minutes ago"
    elif time_diff.seconds < 86400:
        time_str = f"{time_diff.seconds // 3600} hours ago"
    else:
        time_str = f"{time_diff.days} days ago"
    
    # Render card
    with st.expander(f"{category_emoji} {article['title']}", expanded=(index <= 2)):
        st.markdown(f"""
        <div style='padding: 10px; border-left: 4px solid {border_color}; background: {theme_colors['card_bg']}; border-radius: 8px; margin: 10px 0;'>
            <p style='margin: 0; color: {theme_colors['text']}; font-size: 1.05em;'>
                {article['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Metadata
        meta_col1, meta_col2, meta_col3 = st.columns(3)
        with meta_col1:
            st.caption(f"📰 **Source:** {article['source']}")
        with meta_col2:
            st.caption(f"🏷️ **Category:** {article['category']}")
        with meta_col3:
            st.caption(f"⏰ **Posted:** {time_str}")
        
        # Read more button if URL exists
        if article.get('url') and article['url'] != '#':
            st.markdown(f"[🔗 Read Full Article]({article['url']})")


def render_company_news(theme_colors: dict):
    """Render company-specific news with sentiment analysis."""
    st.markdown("### 🏢 Company-Specific News & Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        symbol = st.text_input(
            "Enter Stock Symbol",
            "RELIANCE.NS",
            key="news_symbol",
            help="Enter NSE symbol (e.g., RELIANCE.NS, TCS.NS)"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        fetch_button = st.button("🔍 Fetch News", key="get_company_news", use_container_width=True, type="primary")
    
    if fetch_button and yf:
        # Log activity
        try:
            from src.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            user_id = st.session_state.get('user_id')
            if user_id and supabase.is_connected():
                supabase.log_activity(
                    user_id=user_id,
                    activity_type='news_company_fetch',
                    description=f"Company news fetch for {symbol}",
                    action_details={
                        'symbol': symbol
                    },
                    status='success'
                )
        except Exception:
            pass

        with st.spinner(f"📡 Fetching news for {symbol}..."):
            try:
                ticker = yf.Ticker(symbol)
                news_items = ticker.news
                
                if news_items and len(news_items) > 0:
                    st.success(f"✅ Found {len(news_items)} news items for {symbol}")
                    
                    # Calculate overall sentiment
                    positive_words = ['buy', 'upgrade', 'bullish', 'growth', 'profit', 'surge', 'rally', 'strong', 'outperform']
                    negative_words = ['sell', 'downgrade', 'bearish', 'loss', 'decline', 'crash', 'weak', 'fall', 'underperform']
                    
                    sentiment_scores = []
                    
                    # Display each news item
                    for idx, item in enumerate(news_items[:15], 1):  # Show top 15
                        title = item.get('title', 'No title')
                        publisher = item.get('publisher', 'Unknown')
                        link = item.get('link', '#')
                        
                        # Analyze sentiment
                        title_lower = title.lower()
                        pos_count = sum(1 for word in positive_words if word in title_lower)
                        neg_count = sum(1 for word in negative_words if word in title_lower)
                        
                        if pos_count > neg_count:
                            sentiment = 'Positive'
                            sentiment_color = '#48bb78'
                            sentiment_icon = '🟢'
                            score = 0.5 + (pos_count / (pos_count + neg_count + 1)) * 0.5
                        elif neg_count > pos_count:
                            sentiment = 'Negative'
                            sentiment_color = '#f56565'
                            sentiment_icon = '🔴'
                            score = -0.5 - (neg_count / (pos_count + neg_count + 1)) * 0.5
                        else:
                            sentiment = 'Neutral'
                            sentiment_color = '#ed8936'
                            sentiment_icon = '🟡'
                            score = 0
                        
                        sentiment_scores.append(score)
                        
                        # Convert timestamp if available
                        try:
                            pub_time = datetime.fromtimestamp(item.get('providerPublishTime', 0))
                            time_ago = datetime.now() - pub_time
                            if time_ago.days > 0:
                                time_str = f"{time_ago.days}d ago"
                            elif time_ago.seconds >= 3600:
                                time_str = f"{time_ago.seconds // 3600}h ago"
                            else:
                                time_str = f"{time_ago.seconds // 60}m ago"
                        except:
                            time_str = "Recently"
                        
                        # Render news item
                        st.markdown(f"""
                        <div style='border-left: 4px solid {sentiment_color}; padding: 12px; margin: 12px 0; 
                                    background: {theme_colors['card_bg']}; border-radius: 8px;'>
                            <div style='display: flex; justify-content: space-between; align-items: start;'>
                                <h4 style='margin: 0 0 8px 0; color: {theme_colors['text']}; flex: 1;'>
                                    {idx}. {title}
                                </h4>
                                <span style='background: {sentiment_color}; color: white; padding: 4px 12px; 
                                            border-radius: 12px; font-size: 0.85em; margin-left: 10px; white-space: nowrap;'>
                                    {sentiment_icon} {sentiment}
                                </span>
                            </div>
                            <p style='margin: 8px 0 4px 0; color: {theme_colors['text_secondary']}; font-size: 0.9em;'>
                                📰 {publisher} • ⏰ {time_str}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if link and link != '#':
                            st.markdown(f"[🔗 Read Full Article]({link})")
                        
                        st.markdown("---")
                    
                    # Overall sentiment summary
                    if sentiment_scores:
                        avg_sentiment = np.mean(sentiment_scores)
                        
                        st.markdown("### 📊 Overall News Sentiment")
                        
                        if avg_sentiment > 0.15:
                            overall = "Bullish"
                            overall_color = "#48bb78"
                            overall_icon = "🟢"
                        elif avg_sentiment < -0.15:
                            overall = "Bearish"
                            overall_color = "#f56565"
                            overall_icon = "🔴"
                        else:
                            overall = "Neutral"
                            overall_color = "#ed8936"
                            overall_icon = "🟡"
                        
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, {overall_color}20, {overall_color}10); 
                                    padding: 20px; border-radius: 12px; text-align: center; 
                                    border: 2px solid {overall_color};'>
                            <h2 style='margin: 0; color: {overall_color};'>
                                {overall_icon} {overall}
                            </h2>
                            <p style='margin: 10px 0 0 0; font-size: 1.1em; color: {theme_colors['text']}'>
                                Sentiment Score: {avg_sentiment:.2f} (-1 to +1)
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                
                else:
                    st.warning(f"⚠️ No news data available for {symbol}")
                    st.info("💡 Try entering a different symbol or check if the symbol format is correct (e.g., RELIANCE.NS for NSE)")
                    
            except Exception as e:
                st.error(f"❌ Error fetching news: {str(e)}")
                st.info("💡 Make sure you have an active internet connection and the symbol is valid")
    
    elif fetch_button and not yf:
        st.error("❌ yfinance library is required for company news. Install it with: pip install yfinance")


def render_sentiment_analysis(theme_colors: dict):
    """Render comprehensive market sentiment analysis."""
    st.markdown("### 🎭 Market Sentiment Dashboard")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        symbols = st.text_area(
            "Enter Stock Symbols (one per line)",
            "RELIANCE.NS\nTCS.NS\nINFY.NS\nHDFCBANK.NS\nICICIBANK.NS",
            height=150,
            help="Enter multiple symbols to compare sentiment"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button("📊 Analyze Sentiment", use_container_width=True, type="primary")
    
    if analyze_button:
        symbol_list = [s.strip() for s in symbols.split('\n') if s.strip()]

        if not symbol_list:
            st.warning("Please enter at least one symbol")
            return

        # Log activity
        try:
            from src.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            user_id = st.session_state.get('user_id')
            if user_id and supabase.is_connected():
                supabase.log_activity(
                    user_id=user_id,
                    activity_type='news_sentiment',
                    description="News sentiment analysis",
                    action_details={
                        'symbols': symbol_list
                    },
                    status='success'
                )
        except Exception:
            pass

        st.info(f"🔄 Analyzing sentiment for {len(symbol_list)} stocks...")
        
        results = []
        progress_bar = st.progress(0)
        
        for idx, symbol in enumerate(symbol_list):
            try:
                sentiment_score = get_news_sentiment(symbol)
                
                if sentiment_score > 0.15:
                    sentiment = "Bullish"
                    color = "#48bb78"
                    icon = "🟢"
                elif sentiment_score < -0.15:
                    sentiment = "Bearish"
                    color = "#f56565"
                    icon = "🔴"
                else:
                    sentiment = "Neutral"
                    color = "#ed8936"
                    icon = "🟡"
                
                results.append({
                    'Symbol': symbol,
                    'Sentiment': sentiment,
                    'Score': sentiment_score,
                    'Color': color,
                    'Icon': icon
                })
                
            except Exception as e:
                results.append({
                    'Symbol': symbol,
                    'Sentiment': 'Error',
                    'Score': 0,
                    'Color': '#718096',
                    'Icon': '⚪'
                })
            
            progress_bar.progress((idx + 1) / len(symbol_list))
        
        progress_bar.empty()
        
        # Display results
        st.success(f"✅ Analysis complete for {len(results)} stocks")
        
        # Create sentiment chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=[r['Symbol'] for r in results],
            y=[r['Score'] for r in results],
            marker_color=[r['Color'] for r in results],
            text=[f"{r['Icon']} {r['Sentiment']}" for r in results],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Score: %{y:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="📊 News Sentiment Comparison",
            xaxis_title="Stock Symbol",
            yaxis_title="Sentiment Score",
            yaxis=dict(range=[-1, 1], zeroline=True, zerolinewidth=2, zerolinecolor='gray'),
            height=500,
            template='plotly_dark' if theme_colors.get('is_dark', False) else 'plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed results table
        st.markdown("### 📋 Detailed Results")
        
        for result in sorted(results, key=lambda x: x['Score'], reverse=True):
            st.markdown(f"""
            <div style='background: {theme_colors['card_bg']}; padding: 16px; border-radius: 8px; 
                        margin: 10px 0; border-left: 4px solid {result['Color']};'>
                <h4 style='margin: 0; color: {theme_colors['text']};'>
                    {result['Icon']} {result['Symbol']} - {result['Sentiment']}
                </h4>
                <p style='margin: 8px 0 0 0; color: {theme_colors['text_secondary']}'>
                    Sentiment Score: <strong>{result['Score']:.2f}</strong> (-1 to +1)
                </p>
            </div>
            """, unsafe_allow_html=True)


def render_news_search(theme_colors: dict):
    """Render advanced news search functionality."""
    st.markdown("### 🔍 Advanced News Search")
    
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        search_query = st.text_input(
            "Search Keywords",
            placeholder="Enter keywords, company names, or topics...",
            help="Search through news articles by keywords"
        )
    
    with search_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button("🔍 Search", use_container_width=True, type="primary")
    
    # Advanced filters
    with st.expander("🔧 Advanced Filters", expanded=False):
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            category_filter = st.selectbox("Category", ["All", "Finance", "Politics"])
        
        with filter_col2:
            days_filter = st.slider("Days Back", 1, 30, 7)
        
        with filter_col3:
            source_filter = st.multiselect(
                "Sources",
                ["Reuters", "Bloomberg", "CNBC", "Financial Times", "Trading View"],
                default=[]
            )
    
    if search_button and search_query:
        # Log activity
        try:
            from src.supabase_client import get_supabase_client
            supabase = get_supabase_client()
            user_id = st.session_state.get('user_id')
            if user_id and supabase.is_connected():
                supabase.log_activity(
                    user_id=user_id,
                    activity_type='news_search',
                    description="News search",
                    action_details={
                        'query': search_query,
                        'category': category_filter,
                        'days': days_filter,
                        'sources': source_filter
                    },
                    status='success'
                )
        except Exception:
            pass

        st.info(f"🔄 Searching for: '{search_query}'")
        
        # Get all news
        news = NewsProvider.get_latest_news(days=days_filter, category=category_filter)
        
        # Filter by search query
        search_lower = search_query.lower()
        filtered_news = [
            article for article in news
            if search_lower in article['title'].lower() or 
               search_lower in article['description'].lower()
        ]
        
        # Filter by source if specified
        if source_filter:
            filtered_news = [
                article for article in filtered_news
                if article['source'] in source_filter
            ]
        
        if filtered_news:
            st.success(f"✅ Found {len(filtered_news)} matching articles")
            
            for idx, article in enumerate(filtered_news, 1):
                render_news_card(article, idx, theme_colors)
        else:
            st.warning(f"⚠️ No articles found matching '{search_query}'")
            st.info("💡 Try different keywords or broaden your search filters")
    
    elif not search_query:
        st.info("💡 Enter keywords above and click Search to find relevant news articles")


def render_trending_topics(theme_colors: dict):
    """Render trending topics and related news."""
    st.markdown("### 🔥 Trending Market Topics")
    
    trending = NewsProvider.get_trending_topics()
    
    # Display trending topics
    cols = st.columns(3)
    
    for idx, topic in enumerate(trending):
        with cols[idx % 3]:
            # Count related articles
            all_news = NewsProvider.get_latest_news(days=7)
            related_count = sum(
                1 for article in all_news
                if topic.lower() in article['description'].lower() or 
                   topic.lower() in article['title'].lower()
            )
            
            st.markdown(f"""
            <div style='background: {theme_colors['card_bg']}; padding: 20px; border-radius: 12px; 
                        text-align: center; border: 2px solid {theme_colors['gradient_bg']};'>
                <h3 style='margin: 0; color: {theme_colors['text']};'>#{idx + 1}</h3>
                <h4 style='margin: 10px 0; color: {theme_colors['text']};'>{topic}</h4>
                <p style='margin: 0; color: {theme_colors['text_secondary']}; font-size: 1.2em;'>
                    📰 {related_count} articles
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
    
    # Show related news for selected topic
    st.markdown("---")
    st.markdown("### 📰 News by Topic")
    
    selected_topic = st.selectbox("Select Topic to View Related News", trending, key="trending_topic")
    
    if selected_topic:
        st.markdown(f"#### News related to: **{selected_topic}**")
        
        all_news = NewsProvider.get_latest_news(days=7)
        topic_news = [
            article for article in all_news
            if selected_topic.lower() in article['description'].lower() or 
               selected_topic.lower() in article['title'].lower()
        ]
        
        if topic_news:
            for idx, article in enumerate(topic_news, 1):
                render_news_card(article, idx, theme_colors)
        else:
            st.info(f"No recent news found for topic: {selected_topic}")