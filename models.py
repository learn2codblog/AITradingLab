# models.py
"""
Machine Learning Models for Trading Signal Generation
Enhanced with better hyperparameters and feature support
"""

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import xgboost as xgb
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam


def train_random_forest(X_train, y_train, n_estimators: int = 500, max_depth: int = 15):
    """
    Train Random Forest classifier with balanced class weights
    
    Args:
        X_train: Training features
        y_train: Training labels
        n_estimators: Number of trees
        max_depth: Maximum tree depth
        
    Returns:
        Trained RandomForestClassifier
    """
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features='sqrt',
        class_weight='balanced',
        n_jobs=-1,
        random_state=42,
        verbose=0
    )
    model.fit(X_train, y_train)
    return model


def train_xgboost(X_train, y_train, n_estimators: int = 500, max_depth: int = 8, learning_rate: float = 0.05):
    """
    Train XGBoost classifier with optimized hyperparameters
    
    Args:
        X_train: Training features
        y_train: Training labels
        n_estimators: Number of boosting rounds
        max_depth: Maximum tree depth
        learning_rate: Learning rate for boosting
        
    Returns:
        Trained XGBClassifier
    """
    model = xgb.XGBClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        subsample=0.8,
        colsample_bytree=0.8,
        colsample_bylevel=0.9,
        min_child_weight=1,
        gamma=0.5,
        reg_alpha=0.1,
        reg_lambda=1.0,
        scale_pos_weight=1,
        eval_metric='logloss',
        tree_method='hist',
        random_state=42,
        n_jobs=-1,
        verbosity=0
    )
    model.fit(X_train, y_train)
    return model


def train_gradient_boosting(X_train, y_train, n_estimators: int = 500, learning_rate: float = 0.05):
    """
    Train Gradient Boosting classifier
    
    Args:
        X_train: Training features
        y_train: Training labels
        n_estimators: Number of boosting stages
        learning_rate: Shrinkage parameter
        
    Returns:
        Trained GradientBoostingClassifier
    """
    model = GradientBoostingClassifier(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=6,
        min_samples_split=5,
        min_samples_leaf=2,
        subsample=0.8,
        random_state=42,
        verbose=0
    )
    model.fit(X_train, y_train)
    return model


def build_lstm_model(input_shape, lstm_units: int = 128, dropout_rate: float = 0.3):
    """
    Build LSTM deep learning model for sequence prediction
    
    Args:
        input_shape: Shape of input sequences (sequence_length, n_features)
        lstm_units: Number of LSTM units in first layer
        dropout_rate: Dropout rate for regularization
        
    Returns:
        Compiled Keras Sequential model
    """
    model = Sequential([
        LSTM(lstm_units, return_sequences=True, input_shape=input_shape),
        BatchNormalization(),
        Dropout(dropout_rate),
        
        LSTM(lstm_units // 2, return_sequences=False),
        BatchNormalization(),
        Dropout(dropout_rate),
        
        Dense(64, activation='relu'),
        BatchNormalization(),
        Dropout(dropout_rate * 0.8),
        
        Dense(32, activation='relu'),
        Dropout(dropout_rate * 0.5),
        
        Dense(1, activation='sigmoid')
    ])
    
    optimizer = Adam(learning_rate=0.001)
    model.compile(
        optimizer=optimizer,
        loss='binary_crossentropy',
        metrics=['accuracy', 'AUC']
    )
    return model


def build_dense_model(input_dim: int):
    """
    Build dense neural network for feature-based prediction
    
    Args:
        input_dim: Number of input features
        
    Returns:
        Compiled Keras Sequential model
    """
    model = Sequential([
        Dense(256, activation='relu', input_dim=input_dim),
        BatchNormalization(),
        Dropout(0.3),
        
        Dense(128, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        
        Dense(64, activation='relu'),
        BatchNormalization(),
        Dropout(0.2),
        
        Dense(32, activation='relu'),
        Dropout(0.2),
        
        Dense(1, activation='sigmoid')
    ])
    
    optimizer = Adam(learning_rate=0.001)
    model.compile(
        optimizer=optimizer,
        loss='binary_crossentropy',
        metrics=['accuracy', 'AUC']
    )
    return model
