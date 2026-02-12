"""
Email Alert Module
Sends trading signal alerts via Gmail
Free alternative to commercial alert services like Twilio
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
import json
import os
import warnings
warnings.filterwarnings('ignore')


# ══════════════════════════════════════════════════════════════════════
# GMAIL CONFIGURATION
# ══════════════════════════════════════════════════════════════════════

class EmailAlertConfig:
    """Manage email alert configuration"""
    
    def __init__(self, config_file: str = '.email_config.json'):
        """
        Initialize email config
        
        Args:
            config_file: Path to config file (will create if not exists)
        """
        self.config_file = config_file
        self.config = self._load_or_create_config()
    
    def _load_or_create_config(self) -> Dict:
        """Load existing config or create new one"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default config
        default_config = {
            'gmail_address': '',
            'app_password': '',  # Gmail App Password (not regular password)
            'alert_recipients': [],
            'alert_on_buy': True,
            'alert_on_sell': True,
            'alert_on_anomaly': True,
            'min_confidence': 60.0,
            'email_limit_per_day': 100
        }
        
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Dict) -> bool:
        """Save config to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.config = config
            return True
        except Exception as e:
            print(f"Error saving config: {str(e)}")
            return False
    
    def update_gmail_credentials(self, email: str, app_password: str) -> bool:
        """
        Update Gmail credentials
        
        Args:
            email: Gmail address
            app_password: Gmail App Password (get from myaccount.google.com/apppasswords)
        
        Returns:
            True if successful
        """
        self.config['gmail_address'] = email
        self.config['app_password'] = app_password
        return self.save_config(self.config)
    
    def add_recipient(self, email: str) -> bool:
        """Add recipient email"""
        if email not in self.config.get('alert_recipients', []):
            self.config['alert_recipients'].append(email)
            return self.save_config(self.config)
        return True
    
    def set_alert_preferences(self, buy: bool = True, sell: bool = True,
                            anomaly: bool = True,
                            min_confidence: float = 60.0) -> bool:
        """Set alert preferences"""
        self.config['alert_on_buy'] = buy
        self.config['alert_on_sell'] = sell
        self.config['alert_on_anomaly'] = anomaly
        self.config['min_confidence'] = min_confidence
        return self.save_config(self.config)


# ══════════════════════════════════════════════════════════════════════
# EMAIL ALERT SENDER
# ══════════════════════════════════════════════════════════════════════

class EmailAlertSender:
    """Send trading signal alerts via Gmail"""
    
    # Gmail SMTP settings
    GMAIL_SMTP = 'smtp.gmail.com'
    GMAIL_PORT = 587
    
    def __init__(self, config: EmailAlertConfig):
        """
        Initialize email sender
        
        Args:
            config: EmailAlertConfig instance
        """
        self.config = config
        self.emails_sent_today = 0
    
    def _validate_credentials(self) -> bool:
        """Validate Gmail credentials are set"""
        if not self.config.config.get('gmail_address'):
            print("Error: Gmail address not configured")
            return False
        
        if not self.config.config.get('app_password'):
            print("Error: Gmail app password not configured")
            return False
        
        if not self.config.config.get('alert_recipients'):
            print("Error: No alert recipients configured")
            return False
        
        return True
    
    def send_signal_alert(self, symbol: str, signal: Dict, 
                         current_price: float, target_prices: Dict = None) -> bool:
        """
        Send trading signal alert
        
        Args:
            symbol: Trading symbol
            signal: Signal dict with recommendation and confidence
            current_price: Current price
            target_prices: Optional dict with entry, target, stop_loss
        
        Returns:
            True if successful
        """
        if not self._validate_credentials():
            return False
        
        recommendation = signal.get('recommendation', 'HOLD')
        confidence = signal.get('confidence', 0)
        
        # Check if alert should be sent based on preferences
        config = self.config.config
        
        if 'BUY' in recommendation and not config.get('alert_on_buy'):
            return False
        
        if 'SELL' in recommendation and not config.get('alert_on_sell'):
            return False
        
        if confidence < config.get('min_confidence', 60):
            return False
        
        # Check daily limit
        if self.emails_sent_today >= config.get('email_limit_per_day', 100):
            print("Daily email limit reached")
            return False
        
        # Build email
        subject = f"🚨 Trading Alert: {symbol} - {recommendation}"
        
        body_html = self._build_signal_email_html(
            symbol, signal, current_price, target_prices
        )
        
        # Send email
        success = self._send_email(subject, body_html)
        
        if success:
            self.emails_sent_today += 1
        
        return success
    
    def send_anomaly_alert(self, symbol: str, anomaly_type: str,
                          details: Dict) -> bool:
        """
        Send anomaly detection alert
        
        Args:
            symbol: Trading symbol
            anomaly_type: Type of anomaly (volume spike, price spike, etc.)
            details: Anomaly details
        
        Returns:
            True if successful
        """
        if not self._validate_credentials():
            return False
        
        if not self.config.config.get('alert_on_anomaly'):
            return False
        
        # Check daily limit
        if self.emails_sent_today >= self.config.config.get('email_limit_per_day', 100):
            return False
        
        # Build email
        subject = f"⚠️ Anomaly Detected: {symbol} - {anomaly_type}"
        
        body_html = self._build_anomaly_email_html(symbol, anomaly_type, details)
        
        # Send email
        success = self._send_email(subject, body_html)
        
        if success:
            self.emails_sent_today += 1
        
        return success
    
    def _build_signal_email_html(self, symbol: str, signal: Dict,
                                current_price: float,
                                target_prices: Dict = None) -> str:
        """Build HTML email for signal"""
        
        recommendation = signal.get('recommendation', 'HOLD')
        confidence = signal.get('confidence', 0)
        
        # Color based on signal
        if 'BUY' in recommendation:
            color = '#27AE60'  # Green
            emoji = '📈'
        elif 'SELL' in recommendation:
            color = '#E74C3C'  # Red
            emoji = '📉'
        else:
            color = '#F39C12'  # Orange
            emoji = '➡️'
        
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
                    .header {{ color: {color}; font-size: 24px; font-weight: bold; margin-bottom: 20px; }}
                    .signal-box {{ background: {color}; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                    .signal-text {{ font-size: 18px; font-weight: bold; }}
                    .details {{ background: #f9f9f9; padding: 15px; border-radius: 5px; border-left: 4px solid {color}; }}
                    .detail-row {{ margin-bottom: 10px; }}
                    .label {{ font-weight: bold; color: #333; }}
                    .value {{ color: #666; }}
                    .timestamp {{ color: #999; font-size: 12px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">{emoji} {symbol} Trading Alert</div>
                    
                    <div class="signal-box">
                        <div class="signal-text">{recommendation}</div>
                    </div>
                    
                    <div class="details">
                        <div class="detail-row">
                            <span class="label">Symbol:</span>
                            <span class="value">{symbol}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Current Price:</span>
                            <span class="value">₹{current_price:.2f}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Confidence:</span>
                            <span class="value">{confidence:.1f}%</span>
                        </div>
        """
        
        if target_prices:
            html += f"""
                        <div class="detail-row">
                            <span class="label">Entry Target:</span>
                            <span class="value">₹{target_prices.get('entry', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Price Target:</span>
                            <span class="value">₹{target_prices.get('target', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Stop Loss:</span>
                            <span class="value">₹{target_prices.get('stop_loss', 'N/A')}</span>
                        </div>
            """
        
        html += f"""
                        <div class="detail-row">
                            <span class="label">Signal:</span>
                            <span class="value">{signal.get('factors', {}).get('technical_score', 'N/A')}</span>
                        </div>
                    </div>
                    
                    <p class="timestamp">Alert sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p style="color: #999; font-size: 12px; margin-top: 10px;">
                        This is an automated alert. Please do your own analysis before trading.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return html
    
    def _build_anomaly_email_html(self, symbol: str, anomaly_type: str,
                                 details: Dict) -> str:
        """Build HTML email for anomaly alert"""
        
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
                    .header {{ color: #E74C3C; font-size: 24px; font-weight: bold; margin-bottom: 20px; }}
                    .alert-box {{ background: #E74C3C; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                    .alert-text {{ font-size: 18px; font-weight: bold; }}
                    .details {{ background: #f9f9f9; padding: 15px; border-radius: 5px; border-left: 4px solid #E74C3C; }}
                    .detail-row {{ margin-bottom: 10px; }}
                    .label {{ font-weight: bold; color: #333; }}
                    .value {{ color: #666; }}
                    .timestamp {{ color: #999; font-size: 12px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">⚠️ {symbol} - {anomaly_type}</div>
                    
                    <div class="alert-box">
                        <div class="alert-text">Unusual Activity Detected</div>
                    </div>
                    
                    <div class="details">
                        <div class="detail-row">
                            <span class="label">Symbol:</span>
                            <span class="value">{symbol}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Anomaly Type:</span>
                            <span class="value">{anomaly_type}</span>
                        </div>
        """
        
        for key, value in details.items():
            html += f"""
                        <div class="detail-row">
                            <span class="label">{key.title()}:</span>
                            <span class="value">{value}</span>
                        </div>
            """
        
        html += f"""
                    </div>
                    
                    <p class="timestamp">Alert sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p style="color: #999; font-size: 12px; margin-top: 10px;">
                        This anomaly-based alert requires manual verification.
                    </p>
                </div>
            </body>
        </html>
        """
        
        return html
    
    def _send_email(self, subject: str, body_html: str) -> bool:
        """
        Send email via Gmail
        
        Args:
            subject: Email subject
            body_html: Email body (HTML)
        
        Returns:
            True if successful
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.config['gmail_address']
            msg['To'] = ', '.join(self.config.config['alert_recipients'])
            
            # Attach HTML part
            msg.attach(MIMEText(body_html, 'html'))
            
            # Send via Gmail SMTP
            with smtplib.SMTP(self.GMAIL_SMTP, self.GMAIL_PORT) as server:
                server.starttls()
                server.login(
                    self.config.config['gmail_address'],
                    self.config.config['app_password']
                )
                server.send_message(msg)
            
            print(f"Email sent successfully: {subject}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("Error: Gmail authentication failed. Check credentials.")
            return False
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False


# ══════════════════════════════════════════════════════════════════════
# ALERT MANAGER
# ══════════════════════════════════════════════════════════════════════

class AlertManager:
    """Manage and trigger alerts based on trading logic"""
    
    def __init__(self, config: EmailAlertConfig):
        """Initialize alert manager"""
        self.config = config
        self.sender = EmailAlertSender(config)
        self.alert_history = []
    
    def check_and_alert_signal(self, symbol: str, signal: Dict,
                              current_price: float,
                              target_prices: Dict = None) -> Dict:
        """
        Check signal and send alert if conditions met
        
        Args:
            symbol: Trading symbol
            signal: Signal dict
            current_price: Current price
            target_prices: Optional target prices
        
        Returns:
            Dict with alert result
        """
        recommendation = signal.get('recommendation', 'HOLD')
        
        # Don't alert on HOLD
        if recommendation == 'HOLD':
            return {'alerted': False, 'reason': 'HOLD signal'}
        
        # Send alert
        success = self.sender.send_signal_alert(
            symbol, signal, current_price, target_prices
        )
        
        if success:
            self.alert_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'SIGNAL',
                'symbol': symbol,
                'signal': recommendation,
                'price': current_price
            })
        
        return {
            'alerted': success,
            'signal': recommendation,
            'symbol': symbol
        }
    
    def check_and_alert_anomaly(self, symbol: str, anomaly_type: str,
                               details: Dict) -> Dict:
        """Check anomaly and send alert if enabled"""
        success = self.sender.send_anomaly_alert(symbol, anomaly_type, details)
        
        if success:
            self.alert_history.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'ANOMALY',
                'symbol': symbol,
                'anomaly': anomaly_type
            })
        
        return {
            'alerted': success,
            'anomaly': anomaly_type,
            'symbol': symbol
        }
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """Get recent alert history"""
        return self.alert_history[-limit:]

