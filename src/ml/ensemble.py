"""
Ensemble ML Models Module for TradeGenius AI
=============================================
Includes:
- Ensemble prediction using multiple ML models
- Model voting and confidence weighting
- Price action context analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


def create_ensemble_prediction(df: pd.DataFrame, quick_mode: bool = False, deep_mode: bool = False) -> dict:
    """
    Create ensemble prediction using multiple ML models

    Args:
        df: DataFrame with price and indicator data
        quick_mode: If True, use fewer models for faster analysis
        deep_mode: If True, use more rigorous validation and all models

    Returns:
        Dict with ensemble prediction and individual model results
    """
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split, cross_val_score

    # Prepare features
    df_features = df.copy()

    # Create target (1 = price up next day, 0 = down)
    # NOTE: This is a 1-day forward prediction target
    df_features['Target'] = (df_features['Close'].shift(-1) > df_features['Close']).astype(int)

    # Select features based on mode
    if quick_mode:
        feature_cols = ['RSI_14', 'MACD', 'BB_Percent', 'Stoch_K', 'Distance_SMA_20']
    elif deep_mode:
        feature_cols = ['RSI_14', 'RSI_7', 'RSI_21', 'MACD', 'MACD_Histogram', 'BB_Percent', 'BB_Width',
                        'ROC', 'Stoch_K', 'Stoch_D', 'StochRSI_K', 'Distance_SMA_20', 'Distance_SMA_50',
                        'Distance_SMA_200', 'HV_20', 'MFI', 'CCI', 'Williams_R', 'CMF', 'ADX',
                        'Momentum', 'Awesome_Oscillator', 'Force_Index_13', 'Trend_Score']
    else:
        feature_cols = ['RSI_14', 'MACD', 'BB_Percent', 'ROC', 'Stoch_K',
                        'Distance_SMA_20', 'Distance_SMA_50', 'HV_20', 'MFI', 'CCI']

    # Filter available columns
    available_features = [col for col in feature_cols if col in df_features.columns]

    if len(available_features) < 3:
        return {'error': 'Insufficient features calculated'}

    # Drop NaN rows
    df_clean = df_features[available_features + ['Target']].dropna()

    if len(df_clean) < 100:
        return {'error': 'Insufficient data for ML training'}

    X = df_clean[available_features].values
    y = df_clean['Target'].values

    # Replace infinities and validate numeric input
    if not np.isfinite(X).all():
        finite_mask = np.isfinite(X).all(axis=1)
        X = X[finite_mask]
        y = y[finite_mask]

    if X.size == 0 or y.size == 0:
        return {'error': 'No valid numeric data for training after cleaning'}

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split data - different test size based on mode
    test_size = 0.1 if quick_mode else (0.3 if deep_mode else 0.2)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=test_size, shuffle=False)

    # Define models based on mode
    if quick_mode:
        # Quick mode: only 2 fastest models
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1),
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=200)
        }
    elif deep_mode:
        # Deep mode: all models with more estimators
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1, max_depth=10),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=150, random_state=42, learning_rate=0.05),
            'AdaBoost': AdaBoostClassifier(n_estimators=150, random_state=42, learning_rate=0.5),
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=500, C=0.5),
            'SVM': SVC(probability=True, random_state=42, kernel='rbf', C=1.0)
        }
    else:
        # Standard mode
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'AdaBoost': AdaBoostClassifier(n_estimators=100, random_state=42),
            'Logistic Regression': LogisticRegression(random_state=42),
            'SVM': SVC(probability=True, random_state=42)
        }

    predictions = {}
    probabilities = []

    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            accuracy = model.score(X_test, y_test)

            # For deep mode, use cross-validation for more reliable accuracy
            cv_accuracy = None
            if deep_mode:
                try:
                    cv_scores = cross_val_score(model, X_scaled[:-1], y[:-1], cv=5, scoring='accuracy')
                    cv_accuracy = float(np.mean(cv_scores))
                except:
                    cv_accuracy = accuracy

            # Predict for last row (tomorrow)
            last_features = X_scaled[-1:].reshape(1, -1)
            pred = model.predict(last_features)[0]
            prob = model.predict_proba(last_features)[0]

            predictions[name] = {
                'prediction': 'Bullish' if pred == 1 else 'Bearish',
                'confidence': float(max(prob)),
                'accuracy': float(cv_accuracy if cv_accuracy else accuracy),
                'test_accuracy': float(accuracy)
            }
            probabilities.append(prob[1])  # Probability of bullish

        except Exception as e:
            predictions[name] = {'error': str(e)}

    # Ensemble vote
    if probabilities:
        avg_prob = np.mean(probabilities)

        # Count votes from individual models
        bullish_votes = 0
        bearish_votes = 0
        bullish_confidence_sum = 0
        bearish_confidence_sum = 0

        for name, pred_data in predictions.items():
            if 'error' not in pred_data:
                conf = pred_data.get('confidence', 0.5)
                acc = pred_data.get('accuracy', 0.5)
                weight = conf * acc

                if pred_data['prediction'] == 'Bullish':
                    bullish_votes += 1
                    bullish_confidence_sum += weight
                else:
                    bearish_votes += 1
                    bearish_confidence_sum += weight

        total_votes = bullish_votes + bearish_votes

        # Ensemble decision based on majority vote weighted by confidence
        if total_votes > 0:
            # Calculate weighted vote - higher values = more bullish
            if bullish_votes > bearish_votes:
                # Majority bullish
                weighted_avg = 0.5 + (bullish_confidence_sum / total_votes) * 0.5
                ensemble_prediction = 'Bullish'
            elif bearish_votes > bullish_votes:
                # Majority bearish
                weighted_avg = 0.5 - (bearish_confidence_sum / total_votes) * 0.5
                ensemble_prediction = 'Bearish'
            else:
                # Tie - use raw probability average
                weighted_avg = avg_prob
                ensemble_prediction = 'Bullish' if avg_prob > 0.5 else 'Bearish'
        else:
            weighted_avg = avg_prob
            ensemble_prediction = 'Bullish' if avg_prob > 0.5 else 'Bearish'

        ensemble_confidence = abs(weighted_avg - 0.5) * 2  # Scale to 0-1
    else:
        avg_prob = 0.5
        weighted_avg = 0.5
        ensemble_prediction = 'Neutral'
        ensemble_confidence = 0

    # ═══ Price Action Context (informational, does NOT override ML) ═══
    # Instead of overriding ML predictions, we report price action context
    # so the user can see when ML disagrees with recent price action
    price_action_context = {}
    if len(df) > 20:
        try:
            recent_close = df['Close'].iloc[-1]
            close_5d_ago = df['Close'].iloc[-5] if len(df) >= 5 else recent_close
            close_10d_ago = df['Close'].iloc[-10] if len(df) >= 10 else recent_close
            close_20d_ago = df['Close'].iloc[-20] if len(df) >= 20 else recent_close

            short_trend = (recent_close / close_5d_ago - 1) * 100
            med_trend = (recent_close / close_10d_ago - 1) * 100

            sma_20 = df['Close'].rolling(20).mean().iloc[-1] if len(df) >= 20 else recent_close
            sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else recent_close

            price_action_score = 0
            if short_trend > 2: price_action_score += 1
            elif short_trend < -2: price_action_score -= 1
            if med_trend > 3: price_action_score += 1
            elif med_trend < -3: price_action_score -= 1
            if recent_close > sma_20: price_action_score += 1
            else: price_action_score -= 1
            if recent_close > sma_50: price_action_score += 0.5
            else: price_action_score -= 0.5
            if sma_20 > sma_50: price_action_score += 0.5
            else: price_action_score -= 0.5

            if price_action_score >= 2:
                pa_direction = 'Bullish'
            elif price_action_score <= -2:
                pa_direction = 'Bearish'
            else:
                pa_direction = 'Neutral'

            price_action_context = {
                'direction': pa_direction,
                'score': price_action_score,
                'short_trend_5d': round(short_trend, 2),
                'med_trend_10d': round(med_trend, 2),
                'agrees_with_ml': (pa_direction == ensemble_prediction) or pa_direction == 'Neutral'
            }

            # Only reduce confidence when there's a strong disagreement - do NOT flip predictions
            if not price_action_context['agrees_with_ml'] and abs(price_action_score) >= 2.5:
                ensemble_confidence = max(0.4, ensemble_confidence - 0.15)

        except Exception:
            pass  # Keep original ensemble if price action check fails

    return {
        'ensemble_prediction': ensemble_prediction,
        'ensemble_confidence': ensemble_confidence,
        'prediction_horizon': '1-day',  # Clearly label the prediction timeframe
        'bullish_probability': avg_prob,
        'weighted_probability': weighted_avg,
        'individual_models': predictions,
        'features_used': available_features,
        'analysis_mode': 'Quick' if quick_mode else ('Deep' if deep_mode else 'Standard'),
        'models_used': len(models),
        'price_action_context': price_action_context
    }