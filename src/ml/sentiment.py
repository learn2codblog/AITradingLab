"""
Sentiment Analysis Module for TradeGenius AI
=============================================
Includes:
- Keyword-based sentiment analysis
- Transformer-based sentiment analysis (FinBERT, RoBERTa)
- Batch sentiment processing
- News sentiment aggregation
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


def analyze_sentiment_simple(text: str) -> dict:
    """
    Simple keyword-based sentiment analysis

    Args:
        text: Text to analyze

    Returns:
        Dict with sentiment score and label
    """
    positive_words = [
        'buy', 'bullish', 'upgrade', 'growth', 'profit', 'gain', 'surge', 'rally',
        'strong', 'outperform', 'beat', 'exceed', 'positive', 'optimistic', 'recovery',
        'breakthrough', 'success', 'high', 'rise', 'jump', 'soar', 'boost'
    ]

    negative_words = [
        'sell', 'bearish', 'downgrade', 'loss', 'decline', 'drop', 'fall', 'crash',
        'weak', 'underperform', 'miss', 'negative', 'pessimistic', 'concern', 'risk',
        'fail', 'low', 'plunge', 'tumble', 'slump', 'cut', 'warning'
    ]

    text_lower = text.lower()
    words = text_lower.split()

    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)

    total = positive_count + negative_count
    if total == 0:
        return {'score': 0, 'label': 'Neutral', 'confidence': 0.5}

    score = (positive_count - negative_count) / total

    if score > 0.3:
        label = 'Positive'
    elif score < -0.3:
        label = 'Negative'
    else:
        label = 'Neutral'

    confidence = abs(score) * 0.5 + 0.5

    return {
        'score': score,
        'label': label,
        'confidence': confidence,
        'positive_words': positive_count,
        'negative_words': negative_count
    }


def analyze_sentiment_transformer(text: str, use_cache: bool = True,
                                   model_type: str = 'financial') -> dict:
    """
    Enhanced sentiment analysis using HuggingFace transformer model.
    Supports financial domain models for better accuracy on market-related text.
    Falls back to keyword-based method if transformers not available.

    Args:
        text: Text to analyze
        use_cache: Whether to cache the model (default True)
        model_type: 'financial' (FinBERT), 'twitter' (RoBERTa), or 'general' (DistilBERT)

    Returns:
        Dict with sentiment score, label, and confidence
    """
    # Model options in order of preference for financial text
    model_configs = {
        'financial': {
            'model': 'ProsusAI/finbert',
            'labels': {'positive': 1, 'negative': -1, 'neutral': 0}
        },
        'twitter': {
            'model': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
            'labels': {'positive': 1, 'negative': -1, 'neutral': 0}
        },
        'general': {
            'model': 'distilbert-base-uncased-finetuned-sst-2-english',
            'labels': {'POSITIVE': 1, 'NEGATIVE': -1}
        }
    }

    # Try transformer-based analysis
    try:
        from transformers import pipeline

        # Get model config
        config = model_configs.get(model_type, model_configs['financial'])
        cache_key = f'_pipeline_{model_type}'

        # Use cached model or create new one
        if not hasattr(analyze_sentiment_transformer, cache_key) or not use_cache:
            try:
                # Try preferred model first
                setattr(analyze_sentiment_transformer, cache_key, pipeline(
                    "sentiment-analysis",
                    model=config['model'],
                    device=-1  # CPU
                ))
            except Exception:
                # Fallback to general model
                if model_type != 'general':
                    config = model_configs['general']
                    setattr(analyze_sentiment_transformer, cache_key, pipeline(
                        "sentiment-analysis",
                        model=config['model'],
                        device=-1
                    ))
                else:
                    raise

        sentiment_pipeline = getattr(analyze_sentiment_transformer, cache_key)

        # Truncate text if too long
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]

        result = sentiment_pipeline(text)[0]

        # Convert to our format based on model type
        label = result['label'].lower()
        raw_score = result['score']

        # Map label to sentiment direction
        label_map = {k.lower(): v for k, v in config['labels'].items()}
        direction = label_map.get(label, 0)

        if direction == 1:
            sentiment_score = raw_score
            sentiment_label = 'Positive'
        elif direction == -1:
            sentiment_score = -raw_score
            sentiment_label = 'Negative'
        else:
            sentiment_score = 0
            sentiment_label = 'Neutral'

        # Adjust for confidence threshold
        if abs(sentiment_score) < 0.6:
            sentiment_label = 'Neutral'

        return {
            'score': float(sentiment_score),
            'label': sentiment_label,
            'confidence': float(raw_score),
            'method': 'transformer',
            'model': config['model'],
            'model_type': model_type,
            'raw_label': result['label'],
            'raw_score': float(result['score'])
        }

    except ImportError:
        result = analyze_sentiment_simple(text)
        result['method'] = 'keyword'
        result['note'] = 'Install transformers package for better accuracy: pip install transformers'
        return result

    except Exception as e:
        # Fall back to keyword-based analysis on any error
        result = analyze_sentiment_simple(text)
        result['method'] = 'keyword'
        result['error'] = str(e)
        result['fallback_reason'] = f'Failed to load {model_type} model'
        return result


def analyze_sentiment_batch(texts: list, use_transformer: bool = True) -> list:
    """
    Analyze sentiment for multiple texts efficiently

    Args:
        texts: List of text strings to analyze
        use_transformer: Whether to try transformer first (default True)

    Returns:
        List of sentiment result dicts
    """
    results = []

    if use_transformer:
        try:
            from transformers import pipeline

            # Batch processing with transformer
            if not hasattr(analyze_sentiment_batch, '_pipeline'):
                analyze_sentiment_batch._pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=-1
                )

            pipe = analyze_sentiment_batch._pipeline

            # Truncate texts
            truncated = [t[:500] if len(t) > 500 else t for t in texts]

            # Batch predict
            raw_results = pipe(truncated, batch_size=8)

            for raw in raw_results:
                label = raw['label']
                score = raw['score']

                if label == 'POSITIVE':
                    sentiment_score = score
                    sentiment_label = 'Positive' if score >= 0.6 else 'Neutral'
                else:
                    sentiment_score = -score
                    sentiment_label = 'Negative' if score >= 0.6 else 'Neutral'

                results.append({
                    'score': float(sentiment_score),
                    'label': sentiment_label,
                    'confidence': float(score),
                    'method': 'transformer'
                })

            return results

        except Exception:
            pass

    # Fallback to keyword method
    for text in texts:
        result = analyze_sentiment_simple(text)
        result['method'] = 'keyword'
        results.append(result)

    return results


def analyze_news_sentiment(news_list: list) -> dict:
    """
    Analyze sentiment from list of news headlines

    Args:
        news_list: List of news headlines/articles

    Returns:
        Aggregated sentiment analysis
    """
    if not news_list:
        return {'overall_sentiment': 'Neutral', 'score': 0, 'confidence': 0}

    sentiments = [analyze_sentiment_simple(news) for news in news_list]

    avg_score = np.mean([s['score'] for s in sentiments])
    avg_confidence = np.mean([s['confidence'] for s in sentiments])

    positive_count = sum(1 for s in sentiments if s['label'] == 'Positive')
    negative_count = sum(1 for s in sentiments if s['label'] == 'Negative')
    neutral_count = sum(1 for s in sentiments if s['label'] == 'Neutral')

    if avg_score > 0.2:
        overall = 'Positive'
    elif avg_score < -0.2:
        overall = 'Negative'
    else:
        overall = 'Neutral'

    return {
        'overall_sentiment': overall,
        'score': avg_score,
        'confidence': avg_confidence,
        'breakdown': {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count
        },
        'total_analyzed': len(news_list)
    }