import os
from datetime import datetime
import logging
from typing import Dict, List, Optional
import json

class AdvancedConfig:
    """מחלקה לניהול הגדרות מערכת מתקדמות"""
    
    def __init__(self):
        self._load_environment_variables()
        self._setup_logging()
        self._validate_config()
        
    def _load_environment_variables(self):
        """טוען משתני סביבה"""
        # =============================================
        # 🔐 TELEGRAM CONFIGURATION
        # =============================================
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.USER_CHAT_ID = os.getenv('USER_CHAT_ID', '')
        self.GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID', '')
        self.ADMIN_GROUP_CHAT_ID = os.getenv('ADMIN_GROUP_CHAT_ID', '-1002299250120')
        
        # =============================================
        # 🔐 EXCHANGE API CONFIGURATION
        # =============================================
        self.BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
        self.BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', '')
        self.BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', '')
        self.BYBIT_SECRET_KEY = os.getenv('BYBIT_SECRET_KEY', '')
        
        # =============================================
        # 🔐 WEBHOOK SECURITY
        # =============================================
        self.WEBHOOK_KEY = os.getenv('WEBHOOK_KEY', 'MySuperSecureTonBotKey2024!')
        self.SERVER_PORT = int(os.getenv('PORT', 8080))
        
        # =============================================
        # 📊 TRADING CONFIGURATION
        # =============================================
        self.SYMBOLS_TO_ANALYZE = ['TONUSDT', 'BNBUSDT', 'BTCUSDT', 'ETHUSDT']
        self.TIMEFRAMES = ['15m', '1h', '4h', '1d']
        self.ANALYSIS_INTERVAL_MINUTES = 15
        
        # =============================================
        # 🧠 ML & AI CONFIGURATION
        # =============================================
        self.ML_ENABLED = os.getenv('ML_ENABLED', 'True').lower() == 'true'
        self.ML_MODEL_PATH = 'models/'
        self.ML_TRAINING_INTERVAL_HOURS = 24
        
        # =============================================
        # 🔔 ALERTS CONFIGURATION
        # =============================================
        self.ALERTS_ENABLED = True
        self.WHALE_ALERT_THRESHOLD = 50000  # TON
        self.PRICE_ALERT_PERCENT = 5.0
        self.VOLUME_ALERT_MULTIPLIER = 3.0
        
        # =============================================
        # ⚙️ APPLICATION SETTINGS
        # =============================================
        self.DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.DATABASE_PATH = 'database/'
        self.CACHE_ENABLED = True
        self.BACKUP_ENABLED = True
        self.BACKUP_INTERVAL_HOURS = 24
        
        # =============================================
        # 🛡️ RISK MANAGEMENT
        # =============================================
        self.RISK_CONFIG = {
            'max_position_size': 5.0,
            'stop_loss_percent': 3.0,
            'take_profit_percent': 6.0,
            'daily_loss_limit': 5.0,
            'max_leverage': 3,
            'risk_per_trade': 1.0
        }
        
        # =============================================
        # 📈 TECHNICAL ANALYSIS
        # =============================================
        self.TECHNICAL_INDICATORS = {
            'rsi': {'period': 14, 'oversold': 30, 'overbought': 70},
            'macd': {'fast': 12, 'slow': 26, 'signal': 9},
            'bollinger': {'period': 20, 'std_dev': 2},
            'stochastic': {'k_period': 14, 'd_period': 3},
            'atr': {'period': 14},
            'ema': {'periods': [9, 21, 50, 200]}
        }
        
        # =============================================
        # 🌐 API RATE LIMITS
        # =============================================
        self.RATE_LIMITS = {
            'binance': {'requests_per_minute': 1200, 'requests_per_second': 10},
            'telegram': {'messages_per_second': 1, 'messages_per_minute': 20},
            'webhook': {'requests_per_minute': 60}
        }
        
        # =============================================
        # 💰 PAYMENT & SUBSCRIPTION
        # =============================================
        self.PAYMENT_CONFIG = {
            'premium_price_monthly': 2.99,
            'premium_price_yearly': 29.99,
            'premium_price_lifetime': 71.99,
            'referral_bonus_percent': 10,
            'free_trial_days': 7
        }
        
        # =============================================
        # 📊 PERFORMANCE OPTIMIZATION
        # =============================================
        self.PERFORMANCE_CONFIG = {
            'cache_ttl_minutes': 30,
            'data_retention_days': 365,
            'max_concurrent_requests': 10,
            'request_timeout_seconds': 30
        }

    def _setup_logging(self):
        """מגדיר את מערכת הלוגים"""
        log_level = getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('logs/trading_bot.log', encoding='utf-8')
            ]
        )
        
        # יצירת תיקיות נדרשות
        os.makedirs('logs', exist_ok=True)
        os.makedirs('database', exist_ok=True)
        os.makedirs('backups', exist_ok=True)
        os.makedirs('models', exist_ok=True)

    def _validate_config(self):
        """בודק תקינות ההגדרות"""
        errors = []
        warnings = []
        
        # בדיקות חובה
        required_vars = {
            'TELEGRAM_BOT_TOKEN': self.TELEGRAM_BOT_TOKEN,
            'USER_CHAT_ID': self.USER_CHAT_ID,
            'BINANCE_API_KEY': self.BINANCE_API_KEY,
            'BINANCE_SECRET_KEY': self.BINANCE_SECRET_KEY,
            'WEBHOOK_KEY': self.WEBHOOK_KEY
        }
        
        for name, value in required_vars.items():
            if not value:
                errors.append(f"❌ {name} not configured")
        
        # בדיקות אזהרה
        if not self.GROUP_CHAT_ID:
            warnings.append("⚠️ GROUP_CHAT_ID not configured - group features disabled")
        
        if len(self.SYMBOLS_TO_ANALYZE) == 0:
            warnings.append("⚠️ No symbols configured for analysis")
        
        if self.DEBUG_MODE:
            warnings.append("⚠️ Debug mode enabled - not recommended for production")
        
        # הדפסת תוצאות
        if errors:
            print("\n".join(errors))
            raise ValueError("Configuration validation failed")
        
        if warnings:
            print("\n".join(warnings))
        
        print("✅ Configuration validated successfully")
        print(f"🚀 Server will run on port: {self.SERVER_PORT}")
        print(f"📊 Symbols to analyze: {', '.join(self.SYMBOLS_TO_ANALYZE)}")
        print(f"🎁 Premium pricing: ${self.PAYMENT_CONFIG['premium_price_monthly']}/month")
        print(f"🔔 Alerts enabled: {self.ALERTS_ENABLED}")
        print(f"🧠 ML enabled: {self.ML_ENABLED}")

    def get_telegram_config(self) -> Dict:
        """מחזיר הגדרות Telegram"""
        return {
            'bot_token': self.TELEGRAM_BOT_TOKEN,
            'user_chat_id': self.USER_CHAT_ID,
            'group_chat_id': self.GROUP_CHAT_ID,
            'admin_group_chat_id': self.ADMIN_GROUP_CHAT_ID,
            'rate_limits': self.RATE_LIMITS['telegram']
        }

    def get_trading_config(self) -> Dict:
        """מחזיר הגדרות מסחר"""
        return {
            'symbols': self.SYMBOLS_TO_ANALYZE,
            'timeframes': self.TIMEFRAMES,
            'analysis_interval': self.ANALYSIS_INTERVAL_MINUTES,
            'risk_management': self.RISK_CONFIG,
            'technical_indicators': self.TECHNICAL_INDICATORS
        }

    def get_api_config(self) -> Dict:
        """מחזיר הגדרות API"""
        return {
            'binance': {
                'api_key': self.BINANCE_API_KEY,
                'secret_key': self.BINANCE_SECRET_KEY,
                'rate_limits': self.RATE_LIMITS['binance']
            },
            'bybit': {
                'api_key': self.BYBIT_API_KEY,
                'secret_key': self.BYBIT_SECRET_KEY
            },
            'webhook_key': self.WEBHOOK_KEY,
            'server_port': self.SERVER_PORT
        }

    def get_ml_config(self) -> Dict:
        """מחזיר הגדרות Machine Learning"""
        return {
            'enabled': self.ML_ENABLED,
            'model_path': self.ML_MODEL_PATH,
            'training_interval': self.ML_TRAINING_INTERVAL_HOURS
        }

    def get_alerts_config(self) -> Dict:
        """מחזיר הגדרות התראות"""
        return {
            'enabled': self.ALERTS_ENABLED,
            'whale_threshold': self.WHALE_ALERT_THRESHOLD,
            'price_alert_percent': self.PRICE_ALERT_PERCENT,
            'volume_alert_multiplier': self.VOLUME_ALERT_MULTIPLIER
        }

    def get_performance_config(self) -> Dict:
        """מחזיר הגדרות ביצועים"""
        return {
            'cache_enabled': self.CACHE_ENABLED,
            'cache_ttl': self.PERFORMANCE_CONFIG['cache_ttl_minutes'],
            'data_retention': self.PERFORMANCE_CONFIG['data_retention_days'],
            'max_concurrent_requests': self.PERFORMANCE_CONFIG['max_concurrent_requests'],
            'request_timeout': self.PERFORMANCE_CONFIG['request_timeout_seconds']
        }

    def update_config(self, new_config: Dict):
        """מעדכן הגדרות באופן דינמי"""
        try:
            for key, value in new_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                elif key in self.RISK_CONFIG:
                    self.RISK_CONFIG[key] = value
                elif key in self.TECHNICAL_INDICATORS:
                    self.TECHNICAL_INDICATORS[key] = value
            
            self._validate_config()
            self.logger.info("✅ Configuration updated successfully")
            
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
            raise

    def save_config_backup(self):
        """שומר גיבוי של ההגדרות"""
        try:
            config_data = {
                'telegram': self.get_telegram_config(),
                'trading': self.get_trading_config(),
                'api': self.get_api_config(),
                'ml': self.get_ml_config(),
                'alerts': self.get_alerts_config(),
                'performance': self.get_performance_config(),
                'timestamp': datetime.now().isoformat()
            }
            
            backup_path = f"backups/config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs('backups', exist_ok=True)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"💾 Configuration backup saved: {backup_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving config backup: {e}")

# יצירת instance גלובלי
config = AdvancedConfig()
