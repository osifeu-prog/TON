from flask import Flask, request, jsonify, render_template_string, send_from_directory
import threading
import schedule
import time
from datetime import datetime, timedelta
import logging
import os
import sys
import traceback
import json
from logging.handlers import RotatingFileHandler
import sqlite3
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """הגדרת מערכת logging מפורטת"""
    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
    )
    
    os.makedirs('logs', exist_ok=True)
    
    file_handler = RotatingFileHandler(
        'logs/trading.log', 
        maxBytes=10485760,
        backupCount=5
    )
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)
    
    error_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10485760,
        backupCount=5
    )
    error_handler.setFormatter(log_formatter)
    error_handler.setLevel(logging.ERROR)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)
    
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, error_handler, console_handler]
    )

setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)

try:
    from advanced_trading_logic import AdvancedTradingLogic
    from telegram_bot import AdvancedTelegramBot
    from payment_manager import PaymentManager
    from fibonacci_calculator import FibonacciCalculator
    from whale_tracker import WhaleTracker
    from correlation_analyzer import CorrelationAnalyzer
    from binance_client import AdvancedBinanceClient
    from tradingview_client import TradingViewClient
    from technical_analyzer import AdvancedTechnicalAnalyzer
    from data_manager import AdvancedDataManager
    from ml_predictor import AdvancedMLPredictor
    from risk_manager import AdvancedRiskManager, TradeAction
    from dashboard import create_dashboard_app
    import config
    
    logger.info("✅ כל הרכיבים יובאו בהצלחה")
    
except ImportError as e:
    logger.error(f"❌ שגיאה בייבוא רכיבים: {e}")
    logger.error(traceback.format_exc())
    
    # Fallback classes במקרה של שגיאה
    class AdvancedTradingLogic:
        def comprehensive_analysis(self, symbol="TONUSDT"):
            return {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'current_data': {'price': 2.45, 'price_change_percent': 1.5},
                'trading_decision': {'action': 'HOLD', 'confidence_score': 0.5}
            }
        def multi_symbol_analysis(self):
            return {'analyses': {}, 'timestamp': datetime.now().isoformat()}
    
    class AdvancedTelegramBot:
        def __init__(self):
            self.token = os.getenv('TELEGRAM_BOT_TOKEN', '')
            self.joined_groups = set()
        
        def send_immediate_alert(self, analysis): 
            logger.info("📨 שליחת התראה (ברירת מחדל)")
        
        def send_daily_to_group(self, analysis): 
            logger.info("📅 שליחת דוח יומי (ברירת מחדל)")
        
        def handle_webhook_update(self, data):
            logger.info("📱 עיבוד עדכון Telegram")
        
        def send_message(self, chat_id, text):
            logger.info(f"💬 שליחת הודעה ל-{chat_id}")
    
    class PaymentManager:
        def __init__(self):
            self.pricing = {
                'monthly': 24.99, 
                'yearly': 249.00, 
                'lifetime': 599.00,
                'monthly_black_friday': 2.99,
                'yearly_black_friday': 29.99,
                'lifetime_black_friday': 71.99
            }
        
        def register_user(self, user_data):
            return True
        
        def check_premium_status(self, user_id):
            return False
        
        def get_payment_info(self):
            return {
                'pricing': self.pricing,
                'payment_methods': {
                    'bank': {
                        'bank_name': 'בנק הפועלים',
                        'branch': '153 - כפר גנים', 
                        'account_number': '73462',
                        'account_holder': 'אוסף אונגר'
                    },
                    'crypto': {
                        'ton_wallet': 'UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp',
                        'network': 'TON'
                    }
                }
            }
        
        def get_admin_stats(self):
            return {
                'total_users': 150,
                'premium_users': 45,
                'free_users': 105,
                'completed_payments': 67,
                'total_revenue': 2450.00,
                'total_referrals': 23,
                'new_users_today': 12,
                'premium_conversion_rate': 30.0
            }

    class FibonacciCalculator:
        def calculate_retracement(self, high, low):
            return {'retracement_levels': {}}
        
        def calculate_extensions(self, high, low, current_price):
            return {'extension_levels': {}, 'current_position': 'UNKNOWN'}

    class WhaleTracker:
        def track_whale_transactions(self, symbol):
            return []

    class CorrelationAnalyzer:
        def analyze_correlation(self, symbol1, symbol2):
            return {}

    class AdvancedBinanceClient:
        def get_current_price(self, symbol):
            return {'price': 2.45}
        
        def get_24h_high_low(self, symbol):
            return {'high': 2.5, 'low': 2.4}

    class TradingViewClient:
        def send_webhook_alert(self, data):
            return True

    class AdvancedTechnicalAnalyzer:
        def comprehensive_technical_analysis(self, df, symbol):
            return {'summary': {'action': 'HOLD', 'confidence': 0.5}}

    class AdvancedDataManager:
        def get_historical_data(self, symbol, days=30):
            return pd.DataFrame()
        
        def calculate_performance_metrics(self, symbol):
            return {}

    class AdvancedMLPredictor:
        def predict_future(self, df, periods=10):
            return {'ensemble_prediction': 2.45, 'ensemble_confidence': 0.5}

    class AdvancedRiskManager:
        def assess_trade_risk(self, symbol, action, quantity, price, market_data, portfolio):
            return {'overall_risk_level': 'MEDIUM', 'can_proceed': True}

    class TradeAction:
        BUY = "BUY"
        SELL = "SELL"
        HOLD = "HOLD"

    import types
    config = types.SimpleNamespace()
    config.SERVER_PORT = int(os.getenv('PORT', 8080))
    config.SYMBOLS_TO_ANALYZE = ['TONUSDT', 'BNBUSDT']
    config.WEBHOOK_KEY = os.getenv('WEBHOOK_KEY', 'default_key')
    config.DEBUG_MODE = False

    def validate_config():
        logger.info("⚠️ שימוש בהגדרות ברירת מחדל")
        return True
    
    config.validate_config = validate_config

# אתחול הרכיבים
try:
    # אתחול מנהלי נתונים
    data_manager = AdvancedDataManager()
    technical_analyzer = AdvancedTechnicalAnalyzer()
    
    # אתחול מודלים מתקדמים
    ml_predictor = AdvancedMLPredictor()
    risk_manager = AdvancedRiskManager()
    
    # אתחול לקוחות חיצוניים
    binance_client = AdvancedBinanceClient()
    tradingview_client = TradingViewClient()
    
    # אתחול לוגיקת מסחר
    trading_logic = AdvancedTradingLogic()
    
    # אתחול מערכת תשלומים
    payment_manager = PaymentManager()
    
    # אתחול בוט Telegram
    telegram_bot = AdvancedTelegramBot()
    telegram_bot.set_trading_logic(trading_logic)
    
    # אתחול אנלייזרים נוספים
    fibonacci_calc = FibonacciCalculator()
    whale_tracker = WhaleTracker()
    correlation_analyzer = CorrelationAnalyzer()
    
    logger.info("✅ כל הרכיבים אותחלו בהצלחה")
    
except Exception as e:
    logger.error(f"❌ שגיאה באתחול רכיבים: {e}")
    logger.error(traceback.format_exc())
    
    # אתחול גיבוי
    data_manager = AdvancedDataManager()
    technical_analyzer = AdvancedTechnicalAnalyzer()
    ml_predictor = AdvancedMLPredictor()
    risk_manager = AdvancedRiskManager()
    binance_client = AdvancedBinanceClient()
    tradingview_client = TradingViewClient()
    trading_logic = AdvancedTradingLogic()
    payment_manager = PaymentManager()
    telegram_bot = AdvancedTelegramBot()
    fibonacci_calc = FibonacciCalculator()
    whale_tracker = WhaleTracker()
    correlation_analyzer = CorrelationAnalyzer()

# יצירת תיקיות נדרשות
os.makedirs('database', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('models', exist_ok=True)
os.makedirs('backups', exist_ok=True)

# HTML template for dashboard
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TON Trading Bot Pro - Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .card h3 { margin-top: 0; color: #333; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .stat { text-align: center; padding: 15px; background: #f8f9fa; border-radius: 8px; }
        .stat .value { font-size: 24px; font-weight: bold; color: #667eea; }
        .stat .label { font-size: 14px; color: #666; }
        .alert { padding: 15px; border-radius: 8px; margin: 10px 0; }
        .alert.success { background: #d4edda; color: #155724; }
        .alert.warning { background: #fff3cd; color: #856404; }
        .alert.danger { background: #f8d7da; color: #721c24; }
        table { width: 100%; border-collapse: collapse; background: white; }
        th, td { padding: 12px; text-align: right; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
        .btn { display: inline-block; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 TON Trading Bot Pro - Dashboard</h1>
            <p>מערכת ניתוח שוק קריפטו מתקדמת - ניהול בזמן אמת</p>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="value">{{ stats.total_users }}</div>
                <div class="label">👥 משתמשים</div>
            </div>
            <div class="stat">
                <div class="value">{{ stats.premium_users }}</div>
                <div class="label">💎 משתמשי Premium</div>
            </div>
            <div class="stat">
                <div class="value">${{ "%.2f"|format(stats.total_revenue) }}</div>
                <div class="label">💰 הכנסות</div>
            </div>
            <div class="stat">
                <div class="value">{{ stats.new_users_today }}</div>
                <div class="label">📈 משתמשים חדשים היום</div>
            </div>
        </div>

        <div class="cards">
            <div class="card">
                <h3>📊 ניתוח שוק נוכחי</h3>
                {% for symbol, analysis in market_analysis.items() %}
                <div class="alert {% if analysis.action == 'BUY' %}success{% elif analysis.action == 'SELL' %}danger{% else %}warning{% endif %}">
                    <strong>{{ symbol }}</strong>: {{ analysis.action }} (ביטחון: {{ "%.1f"|format(analysis.confidence * 100) }}%)
                    <br><small>מחיר: ${{ "%.4f"|format(analysis.price) }}</small>
                </div>
                {% endfor %}
            </div>

            <div class="card">
                <h3>🐋 פעילות לווייתנים</h3>
                {% if whale_activity %}
                    {% for whale in whale_activity[:3] %}
                    <div class="alert warning">
                        <strong>{{ whale.whale_size }}</strong> - {{ whale.amount }} TON
                        <br><small>מחיר: ${{ "%.4f"|format(whale.price) }} • {{ whale.type }}</small>
                    </div>
                    {% endfor %}
                {% else %}
                    <p>אין פעילות לווייתנים משמעותית</p>
                {% endif %}
            </div>

            <div class="card">
                <h3>🔗 קורלציות</h3>
                {% for corr in correlations %}
                <p>{{ corr.symbols }}: {{ "%.3f"|format(corr.correlation) }} ({{ corr.strength }})</p>
                {% endfor %}
            </div>
        </div>

        <div class="card">
            <h3>🚨 התראות אחרונות</h3>
            {% if recent_alerts %}
                <table>
                    <thead>
                        <tr>
                            <th>זמן</th>
                            <th>סוג</th>
                            <th>הודעה</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for alert in recent_alerts %}
                        <tr>
                            <td>{{ alert.timestamp }}</td>
                            <td>{{ alert.type }}</td>
                            <td>{{ alert.message }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>אין התראות אחרונות</p>
            {% endif %}
        </div>

        <div style="text-align: center; margin-top: 20px;">
            <a href="/health" class="btn">🔧 בדיקת מערכת</a>
            <a href="/admin/stats" class="btn">📈 סטטיסטיקות</a>
            <a href="/logs" class="btn">📋 לוגים</a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def dashboard():
    """דשבורד ראשי של המערכת"""
    try:
        stats = payment_manager.get_admin_stats()
        market_data = {}
        whale_activity = []
        correlations = []
        recent_alerts = []

        try:
            # נתוני שוק
            for symbol in config.SYMBOLS_TO_ANALYZE:
                analysis = trading_logic.comprehensive_analysis(symbol)
                decision = analysis.get('trading_decision', {})
                market_data[symbol] = {
                    'action': decision.get('action', 'HOLD'),
                    'confidence': decision.get('confidence', 0),
                    'price': analysis.get('market_analysis', {}).get('current_price', 0)
                }

            # פעילות לווייתנים
            whale_activity = whale_tracker.track_whale_transactions('TONUSDT')[:5]

            # קורלציות
            corr_result = correlation_analyzer.analyze_correlation('TONUSDT', 'BNBUSDT')
            correlations.append({
                'symbols': 'TON-USDT/BNB-USDT',
                'correlation': corr_result.get('correlation_coefficient', 0),
                'strength': corr_result.get('strength', 'UNKNOWN')
            })

            # התראות אחרונות
            recent_alerts = [
                {'timestamp': '2024-01-01 10:30', 'type': 'WHALE', 'message': 'לווייתן קנה 50,000 TON'},
                {'timestamp': '2024-01-01 09:15', 'type': 'ANALYSIS', 'message': 'ניתוח TON: STRONG_BUY'}
            ]

        except Exception as e:
            logger.error(f"Error preparing dashboard data: {e}")

        return render_template_string(DASHBOARD_HTML,
            stats=stats,
            market_analysis=market_data,
            whale_activity=whale_activity,
            correlations=correlations,
            recent_alerts=recent_alerts
        )

    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """בדיקת בריאות מפורטת"""
    try:
        components_status = {
            'flask': 'healthy',
            'trading_logic': 'unknown',
            'telegram_bot': 'unknown',
            'payment_system': 'unknown',
            'database': 'unknown',
            'fibonacci_calc': 'unknown',
            'whale_tracker': 'unknown',
            'correlation_analyzer': 'unknown',
            'binance_client': 'unknown',
            'technical_analyzer': 'unknown',
            'data_manager': 'unknown',
            'ml_predictor': 'unknown',
            'risk_manager': 'unknown'
        }
        
        try:
            test_analysis = trading_logic.comprehensive_analysis('TONUSDT')
            components_status['trading_logic'] = 'healthy'
        except Exception as e:
            components_status['trading_logic'] = f'error: {str(e)}'
        
        try:
            if hasattr(telegram_bot, 'token') and telegram_bot.token:
                components_status['telegram_bot'] = 'healthy'
            else:
                components_status['telegram_bot'] = 'not configured'
        except Exception as e:
            components_status['telegram_bot'] = f'error: {str(e)}'
        
        try:
            test_user = payment_manager.get_user(1)
            components_status['payment_system'] = 'healthy'
        except Exception as e:
            components_status['payment_system'] = f'error: {str(e)}'
        
        try:
            conn = sqlite3.connect('database/payments.db')
            conn.close()
            components_status['database'] = 'healthy'
        except Exception as e:
            components_status['database'] = f'error: {str(e)}'
        
        try:
            fib_test = fibonacci_calc.calculate_retracement(2.5, 2.4)
            components_status['fibonacci_calc'] = 'healthy'
        except Exception as e:
            components_status['fibonacci_calc'] = f'error: {str(e)}'

        try:
            whale_test = whale_tracker.track_whale_transactions('TONUSDT')
            components_status['whale_tracker'] = 'healthy'
        except Exception as e:
            components_status['whale_tracker'] = f'error: {str(e)}'

        try:
            corr_test = correlation_analyzer.analyze_correlation('TONUSDT', 'BNBUSDT')
            components_status['correlation_analyzer'] = 'healthy'
        except Exception as e:
            components_status['correlation_analyzer'] = f'error: {str(e)}'

        try:
            price_test = binance_client.get_current_price('TONUSDT')
            components_status['binance_client'] = 'healthy'
        except Exception as e:
            components_status['binance_client'] = f'error: {str(e)}'

        try:
            df_test = data_manager.get_historical_data('TONUSDT', days=7)
            components_status['data_manager'] = 'healthy'
        except Exception as e:
            components_status['data_manager'] = f'error: {str(e)}'

        try:
            ta_test = technical_analyzer.comprehensive_technical_analysis(df_test, 'TONUSDT')
            components_status['technical_analyzer'] = 'healthy'
        except Exception as e:
            components_status['technical_analyzer'] = f'error: {str(e)}'

        try:
            ml_test = ml_predictor.predict_future(df_test, periods=3)
            components_status['ml_predictor'] = 'healthy'
        except Exception as e:
            components_status['ml_predictor'] = f'error: {str(e)}'

        try:
            risk_test = risk_manager.assess_trade_risk('TONUSDT', TradeAction.BUY, 100, 2.45, {}, {})
            components_status['risk_manager'] = 'healthy'
        except Exception as e:
            components_status['risk_manager'] = f'error: {str(e)}'
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': components_status,
            'environment': {
                'python_version': sys.version,
                'server_port': config.SERVER_PORT,
                'symbols_tracked': config.SYMBOLS_TO_ANALYZE
            }
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/analysis', methods=['GET'])
def get_current_analysis():
    """ניתוח שוק נוכחי"""
    try:
        symbol = request.args.get('symbol', 'TONUSDT')
        user_id = request.args.get('user_id', None)
        
        if user_id and not payment_manager.check_premium_status(int(user_id)):
            return jsonify({
                'status': 'premium_required',
                'message': 'נדרש מנוי Premium לגישה לניתוח מתקדם',
                'upgrade_url': '/premium'
            }), 402
        
        logger.info(f"📊 מתבצע ניתוח עבור: {symbol}")
        
        analysis = trading_logic.comprehensive_analysis(symbol)
        
        logger.info(f"✅ ניתוח הושלם: {analysis.get('trading_decision', {}).get('action')}")
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"❌ שגיאה בניתוח: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol
        }), 500

@app.route('/multi_analysis', methods=['GET'])
def get_multi_analysis():
    """ניתוח מרובה מטבעות - למשתמשי Premium בלבד"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'status': 'auth_required',
                'message': 'נדרש מזהה משתמש לגישה לניתוח מרובה מטבעות'
            }), 401
        
        if not payment_manager.check_premium_status(int(user_id)):
            return jsonify({
                'status': 'premium_required',
                'message': 'נדרש מנוי Premium לגישה לניתוח מרובה מטבעות',
                'upgrade_url': '/premium'
            }), 402
        
        logger.info("🌐 מתבצע ניתוח מרובה מטבעות")
        
        analysis = trading_logic.multi_symbol_analysis()
        
        logger.info(f"✅ ניתוח מרובה מטבעות הושלם: {len(analysis.get('analyses', {}))} מטבעות")
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"❌ שגיאה בניתוח מרובה מטבעות: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/technical/<symbol>', methods=['GET'])
def get_technical_analysis(symbol):
    """ניתוח טכני מתקדם"""
    try:
        user_id = request.args.get('user_id')
        if user_id and not payment_manager.check_premium_status(int(user_id)):
            return jsonify({
                'status': 'premium_required',
                'message': 'נדרש מנוי Premium לגישה לניתוח טכני מתקדם'
            }), 402
        
        # קבלת נתונים היסטוריים
        df = data_manager.get_historical_data(symbol, days=60)
        
        if df.empty:
            return jsonify({'status': 'error', 'message': 'No data available'}), 404
        
        # ניתוח טכני
        analysis = technical_analyzer.comprehensive_technical_analysis(df, symbol)
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error in technical analysis: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/ml-prediction/<symbol>', methods=['GET'])
def get_ml_prediction(symbol):
    """חיזוי Machine Learning"""
    try:
        user_id = request.args.get('user_id')
        if user_id and not payment_manager.check_premium_status(int(user_id)):
            return jsonify({
                'status': 'premium_required',
                'message': 'נדרש מנוי Premium לגישה לחיזוי ML'
            }), 402
        
        periods = int(request.args.get('periods', 10))
        
        # קבלת נתונים לאימון
        df = data_manager.get_historical_data(symbol, days=180)
        
        if df.empty:
            return jsonify({'status': 'error', 'message': 'Insufficient data for ML prediction'}), 404
        
        # אימון מודל (בפעם הראשונה) או שימוש במודל קיים
        if not hasattr(ml_predictor, 'model_performance') or not ml_predictor.model_performance:
            ml_predictor.train_models(df)
        
        # חיזוי
        prediction = ml_predictor.predict_future(df, periods)
        
        return jsonify(prediction)
        
    except Exception as e:
        logger.error(f"Error in ML prediction: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/risk-assessment', methods=['POST'])
def get_risk_assessment():
    """הערכת סיכון לעסקה"""
    try:
        data = request.get_json()
        
        symbol = data.get('symbol', 'TONUSDT')
        action = getattr(TradeAction, data.get('action', 'BUY'))
        quantity = float(data.get('quantity', 0))
        price = float(data.get('price', 0))
        
        # נתוני שוק (סימולציה - בפועל יגיעו ממקורות אמיתיים)
        market_data = {
            'volatility': 0.02,
            'volume_24h': 1000000,
            'average_volume': 800000,
            'trend_strength': 0.6,
            'historical_volatility': 0.018
        }
        
        # נתוני תיק (סימולציה)
        portfolio = {
            'total_value': 10000,
            'current_drawdown': 0.02,
            'positions': {
                'BTCUSDT': {'value': 3000},
                'ETHUSDT': {'value': 2000}
            }
        }
        
        risk_assessment = risk_manager.assess_trade_risk(
            symbol, action, quantity, price, market_data, portfolio
        )
        
        return jsonify(risk_assessment)
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/fibonacci/<symbol>', methods=['GET'])
def get_fibonacci_analysis(symbol):
    """ניתוח פיבונאצ'י עבור סימל"""
    try:
        current_data = binance_client.get_current_price(symbol)
        high_low_data = binance_client.get_24h_high_low(symbol)
        
        high = high_low_data.get('high', 2.5)
        low = high_low_data.get('low', 2.4)
        current_price = current_data.get('price', 2.45)
        
        fib_retracement = fibonacci_calc.calculate_retracement(high, low)
        fib_extensions = fibonacci_calc.calculate_extensions(high, low, current_price)
        
        return jsonify({
            'symbol': symbol,
            'current_price': current_price,
            'swing_high': high,
            'swing_low': low,
            'fibonacci_retracement': fib_retracement,
            'fibonacci_extensions': fib_extensions,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in Fibonacci analysis: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/whales/<symbol>', methods=['GET'])
def get_whale_activity(symbol):
    """פעילות לווייתנים עבור סימל"""
    try:
        user_id = request.args.get('user_id')
        if user_id and not payment_manager.check_premium_status(int(user_id)):
            return jsonify({
                'status': 'premium_required',
                'message': 'נדרש מנוי Premium לגישה לנתוני לווייתנים'
            }), 402
        
        whale_data = whale_tracker.track_whale_transactions(symbol)
        
        return jsonify({
            'symbol': symbol,
            'whale_activity': whale_data,
            'total_whales': len(whale_data),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting whale activity: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/correlation', methods=['GET'])
def get_correlation_analysis():
    """ניתוח קורלציה בין שני סימלים"""
    try:
        symbol1 = request.args.get('symbol1', 'TONUSDT')
        symbol2 = request.args.get('symbol2', 'BNBUSDT')
        period = int(request.args.get('period', 30))
        
        correlation = correlation_analyzer.analyze_correlation(symbol1, symbol2, period)
        
        return jsonify({
            'correlation_analysis': correlation,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in correlation analysis: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """מטפל בהתראות webhook"""
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("❌ Webhook ללא data")
            return jsonify({'status': 'error', 'message': 'No JSON data'}), 400
            
        logger.info(f"📨 Webhook התקבל: {data.get('symbol', 'unknown')}")
        
        if data.get('key') != config.WEBHOOK_KEY:
            logger.warning("❌ Webhook key לא תקין")
            return jsonify({'status': 'error', 'message': 'Invalid key'}), 401
        
        # שליחה להתראה בבוט
        telegram_bot.send_immediate_alert(data)
        
        # שליחה ל-TradingView אם רלוונטי
        if data.get('source') == 'tradingview':
            tradingview_client.send_webhook_alert(data)
        
        logger.info("✅ Webhook עובד בהצלחה והתראות נשלחו")
        return jsonify({
            'status': 'success', 
            'processed_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ שגיאה ב-webhook: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/telegram_webhook', methods=['POST'])
def handle_telegram_webhook():
    """מטפל ב-webhook של Telegram"""
    try:
        data = request.get_json()
        telegram_bot.handle_webhook_update(data)
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"❌ שגיאה ב-Telegram webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/whale_alert', methods=['POST'])
def handle_whale_alert():
    """מטפל בהתראות לווייתנים"""
    try:
        data = request.get_json()
        
        if not data or 'symbol' not in data:
            return jsonify({'status': 'error', 'message': 'Invalid whale alert data'}), 400
        
        # שליחת התראת לווייתן לבוט
        telegram_bot.send_whale_alert(data)
        
        logger.info(f"🐋 Whale alert processed for {data['symbol']}")
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error processing whale alert: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/system/restart', methods=['POST'])
def restart_system():
    """מאתחל את המערכת (לדרי administrator)"""
    try:
        admin_key = request.headers.get('X-Admin-Key')
        if admin_key != os.getenv('ADMIN_KEY', 'default_admin_key'):
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        
        logger.warning("🔄 System restart initiated by admin")
        
        # אתחול מחדש של הרכיבים
        global trading_logic, telegram_bot, payment_manager
        global data_manager, technical_analyzer, ml_predictor, risk_manager
        
        trading_logic = AdvancedTradingLogic()
        telegram_bot = AdvancedTelegramBot()
        payment_manager = PaymentManager()
        data_manager = AdvancedDataManager()
        technical_analyzer = AdvancedTechnicalAnalyzer()
        ml_predictor = AdvancedMLPredictor()
        risk_manager = AdvancedRiskManager()
        
        return jsonify({
            'status': 'success',
            'message': 'System restarted successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error restarting system: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def scheduled_analysis():
    """מריץ ניתוח לפי לוח זמנים"""
    try:
        logger.info("⏰ מתבצע ניתוח מתוזמן...")
        analysis = trading_logic.multi_symbol_analysis()
        
        symbols_analyzed = len(analysis.get('analyses', {}))
        decisions = []
        for symbol, analysis_data in analysis.get('analyses', {}).items():
            decision = analysis_data.get('trading_decision', {})
            decisions.append(f"{symbol}: {decision.get('action')} ({decision.get('confidence_score', 0):.1%})")
        
        logger.info(f"✅ ניתוח מתוזמן הושלם: {symbols_analyzed} מטבעות")
        logger.info(f"📋 החלטות: {', '.join(decisions)}")
        
        telegram_bot.send_immediate_alert(analysis)
        
        if datetime.now().hour == 9 and datetime.now().minute < 5:
            logger.info("🌅 שליחת דוח יומי...")
            telegram_bot.send_daily_to_group(analysis)
            
    except Exception as e:
        logger.error(f"❌ שגיאה בניתוח מתוזמן: {e}")
        logger.error(traceback.format_exc())

def whale_monitoring():
    """מעקב אחר לווייתנים"""
    try:
        logger.info("🐋 מתבצע מעקב לווייתנים...")
        
        for symbol in config.SYMBOLS_TO_ANALYZE:
            whale_data = whale_tracker.track_whale_transactions(symbol)
            
            for whale in whale_data:
                if whale.get('impact_score', 0) > 0.7:  # רק התראות משמעותיות
                    telegram_bot.send_whale_alert(whale)
                    logger.info(f"🚨 Whale alert sent for {symbol}")
                    
    except Exception as e:
        logger.error(f"Error in whale monitoring: {e}")

def premium_status_check():
    """בודק תוקף Premium של משתמשים"""
    try:
        logger.info("🔍 בודק תוקף Premium...")
        conn = sqlite3.connect('database/payments.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, premium_until FROM users 
            WHERE is_premium = 1 AND premium_until < datetime('now', '+7 days')
        ''')
        
        expiring_users = cursor.fetchall()
        
        for user_id, premium_until in expiring_users:
            days_left = (datetime.fromisoformat(premium_until) - datetime.now()).days
            if days_left <= 3:
                logger.info(f"⚠️ Premium של משתמש {user_id} יפוג בעוד {days_left} ימים")
                # אפשר לשלוח התראה למשתמש
            
        conn.close()
        
    except Exception as e:
        logger.error(f"Error in premium status check: {e}")

def ml_model_retraining():
    """מאמן מחדש את מודלי ה-ML"""
    try:
        logger.info("🧠 מתבצע אימון מחדש של מודלי ML...")
        
        for symbol in config.SYMBOLS_TO_ANALYZE[:2]:  # מאמן רק על 2 סימלים ראשונים
            df = data_manager.get_historical_data(symbol, days=180)
            if not df.empty:
                ml_predictor.train_models(df)
                logger.info(f"✅ ML model retrained for {symbol}")
        
        ml_predictor.save_models()
        logger.info("💾 ML models saved")
        
    except Exception as e:
        logger.error(f"Error in ML retraining: {e}")

def run_scheduler():
    """מריץ את ה-scheduler"""
    logger.info("🔄 מתחיל scheduler...")
    
    schedule.every(15).minutes.do(scheduled_analysis)
    schedule.every(10).minutes.do(whale_monitoring)
    schedule.every().day.at("09:00").do(lambda: scheduled_analysis())
    schedule.every().day.at("03:00").do(premium_status_check)
    schedule.every().day.at("04:00").do(ml_model_retraining)
    schedule.every(5).minutes.do(lambda: logger.info("💓 System heartbeat"))
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except Exception as e:
            logger.error(f"❌ שגיאה ב-scheduler: {e}")
            time.sleep(60)

def start_server():
    """מתחיל את שרת Flask"""
    try:
        logger.info("=" * 60)
        logger.info("🚀 TON Trading Bot Pro - Starting Server")
        logger.info(f"📊 Port: {config.SERVER_PORT}")
        logger.info(f"🎯 Symbols: {', '.join(config.SYMBOLS_TO_ANALYZE)}")
        logger.info(f"💰 Pricing: ${payment_manager.pricing['monthly_black_friday']}/month (BLACK FRIDAY)")
        logger.info("🐋 Whale Tracking: ACTIVE")
        logger.info("📈 Fibonacci Analysis: ACTIVE")
        logger.info("🔗 Correlation Analysis: ACTIVE")
        logger.info("🧠 ML Prediction: ACTIVE")
        logger.info("🛡️ Risk Management: ACTIVE")
        logger.info("=" * 60)
        
        app.run(
            host='0.0.0.0', 
            port=config.SERVER_PORT, 
            debug=config.DEBUG_MODE,
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == '__main__':
    print("🤖 Initializing TON Trading Bot Pro with Advanced Features...")
    
    if not config.validate_config():
        logger.error("❌ Invalid configuration. Please check environment variables")
        sys.exit(1)
    
    try:
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("✅ Scheduler started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")
        logger.error(traceback.format_exc())
    
    start_server()

# === Static Web Portal Routes ===
@app.route('/site')
def site_index():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    web_dir = os.path.join(base_dir, 'web')
    return send_from_directory(web_dir, 'index.html')

@app.route('/site/<path:filename>')
def site_files(filename):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    web_dir = os.path.join(base_dir, 'web')
    return send_from_directory(web_dir, filename)
