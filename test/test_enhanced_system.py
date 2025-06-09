"""
Enhanced System Test Script
Modüler enhanced sistem testi
"""

import sys
import os
from pathlib import Path

# Proje kök dizinini path'e ekle
current_dir = Path(__file__).parent
project_root = current_dir.parent  # ImageDatesetAnalayze klasörü
sys.path.insert(0, str(project_root))

# Test fonksiyonları
def test_import_modules():
    """Modül import testleri"""
    print("🧪 Modül import testleri...")
    
    try:
        # Enhanced analyzer modüllerini test et
        from src.enhanced_analyzer import EnhancedDatasetAnalyzer
        from src.enhanced_analyzer.config_manager import ConfigManager
        from src.enhanced_analyzer.report_manager import ReportManager
        from src.enhanced_analyzer.analysis_pipeline import PipelineBuilder
        
        print("✅ Enhanced analyzer modülleri başarıyla import edildi")
        
        # Quality assessor modüllerini test et
        from src.quality_assessor import DatasetQualityAssessor
        print("✅ Quality assessor modülleri başarıyla import edildi")
        
        # Temel modülleri test et
        from src.data_loader import DatasetLoader
        from src.image_analyzer import ImageAnalyzer
        print("✅ Temel modüller başarıyla import edildi")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import hatası: {str(e)}")
        return False

def test_config_manager():
    """Config Manager testi"""
    print("\n🧪 Config Manager testi...")
    
    try:
        from src.enhanced_analyzer.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        
        # Varsayılan config yükle
        config = config_manager.load_config()
        print("✅ Varsayılan config yüklendi")
        
        # Config değerlerini test et
        assert 'logging' in config
        assert 'analysis' in config
        assert 'reporting' in config  # 'output' yerine 'reporting'
        print("✅ Config yapısı doğru")
        
        return True
        
    except Exception as e:
        print(f"❌ Config Manager testi hatası: {str(e)}")
        return False

def test_enhanced_analyzer():
    """Enhanced Analyzer testi"""
    print("\n🧪 Enhanced Analyzer testi...")
    
    # Veri seti yolu
    dataset_path = project_root / 'data' / 'input' / 'yolov11_dataset_vol1'
    
    if not dataset_path.exists():
        print(f"⚠️  Test veri seti bulunamadı: {dataset_path}")
        return False
    
    try:
        from src.enhanced_analyzer import EnhancedDatasetAnalyzer
        
        # Test konfigürasyonu
        test_config = {
            'output': {
                'reports_dir': 'data/output/test',
                'save_detailed_report': True,
                'save_summary_report': True
            },
            'logging': {
                'level': 'INFO'
            }
        }
        
        # Enhanced Analyzer'ı başlat
        analyzer = EnhancedDatasetAnalyzer(
            dataset_path=str(dataset_path),
            annotation_format='yolo',
            config=test_config
        )
        print("✅ EnhancedDatasetAnalyzer başarıyla başlatıldı")
        
        # Hızlı değerlendirme testi
        print("\n🏃 Hızlı değerlendirme testi...")
        quick_result = analyzer.run_quick_assessment()
        
        if quick_result['success']:
            print(f"✅ Hızlı değerlendirme başarılı: {quick_result.get('quick_score', 0):.1f}/100")
        else:
            print(f"❌ Hızlı değerlendirme başarısız: {quick_result.get('error', '')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Analyzer testi hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_pipeline_system():
    """Pipeline sistem testi"""
    print("\n🧪 Pipeline sistem testi...")
    
    try:
        from src.enhanced_analyzer.analysis_pipeline import AnalysisPipeline, PipelineBuilder
        
        # Basit pipeline oluştur
        config = {'processing': {'timeout_seconds': 60}}
        pipeline = AnalysisPipeline(config)
        
        # Test adımları ekle
        def test_step1(**kwargs):
            return {'result': 'step1_completed'}
        
        def test_step2(**kwargs):
            pipeline_results = kwargs.get('pipeline_results', {})
            step1_result = pipeline_results.get('step1', {})
            return {'result': 'step2_completed', 'previous': step1_result}
        
        pipeline.add_step('step1', test_step1, 'Test adım 1')
        pipeline.add_step('step2', test_step2, 'Test adım 2', dependencies=['step1'])
        
        # Pipeline'ı çalıştır
        result = pipeline.run_pipeline()
        
        if result['success']:
            print("✅ Pipeline başarıyla tamamlandı")
            print(f"   Tamamlanan adımlar: {len(result['completed_steps'])}")
            print(f"   Başarısız adımlar: {len(result['failed_steps'])}")
        else:
            print("❌ Pipeline başarısız")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline testi hatası: {str(e)}")
        return False

def run_integration_test():
    """Entegrasyon testi"""
    print("\n🔗 ENTEGRASYON TESTİ...")
    
    dataset_path = project_root / 'data' / 'input' / 'yolov11_dataset_vol1'
    
    if not dataset_path.exists():
        print(f"⚠️  Test veri seti bulunamadı: {dataset_path}")
        return False
    
    try:
        from src.enhanced_analyzer import EnhancedDatasetAnalyzer
        
        # Enhanced analyzer ile mini analiz
        test_config = {
            'output': {
                'reports_dir': 'data/output/integration_test'
            },
            'logging': {
                'level': 'WARNING'  # Daha az log
            }
        }
        
        print("🚀 Enhanced Analyzer başlatılıyor...")
        analyzer = EnhancedDatasetAnalyzer(
            dataset_path=str(dataset_path),
            annotation_format='yolo',
            config=test_config
        )
        
        print("🏃 Hızlı kalite değerlendirmesi...")
        result = analyzer.run_quick_assessment()
        
        if result['success']:
            print(f"✅ Entegrasyon testi başarılı!")
            print(f"   Hızlı Skor: {result.get('quick_score', 0):.1f}/100")
            print(f"   Not: {result.get('grade', 'F')}")
            print(f"   Durum: {result.get('status', 'Bilinmiyor')}")
            return True
        else:
            print(f"❌ Entegrasyon testi başarısız: {result.get('error', '')}")
            return False
        
    except Exception as e:
        print(f"❌ Entegrasyon testi hatası: {str(e)}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🚀 ENHANCED SYSTEM TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_import_modules),
        ("Config Manager Test", test_config_manager),
        ("Pipeline System Test", test_pipeline_system),
        ("Enhanced Analyzer Test", test_enhanced_analyzer),
        ("Integration Test", run_integration_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name} BAŞARILI")
            else:
                print(f"❌ {test_name} BAŞARISIZ")
                
        except Exception as e:
            print(f"❌ {test_name} KRİTİK HATA: {str(e)}")
            results.append((test_name, False))
    
    # Sonuçları özetle
    print("\n" + "=" * 60)
    print("📈 TEST SONUÇLARI")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ BAŞARILI" if success else "❌ BAŞARISIZ"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Toplam: {passed}/{total} test başarılı")
    
    if passed == total:
        print("🎉 TÜM TESTLER BAŞARILI! Enhanced sistem kullanıma hazır.")
        return True
    else:
        print(f"⚠️  {total - passed} test başarısız. Lütfen hatalara bakın.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
