"""
News Module for AITradingLab
Fetches and displays general finance, politics, and important announcements
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json


class NewsProvider:
    """Handle news fetching and caching"""
    
    # Sample news data - In production, integrate with real API like NewsAPI
    SAMPLE_NEWS_DATA = [
        {
            "title": "Federal Reserve Signals Pause in Rate Hikes",
            "description": "The Fed maintains interest rates amid economic uncertainty",
            "category": "Finance",
            "source": "Reuters",
            "timestamp": datetime.now() - timedelta(hours=2),
            "url": "#"
        },
        {
            "title": "S&P 500 Reaches New All-Time High",
            "description": "Tech stocks lead market rally on AI optimism",
            "category": "Finance",
            "source": "Bloomberg",
            "timestamp": datetime.now() - timedelta(hours=5),
            "url": "#"
        },
        {
            "title": "Government Announces New Economic Reform Package",
            "description": "Administration proposes comprehensive economic stimulus measures",
            "category": "Politics",
            "source": "CNBC",
            "timestamp": datetime.now() - timedelta(hours=8),
            "url": "#"
        },
        {
            "title": "Central Bank Cuts Key Policy Rate by 25 Basis Points",
            "description": "Monetary policy adjusted to support economic growth",
            "category": "Finance",
            "source": "Trading View",
            "timestamp": datetime.now() - timedelta(hours=12),
            "url": "#"
        },
        {
            "title": "Major Trade Agreement Signed Between Nations",
            "description": "New tariff reduction agreement expected to boost markets",
            "category": "Politics",
            "source": "Reuters",
            "timestamp": datetime.now() - timedelta(hours=18),
            "url": "#"
        },
        {
            "title": "Tech Sector Records Strongest Growth in 5 Years",
            "description": "AI and software companies drive market expansion",
            "category": "Finance",
            "source": "Financial Times",
            "timestamp": datetime.now() - timedelta(hours=24),
            "url": "#"
        },
        {
            "title": "Oil Prices Surge on OPEC Production Cuts",
            "description": "Energy markets respond to supply-side pressures",
            "category": "Finance",
            "source": "Bloomberg",
            "timestamp": datetime.now() - timedelta(hours=30),
            "url": "#"
        },
        {
            "title": "Congress Approves $50 Billion Inflation Relief Bill",
            "description": "Lawmakers pass measure to address rising consumer costs",
            "category": "Politics",
            "source": "AP News",
            "timestamp": datetime.now() - timedelta(hours=36),
            "url": "#"
        },
        {
            "title": "Cryptocurrency Market Rebounds After Regulation News",
            "description": "Digital assets gain as regulatory clarity increases",
            "category": "Finance",
            "source": "CoinDesk",
            "timestamp": datetime.now() - timedelta(hours=42),
            "url": "#"
        },
        {
            "title": "World Bank Upgrades Global Growth Forecast",
            "description": "International organization raises economic projections",
            "category": "Finance",
            "source": "Reuters",
            "timestamp": datetime.now() - timedelta(hours=48),
            "url": "#"
        }
    ]
    
    @classmethod
    def get_latest_news(cls, days: int = 7, category: str = "All") -> List[Dict]:
        """
        Get latest financial and political news
        
        Args:
            days: Number of days to look back
            category: News category filter (All, Finance, Politics)
        
        Returns:
            List of news articles
        """
        # Sort by timestamp descending (latest first)
        news = sorted(cls.SAMPLE_NEWS_DATA, key=lambda x: x['timestamp'], reverse=True)
        
        # Filter by category
        if category != "All":
            news = [n for n in news if n['category'] == category]
        
        return news
    
    @classmethod
    def get_news_by_category(cls) -> Dict[str, List[Dict]]:
        """Get news organized by category"""
        news_by_cat = {
            "Finance": [],
            "Politics": [],
            "Announcements": []
        }
        
        for article in cls.SAMPLE_NEWS_DATA:
            category = article.get('category', 'Announcements')
            if category in news_by_cat:
                news_by_cat[category].append(article)
        
        return news_by_cat
    
    @classmethod
    def get_trending_topics(cls) -> List[str]:
        """Get trending news topics"""
        return [
            "Fed Policy Decisions",
            "Market Volatility",
            "AI Revolution",
            "Trade Negotiations",
            "Economic Growth",
            "Inflation Control"
        ]


class NewsDisplay:
    """Handle news display and formatting"""
    
    @staticmethod
    def render_news_feed():
        """Render complete news feed page"""
        st.markdown("# 📰 Financial News & Announcements")
        
        st.markdown("""
        Stay updated with the latest financial news, political developments, 
        and market announcements that could impact your trading decisions.
        """)
        
        st.markdown("---")
        
        # Filter options
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            category = st.selectbox(
                "📁 Category",
                ["All", "Finance", "Politics"],
                help="Filter news by category"
            )
        
        with col2:
            days = st.slider(
                "📅 Days Back",
                1, 30, 7,
                help="Show news from last N days"
            )
        
        with col3:
            sort_order = st.selectbox(
                "⏱️ Sort By",
                ["Latest First", "Oldest First"],
                help="Sort order"
            )
        
        st.markdown("---")
        
        # Get news
        news = NewsProvider.get_latest_news(days=days, category=category)
        
        if sort_order == "Oldest First":
            news = list(reversed(news))
        
        # Display news count
        st.info(f"📊 Showing {len(news)} articles")
        
        if not news:
            st.warning("No news found for selected filters")
            return
        
        # Display news articles
        for idx, article in enumerate(news, 1):
            NewsDisplay._render_news_card(article, idx)
    
    @staticmethod
    def _render_news_card(article: Dict, index: int):
        """Render individual news card"""
        # Determine color by category
        category_color = {
            "Finance": "🟢",
            "Politics": "🔵",
            "Announcements": "🟡"
        }
        
        color_emoji = category_color.get(article['category'], "⚪")
        
        # Format timestamp
        time_diff = datetime.now() - article['timestamp']
        if time_diff.seconds < 3600:
            time_str = f"{time_diff.seconds // 60} minutes ago"
        elif time_diff.seconds < 86400:
            time_str = f"{time_diff.seconds // 3600} hours ago"
        else:
            time_str = f"{time_diff.days} days ago"
        
        with st.container():
            col1, col2 = st.columns([0.1, 0.9])
            
            with col1:
                st.markdown(f"## {color_emoji}")
            
            with col2:
                st.markdown(f"### {article['title']}")
                st.markdown(article['description'])
                
                # Footer with metadata
                col_meta1, col_meta2, col_meta3, col_meta4 = st.columns([2, 2, 2, 2])
                
                with col_meta1:
                    st.caption(f"📰 {article['source']}")
                
                with col_meta2:
                    st.caption(f"🏷️ {article['category']}")
                
                with col_meta3:
                    st.caption(f"⏰ {time_str}")
                
                with col_meta4:
                    st.caption(f"#{index}")
            
            st.markdown("---")
    
    @staticmethod
    def render_news_dashboard():
        """Render comprehensive news dashboard"""
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["All News", "By Category", "Trending"])
        
        with tab1:
            NewsDisplay.render_news_feed()
        
        with tab2:
            NewsDisplay._render_by_category()
        
        with tab3:
            NewsDisplay._render_trending()
    
    @staticmethod
    def _render_by_category():
        """Render news organized by category"""
        st.markdown("## 📂 News by Category")
        
        news_by_cat = NewsProvider.get_news_by_category()
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("🟢 Finance News", expanded=True):
                for article in news_by_cat['Finance'][:5]:
                    st.markdown(f"**{article['title']}**")
                    st.caption(f"{article['source']} • {article['category']}")
                    st.markdown("---")
        
        with col2:
            with st.expander("🔵 Politics & Announcements", expanded=True):
                all_political = news_by_cat['Politics'] + news_by_cat.get('Announcements', [])
                for article in all_political[:5]:
                    st.markdown(f"**{article['title']}**")
                    st.caption(f"{article['source']} • {article['category']}")
                    st.markdown("---")
    
    @staticmethod
    def _render_trending():
        """Render trending topics"""
        st.markdown("## 🔥 Trending Topics")
        
        trending = NewsProvider.get_trending_topics()
        
        cols = st.columns(3)
        
        for idx, topic in enumerate(trending):
            with cols[idx % 3]:
                st.markdown(f"""
                ### #{idx + 1}
                **{topic}**
                """)
                
                # Show related news count
                related_count = sum(
                    1 for article in NewsProvider.SAMPLE_NEWS_DATA
                    if topic.lower() in article['description'].lower() or 
                    topic.lower() in article['title'].lower()
                )
                
                st.metric("Related Articles", related_count)
    
    @staticmethod
    def render_news_sidebar():
        """Render compact news widget for sidebar/header"""
        with st.expander("📰 Market News", expanded=False):
            news = NewsProvider.get_latest_news(days=1)[:3]
            
            for article in news:
                st.markdown(f"**{article['title']}**")
                st.caption(f"{article['source']}")
                st.markdown("---")


# Quick access functions
def load_news_feed():
    """Load and display news feed"""
    NewsDisplay.render_news_dashboard()


def get_latest_headlines(limit: int = 5) -> List[Dict]:
    """Get latest headlines for display in other parts of app"""
    return NewsProvider.get_latest_news()[:limit]
