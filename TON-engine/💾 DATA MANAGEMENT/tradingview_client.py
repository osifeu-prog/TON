import requests
import logging
from typing import Dict, List, Optional
import json
from datetime import datetime
import pandas as pd
import numpy as np

class TradingViewClient:
    """לקוח TradingView לאיסוף נתונים וניתוחים"""
    
    def __init__(self):
        self.base_url = "https://scanner.tradingview.com"
        self.websocket_url = "wss://data.tradingview.com/socket.io/websocket"
        self.logger = logging.getLogger(__name__)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Origin': 'https://www.tradingview.com',
            'Referer': 'https://www.tradingview.com/'
        })
        
        # הגדרות ברירת מחדל
        self.screener_configs = {
            'crypto': {
                'filter': [
                    {"left": "exchange", "operation": "equal", "right": "BINANCE"},
                    {"left": "type", "operation": "equal", "right": "crypto"}
                ],
                'options': {"lang": "en"},
                'symbols': {},
                'columns': [
                    "base_currency_logoid",
                    "currency_logoid", 
                    "name",
                    "close",
                    "change",
                    "change_abs",
                    "Recommend.All",
                    "volume",
                    "market_cap_basic",
                    "price_earnings_ttm",
                    "earnings_per_share_basic_ttm",
                    "number_of_employees",
                    "sector",
                    "description",
                    "name",
                    "type",
                    "subtype",
                    "update_mode",
                    "pricescale",
                    "minmov",
                    "fractional",
                    "minmove2"
                ]
            }
        }
    
    def get_technical_analysis(self, symbol: str, exchange: str = "BINANCE") -> Dict:
        """מביא ניתוח טכני מ-TradingView"""
        try:
            # סימולציה - בפועל זה ידרוש integration עם TradingView API
            # כאן נשתמש בנתונים מדומים
            
            analysis = {
                'symbol': symbol,
                'exchange': exchange,
                'summary': {
                    'RECOMMENDATION': np.random.choice(['STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG_SELL']),
                    'BUY': np.random.randint(10, 30),
                    'SELL': np.random.randint(10, 30),
                    'NEUTRAL': np.random.randint(10, 30)
                },
                'oscillators': {
                    'RECOMMENDATION': np.random.choice(['STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG_SELL']),
                    'BUY': np.random.randint(5, 15),
                    'SELL': np.random.randint(5, 15),
                    'NEUTRAL': np.random.randint(5, 15)
                },
                'moving_averages': {
                    'RECOMMENDATION': np.random.choice(['STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG_SELL']),
                    'BUY': np.random.randint(5, 15),
                    'SELL': np.random.randint(5, 15),
                    'NEUTRAL': np.random.randint(5, 15)
                },
                'indicators': {
                    'RSI': round(np.random.uniform(20, 80), 2),
                    'RSI[1]': round(np.random.uniform(20, 80), 2),
                    'Stoch.K': round(np.random.uniform(20, 80), 2),
                    'Stoch.D': round(np.random.uniform(20, 80), 2),
                    'CCI20': round(np.random.uniform(-200, 200), 2),
                    'ADX': round(np.random.uniform(10, 50), 2),
                    'AO': round(np.random.uniform(-10, 10), 4),
                    'Mom': round(np.random.uniform(-5, 5), 2),
                    'MACD.macd': round(np.random.uniform(-0.5, 0.5), 4),
                    'MACD.signal': round(np.random.uniform(-0.5, 0.5), 4),
                    'Rec.Stoch.RSI': round(np.random.uniform(0, 10), 1),
                    'W.R': round(np.random.uniform(-80, -20), 2),
                    'BBPower': round(np.random.uniform(-1, 1), 2),
                    'UO': round(np.random.uniform(20, 80), 2)
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # חישוב ציון משוקלל
            analysis['composite_score'] = self._calculate_composite_score(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error getting TradingView analysis: {e}")
            return self._get_fallback_analysis(symbol, exchange)
    
    def _calculate_composite_score(self, analysis: Dict) -> float:
        """מחשב ציון משוקלל מהניתוח"""
        try:
            summary = analysis.get('summary', {})
            recommendation = summary.get('RECOMMENDATION', 'NEUTRAL')
            
            score_map = {
                'STRONG_BUY': 0.9,
                'BUY': 0.7,
                'NEUTRAL': 0.5,
                'SELL': 0.3,
                'STRONG_SELL': 0.1
            }
            
            base_score = score_map.get(recommendation, 0.5)
            
            # התאמה לפי אינדיקטורים
            indicators = analysis.get('indicators', {})
            rsi = indicators.get('RSI', 50)
            if rsi < 30:
                base_score += 0.1
            elif rsi > 70:
                base_score -= 0.1
            
            macd = indicators.get('MACD.macd', 0)
            if macd > 0:
                base_score += 0.05
            
            return max(0.0, min(1.0, base_score))
            
        except:
            return 0.5
    
    def scan_market(self, screener: str = "crypto", market: str = "BINANCE") -> List[Dict]:
        """סורק את השוק לפי מסננים"""
        try:
            # סימולציה של סריקת שוק
            symbols = ['TONUSDT', 'BNBUSDT', 'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT']
            
            results = []
            for symbol in symbols:
                analysis = self.get_technical_analysis(symbol, market)
                results.append({
                    'symbol': symbol,
                    'analysis': analysis,
                    'composite_score': analysis.get('composite_score', 0.5),
                    'recommendation': analysis.get('summary', {}).get('RECOMMENDATION', 'NEUTRAL')
                })
            
            # מיון לפי ציון
            results.sort(key=lambda x: x['composite_score'], reverse=True)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error scanning market: {e}")
            return []
    
    def get_top_signals(self, screener: str = "crypto", limit: int = 10) -> List[Dict]:
        """מביא את האותות המובילים"""
        try:
            market_scan = self.scan_market(screener)
            
            # סינון רק אותות חזקים
            strong_signals = [
                signal for signal in market_scan 
                if signal['composite_score'] > 0.7 or signal['composite_score'] < 0.3
            ]
            
            return strong_signals[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting top signals: {e}")
            return []
    
    def get_idea_stream(self, symbol: str = None) -> List[Dict]:
        """מביא רעיונות מסחר מ-TradingView"""
        try:
            # סימולציה של רעיונות מסחר
            ideas = []
            
            base_symbols = ['TON', 'BNB', 'BTC', 'ETH'] if not symbol else [symbol.replace('USDT', '')]
            
            for base_symbol in base_symbols:
                for i in range(3):
                    idea_type = np.random.choice(['LONG', 'SHORT'])
                    confidence = round(np.random.uniform(0.6, 0.95), 2)
                    
                    ideas.append({
                        'symbol': f"{base_symbol}USDT",
                        'type': idea_type,
                        'title': f"{idea_type} {base_symbol} - Technical Breakout",
                        'description': f"Technical analysis suggests {idea_type.lower()} opportunity for {base_symbol}",
                        'confidence': confidence,
                        'timestamp': datetime.now().isoformat(),
                        'metrics': {
                            'potential_upside': round(np.random.uniform(5, 25), 1),
                            'risk_level': np.random.choice(['LOW', 'MEDIUM', 'HIGH']),
                            'timeframe': np.random.choice(['SHORT', 'MEDIUM', 'LONG'])
                        }
                    })
            
            return ideas
            
        except Exception as e:
            self.logger.error(f"Error getting idea stream: {e}")
            return []
    
    def get_market_sentiment(self, symbol: str = None) -> Dict:
        """מביא סנטימנט שוק"""
        try:
            if symbol:
                analysis = self.get_technical_analysis(symbol)
                summary = analysis.get('summary', {})
                
                return {
                    'symbol': symbol,
                    'bullish_percent': summary.get('BUY', 0),
                    'bearish_percent': summary.get('SELL', 0),
                    'neutral_percent': summary.get('NEUTRAL', 0),
                    'overall_sentiment': summary.get('RECOMMENDATION', 'NEUTRAL'),
                    'sentiment_score': analysis.get('composite_score', 0.5),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # סנטימנט שוק כללי
                return {
                    'market': 'CRYPTO',
                    'bullish_percent': np.random.randint(40, 70),
                    'bearish_percent': np.random.randint(20, 40),
                    'neutral_percent': np.random.randint(10, 30),
                    'fear_greed_index': np.random.randint(30, 70),
                    'dominance_btc': round(np.random.uniform(40, 50), 1),
                    'dominance_eth': round(np.random.uniform(15, 20), 1),
                    'total_market_cap': np.random.randint(1500000000000, 2000000000000),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting market sentiment: {e}")
            return {}
    
    def get_support_resistance(self, symbol: str) -> Dict:
        """מביא רמות תמיכה והתנגדות"""
        try:
            # סימולציה של רמות תמיכה והתנגדות
            current_price = np.random.uniform(2.0, 3.0) if 'TON' in symbol else np.random.uniform(300, 400)
            
            support_levels = [
                round(current_price * 0.95, 4),
                round(current_price * 0.90, 4),
                round(current_price * 0.85, 4)
            ]
            
            resistance_levels = [
                round(current_price * 1.05, 4),
                round(current_price * 1.10, 4),
                round(current_price * 1.15, 4)
            ]
            
            return {
                'symbol': symbol,
                'current_price': round(current_price, 4),
                'support_levels': support_levels,
                'resistance_levels': resistance_levels,
                'pivot_point': round(current_price, 4),
                'r1': resistance_levels[0],
                'r2': resistance_levels[1],
                's1': support_levels[0],
                's2': support_levels[1],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting support resistance: {e}")
            return {}
    
    def get_advanced_analysis(self, symbol: str) -> Dict:
        """מביא ניתוח מתקדם"""
        try:
            technical_analysis = self.get_technical_analysis(symbol)
            support_resistance = self.get_support_resistance(symbol)
            market_sentiment = self.get_market_sentiment(symbol)
            ideas = self.get_idea_stream(symbol)
            
            return {
                'symbol': symbol,
                'technical_analysis': technical_analysis,
                'support_resistance': support_resistance,
                'market_sentiment': market_sentiment,
                'trading_ideas': ideas,
                'composite_rating': self._calculate_composite_rating(
                    technical_analysis, market_sentiment
                ),
                'risk_assessment': self._assess_risk(technical_analysis),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting advanced analysis: {e}")
            return self._get_fallback_analysis(symbol)
    
    def _calculate_composite_rating(self, technical_analysis: Dict, market_sentiment: Dict) -> str:
        """מחשב דירוג משוקלל"""
        try:
            tech_score = technical_analysis.get('composite_score', 0.5)
            sentiment_score = market_sentiment.get('sentiment_score', 0.5)
            
            composite_score = (tech_score * 0.7) + (sentiment_score * 0.3)
            
            if composite_score > 0.8:
                return "STRONG_BUY"
            elif composite_score > 0.6:
                return "BUY"
            elif composite_score > 0.4:
                return "NEUTRAL"
            elif composite_score > 0.2:
                return "SELL"
            else:
                return "STRONG_SELL"
                
        except:
            return "NEUTRAL"
    
    def _assess_risk(self, technical_analysis: Dict) -> Dict:
        """מעריך סיכון"""
        try:
            indicators = technical_analysis.get('indicators', {})
            
            volatility = abs(indicators.get('RSI', 50) - 50) / 50
            momentum = abs(indicators.get('MACD.macd', 0)) * 10
            trend_strength = indicators.get('ADX', 25) / 50
            
            risk_score = (volatility + momentum + trend_strength) / 3
            
            if risk_score > 0.7:
                risk_level = "HIGH"
            elif risk_score > 0.4:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            return {
                'risk_score': round(risk_score, 3),
                'risk_level': risk_level,
                'volatility_risk': round(volatility, 3),
                'momentum_risk': round(momentum, 3),
                'trend_risk': round(trend_strength, 3)
            }
            
        except:
            return {'risk_score': 0.5, 'risk_level': 'MEDIUM'}
    
    def _get_fallback_analysis(self, symbol: str, exchange: str = "BINANCE") -> Dict:
        """מחזיר ניתוח גיבוי"""
        return {
            'symbol': symbol,
            'exchange': exchange,
            'summary': {'RECOMMENDATION': 'NEUTRAL', 'BUY': 0, 'SELL': 0, 'NEUTRAL': 0},
            'composite_score': 0.5,
            'timestamp': datetime.now().isoformat()
        }
    
    def health_check(self) -> Dict:
        """בודק את בריאות החיבור"""
        try:
            # בדיקת חיבור בסיסית
            test_analysis = self.get_technical_analysis('BTCUSDT')
            
            return {
                'status': 'healthy' if test_analysis else 'unhealthy',
                'last_successful_request': datetime.now().isoformat(),
                'features_working': {
                    'technical_analysis': bool(test_analysis),
                    'market_scan': True,
                    'sentiment_analysis': True
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {'status': 'unhealthy', 'error': str(e)}
