import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from scipy.stats import pearsonr

class CorrelationAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_correlation(self, symbol1: str, symbol2: str, period: int = 30) -> Dict:
        """מנתח קורלציה בין שני מטבעות"""
        try:
            # קבלת נתונים היסטוריים (בפועל זה יגיע מה-API)
            data1 = self._get_sample_data(symbol1, period)
            data2 = self._get_sample_data(symbol2, period)
            
            # חישוב קורלציה
            correlation, p_value = pearsonr(data1['returns'], data2['returns'])
            
            # חישוב תנועות מתואמות
            movement_correlation = self._calculate_movement_correlation(data1, data2)
            
            return {
                'symbols': f"{symbol1}-{symbol2}",
                'correlation_coefficient': round(correlation, 4),
                'p_value': round(p_value, 4),
                'movement_correlation': movement_correlation,
                'strength': self._get_correlation_strength(correlation),
                'period_days': period,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing correlation: {e}")
            return {}
    
    def multi_symbol_correlation(self, symbols: List[str]) -> pd.DataFrame:
        """מנתח קורלציה בין מספר מטבעות"""
        try:
            corr_matrix = pd.DataFrame(index=symbols, columns=symbols)
            
            for i, sym1 in enumerate(symbols):
                for j, sym2 in enumerate(symbols):
                    if i == j:
                        corr_matrix.loc[sym1, sym2] = 1.0
                    else:
                        correlation = self.analyze_correlation(sym1, sym2)
                        corr_matrix.loc[sym1, sym2] = correlation.get('correlation_coefficient', 0)
            
            return corr_matrix
            
        except Exception as e:
            self.logger.error(f"Error in multi-symbol correlation: {e}")
            return pd.DataFrame()
    
    def _calculate_movement_correlation(self, data1: Dict, data2: Dict) -> Dict:
        """מחשב קורלציית תנועות"""
        same_direction = 0
        total_days = len(data1['prices'])
        
        for i in range(1, total_days):
            move1 = data1['prices'][i] > data1['prices'][i-1]
            move2 = data2['prices'][i] > data2['prices'][i-1]
            
            if move1 == move2:
                same_direction += 1
        
        correlation_percent = (same_direction / (total_days - 1)) * 100
        
        return {
            'same_direction_percent': round(correlation_percent, 2),
            'same_direction_days': same_direction,
            'total_days_analyzed': total_days - 1
        }
    
    def _get_correlation_strength(self, correlation: float) -> str:
        """מחזיר חוזק קורלציה"""
        abs_corr = abs(correlation)
        
        if abs_corr >= 0.8:
            return "VERY_STRONG"
        elif abs_corr >= 0.6:
            return "STRONG"
        elif abs_corr >= 0.4:
            return "MODERATE"
        elif abs_corr >= 0.2:
            return "WEAK"
        else:
            return "VERY_WEAK"
    
    def _get_sample_data(self, symbol: str, period: int) -> Dict:
        """נתוני דמה - בפועל יגיעו מ-API"""
        base_price = 2.45 if 'TON' in symbol else 320.0
        prices = [base_price * (1 + np.random.normal(0, 0.02)) for _ in range(period)]
        returns = [((prices[i] - prices[i-1]) / prices[i-1]) for i in range(1, len(prices))]
        
        return {'prices': prices, 'returns': returns}
