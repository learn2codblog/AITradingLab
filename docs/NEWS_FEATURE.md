# 📰 News Feature - Live News Integration

## Overview

The News feature has been upgraded to fetch **real-time, live news** from multiple sources instead of displaying hardcoded sample data.

## News Sources

The app now fetches news from:

### 1. **RSS Feeds** (Free, No API Key Required)
- Bloomberg Markets
- CNBC Markets & Politics
- Financial Times
- NASDAQ Markets
- Reuters Politics News

### 2. **Yahoo Finance** (Free, No API Key Required)
- Market indices news (S&P 500, Dow Jones, NASDAQ)
- Real-time financial news
- Company-specific news

### 3. **NewsAPI** (Optional, Requires Free API Key)
- 70+ news sources worldwide
- Business and general news categories
- Top headlines and breaking news

## Features

### ✅ **Live News Fetching**
- Fetches latest news every 10 minutes (cached for performance)
- Automatically filters by date range (1-30 days)
- Category filtering (Finance, Politics, All)
- Duplicate removal based on title similarity

### ✅ **Multiple Tabs**
1. **📈 Market News** - General financial market news
2. **📰 Company News** - Company-specific news with sentiment analysis
3. **📊 Sentiment Analysis** - AI-powered sentiment scoring
4. **🔍 News Search** - Search through fetched articles
5. **🔥 Trending Topics** - Most discussed topics

### ✅ **Automatic Fallback**
If live news fetching fails (network issues, API limits):
- Automatically falls back to sample news data
- Shows informational message to user
- App continues to function normally

## Setup (Optional Enhancement)

### Get NewsAPI Key (Free)

1. Visit https://newsapi.org/
2. Sign up for a free account
3. Get your API key (70,000 requests/month on free tier)
4. Add to your `.env` file:

```env
NEWSAPI_KEY=your-api-key-here
```

### Without NewsAPI Key

The app works perfectly fine without NewsAPI! It will:
- Fetch news from RSS feeds (Bloomberg, CNBC, Reuters, etc.)
- Fetch news from Yahoo Finance
- Display live, up-to-date news articles
- Show 15-20 articles from multiple sources

## How It Works

### News Fetching Priority

```
1. Try NewsAPI (if key configured) → Get 20 articles
2. Try RSS Feeds (always) → Get 15-20 articles  
3. Try Yahoo Finance (always) → Get 10-15 articles
4. Merge all sources → Remove duplicates → Sort by date
5. If all fail → Use sample fallback data
```

### Caching Strategy

- News is cached for **10 minutes** (@st.cache_data with ttl=600)
- Reduces API calls and improves performance
- Fresh news every 10 minutes automatically

### Article Structure

Each article contains:
```python
{
    'title': str,           # Article headline
    'description': str,     # Brief summary
    'category': str,        # Finance or Politics
    'source': str,          # News source name
    'timestamp': datetime,  # Publication time
    'url': str,            # Link to full article
    'content': str         # Full article text (if available)
}
```

## User Experience

### What Users See

1. **Real-time News**: Articles from today and recent days
2. **Source Attribution**: Each article shows its source
3. **Time Indicators**: "2 hours ago", "1 day ago", etc.
4. **Click to Read**: Links to full articles on original websites
5. **Category Filtering**: Filter by Finance or Politics
6. **Date Range**: Adjust how many days back to show news

### Performance

- **First Load**: ~5 seconds (fetching from all sources)
- **Subsequent Loads**: Instant (cached for 10 minutes)
- **No Blocking**: News fetches asynchronously
- **Fallback**: Always works even if sources are down

## Testing

Verified live news fetching:
```
✅ Fetched 20 articles
✅ 19 articles from today
✅ Real news from Bloomberg, CNBC, Reuters
✅ Articles about current events (verified March 14, 2026)
```

## Troubleshooting

### No News Displayed
- **Check internet connection**
- **RSS feeds may be temporarily down**
- **App will show sample data as fallback**

### Old News Showing
- **Clear Streamlit cache** (press 'C' in the app)
- **Wait 10 minutes** for cache to expire
- **Refresh the page**

### Want More News Sources
- **Add NEWSAPI_KEY** to .env file
- **Increases articles from 20 to 40+**
- **Free tier: 70,000 requests/month**

## Code Changes

### Modified Files
1. `src/news_provider.py` - Added live news fetching logic
2. `requirements.txt` - Added `feedparser>=6.0.10`
3. `.env.example` - Added NEWSAPI_KEY configuration

### New Functions
- `_fetch_from_newsapi()` - Fetch from NewsAPI
- `_fetch_from_rss_feeds()` - Fetch from RSS feeds
- `_fetch_from_yahoo_finance()` - Fetch from Yahoo Finance
- `_remove_duplicate_news()` - Remove duplicate articles

## Activity Logging

The app logs when users fetch company-specific news:
```python
supabase.log_activity(
    user_id=user_id,
    activity_type='news_company_fetch',
    description=f"Company news fetch for {symbol}",
    action_details={'symbol': symbol},
    status='success'
)
```

## Future Enhancements

Potential improvements:
- [ ] Add more RSS feed sources
- [ ] Implement full-text article extraction
- [ ] Add news alerts for specific keywords
- [ ] Email digest of top news
- [ ] Custom news feeds per user
- [ ] News sentiment trends over time

## Summary

✅ **Live news fetching implemented**  
✅ **Multiple reliable sources (RSS, Yahoo Finance, NewsAPI)**  
✅ **Works without API keys**  
✅ **Automatic fallback for reliability**  
✅ **Cached for performance**  
✅ **Tested and verified working**  

Users now see **real, up-to-date financial news** instead of hardcoded sample articles!

