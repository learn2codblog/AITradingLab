# fundamental_analysis.py
"""
Fundamental Analysis Module
Handles company fundamentals, financial metrics, and qualitative indicators
"""

import yfinance as yf
import pandas as pd
import numpy as np


def get_fundamentals(ticker: str) -> dict:
    """
    Retrieve fundamental financial metrics for a company
    
    Metrics:
    - ROE (Return on Equity): Profitability relative to shareholder equity
    - PE (Price-to-Earnings): Valuation metric
    - Profit Margin: Net profit as percentage of revenue
    - Revenue Growth: YoY revenue growth rate
    - Market Cap: Total market capitalization
    - Sector: Industry sector classification
    - Beta: Volatility relative to market
    - EPS Growth: Earnings per share growth rate
    
    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS')
    
    Returns:
        Dictionary with fundamental metrics or empty dict if data unavailable
    """
    try:
        info = yf.Ticker(ticker).info
        return {
            "ROE": info.get("returnOnEquity", np.nan),
            "PE": info.get("trailingPE", np.nan),
            "ProfitMargin": info.get("profitMargins", np.nan),
            "RevenueGrowth": info.get("revenueGrowth", np.nan),
            "MarketCap": info.get("marketCap", np.nan),
            "Sector": info.get("sector", "Unknown"),
            "Beta": info.get("beta", np.nan),
            "EPSGrowth": info.get("earningsGrowth", np.nan),
            "DividendYield": info.get("dividendYield", np.nan),
            "DebtToEquity": info.get("debtToEquity", np.nan),
            "CurrentRatio": info.get("currentRatio", np.nan),
            "QuickRatio": info.get("quickRatio", np.nan),
        }
    except Exception as e:
        print(f"Error fetching fundamentals for {ticker}: {e}")
        return {}


def get_news_sentiment(ticker: str, num_news: int = 20) -> float:
    """
    Calculate sentiment score from recent news articles
    
    Sentiment Analysis:
    - Uses simple keyword-based heuristic
    - Counts positive vs negative keywords in article titles
    - Returns average sentiment score across articles
    
    Args:
        ticker: Stock ticker symbol
        num_news: Number of recent articles to analyze (default: 20)
    
    Returns:
        Float sentiment score (typically -1.0 to 1.0)
    """
    try:
        news = yf.Ticker(ticker).news[:num_news]
        if not news:
            return 0.0
        
        sentiments = []
        pos_words = ['up', 'gain', 'positive', 'growth', 'bull', 'surge', 'strong']
        neg_words = ['down', 'loss', 'negative', 'decline', 'bear', 'fall', 'weak']
        
        for article in news:
            title = article.get('title', '').lower()
            score = (sum(1 for w in pos_words if w in title) - 
                    sum(1 for w in neg_words if w in title))
            sentiments.append(score)
        
        return np.mean(sentiments) if sentiments else 0.0
    
    except Exception as e:
        print(f"Error fetching sentiment for {ticker}: {e}")
        return 0.0


def get_analyst_ratings(ticker: str) -> dict:
    """
    Get analyst consensus ratings and target price
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dictionary with analyst data
    """
    try:
        info = yf.Ticker(ticker).info
        return {
            "TargetPrice": info.get("targetMeanPrice", np.nan),
            "NumberOfAnalysts": info.get("numberOfAnalystOpinions", np.nan),
            "RecommendationKey": info.get("recommendationKey", "none"),
            "RecommendationRating": info.get("recommendationRating", np.nan),
        }
    except Exception as e:
        print(f"Error fetching analyst ratings for {ticker}: {e}")
        return {}


def get_quality_metrics(ticker: str) -> dict:
    """
    Retrieve quality/health metrics for financial analysis
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dictionary with quality metrics
    """
    try:
        info = yf.Ticker(ticker).info
        return {
            "ROA": info.get("returnOnAssets", np.nan),
            "OperatingMargin": info.get("operatingMargins", np.nan),
            "PayoutRatio": info.get("payoutRatio", np.nan),
            "DebtRatio": info.get("totalDebt", np.nan) / info.get("totalAssets", 1) if info.get("totalAssets") else np.nan,
            "AssetTurnover": info.get("assetTurnover", np.nan),
        }
    except Exception as e:
        print(f"Error fetching quality metrics for {ticker}: {e}")
        return {}
