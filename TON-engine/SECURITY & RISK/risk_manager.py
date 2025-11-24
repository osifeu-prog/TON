import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM" 
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"

class TradeAction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    REDUCE = "REDUCE"
    CLOSE = "CLOSE"

@dataclass
class Position:
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    position_type: str  # LONG/SHORT
    leverage: float = 1.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    entry_time: datetime = None
    
    def __post_init__(self):
        if self.entry_time is None:
            self.entry_time = datetime.now()

class AdvancedRiskManager:
    """מנהל סיכונים מתקדם עם ניתוח רב-ממדי"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.positions = {}
        self.risk_metrics = {}
        self.risk_config = self._load_risk_config()
        self.market_regimes = {}
        
    def _load_risk_config(self) -> Dict:
        """טוען הגדרות סיכון"""
        return {
            # הגבלות בסיסיות
            'max_portfolio_risk': 0.05,  # 5% סיכון מקסימלי על התיק
            'max_position_size': 0.10,   # 10% מקסימום לכל פוזיציה
            'max_daily_loss': 0.03,      # 3% הפסד יומי מקסימלי
            'max_drawdown': 0.15,        # 15% drawdown מקסימלי
            
            # הגדרות stop loss
            'default_stop_loss': 0.03,   # 3% stop loss ברירת מחדל
            'volatility_adjusted_sl': True,
            'trailing_stop_enabled': True,
            'trailing_stop_distance': 0.02,  # 2% trailing stop
            
            # הגדרות leverage
            'max_leverage': 3.0,
            'leverage_by_volatility': True,
            
            # הגדרות correlation
            'max_correlation': 0.7,      # correlation מקסימלי בין פוזיציות
            'diversification_minimum': 3, # מינימום נכסים שונים
            
            # הגדרות volatility
            'volatility_threshold_high': 0.05,  # 5% תנודתיות גבוהה
            'volatility_threshold_low': 0.01,   # 1% תנודתיות נמוכה
            
            # הגדרות market regime
            'regime_switch_threshold': 0.02,    # 2% threshold לשינוי regime
        }
    
    def assess_trade_risk(self, symbol: str, action: TradeAction, 
                         quantity: float, price: float, 
                         market_data: Dict, portfolio: Dict) -> Dict:
        """מעריך סיכון עבור עסקה פוטנציאלית"""
        try:
            risk_assessment = {
                'symbol': symbol,
                'action': action.value,
                'proposed_quantity': quantity,
                'current_price': price,
                'timestamp': datetime.now().isoformat(),
                'risk_factors': {},
                'warnings': [],
                'recommendations': []
            }
            
            # 1. ניתוח סיכון שוק
            market_risk = self._assess_market_risk(symbol, market_data)
            risk_assessment['risk_factors']['market_risk'] = market_risk
            
            # 2. ניתוח סיכון פוזיציה
            position_risk = self._assess_position_risk(symbol, quantity, price, portfolio)
            risk_assessment['risk_factors']['position_risk'] = position_risk
            
            # 3. ניתוח סיכון תיק
            portfolio_risk = self._assess_portfolio_risk(portfolio, symbol, quantity, price)
            risk_assessment['risk_factors']['portfolio_risk'] = portfolio_risk
            
            # 4. ניתוח סיכון נזילות
            liquidity_risk = self._assess_liquidity_risk(symbol, quantity, market_data)
            risk_assessment['risk_factors']['liquidity_risk'] = liquidity_risk
            
            # 5. ניתוח סיכון volatility
            volatility_risk = self._assess_volatility_risk(symbol, market_data)
            risk_assessment['risk_factors']['volatility_risk'] = volatility_risk
            
            # חישוב סיכון כולל
            overall_risk = self._calculate_overall_risk(risk_assessment['risk_factors'])
            risk_assessment['overall_risk_score'] = overall_risk['score']
            risk_assessment['overall_risk_level'] = overall_risk['level']
            risk_assessment['can_proceed'] = overall_risk['can_proceed']
            
            # המלצות התאמה
            if not risk_assessment['can_proceed']:
                adjustment = self._suggest_position_adjustment(risk_assessment, portfolio)
                risk_assessment['recommended_adjustment'] = adjustment
                risk_assessment['warnings'].append("Trade requires adjustment before execution")
            
            # stop loss ות take profit מומלצים
            risk_assessment['recommended_stop_loss'] = self._calculate_stop_loss(
                symbol, price, market_data, action
            )
            risk_assessment['recommended_take_profit'] = self._calculate_take_profit(
                symbol, price, market_data, action
            )
            
            # position sizing מומלץ
            risk_assessment['recommended_position_size'] = self._calculate_position_size(
                symbol, price, portfolio, market_data
            )
            
            self.logger.info(f"🔍 Risk assessment for {symbol}: {risk_assessment['overall_risk_level']}")
            return risk_assessment
            
        except Exception as e:
            self.logger.error(f"Error in trade risk assessment: {e}")
            return self._get_fallback_assessment(symbol, action)
    
    def _assess_market_risk(self, symbol: str, market_data: Dict) -> Dict:
        """מעריך סיכון שוק"""
        try:
            risk_factors = {}
            
            # ניתוח volatility
            if 'volatility' in market_data:
                volatility = market_data['volatility']
                if volatility > self.risk_config['volatility_threshold_high']:
                    risk_factors['volatility'] = {'level': RiskLevel.HIGH, 'score': 0.8}
                elif volatility < self.risk_config['volatility_threshold_low']:
                    risk_factors['volatility'] = {'level': RiskLevel.LOW, 'score': 0.2}
                else:
                    risk_factors['volatility'] = {'level': RiskLevel.MEDIUM, 'score': 0.5}
            
            # ניתוח volume
            if 'volume' in market_data and 'average_volume' in market_data:
                volume_ratio = market_data['volume'] / market_data['average_volume']
                if volume_ratio < 0.5:
                    risk_factors['liquidity'] = {'level': RiskLevel.HIGH, 'score': 0.7}
                elif volume_ratio > 2.0:
                    risk_factors['liquidity'] = {'level': RiskLevel.LOW, 'score': 0.3}
                else:
                    risk_factors['liquidity'] = {'level': RiskLevel.MEDIUM, 'score': 0.5}
            
            # ניתוח trend
            if 'trend_strength' in market_data:
                trend_strength = market_data['trend_strength']
                if trend_strength > 0.7:
                    risk_factors['trend'] = {'level': RiskLevel.LOW, 'score': 0.3}
                elif trend_strength < 0.3:
                    risk_factors['trend'] = {'level': RiskLevel.HIGH, 'score': 0.7}
                else:
                    risk_factors['trend'] = {'level': RiskLevel.MEDIUM, 'score': 0.5}
            
            # ניתוח market regime
            regime_risk = self._assess_market_regime(symbol, market_data)
            risk_factors['market_regime'] = regime_risk
            
            return risk_factors
            
        except Exception as e:
            self.logger.error(f"Error assessing market risk: {e}")
            return {'error': str(e)}
    
    def _assess_market_regime(self, symbol: str, market_data: Dict) -> Dict:
        """מעריך market regime"""
        try:
            # ניתוח regime based on volatility and trend
            volatility = market_data.get('volatility', 0.02)
            trend = market_data.get('trend_strength', 0.5)
            
            if volatility < 0.01 and trend > 0.6:
                regime = "LOW_VOL_TRENDING"
                risk_score = 0.2
            elif volatility > 0.04 and trend < 0.4:
                regime = "HIGH_VOL_RANGING"
                risk_score = 0.8
            elif volatility > 0.06:
                regime = "HIGH_VOL_BREAKOUT"
                risk_score = 0.9
            else:
                regime = "NORMAL"
                risk_score = 0.5
            
            self.market_regimes[symbol] = {
                'regime': regime,
                'risk_score': risk_score,
                'timestamp': datetime.now().isoformat()
            }
            
            return {'level': RiskLevel.HIGH if risk_score > 0.7 else RiskLevel.LOW if risk_score < 0.3 else RiskLevel.MEDIUM,
                   'score': risk_score,
                   'regime': regime}
                   
        except Exception as e:
            self.logger.error(f"Error assessing market regime: {e}")
            return {'level': RiskLevel.MEDIUM, 'score': 0.5, 'regime': 'UNKNOWN'}
    
    def _assess_position_risk(self, symbol: str, quantity: float, 
                            price: float, portfolio: Dict) -> Dict:
        """מעריך סיכון פוזיציה"""
        try:
            position_value = quantity * price
            portfolio_value = portfolio.get('total_value', 1)
            
            # גודל פוזיציה יחסית לתיק
            position_size = position_value / portfolio_value
            
            risk_factors = {}
            
            # סיכון גודל פוזיציה
            if position_size > self.risk_config['max_position_size']:
                risk_factors['size'] = {
                    'level': RiskLevel.VERY_HIGH,
                    'score': 0.9,
                    'message': f"Position size {position_size:.1%} exceeds maximum {self.risk_config['max_position_size']:.1%}"
                }
            elif position_size > self.risk_config['max_position_size'] * 0.8:
                risk_factors['size'] = {
                    'level': RiskLevel.HIGH,
                    'score': 0.7,
                    'message': f"Position size {position_size:.1%} approaching maximum"
                }
            else:
                risk_factors['size'] = {
                    'level': RiskLevel.LOW,
                    'score': 0.3,
                    'message': f"Position size {position_size:.1%} within limits"
                }
            
            # סיכון ריכוז
            current_concentration = self._calculate_portfolio_concentration(portfolio)
            if current_concentration > 0.5:
                risk_factors['concentration'] = {
                    'level': RiskLevel.HIGH,
                    'score': 0.8,
                    'message': "High portfolio concentration"
                }
            
            return risk_factors
            
        except Exception as e:
            self.logger.error(f"Error assessing position risk: {e}")
            return {'error': str(e)}
    
    def _assess_portfolio_risk(self, portfolio: Dict, symbol: str, 
                             quantity: float, price: float) -> Dict:
        """מעריך סיכון תיק"""
        try:
            risk_factors = {}
            
            # סיכון drawdown
            current_drawdown = portfolio.get('current_drawdown', 0)
            if current_drawdown > self.risk_config['max_drawdown']:
                risk_factors['drawdown'] = {
                    'level': RiskLevel.VERY_HIGH,
                    'score': 0.9,
                    'message': f"Current drawdown {current_drawdown:.1%} exceeds maximum"
                }
            
            # סיכון correlation
            correlation_risk = self._assess_correlation_risk(portfolio, symbol)
            risk_factors['correlation'] = correlation_risk
            
            # סיכון diversification
            diversification_score = self._calculate_diversification_score(portfolio)
            if diversification_score < 0.3:
                risk_factors['diversification'] = {
                    'level': RiskLevel.HIGH,
                    'score': 0.8,
                    'message': "Low portfolio diversification"
                }
            
            return risk_factors
            
        except Exception as e:
            self.logger.error(f"Error assessing portfolio risk: {e}")
            return {'error': str(e)}
    
    def _assess_liquidity_risk(self, symbol: str, quantity: float, 
                             market_data: Dict) -> Dict:
        """מעריך סיכון נזילות"""
        try:
            # סימולציה - בפועל ידרוש נתוני order book
            daily_volume = market_data.get('volume_24h', 0)
            proposed_trade_value = quantity * market_data.get('current_price', 0)
            
            if daily_volume > 0:
                trade_to_volume_ratio = proposed_trade_value / daily_volume
                
                if trade_to_volume_ratio > 0.05:  # 5% מה-volume היומי
                    return {
                        'level': RiskLevel.HIGH,
                        'score': 0.8,
                        'message': "High liquidity risk - large trade relative to daily volume"
                    }
                elif trade_to_volume_ratio > 0.01:  # 1% מה-volume היומי
                    return {
                        'level': RiskLevel.MEDIUM,
                        'score': 0.5,
                        'message': "Moderate liquidity risk"
                    }
                else:
                    return {
                        'level': RiskLevel.LOW,
                        'score': 0.2,
                        'message': "Low liquidity risk"
                    }
            else:
                return {
                    'level': RiskLevel.MEDIUM,
                    'score': 0.5,
                    'message': "Insufficient volume data"
                }
                
        except Exception as e:
            self.logger.error(f"Error assessing liquidity risk: {e}")
            return {'level': RiskLevel.MEDIUM, 'score': 0.5, 'message': str(e)}
    
    def _assess_volatility_risk(self, symbol: str, market_data: Dict) -> Dict:
        """מעריך סיכון תנודתיות"""
        try:
            volatility = market_data.get('volatility', 0.02)
            historical_vol = market_data.get('historical_volatility', volatility)
            
            # ניתוח תנודתיות יחסית
            if volatility > historical_vol * 1.5:
                level = RiskLevel.HIGH
                score = 0.8
                message = "High volatility relative to history"
            elif volatility > historical_vol * 1.2:
                level = RiskLevel.MEDIUM
                score = 0.6
                message = "Elevated volatility"
            else:
                level = RiskLevel.LOW
                score = 0.3
                message = "Normal volatility levels"
            
            return {
                'level': level,
                'score': score,
                'message': message,
                'current_volatility': volatility,
                'historical_volatility': historical_vol
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing volatility risk: {e}")
            return {'level': RiskLevel.MEDIUM, 'score': 0.5, 'message': str(e)}
    
    def _calculate_overall_risk(self, risk_factors: Dict) -> Dict:
        """מחשב סיכון כולל משוקלל"""
        try:
            weights = {
                'market_risk': 0.25,
                'position_risk': 0.30,
                'portfolio_risk': 0.25,
                'liquidity_risk': 0.10,
                'volatility_risk': 0.10
            }
            
            total_score = 0
            total_weight = 0
            
            for risk_type, weight in weights.items():
                if risk_type in risk_factors:
                    factors = risk_factors[risk_type]
                    if isinstance(factors, dict) and 'score' in factors:
                        total_score += factors['score'] * weight
                        total_weight += weight
                    elif isinstance(factors, dict):
                        # אם יש תתי-סיכונים
                        sub_scores = [f['score'] for f in factors.values() if isinstance(f, dict) and 'score' in f]
                        if sub_scores:
                            avg_sub_score = np.mean(sub_scores)
                            total_score += avg_sub_score * weight
                            total_weight += weight
            
            if total_weight > 0:
                overall_score = total_score / total_weight
            else:
                overall_score = 0.5
            
            # קביעת רמת סיכון
            if overall_score > 0.7:
                level = RiskLevel.VERY_HIGH
                can_proceed = False
            elif overall_score > 0.6:
                level = RiskLevel.HIGH
                can_proceed = False
            elif overall_score > 0.4:
                level = RiskLevel.MEDIUM
                can_proceed = True
            else:
                level = RiskLevel.LOW
                can_proceed = True
            
            return {
                'score': round(overall_score, 3),
                'level': level,
                'can_proceed': can_proceed
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating overall risk: {e}")
            return {'score': 0.5, 'level': RiskLevel.MEDIUM, 'can_proceed': True}
    
    def _suggest_position_adjustment(self, risk_assessment: Dict, portfolio: Dict) -> Dict:
        """מציע התאמות לפוזיציה"""
        try:
            current_quantity = risk_assessment['proposed_quantity']
            current_price = risk_assessment['current_price']
            max_position_size = self.risk_config['max_position_size']
            portfolio_value = portfolio.get('total_value', 1)
            
            # חישוב גודל פוזיציה מקסימלי
            max_quantity = (portfolio_value * max_position_size) / current_price
            
            if current_quantity > max_quantity:
                adjusted_quantity = max_quantity * 0.8  # 80% מהמקסימום
                reduction_pct = (current_quantity - adjusted_quantity) / current_quantity * 100
                
                return {
                    'action': 'REDUCE',
                    'current_quantity': current_quantity,
                    'recommended_quantity': adjusted_quantity,
                    'reduction_percent': round(reduction_pct, 1),
                    'reason': 'Position size exceeds risk limits'
                }
            else:
                return {
                    'action': 'PROCEED',
                    'current_quantity': current_quantity,
                    'recommended_quantity': current_quantity,
                    'reason': 'Position within acceptable limits'
                }
                
        except Exception as e:
            self.logger.error(f"Error suggesting adjustment: {e}")
            return {'action': 'HOLD', 'reason': 'Error in risk calculation'}
    
    def _calculate_stop_loss(self, symbol: str, price: float, 
                           market_data: Dict, action: TradeAction) -> float:
        """מחשב stop loss מומלץ"""
        try:
            volatility = market_data.get('volatility', 0.02)
            
            if self.risk_config['volatility_adjusted_sl']:
                # stop loss מותאם תנודתיות
                sl_distance = volatility * 2  # 2x volatility
            else:
                sl_distance = self.risk_config['default_stop_loss']
            
            if action == TradeAction.BUY:
                stop_loss = price * (1 - sl_distance)
            else:  # SELL
                stop_loss = price * (1 + sl_distance)
            
            return round(stop_loss, 6)
            
        except Exception as e:
            self.logger.error(f"Error calculating stop loss: {e}")
            return price * 0.97 if action == TradeAction.BUY else price * 1.03
    
    def _calculate_take_profit(self, symbol: str, price: float, 
                             market_data: Dict, action: TradeAction) -> float:
        """מחשב take profit מומלץ"""
        try:
            # risk-reward ratio של 1:2
            sl_distance = abs(price - self._calculate_stop_loss(symbol, price, market_data, action)) / price
            
            if action == TradeAction.BUY:
                take_profit = price * (1 + (sl_distance * 2))
            else:  # SELL
                take_profit = price * (1 - (sl_distance * 2))
            
            return round(take_profit, 6)
            
        except Exception as e:
            self.logger.error(f"Error calculating take profit: {e}")
            return price * 1.06 if action == TradeAction.BUY else price * 0.94
    
    def _calculate_position_size(self, symbol: str, price: float, 
                               portfolio: Dict, market_data: Dict) -> float:
        """מחשב גודל פוזיציה מומלץ"""
        try:
            portfolio_value = portfolio.get('total_value', 1000)
            risk_per_trade = self.risk_config['max_portfolio_risk']
            volatility = market_data.get('volatility', 0.02)
            
            # position size מותאם סיכון ותנודתיות
            if volatility > 0.04:
                risk_multiplier = 0.5
            elif volatility < 0.01:
                risk_multiplier = 1.5
            else:
                risk_multiplier = 1.0
            
            max_risk_amount = portfolio_value * risk_per_trade * risk_multiplier
            position_value = max_risk_amount / (volatility * 2)  # התאמה לתנודתיות
            
            max_position_value = portfolio_value * self.risk_config['max_position_size']
            position_value = min(position_value, max_position_value)
            
            quantity = position_value / price
            
            return round(quantity, 6)
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return (portfolio.get('total_value', 1000) * 0.02) / price
    
    def _calculate_portfolio_concentration(self, portfolio: Dict) -> float:
        """מחשב ריכוז תיק"""
        try:
            positions = portfolio.get('positions', {})
            if not positions:
                return 0.0
            
            total_value = portfolio.get('total_value', 1)
            if total_value == 0:
                return 0.0
            
            # חישוב Herfindahl-Hirschman Index (HHI) לריכוזיות
            hhi = 0
            for position in positions.values():
                position_share = position.get('value', 0) / total_value
                hhi += position_share ** 2
            
            return hhi
            
        except Exception as e:
            self.logger.error(f"Error calculating concentration: {e}")
            return 0.5
    
    def _assess_correlation_risk(self, portfolio: Dict, new_symbol: str) -> Dict:
        """מעריך סיכון correlation"""
        try:
            # סימולציה - בפועל ידרוש נתוני correlation
            positions = portfolio.get('positions', {})
            
            if len(positions) < 2:
                return {'level': RiskLevel.LOW, 'score': 0.2, 'message': "Insufficient positions for correlation analysis"}
            
            # בדיקת correlation עם נכסים קיימים
            high_correlation_count = 0
            for symbol, position in positions.items():
                # סימולציית correlation - בפועל תגיע ממסד נתונים
                simulated_correlation = np.random.uniform(0.1, 0.8)
                if simulated_correlation > self.risk_config['max_correlation']:
                    high_correlation_count += 1
            
            correlation_ratio = high_correlation_count / len(positions)
            
            if correlation_ratio > 0.5:
                return {
                    'level': RiskLevel.HIGH,
                    'score': 0.8,
                    'message': f"High correlation with {high_correlation_count} existing positions"
                }
            elif correlation_ratio > 0.3:
                return {
                    'level': RiskLevel.MEDIUM,
                    'score': 0.5,
                    'message': f"Moderate correlation with {high_correlation_count} positions"
                }
            else:
                return {
                    'level': RiskLevel.LOW,
                    'score': 0.2,
                    'message': "Low correlation risk"
                }
                
        except Exception as e:
            self.logger.error(f"Error assessing correlation risk: {e}")
            return {'level': RiskLevel.MEDIUM, 'score': 0.5, 'message': str(e)}
    
    def _calculate_diversification_score(self, portfolio: Dict) -> float:
        """מחשב ציון גיוון תיק"""
        try:
            positions = portfolio.get('positions', {})
            if not positions:
                return 0.0
            
            # ציון גיוון בסיסי - יותר נכסים = יותר גיוון
            num_positions = len(positions)
            max_diversification = 10  # מקסימום נכסים לגיוון אופטימלי
            
            diversification_score = min(num_positions / max_diversification, 1.0)
            
            return diversification_score
            
        except Exception as e:
            self.logger.error(f"Error calculating diversification: {e}")
            return 0.5
    
    def _get_fallback_assessment(self, symbol: str, action: TradeAction) -> Dict:
        """מחזיר הערכת סיכון גיבוי"""
        return {
            'symbol': symbol,
            'action': action.value,
            'overall_risk_score': 0.5,
            'overall_risk_level': RiskLevel.MEDIUM,
            'can_proceed': True,
            'warnings': ['Using fallback risk assessment'],
            'timestamp': datetime.now().isoformat()
        }
    
    def monitor_portfolio_risk(self, portfolio: Dict, market_data: Dict) -> Dict:
        """מנטר סיכון תיק רציף"""
        try:
            risk_report = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_metrics': {},
                'risk_alerts': [],
                'recommendations': []
            }
            
            # ניתוח drawdown
            current_drawdown = portfolio.get('current_drawdown', 0)
            if current_drawdown > self.risk_config['max_drawdown'] * 0.8:
                risk_report['risk_alerts'].append({
                    'type': 'DRAWDOWN_WARNING',
                    'message': f"Drawdown approaching limit: {current_drawdown:.1%}",
                    'severity': 'HIGH'
                })
            
            # ניתוח ריכוזיות
            concentration = self._calculate_portfolio_concentration(portfolio)
            if concentration > 0.6:
                risk_report['risk_alerts'].append({
                    'type': 'CONCENTRATION_WARNING',
                    'message': f"High portfolio concentration: {concentration:.1%}",
                    'severity': 'MEDIUM'
                })
            
            # ניתוח גיוון
            diversification = self._calculate_diversification_score(portfolio)
            if diversification < 0.3:
                risk_report['recommendations'].append({
                    'action': 'DIVERSIFY',
                    'message': "Consider diversifying portfolio",
                    'priority': 'MEDIUM'
                })
            
            risk_report['portfolio_metrics'] = {
                'current_drawdown': current_drawdown,
                'concentration_index': concentration,
                'diversification_score': diversification,
                'total_positions': len(portfolio.get('positions', {})),
                'portfolio_value': portfolio.get('total_value', 0)
            }
            
            return risk_report
            
        except Exception as e:
            self.logger.error(f"Error in portfolio risk monitoring: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
