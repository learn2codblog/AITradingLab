"""
News Module for AITradingLab
Fetches and displays general finance, politics, and important announcements
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import json
import os
from dotenv import load_dotenv
import feedparser

load_dotenv()

# Optional external fetch/parsing
try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    requests = None
    BeautifulSoup = None

try:
    import yfinance as yf
except ImportError:
    yf = None


class NewsProvider:
    """Handle news fetching and caching"""
    
    # NewsAPI key (optional - get free key from https://newsapi.org/)
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '')

    # RSS Feed URLs for financial news
    RSS_FEEDS = {
        'Finance': [
            'https://feeds.bloomberg.com/markets/news.rss',
            'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'https://www.ft.com/?format=rss',
            'https://www.nasdaq.com/feed/rssoutbound?category=Markets',
        ],
        'Politics': [
            'https://feeds.reuters.com/reuters/politicsNews',
            'https://www.cnbc.com/id/10000113/device/rss/rss.html',
        ]
    }

    @staticmethod
    def _now_utc():
        """Get current UTC time with timezone awareness"""
        return datetime.now(timezone.utc)

    @staticmethod
    def _normalize_timestamp(dt):
        """Normalize datetime to timezone-aware UTC (defensive programming)"""
        if dt is None:
            return datetime.now(timezone.utc)
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            # Naive datetime - assume UTC
            return dt.replace(tzinfo=timezone.utc)
        return dt

    # Fallback sample news data (used when all APIs fail)
    @classmethod
    def _get_sample_news(cls):
        """Generate sample news with current timestamps"""
        now = cls._now_utc()
        return [
        {
            "title": "Federal Reserve Signals Pause in Rate Hikes",
            "description": "The Fed maintains interest rates amid economic uncertainty",
            "category": "Finance",
            "source": "Reuters",
            "timestamp": now - timedelta(hours=2),
            "url": "#"
        },
        {
            "title": "S&P 500 Reaches New All-Time High",
            "description": "Tech stocks lead market rally on AI optimism",
            "category": "Finance",
            "source": "Bloomberg",
            "timestamp": now - timedelta(hours=5),
            "url": "#"
        },
        {
            "title": "Government Announces New Economic Reform Package",
            "description": "Administration proposes comprehensive economic stimulus measures",
            "category": "Politics",
            "source": "CNBC",
            "timestamp": now - timedelta(hours=8),
            "url": "#"
        },
        {
            "title": "Central Bank Cuts Key Policy Rate by 25 Basis Points",
            "description": "Monetary policy adjusted to support economic growth",
            "category": "Finance",
            "source": "Trading View",
            "timestamp": now - timedelta(hours=12),
            "url": "#"
        },
        {
            "title": "Major Trade Agreement Signed Between Nations",
            "description": "New tariff reduction agreement expected to boost markets",
            "category": "Politics",
            "source": "Reuters",
            "timestamp": now - timedelta(hours=18),
            "url": "#"
        },
        {
            "title": "Tech Sector Records Strongest Growth in 5 Years",
            "description": "AI and software companies drive market expansion",
            "category": "Finance",
            "source": "Financial Times",
            "timestamp": now - timedelta(hours=24),
            "url": "#"
        },
        {
            "title": "Oil Prices Surge on OPEC Production Cuts",
            "description": "Energy markets respond to supply-side pressures",
            "category": "Finance",
            "source": "Bloomberg",
            "timestamp": now - timedelta(hours=30),
            "url": "#"
        },
        {
            "title": "Congress Approves $50 Billion Inflation Relief Bill",
            "description": "Lawmakers pass measure to address rising consumer costs",
            "category": "Politics",
            "source": "AP News",
            "timestamp": now - timedelta(hours=36),
            "url": "#"
        },
        {
            "title": "Cryptocurrency Market Rebounds After Regulation News",
            "description": "Digital assets gain as regulatory clarity increases",
            "category": "Finance",
            "source": "CoinDesk",
            "timestamp": now - timedelta(hours=42),
            "url": "#"
        },
        {
            "title": "World Bank Upgrades Global Growth Forecast",
            "description": "International organization raises economic projections",
            "category": "Finance",
            "source": "Reuters",
            "timestamp": now - timedelta(hours=48),
            "url": "#"
        }
    ]
    
    @classmethod
    @st.cache_data(ttl=600)  # Cache for 10 minutes
    def get_latest_news(cls, days: int = 7, category: str = "All") -> List[Dict]:
        """
        Get latest financial and political news from live sources

        Args:
            days: Number of days to look back
            category: News category filter (All, Finance, Politics)
        
        Returns:
            List of news articles
        """
        all_news = []

        # Try to fetch from multiple sources
        try:
            # Source 1: NewsAPI (if key available)
            if cls.NEWSAPI_KEY:
                newsapi_articles = cls._fetch_from_newsapi(days, category)
                all_news.extend(newsapi_articles)

            # Source 2: RSS Feeds
            rss_articles = cls._fetch_from_rss_feeds(days, category)
            all_news.extend(rss_articles)

            # Source 3: Yahoo Finance (using yfinance)
            if yf:
                yf_articles = cls._fetch_from_yahoo_finance(days)
                all_news.extend(yf_articles)

        except Exception as e:
            st.warning(f"Error fetching live news: {str(e)}")

        # If no news fetched, use sample data as fallback
        if not all_news:
            st.info("📰 Using sample news data. Configure NEWSAPI_KEY in .env for live news.")
            all_news = cls._get_sample_news()

        # Normalize all timestamps to be timezone-aware (defensive programming)
        for article in all_news:
            if 'timestamp' in article:
                article['timestamp'] = cls._normalize_timestamp(article['timestamp'])

        # Sort by timestamp descending (latest first)
        all_news = sorted(all_news, key=lambda x: cls._normalize_timestamp(x.get('timestamp')), reverse=True)

        # Filter by category if not "All"
        if category != "All":
            all_news = [n for n in all_news if n.get('category', 'Finance') == category]

        # Filter by date range
        cutoff_date = cls._now_utc() - timedelta(days=days)
        all_news = [n for n in all_news if cls._normalize_timestamp(n.get('timestamp')) >= cutoff_date]

        # Remove duplicates based on title similarity
        all_news = cls._remove_duplicate_news(all_news)

        return all_news

    @classmethod
    def _fetch_from_newsapi(cls, days: int, category: str) -> List[Dict]:
        """Fetch news from NewsAPI.org"""
        if not requests or not cls.NEWSAPI_KEY:
            return []

        try:
            # Map our categories to NewsAPI categories
            newsapi_category = 'business' if category in ['All', 'Finance'] else 'general'

            url = f'https://newsapi.org/v2/top-headlines'
            params = {
                'apiKey': cls.NEWSAPI_KEY,
                'category': newsapi_category,
                'language': 'en',
                'pageSize': 20
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            articles = []
            for article in data.get('articles', []):
                if article.get('title') and article.get('title') != '[Removed]':
                    pub_date = article.get('publishedAt', '')
                    try:
                        timestamp = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    except:
                        timestamp = cls._now_utc()

                    articles.append({
                        'title': article.get('title', 'No Title'),
                        'description': article.get('description', 'No description available'),
                        'category': 'Finance' if newsapi_category == 'business' else 'Politics',
                        'source': article.get('source', {}).get('name', 'NewsAPI'),
                        'timestamp': timestamp,
                        'url': article.get('url', '#'),
                        'content': article.get('content', '')
                    })

            return articles
        except Exception as e:
            print(f"NewsAPI fetch error: {str(e)}")
            return []

    @classmethod
    def _fetch_from_rss_feeds(cls, days: int, category: str) -> List[Dict]:
        """Fetch news from RSS feeds"""
        articles = []

        try:
            feeds_to_fetch = []
            if category == "All":
                feeds_to_fetch = cls.RSS_FEEDS['Finance'][:2] + cls.RSS_FEEDS['Politics'][:1]
            elif category == "Finance":
                feeds_to_fetch = cls.RSS_FEEDS['Finance'][:2]
            elif category == "Politics":
                feeds_to_fetch = cls.RSS_FEEDS['Politics'][:1]

            for feed_url in feeds_to_fetch:
                try:
                    feed = feedparser.parse(feed_url)
                    feed_category = 'Finance' if feed_url in cls.RSS_FEEDS['Finance'] else 'Politics'

                    for entry in feed.entries[:10]:  # Limit per feed
                        try:
                            # Parse published date
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                timestamp = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                            else:
                                timestamp = cls._now_utc()

                            # Skip old articles
                            if (cls._now_utc() - timestamp).days > days:
                                continue

                            articles.append({
                                'title': entry.get('title', 'No Title')[:200],
                                'description': entry.get('summary', 'No description')[:500],
                                'category': feed_category,
                                'source': feed.feed.get('title', 'RSS Feed'),
                                'timestamp': timestamp,
                                'url': entry.get('link', '#'),
                                'content': entry.get('description', '')
                            })
                        except Exception:
                            continue
                except Exception:
                    continue

        except Exception as e:
            print(f"RSS fetch error: {str(e)}")

        return articles

    @classmethod
    def _fetch_from_yahoo_finance(cls, days: int) -> List[Dict]:
        """Fetch financial news from Yahoo Finance"""
        if not yf:
            return []

        articles = []
        try:
            # Fetch news for major indices
            symbols = ['^GSPC', '^DJI', '^IXIC']  # S&P 500, Dow Jones, NASDAQ

            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    news_items = ticker.news

                    if news_items:
                        for item in news_items[:5]:  # Limit per symbol
                            try:
                                timestamp = datetime.fromtimestamp(item.get('providerPublishTime', 0), tz=timezone.utc)

                                # Skip old articles
                                if (cls._now_utc() - timestamp).days > days:
                                    continue

                                articles.append({
                                    'title': item.get('title', 'No Title')[:200],
                                    'description': item.get('summary', 'No description')[:500],
                                    'category': 'Finance',
                                    'source': item.get('publisher', 'Yahoo Finance'),
                                    'timestamp': timestamp,
                                    'url': item.get('link', '#'),
                                    'content': item.get('summary', '')
                                })
                            except Exception:
                                continue
                except Exception:
                    continue

        except Exception as e:
            print(f"Yahoo Finance fetch error: {str(e)}")

        return articles

    @classmethod
    def _remove_duplicate_news(cls, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        seen_titles = set()
        unique_articles = []

        for article in articles:
            # Normalize title for comparison
            title_key = article.get('title', '').lower().strip()[:50]

            if title_key and title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_articles.append(article)

        return unique_articles

    @classmethod
    @classmethod
    def get_news_by_category(cls) -> Dict[str, List[Dict]]:
        """Get news organized by category"""
        news_by_cat = {
            "Finance": [],
            "Politics": [],
            "Announcements": []
        }
        
        for article in cls._get_sample_news():
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
        
        # Initialize selected index and prefetch cache in session state
        if 'selected_news_index' not in st.session_state:
            st.session_state.selected_news_index = None
        if 'news_full_texts' not in st.session_state:
            st.session_state.news_full_texts = {}

        # Get news
        news = NewsProvider.get_latest_news(days=days, category=category)

        # Prefetch top-N full articles (configurable via env var NEWS_PREFETCH_TOP_N)
        try:
            import os as _os
            prefetch_n = int(_os.getenv('NEWS_PREFETCH_TOP_N', '3'))
        except Exception:
            prefetch_n = 3

        # Only attempt prefetch if requests+bs4 are available
        if prefetch_n > 0 and requests and BeautifulSoup and news:
            with st.spinner(f"Prefetching top {prefetch_n} articles..."):
                for idx, article in enumerate(news[:prefetch_n], 1):
                    if idx in st.session_state.news_full_texts:
                        continue
                    url = article.get('url')
                    try:
                        if url and url != '#':
                            st.session_state.news_full_texts[idx] = NewsDisplay._fetch_article_text(url)
                        else:
                            st.session_state.news_full_texts[idx] = article.get('content') or article.get('description') or ''
                    except Exception:
                        st.session_state.news_full_texts[idx] = article.get('content') or article.get('description') or ''
        
        if sort_order == "Oldest First":
            news = list(reversed(news))
        
        # Display news count
        st.info(f"📊 Showing {len(news)} articles")
        
        if not news:
            st.warning("No news found for selected filters")
            return
        
        # Display news articles. Use index starting at 1 for display consistency.
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
        
        # Format timestamp - normalize to ensure timezone awareness
        article_time = NewsProvider._normalize_timestamp(article.get('timestamp'))

        time_diff = datetime.now(timezone.utc) - article_time
        if time_diff.total_seconds() < 3600:
            time_str = f"{int(time_diff.total_seconds() // 60)} minutes ago"
        elif time_diff.total_seconds() < 86400:
            time_str = f"{int(time_diff.total_seconds() // 3600)} hours ago"
        else:
            time_str = f"{time_diff.days} days ago"
        
        # Use an expander so clicking the headline reveals the full article for any user
        with st.container():
            col1, col2 = st.columns([0.06, 0.94])

            with col1:
                st.markdown(f"## {color_emoji}")

            # Determine if this article should be expanded by default (sidebar click)
            selected_idx = st.session_state.get('selected_news_index')
            expand_default = (selected_idx == index)

            with col2:
                with st.expander(f"{article['title']}", expanded=expand_default):
                    # Prefer a prefetched copy if available for instant display
                    prefetched = st.session_state.get('news_full_texts', {}).get(index)
                    url = article.get('url')
                    if prefetched:
                        st.write(prefetched)
                    else:
                        # If a URL exists and we can fetch, try to fetch full article text
                        full_text = ''
                        if url and url != '#' and requests and BeautifulSoup:
                            try:
                                full_text = NewsDisplay._fetch_article_text(url)
                            except Exception:
                                full_text = article.get('content') or article.get('description') or ''
                        else:
                            full_text = article.get('content') or article.get('description') or ''

                        if full_text:
                            st.write(full_text)
                        else:
                            st.write("No full text available. Click the link to read the original article.")

                    # If there's an external URL, show a link button
                    if url and url != '#':
                        st.markdown(f"[Read original article]({url})")

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
                    1 for article in NewsProvider._get_sample_news()
                    if topic.lower() in article['description'].lower() or
                    topic.lower() in article['title'].lower()
                )
                
                st.metric("Related Articles", related_count)

    @staticmethod
    @st.cache_data(ttl=3600)
    def _fetch_article_text(url: str) -> str:
        """Fetch article full text from URL using requests + BeautifulSoup when available.

        Returns a best-effort plain-text extraction (joins paragraph tags).
        If requests/bs4 are not available or extraction fails, raises Exception.
        """
        if not requests or not BeautifulSoup:
            raise RuntimeError("requests or BeautifulSoup not available")

        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Simple extraction: join readable <p> text
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
        if not paragraphs:
            # Fallback: return the raw body text
            body = soup.body.get_text(separator=' ', strip=True) if soup.body else resp.text
            return body
        return '\n\n'.join(paragraphs)
    
    @staticmethod
    def render_news_sidebar():
        """Render compact news widget for sidebar/header"""
        with st.expander("📰 Market News", expanded=False):
            news = NewsProvider.get_latest_news(days=1)[:5]

            # Show clickable titles that set the selected index so the main feed can expand it
            for idx, article in enumerate(news, 1):
                if st.button(article['title'], key=f"news_sidebar_{idx}"):
                    st.session_state.selected_news_index = idx
                    try:
                        st.experimental_rerun()
                    except Exception:
                        pass
                st.caption(f"{article['source']}")
                st.markdown("---")


# Quick access functions
def load_news_feed():
    """Load and display news feed"""
    NewsDisplay.render_news_dashboard()


def get_latest_headlines(limit: int = 5) -> List[Dict]:
    """Get latest headlines for display in other parts of app"""
    return NewsProvider.get_latest_news()[:limit]
