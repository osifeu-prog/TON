import sqlite3
import logging
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional
import hashlib
import hmac

class PaymentManager:
    def __init__(self):
        self.conn = sqlite3.connect('database/payments.db', check_same_thread=False)
        self.create_tables()
        self.logger = logging.getLogger(__name__)
        
        self.load_pricing()
        self.setup_payment_methods()
        
        self.analytics_data = {
            'daily_revenue': 0,
            'monthly_revenue': 0,
            'conversion_rate': 0,
            'refund_rate': 0
        }

    def setup_payment_methods(self):
        """מגדיר שיטות תשלום מתקדמות"""
        self.payment_details = {
            'bank': {
                'bank_name': 'בנק הפועלים',
                'branch': '153 - כפר גנים',
                'account_number': '73462',
                'account_holder': 'אוסף אונגר',
                'supported_currencies': ['ILS', 'USD'],
                'processing_time': '1-2 ימי עסקים'
            },
            'crypto': {
                'ton_wallet': 'UQCr743gEr_nqV_0SBkSp3CtYS_15R3LDLBvLmKeEv7XdGvp',
                'bnb_wallet': '0x742d35Cc6634C0532925a3b8D4C9e7a7a6F1a8c7',
                'btc_wallet': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                'network': 'TON/BNB/BTC',
                'min_confirmation': 3,
                'supported_coins': ['TON', 'BNB', 'BTC', 'ETH']
            },
            'paypal': {
                'email': 'payments@tontrading.com',
                'supported_currencies': ['USD', 'EUR'],
                'fee_percentage': 3.5
            },
            'credit_card': {
                'processor': 'Stripe',
                'supported_cards': ['VISA', 'MasterCard', 'AMEX'],
                'fee_percentage': 2.9,
                'secure_3d': True
            }
        }

    def load_pricing(self):
        """טוען מחירים מהקובץ"""
        try:
            if os.path.exists('database/pricing_config.json'):
                with open('database/pricing_config.json', 'r', encoding='utf-8') as f:
                    pricing_data = json.load(f)
                    self.pricing = pricing_data.get('pricing', self.get_default_pricing())
                    self.features = pricing_data.get('features', self.get_default_features())
                    self.promotions = pricing_data.get('promotions', self.get_default_promotions())
            else:
                self.pricing = self.get_default_pricing()
                self.features = self.get_default_features()
                self.promotions = self.get_default_promotions()
                self.save_pricing()
                
        except Exception as e:
            self.logger.error(f"Error loading pricing: {e}")
            self.pricing = self.get_default_pricing()
            self.features = self.get_default_features()
            self.promotions = self.get_default_promotions()

    def get_default_pricing(self):
        """מחירי ברירת מחדל עם מבצעים"""
        return {
            'monthly': {
                'regular': 24.99,
                'black_friday': 2.99,
                'annual_savings': '88%',
                'popular': True
            },
            'quarterly': {
                'regular': 64.99,
                'black_friday': 7.99,
                'annual_savings': '87%',
                'popular': False
            },
            'yearly': {
                'regular': 249.00,
                'black_friday': 29.99,
                'annual_savings': '88%',
                'popular': False
            },
            'lifetime': {
                'regular': 599.00,
                'black_friday': 71.99,
                'annual_savings': '88%',
                'popular': True
            }
        }

    def get_default_features(self):
        """פיצ'רים של ברירת מחדל"""
        return {
            'free': [
                "ניתוח בסיסי 1x ביום",
                "התראות TON בלבד",
                "פקודת /analysis בסיסית",
                "צפייה בסטטוס",
                "גישה לניתוחי דמו",
                "מעקב לווייתנים בסיסי"
            ],
            'premium': [
                "✅ ניתוחים מתקדמים כל 15 דקות",
                "✅ ניתוח מרובה מטבעות (TON + BNB + BTC)",
                "✅ התראות בזמן אמת",
                "✅ ניתוחים טכניים מתקדמים",
                "✅ חיזוי Machine Learning",
                "✅ נקודות כניסה/יציאה מפורטות",
                "✅ גישה לקבוצת VIP",
                "✅ תמיכה מועדפת",
                "✅ עדכונים ראשונים לפיצ'רים חדשים",
                "✅ מעקב לווייתנים מתקדם",
                "✅ ניתוח פיבונאצ'י מלא",
                "✅ ניתוח קורלציות",
                "✅ דוחות מותאמים אישית",
                "✅ גישה ל-API מתקדם"
            ]
        }

    def get_default_promotions(self):
        """מבצעים וקופונים"""
        return {
            'black_friday': {
                'active': True,
                'discount': '88%',
                'end_date': '2024-12-01',
                'description': 'BLACK FRIDAY - הנחה חד פעמית!'
            },
            'welcome_10': {
                'active': True,
                'discount': '10%',
                'code': 'WELCOME10',
                'description': 'הנחת ברוך הבא'
            },
            'referral_bonus': {
                'active': True,
                'bonus': '10%',
                'description': '10% מהתשלום הראשון של מוזמנים'
            }
        }

    def update_pricing(self, new_pricing: Dict):
        """מעדכן מחירים באופן דינמי"""
        try:
            self.pricing.update(new_pricing)
            self.save_pricing()
            self.logger.info("✅ Pricing updated successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error updating pricing: {e}")
            return False

    def save_pricing(self):
        """שומר את המחירים לקובץ"""
        try:
            os.makedirs('database', exist_ok=True)
            pricing_data = {
                'pricing': self.pricing,
                'features': self.features,
                'promotions': self.promotions,
                'last_updated': datetime.now().isoformat()
            }
            with open('database/pricing_config.json', 'w', encoding='utf-8') as f:
                json.dump(pricing_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving pricing: {e}")

    def create_tables(self):
        """יוצר טבלאות מסד נתונים מתקדמות"""
        cursor = self.conn.cursor()
        
        # טבלת משתמשים מורחבת
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                join_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_premium BOOLEAN DEFAULT FALSE,
                premium_until DATETIME,
                subscription_type TEXT DEFAULT 'free',
                referral_count INTEGER DEFAULT 0,
                total_earned REAL DEFAULT 0,
                analysis_count INTEGER DEFAULT 0,
                alerts_count INTEGER DEFAULT 0,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                preferences TEXT DEFAULT '{}',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # טבלת תשלומים מורחבת
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                currency TEXT DEFAULT 'USD',
                plan_type TEXT,
                subscription_period TEXT,
                payment_method TEXT,
                payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                transaction_id TEXT UNIQUE,
                proof_image TEXT,
                admin_approved BOOLEAN DEFAULT FALSE,
                refunded BOOLEAN DEFAULT FALSE,
                refund_reason TEXT,
                payment_gateway TEXT,
                gateway_transaction_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # טבלת referrals מורחבת
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                referral_id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                bonus_earned REAL DEFAULT 0,
                referral_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                conversion_type TEXT DEFAULT 'free',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                FOREIGN KEY (referred_id) REFERENCES users (user_id)
            )
        ''')
        
        # טבלת קופונים
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coupons (
                coupon_id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                discount_percent REAL,
                max_uses INTEGER,
                used_count INTEGER DEFAULT 0,
                valid_until DATETIME,
                active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # טבלת analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                revenue REAL DEFAULT 0,
                new_users INTEGER DEFAULT 0,
                premium_conversions INTEGER DEFAULT 0,
                referral_signups INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()

    def register_user(self, user_data: Dict) -> bool:
        """רושם משתמש חדש עם נתונים מורחבים"""
        try:
            cursor = self.conn.cursor()
            
            preferences = {
                'language': 'he',
                'timezone': 'Asia/Jerusalem',
                'notifications': True,
                'whale_alerts': True,
                'fibonacci_alerts': True
            }
            
            cursor.execute('''
                INSERT OR IGNORE INTO users 
                (user_id, username, first_name, last_name, join_date, preferences)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_data['id'],
                user_data.get('username'),
                user_data.get('first_name'),
                user_data.get('last_name'),
                datetime.now(),
                json.dumps(preferences)
            ))
            
            # אם המשתמש כבר קיים, עדכן last_active
            cursor.execute('''
                UPDATE users SET last_active = ? WHERE user_id = ?
            ''', (datetime.now(), user_data['id']))
            
            self.conn.commit()
            self.logger.info(f"✅ Registered/updated user: {user_data['id']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering user: {e}")
            return False

    def get_user(self, user_id: int) -> Optional[Dict]:
        """מביא נתוני משתמש מורחבים"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            
            if user:
                return {
                    'user_id': user[0],
                    'username': user[1],
                    'first_name': user[2],
                    'last_name': user[3],
                    'join_date': user[4],
                    'is_premium': bool(user[5]),
                    'premium_until': user[6],
                    'subscription_type': user[7],
                    'referral_count': user[8],
                    'total_earned': user[9],
                    'analysis_count': user[10],
                    'alerts_count': user[11],
                    'last_active': user[12],
                    'preferences': json.loads(user[13]) if user[13] else {},
                    'created_at': user[14]
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting user: {e}")
            return None

    def add_payment(self, user_id: int, amount: float, plan_type: str, 
                   payment_method: str, transaction_id: str, 
                   proof_image: str = None, coupon_code: str = None) -> Dict:
        """מוסיף תשלום חדש עם תמיכה בקופונים"""
        try:
            cursor = self.conn.cursor()
            
            # חישוב הנחה אם יש קופון
            final_amount = amount
            discount_applied = 0
            
            if coupon_code:
                discount = self.validate_coupon(coupon_code)
                if discount > 0:
                    discount_applied = amount * (discount / 100)
                    final_amount = amount - discount_applied
            
            # קביעת תקופת מנוי
            subscription_period = self._get_subscription_period(plan_type)
            
            cursor.execute('''
                INSERT INTO payments 
                (user_id, amount, plan_type, subscription_period, payment_method, 
                 transaction_id, proof_image, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, final_amount, plan_type, subscription_period, 
                 payment_method, transaction_id, proof_image, 'pending'))
            
            payment_id = cursor.lastrowid
            
            self.conn.commit()
            self.logger.info(f"✅ Payment recorded for user {user_id}")
            
            # עדכון סטטיסטיקות
            self._update_analytics('revenue', final_amount)
            
            # התראה על תשלום חדש
            self._notify_new_payment(user_id, final_amount, plan_type, discount_applied)
            
            return {
                'success': True,
                'payment_id': payment_id,
                'final_amount': final_amount,
                'discount_applied': discount_applied,
                'subscription_period': subscription_period
            }
            
        except Exception as e:
            self.logger.error(f"Error adding payment: {e}")
            return {'success': False, 'error': str(e)}

    def _get_subscription_period(self, plan_type: str) -> str:
        """מחזיר תקופת מנוי"""
        periods = {
            'monthly': '1 month',
            'quarterly': '3 months',
            'yearly': '1 year',
            'lifetime': 'lifetime'
        }
        return periods.get(plan_type, '1 month')

    def validate_coupon(self, coupon_code: str) -> float:
        """בודק תוקף קופון"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT discount_percent, max_uses, used_count, valid_until, active
                FROM coupons WHERE code = ?
            ''', (coupon_code,))
            
            coupon = cursor.fetchone()
            
            if not coupon:
                return 0
                
            discount, max_uses, used_count, valid_until, active = coupon
            
            if not active:
                return 0
                
            if max_uses and used_count >= max_uses:
                return 0
                
            if valid_until and datetime.now() > datetime.fromisoformat(valid_until):
                return 0
                
            # עדכן ספירת שימוש
            cursor.execute('''
                UPDATE coupons SET used_count = used_count + 1 WHERE code = ?
            ''', (coupon_code,))
            self.conn.commit()
            
            return discount
            
        except Exception as e:
            self.logger.error(f"Error validating coupon: {e}")
            return 0

    def _notify_new_payment(self, user_id: int, amount: float, plan_type: str, discount: float = 0):
        """שולח התראה על תשלום חדש"""
        try:
            user = self.get_user(user_id)
            if not user:
                return
                
            payment_message = f"""
💰 **תשלום חדש התקבל!**

👤 **משתמש:** {user.get('username', f"{user.get('first_name', '')} {user.get('last_name', '')}")}
🆔 **ID:** {user_id}
💳 **סכום:** ${amount:.2f}
📦 **חבילה:** {plan_type}
{'🎫 **הנחה:** ' + f"${discount:.2f}" if discount > 0 else ''}
⏰ **זמן:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

💎 **סטטוס:** ממתין לאישור
"""
            self.logger.info(f"Payment notification: {payment_message}")
            
        except Exception as e:
            self.logger.error(f"Error notifying new payment: {e}")

    def approve_payment(self, transaction_id: str) -> Dict:
        """מאשר תשלום ומשדרג משתמש"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('SELECT * FROM payments WHERE transaction_id = ?', (transaction_id,))
            payment = cursor.fetchone()
            
            if not payment:
                return {'success': False, 'error': 'Payment not found'}
            
            user_id = payment[1]
            plan_type = payment[4]
            subscription_period = payment[5]
            
            # חישוב תאריך סיום
            premium_until = self._calculate_premium_until(plan_type)
            
            cursor.execute('''
                UPDATE payments 
                SET status = 'completed', admin_approved = TRUE
                WHERE transaction_id = ?
            ''', (transaction_id,))
            
            cursor.execute('''
                UPDATE users 
                SET is_premium = TRUE, premium_until = ?, subscription_type = ?
                WHERE user_id = ?
            ''', (premium_until, plan_type, user_id))
            
            # בדיקת referral
            self._check_referral_bonus(user_id, payment[2])  # amount
            
            self.conn.commit()
            self.logger.info(f"✅ Payment approved and user {user_id} upgraded")
            
            return {
                'success': True,
                'user_id': user_id,
                'premium_until': premium_until,
                'subscription_type': plan_type
            }
            
        except Exception as e:
            self.logger.error(f"Error approving payment: {e}")
            return {'success': False, 'error': str(e)}

    def _calculate_premium_until(self, plan_type: str) -> datetime:
        """מחשב תאריך סיום מנוי"""
        if plan_type == 'monthly':
            return datetime.now() + timedelta(days=30)
        elif plan_type == 'quarterly':
            return datetime.now() + timedelta(days=90)
        elif plan_type == 'yearly':
            return datetime.now() + timedelta(days=365)
        elif plan_type == 'lifetime':
            return datetime.now() + timedelta(days=3650)  # 10 years
        else:
            return datetime.now() + timedelta(days=30)

    def _check_referral_bonus(self, user_id: int, amount: float):
        """בודק ומעניק bonus referral"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                SELECT referrer_id FROM referrals 
                WHERE referred_id = ? AND status = 'active'
            ''', (user_id,))
            
            referral = cursor.fetchone()
            if referral:
                referrer_id = referral[0]
                bonus_amount = amount * 0.10  # 10% bonus
                
                cursor.execute('''
                    UPDATE referrals 
                    SET bonus_earned = ?, status = 'completed'
                    WHERE referred_id = ? AND referrer_id = ?
                ''', (bonus_amount, user_id, referrer_id))
                
                cursor.execute('''
                    UPDATE users 
                    SET total_earned = total_earned + ?
                    WHERE user_id = ?
                ''', (bonus_amount, referrer_id))
                
                self.logger.info(f"✅ Referral bonus awarded: {referrer_id} -> {bonus_amount}")
                
        except Exception as e:
            self.logger.error(f"Error processing referral bonus: {e}")

    def check_premium_status(self, user_id: int) -> bool:
        """בודק סטטוס Premium"""
        try:
            user = self.get_user(user_id)
            if not user:
                return False
            
            if user['is_premium'] and user['premium_until']:
                premium_until = datetime.fromisoformat(user['premium_until'])
                if premium_until > datetime.now():
                    return True
                else:
                    self.downgrade_user(user_id)
                    return False
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking premium status: {e}")
            return False

    def downgrade_user(self, user_id: int):
        """מוריד משתמש ל-Free"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET is_premium = FALSE, premium_until = NULL, subscription_type = 'free'
                WHERE user_id = ?
            ''', (user_id,))
            self.conn.commit()
            self.logger.info(f"✅ User {user_id} downgraded to free")
        except Exception as e:
            self.logger.error(f"Error downgrading user: {e}")

    def add_referral(self, referrer_id: int, referred_id: int) -> bool:
        """מוסיף referral ומעדכן bonus"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                SELECT * FROM referrals 
                WHERE referrer_id = ? AND referred_id = ?
            ''', (referrer_id, referred_id))
            
            if cursor.fetchone():
                return False
            
            cursor.execute('''
                INSERT INTO referrals 
                (referrer_id, referred_id)
                VALUES (?, ?)
            ''', (referrer_id, referred_id))
            
            cursor.execute('''
                UPDATE users 
                SET referral_count = referral_count + 1
                WHERE user_id = ?
            ''', (referrer_id,))
            
            self.conn.commit()
            self.logger.info(f"✅ Referral added: {referrer_id} -> {referred_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding referral: {e}")
            return False

    def get_payment_info(self) -> Dict:
        """מחזיר מידע תמחור ופרטי תשלום מלא"""
        return {
            'pricing': self.pricing,
            'features': self.features,
            'promotions': self.promotions,
            'payment_methods': self.payment_details,
            'referral_bonus': "10% מהתשלום הראשון של מוזמנים",
            'premium_group_link': "https://t.me/+HIzvM8sEgh1kNWY0",
            'support_contact': "אוסף אונגר"
        }

    def get_admin_stats(self) -> Dict:
        """מחזיר סטטיסטיקות מערכת מתקדמות"""
        try:
            cursor = self.conn.cursor()
            
            # סטטיסטיקות בסיסיות
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE is_premium = 1')
            premium_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM payments WHERE status = "completed"')
            completed_payments = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(amount) FROM payments WHERE status = "completed"')
            total_revenue = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT COUNT(*) FROM referrals')
            total_referrals = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE("now")')
            new_users_today = cursor.fetchone()[0]
            
            # סטטיסטיקות מתקדמות
            cursor.execute('SELECT COUNT(*) FROM users WHERE last_active > datetime("now", "-7 days")')
            active_users_7d = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(amount) FROM payments WHERE status = "completed" AND payment_date > datetime("now", "-30 days")')
            monthly_revenue = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT COUNT(*) FROM payments WHERE status = "refunded"')
            refunded_payments = cursor.fetchone()[0]
            
            # חישוב מדדים
            conversion_rate = (premium_users / total_users * 100) if total_users > 0 else 0
            refund_rate = (refunded_payments / completed_payments * 100) if completed_payments > 0 else 0
            arpu = (total_revenue / premium_users) if premium_users > 0 else 0  # Average Revenue Per User
            
            return {
                'total_users': total_users,
                'premium_users': premium_users,
                'free_users': total_users - premium_users,
                'completed_payments': completed_payments,
                'total_revenue': total_revenue,
                'monthly_revenue': monthly_revenue,
                'total_referrals': total_referrals,
                'new_users_today': new_users_today,
                'active_users_7d': active_users_7d,
                'premium_conversion_rate': round(conversion_rate, 1),
                'refund_rate': round(refund_rate, 1),
                'arpu': round(arpu, 2),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting admin stats: {e}")
            return {}

    def _update_analytics(self, metric: str, value: float):
        """מעדכן סטטיסטיקות"""
        try:
            cursor = self.conn.cursor()
            today = datetime.now().date().isoformat()
            
            cursor.execute('SELECT * FROM analytics WHERE date = ?', (today,))
            if cursor.fetchone():
                cursor.execute(f'UPDATE analytics SET {metric} = {metric} + ? WHERE date = ?', (value, today))
            else:
                cursor.execute(f'INSERT INTO analytics (date, {metric}) VALUES (?, ?)', (today, value))
            
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error updating analytics: {e}")

    def get_premium_users(self) -> List[int]:
        """מחזיר רשימת משתמשי Premium פעילים"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT user_id FROM users WHERE is_premium = 1 AND premium_until > datetime("now")')
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Error getting premium users: {e}")
            return []

    def update_user_preferences(self, user_id: int, preferences: Dict):
        """מעדכן העדפות משתמש"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE users SET preferences = ? WHERE user_id = ?', 
                         (json.dumps(preferences), user_id))
            self.conn.commit()
            self.logger.info(f"✅ Preferences updated for user {user_id}")
        except Exception as e:
            self.logger.error(f"Error updating user preferences: {e}")

    def increment_analysis_count(self, user_id: int):
        """מעדכן ספירת ניתוחים"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE users SET analysis_count = analysis_count + 1 WHERE user_id = ?', (user_id,))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error incrementing analysis count: {e}")

    def increment_alerts_count(self, user_id: int):
        """מעדכן ספירת התראות"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('UPDATE users SET alerts_count = alerts_count + 1 WHERE user_id = ?', (user_id,))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error incrementing alerts count: {e}")
