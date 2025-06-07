#!/usr/bin/env python3
"""
Data Loader Test Scripti

Bu script data_loader modüllerini test eder.
"""

import sys
import os
from pathlib import Path
import logging

# Ana dizini path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.data_loader import DatasetLoader, load_dataset, quick_validate
    print("✅ Modül import'ları başarılı!")
except ImportError as e:
    print(f"❌ Import hatası: {e}")
    print("\n🔧 Import hatası çözümü:")
    print("1. src/__init__.py dosyasını kontrol edin")
    print("2. Python path'inin doğru olduğundan emin olun")
    print("3. Tüm gerekli modüllerin var olduğunu kontrol edin")
    sys.exit(1)

def test_basic_functionality():
    """Temel fonksiyonaliteyi test et"""
    print("\n🔧 Temel Fonksiyonalite Testi...")
    
    # DatasetLoader sınıfını test et
    try:
        # Sahte bir dizin ile test (hata vermeli)
        fake_path = "C:\\Users\\ademd\\OneDrive\\Desktop\\DeepLearningProject\\ImageDatesetAnalayze\\data\\input\\yolov11_dataset_vol1"
        try:
            loader = DatasetLoader(fake_path)
            print("❌ Sahte dizin testi başarısız - hata vermedi!")
        except FileNotFoundError:
            print("✅ Sahte dizin testi başarılı - beklenen hata alındı")
        
        # Desteklenen formatları kontrol et
        supported = DatasetLoader.SUPPORTED_FORMATS
        print(f"✅ Desteklenen formatlar: {list(supported.keys())}")
        
        print("✅ Temel fonksiyonalite testleri tamamlandı!")
        
    except Exception as e:
        print(f"❌ Temel test hatası: {e}")
        return False
    
    return True

def test_with_dataset(dataset_path: str):
    """Gerçek veri seti ile test"""
    print(f"\n📊 Veri Seti Testi: {dataset_path}")
    
    try:
        # 1. Dataset path kontrolü
        path = Path(dataset_path)
        if not path.exists():
            print(f"❌ Veri seti bulunamadı: {dataset_path}")
            return False
        
        print(f"✅ Veri seti dizini bulundu: {path}")
        
        # 2. DatasetLoader oluştur
        print("🔄 DatasetLoader oluşturuluyor...")
        loader = DatasetLoader(dataset_path, annotation_format='auto')
        print(f"✅ Loader oluşturuldu - Tespit edilen format: {loader.annotation_format}")
        
        # 3. Veri setini yükle
        print("🔄 Veri seti yükleniyor...")
        images, annotations = loader.load_dataset()
        print(f"✅ Veri seti yüklendi:")
        print(f"   📸 Görüntü sayısı: {len(images)}")
        print(f"   🏷️  Annotation sayısı: {len(annotations)}")
        print(f"   🎯 Sınıf sayısı: {len(loader.classes_info)}")
        
        # 4. Temel istatistikler
        print("🔄 İstatistikler hesaplanıyor...")
        stats = loader.get_basic_statistics()
        print(f"✅ İstatistikler:")
        print(f"   📊 Ortalama annotation/görüntü: {stats.get('annotation_stats', {}).get('avg_annotations_per_image', 0):.2f}")
        
        # 5. Sınıf dağılımı
        if loader.classes_info:
            print(f"✅ Sınıflar: {list(loader.classes_info.values())[:5]}{'...' if len(loader.classes_info) > 5 else ''}")
        
        # 6. Doğrulama testi
        print("🔄 Veri seti doğrulaması yapılıyor...")
        validation = loader.validate_dataset()
        print(f"✅ Doğrulama tamamlandı:")
        print(f"   🎯 Kalite skoru: {validation['overall_score']:.1f}/100")
        print(f"   ✅ Geçerli: {validation['is_valid']}")
        
        if validation['errors']:
            print(f"   ❌ Hatalar ({len(validation['errors'])}): {validation['errors'][:2]}")
        
        if validation['warnings']:
            print(f"   ⚠️  Uyarılar ({len(validation['warnings'])}): {validation['warnings'][:2]}")
        
        print("🎉 Veri seti testi başarıyla tamamlandı!")
        return True
        
    except Exception as e:
        print(f"❌ Veri seti test hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_convenience_functions():
    """Convenience fonksiyonları test et"""
    print("\n🚀 Convenience Function Testleri...")
    
    # Test için örnek dizin yolu (kullanıcı verecek)
    test_path = input("Test için veri seti yolu girin (Enter = atla): ").strip()
    
    if not test_path:
        print("⏭️  Convenience function testleri atlandı")
        return True
    
    try:
        # quick_validate test
        print("🔄 quick_validate() testi...")
        results = quick_validate(test_path)
        print(f"✅ Quick validate: {results['overall_score']:.1f}/100")
        
        # load_dataset test
        print("🔄 load_dataset() testi...")
        loader = load_dataset(test_path)
        print(f"✅ Load dataset: {len(loader)} görüntü")
        
        print("✅ Convenience function testleri tamamlandı!")
        return True
        
    except Exception as e:
        print(f"❌ Convenience function test hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🧪 DATA LOADER TEST SÜİTİ")
    print("=" * 50)
    
    # Logging seviyesini ayarla
    logging.basicConfig(level=logging.INFO)
    
    # Test sırası
    tests = [
        ("Temel Fonksiyonalite", test_basic_functionality),
        ("Convenience Functions", test_convenience_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 {test_name} Testi Başlıyor...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} - BAŞARILI")
        else:
            print(f"❌ {test_name} - BAŞARISIZ")
    
    # Veri seti testi (opsiyonel)
    dataset_path = input(f"\n📂 Test için veri seti yolu girin (Enter = atla): ").strip()
    if dataset_path:
        print(f"\n🔬 Veri Seti Testi Başlıyor...")
        if test_with_dataset(dataset_path):
            passed += 1
            total += 1
            print(f"✅ Veri Seti Testi - BAŞARILI")
        else:
            total += 1
            print(f"❌ Veri Seti Testi - BAŞARISIZ")
    
    # Sonuç
    print(f"\n📊 TEST SONUÇLARI")
    print("=" * 30)
    print(f"✅ Başarılı: {passed}/{total}")
    print(f"❌ Başarısız: {total-passed}/{total}")
    print(f"📈 Başarı Oranı: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 TÜM TESTLER BAŞARILI! 🎉")
    else:
        print(f"\n⚠️  {total-passed} test başarısız oldu")

if __name__ == "__main__":
    main()
