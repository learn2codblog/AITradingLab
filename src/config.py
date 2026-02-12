"""
Configuration Loader for TradeGenius AI
Loads settings from config.yaml with sensible defaults
"""

import os
import logging

logger = logging.getLogger(__name__)

# Default configuration (used if config.yaml is missing)
_DEFAULTS = {
    'market': {
        'risk_free_rate': 0.05,
        'trading_days_per_year': 252,
        'default_period': '3y',
        'min_data_points': 100,
        'min_data_points_basic': 30,
    },
    'indicators': {
        'rsi_period': 14,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'bollinger_period': 20,
        'bollinger_std': 2,
        'atr_period': 14,
        'stochastic_period': 14,
        'adx_period': 14,
        'cci_period': 20,
        'roc_period': 10,
        'mfi_period': 14,
    },
    'supertrend': {
        'period': 10,
        'multiplier': 2.0,
    },
    'ml': {
        'random_forest': {'n_estimators': 100, 'max_depth': 10, 'min_samples_split': 5, 'min_samples_leaf': 2},
        'xgboost': {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.1},
        'ensemble': {'test_size': 0.2, 'quick_test_size': 0.1, 'deep_test_size': 0.3},
        'lstm': {'lookback': 60, 'forecast_days': 5, 'epochs': 50, 'batch_size': 32, 'mc_samples': 30, 'model_size': 'small'},
    },
    'signals': {
        'rsi_overbought': 70,
        'rsi_oversold': 30,
        'rsi_bullish_momentum': 50,
        'adx_strong_trend': 25,
        'volume_high_ratio': 1.5,
        'volume_low_ratio': 0.8,
        'confidence_max': 0.90,
        'signal_conflict_threshold': 0.6,
    },
    'price_targets': {
        'bullish_pullback_min': 0.02,
        'bullish_pullback_max': 0.05,
        'bearish_pullback_min': 0.03,
        'bearish_pullback_max': 0.08,
        'stop_loss_buffer': 0.03,
    },
    'portfolio': {
        'max_weight': 0.30,
        'min_weight': 0.02,
        'optimizer_timeout': 30,
        'risk_free_rate': 0.05,
    },
    'scoring': {
        'quick': {'technical': 0.40, 'regime': 0.25, 'ml': 0.15, 'pattern': 0.20},
        'standard': {'technical': 0.30, 'regime': 0.25, 'ml': 0.25, 'pattern': 0.20},
        'deep': {'technical': 0.20, 'regime': 0.20, 'ml': 0.35, 'pattern': 0.25},
    },
    'logging': {
        'level': 'INFO',
        'file': 'tradegenius.log',
        'max_bytes': 5242880,
        'backup_count': 3,
    },
    'ui': {
        'cache_ttl': 3600,
        'max_stocks_per_scan': 500,
        'default_prediction_days': 5,
    },
}

_config = None


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base dict"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config_path: str = None) -> dict:
    """
    Load configuration from YAML file, falling back to defaults.

    Args:
        config_path: Path to config.yaml (auto-detected if None)

    Returns:
        Configuration dictionary
    """
    global _config
    if _config is not None:
        return _config

    config = _DEFAULTS.copy()

    # Try to find config.yaml
    if config_path is None:
        candidates = [
            'config.yaml',
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml'),
        ]
        for path in candidates:
            if os.path.exists(path):
                config_path = path
                break

    if config_path and os.path.exists(config_path):
        try:
            import yaml
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f) or {}
            config = _deep_merge(_DEFAULTS, file_config)
            logger.info(f"Configuration loaded from {config_path}")
        except ImportError:
            logger.warning("PyYAML not installed. Using default configuration.")
        except Exception as e:
            logger.warning(f"Error loading config from {config_path}: {e}. Using defaults.")
    else:
        logger.info("No config.yaml found. Using default configuration.")

    _config = config
    return config


def get(section: str, key: str = None, default=None):
    """
    Get a configuration value.

    Args:
        section: Top-level section (e.g., 'market', 'ml')
        key: Key within section (e.g., 'risk_free_rate'). If None, returns entire section.
        default: Default value if key not found

    Returns:
        Configuration value
    """
    config = load_config()
    section_data = config.get(section, {})

    if key is None:
        return section_data

    if isinstance(section_data, dict):
        return section_data.get(key, default)

    return default


def reload():
    """Force reload of configuration"""
    global _config
    _config = None
    return load_config()
