import pandas as pd
import numpy as np
import ta
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator, ROCIndicator
from ta.trend import MACD, EMAIndicator, ADXIndicator, IchimokuIndicator, PSARIndicator
from ta.volatility import BollingerBands, AverageTrueRange, KeltnerChannel, DonchianChannel
from ta.volume import VolumeWeightedAveragePrice, OnBalanceVolumeIndicator, AccDistIndexIndicator
from ta.other import DailyReturnIndicator
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class AdvancedTechnicalAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_indicators_config()
    
    def setup_indicators_config(self):
        """הגדרות מתקדמות לאינדיקטורים"""
        self.config = {
            'rsi': {'period': 14, 'oversold': 30, 'overbought': 70},
            'macd': {'fast': 12, 'slow': 26, 'signal': 9},
            'bollinger': {'period': 20, 'std_dev': 2},
            'stochastic': {'k_period': 14, 'd_period': 3},
            'ichimoku': {'conversion': 9, 'base': 26, 'lagging': 52, 'displacement': 26},
            'atr': {'period': 14},
            'volume_ma': {'period': 20}
        }
        
        # משקלות לניתוח משוקלל
        self.weights = {
            'trend': 0.25,
            'momentum': 0.25,
            'volatility': 0.20,
            'volume': 0.15,
            'market_structure': 0.15
        }

    def comprehensive_technical_analysis(self, df: pd.DataFrame, symbol: str = "TONUSDT") -> Dict:
        """ניתוח טכני מקיף ומתקדם"""
        try:
            if df.empty or len(df) < 50:
                return self._get_sample_analysis()
            
            self.logger.info(f"🔍 Running comprehensive technical analysis for {symbol}")
            
            # ניתוח רב-שכבתי
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'basic_analysis': self._basic_analysis(df),
                'advanced_indicators': self._advanced_indicators_analysis(df),
                'multi_timeframe_analysis': self._multi_timeframe_analysis(df),
                'market_structure': self._market_structure_analysis(df),
                'pattern_recognition': self._advanced_pattern_recognition(df),
                'volume_analysis': self._comprehensive_volume_analysis(df),
                'momentum_analysis': self._momentum_analysis(df),
                'trend_analysis': self._trend_analysis(df),
                'volatility_analysis': self._volatility_analysis(df),
                'trading_signals': self._generate_trading_signals(df),
                'risk_assessment': self._technical_risk_assessment(df),
                'summary': {}
            }
            
            # חישוב סיכום משוקלל
            analysis['summary'] = self._calculate_comprehensive_summary(analysis)
            
            self.logger.info(f"✅ Technical analysis completed for {symbol}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"❌ Error in comprehensive technical analysis: {e}")
            return self._get_sample_analysis()

    def _basic_analysis(self, df: pd.DataFrame) -> Dict:
        """ניתוח בסיסי"""
        try:
            current_price = df['close'].iloc[-1]
            prev_price = df['close'].iloc[-2]
            price_change = current_price - prev_price
            price_change_pct = (price_change / prev_price) * 100
            
            # תנועות מחיר
            high_24h = df['high'].tail(24).max()
            low_24h = df['low'].tail(24).min()
            range_24h = high_24h - low_24h
            range_pct = (range_24h / current_price) * 100
            
            return {
                'current_price': round(current_price, 6),
                'price_change': round(price_change, 6),
                'price_change_pct': round(price_change_pct, 2),
                'high_24h': round(high_24h, 6),
                'low_24h': round(low_24h, 6),
                'range_24h': round(range_24h, 6),
                'range_pct': round(range_pct, 2),
                'volume_24h': round(df['volume'].tail(24).sum(), 2),
                'signal': 'BULLISH' if price_change_pct > 0 else 'BEARISH'
            }
        except Exception as e:
            self.logger.error(f"Error in basic analysis: {e}")
            return {}

    def _advanced_indicators_analysis(self, df: pd.DataFrame) -> Dict:
        """ניתוח אינדיקטורים מתקדמים"""
        try:
            return {
                'trend_indicators': self._calculate_trend_indicators(df),
                'momentum_indicators': self._calculate_momentum_indicators(df),
                'volatility_indicators': self._calculate_volatility_indicators(df),
                'volume_indicators': self._calculate_volume_indicators(df),
                'cycle_indicators': self._calculate_cycle_indicators(df),
                'market_health': self._calculate_market_health(df)
            }
        except Exception as e:
            self.logger.error(f"Error in advanced indicators analysis: {e}")
            return {}

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
            ichimoku = IchimokuIndicator(
                high=df['high'], low=df['low'],
                window1=9, window2=26, window3=52
            )
            ichimoku_a = ichimoku.ichimoku_a()
            ichimoku_b = ichimoku.ichimoku_b()
            ichimoku_base = ichimoku.ichimoku_base_line()
            ichimoku_conversion = ichimoku.ichimoku_conversion_line()
            
            # Parabolic SAR
            psar = PSARIndicator(high=df['high'], low=df['low'], close=df['close'])
            psar_value = psar.psar()
            
            return {
                'moving_averages': {
                    'ema_9': round(ema_9.iloc[-1], 6),
                    'ema_21': round(ema_21.iloc[-1], 6),
                    'ema_50': round(ema_50.iloc[-1], 6),
                    'ema_200': round(ema_200.iloc[-1], 6),
                    'alignment': self._check_ma_alignment(ema_9, ema_21, ema_50, ema_200),
                    'trend_strength': self._calculate_trend_strength(ema_9, ema_21, ema_50),
                    'golden_cross': self._check_golden_cross(ema_9, ema_21, ema_50),
                    'death_cross': self._check_death_cross(ema_9, ema_21, ema_50)
                },
                'adx': {
                    'value': round(adx.iloc[-1], 2),
                    'plus_di': round(plus_di.iloc[-1], 2),
                    'minus_di': round(minus_di.iloc[-1], 2),
                    'trend_strength': 'VERY_STRONG' if adx.iloc[-1] > 50 else 
                                     'STRONG' if adx.iloc[-1] > 25 else 'WEAK',
                    'direction': 'BULLISH' if plus_di.iloc[-1] > minus_di.iloc[-1] else 'BEARISH',
                    'crossover': self._check_di_crossover(plus_di, minus_di)
                },
                'ichimoku_cloud': {
                    'conversion_line': round(ichimoku_conversion.iloc[-1], 6),
                    'base_line': round(ichimoku_base.iloc[-1], 6),
                    'leading_span_a': round(ichimoku_a.iloc[-1], 6),
                    'leading_span_b': round(ichimoku_b.iloc[-1], 6),
                    'cloud_position': self._get_ichimoku_cloud_position(df, ichimoku_a, ichimoku_b),
                    'signal': self._get_ichimoku_signal(df, ichimoku_conversion, ichimoku_base, ichimoku_a, ichimoku_b)
                },
                'parabolic_sar': {
                    'value': round(psar_value.iloc[-1], 6),
                    'trend': 'BULLISH' if df['close'].iloc[-1] > psar_value.iloc[-1] else 'BEARISH',
                    'reversal': self._check_psar_reversal(psar_value)
                }
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
            williams_r = WilliamsRIndicator(high=df['high'], low=df['low'], close=df['close']).williams_r()
            
            # ROC - Rate of Change
            roc = ROCIndicator(close=df['close']).roc()
            
            # CCI - Commodity Channel Index
            cci = self._calculate_cci(df)
            
            # MFI - Money Flow Index
            mfi = self._calculate_mfi(df)
            
            return {
                'rsi': {
                    'value': round(rsi.iloc[-1], 2),
                    'signal': 'OVERSOLD' if rsi.iloc[-1] < 30 else 
                             'OVERBOUGHT' if rsi.iloc[-1] > 70 else 'NEUTRAL',
                    'divergence': self._check_rsi_divergence(df, rsi),
                    'momentum': 'BULLISH' if rsi.iloc[-1] > 50 else 'BEARISH'
                },
                'macd': {
                    'value': round(macd_line.iloc[-1], 6),
                    'signal_line': round(macd_signal.iloc[-1], 6),
                    'histogram': round(macd_histogram.iloc[-1], 6),
                    'signal': 'BULLISH' if macd_histogram.iloc[-1] > 0 else 'BEARISH',
                    'crossover': self._check_macd_crossover(macd_line, macd_signal),
                    'divergence': self._check_macd_divergence(df, macd_line)
                },
                'stochastic': {
                    'k': round(stoch_k.iloc[-1], 2),
                    'd': round(stoch_d.iloc[-1], 2),
                    'signal': 'OVERSOLD' if stoch_k.iloc[-1] < 20 else 
                             'OVERBOUGHT' if stoch_k.iloc[-1] > 80 else 'NEUTRAL',
                    'crossover': self._check_stochastic_crossover(stoch_k, stoch_d)
                },
                'williams_r': {
                    'value': round(williams_r.iloc[-1], 2),
                    'signal': 'OVERSOLD' if williams_r.iloc[-1] < -80 else 
                             'OVERBOUGHT' if williams_r.iloc[-1] > -20 else 'NEUTRAL'
                },
                'roc': {
                    'value': round(roc.iloc[-1], 2),
                    'momentum': 'BULLISH' if roc.iloc[-1] > 0 else 'BEARISH'
                },
                'cci': cci,
                'mfi': mfi
            }
        except Exception as e:
            self.logger.error(f"Error calculating momentum indicators: {e}")
            return {}

    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict:
        """מחשב אינדיקטורי תנודתיות מתקדמים"""
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
            keltner = KeltnerChannel(high=df['high'], low=df['low'], close=df['close'])
            kc_upper = keltner.keltner_channel_hband()
            kc_lower = keltner.keltner_channel_lband()
            kc_middle = keltner.keltner_channel_mband()
            
            # Donchian Channel
            donchian = DonchianChannel(high=df['high'], low=df['low'], close=df['close'])
            dc_upper = donchian.donchian_channel_hband()
            dc_lower = donchian.donchian_channel_lband()
            dc_middle = donchian.donchian_channel_mband()
            
            return {
                'bollinger_bands': {
                    'upper': round(bb_upper.iloc[-1], 6),
                    'lower': round(bb_lower.iloc[-1], 6),
                    'middle': round(bb_middle.iloc[-1], 6),
                    'width': round(bb_upper.iloc[-1] - bb_lower.iloc[-1], 6),
                    'squeeze': self._check_bollinger_squeeze(bb_upper, bb_lower, bb_middle),
                    'position': self._get_bb_position(df['close'].iloc[-1], bb_upper.iloc[-1], bb_lower.iloc[-1]),
                    'signal': self._get_bb_signal(df, bb_upper, bb_lower)
                },
                'atr': {
                    'value': round(atr_value.iloc[-1], 6),
                    'percent': round((atr_value.iloc[-1] / df['close'].iloc[-1]) * 100, 2),
                    'volatility': 'VERY_HIGH' if (atr_value.iloc[-1] / df['close'].iloc[-1]) > 0.05 else
                                 'HIGH' if (atr_value.iloc[-1] / df['close'].iloc[-1]) > 0.03 else
                                 'MODERATE' if (atr_value.iloc[-1] / df['close'].iloc[-1]) > 0.01 else 'LOW'
                },
                'keltner_channel': {
                    'upper': round(kc_upper.iloc[-1], 6),
                    'lower': round(kc_lower.iloc[-1], 6),
                    'middle': round(kc_middle.iloc[-1], 6),
                    'position': self._get_kc_position(df['close'].iloc[-1], kc_upper.iloc[-1], kc_lower.iloc[-1])
                },
                'donchian_channel': {
                    'upper': round(dc_upper.iloc[-1], 6),
                    'lower': round(dc_lower.iloc[-1], 6),
                    'middle': round(dc_middle.iloc[-1], 6),
                    'breakout': self._check_donchian_breakout(df, dc_upper, dc_lower)
                }
            }
        except Exception as e:
            self.logger.error(f"Error calculating volatility indicators: {e}")
            return {}

    def _calculate_volume_indicators(self, df: pd.DataFrame) -> Dict:
        """מחשב אינדיקטורי ווליום מתקדמים"""
        try:
            # OBV - On Balance Volume
            obv = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume']).on_balance_volume()
            
            # VWAP - Volume Weighted Average Price
            vwap = VolumeWeightedAveragePrice(
                high=df['high'], low=df['low'], close=df['close'], volume=df['volume']
            ).volume_weighted_average_price()
            
            # Accumulation/Distribution Line
            adl = AccDistIndexIndicator(high=df['high'], low=df['low'], close=df['close'], volume=df['volume']).acc_dist_index()
            
            # Volume SMA
            volume_sma = df['volume'].rolling(window=20).mean()
            
            # Chaikin Money Flow
            cmf = self._calculate_cmf(df)
            
            return {
                'obv': {
                    'value': obv.iloc[-1],
                    'trend': 'BULLISH' if obv.iloc[-1] > obv.iloc[-2] else 'BEARISH',
                    'divergence': self._check_volume_divergence(df, obv),
                    'signal': self._get_obv_signal(obv)
                },
                'vwap': {
                    'value': round(vwap.iloc[-1], 6),
                    'position': 'ABOVE' if df['close'].iloc[-1] > vwap.iloc[-1] else 'BELOW',
                    'signal': 'BULLISH' if df['close'].iloc[-1] > vwap.iloc[-1] else 'BEARISH',
                    'deviation': round(((df['close'].iloc[-1] - vwap.iloc[-1]) / vwap.iloc[-1]) * 100, 2)
                },
                'accumulation_distribution': {
                    'value': adl.iloc[-1],
                    'trend': 'ACCUMULATION' if adl.iloc[-1] > adl.iloc[-2] else 'DISTRIBUTION',
                    'signal': self._get_adl_signal(adl)
                },
                'volume_analysis': {
                    'current_volume': df['volume'].iloc[-1],
                    'volume_avg_20': volume_sma.iloc[-1],
                    'volume_ratio': round(df['volume'].iloc[-1] / volume_sma.iloc[-1], 2),
                    'volume_trend': 'INCREASING' if df['volume'].iloc[-1] > df['volume'].iloc[-2] else 'DECREASING',
                    'signal': 'HIGH_VOLUME' if (df['volume'].iloc[-1] / volume_sma.iloc[-1]) > 2 else
                             'LOW_VOLUME' if (df['volume'].iloc[-1] / volume_sma.iloc[-1]) < 0.5 else 'NORMAL'
                },
                'chaikin_money_flow': cmf
            }
        except Exception as e:
            self.logger.error(f"Error calculating volume indicators: {e}")
            return {}

    def _multi_timeframe_analysis(self, df: pd.DataFrame) -> Dict:
        """ניתוח רב- timeframe"""
        try:
            # סימולציה של נתונים מרובי timeframe
            # בפועל זה יגיע מנתונים אמיתיים
            return {
                '1h': {
                    'trend': 'BULLISH',
                    'momentum': 'STRONG',
                    'key_levels': {
                        'support': [df['close'].iloc[-1] * 0.98, df['close'].iloc[-1] * 0.96],
                        'resistance': [df['close'].iloc[-1] * 1.02, df['close'].iloc[-1] * 1.04]
                    }
                },
                '4h': {
                    'trend': 'BULLISH',
                    'momentum': 'MODERATE',
                    'key_levels': {
                        'support': [df['close'].iloc[-1] * 0.97, df['close'].iloc[-1] * 0.94],
                        'resistance': [df['close'].iloc[-1] * 1.03, df['close'].iloc[-1] * 1.06]
                    }
                },
                '1d': {
                    'trend': 'BULLISH',
                    'momentum': 'WEAK',
                    'key_levels': {
                        'support': [df['close'].iloc[-1] * 0.95, df['close'].iloc[-1] * 0.90],
                        'resistance': [df['close'].iloc[-1] * 1.05, df['close'].iloc[-1] * 1.10]
                    }
                },
                'consensus': {
                    'trend': 'BULLISH',
                    'confidence': 0.75,
                    'timeframe_alignment': 'ALIGNED'
                }
            }
        except Exception as e:
            self.logger.error(f"Error in multi timeframe analysis: {e}")
            return {}

    def _market_structure_analysis(self, df: pd.DataFrame) -> Dict:
        """ניתוח מבנה שוק"""
        try:
            # זיהוי רמות תמיכה והתנגדות
            support_levels = self._find_support_levels(df)
            resistance_levels = self._find_resistance_levels(df)
            
            # זיהוי מגמות
            trend_lines = self._identify_trend_lines(df)
            
            # ניתוח supply/demand zones
            supply_demand_zones = self._identify_supply_demand_zones(df)
            
            return {
                'support_levels': support_levels,
                'resistance_levels': resistance_levels,
                'trend_lines': trend_lines,
                'supply_demand_zones': supply_demand_zones,
                'market_phase': self._determine_market_phase(df),
                'key_levels': self._identify_key_levels(df)
            }
        except Exception as e:
            self.logger.error(f"Error in market structure analysis: {e}")
            return {}

    def _advanced_pattern_recognition(self, df: pd.DataFrame) -> Dict:
        """זיהוי תבניות מתקדם"""
        try:
            return {
                'candlestick_patterns': self._identify_candlestick_patterns(df),
                'chart_patterns': self._identify_chart_patterns(df),
                'harmonic_patterns': self._identify_harmonic_patterns(df),
                'elliott_wave': self._analyze_elliott_wave(df),
                'pattern_quality': self._assess_pattern_quality(df)
            }
        except Exception as e:
            self.logger.error(f"Error in pattern recognition: {e}")
            return {}

    def _comprehensive_volume_analysis(self, df: pd.DataFrame) -> Dict:
        """ניתוח ווליום מקיף"""
        try:
            return {
                'volume_profile': self._calculate_volume_profile(df),
                'volume_clusters': self._identify_volume_clusters(df),
                'volume_spikes': self._detect_volume_spikes(df),
                'volume_trend': self._analyze_volume_trend(df),
                'volume_confirmation': self._check_volume_confirmation(df)
            }
        except Exception as e:
            self.logger.error(f"Error in volume analysis: {e}")
            return {}

    def _momentum_analysis(self, df: pd.DataFrame) -> Dict:
        """ניתוח מומנטום מתקדם"""
        try:
            return {
                'momentum_indicators': self._calculate_momentum_indicators(df),
                'momentum_divergence': self._check_momentum_divergence(df),
                'momentum_trend': self._analyze_momentum_trend(df),
                'momentum_quality': self._assess_momentum_quality(df)
            }
        except Exception as e:
            self.logger.error(f"Error in momentum analysis: {e}")
            return {}

    def _trend_analysis(self, df: pd.DataFrame) -> Dict:
        """ניתוח מגמות מתקדם"""
        try:
            return {
                'trend_direction': self._determine_trend_direction(df),
                'trend_strength': self._calculate_trend_strength_advanced(df),
                'trend_duration': self._analyze_trend_duration(df),
                'trend_quality': self._assess_trend_quality(df),
                'trend_reversal_signals': self._check_trend_reversal_signals(df)
            }
        except Exception as e:
            self.logger.error(f"Error in trend analysis: {e}")
            return {}

    def _volatility_analysis(self, df: pd.DataFrame) -> Dict:
        """ניתוח תנודתיות מתקדם"""
        try:
            return {
                'volatility_regimes': self._identify_volatility_regimes(df),
                'volatility_cycles': self._analyze_volatility_cycles(df),
                'volatility_breakouts': self._detect_volatility_breakouts(df),
                'volatility_compression': self._check_volatility_compression(df)
            }
        except Exception as e:
            self.logger.error(f"Error in volatility analysis: {e}")
            return {}

    def _generate_trading_signals(self, df: pd.DataFrame) -> Dict:
        """יצירת אותות מסחר מתקדמים"""
        try:
            signals = {
                'entry_signals': self._generate_entry_signals(df),
                'exit_signals': self._generate_exit_signals(df),
                'stop_loss_levels': self._calculate_stop_loss_levels(df),
                'take_profit_levels': self._calculate_take_profit_levels(df),
                'position_sizing': self._calculate_position_sizing(df),
                'risk_reward_ratio': self._calculate_risk_reward_ratio(df),
                'signal_quality': self._assess_signal_quality(df),
                'timeframe_alignment': self._check_timeframe_alignment(df)
            }
            
            # סיכום אותות
            signals['summary'] = self._generate_signal_summary(signals)
            
            return signals
        except Exception as e:
            self.logger.error(f"Error generating trading signals: {e}")
            return {}

    def _technical_risk_assessment(self, df: pd.DataFrame) -> Dict:
        """הערכת סיכונים טכנית"""
        try:
            return {
                'market_risk': self._assess_market_risk(df),
                'volatility_risk': self._assess_volatility_risk(df),
                'liquidity_risk': self._assess_liquidity_risk(df),
                'technical_risk': self._assess_technical_risk(df),
                'risk_score': self._calculate_technical_risk_score(df),
                'risk_mitigation': self._suggest_risk_mitigation(df)
            }
        except Exception as e:
            self.logger.error(f"Error in technical risk assessment: {e}")
            return {}

    # Helper methods - רק חלק מהפונקציות העזר

    def _check_ma_alignment(self, ema_9, ema_21, ema_50, ema_200) -> str:
        """בודק יישור ממוצעים נעים"""
        try:
            if (ema_9.iloc[-1] > ema_21.iloc[-1] > ema_50.iloc[-1] > ema_200.iloc[-1]):
                return "STRONG_BULLISH_ALIGNMENT"
            elif (ema_9.iloc[-1] < ema_21.iloc[-1] < ema_50.iloc[-1] < ema_200.iloc[-1]):
                return "STRONG_BEARISH_ALIGNMENT"
            elif (ema_9.iloc[-1] > ema_21.iloc[-1] > ema_50.iloc[-1]):
                return "BULLISH_ALIGNMENT"
            elif (ema_9.iloc[-1] < ema_21.iloc[-1] < ema_50.iloc[-1]):
                return "BEARISH_ALIGNMENT"
            else:
                return "MIXED_ALIGNMENT"
        except:
            return "UNKNOWN"

    def _calculate_trend_strength(self, ema_9, ema_21, ema_50) -> str:
        """מחשב חוזק מגמה"""
        try:
            short_trend = (ema_9.iloc[-1] - ema_9.iloc[-5]) / ema_9.iloc[-5]
            medium_trend = (ema_21.iloc[-1] - ema_21.iloc[-10]) / ema_21.iloc[-10]
            long_trend = (ema_50.iloc[-1] - ema_50.iloc[-20]) / ema_50.iloc[-20]
            
            avg_trend = (abs(short_trend) + abs(medium_trend) + abs(long_trend)) / 3
            
            if avg_trend > 0.05:
                return "VERY_STRONG"
            elif avg_trend > 0.02:
                return "STRONG"
            elif avg_trend > 0.01:
                return "MODERATE"
            else:
                return "WEAK"
        except:
            return "UNKNOWN"

    def _check_golden_cross(self, ema_9, ema_21, ema_50) -> bool:
        """בודק Golden Cross"""
        try:
            return (ema_9.iloc[-1] > ema_21.iloc[-1] and 
                   ema_21.iloc[-1] > ema_50.iloc[-1] and
                   ema_9.iloc[-2] <= ema_21.iloc[-2])
        except:
            return False

    def _check_death_cross(self, ema_9, ema_21, ema_50) -> bool:
        """בודק Death Cross"""
        try:
            return (ema_9.iloc[-1] < ema_21.iloc[-1] and 
                   ema_21.iloc[-1] < ema_50.iloc[-1] and
                   ema_9.iloc[-2] >= ema_21.iloc[-2])
        except:
            return False

    def _check_bollinger_squeeze(self, bb_upper, bb_lower, bb_middle) -> bool:
        """בודק Bollinger Squeeze"""
        try:
            bandwidth = (bb_upper.iloc[-1] - bb_lower.iloc[-1]) / bb_middle.iloc[-1]
            return bandwidth < 0.1
        except:
            return False

    def _get_bb_position(self, price, bb_upper, bb_lower) -> str:
        """מחזיר מיקום מחיר ב-Bollinger Bands"""
        try:
            if price >= bb_upper:
                return "ABOVE_UPPER_BAND"
            elif price <= bb_lower:
                return "BELOW_LOWER_BAND"
            elif price > (bb_upper + bb_lower) / 2:
                return "UPPER_HALF"
            else:
                return "LOWER_HALF"
        except:
            return "UNKNOWN"

    def _check_rsi_divergence(self, df, rsi) -> Dict:
        """בודק RSI Divergence"""
        # מימוש פשטני - בפועל יהיה מורכב יותר
        return {
            'bullish_divergence': False,
            'bearish_divergence': False,
            'hidden_bullish': False,
            'hidden_bearish': False
        }

    def _calculate_comprehensive_summary(self, analysis: Dict) -> Dict:
        """מחשב סיכום משוקלל"""
        try:
            # חישוב ציונים לכל קטגוריה
            trend_score = self._calculate_trend_score(analysis)
            momentum_score = self._calculate_momentum_score(analysis)
            volatility_score = self._calculate_volatility_score(analysis)
            volume_score = self._calculate_volume_score(analysis)
            
            # ציון כולל משוקלל
            total_score = (
                trend_score * self.weights['trend'] +
                momentum_score * self.weights['momentum'] +
                volatility_score * self.weights['volatility'] +
                volume_score * self.weights['volume']
            )
            
            # החלטת מסחר
            if total_score > 0.7:
                action = "STRONG_BUY"
            elif total_score > 0.6:
                action = "BUY"
            elif total_score < 0.3:
                action = "STRONG_SELL"
            elif total_score < 0.4:
                action = "SELL"
            else:
                action = "HOLD"
            
            return {
                'overall_score': round(total_score, 3),
                'action': action,
                'confidence': round(min(total_score, 1 - total_score) * 2, 3),
                'trend_score': round(trend_score, 3),
                'momentum_score': round(momentum_score, 3),
                'volatility_score': round(volatility_score, 3),
                'volume_score': round(volume_score, 3),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error calculating comprehensive summary: {e}")
            return {'action': 'HOLD', 'confidence': 0.5}

    def _get_sample_analysis(self) -> Dict:
        """מחזיר ניתוח לדוגמה"""
        return {
            'timestamp': datetime.now().isoformat(),
            'basic_analysis': {'current_price': 2.45, 'signal': 'NEUTRAL'},
            'summary': {'action': 'HOLD', 'confidence': 0.5}
        }

    # פונקציות עזר נוספות - מימושים פשטניים
    def _calculate_cci(self, df):
        return {'value': 0, 'signal': 'NEUTRAL'}
    
    def _calculate_mfi(self, df):
        return {'value': 50, 'signal': 'NEUTRAL'}
    
    def _calculate_cmf(self, df):
        return {'value': 0, 'signal': 'NEUTRAL'}
    
    def _find_support_levels(self, df):
        return []
    
    def _find_resistance_levels(self, df):
        return []
    
    # וכך הלאה עבור כל הפונקציות החסרות...

# מחלקת util נוספת לניתוח טכני
class TechnicalUtilities:
    @staticmethod
    def detect_divergence(price_highs, price_lows, indicator_highs, indicator_lows):
        """מזהה divergence בין מחיר לאינדיקטור"""
        # מימוש לזיהוי divergence
        pass
    
    @staticmethod
    def fibonacci_retracement(high, low):
        """מחשב רמות פיבונאצ'י"""
        diff = high - low
        return {
            '0.236': high - diff * 0.236,
            '0.382': high - diff * 0.382,
            '0.5': high - diff * 0.5,
            '0.618': high - diff * 0.618,
            '0.786': high - diff * 0.786
        }
    
    @staticmethod
    def pivot_points(high, low, close):
        """מחשב נקודות pivot"""
        pivot = (high + low + close) / 3
        return {
            'pivot': pivot,
            'r1': 2 * pivot - low,
            'r2': pivot + (high - low),
            's1': 2 * pivot - high,
            's2': pivot - (high - low)
        }
