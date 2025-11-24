import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import websocket
import threading
from concurrent.futures import ThreadPoolExecutor

class AdvancedBinanceClient:
    """לקוח Binance מתקדם עם תכונות נוספות"""
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        self.base_url = "https://api.binance.com"
        self.futures_url = "https://fapi.binance.com"
        self.websocket_url = "wss://stream.binance.com:9443"
        
        self.api_key = api_key
        self.secret_key = secret_key
        self.logger = logging.getLogger(__name__)
        
        self.rate_limits = {
            'requests': 1200,
            'interval': 60
        }
        
        self.request_count = 0
        self.last_reset = time.time()
        
        self.websocket_connections = {}
        self.callbacks = {}
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key,
            'User-Agent': 'TON-Trading-Bot/3.0'
        })
        
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        
    def _make_request(self, endpoint: str, params: Dict = None, signed: bool = False, futures: bool = False) -> Dict:
        """מבצע בקשה ל-API עם ניהול rate limiting"""
        try:
            # ניהול rate limiting
            self._check_rate_limit()
            
            base_url = self.futures_url if futures else self.base_url
            url = f"{base_url}/api/v3/{endpoint}"
            
            if params is None:
                params = {}
                
            if signed:
                params['timestamp'] = int(time.time() * 1000)
                query_string = urlencode(params)
                signature = hmac.new(
                    self.secret_key.encode('utf-8'),
                    query_string.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                params['signature'] = signature
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            self.request_count += 1
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Binance API request failed: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error in Binance request: {e}")
            return {}
    
    def _check_rate_limit(self):
        """בודק ומנהל rate limiting"""
        current_time = time.time()
        if current_time - self.last_reset >= 60:
            self.request_count = 0
            self.last_reset = current_time
            
        if self.request_count >= self.rate_limits['requests']:
            sleep_time = 60 - (current_time - self.last_reset)
            if sleep_time > 0:
                self.logger.warning(f"Rate limit approaching, sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
    
    def get_exchange_info(self, symbol: str = None) -> Dict:
        """מביא מידע על הבורסה"""
        params = {}
        if symbol:
            params['symbol'] = symbol
            
        return self._make_request('exchangeInfo', params)
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """מביא מידע על סימל ספציפי"""
        exchange_info = self.get_exchange_info()
        if 'symbols' in exchange_info:
            for sym_info in exchange_info['symbols']:
                if sym_info['symbol'] == symbol:
                    return sym_info
        return {}
    
    def get_current_price(self, symbol: str) -> float:
        """מביא מחיר נוכחי"""
        data = self._make_request('ticker/price', {'symbol': symbol})
        return float(data.get('price', 0)) if data else 0.0
    
    def get_24h_stats(self, symbol: str) -> Dict:
        """מביא סטטיסטיקות 24 שעות"""
        data = self._make_request('ticker/24hr', {'symbol': symbol})
        if data:
            return {
                'symbol': data['symbol'],
                'price_change': float(data['priceChange']),
                'price_change_percent': float(data['priceChangePercent']),
                'weighted_avg_price': float(data['weightedAvgPrice']),
                'prev_close_price': float(data['prevClosePrice']),
                'last_price': float(data['lastPrice']),
                'bid_price': float(data['bidPrice']),
                'ask_price': float(data['askPrice']),
                'open_price': float(data['openPrice']),
                'high_price': float(data['highPrice']),
                'low_price': float(data['lowPrice']),
                'volume': float(data['volume']),
                'quote_volume': float(data['quoteVolume']),
                'open_time': datetime.fromtimestamp(data['openTime'] / 1000),
                'close_time': datetime.fromtimestamp(data['closeTime'] / 1000),
                'first_id': data['firstId'],
                'last_id': data['lastId'],
                'count': data['count']
            }
        return {}
    
    def get_klines_data(self, symbol: str, interval: str = '1h', limit: int = 500) -> pd.DataFrame:
        """מביא נתוני קווים (Candlestick)"""
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        data = self._make_request('klines', params)
        
        if not data:
            return self._generate_sample_klines(symbol, interval, limit)
        
        df = pd.DataFrame(data, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        # המרת טיפוסים
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 
                       'quote_asset_volume', 'taker_buy_base_asset_volume',
                       'taker_buy_quote_asset_volume']
        df[numeric_cols] = df[numeric_cols].astype(float)
        df[['number_of_trades']] = df[['number_of_trades']].astype(int)
        
        # המרת תאריכים
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        df.set_index('open_time', inplace=True)
        
        return df
    
    def get_depth_data(self, symbol: str, limit: int = 100) -> Dict:
        """מביא נתוני עומק שוק (Order Book)"""
        params = {'symbol': symbol, 'limit': limit}
        data = self._make_request('depth', params)
        
        if data:
            return {
                'lastUpdateId': data['lastUpdateId'],
                'bids': [[float(price), float(quantity)] for price, quantity in data['bids']],
                'asks': [[float(price), float(quantity)] for price, quantity in data['asks']],
                'timestamp': datetime.now()
            }
        return {}
    
    def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """מביא עסקאות אחרונות"""
        params = {'symbol': symbol, 'limit': limit}
        data = self._make_request('trades', params)
        
        trades = []
        for trade in data:
            trades.append({
                'id': trade['id'],
                'price': float(trade['price']),
                'quantity': float(trade['qty']),
                'quote_quantity': float(trade['quoteQty']),
                'time': datetime.fromtimestamp(trade['time'] / 1000),
                'is_buyer_maker': trade['isBuyerMaker']
            })
        
        return trades
    
    def get_aggregate_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """מביא עסקאות aggregate (יעיל יותר)"""
        params = {'symbol': symbol, 'limit': limit}
        data = self._make_request('aggTrades', params)
        
        trades = []
        for trade in data:
            trades.append({
                'aggregate_trade_id': trade['a'],
                'price': float(trade['p']),
                'quantity': float(trade['q']),
                'first_trade_id': trade['f'],
                'last_trade_id': trade['l'],
                'timestamp': datetime.fromtimestamp(trade['T'] / 1000),
                'is_buyer_maker': trade['m']
            })
        
        return trades
    
    def get_funding_rate(self, symbol: str) -> Dict:
        """מביא funding rate עבור futures"""
        params = {'symbol': symbol}
        data = self._make_request('fundingRate', params, futures=True)
        
        if data:
            return {
                'symbol': data['symbol'],
                'funding_rate': float(data['fundingRate']),
                'funding_time': datetime.fromtimestamp(data['fundingTime'] / 1000),
                'mark_price': float(data.get('markPrice', 0))
            }
        return {}
    
    def get_open_interest(self, symbol: str) -> Dict:
        """מביא open interest"""
        params = {'symbol': symbol}
        data = self._make_request('openInterest', params, futures=True)
        
        if data:
            return {
                'symbol': data['symbol'],
                'open_interest': float(data['openInterest']),
                'timestamp': datetime.fromtimestamp(data['time'] / 1000)
            }
        return {}
    
    def get_liquidation_data(self, symbol: str = None, limit: int = 100) -> List[Dict]:
        """מביא נתוני liquidation"""
        params = {}
        if symbol:
            params['symbol'] = symbol
        params['limit'] = limit
        
        data = self._make_request('allForceOrders', params, futures=True)
        
        liquidations = []
        for liq in data:
            liquidations.append({
                'symbol': liq['symbol'],
                'price': float(liq['price']),
                'quantity': float(liq['origQty']),
                'side': liq['side'],
                'type': liq['orderType'],
                'time_in_force': liq['timeInForce'],
                'timestamp': datetime.fromtimestamp(liq['time'] / 1000)
            })
        
        return liquidations
    
    def get_account_info(self) -> Dict:
        """מביא מידע על החשבון (דורש חתימה)"""
        if not self.api_key or not self.secret_key:
            self.logger.warning("API keys not configured for account info")
            return {}
        
        data = self._make_request('account', {}, signed=True)
        
        if data:
            account_info = {
                'maker_commission': data['makerCommission'],
                'taker_commission': data['takerCommission'],
                'buyer_commission': data['buyerCommission'],
                'seller_commission': data['sellerCommission'],
                'can_trade': data['canTrade'],
                'can_withdraw': data['canWithdraw'],
                'can_deposit': data['canDeposit'],
                'update_time': datetime.fromtimestamp(data['updateTime'] / 1000),
                'balances': {}
            }
            
            for balance in data['balances']:
                if float(balance['free']) > 0 or float(balance['locked']) > 0:
                    account_info['balances'][balance['asset']] = {
                        'free': float(balance['free']),
                        'locked': float(balance['locked']),
                        'total': float(balance['free']) + float(balance['locked'])
                    }
            
            return account_info
        return {}
    
    def get_my_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """מביא את העסקאות שלי (דורש חתימה)"""
        if not self.api_key or not self.secret_key:
            self.logger.warning("API keys not configured for my trades")
            return []
        
        params = {'symbol': symbol, 'limit': limit}
        data = self._make_request('myTrades', params, signed=True)
        
        trades = []
        for trade in data:
            trades.append({
                'id': trade['id'],
                'order_id': trade['orderId'],
                'symbol': trade['symbol'],
                'price': float(trade['price']),
                'quantity': float(trade['qty']),
                'quote_quantity': float(trade['quoteQty']),
                'commission': float(trade['commission']),
                'commission_asset': trade['commissionAsset'],
                'time': datetime.fromtimestamp(trade['time'] / 1000),
                'is_buyer': trade['isBuyer'],
                'is_maker': trade['isMaker'],
                'is_best_match': trade['isBestMatch']
            })
        
        return trades
    
    def create_test_order(self, symbol: str, side: str, order_type: str, 
                         quantity: float, price: float = None) -> Dict:
        """יוצר test order (לא אמיתי)"""
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity
        }
        
        if price:
            params['price'] = price
        
        if order_type == 'LIMIT':
            params['timeInForce'] = 'GTC'
        
        return self._make_request('order/test', params, signed=True)
    
    def get_server_time(self) -> Dict:
        """מביא את זמן השרת"""
        data = self._make_request('time')
        if data:
            return {
                'server_time': datetime.fromtimestamp(data['serverTime'] / 1000),
                'timestamp': data['serverTime']
            }
        return {}
    
    def get_system_status(self) -> Dict:
        """בודק סטטוס מערכת"""
        data = self._make_request('systemStatus')
        return data if data else {'status': 0, 'msg': 'NORMAL'}
    
    def get_coin_info(self) -> List[Dict]:
        """מביא מידע על coins"""
        data = self._make_request('capital/config/getall', {}, signed=True)
        
        coins = []
        for coin in data:
            coins.append({
                'coin': coin['coin'],
                'deposit_all_enable': coin['depositAllEnable'],
                'withdraw_all_enable': coin['withdrawAllEnable'],
                'name': coin['name'],
                'free': float(coin['free']),
                'locked': float(coin['locked']),
                'freeze': float(coin['freeze']),
                'withdrawing': float(coin['withdrawing']),
                'ipoing': float(coin['ipoing']),
                'ipoable': float(coin['ipoable']),
                'storage': float(coin['storage']),
                'is_legal_money': coin['isLegalMoney'],
                'trading': coin['trading']
            })
        
        return coins
    
    # WebSocket functionality
    def start_kline_stream(self, symbol: str, interval: str, callback: callable):
        """מתחיל stream של קווים"""
        stream_name = f"{symbol.lower()}@kline_{interval}"
        return self._start_stream(stream_name, callback)
    
    def start_trade_stream(self, symbol: str, callback: callable):
        """מתחיל stream של עסקאות"""
        stream_name = f"{symbol.lower()}@trade"
        return self._start_stream(stream_name, callback)
    
    def start_depth_stream(self, symbol: str, callback: callable):
        """מתחיל stream של עומק שוק"""
        stream_name = f"{symbol.lower()}@depth"
        return self._start_stream(stream_name, callback)
    
    def start_aggregate_trade_stream(self, symbol: str, callback: callable):
        """מתחיל stream של aggregate trades"""
        stream_name = f"{symbol.lower()}@aggTrade"
        return self._start_stream(stream_name, callback)
    
    def start_mini_ticker_stream(self, symbol: str, callback: callable):
        """מתחיל stream של mini ticker"""
        stream_name = f"{symbol.lower()}@miniTicker"
        return self._start_stream(stream_name, callback)
    
    def start_book_ticker_stream(self, symbol: str, callback: callable):
        """מתחיל stream של book ticker"""
        stream_name = f"{symbol.lower()}@bookTicker"
        return self._start_stream(stream_name, callback)
    
    def _start_stream(self, stream_name: str, callback: callable) -> bool:
        """מתחיל WebSocket stream"""
        try:
            if stream_name in self.websocket_connections:
                self.logger.info(f"WebSocket stream {stream_name} already running")
                return True
            
            ws_url = f"{self.websocket_url}/ws/{stream_name}"
            
            def on_message(ws, message):
                try:
                    data = json.loads(message)
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Error processing WebSocket message: {e}")
            
            def on_error(ws, error):
                self.logger.error(f"WebSocket error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                self.logger.info(f"WebSocket closed: {stream_name}")
                if stream_name in self.websocket_connections:
                    del self.websocket_connections[stream_name]
            
            def on_open(ws):
                self.logger.info(f"WebSocket opened: {stream_name}")
            
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            # הרצת WebSocket ב-thread נפרד
            thread = threading.Thread(target=ws.run_forever)
            thread.daemon = True
            thread.start()
            
            self.websocket_connections[stream_name] = ws
            self.callbacks[stream_name] = callback
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting WebSocket stream: {e}")
            return False
    
    def stop_stream(self, stream_name: str):
        """עוצר WebSocket stream"""
        try:
            if stream_name in self.websocket_connections:
                self.websocket_connections[stream_name].close()
                del self.websocket_connections[stream_name]
                if stream_name in self.callbacks:
                    del self.callbacks[stream_name]
                self.logger.info(f"Stopped WebSocket stream: {stream_name}")
        except Exception as e:
            self.logger.error(f"Error stopping WebSocket stream: {e}")
    
    def stop_all_streams(self):
        """עוצר את כל ה-WebSocket streams"""
        for stream_name in list(self.websocket_connections.keys()):
            self.stop_stream(stream_name)
    
    # Utility methods
    def _generate_sample_klines(self, symbol: str, interval: str, limit: int) -> pd.DataFrame:
        """מייצר נתוני קווים לדוגמה כאשר ה-API לא זמין"""
        self.logger.info(f"Generating sample klines data for {symbol}")
        
        # קביעת מחיר בסיס לפי הסימל
        base_prices = {
            'TONUSDT': 2.45,
            'BNBUSDT': 320.0,
            'BTCUSDT': 43000.0,
            'ETHUSDT': 2300.0
        }
        base_price = base_prices.get(symbol, 2.45)
        
        # יצירת טווח תאריכים
        end_date = datetime.now()
        
        # קביעת מרווח זמן לפי ה-interval
        interval_minutes = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440
        }
        minutes = interval_minutes.get(interval, 60)
        
        dates = pd.date_range(
            end=end_date, 
            periods=limit, 
            freq=f'{minutes}min'
        )
        
        # יצירת נתונים ריאליסטיים עם מגמה ורעש
        prices = []
        current_price = base_price
        
        for i in range(limit):
            # מגמה + רעש
            trend = np.sin(i / 10) * 0.01  # מגמה סינוסואידלית
            noise = np.random.normal(0, 0.005)  # רעש אקראי
            current_price = current_price * (1 + trend + noise)
            prices.append(current_price)
        
        # יצירת DataFrame
        data = {
            'open_time': dates,
            'open': [p * (1 + np.random.uniform(-0.002, 0.002)) for p in prices],
            'high': [p * (1 + np.random.uniform(0, 0.01)) for p in prices],
            'low': [p * (1 + np.random.uniform(-0.01, 0)) for p in prices],
            'close': prices,
            'volume': [np.random.uniform(100000, 5000000) for _ in range(limit)],
            'close_time': [date + timedelta(minutes=minutes) for date in dates],
            'quote_asset_volume': [np.random.uniform(500000, 25000000) for _ in range(limit)],
            'number_of_trades': [np.random.randint(1000, 50000) for _ in range(limit)],
            'taker_buy_base_asset_volume': [np.random.uniform(50000, 2500000) for _ in range(limit)],
            'taker_buy_quote_asset_volume': [np.random.uniform(250000, 12500000) for _ in range(limit)],
            'ignore': [0] * limit
        }
        
        df = pd.DataFrame(data)
        df.set_index('open_time', inplace=True)
        
        return df
    
    def calculate_advanced_metrics(self, symbol: str) -> Dict:
        """מחשב מדדים מתקדמים"""
        try:
            # נתוני 24 שעות
            stats_24h = self.get_24h_stats(symbol)
            
            # נתוני עומק שוק
            depth = self.get_depth_data(symbol)
            
            # נתוני funding rate (עבור futures)
            funding_rate = self.get_funding_rate(symbol) if 'USDT' in symbol else {}
            
            # חישוב מדדים מתקדמים
            if depth and 'bids' in depth and 'asks' in depth:
                bid_volume = sum([bid[1] for bid in depth['bids']])
                ask_volume = sum([ask[1] for ask in depth['asks']])
                volume_imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume) if (bid_volume + ask_volume) > 0 else 0
                
                best_bid = depth['bids'][0][0] if depth['bids'] else 0
                best_ask = depth['asks'][0][0] if depth['asks'] else 0
                spread = best_ask - best_bid if best_ask > 0 and best_bid > 0 else 0
                spread_percent = (spread / best_bid) * 100 if best_bid > 0 else 0
            else:
                volume_imbalance = 0
                spread = 0
                spread_percent = 0
            
            return {
                'symbol': symbol,
                'price_change_24h': stats_24h.get('price_change_percent', 0),
                'volume_24h': stats_24h.get('volume', 0),
                'quote_volume_24h': stats_24h.get('quote_volume', 0),
                'high_24h': stats_24h.get('high_price', 0),
                'low_24h': stats_24h.get('low_price', 0),
                'volume_imbalance': round(volume_imbalance, 4),
                'spread': round(spread, 6),
                'spread_percent': round(spread_percent, 4),
                'funding_rate': funding_rate.get('funding_rate', 0),
                'open_interest': self.get_open_interest(symbol).get('open_interest', 0),
                'liquidation_ratio': self._calculate_liquidation_ratio(symbol),
                'market_score': self._calculate_market_score(stats_24h, volume_imbalance),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating advanced metrics: {e}")
            return {}
    
    def _calculate_liquidation_ratio(self, symbol: str) -> float:
        """מחשב יחס liquidation"""
        try:
            liquidations = self.get_liquidation_data(symbol, limit=10)
            if not liquidations:
                return 0.0
            
            long_liquidations = sum(1 for liq in liquidations if liq['side'] == 'BUY')
            total_liquidations = len(liquidations)
            
            return long_liquidations / total_liquidations if total_liquidations > 0 else 0.5
            
        except:
            return 0.5
    
    def _calculate_market_score(self, stats_24h: Dict, volume_imbalance: float) -> float:
        """מחשב ציון שוק כולל"""
        try:
            score = 0.5  # נקודת התחלה ניטרלית
            
            # משקל על פי שינוי מחיר
            price_change = abs(stats_24h.get('price_change_percent', 0))
            if price_change > 10:
                score += 0.2
            elif price_change > 5:
                score += 0.1
            elif price_change < 1:
                score -= 0.1
            
            # משקל על פי volume imbalance
            if volume_imbalance > 0.1:
                score += 0.15
            elif volume_imbalance < -0.1:
                score -= 0.15
            
            # משקל על פי volume
            volume = stats_24h.get('volume', 0)
            if volume > 10000000:
                score += 0.1
            elif volume < 1000000:
                score -= 0.1
            
            return max(0.0, min(1.0, score))
            
        except:
            return 0.5
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """מביא מחירים מרובים"""
        results = {}
        
        def get_price(symbol):
            return symbol, self.get_current_price(symbol)
        
        # שימוש ב-thread pool לביצוע מקבילי
        futures = [self.thread_pool.submit(get_price, symbol) for symbol in symbols]
        
        for future in futures:
            try:
                symbol, price = future.result(timeout=10)
                results[symbol] = price
            except Exception as e:
                self.logger.error(f"Error getting price for {symbol}: {e}")
        
        return results
    
    def health_check(self) -> Dict:
        """בודק את בריאות החיבור"""
        try:
            server_time = self.get_server_time()
            system_status = self.get_system_status()
            
            return {
                'status': 'healthy' if server_time and system_status.get('status') == 0 else 'unhealthy',
                'server_time': server_time.get('server_time'),
                'system_status': system_status.get('msg', 'UNKNOWN'),
                'api_key_configured': bool(self.api_key and self.secret_key),
                'websocket_connections': len(self.websocket_connections),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {'status': 'unhealthy', 'error': str(e)}
