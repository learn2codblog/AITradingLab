"""
Zerodha Integration Module
Allows seamless integration with Zerodha Kite trading API
Supports authentication, portfolio management, and order placement
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


# ══════════════════════════════════════════════════════════════════════
# ZERODHA AUTHENTICATION & SESSION MANAGEMENT
# ══════════════════════════════════════════════════════════════════════

class ZerodhaAuthenticator:
    """
    Handles Zerodha OAuth authentication flow
    Manages tokens and session persistence
    """
    
    def __init__(self, api_key: str, api_secret: str,
                 redirect_url: str = "http://localhost:8000/"):
        """
        Initialize Zerodha authenticator
        
        Args:
            api_key: Your Zerodha API key
            api_secret: Your Zerodha API secret
            redirect_url: OAuth redirect URL (must match Zerodha dashboard)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.redirect_url = redirect_url
        self.kite = None
        self.access_token = None
        self.user_id = None
        
        self._initialize_kite()
    
    def _initialize_kite(self):
        """Initialize KiteConnect client"""
        try:
            from kiteconnect import KiteConnect
            self.kite = KiteConnect(api_key=self.api_key)
        except ImportError:
            print("Warning: kiteconnect not installed. Install with: pip install kiteconnect")
            self.kite = None
    
    def get_login_url(self) -> Optional[str]:
        """
        Generate Zerodha login URL for OAuth
        
        Returns:
            Login URL string or None if KiteConnect not available
        """
        if self.kite is None:
            return None
        
        return self.kite.login_url()
    
    def set_access_token(self, request_token: str) -> Dict:
        """
        Exchange request token for access token
        
        Args:
            request_token: Request token from Zerodha login
        
        Returns:
            Dict with user info and access token
        """
        if self.kite is None:
            return {'error': 'KiteConnect not initialized'}
        
        try:
            # Get access token
            data = self.kite.generate_session(request_token, self.api_secret)
            
            # Store tokens and user info
            self.access_token = data['access_token']
            self.user_id = data['user_id']
            
            # Set authorization
            self.kite.set_access_token(self.access_token)
            
            return {
                'success': True,
                'user_id': data['user_id'],
                'email': data.get('email', ''),
                'user_name': data.get('user_name', ''),
                'broker': data.get('broker', ''),
                'access_token': self.access_token
            }
        except Exception as e:
            return {'error': str(e)}
    
    def save_session(self, filepath: str = '.zerodha_session'):
        """Save access token to file for session persistence"""
        if self.access_token is None:
            return False
        
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    'access_token': self.access_token,
                    'user_id': self.user_id,
                    'timestamp': datetime.now().isoformat()
                }, f)
            return True
        except Exception as e:
            print(f"Failed to save session: {str(e)}")
            return False
    
    def load_session(self, filepath: str = '.zerodha_session') -> bool:
        """Load saved access token from file"""
        try:
            if not os.path.exists(filepath):
                return False
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.access_token = data.get('access_token')
            self.user_id = data.get('user_id')
            
            # Validate token is still valid (refresh if needed)
            if self.kite and self.access_token:
                self.kite.set_access_token(self.access_token)
            
            return True
        except Exception as e:
            print(f"Failed to load session: {str(e)}")
            return False


# ══════════════════════════════════════════════════════════════════════
# ZERODHA API WRAPPER
# ══════════════════════════════════════════════════════════════════════

class ZerodhaKite:
    """
    Wrapper for Zerodha Kite API
    Provides high-level methods for trading operations
    """
    
    def __init__(self, authenticator: ZerodhaAuthenticator):
        """
        Initialize Zerodha Kite wrapper
        
        Args:
            authenticator: ZerodhaAuthenticator instance
        """
        self.auth = authenticator
        self.kite = authenticator.kite
    
    def get_profile(self) -> Dict:
        """Get user profile information"""
        if self.kite is None:
            return {'error': 'KiteConnect not initialized'}
        
        try:
            profile = self.kite.profile()
            return {
                'user_id': profile.get('user_id'),
                'user_name': profile.get('user_name'),
                'email': profile.get('email'),
                'broker': profile.get('broker'),
                'exchanges': profile.get('exchanges', []),
                'products': profile.get('products', []),
                'order_types': profile.get('order_types', [])
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_holdings(self) -> Optional[List[Dict]]:
        """
        Get current stock holdings
        
        Returns:
            List of holdings or None if error
        """
        if self.kite is None:
            return None
        
        try:
            holdings = self.kite.holdings()
            
            # Process holdings
            processed = []
            for holding in holdings:
                processed.append({
                    'symbol': holding.get('tradingsymbol'),
                    'exchange': holding.get('exchange'),
                    'quantity': holding.get('quantity'),
                    't1_quantity': holding.get('t1_quantity'),
                    'average_price': holding.get('average_price'),
                    'last_price': holding.get('last_price'),
                    'pnl': holding.get('pnl'),
                    'pnl_percent': holding.get('pnl') / (
                        holding.get('average_price') * holding.get('quantity')
                    ) * 100 if holding.get('quantity') > 0 else 0
                })
            
            return processed
        except Exception as e:
            print(f"Error fetching holdings: {str(e)}")
            return None
    
    def get_positions(self) -> Optional[List[Dict]]:
        """
        Get current open positions (derivatives)
        
        Returns:
            List of positions or None if error
        """
        if self.kite is None:
            return None
        
        try:
            positions_data = self.kite.positions()
            
            # Separate intraday and overnight
            net_positions = positions_data.get('net', [])
            processed = []
            
            for position in net_positions:
                processed.append({
                    'symbol': position.get('tradingsymbol'),
                    'exchange': position.get('exchange'),
                    'quantity': position.get('quantity'),
                    'average_price': position.get('average_price'),
                    'last_price': position.get('last_price'),
                    'pnl': position.get('pnl'),
                    'pnl_percent': position.get('pnl_percent'),
                    'multiplier': position.get('multiplier')
                })
            
            return processed
        except Exception as e:
            print(f"Error fetching positions: {str(e)}")
            return None
    
    def get_margins(self) -> Dict:
        """
        Get account margin information
        
        Returns:
            Dict with margin details
        """
        if self.kite is None:
            return {'error': 'KiteConnect not initialized'}
        
        try:
            margins = self.kite.margins()
            
            # Extract equity margins
            equity = margins.get('equity', {})
            
            return {
                'available_cash': equity.get('available', 0),
                'used': equity.get('utilised', 0),
                'opening_balance': equity.get('opening_balance', 0),
                'net': equity.get('net', 0),
                'margin_utilization': (
                    equity.get('utilised', 0) / equity.get('net', 1)
                ) * 100 if equity.get('net', 0) > 0 else 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    def place_order(self, symbol: str, exchange: str = 'NSE',
                   transaction_type: str = 'BUY',
                   quantity: int = 1,
                   order_type: str = 'MARKET',
                   price: float = None,
                   product: str = 'MIS') -> Dict:
        """
        Place a trading order
        
        Args:
            symbol: Trading symbol (e.g., 'INFY', 'SBIN')
            exchange: Exchange (NSE, BSE, etc.)
            transaction_type: BUY or SELL
            quantity: Number of shares
            order_type: MARKET, LIMIT, STOP, STOPLIMIT
            price: Price for limit orders
            product: MIS (intraday), CNC (delivery), NRML (margin)
        
        Returns:
            Dict with order details or error
        """
        if self.kite is None:
            return {'error': 'KiteConnect not initialized'}
        
        try:
            full_symbol = f'{exchange}:{symbol}'
            
            order_params = {
                'tradingsymbol': symbol,
                'exchange': exchange,
                'transaction_type': transaction_type,
                'quantity': quantity,
                'order_type': order_type,
                'product': product
            }
            
            # Add price for limit orders
            if order_type in ['LIMIT', 'STOPLIMIT'] and price:
                order_params['price'] = price
            
            # Place order
            order_id = self.kite.place_order(**order_params)
            
            return {
                'success': True,
                'order_id': order_id,
                'symbol': symbol,
                'exchange': exchange,
                'transaction_type': transaction_type,
                'quantity': quantity,
                'order_type': order_type,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def cancel_order(self, order_id: str) -> Dict:
        """
        Cancel an open order
        
        Args:
            order_id: Order ID to cancel
        
        Returns:
            Dict with result
        """
        if self.kite is None:
            return {'error': 'KiteConnect not initialized'}
        
        try:
            self.kite.cancel_order(order_id, variety='regular')
            return {
                'success': True,
                'order_id': order_id,
                'message': 'Order cancelled successfully'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_order_history(self, order_id: str = None) -> Optional[List[Dict]]:
        """
        Get order history
        
        Args:
            order_id: Specific order ID (optional)
        
        Returns:
            List of orders or None
        """
        if self.kite is None:
            return None
        
        try:
            if order_id:
                orders = self.kite.order_history(order_id)
            else:
                orders = self.kite.orders()
            
            processed = []
            for order in orders if isinstance(orders, list) else [orders]:
                processed.append({
                    'order_id': order.get('order_id'),
                    'symbol': order.get('tradingsymbol'),
                    'exchange': order.get('exchange'),
                    'transaction_type': order.get('transaction_type'),
                    'quantity': order.get('quantity'),
                    'filled_quantity': order.get('filled_quantity'),
                    'average_price': order.get('average_price'),
                    'status': order.get('status'),
                    'timestamp': order.get('order_timestamp')
                })
            
            return processed
        except Exception as e:
            print(f"Error fetching order history: {str(e)}")
            return None


# ══════════════════════════════════════════════════════════════════════
# AUTOMATED TRADING EXECUTOR
# ══════════════════════════════════════════════════════════════════════

class AutomatedTrader:
    """
    Execute trades based on signals from AI models
    Includes risk management and position sizing
    """
    
    def __init__(self, kite_wrapper: ZerodhaKite,
                 risk_percent: float = 2.0,
                 max_position_size: int = 100):
        """
        Initialize automated trader
        
        Args:
            kite_wrapper: ZerodhaKite instance
            risk_percent: Max percentage risk per trade
            max_position_size: Max shares per position
        """
        self.kite = kite_wrapper
        self.risk_percent = risk_percent
        self.max_position_size = max_position_size
    
    def calculate_position_size(self, symbol: str, 
                               stop_loss_pct: float = 2.0,
                               entry_price: float = None) -> int:
        """
        Calculate position size based on risk
        
        Args:
            symbol: Trading symbol
            stop_loss_pct: Stop loss percentage
            entry_price: Entry price (if None, uses market price)
        
        Returns:
            Calculated position size
        """
        # Get available margin
        margins = self.kite.get_margins()
        if 'error' in margins:
            return 0
        
        available = margins.get('available_cash', 0)
        
        # Risk amount
        risk_amount = available * (self.risk_percent / 100)
        
        # Position size = Risk / Stop loss distance
        if entry_price and entry_price > 0:
            stop_distance = entry_price * (stop_loss_pct / 100)
            position_size = int(risk_amount / stop_distance)
        else:
            # Conservative estimate
            position_size = int(available / 1000)
        
        # Cap at max position size
        return min(position_size, self.max_position_size)
    
    def execute_signal(self, signal: Dict, 
                      symbol: str,
                      current_price: float,
                      stop_loss_pct: float = 2.0) -> Dict:
        """
        Execute trade based on signal
        
        Args:
            signal: Signal dict with 'recommendation' and 'confidence'
            symbol: Trading symbol
            current_price: Current market price
            stop_loss_pct: Stop loss percentage
        
        Returns:
            Dict with execution result
        """
        recommendation = signal.get('recommendation', 'HOLD').upper()
        confidence = signal.get('confidence', 0)
        
        # Only execute high confidence signals
        if confidence < 60:
            return {'skip': True, 'reason': f'Low confidence ({confidence:.1f}%)'}
        
        # Calculate position size
        qty = self.calculate_position_size(symbol, stop_loss_pct, current_price)
        
        if qty == 0:
            return {'error': 'Insufficient margin for position'}
        
        # Execute trade
        if 'BUY' in recommendation:
            result = self.kite.place_order(
                symbol=symbol,
                transaction_type='BUY',
                quantity=qty,
                order_type='MARKET'
            )
        elif 'SELL' in recommendation:
            result = self.kite.place_order(
                symbol=symbol,
                transaction_type='SELL',
                quantity=qty,
                order_type='MARKET'
            )
        else:
            return {'skip': True, 'reason': 'No valid BUY/SELL signal'}
        
        return {
            **result,
            'position_size': qty,
            'signal_strength': recommendation,
            'confidence': confidence
        }


# ══════════════════════════════════════════════════════════════════════
# PORTFOLIO ANALYZER
# ══════════════════════════════════════════════════════════════════════

def analyze_portfolio(kite: ZerodhaKite) -> Dict:
    """
    Analyze portfolio with positions and margins
    
    Args:
        kite: ZerodhaKite instance
    
    Returns:
        Dict with portfolio analysis
    """
    # Get holdings
    holdings = kite.get_holdings()
    positions = kite.get_positions()
    margins = kite.get_margins()
    
    total_investment = 0
    total_value = 0
    total_pnl = 0
    
    holdings_list = []
    if holdings:
        for h in holdings:
            inv = h['average_price'] * h['quantity']
            total_investment += inv
            total_value += h['last_price'] * h['quantity']
            total_pnl += h['pnl']
            
            holdings_list.append({
                'symbol': h['symbol'],
                'quantity': h['quantity'],
                'avg_price': h['average_price'],
                'current_price': h['last_price'],
                'pnl': h['pnl'],
                'pnl_percent': h['pnl_percent']
            })
    
    return {
        'holdings': holdings_list,
        'positions': positions or [],
        'total_investment': total_investment,
        'total_current_value': total_value,
        'total_pnl': total_pnl,
        'total_return_percent': (total_pnl / total_investment * 100) if total_investment > 0 else 0,
        'available_margin': margins.get('available_cash', 0),
        'margin_utilization': margins.get('margin_utilization', 0),
        'timestamp': datetime.now().isoformat()
    }

