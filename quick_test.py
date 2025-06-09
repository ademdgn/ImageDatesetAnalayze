#!/usr/bin/env python3
"""
Quick Test Script
Hızlı import ve fonksiyon testleri
"""

import sys
from pathlib import Path

# Proje kök dizinini sys.path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("🚀 Hızlı Test Başlatılıyor...")
    print("=" * 50)
    
    try:
        # 1. Temel import testleri
        print("\n1. Temel modül import testleri:")
        
        from src.data_loader import DatasetLoader
        print("✅ DatasetLoader import edildi")
        
        from src.image_analyzer import ImageAnalyzer
        print("✅ ImageAnalyzer import edildi")
        
        from src.annotation_analyzer import AnnotationAnalyzer
        print("✅ AnnotationAnalyzer import edildi")
        
        from src.quality_assessor import DatasetQualityAssessor
        print("✅ DatasetQualityAssessor import edildi")
        
        # 2. Enhanced analyzer testleri
        print("\n2. Enhanced analyzer import testleri:")
        
        from src.enhanced_analyzer import EnhancedDatasetAnalyzer
        print("✅ EnhancedDatasetAnalyzer import edildi")
        
        from src.enhanced_analyzer.config_manager import ConfigManager
        print("✅ ConfigManager import edildi")
        
        from src.enhanced_analyzer.report_manager import ReportManager
        print("✅ ReportManager import edildi")
        
        # 3. Basit instance oluşturma testi
        print("\n3. Basit instance oluşturma testleri:")
        
        # Test veri seti yolu
        dataset_path = project_root / 'data' / 'input' / 'yolov11_dataset_vol1'
        
        if dataset_path.exists():
            print(f"✅ Test veri seti bulundu: {dataset_path}")
            
            # DatasetLoader testi
            try:
                data_loader = DatasetLoader(str(dataset_path), 'yolo')
                print("✅ DatasetLoader instance oluşturuldu")
                
                # Temel istatistikleri al
                basic_stats = data_loader.get_basic_statistics()
                print(f"✅ Temel istatistikler alındı: {basic_stats}")
                
            except Exception as e:
                print(f"❌ DatasetLoader hatası: {e}")
            
            # EnhancedDatasetAnalyzer testi
            try:
                config = {
                    'logging': {'level': 'WARNING'},
                    'output': {'reports_dir': 'data/output/test'}
                }
                analyzer = EnhancedDatasetAnalyzer(str(dataset_path), 'yolo', config)
                print("✅ EnhancedDatasetAnalyzer instance oluşturuldu")
                
                # Hızlı değerlendirme
                result = analyzer.run_quick_assessment()
                if result['success']:
                    print(f"✅ Hızlı değerlendirme başarılı: {result['quick_score']:.1f}/100")
                else:
                    print(f"❌ Hızlı değerlendirme başarısız: {result.get('error', '')}")
                
            except Exception as e:
                print(f"❌ EnhancedDatasetAnalyzer hatası: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"⚠️  Test veri seti bulunamadı: {dataset_path}")
        
        print("\n🎉 Hızlı testler tamamlandı!")
        return True
        
    except Exception as e:
        print(f"❌ Kritik hata: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
