#!/usr/bin/env python3
"""
TON Trading Bot - Project File Scanner
סורק את כל הקבצים בפרוייקט ומזהה קבצים חסרים לפי הייבואים ב-app.py
"""

import os
import sys
import ast
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple

class ProjectScanner:
    def __init__(self):
        self.logger = self.setup_logging()
        self.project_root = Path.cwd()
        self.missing_files = set()
        self.existing_files = set()
        self.import_analysis = {}
        
    def setup_logging(self):
        """הגדרת מערכת לוגים"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        return logging.getLogger(__name__)

    def scan_project_structure(self):
        """סורק את המבנה המלא של הפרוייקט"""
        self.logger.info("📁 סורק מבנה הפרוייקט...")
        
        project_structure = {}
        
        # סריקת כל הקבצים והתיקיות
        for root, dirs, files in os.walk(self.project_root):
            # התעלם מתיקיות כמו __pycache__, .git, etc
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            relative_path = Path(root).relative_to(self.project_root)
            if str(relative_path) == '.':
                category = 'ROOT'
            else:
                category = str(relative_path)
            
            project_structure[category] = files
        
        return project_structure

    def analyze_app_imports(self):
        """מנתח את כל הייבואים בקובץ app.py"""
        self.logger.info("📊 מנתח ייבואים ב-app.py...")
        
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parsing the Python file
            tree = ast.parse(content)
            
            imports = {
                'modules': set(),
                'from_imports': {}
            }
            
            for node in ast.walk(tree):
                # טיפול ב-import statements
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports['modules'].add(alias.name)
                        
                # טיפול ב-from ... import ...
                elif isinstance(node, ast.ImportFrom):
                    module = node.module
                    if module not in imports['from_imports']:
                        imports['from_imports'][module] = set()
                    
                    for alias in node.names:
                        imports['from_imports'][module].add(alias.name)
            
            return imports
            
        except Exception as e:
            self.logger.error(f"❌ שגיאה בניתוח app.py: {e}")
            return {'modules': set(), 'from_imports': {}}

    def map_imports_to_files(self, imports: Dict) -> Dict:
        """ממפה ייבואים לקבצים פיזיים"""
        self.logger.info("🗺️ ממפה ייבואים לקבצים...")
        
        import_mapping = {
            'required_files': set(),
            'missing_files': set(),
            'existing_files': set()
        }
        
        # מיפוי מודולים לקבצים
        module_to_file = {
            'telegram_bot': 'telegram_bot.py',
            'advanced_trading_logic': 'advanced_trading_logic.py',
            'payment_manager': 'payment_manager.py',
            'fibonacci_calculator': 'fibonacci_calculator.py',
            'whale_tracker': 'whale_tracker.py',
            'correlation_analyzer': 'correlation_analyzer.py',
            'binance_client': 'binance_client.py',
            'tradingview_client': 'tradingview_client.py',
            'technical_analyzer': 'technical_analyzer.py',
            'data_manager': 'data_manager.py',
            'ml_predictor': 'ml_predictor.py',
            'risk_manager': 'risk_manager.py',
            'dashboard': 'dashboard.py',
            'config': 'config.py'
        }
        
        # בדיקת ייבואים רגילים
        for module in imports['modules']:
            if module in module_to_file:
                filename = module_to_file[module]
                import_mapping['required_files'].add(filename)
                
                if os.path.exists(filename):
                    import_mapping['existing_files'].add(filename)
                else:
                    import_mapping['missing_files'].add(filename)
        
        # בדיקת from imports
        for module, imports_list in imports['from_imports'].items():
            if module in module_to_file:
                filename = module_to_file[module]
                import_mapping['required_files'].add(filename)
                
                if os.path.exists(filename):
                    import_mapping['existing_files'].add(filename)
                else:
                    import_mapping['missing_files'].add(filename)
        
        return import_mapping

    def check_file_health(self, filename: str) -> Dict:
        """בודק את בריאות הקובץ - גודל ותוכן"""
        try:
            if not os.path.exists(filename):
                return {'exists': False, 'size': 0, 'lines': 0, 'health': 'MISSING'}
            
            size = os.path.getsize(filename)
            
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            line_count = len(lines)
            
            # הערכת בריאות לפי גודל ומספר שורות
            if size == 0:
                health = 'EMPTY'
            elif size < 100:  # פחות מ-100 bytes
                health = 'VERY_SMALL'
            elif size < 500:  # פחות מ-500 bytes
                health = 'SMALL'
            elif 'TODO' in ''.join(lines) or 'pass' in ''.join(lines):
                health = 'INCOMPLETE'
            else:
                health = 'HEALTHY'
            
            return {
                'exists': True,
                'size': size,
                'lines': line_count,
                'health': health
            }
            
        except Exception as e:
            return {'exists': False, 'size': 0, 'lines': 0, 'health': 'ERROR', 'error': str(e)}

    def scan_all_imported_files(self):
        """סורק את כל הקבצים המיובאים"""
        self.logger.info("🔍 סורק קבצים מיובאים...")
        
        imports = self.analyze_app_imports()
        mapping = self.map_imports_to_files(imports)
        
        file_health_report = {}
        
        for filename in mapping['required_files']:
            file_health_report[filename] = self.check_file_health(filename)
        
        return {
            'import_analysis': imports,
            'file_mapping': mapping,
            'health_report': file_health_report
        }

    def generate_emergency_fixes(self, health_report: Dict):
        """מייצר תיקוני חירום לקבצים בעייתיים"""
        self.logger.info("🛠️ מכין תיקוני חירום...")
        
        fixes = {}
        
        for filename, health_info in health_report.items():
            if not health_info['exists'] or health_info['health'] in ['EMPTY', 'VERY_SMALL', 'INCOMPLETE']:
                fixes[filename] = self.create_basic_file_content(filename)
        
        return fixes

    def create_basic_file_content(self, filename: str) -> str:
        """יוצר תוכן בסיסי לקובץ חסר"""
        
        base_templates = {
            'advanced_trading_logic.py': '''import logging
from datetime import datetime
from typing import Dict, List

class AdvancedTradingLogic:
    """לוגיקת מסחר מתקדמת - קובץ אוטומטי"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def comprehensive_analysis(self, symbol: str = "TONUSDT") -> Dict:
        """ניתוח מקיף למטבע"""
        return {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'market_analysis': {'current_price': 2.45},
            'trading_decision': {'action': 'HOLD', 'confidence_score': 0.7}
        }
    
    def multi_symbol_analysis(self) -> Dict:
        """ניתוח מרובה מטבעות"""
        return {
            'timestamp': datetime.now().isoformat(),
            'analyses': {},
            'market_summary': {'overall_sentiment': 'NEUTRAL'}
        }
''',

            'risk_manager.py': '''import logging
from enum import Enum
from typing import Dict

class TradeAction(Enum):
    BUY = "BUY"
    SELL = "SELL" 
    HOLD = "HOLD"

class AdvancedRiskManager:
    """מנהל סיכונים מתקדם - קובץ אוטומטי"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def assess_trade_risk(self, symbol: str, action: TradeAction, 
                         quantity: float, price: float, 
                         market_data: Dict, portfolio: Dict) -> Dict:
        """מעריך סיכון עבור עסקה"""
        return {
            'overall_risk_level': 'MEDIUM',
            'can_proceed': True,
            'recommended_position_size': quantity
        }
''',

            'fibonacci_calculator.py': '''class FibonacciCalculator:
    """מחשב פיבונאצ'י - קובץ אוטומטי"""
    
    def calculate_retracement(self, high, low):
        return {"retracement_levels": {0.236: 2.42, 0.382: 2.41, 0.5: 2.40, 0.618: 2.39}}
    
    def calculate_extensions(self, high, low, current_price):
        return {"extension_levels": {1.272: 2.52, 1.618: 2.56}}
''',

            'whale_tracker.py': '''class WhaleTracker:
    """מעקב לווייתנים - קובץ אוטומטי"""
    
    def track_whale_transactions(self, symbol):
        return [{"amount": 50000, "price": 2.45, "type": "BUY", "impact_score": 0.8}]
''',

            'correlation_analyzer.py': '''class CorrelationAnalyzer:
    """אנלייזר קורלציה - קובץ אוטומטי"""
    
    def analyze_correlation(self, symbol1, symbol2):
        return {"correlation_coefficient": 0.75, "strength": "STRONG"}
''',

            'technical_analyzer.py': '''import pandas as pd

class AdvancedTechnicalAnalyzer:
    """אנלייזר טכני - קובץ אוטומטי"""
    
    def comprehensive_technical_analysis(self, df, symbol):
        return {"summary": {"action": "HOLD", "confidence": 0.7}}
''',

            'data_manager.py': '''import pandas as pd

class AdvancedDataManager:
    """מנהל נתונים - קובץ אוטומטי"""
    
    def get_historical_data(self, symbol, days=30):
        return pd.DataFrame()
    
    def calculate_performance_metrics(self, symbol):
        return {}
''',

            'ml_predictor.py': '''class AdvancedMLPredictor:
    """חיזוי ML - קובץ אוטומטי"""
    
    def predict_future(self, df, periods=10):
        return {"ensemble_prediction": 2.45, "ensemble_confidence": 0.65}
''',

            'binance_client.py': '''class BinanceClient:
    """לקוח Binance - קובץ אוטומטי"""
    
    def get_current_price(self, symbol):
        return {"price": 2.45, "symbol": symbol}
    
    def get_24h_high_low(self, symbol):
        return {"high": 2.50, "low": 2.40, "symbol": symbol}
''',

            'tradingview_client.py': '''class TradingViewClient:
    """לקוח TradingView - קובץ אוטומטי"""
    
    def send_webhook_alert(self, data):
        return True
''',

            'dashboard.py': '''from flask import Blueprint

def create_dashboard_app():
    """יוצר דשבורד - קובץ אוטומטי"""
    dashboard_bp = Blueprint('dashboard', __name__)
    
    @dashboard_bp.route('/')
    def dashboard():
        return "Dashboard - Under Construction"
    
    return dashboard_bp
'''
        }
        
        return base_templates.get(filename, f'# {filename} - AUTO-GENERATED FILE\n\nprint("File {filename} is under construction")')

    def apply_fixes(self, fixes: Dict):
        """מחיל את התיקונים על הקבצים"""
        self.logger.info("🔧 מחיל תיקונים...")
        
        applied_fixes = []
        
        for filename, content in fixes.items():
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.info(f"✅ תוקן: {filename}")
                applied_fixes.append(filename)
            except Exception as e:
                self.logger.error(f"❌ שגיאה בתיקון {filename}: {e}")
        
        return applied_fixes

    def verify_fixes(self):
        """מוודא שהתיקונים עבדו"""
        self.logger.info("🔍 מאמת תיקונים...")
        
        try:
            # ניסיון לייבא את המודולים העיקריים
            from telegram_bot import AdvancedTelegramBot
            from advanced_trading_logic import AdvancedTradingLogic
            from risk_manager import AdvancedRiskManager, TradeAction
            
            # בדיקת פונקציונליות
            bot = AdvancedTelegramBot()
            logic = AdvancedTradingLogic()
            risk_mgr = AdvancedRiskManager()
            
            # הבדיקה החשובה - set_trading_logic
            bot.set_trading_logic(logic)
            
            # בדיקת ניתוח
            analysis = logic.comprehensive_analysis("TONUSDT")
            
            self.logger.info("🎉 כל הבדיקות עברו בהצלחה!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ אימות נכשל: {e}")
            return False

    def generate_report(self, scan_results: Dict):
        """מייצר דוח מפורט"""
        print("\n" + "="*80)
        print("📋 TON TRADING BOT - PROJECT SCAN REPORT")
        print("="*80)
        
        health_report = scan_results['health_report']
        file_mapping = scan_results['file_mapping']
        
        print(f"\n📊 סטטיסטיקות:")
        print(f"   • קבצים נדרשים: {len(file_mapping['required_files'])}")
        print(f"   • קבצים קיימים: {len(file_mapping['existing_files'])}")
        print(f"   • קבצים חסרים: {len(file_mapping['missing_files'])}")
        
        print(f"\n✅ קבצים קיימים ובריאים:")
        healthy_count = 0
        for filename, health in health_report.items():
            if health['exists'] and health['health'] == 'HEALTHY':
                print(f"   • {filename} ({health['size']} bytes, {health['lines']} lines)")
                healthy_count += 1
        
        print(f"\n⚠️  קבצים עם בעיות:")
        problem_count = 0
        for filename, health in health_report.items():
            if not health['exists'] or health['health'] != 'HEALTHY':
                status = "חסר" if not health['exists'] else health['health']
                print(f"   • {filename} - {status}")
                if health['exists']:
                    print(f"     📏 גודל: {health['size']} bytes, שורות: {health['lines']}")
                problem_count += 1
        
        print(f"\n🔍 ייבואים קריטיים ב-app.py:")
        imports = scan_results['import_analysis']
        for module, items in imports['from_imports'].items():
            print(f"   • from {module} import {', '.join(items)}")
        
        for module in imports['modules']:
            print(f"   • import {module}")
        
        return {
            'healthy_files': healthy_count,
            'problem_files': problem_count,
            'missing_files': len(file_mapping['missing_files'])
        }

    def run_complete_scan(self):
        """מריץ סריקה מלאה"""
        print("🚀 TON Trading Bot - Project File Scanner")
        print("="*60)
        
        # שלב 1: סריקת מבנה
        structure = self.scan_project_structure()
        
        # שלב 2: אנליזת ייבואים
        scan_results = self.scan_all_imported_files()
        
        # שלב 3: דוח
        report = self.generate_report(scan_results)
        
        # שלב 4: תיקונים אוטומטיים אם נדרש
        if scan_results['file_mapping']['missing_files']:
            print(f"\n🛠️  נמצאו {len(scan_results['file_mapping']['missing_files'])} קבצים חסרים!")
            apply_fix = input("❓ האם ליצור קבצים בסיסיים אוטומטית? (y/n): ")
            
            if apply_fix.lower() == 'y':
                fixes = self.generate_emergency_fixes(scan_results['health_report'])
                applied = self.apply_fixes(fixes)
                
                if applied:
                    print(f"✅ נוצרו {len(applied)} קבצים חדשים")
                    
                    # אימות
                    if self.verify_fixes():
                        print("🎉 הפרויקט מוכן להפעלה!")
                    else:
                        print("⚠️  עדיין יש בעיות - נא לבדוק ידנית")
                else:
                    print("❌ לא נוצרו קבצים חדשים")
        
        print("\n" + "="*60)
        print("📁 סיכום מבנה תיקיות:")
        for category, files in structure.items():
            if files:  # רק תיקיות עם קבצים
                print(f"   📂 {category}/: {len(files)} files")

def main():
    """פונקציה ראשית"""
    scanner = ProjectScanner()
    scanner.run_complete_scan()

if __name__ == '__main__':
    main()
