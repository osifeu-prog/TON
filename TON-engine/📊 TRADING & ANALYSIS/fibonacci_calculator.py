
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from datetime import datetime

class FibonacciCalculator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.retracement_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        self.extension_levels = [1.272, 1.414, 1.618, 2.0, 2.618]
    
    def calculate_retracement(self, high: float, low: float) -> Dict:
        """מחשב רמות פיבונאצ'י retracement"""
        try:
            difference = high - low
            levels = {}
            
            for level in self.retracement_levels:
                price_level = high - (difference * level)
                levels[f'fib_{level}'] = round(price_level, 4)
            
            return {
                'swing_high': high,
                'swing_low': low,
                'retracement_levels': levels,
                'current_range': round(difference, 4)
            }
        except Exception as e:
            self.logger.error(f"Error calculating Fibonacci retracement: {e}")
            return {}
    
    def calculate_extensions(self, high: float, low: float, current_price: float) -> Dict:
        """מחשב רמות פיבונאצ'י extension"""
        try:
            difference = high - low
            levels = {}
            
            for level in self.extension_levels:
                price_level = high + (difference * level)
                levels[f'ext_{level}'] = round(price_level, 4)
            
            return {
                'extension_levels': levels,
                'current_position': self._get_fib_position(current_price, high, low)
            }
        except Exception as e:
            self.logger.error(f"Error calculating Fibonacci extensions: {e}")
            return {}
    
    def _get_fib_position(self, price: float, high: float, low: float) -> str:
        """מחזיר מיקום נוכחי ביחס לרמות פיבונאצ'י"""
        if price >= high:
            return "ABOVE_HIGH"
        elif price <= low:
            return "BELOW_LOW"
        
        diff = high - low
        position = (high - price) / diff
        
        if position <= 0.236:
            return "0.236_RETRACEMENT"
        elif position <= 0.382:
            return "0.382_RETRACEMENT"
        elif position <= 0.5:
            return "0.5_RETRACEMENT"
        elif position <= 0.618:
            return "0.618_RETRACEMENT"
        elif position <= 0.786:
            return "0.786_RETRACEMENT"
        else:
            return "DEEP_RETRACEMENT"
