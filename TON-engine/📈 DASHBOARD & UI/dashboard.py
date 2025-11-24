from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import json

from data_manager import AdvancedDataManager
from technical_analyzer import AdvancedTechnicalAnalyzer
from payment_manager import PaymentManager

class TradingDashboard:
    def __init__(self, data_manager: AdvancedDataManager, 
                 technical_analyzer: AdvancedTechnicalAnalyzer,
                 payment_manager: PaymentManager):
        self.data_manager = data_manager
        self.technical_analyzer = technical_analyzer
        self.payment_manager = payment_manager
        self.logger = logging.getLogger(__name__)
        
    def create_main_dashboard(self, symbol: str = 'TONUSDT') -> Dict:
        """יוצר דשבורד ראשי"""
        try:
            # קבלת נתונים
            historical_data = self.data_manager.get_historical_data(symbol, days=30)
            technical_analysis = self.technical_analyzer.comprehensive_technical_analysis(
                historical_data, symbol
            )
            performance_metrics = self.data_manager.calculate_performance_metrics(symbol)
            recent_decisions = self.data_manager.get_recent_decisions(symbol, hours=24)
            
            # יצירת גרפים
            price_chart = self._create_price_chart(historical_data, technical_analysis)
            indicators_chart = self._create_indicators_chart(historical_data, technical_analysis)
            performance_chart = self._create_performance_chart(performance_metrics)
            volume_chart = self._create_volume_chart(historical_data)
            
            # סטטיסטיקות
            stats = self._calculate_dashboard_stats(historical_data, technical_analysis, performance_metrics)
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'charts': {
                    'price_chart': price_chart,
                    'indicators_chart': indicators_chart,
                    'performance_chart': performance_chart,
                    'volume_chart': volume_chart
                },
                'statistics': stats,
                'recent_decisions': recent_decisions[:10],  # 10 האחרונות
                'technical_summary': technical_analysis.get('summary', {}),
                'alerts': self._get_active_alerts(symbol)
            }
            
        except Exception as e:
            self.logger.error(f"Error creating dashboard: {e}")
            return self._get_empty_dashboard(symbol)
    
    def _create_price_chart(self, data: pd.DataFrame, analysis: Dict) -> str:
        """יוצר גרף מחיר עם אינדיקטורים"""
        try:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                subplot_titles=('Price Chart with Indicators', 'Volume'),
                row_heights=[0.7, 0.3]
            )
            
            # גרף candlestick
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['open'],
                    high=data['high'],
                    low=data['low'],
                    close=data['close'],
                    name='Price'
                ),
                row=1, col=1
            )
            
            # Bollinger Bands
            bb = analysis.get('advanced_indicators', {}).get('volatility_indicators', {}).get('bollinger_bands', {})
            if bb:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=[bb['upper']] * len(data),
                        line=dict(color='rgba(255, 0, 0, 0.3)'),
                        name='BB Upper'
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=[bb['middle']] * len(data),
                        line=dict(color='rgba(0, 255, 0, 0.3)'),
                        name='BB Middle'
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=[bb['lower']] * len(data),
                        line=dict(color='rgba(0, 0, 255, 0.3)'),
                        name='BB Lower'
                    ),
                    row=1, col=1
                )
            
            # גרף ווליום
            colors = ['green' if data['close'].iloc[i] > data['open'].iloc[i] 
                     else 'red' for i in range(len(data))]
            
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['volume'],
                    marker_color=colors,
                    name='Volume'
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title=f"Price and Volume Analysis",
                xaxis_rangeslider_visible=False,
                height=600,
                showlegend=True
            )
            
            return fig.to_json()
            
        except Exception as e:
            self.logger.error(f"Error creating price chart: {e}")
            return "{}"
    
    def _create_indicators_chart(self, data: pd.DataFrame, analysis: Dict) -> str:
        """יוצר גרף אינדיקטורים"""
        try:
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=('RSI', 'MACD', 'Stochastic'),
                row_heights=[0.33, 0.33, 0.34]
            )
            
            # RSI
            rsi = analysis.get('advanced_indicators', {}).get('momentum_indicators', {}).get('rsi', {})
            if rsi:
                # סימולציה - בפועל זה יגיע מהנתונים האמיתיים
                rsi_values = [rsi.get('value', 50)] * len(data)
                
                fig.add_trace(
                    go.Scatter(x=data.index, y=rsi_values, name='RSI'),
                    row=1, col=1
                )
                
                # קווי overbought/oversold
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=1)
            
            # MACD
            macd = analysis.get('advanced_indicators', {}).get('momentum_indicators', {}).get('macd', {})
            if macd:
                # סימולציה
                macd_values = [macd.get('value', 0)] * len(data)
                signal_values = [macd.get('signal_line', 0)] * len(data)
                
                fig.add_trace(
                    go.Scatter(x=data.index, y=macd_values, name='MACD'),
                    row=2, col=1
                )
                fig.add_trace(
                    go.Scatter(x=data.index, y=signal_values, name='Signal'),
                    row=2, col=1
                )
            
            # Stochastic
            stoch = analysis.get('advanced_indicators', {}).get('momentum_indicators', {}).get('stochastic', {})
            if stoch:
                # סימולציה
                k_values = [stoch.get('k', 50)] * len(data)
                d_values = [stoch.get('d', 50)] * len(data)
                
                fig.add_trace(
                    go.Scatter(x=data.index, y=k_values, name='%K'),
                    row=3, col=1
                )
                fig.add_trace(
                    go.Scatter(x=data.index, y=d_values, name='%D'),
                    row=3, col=1
                )
                
                fig.add_hline(y=80, line_dash="dash", line_color="red", row=3, col=1)
                fig.add_hline(y=20, line_dash="dash", line_color="green", row=3, col=1)
            
            fig.update_layout(height=600, showlegend=True)
            return fig.to_json()
            
        except Exception as e:
            self.logger.error(f"Error creating indicators chart: {e}")
            return "{}"
    
    def _create_performance_chart(self, metrics: Dict) -> str:
        """יוצר גרף ביצועים"""
        try:
            # נתונים לדוגמה - בפועל זה יגיע מנתונים היסטוריים
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            returns = np.random.normal(0.001, 0.02, 30).cumsum()
            
            fig = go.Figure()
            
            fig.add_trace(
                go.Scatter(x=dates, y=returns, name='Cumulative Returns', 
                          line=dict(color='blue'))
            )
            
            fig.add_trace(
                go.Scatter(x=dates, y=[0]*30, name='Break Even', 
                          line=dict(color='red', dash='dash'))
            )
            
            fig.update_layout(
                title='Portfolio Performance',
                xaxis_title='Date',
                yaxis_title='Cumulative Return (%)',
                height=400
            )
            
            return fig.to_json()
            
        except Exception as e:
            self.logger.error(f"Error creating performance chart: {e}")
            return "{}"
    
    def _create_volume_chart(self, data: pd.DataFrame) -> str:
        """יוצר גרף ווליום מתקדם"""
        try:
            # חישוב ווליום moving average
            volume_ma = data['volume'].rolling(window=20).mean()
            
            fig = go.Figure()
            
            fig.add_trace(
                go.Bar(x=data.index, y=data['volume'], name='Volume', 
                      marker_color='lightblue')
            )
            
            fig.add_trace(
                go.Scatter(x=data.index, y=volume_ma, name='Volume MA (20)', 
                          line=dict(color='orange'))
            )
            
            fig.update_layout(
                title='Volume Analysis',
                xaxis_title='Date',
                yaxis_title='Volume',
                height=400
            )
            
            return fig.to_json()
            
        except Exception as e:
            self.logger.error(f"Error creating volume chart: {e}")
            return "{}"
    
    def _calculate_dashboard_stats(self, data: pd.DataFrame, 
                                 analysis: Dict, 
                                 metrics: Dict) -> Dict:
        """מחשב סטטיסטיקות לדשבורד"""
        try:
            current_price = data['close'].iloc[-1]
            price_24h_ago = data['close'].iloc[-24] if len(data) >= 24 else data['close'].iloc[0]
            price_change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
            
            high_24h = data['high'].tail(24).max()
            low_24h = data['low'].tail(24).min()
            volume_24h = data['volume'].tail(24).sum()
            
            technical_summary = analysis.get('summary', {})
            
            return {
                'current_price': round(current_price, 4),
                'price_change_24h': round(price_change_24h, 2),
                'price_change_24h_direction': 'up' if price_change_24h > 0 else 'down',
                'high_24h': round(high_24h, 4),
                'low_24h': round(low_24h, 4),
                'volume_24h': round(volume_24h, 0),
                'win_rate': metrics.get('win_rate', 0),
                'total_trades': metrics.get('total_trades', 0),
                'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                'current_signal': technical_summary.get('action', 'HOLD'),
                'signal_confidence': technical_summary.get('confidence', 0),
                'volatility': metrics.get('volatility', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating dashboard stats: {e}")
            return {}
    
    def _get_active_alerts(self, symbol: str) -> List[Dict]:
        """מביא התראות פעילות"""
        try:
            current_price = self.data_manager.get_current_price(symbol)
            return self.data_manager.check_alerts(symbol, current_price)
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}")
            return []
    
    def _get_empty_dashboard(self, symbol: str) -> Dict:
        """מחזיר דשבורד ריק במקרה של שגיאה"""
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'charts': {},
            'statistics': {},
            'recent_decisions': [],
            'technical_summary': {'action': 'HOLD', 'confidence': 0},
            'alerts': []
        }
    
    def create_admin_dashboard(self) -> Dict:
        """יוצר דשבורד מנהל"""
        try:
            admin_stats = self.payment_manager.get_admin_stats()
            db_stats = self.data_manager.get_database_stats()
            
            # גרף משתמשים
            users_fig = self._create_users_chart(admin_stats)
            
            # גרף הכנסות
            revenue_fig = self._create_revenue_chart(admin_stats)
            
            # סטטיסטיקות מערכת
            system_stats = self._get_system_stats()
            
            return {
                'users_chart': users_fig.to_json() if users_fig else "{}",
                'revenue_chart': revenue_fig.to_json() if revenue_fig else "{}",
                'admin_stats': admin_stats,
                'database_stats': db_stats,
                'system_stats': system_stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error creating admin dashboard: {e}")
            return {}
    
    def _create_users_chart(self, admin_stats: Dict) -> Optional[go.Figure]:
        """יוצר גרף משתמשים"""
        try:
            labels = ['Premium Users', 'Free Users']
            values = [admin_stats.get('premium_users', 0), 
                     admin_stats.get('free_users', 0)]
            
            fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
            fig.update_layout(title='User Distribution')
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating users chart: {e}")
            return None
    
    def _create_revenue_chart(self, admin_stats: Dict) -> Optional[go.Figure]:
        """יוצר גרף הכנסות"""
        try:
            # נתונים לדוגמה - בפועל זה יגיע מנתונים היסטוריים
            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            revenue = np.random.normal(100, 20, 30).cumsum()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=revenue, name='Cumulative Revenue'))
            fig.update_layout(title='Revenue Over Time', xaxis_title='Date', yaxis_title='Revenue ($)')
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating revenue chart: {e}")
            return None
    
    def _get_system_stats(self) -> Dict:
        """מביא סטטיסטיקות מערכת"""
        try:
            import psutil
            import platform
            
            return {
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'uptime': self._get_system_uptime()
            }
        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return {}
    
    def _get_system_uptime(self) -> str:
        """מחשב זמן פעילות המערכת"""
        try:
            import psutil
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.now().timestamp() - boot_time
            uptime_hours = uptime_seconds / 3600
            
            if uptime_hours < 1:
                return f"{int(uptime_seconds / 60)} minutes"
            elif uptime_hours < 24:
                return f"{int(uptime_hours)} hours"
            else:
                return f"{int(uptime_hours / 24)} days"
                
        except:
            return "Unknown"

# Flask Dashboard App
def create_dashboard_app(data_manager: AdvancedDataManager,
                        technical_analyzer: AdvancedTechnicalAnalyzer,
                        payment_manager: PaymentManager):
    """יוצר אפליקציית Flask עבור הדשבורד"""
    
    app = Flask(__name__)
    dashboard = TradingDashboard(data_manager, technical_analyzer, payment_manager)
    
    @app.route('/')
    def index():
        """דף הבית של הדשבורד"""
        return render_template('index.html')
    
    @app.route('/api/dashboard/<symbol>')
    def get_dashboard_data(symbol):
        """מחזיר נתוני דשבורד ב-JSON"""
        try:
            dashboard_data = dashboard.create_main_dashboard(symbol)
            return jsonify(dashboard_data)
        except Exception as e:
            logging.error(f"Error getting dashboard data: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin-dashboard')
    def get_admin_dashboard():
        """מחזיר דשבורד מנהל"""
        try:
            admin_dashboard = dashboard.create_admin_dashboard()
            return jsonify(admin_dashboard)
        except Exception as e:
            logging.error(f"Error getting admin dashboard: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/symbols')
    def get_available_symbols():
        """מחזיר רשימת סימלים זמינים"""
        try:
            symbols = ['TONUSDT', 'BNBUSDT', 'BTCUSDT', 'ETHUSDT']
            return jsonify({'symbols': symbols})
        except Exception as e:
            logging.error(f"Error getting symbols: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/performance/<symbol>')
    def get_performance_data(symbol):
        """מחזיר נתוני ביצועים"""
        try:
            metrics = data_manager.calculate_performance_metrics(symbol)
            return jsonify(metrics)
        except Exception as e:
            logging.error(f"Error getting performance data: {e}")
            return jsonify({'error': str(e)}), 500
    
    return app
