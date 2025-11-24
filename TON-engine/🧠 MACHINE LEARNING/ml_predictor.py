import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import joblib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class AdvancedMLPredictor:
    """מודל Machine Learning מתקדם לחיזוי מחירים"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.scalers = {}
        self.model_performance = {}
        
        # הגדרות מודלים
        self.model_config = {
            'lstm': {
                'sequence_length': 60,
                'epochs': 100,
                'batch_size': 32,
                'units': 50,
                'dropout': 0.2
            },
            'xgboost': {
                'n_estimators': 1000,
                'max_depth': 8,
                'learning_rate': 0.1,
                'subsample': 0.8
            },
            'lightgbm': {
                'n_estimators': 1000,
                'max_depth': 8,
                'learning_rate': 0.1,
                'num_leaves': 31
            },
            'random_forest': {
                'n_estimators': 500,
                'max_depth': 10,
                'min_samples_split': 5
            }
        }
        
        self.setup_models()
    
    def setup_models(self):
        """מאתחל את המודלים"""
        try:
            # LSTM Model
            self.models['lstm'] = self._create_lstm_model()
            
            # XGBoost
            self.models['xgboost'] = xgb.XGBRegressor(
                n_estimators=self.model_config['xgboost']['n_estimators'],
                max_depth=self.model_config['xgboost']['max_depth'],
                learning_rate=self.model_config['xgboost']['learning_rate'],
                subsample=self.model_config['xgboost']['subsample'],
                random_state=42
            )
            
            # LightGBM
            self.models['lightgbm'] = lgb.LGBMRegressor(
                n_estimators=self.model_config['lightgbm']['n_estimators'],
                max_depth=self.model_config['lightgbm']['max_depth'],
                learning_rate=self.model_config['lightgbm']['learning_rate'],
                num_leaves=self.model_config['lightgbm']['num_leaves'],
                random_state=42
            )
            
            # Random Forest
            self.models['random_forest'] = RandomForestRegressor(
                n_estimators=self.model_config['random_forest']['n_estimators'],
                max_depth=self.model_config['random_forest']['max_depth'],
                min_samples_split=self.model_config['random_forest']['min_samples_split'],
                random_state=42
            )
            
            # Gradient Boosting
            self.models['gradient_boosting'] = GradientBoostingRegressor(
                n_estimators=500,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            # SVR
            self.models['svr'] = SVR(kernel='rbf', C=1.0, epsilon=0.1)
            
            self.logger.info("✅ ML models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up models: {e}")
    
    def _create_lstm_model(self) -> Sequential:
        """יוצר מודל LSTM"""
        model = Sequential([
            LSTM(self.model_config['lstm']['units'], 
                 return_sequences=True, 
                 input_shape=(self.model_config['lstm']['sequence_length'], 1)),
            Dropout(self.model_config['lstm']['dropout']),
            LSTM(self.model_config['lstm']['units'], return_sequences=True),
            Dropout(self.model_config['lstm']['dropout']),
            LSTM(self.model_config['lstm']['units']),
            Dropout(self.model_config['lstm']['dropout']),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), 
                     loss='mse', 
                     metrics=['mae'])
        return model
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """מכין features מתקדמים למודל"""
        try:
            # Features בסיסיים
            df = df.copy()
            
            # מחירים ו-returns
            df['returns'] = df['close'].pct_change()
            df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
            
            # ממוצעים נעים
            for window in [5, 10, 20, 50]:
                df[f'sma_{window}'] = df['close'].rolling(window=window).mean()
                df[f'ema_{window}'] = df['close'].ewm(span=window).mean()
                df[f'returns_ma_{window}'] = df['returns'].rolling(window=window).mean()
                df[f'volatility_{window}'] = df['returns'].rolling(window=window).std()
            
            # RSI
            df['rsi_14'] = self._calculate_rsi(df['close'], 14)
            df['rsi_21'] = self._calculate_rsi(df['close'], 21)
            
            # MACD
            macd, signal, histogram = self._calculate_macd(df['close'])
            df['macd'] = macd
            df['macd_signal'] = signal
            df['macd_histogram'] = histogram
            
            # Bollinger Bands
            bb_upper, bb_lower, bb_middle = self._calculate_bollinger_bands(df['close'])
            df['bb_upper'] = bb_upper
            df['bb_lower'] = bb_lower
            df['bb_middle'] = bb_middle
            df['bb_position'] = (df['close'] - bb_lower) / (bb_upper - bb_lower)
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            df['obv'] = self._calculate_obv(df['close'], df['volume'])
            
            # תבניות מחיר
            df['price_trend'] = self._calculate_price_trend(df['close'])
            df['support_resistance'] = self._calculate_support_resistance_strength(df)
            
            # Features סטטיסטיים
            df['price_zscore'] = (df['close'] - df['close'].rolling(20).mean()) / df['close'].rolling(20).std()
            df['volume_zscore'] = (df['volume'] - df['volume'].rolling(20).mean()) / df['volume'].rolling(20).std()
            
            # Features זמן
            df['hour'] = df.index.hour
            df['day_of_week'] = df.index.dayofweek
            df['day_of_month'] = df.index.day
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            
            # מידול תנודתיות (GARCH-like)
            df['volatility_cluster'] = df['returns'].rolling(5).std()
            df['volatility_regime'] = (df['volatility_cluster'] > df['volatility_cluster'].rolling(20).mean()).astype(int)
            
            # מידול momentum
            df['momentum_1'] = df['close'] / df['close'].shift(1) - 1
            df['momentum_5'] = df['close'] / df['close'].shift(5) - 1
            df['momentum_10'] = df['close'] / df['close'].shift(10) - 1
            
            # Correlation עם שוק (מדומה)
            df['market_correlation'] = np.random.uniform(0.5, 0.9, len(df))
            
            # ניקוי NaN values
            df = df.replace([np.inf, -np.inf], np.nan)
            df = df.ffill().bfill()
            
            self.logger.info(f"✅ Prepared {len(df.columns)} features for ML model")
            return df
            
        except Exception as e:
            self.logger.error(f"Error preparing features: {e}")
            return df
    
    def _calculate_rsi(self, prices: pd.Series, window: int) -> pd.Series:
        """מחשב RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """מחשב MACD"""
        ema_12 = prices.ewm(span=12).mean()
        ema_26 = prices.ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal
        return macd, signal, histogram
    
    def _calculate_bollinger_bands(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """מחשב Bollinger Bands"""
        sma_20 = prices.rolling(20).mean()
        std_20 = prices.rolling(20).std()
        upper = sma_20 + (std_20 * 2)
        lower = sma_20 - (std_20 * 2)
        return upper, lower, sma_20
    
    def _calculate_obv(self, prices: pd.Series, volume: pd.Series) -> pd.Series:
        """מחשב On Balance Volume"""
        obv = (volume * np.sign(prices.diff())).cumsum()
        return obv
    
    def _calculate_price_trend(self, prices: pd.Series) -> pd.Series:
        """מחשב מגמת מחיר"""
        returns = prices.pct_change()
        trend = returns.rolling(10).mean()
        return trend
    
    def _calculate_support_resistance_strength(self, df: pd.DataFrame) -> pd.Series:
        """מחשב חוזק תמיכה/התנגדות"""
        # מימוש פשטני - בפועל ידרוש ניתוח טכני מתקדם
        resistance = df['high'].rolling(20).max()
        support = df['low'].rolling(20).min()
        current_price = df['close']
        
        # חישוב מרחק מרמות מפתח
        resistance_distance = (resistance - current_price) / current_price
        support_distance = (current_price - support) / current_price
        
        # ציון חוזק - גבוה יותר כאשר המחיר קרוב לתמיכה/התנגדות
        strength = np.where(
            resistance_distance < support_distance,
            resistance_distance,
            -support_distance
        )
        
        return pd.Series(strength, index=df.index)
    
    def create_sequences(self, data: np.ndarray, sequence_length: int) -> Tuple[np.ndarray, np.ndarray]:
        """יוצר sequences עבור LSTM"""
        X, y = [], []
        for i in range(sequence_length, len(data)):
            X.append(data[i-sequence_length:i])
            y.append(data[i])
        return np.array(X), np.array(y)
    
    def train_models(self, df: pd.DataFrame, target_col: str = 'close', test_size: float = 0.2):
        """מאמן את כל המודלים"""
        try:
            # הכנת features
            feature_df = self.prepare_features(df)
            
            # בחירת features רלוונטיים
            feature_columns = [col for col in feature_df.columns 
                             if col not in [target_col, 'open', 'high', 'low', 'volume'] 
                             and not col.startswith('target_')]
            
            X = feature_df[feature_columns].values
            y = feature_df[target_col].values
            
            # הסרה של NaN values
            mask = ~np.isnan(X).any(axis=1) & ~np.isnan(y)
            X = X[mask]
            y = y[mask]
            
            if len(X) == 0:
                self.logger.error("No valid data for training")
                return
            
            # Split data - שימוש ב-TimeSeriesSplit עבור נתונים כרונולוגיים
            tscv = TimeSeriesSplit(n_splits=5)
            
            # Scaling
            self.scalers['X'] = StandardScaler()
            self.scalers['y'] = StandardScaler()
            
            X_scaled = self.scalers['X'].fit_transform(X)
            y_scaled = self.scalers['y'].fit_transform(y.reshape(-1, 1)).flatten()
            
            # אימון כל המודלים
            for model_name, model in self.models.items():
                try:
                    if model_name == 'lstm':
                        # הכנת sequences ל-LSTM
                        sequence_length = self.model_config['lstm']['sequence_length']
                        if len(X_scaled) > sequence_length:
                            X_seq, y_seq = self.create_sequences(X_scaled, sequence_length)
                            
                            # Reshape for LSTM
                            X_seq = X_seq.reshape((X_seq.shape[0], X_seq.shape[1], 1))
                            
                            # Split for LSTM
                            split_idx = int(len(X_seq) * (1 - test_size))
                            X_train, X_test = X_seq[:split_idx], X_seq[split_idx:]
                            y_train, y_test = y_seq[:split_idx], y_seq[split_idx:]
                            
                            # אימון LSTM
                            history = model.fit(
                                X_train, y_train,
                                epochs=self.model_config['lstm']['epochs'],
                                batch_size=self.model_config['lstm']['batch_size'],
                                validation_data=(X_test, y_test),
                                verbose=0
                            )
                            
                            # חיזוי והערכת ביצועים
                            y_pred_scaled = model.predict(X_test)
                            y_pred = self.scalers['y'].inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
                            y_true = self.scalers['y'].inverse_transform(y_test.reshape(-1, 1)).flatten()
                            
                        else:
                            self.logger.warning("Not enough data for LSTM training")
                            continue
                    
                    else:
                        # Split רגיל עבור מודלים אחרים
                        split_idx = int(len(X_scaled) * (1 - test_size))
                        X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
                        y_train, y_test = y_scaled[:split_idx], y_scaled[split_idx:]
                        
                        # אימון המודל
                        model.fit(X_train, y_train)
                        
                        # חיזוי
                        y_pred_scaled = model.predict(X_test)
                        y_pred = self.scalers['y'].inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
                        y_true = self.scalers['y'].inverse_transform(y_test.reshape(-1, 1)).flatten()
                    
                    # הערכת ביצועים
                    performance = self._evaluate_model(y_true, y_pred)
                    self.model_performance[model_name] = performance
                    
                    self.logger.info(f"✅ Trained {model_name}: MAE={performance['mae']:.4f}, R²={performance['r2']:.4f}")
                    
                except Exception as e:
                    self.logger.error(f"Error training {model_name}: {e}")
            
            # בחירת המודל הטוב ביותר
            best_model_name = max(self.model_performance, 
                                key=lambda x: self.model_performance[x]['r2'])
            self.best_model = self.models[best_model_name]
            self.best_model_name = best_model_name
            
            self.logger.info(f"🎯 Best model: {best_model_name} with R²={self.model_performance[best_model_name]['r2']:.4f}")
            
        except Exception as e:
            self.logger.error(f"Error in train_models: {e}")
    
    def _evaluate_model(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """מעריך את ביצועי המודל"""
        return {
            'mae': mean_absolute_error(y_true, y_pred),
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'r2': r2_score(y_true, y_pred),
            'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        }
    
    def predict_future(self, df: pd.DataFrame, periods: int = 10) -> Dict:
        """מבצע חיזוי לעתיד"""
        try:
            # הכנת features
            feature_df = self.prepare_features(df)
            
            # בחירת features
            feature_columns = [col for col in feature_df.columns 
                             if col not in ['close', 'open', 'high', 'low', 'volume'] 
                             and not col.startswith('target_')]
            
            X_current = feature_df[feature_columns].iloc[-1:].values
            
            if len(X_current) == 0:
                return self._get_fallback_prediction(periods)
            
            # Scaling
            X_scaled = self.scalers['X'].transform(X_current)
            
            predictions = {}
            confidence_scores = {}
            
            for model_name, model in self.models.items():
                try:
                    if model_name == 'lstm':
                        # חיזוי עם LSTM דורש sequences
                        sequence_length = self.model_config['lstm']['sequence_length']
                        if len(feature_df) >= sequence_length:
                            # שימוש ב-sequence האחרון
                            X_seq = X_scaled[-sequence_length:].reshape(1, sequence_length, 1)
                            y_pred_scaled = model.predict(X_seq, verbose=0)
                            prediction = self.scalers['y'].inverse_transform(y_pred_scaled.reshape(-1, 1))[0][0]
                        else:
                            continue
                    else:
                        # חיזוי עם מודלים אחרים
                        y_pred_scaled = model.predict(X_scaled)
                        prediction = self.scalers['y'].inverse_transform(y_pred_scaled.reshape(-1, 1))[0][0]
                    
                    predictions[model_name] = max(0, prediction)  # מחיר לא יכול להיות שלילי
                    
                    # ציון ביטחון מבוסס ביצועי המודל
                    if model_name in self.model_performance:
                        confidence_scores[model_name] = max(0, min(1, self.model_performance[model_name]['r2']))
                    else:
                        confidence_scores[model_name] = 0.5
                        
                except Exception as e:
                    self.logger.error(f"Error predicting with {model_name}: {e}")
                    predictions[model_name] = df['close'].iloc[-1]
                    confidence_scores[model_name] = 0.1
            
            # חיזוי ממוצע משוקלל
            if predictions:
                current_price = df['close'].iloc[-1]
                weighted_predictions = []
                weights = []
                
                for model_name, pred in predictions.items():
                    weight = confidence_scores[model_name]
                    weighted_predictions.append(pred * weight)
                    weights.append(weight)
                
                if sum(weights) > 0:
                    ensemble_prediction = sum(weighted_predictions) / sum(weights)
                    ensemble_confidence = sum(weights) / len(weights)
                else:
                    ensemble_prediction = current_price
                    ensemble_confidence = 0.1
                
                # חיזוי ל-multiple periods
                future_predictions = self._predict_multiple_periods(
                    df, ensemble_prediction, periods, ensemble_confidence
                )
                
                return {
                    'current_price': current_price,
                    'predictions': predictions,
                    'ensemble_prediction': ensemble_prediction,
                    'confidence_scores': confidence_scores,
                    'ensemble_confidence': ensemble_confidence,
                    'future_predictions': future_predictions,
                    'model_performance': self.model_performance,
                    'best_model': self.best_model_name,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return self._get_fallback_prediction(periods)
                
        except Exception as e:
            self.logger.error(f"Error in predict_future: {e}")
            return self._get_fallback_prediction(periods)
    
    def _predict_multiple_periods(self, df: pd.DataFrame, next_prediction: float, 
                                periods: int, confidence: float) -> List[Dict]:
        """מבצע חיזוי ל-multiple periods"""
        try:
            predictions = []
            current_price = df['close'].iloc[-1]
            
            for i in range(periods):
                # חישוב שינוי אחוזי משוער
                if i == 0:
                    price_change = (next_prediction - current_price) / current_price
                else:
                    # שימוש בתנודתיות היסטורית לחיזוי עתידי
                    historical_volatility = df['close'].pct_change().std()
                    price_change = np.random.normal(0, historical_volatility)
                
                predicted_price = current_price * (1 + price_change)
                
                # ירידה בביטחון ככל שהחיזוי רחוק יותר
                period_confidence = confidence * (1 - (i * 0.1))
                
                predictions.append({
                    'period': i + 1,
                    'predicted_price': max(0, predicted_price),
                    'price_change_percent': price_change * 100,
                    'confidence': max(0.1, period_confidence),
                    'time_horizon': f"{i+1} period{'s' if i+1 > 1 else ''}"
                })
                
                current_price = predicted_price
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error in multiple periods prediction: {e}")
            return []
    
    def _get_fallback_prediction(self, periods: int) -> Dict:
        """מחזיר חיזוי גיבוי"""
        current_price = 2.45  # מחיר TON משוער
        return {
            'current_price': current_price,
            'ensemble_prediction': current_price,
            'ensemble_confidence': 0.1,
            'future_predictions': [
                {
                    'period': i + 1,
                    'predicted_price': current_price,
                    'price_change_percent': 0,
                    'confidence': 0.1,
                    'time_horizon': f"{i+1} period{'s' if i+1 > 1 else ''}"
                } for i in range(periods)
            ],
            'timestamp': datetime.now().isoformat(),
            'fallback': True
        }
    
    def save_models(self, path: str = 'models/'):
        """שומר את המודלים"""
        try:
            import os
            os.makedirs(path, exist_ok=True)
            
            for model_name, model in self.models.items():
                if model_name == 'lstm':
                    model.save(f'{path}/{model_name}_model.h5')
                else:
                    joblib.dump(model, f'{path}/{model_name}_model.pkl')
            
            joblib.dump(self.scalers, f'{path}/scalers.pkl')
            joblib.dump(self.model_performance, f'{path}/model_performance.pkl')
            
            self.logger.info(f"💾 Models saved to {path}")
            
        except Exception as e:
            self.logger.error(f"Error saving models: {e}")
    
    def load_models(self, path: str = 'models/'):
        """טוען מודלים שמורים"""
        try:
            for model_name in self.models.keys():
                if model_name == 'lstm':
                    from tensorflow.keras.models import load_model
                    self.models[model_name] = load_model(f'{path}/{model_name}_model.h5')
                else:
                    self.models[model_name] = joblib.load(f'{path}/{model_name}_model.pkl')
            
            self.scalers = joblib.load(f'{path}/scalers.pkl')
            self.model_performance = joblib.load(f'{path}/model_performance.pkl')
            
            self.logger.info("📂 Models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading models: {e}")
    
    def get_model_insights(self, df: pd.DataFrame) -> Dict:
        """מחזיר תובנות מהמודל"""
        try:
            feature_df = self.prepare_features(df)
            feature_columns = [col for col in feature_df.columns 
                             if col not in ['close', 'open', 'high', 'low', 'volume'] 
                             and not col.startswith('target_')]
            
            if self.best_model_name and self.best_model_name != 'lstm':
                # Feature importance עבור מודלים tree-based
                if hasattr(self.best_model, 'feature_importances_'):
                    importances = self.best_model.feature_importances_
                    feature_importance = dict(zip(feature_columns, importances))
                    top_features = sorted(feature_importance.items(), 
                                       key=lambda x: x[1], reverse=True)[:10]
                else:
                    top_features = []
            else:
                top_features = []
            
            return {
                'best_model': self.best_model_name,
                'model_performance': self.model_performance.get(self.best_model_name, {}),
                'top_features': top_features,
                'total_features': len(feature_columns),
                'data_points': len(df),
                'training_status': 'trained' if self.model_performance else 'not_trained',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting model insights: {e}")
            return {}
