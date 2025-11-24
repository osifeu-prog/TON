import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple
import requests
import hashlib
import hmac
import time
from urllib.parse import urlencode
import os
import ta
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, EMAIndicator, ADXIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice, OnBalanceVolumeIndicator

class AdvancedTradingLogic:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # קריאת מפתחות API מ-Environment Variables
        self.binance_api_key = os.getenv('BINANCE_API_KEY', '')
        self.binance_secret_key = os.getenv('BINANCE_SECRET_KEY', '')
        
        self.base_url = "https://api.binance.com/api/v3"
        
        # בדיקה אם המפתחות הוגדרו
        if not self.binance_api_key or not self.binance_secret_key:
            self.logger.warning("⚠️ Binance API keys not configured - using advanced simulation mode")
            self.api_available = False
        else:
            self.logger.info("✅ Advanced Trading Logic initialized with Binance API")
            self.api_available = True
        
        # הגדרות מתקדמות
        self.risk_config = {
            'max_position_size': 5.0,  # % מתיק
            'stop_loss_percent': 2.0,
            'take_profit_percent': 4.0,
            'daily_loss_limit': 3.0,
            'risk_per_trade': 1.0
        }
        
        self.ml_weights = {
            'technical': 0.4,
            'sentiment': 0.3,
            'market_structure': 0.2,
            'volume_analysis': 0.1
        }
        
        self.symbol_configs = {
            'TONUSDT': {'volatility': 'high', 'spread': 0.001, 'lot_size': 1.0},
            'BNBUSDT': {'volatility': 'medium', 'spread': 0.002, 'lot_size': 0.1},
            'BTCUSDT': {'volatility': 'low', 'spread': 0.0005, 'lot_size': 0.001}
        }
    
    def _binance_request(self, endpoint: str, params: Dict = None, signed: bool = False) -> Dict:
        """בקשה מתקדמת ל-Binance API"""
        if not self.api_available:
            return self._advanced_simulation(endpoint, params)
            
        try:
            url = f"{self.base_url}/{endpoint}"
            headers = {"X-MBX-APIKEY": self.binance_api_key}
            
            if signed and params:
                params['timestamp'] = int(time.time() * 1000)
                query_string = urlencode(params)
                signature = hmac.new(
                    self.binance_secret_key.encode('utf-8'),
                    query_string.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                params['signature'] = signature
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Binance API error: {e}")
            return self._advanced_simulation(endpoint, params)
    
    def _advanced_simulation(self, endpoint: str, params: Dict = None) -> Dict:
        """סימולציה מתקדמת כאשר ה-API לא זמין"""
        symbol = params.get('symbol', 'TONUSDT') if params else 'TONUSDT'
        
        if endpoint == "ticker/price":
            return self._simulate_real_time_price(symbol)
        elif endpoint == "ticker/24hr":
            return self._simulate_24h_stats(symbol)
        elif endpoint == "klines":
            return self._simulate_advanced_klines(symbol, params.get('limit', 100), params.get('interval', '1h'))
        elif endpoint == "depth":
            return self._simulate_order_book(symbol)
        else:
            return {}
    
    def _simulate_real_time_price(self, symbol: str) -> Dict:
        """סימולצית מחיר ריאליסטית"""
        base_prices = {
            'TONUSDT': 2.45,
            'BNBUSDT': 320.0,
            'BTCUSDT': 43000.0
        }
        
        base_price = base_prices.get(symbol, 2.45)
        
        # סימולציית תנודתיות ריאליסטית
        volatility = self.symbol_configs.get(symbol, {}).get('volatility', 'medium')
        volatility_multiplier = {'low': 0.005, 'medium': 0.01, 'high': 0.02}[volatility]
        
        # מגמה + רעש
        trend = np.sin(time.time() / 3600) * 0.01  # מגמה סינוסואידלית
        noise = np.random.normal(0, volatility_multiplier)
        
        price = base_price * (1 + trend + noise)
        
        return {'symbol': symbol, 'price': round(price, 6)}
    
    def comprehensive_analysis(self, symbol: str = "TONUSDT") -> Dict:
        """ניתוח מסחר מקיף ומתקדם"""
        try:
            # איסוף נתונים ממקורות שונים
            market_data = self.analyze_market_conditions(symbol)
            technical_analysis = self.advanced_technical_analysis(symbol)
            sentiment_analysis = self.market_sentiment_analysis(symbol)
            volume_analysis = self.advanced_volume_analysis(symbol)
            
            # חיזוי Machine Learning
            ml_predictions = self.ml_price_prediction(symbol)
            
            # ניתוח סיכונים מתקדם
            risk_assessment = self.advanced_risk_assessment(
                symbol, market_data, technical_analysis, ml_predictions
            )
            
            # יצירת אותות מסחר
            trading_signals = self.generate_advanced_trading_signals(
                symbol, market_data, technical_analysis, sentiment_analysis, 
                volume_analysis, ml_predictions, risk_assessment
            )
            
            # דוח מסחר מקיף
            trading_report = self.generate_trading_report(
                symbol, trading_signals, risk_assessment
            )
            
            return {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'market_data': market_data,
                'technical_analysis': technical_analysis,
                'sentiment_analysis': sentiment_analysis,
                'volume_analysis': volume_analysis,
                'ml_predictions': ml_predictions,
                'risk_assessment': risk_assessment,
                'trading_signals': trading_signals,
                'trading_report': trading_report,
                'confidence_score': self.calculate_overall_confidence(
                    technical_analysis, ml_predictions, risk_assessment
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive analysis: {e}")
            return self._get_fallback_analysis(symbol)
    
    def advanced_technical_analysis(self, symbol: str) -> Dict:
        """ניתוח טכני מתקדם"""
        try:
            # קבלת נתונים היסטוריים
            df = self.get_klines_data(symbol, '1h', 200)
            
            if df.empty:
                return self._get_sample_technical_analysis()
            
            # אינדיקטורים מתקדמים
            indicators = {
                'trend_indicators': self._calculate_trend_indicators(df),
                'momentum_indicators': self._calculate_momentum_indicators(df),
                'volatility_indicators': self._calculate_volatility_indicators(df),
                'volume_indicators': self._calculate_volume_indicators(df),
                'cycle_indicators': self._calculate_cycle_indicators(df),
                'market_structure': self._analyze_market_structure(df)
            }
            
            # ניתוח רב- timeframe
            multi_timeframe_analysis = self._multi_timeframe_analysis(symbol)
            
            # זיהוי תבניות
            pattern_recognition = self._pattern_recognition(df)
            
            return {
                'indicators': indicators,
                'multi_timeframe_analysis': multi_timeframe_analysis,
                'pattern_recognition': pattern_recognition,
                'summary': self._generate_technical_summary(indicators, pattern_recognition)
            }
            
        except Exception as e:
            self.logger.error(f"Error in advanced technical analysis: {e}")
            return self._get_sample_technical_analysis()
    
    def _calculate_trend_indicators(self, df: pd.DataFrame) -> Dict:
        """מחשב אינדיקטורי מגמה מתקדמים"""
        try:
            # ממוצעים נעים
            ema_9 = EMAIndicator(close=df['close'], window=9).ema_indicator()
            ema_21 = EMAIndicator(close=df['close'], window=21).ema_indicator()
            ema_50 = EMAIndicator(close=df['close'], window=50).ema_indicator()
            ema_200 = EMAIndicator(close=df['close'], window=200).ema_indicator()
            
            # ADX - Average Directional Index
            adx_indicator = ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14)
            adx = adx_indicator.adx()
            plus_di = adx_indicator.adx_pos()
            minus_di = adx_indicator.adx_neg()
            
            # Ichimoku Cloud
            ichimoku = self._calculate_ichimoku(df)
            
            # Parabolic SAR
            psar = self._calculate_parabolic_sar(df)
            
            return {
                'moving_averages': {
                    'ema_9': round(ema_9.iloc[-1], 4),
                    'ema_21': round(ema_21.iloc[-1], 4),
                    'ema_50': round(ema_50.iloc[-1], 4),
                    'ema_200': round(ema_200.iloc[-1], 4),
                    'alignment': self._check_ma_alignment(ema_9, ema_21, ema_50, ema_200),
                    'trend_strength': self._calculate_trend_strength(ema_9, ema_21, ema_50)
                },
                'adx': {
                    'value': round(adx.iloc[-1], 2),
                    'plus_di': round(plus_di.iloc[-1], 2),
                    'minus_di': round(minus_di.iloc[-1], 2),
                    'trend_strength': 'STRONG' if adx.iloc[-1] > 25 else 'WEAK',
                    'direction': 'BULLISH' if plus_di.iloc[-1] > minus_di.iloc[-1] else 'BEARISH'
                },
                'ichimoku_cloud': ichimoku,
                'parabolic_sar': psar
            }
        except Exception as e:
            self.logger.error(f"Error calculating trend indicators: {e}")
            return {}
    
    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict:
        """מחשב אינדיקטורי מומנטום מתקדמים"""
        try:
            # RSI
            rsi = RSIIndicator(close=df['close'], window=14).rsi()
            
            # MACD
            macd_indicator = MACD(close=df['close'])
            macd_line = macd_indicator.macd()
            macd_signal = macd_indicator.macd_signal()
            macd_histogram = macd_indicator.macd_diff()
            
            # Stochastic
            stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'])
            stoch_k = stoch.stoch()
            stoch_d = stoch.stoch_signal()
            
            # Williams %R
            williams_r = self._calculate_williams_r(df)
            
            # CCI - Commodity Channel Index
            cci = self._calculate_cci(df)
            
            return {
                'rsi': {
                    'value': round(rsi.iloc[-1], 2),
                    'signal': 'OVERSOLD' if rsi.iloc[-1] < 30 else 'OVERBOUGHT' if rsi.iloc[-1] > 70 else 'NEUTRAL',
                    'divergence': self._check_rsi_divergence(df, rsi)
                },
                'macd': {
                    'value': round(macd_line.iloc[-1], 4),
                    'signal': round(macd_signal.iloc[-1], 4),
                    'histogram': round(macd_histogram.iloc[-1], 4),
                    'signal': 'BULLISH' if macd_histogram.iloc[-1] > 0 else 'BEARISH',
                    'crossover': self._check_macd_crossover(macd_line, macd_signal)
                },
                'stochastic': {
                    'k': round(stoch_k.iloc[-1], 2),
                    'd': round(stoch_d.iloc[-1], 2),
                    'signal': 'OVERSOLD' if stoch_k.iloc[-1] < 20 else 'OVERBOUGHT' if stoch_k.iloc[-1] > 80 else 'NEUTRAL'
                },
                'williams_r': williams_r,
                'cci': cci
            }
        except Exception as e:
            self.logger.error(f"Error calculating momentum indicators: {e}")
            return {}
    
    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict:
        """מחשב אינדיקטורי תנודתיות"""
        try:
            # Bollinger Bands
            bb = BollingerBands(close=df['close'], window=20, window_dev=2)
            bb_upper = bb.bollinger_hband()
            bb_lower = bb.bollinger_lband()
            bb_middle = bb.bollinger_mavg()
            
            # ATR - Average True Range
            atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14)
            atr_value = atr.average_true_range()
            
            # Keltner Channel
            keltner = self._calculate_keltner_channel(df)
            
            # Donchian Channel
            donchian = self._calculate_donchian_channel(df)
            
            return {
                'bollinger_bands': {
                    'upper': round(bb_upper.iloc[-1], 4),
                    'lower': round(bb_lower.iloc[-1], 4),
                    'middle': round(bb_middle.iloc[-1], 4),
                    'width': round(bb_upper.iloc[-1] - bb_lower.iloc[-1], 4),
                    'squeeze': self._check_bollinger_squeeze(bb_upper, bb_lower, bb_middle),
                    'position': self._get_bb_position(df['close'].iloc[-1], bb_upper.iloc[-1], bb_lower.iloc[-1])
                },
                'atr': {
                    'value': round(atr_value.iloc[-1], 4),
                    'percent': round((atr_value.iloc[-1] / df['close'].iloc[-1]) * 100, 2),
                    'volatility': 'HIGH' if (atr_value.iloc[-1] / df['close'].iloc[-1]) > 0.03 else 'LOW'
                },
                'keltner_channel': keltner,
                'donchian_channel': donchian
            }
        except Exception as e:
            self.logger.error(f"Error calculating volatility indicators: {e}")
            return {}
    
    def market_sentiment_analysis(self, symbol: str) -> Dict:
        """ניתוח סנטימנט שוק"""
        try:
            # במקום אמיתי זה יגיע מ-API של סנטימנט
            return {
                'overall_sentiment': 'BULLISH',
                'sentiment_score': 0.65,
                'social_media_sentiment': {
                    'twitter': 0.72,
                    'reddit': 0.58,
                    'telegram': 0.81
                },
                'fear_greed_index': 68,  # 0-100, >50 = greed
                'put_call_ratio': 0.85,  # <1 = bullish
                'funding_rate': 0.01,  # positive = long bias
                'open_interest': 1500000,
                'sentiment_changes_24h': '+5.2%'
            }
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {e}")
            return {'overall_sentiment': 'NEUTRAL', 'sentiment_score': 0.5}
    
    def advanced_volume_analysis(self, symbol: str) -> Dict:
        """ניתוח ווליום מתקדם"""
        try:
            df = self.get_klines_data(symbol, '1h', 100)
            
            if df.empty:
                return self._get_sample_volume_analysis()
            
            # OBV - On Balance Volume
            obv = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume']).on_balance_volume()
            
            # VWAP - Volume Weighted Average Price
            vwap = VolumeWeightedAveragePrice(high=df['high'], low=df['low'], close=df['close'], volume=df['volume']).volume_weighted_average_price()
            
            # Accumulation/Distribution
            adl = self._calculate_adl(df)
            
            # Volume Profile
            volume_profile = self._calculate_volume_profile(df)
            
            return {
                'obv': {
                    'value': obv.iloc[-1],
                    'trend': 'BULLISH' if obv.iloc[-1] > obv.iloc[-2] else 'BEARISH',
                    'divergence': self._check_volume_divergence(df, obv)
                },
                'vwap': {
                    'value': round(vwap.iloc[-1], 4),
                    'position': 'ABOVE' if df['close'].iloc[-1] > vwap.iloc[-1] else 'BELOW',
                    'signal': 'BULLISH' if df['close'].iloc[-1] > vwap.iloc[-1] else 'BEARISH'
                },
                'accumulation_distribution': adl,
                'volume_profile': volume_profile,
                'volume_analysis': {
                    'current_volume': df['volume'].iloc[-1],
                    'volume_avg_20': df['volume'].tail(20).mean(),
                    'volume_ratio': round(df['volume'].iloc[-1] / df['volume'].tail(20).mean(), 2),
                    'volume_trend': 'INCREASING' if df['volume'].iloc[-1] > df['volume'].iloc[-2] else 'DECREASING'
                }
            }
        except Exception as e:
            self.logger.error(f"Error in volume analysis: {e}")
            return self._get_sample_volume_analysis()
    
    def ml_price_prediction(self, symbol: str) -> Dict:
        """חיזוי מחירים באמצעות ML"""
        try:
            # סימולציה של מודל ML מתקדם
            df = self.get_klines_data(symbol, '1h', 100)
            
            if df.empty:
                return self._get_sample_ml_prediction()
            
            current_price = df['close'].iloc[-1]
            
            # סימולצית חיזוי (בפועל זה יהיה מודל ML אמיתי)
            predictions = self._simulate_ml_predictions(df)
            
            return {
                'predicted_price_1h': round(predictions['1h'], 4),
                'predicted_price_4h': round(predictions['4h'], 4),
                'predicted_price_24h': round(predictions['24h'], 4),
                'confidence_1h': 0.72,
                'confidence_4h': 0.65,
                'confidence_24h': 0.58,
                'predicted_direction': predictions['direction'],
                'trend_strength': predictions['trend_strength'],
                'support_levels': predictions['support_levels'],
                'resistance_levels': predictions['resistance_levels']
            }
        except Exception as e:
            self.logger.error(f"Error in ML prediction: {e}")
            return self._get_sample_ml_prediction()
    
    def advanced_risk_assessment(self, symbol: str, market_data: Dict, 
                               technical_analysis: Dict, ml_predictions: Dict) -> Dict:
        """הערכת סיכונים מתקדמת"""
        try:
            volatility = technical_analysis.get('indicators', {}).get('volatility_indicators', {}).get('atr', {}).get('percent', 0)
            sentiment = market_data.get('sentiment_score', 0.5)
            ml_confidence = ml_predictions.get('confidence_1h', 0.5)
            
            # חישוב ציון סיכון מורכב
            risk_score = self._calculate_risk_score(volatility, sentiment, ml_confidence)
            
            return {
                'risk_level': self._get_risk_level(risk_score),
                'risk_score': round(risk_score, 3),
                'volatility_risk': self._assess_volatility_risk(volatility),
                'liquidity_risk': self._assess_liquidity_risk(symbol),
                'market_risk': self._assess_market_risk(sentiment),
                'position_sizing': self._calculate_position_sizing(risk_score),
                'stop_loss_levels': self._calculate_stop_loss_levels(market_data, technical_analysis),
                'take_profit_levels': self._calculate_take_profit_levels(market_data, technical_analysis),
                'hedging_recommendations': self._generate_hedging_recommendations(risk_score, symbol)
            }
        except Exception as e:
            self.logger.error(f"Error in risk assessment: {e}")
            return {'risk_level': 'MEDIUM', 'risk_score': 0.5}
    
    def generate_advanced_trading_signals(self, symbol: str, market_data: Dict, 
                                        technical_analysis: Dict, sentiment_analysis: Dict,
                                        volume_analysis: Dict, ml_predictions: Dict,
                                        risk_assessment: Dict) -> Dict:
        """מייצר אותות מסחר מתקדמים"""
        try:
            # ציון מסחר משוקלל
            trading_score = self._calculate_trading_score(
                technical_analysis, sentiment_analysis, volume_analysis, ml_predictions
            )
            
            # התאמה לרמת סיכון
            risk_adjusted_score = trading_score * (1 - risk_assessment.get('risk_score', 0.5))
            
            # החלטת מסחר
            action, confidence = self._determine_advanced_trading_action(risk_adjusted_score, risk_assessment)
            
            # פרמטרי מסחר מתקדמים
            trade_parameters = self._calculate_advanced_trade_parameters(
                action, confidence, market_data, technical_analysis, risk_assessment
            )
            
            return {
                'action': action,
                'confidence': confidence,
                'trading_score': trading_score,
                'risk_adjusted_score': risk_adjusted_score,
                'trade_parameters': trade_parameters,
                'entry_strategy': self._generate_entry_strategy(action, technical_analysis),
                'exit_strategy': self._generate_exit_strategy(action, technical_analysis, risk_assessment),
                'risk_management': self._generate_risk_management_strategy(risk_assessment),
                'contingency_plan': self._generate_contingency_plan(action, risk_assessment)
            }
        except Exception as e:
            self.logger.error(f"Error generating trading signals: {e}")
            return {'action': 'HOLD', 'confidence': 0.5}
    
    def multi_symbol_analysis(self) -> Dict:
        """ניתוח מרובה מטבעות מתקדם"""
        symbols = ['TONUSDT', 'BNBUSDT', 'BTCUSDT']
        analyses = {}
        portfolio_recommendations = []
        
        for symbol in symbols:
            try:
                analysis = self.comprehensive_analysis(symbol)
                analyses[symbol] = analysis
                
                # המלצות תיק
                if analysis['trading_signals']['action'] in ['STRONG_BUY', 'BUY']:
                    portfolio_recommendations.append({
                        'symbol': symbol,
                        'action': analysis['trading_signals']['action'],
                        'allocation': self._calculate_portfolio_allocation(symbol, analysis),
                        'confidence': analysis['trading_signals']['confidence']
                    })
                    
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {e}")
                analyses[symbol] = self._get_fallback_analysis(symbol)
        
        # ניתוח תיק כולל
        portfolio_analysis = self._analyze_portfolio(analyses, portfolio_recommendations)
        
        return {
            'analyses': analyses,
            'portfolio_recommendations': portfolio_recommendations,
            'portfolio_analysis': portfolio_analysis,
            'market_correlation': self._analyze_market_correlation(analyses),
            'diversification_score': self._calculate_diversification_score(portfolio_recommendations),
            'timestamp': datetime.now().isoformat()
        }
    
    # helper methods נוספים...
    
    def _simulate_advanced_klines(self, symbol: str, limit: int, interval: str) -> List:
        """סימולציה מתקדמת של נתוני klines"""
        # מימוש דומה לקוד הקודם עם שיפורים
        pass
    
    def _calculate_ichimoku(self, df: pd.DataFrame) -> Dict:
        """מחשב Ichimoku Cloud"""
        # מימוש Ichimoku
        pass
    
    def _calculate_parabolic_sar(self, df: pd.DataFrame) -> Dict:
        """מחשב Parabolic SAR"""
        # מימוש Parabolic SAR
        pass
    
    def _check_ma_alignment(self, ema_9, ema_21, ema_50, ema_200) -> str:
        """בודק יישור ממוצעים נעים"""
        if ema_9.iloc[-1] > ema_21.iloc[-1] > ema_50.iloc[-1] > ema_200.iloc[-1]:
            return "STRONG_BULLISH"
        elif ema_9.iloc[-1] < ema_21.iloc[-1] < ema_50.iloc[-1] < ema_200.iloc[-1]:
            return "STRONG_BEARISH"
        else:
            return "MIXED"
    
    def _simulate_ml_predictions(self, df: pd.DataFrame) -> Dict:
        """סימולצית חיזוי ML"""
        current_price = df['close'].iloc[-1]
        
        # סימולציה בסיסית - בפועל זה יהיה מודל ML אמיתי
        trend = np.random.choice(['BULLISH', 'BEARISH', 'SIDEWAYS'], p=[0.4, 0.3, 0.3])
        
        if trend == 'BULLISH':
            change_1h = np.random.uniform(0.001, 0.02)
            change_4h = np.random.uniform(0.005, 0.05)
            change_24h = np.random.uniform(0.01, 0.1)
        elif trend == 'BEARISH':
            change_1h = np.random.uniform(-0.02, -0.001)
            change_4h = np.random.uniform(-0.05, -0.005)
            change_24h = np.random.uniform(-0.1, -0.01)
        else:
            change_1h = np.random.uniform(-0.01, 0.01)
            change_4h = np.random.uniform(-0.02, 0.02)
            change_24h = np.random.uniform(-0.03, 0.03)
        
        return {
            '1h': current_price * (1 + change_1h),
            '4h': current_price * (1 + change_4h),
            '24h': current_price * (1 + change_24h),
            'direction': trend,
            'trend_strength': np.random.choice(['STRONG', 'MODERATE', 'WEAK']),
            'support_levels': [current_price * 0.98, current_price * 0.96],
            'resistance_levels': [current_price * 1.02, current_price * 1.04]
        }
    
    def _get_sample_technical_analysis(self) -> Dict:
        """נתונים לדוגמה לניתוח טכני"""
        return {
            'indicators': {
                'trend_indicators': {'moving_averages': {'alignment': 'BULLISH'}},
                'momentum_indicators': {'rsi': {'value': 45, 'signal': 'NEUTRAL'}},
                'volatility_indicators': {'bollinger_bands': {'squeeze': False}}
            },
            'summary': 'NEUTRAL'
        }
    
    def _get_sample_volume_analysis(self) -> Dict:
        """נתונים לדוגמה לניתוח ווליום"""
        return {
            'volume_analysis': {'volume_ratio': 1.2, 'volume_trend': 'INCREASING'}
        }
    
    def _get_sample_ml_prediction(self) -> Dict:
        """נתונים לדוגמה לחיזוי ML"""
        return {
            'predicted_price_1h': 2.46,
            'confidence_1h': 0.6,
            'predicted_direction': 'BULLISH'
        }
    
    def _get_fallback_analysis(self, symbol: str) -> Dict:
        """ניתוח גיבוי"""
        return {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'trading_signals': {'action': 'HOLD', 'confidence': 0.5},
            'risk_assessment': {'risk_level': 'MEDIUM'},
            'error': 'System initializing'
        }
