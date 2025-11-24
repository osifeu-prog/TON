import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import logging
import os
import json
from typing import Dict, List, Optional, Any
import pickle
import hashlib
from contextlib import contextmanager

class AdvancedDataManager:
    def __init__(self):
        self.conn = sqlite3.connect('database/market_data.db', check_same_thread=False)
        self.cache_conn = sqlite3.connect('database/cache.db', check_same_thread=False)
        self.setup_database()
        self.logger = logging.getLogger(__name__)
        self.cache_enabled = True
        self.setup_cache()
        
    def setup_database(self):
        """מאתחל את מסדי הנתונים עם טבלאות מתקדמות"""
        cursor = self.conn.cursor()
        
        # טבלת נתוני שוק מורחבת
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                quote_asset_volume REAL,
                number_of_trades INTEGER,
                taker_buy_base_asset_volume REAL,
                taker_buy_quote_asset_volume REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp)
            )
        ''')
        
        # טבלת ניתוחים טכניים
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technical_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                analysis_type TEXT NOT NULL,
                analysis_data TEXT NOT NULL,
                time_frame TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp, analysis_type, time_frame)
            )
        ''')
        
        # טבלת החלטות מסחר
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                action TEXT NOT NULL,
                confidence REAL,
                price REAL,
                indicators TEXT,
                risk_level TEXT,
                position_size REAL,
                stop_loss REAL,
                take_profit REAL,
                explanations TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # טבלת ביצועים
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                period TEXT NOT NULL,
                win_rate REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                total_return REAL,
                volatility REAL,
                trades_count INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp, period)
            )
        ''')
        
        # טבלת התראות
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                trigger_price REAL,
                current_price REAL,
                condition TEXT,
                message TEXT,
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                triggered_at DATETIME
            )
        ''')
        
        # טבלת משתמשים ופעילות
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity_type TEXT,
                symbol TEXT,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        
    def setup_cache(self):
        """מאתחל את מערכת ה-cache"""
        cursor = self.cache_conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value BLOB NOT NULL,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cache_conn.commit()
    
    @contextmanager
    def get_cursor(self, connection):
        """נותן cursor עם טיפול בשגיאות"""
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        except Exception as e:
            connection.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
    
    def save_market_data(self, symbol: str, data: pd.DataFrame, data_type: str = 'klines'):
        """שומר נתוני שוק במסד הנתונים"""
        try:
            with self.get_cursor(self.conn) as cursor:
                for index, row in data.iterrows():
                    cursor.execute('''
                        INSERT OR REPLACE INTO market_data 
                        (symbol, timestamp, open, high, low, close, volume,
                         quote_asset_volume, number_of_trades,
                         taker_buy_base_asset_volume, taker_buy_quote_asset_volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        symbol, index, row['open'], row['high'], row['low'],
                        row['close'], row['volume'], row.get('quote_asset_volume', 0),
                        row.get('number_of_trades', 0),
                        row.get('taker_buy_base_asset_volume', 0),
                        row.get('taker_buy_quote_asset_volume', 0)
                    ))
            
            self.logger.info(f"💾 Saved market data for {symbol} - {len(data)} records")
            
        except Exception as e:
            self.logger.error(f"Error saving market data: {e}")
    
    def save_technical_analysis(self, symbol: str, analysis_type: str, 
                              analysis_data: Dict, time_frame: str = '1h'):
        """שומר ניתוח טכני"""
        try:
            timestamp = datetime.now()
            
            with self.get_cursor(self.conn) as cursor:
                cursor.execute('''
                    INSERT OR REPLACE INTO technical_analysis 
                    (symbol, timestamp, analysis_type, analysis_data, time_frame)
                    VALUES (?, ?, ?, ?, ?)
                ''', (symbol, timestamp, analysis_type, 
                     json.dumps(analysis_data, ensure_ascii=False), time_frame))
            
            # שמירה ב-cache
            cache_key = f"ta_{symbol}_{analysis_type}_{time_frame}"
            self.set_cache(cache_key, analysis_data, expires_minutes=15)
            
            self.logger.info(f"💾 Saved technical analysis for {symbol} - {analysis_type}")
            
        except Exception as e:
            self.logger.error(f"Error saving technical analysis: {e}")
    
    def save_trading_decision(self, symbol: str, action: str, confidence: float,
                            price: float, indicators: Dict, risk_level: str,
                            position_size: float, stop_loss: float, 
                            take_profit: float, explanations: List[str]):
        """שומר החלטת מסחר"""
        try:
            with self.get_cursor(self.conn) as cursor:
                cursor.execute('''
                    INSERT INTO trading_decisions 
                    (symbol, timestamp, action, confidence, price, indicators,
                     risk_level, position_size, stop_loss, take_profit, explanations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, datetime.now(), action, confidence, price,
                    json.dumps(indicators, ensure_ascii=False), risk_level,
                    position_size, stop_loss, take_profit,
                    json.dumps(explanations, ensure_ascii=False)
                ))
            
            self.logger.info(f"💾 Saved trading decision for {symbol}: {action}")
            
        except Exception as e:
            self.logger.error(f"Error saving trading decision: {e}")
    
    def get_historical_data(self, symbol: str, days: int = 30, 
                          interval: str = '1h') -> pd.DataFrame:
        """מביא נתונים היסטוריים"""
        try:
            cache_key = f"hist_{symbol}_{days}_{interval}"
            cached_data = self.get_cache(cache_key)
            
            if cached_data is not None:
                self.logger.info(f"📂 Using cached historical data for {symbol}")
                return pd.DataFrame(cached_data)
            
            query = '''
                SELECT timestamp, open, high, low, close, volume
                FROM market_data 
                WHERE symbol = ? AND timestamp >= datetime('now', ?)
                ORDER BY timestamp
            '''
            
            df = pd.read_sql_query(
                query, self.conn, 
                params=(symbol, f'-{days} days'),
                parse_dates=['timestamp'],
                index_col='timestamp'
            )
            
            # שמירה ב-cache
            if not df.empty:
                self.set_cache(cache_key, df.to_dict('records'), expires_minutes=60)
            
            self.logger.info(f"📊 Loaded historical data for {symbol}: {len(df)} records")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading historical data: {e}")
            return pd.DataFrame()
    
    def get_technical_analysis(self, symbol: str, analysis_type: str, 
                             time_frame: str = '1h') -> Optional[Dict]:
        """מביא ניתוח טכני"""
        try:
            cache_key = f"ta_{symbol}_{analysis_type}_{time_frame}"
            cached_analysis = self.get_cache(cache_key)
            
            if cached_analysis is not None:
                return cached_analysis
            
            with self.get_cursor(self.conn) as cursor:
                cursor.execute('''
                    SELECT analysis_data FROM technical_analysis
                    WHERE symbol = ? AND analysis_type = ? AND time_frame = ?
                    ORDER BY timestamp DESC LIMIT 1
                ''', (symbol, analysis_type, time_frame))
                
                result = cursor.fetchone()
                if result:
                    analysis_data = json.loads(result[0])
                    self.set_cache(cache_key, analysis_data, expires_minutes=15)
                    return analysis_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting technical analysis: {e}")
            return None
    
    def get_recent_decisions(self, symbol: str, hours: int = 24) -> List[Dict]:
        """מביא החלטות מסחר אחרונות"""
        try:
            with self.get_cursor(self.conn) as cursor:
                cursor.execute('''
                    SELECT action, confidence, price, indicators, risk_level,
                           position_size, stop_loss, take_profit, explanations, timestamp
                    FROM trading_decisions
                    WHERE symbol = ? AND timestamp >= datetime('now', ?)
                    ORDER BY timestamp DESC
                ''', (symbol, f'-{hours} hours'))
                
                decisions = []
                for row in cursor.fetchall():
                    decisions.append({
                        'action': row[0],
                        'confidence': row[1],
                        'price': row[2],
                        'indicators': json.loads(row[3]) if row[3] else {},
                        'risk_level': row[4],
                        'position_size': row[5],
                        'stop_loss': row[6],
                        'take_profit': row[7],
                        'explanations': json.loads(row[8]) if row[8] else [],
                        'timestamp': row[9]
                    })
                
                return decisions
                
        except Exception as e:
            self.logger.error(f"Error getting recent decisions: {e}")
            return []
    
    def calculate_performance_metrics(self, symbol: str, period: str = '30d') -> Dict:
        """מחשב מדדי ביצועים"""
        try:
            cache_key = f"perf_{symbol}_{period}"
            cached_metrics = self.get_cache(cache_key)
            
            if cached_metrics is not None:
                return cached_metrics
            
            with self.get_cursor(self.conn) as cursor:
                cursor.execute('''
                    SELECT action, confidence, price, timestamp
                    FROM trading_decisions
                    WHERE symbol = ? AND timestamp >= datetime('now', ?)
                    ORDER BY timestamp
                ''', (symbol, f'-{period}'))
                
                decisions = cursor.fetchall()
                
                if not decisions:
                    return self._get_default_performance_metrics()
                
                # חישוב מדדים מתקדמים
                metrics = self._calculate_advanced_metrics(decisions)
                
                # שמירה ב-cache
                self.set_cache(cache_key, metrics, expires_minutes=30)
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return self._get_default_performance_metrics()
    
    def _calculate_advanced_metrics(self, decisions: List) -> Dict:
        """מחשב מדדי ביצועים מתקדמים"""
        try:
            if not decisions:
                return self._get_default_performance_metrics()
            
            total_trades = len(decisions)
            winning_trades = 0
            total_return = 0
            trade_returns = []
            confidence_scores = []
            
            for i in range(1, len(decisions)):
                prev_decision = decisions[i-1]
                current_decision = decisions[i]
                
                if prev_decision[0] in ['BUY', 'STRONG_BUY']:
                    price_change = (current_decision[2] - prev_decision[2]) / prev_decision[2]
                    trade_returns.append(price_change)
                    confidence_scores.append(prev_decision[1])
                    
                    if price_change > 0:
                        winning_trades += 1
                    total_return += price_change
            
            win_rate = (winning_trades / len(trade_returns)) * 100 if trade_returns else 0
            
            # חישוב מדדים נוספים
            sharpe_ratio = self._calculate_sharpe_ratio(trade_returns)
            max_drawdown = self._calculate_max_drawdown(trade_returns)
            volatility = np.std(trade_returns) * 100 if trade_returns else 0
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
            
            return {
                'win_rate': round(win_rate, 1),
                'total_return': round(total_return * 100, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown': round(max_drawdown * 100, 2),
                'volatility': round(volatility, 2),
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': len(trade_returns) - winning_trades,
                'avg_confidence': round(avg_confidence, 3),
                'best_trade': round(max(trade_returns) * 100, 2) if trade_returns else 0,
                'worst_trade': round(min(trade_returns) * 100, 2) if trade_returns else 0,
                'profit_factor': self._calculate_profit_factor(trade_returns)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating advanced metrics: {e}")
            return self._get_default_performance_metrics()
    
    def _calculate_sharpe_ratio(self, returns: List[float]) -> float:
        """מחשב Sharpe ratio"""
        if not returns:
            return 0.0
        excess_returns = np.array(returns) - 0.02/252  # Assume 2% risk-free rate
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """מחשב maximum drawdown"""
        if not returns:
            return 0.0
        cumulative = np.cumprod(1 + np.array(returns))
        peak = np.maximum.accumulate(cumulative)
        drawdown = (peak - cumulative) / peak
        return np.max(drawdown)
    
    def _calculate_profit_factor(self, returns: List[float]) -> float:
        """מחשב profit factor"""
        if not returns:
            return 0.0
        gross_profit = sum(r for r in returns if r > 0)
        gross_loss = abs(sum(r for r in returns if r < 0))
        return gross_profit / gross_loss if gross_loss != 0 else float('inf')
    
    def _get_default_performance_metrics(self) -> Dict:
        """מחזיר מדדי ביצועים ברירת מחדל"""
        return {
            'win_rate': 0,
            'total_return': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'volatility': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'avg_confidence': 0,
            'best_trade': 0,
            'worst_trade': 0,
            'profit_factor': 0
        }
    
    def set_cache(self, key: str, value: Any, expires_minutes: int = 30):
        """שומר נתונים ב-cache"""
        if not self.cache_enabled:
            return
            
        try:
            expires_at = datetime.now() + timedelta(minutes=expires_minutes)
            
            with self.get_cursor(self.cache_conn) as cursor:
                cursor.execute('''
                    INSERT OR REPLACE INTO cache (key, value, expires_at)
                    VALUES (?, ?, ?)
                ''', (key, pickle.dumps(value), expires_at))
                
        except Exception as e:
            self.logger.error(f"Error setting cache: {e}")
    
    def get_cache(self, key: str) -> Optional[Any]:
        """מביא נתונים מ-cache"""
        if not self.cache_enabled:
            return None
            
        try:
            with self.get_cursor(self.cache_conn) as cursor:
                cursor.execute('''
                    SELECT value FROM cache 
                    WHERE key = ? AND expires_at > datetime('now')
                ''', (key,))
                
                result = cursor.fetchone()
                if result:
                    return pickle.loads(result[0])
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting cache: {e}")
            return None
    
    def clear_expired_cache(self):
        """מנקה cache שפג תוקפו"""
        try:
            with self.get_cursor(self.cache_conn) as cursor:
                cursor.execute('DELETE FROM cache WHERE expires_at <= datetime("now")')
                
            self.logger.info("🧹 Cleared expired cache entries")
            
        except Exception as e:
            self.logger.error(f"Error clearing expired cache: {e}")
    
    def log_user_activity(self, user_id: int, activity_type: str, 
                         symbol: str = None, details: Dict = None):
        """רושם פעילות משתמש"""
        try:
            with self.get_cursor(self.conn) as cursor:
                cursor.execute('''
                    INSERT INTO user_activity 
                    (user_id, activity_type, symbol, details)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, activity_type, symbol, 
                     json.dumps(details, ensure_ascii=False) if details else None))
                
        except Exception as e:
            self.logger.error(f"Error logging user activity: {e}")
    
    def get_user_activity_stats(self, user_id: int, days: int = 7) -> Dict:
        """מביא סטטיסטיקות פעילות משתמש"""
        try:
            with self.get_cursor(self.conn) as cursor:
                cursor.execute('''
                    SELECT activity_type, COUNT(*) as count
                    FROM user_activity
                    WHERE user_id = ? AND timestamp >= datetime('now', ?)
                    GROUP BY activity_type
                ''', (user_id, f'-{days} days'))
                
                activity_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                cursor.execute('''
                    SELECT symbol, COUNT(*) as count
                    FROM user_activity
                    WHERE user_id = ? AND timestamp >= datetime('now', ?)
                    GROUP BY symbol
                    ORDER BY count DESC
                    LIMIT 5
                ''', (user_id, f'-{days} days'))
                
                top_symbols = {row[0]: row[1] for row in cursor.fetchall()}
                
                return {
                    'activity_counts': activity_counts,
                    'top_symbols': top_symbols,
                    'period_days': days
                }
                
        except Exception as e:
            self.logger.error(f"Error getting user activity stats: {e}")
            return {}
    
    def create_alert(self, symbol: str, alert_type: str, trigger_price: float,
                   condition: str, message: str):
        """יוצר התראה חדשה"""
        try:
            current_price = self.get_current_price(symbol)
            
            with self.get_cursor(self.conn) as cursor:
                cursor.execute('''
                    INSERT INTO alerts 
                    (symbol, alert_type, trigger_price, current_price, condition, message)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (symbol, alert_type, trigger_price, current_price, condition, message))
                
            self.logger.info(f"🔔 Created alert for {symbol}: {alert_type}")
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
    
    def check_alerts(self, symbol: str, current_price: float) -> List[Dict]:
        """בודק אם יש התראות שצריכות להתפעל"""
        try:
            with self.get_cursor(self.conn) as cursor:
                cursor.execute('''
                    SELECT * FROM alerts
                    WHERE symbol = ? AND status = 'active'
                ''', (symbol,))
                
                alerts = []
                for row in cursor.fetchall():
                    alert_id, _, alert_type, trigger_price, _, condition, message, status, created_at, triggered_at = row
                    
                    # בדיקת תנאי
                    should_trigger = False
                    if condition == 'above' and current_price >= trigger_price:
                        should_trigger = True
                    elif condition == 'below' and current_price <= trigger_price:
                        should_trigger = True
                    elif condition == 'cross_above' and current_price >= trigger_price:
                        should_trigger = True
                    elif condition == 'cross_below' and current_price <= trigger_price:
                        should_trigger = True
                    
                    if should_trigger:
                        alerts.append({
                            'alert_id': alert_id,
                            'alert_type': alert_type,
                            'trigger_price': trigger_price,
                            'current_price': current_price,
                            'message': message
                        })
                        
                        # עדכון סטטוס ההתראה
                        cursor.execute('''
                            UPDATE alerts 
                            SET status = 'triggered', triggered_at = datetime('now')
                            WHERE id = ?
                        ''', (alert_id,))
                
                return alerts
                
        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
            return []
    
    def get_current_price(self, symbol: str) -> float:
        """מביא מחיר נוכחי"""
        try:
            with self.get_cursor(self.conn) as cursor:
                cursor.execute('''
                    SELECT close FROM market_data
                    WHERE symbol = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''', (symbol,))
                
                result = cursor.fetchone()
                return result[0] if result else 0.0
                
        except Exception as e:
            self.logger.error(f"Error getting current price: {e}")
            return 0.0
    
    def backup_database(self, backup_path: str = None):
        """יוצר גיבוי של מסד הנתונים"""
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f'backups/market_data_backup_{timestamp}.db'
            
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # יצירת גיבוי
            backup_conn = sqlite3.connect(backup_path)
            self.conn.backup(backup_conn)
            backup_conn.close()
            
            self.logger.info(f"💾 Database backed up to: {backup_path}")
            
        except Exception as e:
            self.logger.error(f"Error backing up database: {e}")
    
    def optimize_database(self):
        """מבצע אופטימיזציה למסד הנתונים"""
        try:
            with self.get_cursor(self.conn) as cursor:
                cursor.execute('VACUUM')
                cursor.execute('ANALYZE')
            
            self.logger.info("🔧 Database optimized")
            
        except Exception as e:
            self.logger.error(f"Error optimizing database: {e}")
    
    def get_database_stats(self) -> Dict:
        """מביא סטטיסטיקות מסד נתונים"""
        try:
            with self.get_cursor(self.conn) as cursor:
                # ספירת רשומות
                cursor.execute('SELECT COUNT(*) FROM market_data')
                market_data_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM technical_analysis')
                technical_analysis_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM trading_decisions')
                trading_decisions_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(DISTINCT symbol) FROM market_data')
                symbols_count = cursor.fetchone()[0]
                
                # גודל מסד נתונים
                cursor.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
                db_size = cursor.fetchone()[0]
                
                return {
                    'market_data_records': market_data_count,
                    'technical_analysis_records': technical_analysis_count,
                    'trading_decisions_records': trading_decisions_count,
                    'unique_symbols': symbols_count,
                    'database_size_mb': round(db_size / (1024 * 1024), 2),
                    'last_optimized': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return {}
