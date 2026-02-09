"""
AI Trading Lab - Advanced Stock Analysis and Portfolio Optimization Platform
"""

__version__ = "2.0.0"
__author__ = "AI Trading Lab Team"

# Core modules
from . import data_loader
from . import feature_engineering
from . import fundamental_analysis
from . import metrics
from . import models
from . import portfolio_optimizer
from . import price_targets
from . import price_targets_enhanced
from . import technical_indicators
from . import utils
from . import stock_universe

# New enhanced modules
from . import config
from . import risk_management
from . import backtesting
from . import signal_generator

__all__ = [
    'data_loader',
    'feature_engineering',
    'fundamental_analysis',
    'metrics',
    'models',
    'portfolio_optimizer',
    'price_targets',
    'price_targets_enhanced',
    'technical_indicators',
    'utils',
    'stock_universe',
    'config',
    'risk_management',
    'backtesting',
    'signal_generator',
]

