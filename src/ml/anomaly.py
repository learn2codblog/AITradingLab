"""
Anomaly Detection Module for TradeGenius AI
===========================================
Includes:
- Autoencoder-based anomaly detection
- Statistical anomaly detection
- Market anomaly alerts
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


def detect_anomalies_autoencoder(df: pd.DataFrame, features: list = None,
                                contamination: float = 0.1, epochs: int = 100) -> dict:
    """
    Detect anomalies using autoencoder neural network

    Args:
        df: DataFrame with price and indicator data
        features: List of features to use for anomaly detection
        contamination: Expected proportion of anomalies (0.1 = 10%)
        epochs: Training epochs

    Returns:
        Dict with anomaly detection results
    """
    try:
        from tensorflow.keras.models import Model
        from tensorflow.keras.layers import Input, Dense
        from tensorflow.keras.optimizers import Adam
        from sklearn.preprocessing import MinMaxScaler

        # Default features for anomaly detection
        if features is None:
            features = ['Close', 'Volume', 'RSI_14', 'MACD', 'ATR_14', 'BB_Percent']

        # Filter available features
        available_features = [f for f in features if f in df.columns]
        if len(available_features) < 3:
            return {'error': 'Insufficient features for anomaly detection'}

        # Prepare data
        data = df[available_features].copy()
        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data = data.dropna()

        if len(data) < 50:
            return {'error': 'Insufficient data after cleaning'}

        # Scale data
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(data.values)

        # Build autoencoder
        input_dim = scaled_data.shape[1]
        encoding_dim = max(3, input_dim // 2)

        # Encoder
        input_layer = Input(shape=(input_dim,))
        encoded = Dense(encoding_dim, activation='relu')(input_layer)
        if input_dim > 4:
            encoded = Dense(encoding_dim // 2, activation='relu')(encoded)

        # Decoder
        decoded = Dense(encoding_dim, activation='relu')(encoded)
        if input_dim > 4:
            decoded = Dense(encoding_dim, activation='relu')(decoded)
        decoded = Dense(input_dim, activation='sigmoid')(decoded)

        # Autoencoder model
        autoencoder = Model(input_layer, decoded)
        autoencoder.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

        # Train on normal data (assume most data is normal)
        # For simplicity, use all data but this could be improved with known normal periods
        X_normal = scaled_data

        autoencoder.fit(
            X_normal, X_normal,
            epochs=epochs,
            batch_size=32,
            validation_split=0.1,
            verbose=0,
            shuffle=True
        )

        # Compute reconstruction error
        X_pred = autoencoder.predict(X_normal, verbose=0)
        reconstruction_error = np.mean(np.square(X_normal - X_pred), axis=1)

        # Determine threshold using IQR method
        Q1 = np.percentile(reconstruction_error, 25)
        Q3 = np.percentile(reconstruction_error, 75)
        IQR = Q3 - Q1
        threshold = Q3 + 1.5 * IQR

        # Also use percentile method
        percentile_threshold = np.percentile(reconstruction_error, 100 * (1 - contamination))
        final_threshold = max(threshold, percentile_threshold)

        # Detect anomalies
        anomalies = reconstruction_error > final_threshold
        anomaly_indices = np.where(anomalies)[0]

        # Get data indices (accounting for dropna)
        data_indices = data.index.tolist()

        # Detected anomaly details
        detected_anomalies = []
        for idx in anomaly_indices:
            if idx < len(data_indices):
                date_idx = data_indices[idx]
                detected_anomalies.append({
                    'date': str(date_idx) if hasattr(date_idx, '__str__') else date_idx,
                    'reconstruction_error': float(reconstruction_error[idx]),
                    'values': {feat: float(data.iloc[idx][feat]) for feat in available_features}
                })

        # Sort by reconstruction error (highest first)
        detected_anomalies.sort(key=lambda x: x['reconstruction_error'], reverse=True)

        return {
            'total_samples': len(X_normal),
            'anomalies_detected': int(np.sum(anomalies)),
            'anomaly_ratio': float(np.sum(anomalies) / len(X_normal)),
            'threshold': float(final_threshold),
            'reconstruction_error': {
                'mean': float(np.mean(reconstruction_error)),
                'std': float(np.std(reconstruction_error)),
                'max': float(np.max(reconstruction_error)),
                'min': float(np.min(reconstruction_error))
            },
            'detected_anomalies': detected_anomalies[:20],  # Top 20 anomalies
            'features_used': available_features,
            'model_config': {
                'encoding_dim': max(3, input_dim // 2),
                'epochs': epochs,
                'contamination': contamination
            }
        }

    except ImportError:
        return {'error': 'TensorFlow not installed for autoencoder anomaly detection'}
    except Exception as e:
        return {'error': str(e)}


def detect_anomalies(df: pd.DataFrame) -> dict:
    """
    Detect price and volume anomalies using statistical methods

    Returns:
        Dict with detected anomalies and alerts
    """
    anomalies = []

    # Price anomaly detection
    returns = df['Close'].pct_change()
    mean_return = returns.rolling(50).mean()
    std_return = returns.rolling(50).std()

    # Z-score for last return
    last_return = returns.iloc[-1]
    z_score = (last_return - mean_return.iloc[-1]) / std_return.iloc[-1]

    if abs(z_score) > 2:
        direction = 'positive' if z_score > 0 else 'negative'
        anomalies.append({
            'type': 'Price Anomaly',
            'description': f'Unusual {direction} move ({z_score:.1f} std)',
            'severity': 'High' if abs(z_score) > 3 else 'Medium',
            'value': last_return * 100
        })

    # Volume anomaly detection
    volume_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
    if volume_ratio > 3:
        anomalies.append({
            'type': 'Volume Spike',
            'description': f'Volume {volume_ratio:.1f}x above average',
            'severity': 'High' if volume_ratio > 5 else 'Medium',
            'value': volume_ratio
        })
    elif volume_ratio < 0.3:
        anomalies.append({
            'type': 'Volume Dry-up',
            'description': f'Volume only {volume_ratio:.1%} of average',
            'severity': 'Medium',
            'value': volume_ratio
        })

    # Gap detection
    gap = (df['Open'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
    if abs(gap) > 2:
        direction = 'up' if gap > 0 else 'down'
        anomalies.append({
            'type': f'Gap {direction.capitalize()}',
            'description': f'{abs(gap):.1f}% gap {direction}',
            'severity': 'High' if abs(gap) > 4 else 'Medium',
            'value': gap
        })

    # Volatility expansion
    current_atr = df.get('ATR_14', pd.Series([0])).iloc[-1]
    avg_atr = df.get('ATR_14', pd.Series([0])).rolling(50).mean().iloc[-1]
    if current_atr > avg_atr * 2:
        anomalies.append({
            'type': 'Volatility Expansion',
            'description': 'ATR doubled from average',
            'severity': 'Medium',
            'value': current_atr / avg_atr
        })

    return {
        'anomalies': anomalies,
        'total_alerts': len(anomalies),
        'highest_severity': max([a['severity'] for a in anomalies], default='None')
    }