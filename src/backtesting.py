"""
Advanced Backtesting Module
Comprehensive backtesting with realistic trade simulation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class Trade:
    """Represents a single trade"""

    def __init__(self, symbol: str, entry_date, entry_price: float,
                 position_size: int, trade_type: str = "LONG"):
        self.symbol = symbol
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.position_size = position_size
        self.trade_type = trade_type
        self.exit_date = None
        self.exit_price = None
        self.pnl = 0.0
        self.pnl_pct = 0.0
        self.stop_loss = None
        self.take_profit = None
        self.exit_reason = None

    def close(self, exit_date, exit_price: float, reason: str = "SIGNAL"):
        """Close the trade"""
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.exit_reason = reason

        if self.trade_type == "LONG":
            self.pnl = (exit_price - self.entry_price) * self.position_size
            self.pnl_pct = ((exit_price - self.entry_price) / self.entry_price) * 100
        else:  # SHORT
            self.pnl = (self.entry_price - exit_price) * self.position_size
            self.pnl_pct = ((self.entry_price - exit_price) / self.entry_price) * 100

    def to_dict(self) -> Dict:
        """Convert trade to dictionary"""
        return {
            'symbol': self.symbol,
            'type': self.trade_type,
            'entry_date': self.entry_date,
            'entry_price': self.entry_price,
            'exit_date': self.exit_date,
            'exit_price': self.exit_price,
            'position_size': self.position_size,
            'pnl': self.pnl,
            'pnl_pct': self.pnl_pct,
            'exit_reason': self.exit_reason
        }


class BacktestEngine:
    """Advanced backtesting engine with realistic simulation"""

    def __init__(self, initial_capital: float = 100000, commission: float = 0.001):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.commission = commission
        self.trades: List[Trade] = []
        self.open_trades: List[Trade] = []
        self.equity_curve = []
        self.daily_returns = []

    def enter_trade(self, symbol: str, date, price: float,
                   position_size: int, stop_loss: float = None,
                   take_profit: float = None, trade_type: str = "LONG"):
        """Enter a new trade"""
        cost = price * position_size * (1 + self.commission)

        if cost > self.capital:
            return None  # Insufficient capital

        trade = Trade(symbol, date, price, position_size, trade_type)
        trade.stop_loss = stop_loss
        trade.take_profit = take_profit

        self.capital -= cost
        self.open_trades.append(trade)

        return trade

    def exit_trade(self, trade: Trade, date, price: float, reason: str = "SIGNAL"):
        """Exit an existing trade"""
        trade.close(date, price, reason)

        # Calculate proceeds after commission
        proceeds = trade.exit_price * trade.position_size * (1 - self.commission)
        self.capital += proceeds

        # Move from open to closed
        self.open_trades.remove(trade)
        self.trades.append(trade)

        return trade

    def check_stops(self, date, current_prices: Dict[str, float]):
        """Check stop loss and take profit for open trades"""
        trades_to_close = []

        for trade in self.open_trades:
            if trade.symbol not in current_prices:
                continue

            current_price = current_prices[trade.symbol]

            if trade.trade_type == "LONG":
                # Check stop loss
                if trade.stop_loss and current_price <= trade.stop_loss:
                    trades_to_close.append((trade, trade.stop_loss, "STOP_LOSS"))
                # Check take profit
                elif trade.take_profit and current_price >= trade.take_profit:
                    trades_to_close.append((trade, trade.take_profit, "TAKE_PROFIT"))
            else:  # SHORT
                # Check stop loss
                if trade.stop_loss and current_price >= trade.stop_loss:
                    trades_to_close.append((trade, trade.stop_loss, "STOP_LOSS"))
                # Check take profit
                elif trade.take_profit and current_price <= trade.take_profit:
                    trades_to_close.append((trade, trade.take_profit, "TAKE_PROFIT"))

        # Close trades that hit stops
        for trade, price, reason in trades_to_close:
            self.exit_trade(trade, date, price, reason)

    def update_equity(self, date, current_prices: Dict[str, float]):
        """Update equity curve"""
        unrealized_pnl = 0

        for trade in self.open_trades:
            if trade.symbol in current_prices:
                current_price = current_prices[trade.symbol]
                if trade.trade_type == "LONG":
                    unrealized_pnl += (current_price - trade.entry_price) * trade.position_size
                else:
                    unrealized_pnl += (trade.entry_price - current_price) * trade.position_size

        total_equity = self.capital + unrealized_pnl
        self.equity_curve.append({
            'date': date,
            'equity': total_equity,
            'capital': self.capital,
            'unrealized_pnl': unrealized_pnl
        })

    def run_backtest(self, data: pd.DataFrame, signals: pd.Series,
                    stop_loss_pct: float = 0.05, take_profit_pct: float = 0.15,
                    position_size_pct: float = 0.1) -> Dict:
        """
        Run backtest on data with signals

        Parameters:
        -----------
        data : pd.DataFrame
            Price data with OHLC
        signals : pd.Series
            Trading signals (1 for buy, -1 for sell, 0 for hold)
        stop_loss_pct : float
            Stop loss percentage
        take_profit_pct : float
            Take profit percentage
        position_size_pct : float
            Position size as percentage of capital

        Returns:
        --------
        dict : Backtest results
        """
        symbol = data.get('symbol', 'UNKNOWN')

        for i in range(len(data)):
            date = data.index[i]
            close_price = data['Close'].iloc[i]
            signal = signals.iloc[i] if i < len(signals) else 0

            # Check stops for open trades
            self.check_stops(date, {symbol: close_price})

            # Process signals
            if signal == 1 and len(self.open_trades) == 0:  # Buy signal and no open position
                position_value = self.capital * position_size_pct
                position_size = int(position_value / close_price)

                if position_size > 0:
                    stop_loss = close_price * (1 - stop_loss_pct)
                    take_profit = close_price * (1 + take_profit_pct)
                    self.enter_trade(symbol, date, close_price, position_size,
                                   stop_loss, take_profit, "LONG")

            elif signal == -1 and len(self.open_trades) > 0:  # Sell signal and have position
                for trade in list(self.open_trades):
                    if trade.symbol == symbol:
                        self.exit_trade(trade, date, close_price, "SIGNAL")

            # Update equity curve
            self.update_equity(date, {symbol: close_price})

        # Close any remaining open trades at last price
        last_date = data.index[-1]
        last_price = data['Close'].iloc[-1]
        for trade in list(self.open_trades):
            self.exit_trade(trade, last_date, last_price, "END_OF_DATA")

        return self.get_performance_stats()

    def get_performance_stats(self) -> Dict:
        """Calculate comprehensive performance statistics"""
        if len(self.trades) == 0:
            return {'error': 'No trades executed'}

        # Convert trades to DataFrame
        trades_df = pd.DataFrame([t.to_dict() for t in self.trades])

        # Basic stats
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]

        win_rate = len(winning_trades) / len(trades_df) * 100 if len(trades_df) > 0 else 0

        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0

        profit_factor = abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) \
                       if len(losing_trades) > 0 and losing_trades['pnl'].sum() != 0 else 0

        # Equity curve analysis
        equity_df = pd.DataFrame(self.equity_curve)
        if len(equity_df) > 1:
            equity_df['returns'] = equity_df['equity'].pct_change()

            sharpe = self._calculate_sharpe(equity_df['returns'])
            max_dd = self._calculate_max_drawdown(equity_df['equity'])

            # Calculate Calmar Ratio
            annual_return = total_return / (len(equity_df) / 252) if len(equity_df) > 252 else total_return
            calmar = annual_return / abs(max_dd) if max_dd != 0 else 0
        else:
            sharpe = 0
            max_dd = 0
            calmar = 0

        return {
            'total_return_pct': round(total_return, 2),
            'total_trades': len(trades_df),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate_pct': round(win_rate, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'sharpe_ratio': round(sharpe, 2),
            'max_drawdown_pct': round(max_dd, 2),
            'calmar_ratio': round(calmar, 2),
            'final_capital': round(self.capital, 2),
            'trades_df': trades_df,
            'equity_curve': equity_df
        }

    def _calculate_sharpe(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0

        excess_returns = returns - (risk_free_rate / 252)
        if excess_returns.std() == 0:
            return 0

        sharpe = np.sqrt(252) * (excess_returns.mean() / excess_returns.std())
        return sharpe

    def _calculate_max_drawdown(self, equity: pd.Series) -> float:
        """Calculate maximum drawdown"""
        if len(equity) < 2:
            return 0

        cummax = equity.expanding().max()
        drawdown = (equity - cummax) / cummax * 100
        return drawdown.min()


def compare_strategies(results: Dict[str, Dict]) -> pd.DataFrame:
    """
    Compare multiple backtest results

    Parameters:
    -----------
    results : dict
        Dictionary of strategy name to backtest results

    Returns:
    --------
    pd.DataFrame : Comparison table
    """
    comparison = []

    for strategy_name, result in results.items():
        comparison.append({
            'Strategy': strategy_name,
            'Total Return %': result.get('total_return_pct', 0),
            'Sharpe Ratio': result.get('sharpe_ratio', 0),
            'Max Drawdown %': result.get('max_drawdown_pct', 0),
            'Win Rate %': result.get('win_rate_pct', 0),
            'Total Trades': result.get('total_trades', 0),
            'Profit Factor': result.get('profit_factor', 0),
            'Calmar Ratio': result.get('calmar_ratio', 0)
        })

    return pd.DataFrame(comparison).sort_values('Sharpe Ratio', ascending=False)

