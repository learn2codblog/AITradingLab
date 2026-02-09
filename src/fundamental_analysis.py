"""
Fundamental Analysis Module for TradeGenius AI
"""

import yfinance as yf
import pandas as pd
import numpy as np


def get_fundamentals(symbol: str) -> dict:
    """
    Get fundamental data for a stock

    Args:
        symbol: Stock symbol (e.g., 'RELIANCE.NS')

    Returns:
        Dict with fundamental metrics
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Get ROE - try multiple sources and calculate if not available
        roe_value = info.get('returnOnEquity')
        if roe_value is None or roe_value == 0:
            # Try to calculate ROE from net income and equity
            net_income = info.get('netIncomeToCommon', 0) or 0
            total_equity = info.get('totalStockholderEquity', 0) or info.get('bookValue', 0) * info.get('sharesOutstanding', 1)
            if total_equity and total_equity > 0 and net_income:
                roe_value = net_income / total_equity
            else:
                roe_value = 0

        # Get ROA - try multiple sources
        roa_value = info.get('returnOnAssets')
        if roa_value is None or roa_value == 0:
            net_income = info.get('netIncomeToCommon', 0) or 0
            total_assets = info.get('totalAssets', 0) or 0
            if total_assets > 0 and net_income:
                roa_value = net_income / total_assets
            else:
                roa_value = 0

        fundamentals = {
            'MarketCap': info.get('marketCap', 0),
            'PE': info.get('trailingPE', info.get('forwardPE', 0)) or 0,
            'PB': info.get('priceToBook', 0) or 0,
            'EPS': info.get('trailingEps', 0) or 0,
            'ROE': roe_value if roe_value else 0,
            'ROE_Percent': (roe_value * 100) if roe_value else 0,  # ROE as percentage for display
            'ROA': roa_value if roa_value else 0,
            'ROA_Percent': (roa_value * 100) if roa_value else 0,  # ROA as percentage for display
            'ProfitMargin': info.get('profitMargins', 0) or 0,
            'OperatingMargin': info.get('operatingMargins', 0) or 0,
            'GrossMargin': info.get('grossMargins', 0) or 0,
            'RevenueGrowth': info.get('revenueGrowth', 0) or 0,
            'EarningsGrowth': info.get('earningsGrowth', 0) or 0,
            'EPSGrowth': info.get('earningsQuarterlyGrowth', 0) or 0,
            'DebtToEquity': info.get('debtToEquity', 0) or 0,
            'CurrentRatio': info.get('currentRatio', 0) or 0,
            'QuickRatio': info.get('quickRatio', 0) or 0,
            'Beta': info.get('beta', 1) or 1,
            'DividendYield': info.get('dividendYield', 0) or 0,
            'PayoutRatio': info.get('payoutRatio', 0) or 0,
            'BookValue': info.get('bookValue', 0) or 0,
            'FreeCashFlow': info.get('freeCashflow', 0) or 0,
            'OperatingCashFlow': info.get('operatingCashflow', 0) or 0,
            'Revenue': info.get('totalRevenue', 0) or 0,
            'NetIncome': info.get('netIncomeToCommon', 0) or 0,
            'TotalDebt': info.get('totalDebt', 0) or 0,
            'TotalCash': info.get('totalCash', 0) or 0,
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'FullTimeEmployees': info.get('fullTimeEmployees', 0),
            'SharesOutstanding': info.get('sharesOutstanding', 0),
            'FloatShares': info.get('floatShares', 0),
            '52WeekHigh': info.get('fiftyTwoWeekHigh', 0) or 0,
            '52WeekLow': info.get('fiftyTwoWeekLow', 0) or 0,
            '50DayMA': info.get('fiftyDayAverage', 0) or 0,
            '200DayMA': info.get('twoHundredDayAverage', 0) or 0,
        }

        return fundamentals

    except Exception as e:
        print(f"Error getting fundamentals for {symbol}: {e}")
        return {
            'MarketCap': 0,
            'PE': 0,
            'PB': 0,
            'EPS': 0,
            'ROE': 0,
            'ROA': 0,
            'ProfitMargin': 0,
            'RevenueGrowth': 0,
            'Beta': 1,
            'DividendYield': 0
        }


def get_news_sentiment(symbol: str) -> float:
    """
    Get news sentiment score for a stock
    Simple implementation - returns neutral by default

    Args:
        symbol: Stock symbol

    Returns:
        Sentiment score (-1 to 1)
    """
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news

        if not news:
            return 0.0

        # Simple keyword-based sentiment
        positive_words = ['buy', 'upgrade', 'bullish', 'growth', 'profit', 'surge', 'rally', 'strong']
        negative_words = ['sell', 'downgrade', 'bearish', 'loss', 'decline', 'crash', 'weak', 'fall']

        sentiment_scores = []

        for article in news[:10]:  # Analyze top 10 news
            title = article.get('title', '').lower()

            pos_count = sum(1 for word in positive_words if word in title)
            neg_count = sum(1 for word in negative_words if word in title)

            if pos_count + neg_count > 0:
                score = (pos_count - neg_count) / (pos_count + neg_count)
                sentiment_scores.append(score)

        if sentiment_scores:
            return np.mean(sentiment_scores)

        return 0.0

    except Exception as e:
        print(f"Error getting sentiment for {symbol}: {e}")
        return 0.0


def get_analyst_ratings(symbol: str) -> dict:
    """
    Get analyst ratings and recommendations

    Args:
        symbol: Stock symbol

    Returns:
        Dict with analyst info
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        ratings = {
            'TargetPrice': info.get('targetMeanPrice', info.get('targetMedianPrice', 0)),
            'TargetHigh': info.get('targetHighPrice', 0),
            'TargetLow': info.get('targetLowPrice', 0),
            'NumberOfAnalysts': info.get('numberOfAnalystOpinions', 0),
            'RecommendationKey': info.get('recommendationKey', 'N/A'),
            'RecommendationMean': info.get('recommendationMean', 3),  # 1=Strong Buy, 5=Sell
            'CurrentPrice': info.get('currentPrice', info.get('regularMarketPrice', 0)),
        }

        # Calculate upside potential
        if ratings['TargetPrice'] and ratings['CurrentPrice']:
            ratings['UpsidePotential'] = (ratings['TargetPrice'] - ratings['CurrentPrice']) / ratings['CurrentPrice'] * 100
        else:
            ratings['UpsidePotential'] = 0

        return ratings

    except Exception as e:
        print(f"Error getting analyst ratings for {symbol}: {e}")
        return {
            'TargetPrice': 0,
            'RecommendationKey': 'N/A',
            'NumberOfAnalysts': 0,
            'UpsidePotential': 0
        }


def calculate_intrinsic_value(fundamentals: dict, discount_rate: float = 0.10, growth_rate: float = 0.05) -> dict:
    """
    Calculate intrinsic value using DCF-like approach

    Args:
        fundamentals: Fundamental data dict
        discount_rate: Required rate of return
        growth_rate: Expected growth rate

    Returns:
        Dict with valuation metrics
    """
    try:
        eps = fundamentals.get('EPS', 0)
        pe = fundamentals.get('PE', 15)
        book_value = fundamentals.get('BookValue', 0)
        roe = fundamentals.get('ROE', 0.1)

        # Graham Number
        if eps > 0 and book_value > 0:
            graham_number = np.sqrt(22.5 * eps * book_value)
        else:
            graham_number = 0

        # Simple DCF estimate
        if eps > 0:
            # 10-year DCF
            future_eps = eps * ((1 + growth_rate) ** 10)
            terminal_value = future_eps * 15  # Terminal PE of 15
            dcf_value = terminal_value / ((1 + discount_rate) ** 10)
        else:
            dcf_value = 0

        # PEG-based value
        growth_percent = fundamentals.get('EarningsGrowth', 0) * 100
        if growth_percent > 0 and eps > 0:
            fair_pe = min(growth_percent, 25)  # Cap at 25
            peg_value = eps * fair_pe
        else:
            peg_value = 0

        return {
            'GrahamNumber': graham_number,
            'DCFValue': dcf_value,
            'PEGValue': peg_value,
            'AverageIntrinsic': np.mean([v for v in [graham_number, dcf_value, peg_value] if v > 0]) if any([graham_number, dcf_value, peg_value]) else 0
        }

    except Exception as e:
        print(f"Error calculating intrinsic value: {e}")
        return {
            'GrahamNumber': 0,
            'DCFValue': 0,
            'PEGValue': 0,
            'AverageIntrinsic': 0
        }

