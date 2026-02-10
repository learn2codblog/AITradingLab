"""
Market Analysis Module for TradeGenius AI
==========================================
Includes:
- Market regime detection
- Comprehensive AI analysis generation
- Transformer-based forecasting
- Technical scoring system
- AI recommendation engine
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


def detect_market_regime(df: pd.DataFrame) -> dict:
    """
    Detect current market regime using multiple indicators

    Returns:
        Dict with regime classification and characteristics
    """
    if len(df) < 200:
        return {'regime': 'Unknown', 'confidence': 0}

    latest = df.iloc[-1]

    # Get key indicators
    rsi = latest.get('RSI_14', 50)
    adx = latest.get('ADX', 25)
    bb_width = latest.get('BB_Width', 0.1)
    hv = latest.get('HV_20', 20)
    trend_score = latest.get('Trend_Score', 2.5)

    # Calculate 50-day return and volatility
    returns_50d = (df['Close'].iloc[-1] / df['Close'].iloc[-50] - 1) * 100

    # Regime classification
    regimes = []

    # Trend regimes
    if adx > 25:
        if trend_score >= 4:
            regimes.append(('Strong Uptrend', 0.9))
        elif trend_score <= 1:
            regimes.append(('Strong Downtrend', 0.9))
        else:
            regimes.append(('Trending', 0.7))
    else:
        regimes.append(('Range-bound', 0.6))

    # Volatility regimes
    if hv > 40:
        regimes.append(('High Volatility', 0.85))
    elif hv < 15:
        regimes.append(('Low Volatility', 0.75))
    else:
        regimes.append(('Normal Volatility', 0.6))

    # Momentum regimes
    if rsi > 70:
        regimes.append(('Overbought', 0.8))
    elif rsi < 30:
        regimes.append(('Oversold', 0.8))

    # Determine primary regime
    primary_regime = max(regimes, key=lambda x: x[1])

    # Trading recommendations based on regime
    if 'Strong Uptrend' in primary_regime[0]:
        strategy = 'Buy dips, ride the trend'
        risk_level = 'Low'
    elif 'Strong Downtrend' in primary_regime[0]:
        strategy = 'Avoid buying, wait for reversal signals'
        risk_level = 'High'
    elif 'Range-bound' in primary_regime[0]:
        strategy = 'Buy at support, sell at resistance'
        risk_level = 'Medium'
    elif 'High Volatility' in primary_regime[0]:
        strategy = 'Reduce position size, use tight stops'
        risk_level = 'High'
    elif 'Overbought' in primary_regime[0]:
        strategy = 'Consider taking profits, wait for pullback'
        risk_level = 'Medium-High'
    elif 'Oversold' in primary_regime[0]:
        strategy = 'Look for bullish reversal signals'
        risk_level = 'Medium'
    else:
        strategy = 'Follow standard trend analysis'
        risk_level = 'Medium'

    return {
        'primary_regime': primary_regime[0],
        'confidence': primary_regime[1],
        'all_regimes': [r[0] for r in regimes],
        'suggested_strategy': strategy,
        'risk_level': risk_level,
        'indicators': {
            'ADX': adx,
            'RSI': rsi,
            'Historical_Volatility': hv,
            'Trend_Score': trend_score,
            '50d_Return': returns_50d
        }
    }


def calculate_technical_score(df: pd.DataFrame) -> dict:
    """
    Calculate composite technical score from 0-100
    """
    scores = []
    breakdown = {}

    latest = df.iloc[-1]

    # Trend Score (25 points max)
    trend_score = latest.get('Trend_Score', 2.5)
    trend_points = (trend_score / 5) * 25
    breakdown['Trend'] = trend_points
    scores.append(trend_points)

    # Momentum Score (25 points max)
    rsi = latest.get('RSI_14', 50)
    macd = latest.get('MACD', 0)
    macd_signal = latest.get('MACD_Signal', 0)

    # RSI scoring: Higher score = more bullish momentum
    # 50-65: Healthy bullish momentum (best)
    # 40-50: Neutral/weak
    # 30-40: Bearish momentum
    # <30: Oversold (potential reversal but NOT confirmed bullish - score low)
    # 65-70: Strong but approaching overbought
    # >70: Overbought (bearish risk - score low)
    if 50 <= rsi <= 65:
        rsi_score = 12.5  # Healthy bullish momentum
    elif 40 <= rsi < 50:
        rsi_score = 8      # Neutral/slightly bearish
    elif 65 < rsi <= 70:
        rsi_score = 10     # Strong but approaching overbought
    elif rsi > 70:
        rsi_score = 3      # Overbought - bearish risk
    elif 30 <= rsi < 40:
        rsi_score = 5      # Bearish momentum
    else:  # rsi < 30
        rsi_score = 3      # Oversold - not confirmed bullish yet

    macd_score = 12.5 if macd > macd_signal else 5
    momentum_points = rsi_score + macd_score
    breakdown['Momentum'] = momentum_points
    scores.append(momentum_points)

    # Volume Score (25 points max)
    mfi = latest.get('MFI', 50)
    cmf = latest.get('CMF', 0)

    mfi_score = 12.5 if mfi > 50 else 5
    cmf_score = 12.5 if cmf > 0 else 5
    volume_points = mfi_score + cmf_score
    breakdown['Volume'] = volume_points
    scores.append(volume_points)

    # Volatility Score (25 points max)
    bb_percent = latest.get('BB_Percent', 0.5)
    hv = latest.get('HV_20', 20)

    bb_score = 15 if 0.2 < bb_percent < 0.8 else 5
    vol_score = 10 if hv < 30 else 5
    volatility_points = bb_score + vol_score
    breakdown['Volatility'] = volatility_points
    scores.append(volatility_points)

    total_score = sum(scores)

    # Grade
    if total_score >= 80:
        grade = 'A'
    elif total_score >= 70:
        grade = 'B'
    elif total_score >= 55:
        grade = 'C'
    elif total_score >= 40:
        grade = 'D'
    else:
        grade = 'F'

    return {
        'score': total_score,
        'grade': grade,
        'breakdown': breakdown,
        'max_score': 100
    }


def generate_ai_recommendation(analysis: dict, fundamentals: dict = None, analysis_depth: str = 'Standard') -> dict:
    """
    Generate final AI recommendation based on all analysis

    Args:
        analysis: Dict containing all analysis results
        fundamentals: Fundamental data (optional)
        analysis_depth: 'Quick Analysis', 'Standard', or 'Deep Analysis'
    """
    signals = []

    # Weight multipliers based on analysis depth
    if analysis_depth == 'Quick Analysis':
        # Quick mode: More weight on technical score, less on ML
        tech_weight = 0.40
        regime_weight = 0.25
        ml_weight = 0.15
        pattern_weight = 0.20
    elif analysis_depth == 'Deep Analysis':
        # Deep mode: More weight on ML, patterns get more weight
        tech_weight = 0.20
        regime_weight = 0.20
        ml_weight = 0.35
        pattern_weight = 0.25
    else:
        # Standard mode: Balanced weights
        tech_weight = 0.30
        regime_weight = 0.25
        ml_weight = 0.25
        pattern_weight = 0.20

    # Technical Score signal
    tech_score = analysis.get('technical_score', {}).get('score', 50)
    if tech_score >= 70:
        signals.append(('BUY', tech_weight))
    elif tech_score <= 30:
        signals.append(('SELL', tech_weight))
    else:
        signals.append(('HOLD', tech_weight * 0.6))

    # Market Regime signal
    regime = analysis.get('market_regime', {}).get('primary_regime', 'Unknown')
    if 'Uptrend' in regime:
        signals.append(('BUY', regime_weight))
    elif 'Downtrend' in regime:
        signals.append(('SELL', regime_weight))
    elif 'Oversold' in regime:
        signals.append(('BUY', regime_weight * 0.8))
    elif 'Overbought' in regime:
        signals.append(('SELL', regime_weight * 0.8))
    else:
        signals.append(('HOLD', regime_weight * 0.5))

    # ML Ensemble signal
    ml_pred = analysis.get('ml_ensemble', {}).get('ensemble_prediction', 'Unknown')
    ml_conf = analysis.get('ml_ensemble', {}).get('ensemble_confidence', 0.5)
    if ml_pred == 'Bullish':
        signals.append(('BUY', ml_weight * ml_conf))
    elif ml_pred == 'Bearish':
        signals.append(('SELL', ml_weight * ml_conf))
    else:
        signals.append(('HOLD', ml_weight * 0.3))

    # Pattern signal - consider both candlestick and chart patterns
    candle_patterns = analysis.get('candlestick_patterns', {})
    chart_patterns = analysis.get('chart_patterns', {})

    bullish_patterns = sum(1 for p in candle_patterns.values() if p.get('signal') == 'Bullish')
    bearish_patterns = sum(1 for p in candle_patterns.values() if p.get('signal') == 'Bearish')
    bullish_patterns += sum(1 for p in chart_patterns.values() if p.get('signal') == 'Bullish')
    bearish_patterns += sum(1 for p in chart_patterns.values() if p.get('signal') == 'Bearish')

    if bullish_patterns > bearish_patterns:
        signals.append(('BUY', pattern_weight * min(1.0, bullish_patterns / 3)))
    elif bearish_patterns > bullish_patterns:
        signals.append(('SELL', pattern_weight * min(1.0, bearish_patterns / 3)))
    else:
        signals.append(('HOLD', pattern_weight * 0.4))

    # Calculate weighted recommendation
    buy_score = sum(w for s, w in signals if s == 'BUY')
    sell_score = sum(w for s, w in signals if s == 'SELL')
    hold_score = sum(w for s, w in signals if s == 'HOLD')

    total = buy_score + sell_score + hold_score
    if total > 0:
        buy_pct = buy_score / total
        sell_pct = sell_score / total
        hold_pct = hold_score / total
    else:
        buy_pct = sell_pct = hold_pct = 0.33

    # Check for conflicting signals: if buy and sell are both significant, reduce confidence
    # This prevents the system from giving a strong BUY when half the signals say SELL
    signal_conflict = min(buy_score, sell_score) / max(buy_score, sell_score, 0.01)

    # Final recommendation
    if signal_conflict > 0.7:
        # Strong conflict (>70%) between buy and sell signals - force HOLD
        recommendation = 'HOLD'
        action = 'Wait for clearer signal - high indicator conflict'
        confidence = 0.25  # Low confidence due to high conflict
    elif signal_conflict > 0.5:
        # Moderate conflict - reduce confidence but allow directional recommendation
        if buy_pct > sell_pct:
            recommendation = 'BUY'
            action = 'Caution: moderate signal conflict'
            confidence = buy_pct * 0.5
        elif sell_pct > buy_pct:
            recommendation = 'SELL'
            action = 'Caution: moderate signal conflict'
            confidence = sell_pct * 0.5
        else:
            recommendation = 'HOLD'
            action = 'Wait for clearer signal'
            confidence = 0.3
    elif buy_pct > 0.5:
        recommendation = 'STRONG BUY' if buy_pct > 0.7 else 'BUY'
        action = 'Enter long position'
        confidence = buy_pct * (1 - signal_conflict * 0.5)  # Reduce confidence by conflict level
    elif sell_pct > 0.5:
        recommendation = 'STRONG SELL' if sell_pct > 0.7 else 'SELL'
        action = 'Exit or short position'
        confidence = sell_pct * (1 - signal_conflict * 0.5)
    else:
        recommendation = 'HOLD'
        action = 'Wait for clearer signal'
        confidence = max(buy_pct, sell_pct, hold_pct)

    # Detect contradictions between signals
    contradictions = []
    warnings = []

    # Check if patterns and ML contradict
    pattern_signal = 'Bullish' if bullish_patterns > bearish_patterns else ('Bearish' if bearish_patterns > bullish_patterns else 'Neutral')
    if pattern_signal != 'Neutral' and ml_pred != 'Unknown':
        if pattern_signal == 'Bullish' and ml_pred == 'Bearish':
            contradictions.append({
                'type': 'Pattern vs ML Contradiction',
                'description': f'Chart patterns suggest Bullish ({bullish_patterns} bullish vs {bearish_patterns} bearish) but ML models predict Bearish',
                'resolution': 'Consider waiting for confirmation or reducing position size'
            })
        elif pattern_signal == 'Bearish' and ml_pred == 'Bullish':
            contradictions.append({
                'type': 'Pattern vs ML Contradiction',
                'description': f'Chart patterns suggest Bearish ({bearish_patterns} bearish vs {bullish_patterns} bullish) but ML models predict Bullish',
                'resolution': 'Consider waiting for confirmation or reducing position size'
            })

    # Check if regime contradicts recommendation
    if 'Uptrend' in regime and 'SELL' in recommendation:
        warnings.append('Market is in uptrend but recommendation is SELL - possible short-term correction')
    elif 'Downtrend' in regime and 'BUY' in recommendation:
        warnings.append('Market is in downtrend but recommendation is BUY - possible reversal signal')

    # Check if overbought/oversold contradicts patterns
    if 'Overbought' in regime and bullish_patterns > bearish_patterns:
        warnings.append('Bullish patterns detected but RSI shows overbought - be cautious of pullback')
    elif 'Oversold' in regime and bearish_patterns > bullish_patterns:
        warnings.append('Bearish patterns detected but RSI shows oversold - potential bounce possible')

    return {
        'recommendation': recommendation,
        'action': action,
        'confidence': confidence,
        'probabilities': {
            'buy': buy_pct,
            'sell': sell_pct,
            'hold': hold_pct
        },
        'factors': {
            'technical_score': tech_score,
            'market_regime': regime,
            'ml_prediction': ml_pred,
            'bullish_patterns': bullish_patterns,
            'bearish_patterns': bearish_patterns
        },
        'contradictions': contradictions,
        'warnings': warnings,
        'analysis_depth': analysis_depth
    }


def generate_ai_analysis(df: pd.DataFrame, symbol: str = '', fundamentals: dict = None, analysis_depth: str = 'Standard') -> dict:
    """
    Generate comprehensive AI-powered analysis

    Args:
        df: DataFrame with price data and indicators
        symbol: Stock symbol
        fundamentals: Fundamental data
        analysis_depth: 'Quick Analysis', 'Standard', or 'Deep Analysis'

    Returns:
        Complete AI analysis report
    """
    from .indicators import calculate_advanced_indicators
    from .patterns import detect_candlestick_patterns, detect_chart_patterns
    from .ensemble import create_ensemble_prediction

    analysis = {
        'symbol': symbol,
        'timestamp': datetime.now().isoformat(),
        'current_price': df['Close'].iloc[-1],
        'analysis_depth': analysis_depth
    }

    # 1. Calculate advanced indicators if not present
    if 'RSI_14' not in df.columns:
        df = calculate_advanced_indicators(df)

    # 2. Pattern Recognition - Always run for all modes
    analysis['candlestick_patterns'] = detect_candlestick_patterns(df)
    analysis['chart_patterns'] = detect_chart_patterns(df)

    # 3. Market Regime - Always run
    analysis['market_regime'] = detect_market_regime(df)

    # 4. Anomaly Detection - Skip for Quick Analysis
    if analysis_depth != 'Quick Analysis':
        from .anomaly import detect_anomalies
        analysis['anomalies'] = detect_anomalies(df)
    else:
        analysis['anomalies'] = {'anomalies': [], 'total_alerts': 0, 'highest_severity': 'None'}

    # 5. Ensemble ML Prediction - Different configs based on depth
    if len(df) >= 200:
        if analysis_depth == 'Quick Analysis':
            # Quick: Use fewer models and less data
            analysis['ml_ensemble'] = create_ensemble_prediction(df, quick_mode=True)
        elif analysis_depth == 'Deep Analysis':
            # Deep: Use all models with extended validation
            analysis['ml_ensemble'] = create_ensemble_prediction(df, deep_mode=True)
        else:
            # Standard mode
            analysis['ml_ensemble'] = create_ensemble_prediction(df)
    else:
        analysis['ml_ensemble'] = {'error': 'Insufficient data for ML'}

    # 6. Technical Score (0-100)
    tech_score = calculate_technical_score(df)
    analysis['technical_score'] = tech_score

    # 7. Overall AI Recommendation - weighted differently based on depth
    analysis['ai_recommendation'] = generate_ai_recommendation(analysis, fundamentals, analysis_depth)

    return analysis


def get_positional_encoding(seq_len: int, d_model: int) -> np.ndarray:
    """
    Generate positional encoding for Transformer

    Args:
        seq_len: Sequence length
        d_model: Model dimension

    Returns:
        Positional encoding matrix
    """
    pos = np.arange(seq_len)[:, np.newaxis]
    dim_idxs = np.arange(d_model)[np.newaxis, :]

    angle_rates = 1 / np.power(10000, (2 * (dim_idxs // 2)) / np.float32(d_model))
    pos_encoding = pos * angle_rates

    # Apply sin to even indices, cos to odd indices
    pos_encoding[:, 0::2] = np.sin(pos_encoding[:, 0::2])
    pos_encoding[:, 1::2] = np.cos(pos_encoding[:, 1::2])

    return pos_encoding[np.newaxis, ...]


def build_transformer_model(seq_len: int = 60, forecast_len: int = 5,
                           n_features: int = 1, n_heads: int = 4,
                           n_layers: int = 2, d_model: int = 64):
    """
    Build Transformer model for time series forecasting

    Args:
        seq_len: Input sequence length
        forecast_len: Output forecast length
        n_features: Number of input features
        n_heads: Number of attention heads
        d_model: Model/embedding dimension
        n_layers: Number of transformer layers

    Returns:
        Compiled Keras model
    """
    try:
        from tensorflow.keras.models import Model
        from tensorflow.keras.layers import (
            Input, Dense, MultiHeadAttention, LayerNormalization,
            Dropout, Add, Flatten, RepeatVector, TimeDistributed,
            Embedding, Reshape
        )
        from tensorflow.keras.optimizers import Adam
        import tensorflow as tf

        # Input
        inputs = Input(shape=(seq_len, n_features))

        # Linear projection to d_model dimensions
        x = Dense(d_model)(inputs)

        # Add positional encoding
        pos_encoding = get_positional_encoding(seq_len, d_model)
        pos_encoding = tf.convert_to_tensor(pos_encoding, dtype=tf.float32)
        x = x + pos_encoding
        x = Dropout(0.1)(x)

        # Transformer encoder blocks
        for _ in range(n_layers):
            # Multi-head attention
            attn_output = MultiHeadAttention(
                num_heads=n_heads,
                key_dim=d_model // n_heads
            )(x, x)
            attn_output = Dropout(0.1)(attn_output)

            # Skip connection and norm
            x = Add()([x, attn_output])
            x = LayerNormalization(epsilon=1e-6)(x)

            # Feed-forward
            ff_output = Dense(d_model * 2, activation='relu')(x)
            ff_output = Dense(d_model)(ff_output)
            ff_output = Dropout(0.1)(ff_output)

            # Skip connection and norm
            x = Add()([x, ff_output])
            x = LayerNormalization(epsilon=1e-6)(x)

        # Decoder - use last timestep representation
        x_last = x[:, -1, :]  # Take last timestep

        # Project to a hidden representation
        x = Dense(d_model, activation='relu')(x_last)
        x = Dense(d_model, activation='relu')(x)

        # Project directly to forecast_len * n_features and reshape
        x = Dense(forecast_len * n_features)(x)
        outputs = Reshape((forecast_len, n_features))(x)

        # Create model
        model = Model(inputs=inputs, outputs=outputs)

        # Compile
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='huber',
            metrics=['mae']
        )

        return model

    except ImportError:
        return None


def predict_with_transformer(df: pd.DataFrame, seq_len: int = 60,
                            forecast_len: int = 5, epochs: int = 50,
                            n_heads: int = 4, n_layers: int = 2,
                            d_model: int = 64) -> dict:
    """
    Multi-step forecasting using Transformer model
    Predicts next 1, 3, and 5 days prices

    Args:
        df: DataFrame with price data
        seq_len: Sequence length for input
        forecast_len: Days to forecast (5 by default = 1/3/5 days)
        epochs: Training epochs
        n_heads: Number of attention heads
        n_layers: Number of transformer layers
        d_model: Embedding dimension

    Returns:
        Dict with predictions for 1, 3, 5 days
    """
    try:
        from sklearn.preprocessing import MinMaxScaler
        from tensorflow.keras.callbacks import EarlyStopping

        min_required = seq_len + forecast_len + 50
        if len(df) < min_required:
            return {'error': f'Insufficient data. Need {min_required} rows, got {len(df)}'}

        # Use Close price
        data = df['Close'].values.reshape(-1, 1)

        # Scale
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)

        # Create sequences
        X, y = [], []
        for i in range(seq_len, len(scaled_data) - forecast_len):
            X.append(scaled_data[i - seq_len:i])
            y.append(scaled_data[i:i + forecast_len])

        X = np.array(X)
        y = np.array(y)

        # Train/test split (80/20)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # Build model
        model = build_transformer_model(
            seq_len=seq_len,
            forecast_len=forecast_len,
            n_features=1,
            n_heads=n_heads,
            n_layers=n_layers,
            d_model=d_model
        )

        if model is None:
            return {'error': 'TensorFlow not installed'}

        # Train
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )

        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=32,
            validation_split=0.1,
            callbacks=[early_stop],
            verbose=0
        )

        # Predict on test set for evaluation
        y_pred_test = model.predict(X_test, verbose=0)
        mae_test = np.mean(np.abs(y_pred_test - y_test))

        # Get last 5-day window for future prediction
        last_sequence = scaled_data[-seq_len:].reshape(1, seq_len, 1)

        # Predict
        predicted_scaled = model.predict(last_sequence, verbose=0)[0]

        # Inverse transform
        dummy = np.repeat(data[-1], forecast_len).reshape(-1, 1)
        dummy[:, 0] = predicted_scaled[:, 0]
        predicted_prices = scaler.inverse_transform(dummy)[:, 0]

        current_price = df['Close'].iloc[-1]

        # Extract 1-day, 3-day, 5-day predictions
        pred_1day = predicted_prices[0] if len(predicted_prices) > 0 else current_price
        pred_3day = predicted_prices[2] if len(predicted_prices) > 2 else (predicted_prices[-1] if len(predicted_prices) > 0 else current_price)
        pred_5day = predicted_prices[-1]

        # Calculate returns
        ret_1day = (pred_1day - current_price) / current_price * 100
        ret_3day = (pred_3day - current_price) / current_price * 100
        ret_5day = (pred_5day - current_price) / current_price * 100

        # Determine trend
        final_trend = 'Bullish' if ret_5day > 2 else ('Strong Bullish' if ret_5day > 3 else
                     ('Bearish' if ret_5day < -2 else ('Strong Bearish' if ret_5day < -3 else 'Neutral')))

        return {
            'model_type': 'Transformer',
            'current_price': float(current_price),
            'predictions': {
                '1_day': {
                    'price': float(pred_1day),
                    'change_pct': float(ret_1day)
                },
                '3_day': {
                    'price': float(pred_3day),
                    'change_pct': float(ret_3day)
                },
                '5_day': {
                    'price': float(pred_5day),
                    'change_pct': float(ret_5day)
                }
            },
            'all_daily_predictions': predicted_prices.tolist(),
            'overall_trend': final_trend,
            'mae_test': float(mae_test),
            'n_test_samples': len(X_test),
            'model_config': {
                'seq_len': seq_len,
                'forecast_len': forecast_len,
                'n_heads': n_heads,
                'n_layers': n_layers,
                'd_model': d_model
            },
            'epochs_trained': len(history.history['loss'])
        }

    except Exception as e:
        return {'error': str(e)}