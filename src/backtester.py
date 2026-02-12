"""
Backtesting Engine for Trading Signals
Provides both Backtrader integration and pandas-based walk-forward testing
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, Dict, List, Callable
import warnings
warnings.filterwarnings('ignore')


# ══════════════════════════════════════════════════════════════════════
# PANDAS-BASED BACKTESTER (Simple, no external dependencies)
# ══════════════════════════════════════════════════════════════════════

class SimpleBacktester:
    """
    Simple pandas-based backtester for strategy signals
    No heavy dependencies, lightweight and fast
    """
    
    def __init__(self, initial_capital: float = 100000, commission: float = 0.001,
                 slippage: float = 0.0005):
        """
        Initialize backtester
        
        Args:
            initial_capital: Starting capital
            commission: Trading commission (0.1% = 0.001)
            slippage: Price slippage per trade
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
    def backtest(self, df: pd.DataFrame, signals: pd.Series, 
                 position_type: str = 'long') -> Dict:
        """
        Run backtest on signals
        
        Args:
            df: DataFrame with OHLCV data
            signals: Series with 1 (buy), -1 (sell), 0 (hold)
            position_type: 'long' or 'long_short'
        
        Returns:
            Dict with backtest results
        """
        df = df.copy()
        signals = signals.copy()
        
        # Ensure alignment
        common_idx = df.index.intersection(signals.index)
        df = df.loc[common_idx]
        signals = signals.loc[common_idx]
        
        # Initialize tracking
        cash = self.initial_capital
        position = 0
        position_price = 0
        equity_curve = [self.initial_capital]
        trades = []
        
        for i in range(len(df)):
            date = df.index[i]
            price = df['Close'].iloc[i]
            signal = signals.iloc[i]
            
            # Skip NaN signals
            if pd.isna(signal):
                signal = 0
            
            # Process signal
            if signal == 1 and position == 0:  # Buy signal
                # Calculate position size
                entry_price = price * (1 + self.slippage)
                shares = int((cash * 0.95) / entry_price)  # Use 95% of capital
                
                if shares > 0:
                    cost = shares * entry_price * (1 + self.commission)
                    cash -= cost
                    position = shares
                    position_price = entry_price
                    
                    trades.append({
                        'date': date,
                        'type': 'BUY',
                        'price': entry_price,
                        'shares': shares,
                        'value': shares * entry_price
                    })
            
            elif signal == -1 and position > 0:  # Sell signal
                # Close position
                exit_price = price * (1 - self.slippage)
                proceeds = position * exit_price * (1 - self.commission)
                profit = proceeds - (position * position_price)
                
                cash += proceeds
                
                trades.append({
                    'date': date,
                    'type': 'SELL',
                    'price': exit_price,
                    'shares': position,
                    'value': proceeds,
                    'profit': profit
                })
                
                position = 0
                position_price = 0
            
            # Update equity
            current_equity = cash + (position * price if position > 0 else 0)
            equity_curve.append(current_equity)
        
        # Close any open position
        if position > 0:
            exit_price = df['Close'].iloc[-1]
            cash += position * exit_price * (1 - self.commission)
        
        final_equity = cash + (position * df['Close'].iloc[-1] if position > 0 else 0)
        
        # Calculate metrics
        equity_curve = np.array(equity_curve)
        returns = np.diff(equity_curve) / equity_curve[:-1]
        
        total_return = (final_equity - self.initial_capital) / self.initial_capital
        annual_return = total_return * (252 / len(df))
        
        # Sharpe ratio (annualized)
        if len(returns) > 0 and np.std(returns) > 0:
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)
        else:
            sharpe = 0
        
        # Maximum drawdown
        max_equity = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - max_equity) / max_equity
        max_drawdown = np.min(drawdown)
        
        # Win rate
        profitable_trades = sum(1 for t in trades if t.get('profit', 0) > 0)
        win_rate = profitable_trades / len(trades) if trades else 0
        
        # Trade statistics
        trade_profits = [t.get('profit', 0) for t in trades if 'profit' in t]
        avg_profit = np.mean(trade_profits) if trade_profits else 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return_pct': total_return * 100,
            'annual_return_pct': annual_return * 100,
            'sharpe_ratio': sharpe,
            'max_drawdown_pct': max_drawdown * 100,
            'num_trades': len(trades),
            'profitable_trades': profitable_trades,
            'win_rate_pct': win_rate * 100,
            'avg_profit_per_trade': avg_profit,
            'equity_curve': equity_curve.tolist(),
            'trades': trades,
            'metrics': {
                'profit_factor': self._calculate_profit_factor(trade_profits),
                'recovery_factor': final_equity / (self.initial_capital * 0.5) if max_drawdown != 0 else 0,
                'calmar_ratio': annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
            }
        }
    
    @staticmethod
    def _calculate_profit_factor(profits: List[float]) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        gains = sum(p for p in profits if p > 0)
        losses = abs(sum(p for p in profits if p < 0))
        return gains / losses if losses > 0 else 0


class WalkForwardBacktester:
    """
    Walk-forward analysis for more robust backtesting
    Trains on past data, tests on future data
    """
    
    def __init__(self, initial_capital: float = 100000,
                 train_period: int = 100,
                 test_period: int = 20):
        """
        Initialize walk-forward backtester
        
        Args:
            initial_capital: Starting capital
            train_period: Number of days for training period
            test_period: Number of days for test period
        """
        self.initial_capital = initial_capital
        self.train_period = train_period
        self.test_period = test_period
        self.backtester = SimpleBacktester(initial_capital)
    
    def backtest_walk_forward(self, df: pd.DataFrame, 
                             signal_generator: Callable) -> Dict:
        """
        Run walk-forward backtest
        
        Args:
            df: DataFrame with price data
            signal_generator: Function that generates signals given dataframe
                            Returns Series with 1, -1, 0 signals
        
        Returns:
            Dict with walk-forward results
        """
        df = df.copy().dropna()
        
        if len(df) < self.train_period + self.test_period:
            return {'error': 'Insufficient data for walk-forward test'}
        
        all_trades = []
        all_equity_curves = []
        fold_results = []
        
        # Walk-forward loop
        start_idx = 0
        fold = 0
        
        while start_idx + self.train_period + self.test_period <= len(df):
            fold += 1
            
            # Train period
            train_start = start_idx
            train_end = start_idx + self.train_period
            df_train = df.iloc[train_start:train_end]
            
            # Test period
            test_start = train_end
            test_end = train_end + self.test_period
            df_test = df.iloc[test_start:test_end]
            
            try:
                # Generate signals for test period
                signals_test = signal_generator(df_test)
                
                # Run backtest on test period
                result = self.backtester.backtest(df_test, signals_test)
                
                # Store results
                all_trades.extend(result.get('trades', []))
                all_equity_curves.append(result['equity_curve'])
                
                fold_results.append({
                    'fold': fold,
                    'test_start_date': df_test.index[0],
                    'test_end_date': df_test.index[-1],
                    'return_pct': result['total_return_pct'],
                    'sharpe': result['sharpe_ratio'],
                    'max_drawdown_pct': result['max_drawdown_pct']
                })
                
            except Exception as e:
                print(f"Error in fold {fold}: {str(e)}")
                continue
            
            # Move walk-forward window
            start_idx += self.test_period
        
        # Aggregate results
        fold_returns = [fr['return_pct'] for fr in fold_results]
        fold_sharpes = [fr['sharpe'] for fr in fold_results]
        
        return {
            'num_folds': len(fold_results),
            'fold_results': fold_results,
            'avg_return_pct': np.mean(fold_returns) if fold_returns else 0,
            'avg_sharpe': np.mean(fold_sharpes) if fold_sharpes else 0,
            'std_return_pct': np.std(fold_returns) if fold_returns else 0,
            'total_trades': len(all_trades),
            'trades': all_trades
        }


# ══════════════════════════════════════════════════════════════════════
# STRATEGY SIGNAL GENERATORS
# ══════════════════════════════════════════════════════════════════════

def generate_ma_crossover_signals(df: pd.DataFrame, 
                                  fast_period: int = 20,
                                  slow_period: int = 50) -> pd.Series:
    """
    Simple moving average crossover strategy
    
    Args:
        df: DataFrame with Close price
        fast_period: Fast MA period
        slow_period: Slow MA period
    
    Returns:
        Series with signals (1=buy, -1=sell, 0=hold)
    """
    df = df.copy()
    
    # Calculate MAs
    df['SMA_fast'] = df['Close'].rolling(fast_period).mean()
    df['SMA_slow'] = df['Close'].rolling(slow_period).mean()
    
    # Generate signals
    signals = pd.Series(0, index=df.index)
    signals[df['SMA_fast'] > df['SMA_slow']] = 1  # Buy signal
    signals[df['SMA_fast'] < df['SMA_slow']] = -1  # Sell signal
    
    return signals


def generate_rsi_signals(df: pd.DataFrame, 
                        period: int = 14,
                        oversold: float = 30,
                        overbought: float = 70) -> pd.Series:
    """
    RSI-based trading strategy
    
    Args:
        df: DataFrame with Close price
        period: RSI period
        oversold: Oversold threshold (default 30)
        overbought: Overbought threshold (default 70)
    
    Returns:
        Series with signals
    """
    df = df.copy()
    
    # Calculate RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # Generate signals
    signals = pd.Series(0, index=df.index)
    signals[rsi < oversold] = 1  # Buy oversold
    signals[rsi > overbought] = -1  # Sell overbought
    
    return signals


def generate_macd_signals(df: pd.DataFrame,
                         fast: int = 12,
                         slow: int = 26,
                         signal_period: int = 9) -> pd.Series:
    """
    MACD-based trading strategy
    
    Args:
        df: DataFrame with Close price
        fast: Fast EMA period
        slow: Slow EMA period
        signal_period: Signal line period
    
    Returns:
        Series with signals
    """
    df = df.copy()
    
    # Calculate MACD
    ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal_period, adjust=False).mean()
    
    # Generate signals
    signals = pd.Series(0, index=df.index)
    signals[macd > signal_line] = 1  # Buy when MACD > signal
    signals[macd < signal_line] = -1  # Sell when MACD < signal
    
    return signals


# ══════════════════════════════════════════════════════════════════════
# BACKTRADER INTEGRATION (if available)
# ══════════════════════════════════════════════════════════════════════

def backtest_with_backtrader(df: pd.DataFrame, strategy_class,
                            initial_cash: float = 100000) -> Dict:
    """
    Run backtest using Backtrader
    
    Args:
        df: DataFrame with OHLCV data
        strategy_class: Backtrader strategy class
        initial_cash: Starting cash
    
    Returns:
        Dict with backtest results
    """
    try:
        import backtrader as bt
        
        class DataFeed(bt.DataBase):
            """Custom Backtrader data feed"""
            params = (('dtformat', '%Y-%m-%d'),)
            
            def _load(self):
                if self.idx >= len(self.df):
                    return False
                
                row = self.df.iloc[self.idx]
                self.lines.datetime.array[len(self)] = bt.date2num(row.name)
                self.lines.open[len(self)] = row['Open']
                self.lines.high[len(self)] = row['High']
                self.lines.low[len(self)] = row['Low']
                self.lines.close[len(self)] = row['Close']
                self.lines.volume[len(self)] = row.get('Volume', 0)
                self.lines.openinterest[len(self)] = 0
                
                self.idx += 1
                return True
        
        # Prepare data
        cerebro = bt.Cerebro()
        cerebro.addstrategy(strategy_class)
        cerebro.broker.setcash(initial_cash)
        
        # Add data
        data = backtrader.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        
        # Run
        results = cerebro.run()
        final_value = cerebro.broker.getvalue()
        
        return {
            'initial_cash': initial_cash,
            'final_value': final_value,
            'return_pct': (final_value - initial_cash) / initial_cash * 100
        }
        
    except ImportError:
        return {'error': 'Backtrader not installed. Use: pip install backtrader'}
    except Exception as e:
        return {'error': str(e)}

