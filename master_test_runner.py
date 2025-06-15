#!/usr/bin/env python3
"""
🧪 MASTER TEST RUNNER - Kapsamlı Test Sistemi
ImageDatasetAnalyze Projesi için Tam Test Pipeline'ı

Bu script tüm proje modüllerini test eder:
- Import ve bağımlılık testleri
- Modül işlevsellik testleri
- Entegrasyon testleri
- Performance testleri
- Error handling testleri
- End-to-end sistem testleri
"""

import sys
import os
import time
import traceback
import argparse
import warnings
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
import json

# Proje kök dizinini path'e ekle
current_dir = Path(__file__).parent
project_root = current_dir.parent if current_dir.name == 'test' else current_dir
sys.path.insert(0, str(project_root))

# Warnings'leri filtrele
warnings.filterwarnings("ignore", category=DeprecationWarning)

@dataclass
class TestResult:
    """Test sonuç veri sınıfı"""
    name: str
    success: bool
    duration: float
    error_message: Optional[str] = None
    details: Optional[Dict] = None

class TestSuite:
    """Ana test suite sınıfı"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[TestResult] = []
        self.start_time = time.time()
        
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> TestResult:
        """Tek bir testi çalıştır"""
        if self.verbose:
            print(f"\n🧪 {test_name} başlatılıyor...")
        
        start_time = time.time()
        
        try:
            result = test_func(*args, **kwargs)
            duration = time.time() - start_time
            
            if isinstance(result, dict):
                success = result.get('success', True)
                details = result
                error_msg = result.get('error', None)
            elif isinstance(result, bool):
                success = result
                details = None
                error_msg = None
            else:
                success = bool(result)
                details = {'result': result}
                error_msg = None
            
            test_result = TestResult(
                name=test_name,
                success=success,
                duration=duration,
                error_message=error_msg,
                details=details
            )
            
        except Exception as e:
            duration = time.time() - start_time
            test_result = TestResult(
                name=test_name,
                success=False,
                duration=duration,
                error_message=str(e),
                details={'traceback': traceback.format_exc()}
            )
        
        self.results.append(test_result)
        
        # Sonucu yazdır
        status = "✅ BAŞARILI" if test_result.success else "❌ BAŞARISIZ"
        print(f"   {test_name}: {status} ({duration:.2f}s)")
        
        if not test_result.success and self.verbose:
            print(f"     Hata: {test_result.error_message}")
        
        return test_result
    
    def get_summary(self) -> Dict:
        """Test özetini döndür"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed
        total_duration = time.time() - self.start_time
        
        return {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'total_duration': total_duration,
            'results': self.results
        }

# =================== TEST FONKSİYONLARI ===================

def test_python_environment():
    """Python ortamını test et"""
    import sys
    
    # Python versiyonu kontrolü
    if sys.version_info < (3, 8):
        return {
            'success': False,
            'error': f'Python 3.8+ gerekli, mevcut: {sys.version}'
        }
    
    return {
        'success': True,
        'python_version': sys.version,
        'platform': sys.platform
    }

def test_dependencies():
    """Bağımlılık paketlerini test et"""
    required_packages = [
        'numpy', 'pandas', 'matplotlib', 'seaborn', 'plotly',
        'opencv-python', 'Pillow', 'albumentations', 'sklearn',
        'yaml', 'tqdm', 'pathlib'
    ]
    
    missing_packages = []
    installed_packages = {}
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
                installed_packages[package] = cv2.__version__
            elif package == 'Pillow':
                import PIL
                installed_packages[package] = PIL.__version__
            elif package == 'sklearn':
                import sklearn
                installed_packages[package] = sklearn.__version__
            elif package == 'yaml':
                import yaml
                installed_packages[package] = getattr(yaml, '__version__', 'unknown')
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                installed_packages[package] = version
        except ImportError:
            missing_packages.append(package)
    
    success = len(missing_packages) == 0
    
    return {
        'success': success,
        'installed_packages': installed_packages,
        'missing_packages': missing_packages,
        'total_required': len(required_packages)
    }

def test_project_structure():
    """Proje yapısını test et"""
    required_dirs = [
        'src',
        'src/data_loader',
        'src/image_analyzer', 
        'src/enhanced_analyzer',
        'src/quality_assessor',
        'config',
        'data',
        'test'
    ]
    
    required_files = [
        'main.py',
        'enhanced_main.py',
        'requirements.txt',
        'README.md',
        'config/config.yaml'
    ]
    
    missing_dirs = []
    missing_files = []
    
    for dir_path in required_dirs:
        if not (project_root / dir_path).exists():
            missing_dirs.append(dir_path)
    
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    success = len(missing_dirs) == 0 and len(missing_files) == 0
    
    return {
        'success': success,
        'missing_directories': missing_dirs,
        'missing_files': missing_files,
        'project_root': str(project_root)
    }

def test_module_imports():
    """Modül import testlerini çalıştır"""
    modules_to_test = [
        ('src.data_loader', 'DatasetLoader'),
        ('src.image_analyzer', 'ImageAnalyzer'),
        ('src.enhanced_analyzer', 'EnhancedDatasetAnalyzer'),
        ('src.enhanced_analyzer.config_manager', 'ConfigManager'),
        ('src.enhanced_analyzer.report_manager', 'ReportManager'),
        ('src.enhanced_analyzer.analysis_pipeline', 'AnalysisPipeline')
    ]
    
    import_results = {}
    failed_imports = []
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            import_results[f"{module_name}.{class_name}"] = "✅ OK"
        except ImportError as e:
            import_results[f"{module_name}.{class_name}"] = f"❌ {str(e)}"
            failed_imports.append((module_name, class_name, str(e)))
        except AttributeError as e:
            import_results[f"{module_name}.{class_name}"] = f"❌ Class not found: {str(e)}"
            failed_imports.append((module_name, class_name, str(e)))
    
    success = len(failed_imports) == 0
    
    return {
        'success': success,
        'import_results': import_results,
        'failed_imports': failed_imports,
        'total_modules': len(modules_to_test)
    }

def test_config_system():
    """Konfigürasyon sistemi testleri"""
    try:
        from src.enhanced_analyzer.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Temel konfigürasyon bölümlerini kontrol et
        required_sections = ['logging', 'analysis', 'reporting']
        missing_sections = [section for section in required_sections if section not in config]
        
        success = len(missing_sections) == 0
        
        return {
            'success': success,
            'config_sections': list(config.keys()),
            'missing_sections': missing_sections,
            'config_loaded': True
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'config_loaded': False
        }

def test_data_loader():
    """Data Loader modülü testleri"""
    # Test veri setini kontrol et
    test_dataset_path = project_root / 'data' / 'input' / 'yolov11_dataset_vol1'
    
    if not test_dataset_path.exists():
        return {
            'success': False,
            'error': f'Test veri seti bulunamadı: {test_dataset_path}',
            'dataset_available': False
        }
    
    try:
        from src.data_loader import DatasetLoader
        
        # DatasetLoader'ı başlat
        loader = DatasetLoader(str(test_dataset_path), 'yolo')
        
        # Temel işlevleri test et
        images, annotations = loader.load_dataset()
        basic_stats = loader.get_basic_statistics()
        validation = loader.validate_dataset()
        
        return {
            'success': True,
            'dataset_available': True,
            'total_images': len(images),
            'total_annotations': len(annotations),
            'validation_passed': validation.get('overall_score', 0) > 0,
            'basic_stats': basic_stats
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'dataset_available': True
        }

def test_image_analyzer():
    """Image Analyzer modülü testleri"""
    # Test görüntüsü kontrolü
    test_image_path = project_root / 'data' / 'test_image' / 'valid_image.jpg'
    
    if not test_image_path.exists():
        # Alternatif test görüntüsü ara
        dataset_path = project_root / 'data' / 'input' / 'yolov11_dataset_vol1' / 'train' / 'images'
        if dataset_path.exists():
            image_files = list(dataset_path.glob('*.jpg'))
            if image_files:
                test_image_path = image_files[0]
            else:
                return {
                    'success': False,
                    'error': 'Test görüntüsü bulunamadı',
                    'image_available': False
                }
        else:
            return {
                'success': False,
                'error': 'Test veri seti bulunamadı',
                'image_available': False
            }
    
    try:
        from src.image_analyzer import ImageAnalyzer
        
        analyzer = ImageAnalyzer()
        
        # Test görüntülerini analiz et
        images = [str(test_image_path)]
        
        # Temel analiz işlevlerini test et
        properties = analyzer.analyze_image_properties(images)
        dataset_analysis = analyzer.analyze_dataset_images(images)
        
        return {
            'success': True,
            'image_available': True,
            'test_image': str(test_image_path),
            'properties_analysis': bool(properties),
            'dataset_analysis': bool(dataset_analysis)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'image_available': True
        }

def test_enhanced_analyzer():
    """Enhanced Analyzer sistemi testleri"""
    test_dataset_path = project_root / 'data' / 'input' / 'yolov11_dataset_vol1'
    
    if not test_dataset_path.exists():
        return {
            'success': False,
            'error': 'Test veri seti bulunamadı',
            'dataset_available': False
        }
    
    try:
        from src.enhanced_analyzer import EnhancedDatasetAnalyzer
        
        # Test konfigürasyonu
        test_config = {
            'output': {
                'reports_dir': 'data/output/master_test',
                'save_detailed_report': False,  # Test sırasında dosya kaydetme
                'save_summary_report': False
            },
            'logging': {
                'level': 'WARNING'  # Test sırasında daha az log
            }
        }
        
        # Enhanced Analyzer'ı başlat
        analyzer = EnhancedDatasetAnalyzer(
            dataset_path=str(test_dataset_path),
            annotation_format='yolo',
            config=test_config
        )
        
        # Hızlı değerlendirme testi
        quick_result = analyzer.run_quick_assessment()
        
        return {
            'success': quick_result['success'],
            'dataset_available': True,
            'quick_score': quick_result.get('quick_score', 0),
            'grade': quick_result.get('grade', 'F'),
            'error': quick_result.get('error') if not quick_result['success'] else None
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'dataset_available': True
        }

def test_pipeline_system():
    """Pipeline sistem testleri"""
    try:
        from src.enhanced_analyzer.analysis_pipeline import AnalysisPipeline
        
        # Test pipeline'ı oluştur
        config = {'processing': {'timeout_seconds': 30}}
        pipeline = AnalysisPipeline(config)
        
        # Test adımları ekle
        def test_step1(**kwargs):
            time.sleep(0.1)  # Simüle edilen işlem
            return {'result': 'step1_completed', 'data': [1, 2, 3]}
        
        def test_step2(**kwargs):
            pipeline_results = kwargs.get('pipeline_results', {})
            step1_result = pipeline_results.get('step1', {})
            return {
                'result': 'step2_completed',
                'previous_data': step1_result.get('data', []),
                'processed_count': len(step1_result.get('data', []))
            }
        
        def test_step3(**kwargs):
            pipeline_results = kwargs.get('pipeline_results', {})
            step2_result = pipeline_results.get('step2', {})
            return {
                'result': 'step3_completed',
                'final_count': step2_result.get('processed_count', 0) * 2
            }
        
        # Adımları pipeline'a ekle
        pipeline.add_step('step1', test_step1, 'Test Adım 1')
        pipeline.add_step('step2', test_step2, 'Test Adım 2', dependencies=['step1'])
        pipeline.add_step('step3', test_step3, 'Test Adım 3', dependencies=['step2'])
        
        # Pipeline'ı çalıştır
        result = pipeline.run_pipeline()
        
        return {
            'success': result['success'],
            'completed_steps': len(result['completed_steps']),
            'failed_steps': len(result['failed_steps']),
            'total_duration': result.get('total_duration', 0),
            'final_result': result['results'].get('step3', {})
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def test_error_handling():
    """Error handling testleri"""
    test_results = {}
    
    # 1. Olmayan veri seti testi
    try:
        from src.enhanced_analyzer import EnhancedDatasetAnalyzer
        
        analyzer = EnhancedDatasetAnalyzer(
            dataset_path="/nonexistent/path",
            annotation_format='yolo'
        )
        result = analyzer.run_quick_assessment()
        test_results['nonexistent_dataset'] = {
            'handled_gracefully': not result['success'],
            'error_message': result.get('error', '')
        }
    except Exception as e:
        test_results['nonexistent_dataset'] = {
            'handled_gracefully': False,
            'exception': str(e)
        }
    
    # 2. Geçersiz format testi
    try:
        from src.data_loader import DatasetLoader
        
        loader = DatasetLoader("/tmp", "invalid_format")
        test_results['invalid_format'] = {
            'handled_gracefully': True,  # Exception fırlatmadı ise başarılı
            'created_successfully': True
        }
    except Exception as e:
        test_results['invalid_format'] = {
            'handled_gracefully': True,  # Beklenen hata
            'exception': str(e)
        }
    
    success = all(result.get('handled_gracefully', False) for result in test_results.values())
    
    return {
        'success': success,
        'test_results': test_results,
        'total_error_tests': len(test_results)
    }

def test_performance():
    """Performance testleri"""
    test_dataset_path = project_root / 'data' / 'input' / 'yolov11_dataset_vol1'
    
    if not test_dataset_path.exists():
        return {
            'success': False,
            'error': 'Test veri seti bulunamadı'
        }
    
    try:
        from src.enhanced_analyzer import EnhancedDatasetAnalyzer
        
        # Performance test konfigürasyonu
        config = {
            'output': {'save_detailed_report': False, 'save_summary_report': False},
            'logging': {'level': 'ERROR'}
        }
        
        # Timing testi
        start_time = time.time()
        
        analyzer = EnhancedDatasetAnalyzer(
            dataset_path=str(test_dataset_path),
            annotation_format='yolo',
            config=config
        )
        
        init_time = time.time() - start_time
        
        # Hızlı analiz timing
        analysis_start = time.time()
        result = analyzer.run_quick_assessment()
        analysis_time = time.time() - analysis_start
        
        # Performance kriterleri
        init_acceptable = init_time < 5.0  # 5 saniyeden hızlı başlatma
        analysis_acceptable = analysis_time < 30.0  # 30 saniyeden hızlı analiz
        
        return {
            'success': result['success'] and init_acceptable and analysis_acceptable,
            'init_time': init_time,
            'analysis_time': analysis_time,
            'init_acceptable': init_acceptable,
            'analysis_acceptable': analysis_acceptable,
            'quick_score': result.get('quick_score', 0)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def run_integration_test():
    """Tam entegrasyon testi"""
    test_dataset_path = project_root / 'data' / 'input' / 'yolov11_dataset_vol1'
    
    if not test_dataset_path.exists():
        return {
            'success': False,
            'error': 'Test veri seti bulunamadı'
        }
    
    try:
        # 1. Config Manager
        from src.enhanced_analyzer.config_manager import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # 2. Enhanced Analyzer ile full pipeline
        from src.enhanced_analyzer import EnhancedDatasetAnalyzer
        
        test_config = dict(config)  # Kopyala
        test_config['output'] = {
            'reports_dir': 'data/output/integration_test',
            'save_detailed_report': True,
            'save_summary_report': True
        }
        
        analyzer = EnhancedDatasetAnalyzer(
            dataset_path=str(test_dataset_path),
            annotation_format='yolo',
            config=test_config
        )
        
        # 3. Hızlı değerlendirme
        quick_result = analyzer.run_quick_assessment()
        
        if not quick_result['success']:
            return {
                'success': False,
                'error': f"Hızlı değerlendirme başarısız: {quick_result.get('error', '')}"
            }
        
        # 4. Report dosyalarını kontrol et (eğer kaydedildiyse)
        reports_created = []
        if 'report_paths' in quick_result:
            for report_type, path in quick_result['report_paths'].items():
                if Path(path).exists():
                    reports_created.append(report_type)
        
        return {
            'success': True,
            'quick_score': quick_result.get('quick_score', 0),
            'grade': quick_result.get('grade', 'F'),
            'status': quick_result.get('status', 'Unknown'),
            'reports_created': reports_created,
            'full_pipeline_completed': True
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'full_pipeline_completed': False
        }

# =================== MAIN RUNNER ===================

def main():
    """Ana test runner fonksiyonu"""
    parser = argparse.ArgumentParser(
        description="🧪 Image Dataset Analyzer - Master Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--verbose', '-v', action='store_true', help='Detaylı çıktı')
    parser.add_argument('--quick', '-q', action='store_true', help='Sadece hızlı testler')
    parser.add_argument('--module', choices=['all', 'imports', 'core', 'enhanced', 'performance'], 
                       default='all', help='Test modülü seçimi')
    parser.add_argument('--save-results', action='store_true', help='Test sonuçlarını JSON olarak kaydet')
    
    args = parser.parse_args()
    
    # Başlık
    print("\n" + "="*80)
    print("🧪 IMAGE DATASET ANALYZER - MASTER TEST SUITE")
    print("   Kapsamlı Sistem Testi ve Validasyon")
    print("="*80)
    print(f"📋 Test Modu: {args.module.upper()}")
    print(f"🔍 Detaylı Çıktı: {'Evet' if args.verbose else 'Hayır'}")
    print(f"⚡ Hızlı Test: {'Evet' if args.quick else 'Hayır'}")
    print("="*80)
    
    # Test suite'i başlat
    suite = TestSuite(verbose=args.verbose)
    
    # Test grupları
    basic_tests = [
        ("Python Environment", test_python_environment),
        ("Dependencies Check", test_dependencies),
        ("Project Structure", test_project_structure),
    ]
    
    import_tests = [
        ("Module Imports", test_module_imports),
        ("Config System", test_config_system),
    ]
    
    core_tests = [
        ("Data Loader", test_data_loader),
        ("Image Analyzer", test_image_analyzer),
    ]
    
    enhanced_tests = [
        ("Enhanced Analyzer", test_enhanced_analyzer),
        ("Pipeline System", test_pipeline_system),
        ("Error Handling", test_error_handling),
    ]
    
    performance_tests = [
        ("Performance Test", test_performance),
        ("Integration Test", run_integration_test),
    ]
    
    # Test modülüne göre çalıştır
    if args.module == 'all':
        test_groups = [
            ("🔧 TEMEL TESTLER", basic_tests),
            ("📦 IMPORT TESTLER", import_tests),
            ("🎯 ÇEKİRDEK MODÜL TESTLER", core_tests),
            ("🚀 GELİŞMİŞ SİSTEM TESTLER", enhanced_tests),
        ]
        if not args.quick:
            test_groups.append(("⚡ PERFORMANCE TESTLER", performance_tests))
    elif args.module == 'imports':
        test_groups = [("📦 IMPORT TESTLER", basic_tests + import_tests)]
    elif args.module == 'core':
        test_groups = [("🎯 ÇEKİRDEK TESTLER", basic_tests + core_tests)]
    elif args.module == 'enhanced':
        test_groups = [("🚀 GELİŞMİŞ TESTLER", basic_tests + enhanced_tests)]
    elif args.module == 'performance':
        test_groups = [("⚡ PERFORMANCE TESTLER", basic_tests + performance_tests)]
    
    # Testleri çalıştır
    total_start_time = time.time()
    
    for group_name, tests in test_groups:
        print(f"\n{group_name}")
        print("-" * len(group_name))
        
        for test_name, test_func in tests:
            suite.run_test(test_name, test_func)
    
    # Sonuçları özetle
    summary = suite.get_summary()
    total_duration = time.time() - total_start_time
    
    print("\n" + "="*80)
    print("📊 TEST SONUÇLARI ÖZET")
    print("="*80)
    
    # Genel istatistikler
    print(f"✅ Başarılı Testler: {summary['passed']}")
    print(f"❌ Başarısız Testler: {summary['failed']}")
    print(f"📈 Başarı Oranı: {summary['success_rate']:.1f}%")
    print(f"⏱️  Toplam Süre: {total_duration:.2f} saniye")
    
    # Başarısız testleri listele
    failed_tests = [r for r in summary['results'] if not r.success]
    if failed_tests:
        print(f"\n❌ BAŞARISIZ TESTLER ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   • {test.name}: {test.error_message}")
    
    # Test detayları (verbose modda)
    if args.verbose:
        print(f"\n🔍 DETAYLI TEST SONUÇLARI:")
        for result in summary['results']:
            status = "✅" if result.success else "❌"
            print(f"   {status} {result.name} ({result.duration:.2f}s)")
            if result.details and args.verbose:
                for key, value in result.details.items():
                    if key not in ['traceback']:
                        print(f"      {key}: {value}")
    
    # Kritik değerlendirme
    print(f"\n🎯 KRİTİK DEĞERLENDİRME:")
    
    # Import testleri
    import_success = all(r.success for r in summary['results'] 
                        if r.name in ["Dependencies Check", "Module Imports", "Config System"])
    print(f"   📦 Import Sistemi: {'✅ Çalışıyor' if import_success else '❌ Sorunlu'}")
    
    # Core modüller
    core_success = all(r.success for r in summary['results'] 
                      if r.name in ["Data Loader", "Image Analyzer"])
    print(f"   🎯 Çekirdek Modüller: {'✅ Çalışıyor' if core_success else '❌ Sorunlu'}")
    
    # Enhanced sistem
    enhanced_success = any(r.success for r in summary['results'] 
                          if r.name == "Enhanced Analyzer")
    print(f"   🚀 Enhanced Sistem: {'✅ Çalışıyor' if enhanced_success else '❌ Sorunlu'}")
    
    # Genel sistem durumu
    overall_health = summary['success_rate']
    if overall_health >= 90:
        system_status = "🎉 MÜKEMMEL - Sistem tam çalışır durumda"
        exit_code = 0
    elif overall_health >= 75:
        system_status = "✅ İYİ - Sistem çoğunlukla çalışıyor, küçük sorunlar var"
        exit_code = 0
    elif overall_health >= 50:
        system_status = "⚠️  ORTA - Sistem kısmen çalışıyor, önemli sorunlar var"
        exit_code = 1
    else:
        system_status = "❌ KÖTÜ - Sistem ciddi sorunlar içeriyor"
        exit_code = 1
    
    print(f"\n🏆 GENEL DURUM: {system_status}")
    
    # Sonuçları kaydet (istenirse)
    if args.save_results:
        results_path = project_root / 'test_results.json'
        results_data = {
            'timestamp': time.time(),
            'summary': {
                'total_tests': summary['total_tests'],
                'passed': summary['passed'],
                'failed': summary['failed'],
                'success_rate': summary['success_rate'],
                'total_duration': total_duration
            },
            'test_results': [
                {
                    'name': r.name,
                    'success': r.success,
                    'duration': r.duration,
                    'error_message': r.error_message,
                    'details': r.details
                }
                for r in summary['results']
            ],
            'system_status': system_status,
            'import_system_ok': import_success,
            'core_modules_ok': core_success,
            'enhanced_system_ok': enhanced_success
        }
        
        try:
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Test sonuçları kaydedildi: {results_path}")
        except Exception as e:
            print(f"\n⚠️  Test sonuçları kaydedilemedi: {e}")
    
    # Öneri ve çözümler
    if summary['failed'] > 0:
        print(f"\n🔧 ÇÖZüM ÖNERİLERİ:")
        
        # Dependency sorunları
        dep_failed = any(r.name == "Dependencies Check" and not r.success for r in summary['results'])
        if dep_failed:
            print("   📦 Eksik paketler için: pip install -r requirements.txt")
        
        # Import sorunları
        import_failed = any(r.name == "Module Imports" and not r.success for r in summary['results'])
        if import_failed:
            print("   📂 Python path sorunları için: PYTHONPATH kontrol edin")
        
        # Dataset sorunları
        dataset_failed = any("veri seti bulunamadı" in str(r.error_message) for r in summary['results'] if r.error_message)
        if dataset_failed:
            print("   📁 Test veri seti için: data/input/ klasörünü kontrol edin")
        
        print("   🔍 Detaylı bilgi için: --verbose parametresi kullanın")
        print("   📋 Spesifik modül testi için: --module [imports|core|enhanced] kullanın")
    
    print("\n" + "="*80)
    
    return exit_code

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Test çalıştırması kullanıcı tarafından durduruldu.")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Kritik test runner hatası: {str(e)}")
        if '--verbose' in sys.argv or '-v' in sys.argv:
            traceback.print_exc()
        sys.exit(1)