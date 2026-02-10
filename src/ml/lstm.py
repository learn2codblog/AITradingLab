"""
LSTM Deep Learning Module for TradeGenius AI
=============================================
Includes:
- LSTM Price Prediction
- Multi-feature LSTM
- MC Dropout for Uncertainty
- Model Building and Training
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')


def prepare_lstm_data(df: pd.DataFrame, lookback: int = 60, forecast_days: int = 5):
    """
    Prepare data for LSTM model

    Args:
        df: DataFrame with price data
        lookback: Number of days to look back
        forecast_days: Number of days to forecast

    Returns:
        X, y arrays for training
    """
    from sklearn.preprocessing import MinMaxScaler

    # Use Close price
    data = df['Close'].values.reshape(-1, 1)

    # Scale data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    X, y = [], []
    for i in range(lookback, len(scaled_data) - forecast_days):
        X.append(scaled_data[i - lookback:i, 0])
        y.append(scaled_data[i:i + forecast_days, 0])

    X = np.array(X)
    y = np.array(y)

    # Reshape for LSTM [samples, time steps, features]
    X = X.reshape((X.shape[0], X.shape[1], 1))

    return X, y, scaler


def build_lstm_model(lookback: int = 60, forecast_days: int = 5, n_features: int = 1,
                     use_mc_dropout: bool = True, model_size: str = 'small'):
    """
    Build enhanced LSTM model for price prediction with MC Dropout and L2 regularization

    Args:
        lookback: Number of timesteps to look back
        forecast_days: Number of days to forecast
        n_features: Number of input features
        use_mc_dropout: If True, use MC Dropout for uncertainty estimation
        model_size: 'small', 'medium', or 'large' architecture

    Returns:
        Compiled Keras model
    """
    try:
        from tensorflow.keras.models import Sequential, Model
        from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization, Input
        from tensorflow.keras.optimizers import Adam
        from tensorflow.keras.regularizers import l2
        import tensorflow as tf

        # Custom Dropout layer that stays active during inference for MC Dropout
        class MCDropout(Dropout):
            def call(self, inputs, training=None):
                return super().call(inputs, training=True)

        dropout_layer = MCDropout if use_mc_dropout else Dropout

        # L2 regularization strength
        l2_reg = 0.001

        # Architecture based on model size (smaller = less overfitting)
        if model_size == 'small':
            units = [32, 16]
            dropout_rate = 0.3
        elif model_size == 'medium':
            units = [64, 32]
            dropout_rate = 0.25
        else:  # large
            units = [128, 64, 32]
            dropout_rate = 0.2

        model = Sequential()

        # First LSTM layer
        model.add(LSTM(units[0], return_sequences=len(units) > 1,
                      input_shape=(lookback, n_features),
                      kernel_regularizer=l2(l2_reg),
                      recurrent_regularizer=l2(l2_reg)))
        model.add(dropout_layer(dropout_rate))
        model.add(BatchNormalization())

        # Middle LSTM layers
        for i, unit in enumerate(units[1:], 1):
            return_seq = i < len(units) - 1
            model.add(LSTM(unit, return_sequences=return_seq,
                          kernel_regularizer=l2(l2_reg),
                          recurrent_regularizer=l2(l2_reg)))
            model.add(dropout_layer(dropout_rate))
            if return_seq:
                model.add(BatchNormalization())

        # Dense layers
        model.add(Dense(32, activation='relu', kernel_regularizer=l2(l2_reg)))
        model.add(dropout_layer(dropout_rate * 0.5))
        model.add(Dense(forecast_days))

        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='huber',  # More robust to outliers than MSE
            metrics=['mae']
        )

        return model

    except ImportError:
        return None


def prepare_lstm_features(df: pd.DataFrame, features: list = None) -> tuple:
    """
    Prepare multi-feature data for LSTM training

    Args:
        df: DataFrame with OHLCV and indicator data
        features: List of feature column names to use

    Returns:
        Tuple of (feature_data, feature_names, close_idx)
    """
    if features is None:
        # Default features - mix of price, momentum, volatility, volume
        default_features = [
            'Close', 'RSI_14', 'MACD', 'ATR_14', 'BB_Percent',
            'Stoch_K', 'ROC', 'MFI', 'Volume_Ratio', 'Momentum'
        ]
        features = [f for f in default_features if f in df.columns]

    # Ensure Close is always first for target prediction
    if 'Close' not in features:
        features = ['Close'] + features
    elif features[0] != 'Close':
        features.remove('Close')
        features = ['Close'] + features

    # Filter to available columns
    available_features = [f for f in features if f in df.columns]

    if len(available_features) < 2:
        available_features = ['Close']

    return df[available_features].copy(), available_features, 0  # close_idx = 0


def predict_with_lstm(df: pd.DataFrame, lookback: int = 60, forecast_days: int = 5,
                      epochs: int = 50, features: list = None,
                      n_mc_samples: int = 30, model_size: str = 'small') -> dict:
    """
    Enhanced LSTM prediction with TimeSeriesSplit, L2 regularization,
    MC Dropout for uncertainty estimation, and overfitting detection.

    Args:
        df: DataFrame with price and indicator data
        lookback: Days to look back (default 60)
        forecast_days: Days to predict (default 5)
        epochs: Maximum training epochs (default 50)
        features: List of feature columns to use (default: auto-select)
        n_mc_samples: Number of MC Dropout samples for uncertainty (default 30)
        model_size: 'small', 'medium', or 'large' (default 'small' to prevent overfitting)

    Returns:
        Dict with predictions, confidence intervals, metrics, and overfitting diagnostics
    """
    try:
        from sklearn.preprocessing import MinMaxScaler
        from sklearn.model_selection import TimeSeriesSplit
        from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

        # Check if we have enough data
        min_required = lookback + forecast_days + 50
        if len(df) < min_required:
            return {'error': f'Insufficient data. Need {min_required} rows, got {len(df)}'}

        # Prepare multi-feature data
        feature_data, feature_names, close_idx = prepare_lstm_features(df, features)
        n_features = len(feature_names)

        # Handle NaN and infinite values
        feature_data = feature_data.copy()
        feature_data.replace([np.inf, -np.inf], np.nan, inplace=True)
        feature_data = feature_data.dropna()
        if len(feature_data) < min_required:
            return {'error': 'Too many NaN or infinite values after feature preparation'}

        # Determine train/val/test split indices BEFORE scaling to prevent data leakage
        raw_data = feature_data.values

        # Create sequences first on raw data to determine split indices
        all_indices = list(range(lookback, len(raw_data) - forecast_days))

        # Use TimeSeriesSplit to get train/val split
        tscv = TimeSeriesSplit(n_splits=3)
        for train_idx, val_idx in tscv.split(all_indices):
            pass  # Get last fold indices

        # Map sequence indices back to raw data indices
        # train_idx refers to indices within all_indices
        train_end_raw = all_indices[train_idx[-1]] + forecast_days  # Last raw index used by training

        # Fit scaler ONLY on training portion of raw data (no data leakage)
        scaler = MinMaxScaler(feature_range=(0, 1))
        # Ensure training portion has finite values
        if not np.isfinite(raw_data[:train_end_raw]).all():
            return {'error': 'Training data contains non-finite values (inf or NaN). Please clean the input data.'}
        scaler.fit(raw_data[:train_end_raw])
        scaled_data = scaler.transform(raw_data)

        # Create sequences with all features, predict only Close
        X, y = [], []
        for i in range(lookback, len(scaled_data) - forecast_days):
            X.append(scaled_data[i - lookback:i])
            y.append(scaled_data[i:i + forecast_days, close_idx])

        X = np.array(X)
        y = np.array(y)

        # Apply the same split
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        # Keep some data for final test (last 10%)
        test_size = max(10, int(len(X_val) * 0.3))
        X_test = X_val[-test_size:]
        y_test = y_val[-test_size:]
        X_val = X_val[:-test_size]
        y_val = y_val[:-test_size]

        # Build model with smaller architecture to prevent overfitting
        model = build_lstm_model(lookback, forecast_days, n_features,
                                use_mc_dropout=True, model_size=model_size)
        if model is None:
            return {'error': 'TensorFlow not installed'}

        # Callbacks for early stopping and learning rate reduction
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                min_delta=0.0001
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=0.0001
            )
        ]

        # Train with validation
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=32,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            verbose=0
        )

        # Prepare last sequence for prediction
        last_sequence = scaled_data[-lookback:].reshape(1, lookback, n_features)

        # MC Dropout: Run multiple predictions for uncertainty estimation
        mc_predictions = []
        for _ in range(n_mc_samples):
            pred = model(last_sequence, training=True)  # training=True keeps dropout active
            mc_predictions.append(pred.numpy()[0])

        mc_predictions = np.array(mc_predictions)

        # Calculate mean prediction and uncertainty
        predicted_scaled_mean = np.mean(mc_predictions, axis=0)
        predicted_scaled_std = np.std(mc_predictions, axis=0)

        # FIXED INVERSE SCALING - use last scaled row as base for proper inverse transform
        last_scaled_row = scaled_data[-1].copy()

        # Inverse transform predictions using correct context
        dummy_mean = np.tile(last_scaled_row, (forecast_days, 1))
        dummy_mean[:, close_idx] = predicted_scaled_mean
        predicted_prices = scaler.inverse_transform(dummy_mean)[:, close_idx]

        # Calculate confidence intervals
        dummy_low = np.tile(last_scaled_row, (forecast_days, 1))
        dummy_low[:, close_idx] = predicted_scaled_mean - 1.96 * predicted_scaled_std
        predicted_low = scaler.inverse_transform(dummy_low)[:, close_idx]

        dummy_high = np.tile(last_scaled_row, (forecast_days, 1))
        dummy_high[:, close_idx] = predicted_scaled_mean + 1.96 * predicted_scaled_std
        predicted_high = scaler.inverse_transform(dummy_high)[:, close_idx]

        # Evaluate on test set (also with fixed inverse scaling)
        if len(X_test) > 0:
            test_pred = model.predict(X_test, verbose=0)
            test_pred_flat = test_pred.flatten()
            y_test_flat = y_test.flatten()

            # Use last timestep of each test sequence as context for inverse transform
            last_timesteps = X_test[:, -1, :]
            dummy_test = np.repeat(last_timesteps, forecast_days, axis=0)
            dummy_test[:, close_idx] = test_pred_flat
            test_pred_inv = scaler.inverse_transform(dummy_test)[:, close_idx]

            dummy_actual = np.repeat(last_timesteps, forecast_days, axis=0)
            dummy_actual[:, close_idx] = y_test_flat
            test_actual_inv = scaler.inverse_transform(dummy_actual)[:, close_idx]

            mae = np.mean(np.abs(test_pred_inv - test_actual_inv))
            mape = np.mean(np.abs((test_actual_inv - test_pred_inv) / test_actual_inv)) * 100
        else:
            mae = 0
            mape = 0

        current_price = df['Close'].iloc[-1]

        # Confidence based on prediction uncertainty and historical accuracy
        uncertainty_ratio = np.mean(predicted_scaled_std) / np.mean(np.abs(predicted_scaled_mean))
        confidence = max(0, min(100, 100 * (1 - uncertainty_ratio) * (1 - mape/100)))

        # Trend direction with strength
        final_predicted = predicted_prices[-1]
        price_change = final_predicted - current_price
        pct_change = (price_change / current_price) * 100

        if pct_change > 3:
            trend = 'Strong Bullish'
        elif pct_change > 1:
            trend = 'Bullish'
        elif pct_change < -3:
            trend = 'Strong Bearish'
        elif pct_change < -1:
            trend = 'Bearish'
        else:
            trend = 'Neutral'

        # Calculate overfitting gap (train MAE - val MAE) / val MAE
        train_mae = history.history['mae'][-1] if 'mae' in history.history else 0
        val_mae = history.history['val_mae'][-1] if 'val_mae' in history.history else train_mae
        overfitting_gap = ((train_mae - val_mae) / val_mae * 100) if val_mae > 0 else 0

        # Determine if model is overfitting
        if overfitting_gap > 20:
            overfitting_status = 'High Risk - Consider smaller model'
        elif overfitting_gap > 10:
            overfitting_status = 'Moderate - Monitor closely'
        elif overfitting_gap > 0:
            overfitting_status = 'Low - Model generalizes well'
        else:
            overfitting_status = 'Good - Validation better than training'

        return {
            'current_price': float(current_price),
            'predictions': predicted_prices.tolist(),
            'prediction_low': predicted_low.tolist(),
            'prediction_high': predicted_high.tolist(),
            'forecast_days': forecast_days,
            'trend': trend,
            'expected_return': float(pct_change),
            'confidence': float(confidence),
            'mae': float(mae),
            'mape': float(mape),
            'uncertainty': float(np.mean(predicted_scaled_std)),
            'features_used': feature_names,
            'n_features': n_features,
            'model_size': model_size,
            'epochs_trained': len(history.history['loss']),
            'final_loss': float(history.history['loss'][-1]),
            'final_val_loss': float(history.history['val_loss'][-1]) if 'val_loss' in history.history else None,
            'train_mae': float(train_mae),
            'val_mae': float(val_mae),
            'overfitting_gap_pct': float(overfitting_gap),
            'overfitting_status': overfitting_status
        }

    except ImportError as e:
        return {'error': f'Missing dependency: {str(e)}'}
    except Exception as e:
        return {'error': str(e)}