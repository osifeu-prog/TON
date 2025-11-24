import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import time

class WhaleTracker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.whale_thresholds = {
            'TON': 50000,  # 50,000 TON
            'BNB': 1000,   # 1,000 BNB
            'BTC': 10,     # 10 BTC
            'ETH': 100     # 100 ETH
        }
    
    def track_whale_transactions(self, symbol: str) -> List[Dict]:
        """מעקב אחר עסקאות לווייתנים"""
        try:
            # סימולציה - בחיים האמיתיים זה יתחבר ל-API של ביננס/בלוקצ'יין
            transactions = self._simulate_whale_activity(symbol)
            
            whale_txs = []
            for tx in transactions:
                if self._is_whale_transaction(tx, symbol):
                    whale_txs.append({
                        'symbol': symbol,
                        'amount': tx['amount'],
                        'price': tx['price'],
                        'timestamp': tx['timestamp'],
                        'type': tx['type'],
                        'whale_size': self._get_whale_size(tx['amount'], symbol),
                        'impact_score': self._calculate_impact_score(tx)
                    })
            
            return whale_txs
            
        except Exception as e:
            self.logger.error(f"Error tracking whale transactions: {e}")
            return []
    
    def _is_whale_transaction(self, transaction: Dict, symbol: str) -> bool:
        """בודק אם עסקה נחשבת ללווייתן"""
        threshold = self.whale_thresholds.get(symbol, 1000)
        return transaction['amount'] >= threshold
    
    def _get_whale_size(self, amount: float, symbol: str) -> str:
        """מחזיר גודל לווייתן"""
        threshold = self.whale_thresholds.get(symbol, 1000)
        
        if amount >= threshold * 5:
            return "MEGA_WHALE"
        elif amount >= threshold * 2:
            return "LARGE_WHALE"
        else:
            return "WHALE"
    
    def _calculate_impact_score(self, transaction: Dict) -> float:
        """מחשב ציון השפעה של עסקת לווייתן"""
        amount_score = min(transaction['amount'] / 100000, 1.0)
        price_impact = abs(transaction.get('price_impact', 0)) / 10
        volume_ratio = transaction.get('volume_ratio', 0)
        
        return min((amount_score * 0.5 + price_impact * 0.3 + volume_ratio * 0.2), 1.0)
    
    def _simulate_whale_activity(self, symbol: str) -> List[Dict]:
        """סימולציה של פעילות לווייתנים - במקום API אמיתי"""
        base_price = 2.45 if 'TON' in symbol else 320.0
        transactions = []
        
        for i in range(10):
            transactions.append({
                'amount': np.random.uniform(1000, 100000),
                'price': base_price * np.random.uniform(0.98, 1.02),
                'timestamp': datetime.now() - timedelta(hours=i),
                'type': 'BUY' if np.random.random() > 0.5 else 'SELL',
                'price_impact': np.random.uniform(0.1, 5.0),
                'volume_ratio': np.random.uniform(0.01, 0.5)
            })
        
        return transactions
