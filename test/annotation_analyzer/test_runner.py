#!/usr/bin/env python3
"""
Test Runner - Ana Test Çalıştırıcı

Bu script tüm annotation analyzer testlerini modüler şekilde çalıştırır.
"""

import sys
from pathlib import Path

# Ana dizini path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .test_imports import test_imports
from .test_format_parsers import test_format_parsers
from .test_class_distribution import test_class_distribution_analyzer

def run_annotation_analyzer_tests():
    """Tüm annotation analyzer testlerini çalıştır"""
    print("🚀 ANNOTATION ANALYZER MODÜLER TEST SÜİTİ")
    print("=" * 80)
    print(f"Test zamanı: {__import__('datetime').datetime.now()}")
    print("=" * 80)
    
    test_functions = [
        ("Import Testleri", test_imports),
        ("Format Parser Testleri", test_format_parsers),
        ("Sınıf Dağılımı Analiz Testleri", test_class_distribution_analyzer),
    ]
    
    passed_tests = 0
    failed_tests = 0
    test_results = []
    
    for test_name, test_func in test_functions:
        try:
            print(f"\n🧪 {test_name} başlatılıyor...")
            result = test_func()
            
            if result:
                print(f"✅ {test_name} - BAŞARILI")
                passed_tests += 1
                test_results.append((test_name, "BAŞARILI", None))
            else:
                print(f"❌ {test_name} - BAŞARISIZ")
                failed_tests += 1
                test_results.append((test_name, "BAŞARISIZ", "Test fonksiyonu False döndü"))
                
        except Exception as e:
            print(f"💥 {test_name} - HATA: {e}")
            failed_tests += 1
            test_results.append((test_name, "HATA", str(e)))
    
    # Özet raporu
    print("\n" + "="*80)
    print("📊 TEST SONUÇLARI ÖZETİ")
    print("="*80)
    
    for test_name, status, error in test_results:
        status_icon = "✅" if status == "BAŞARILI" else "❌" if status == "BAŞARISIZ" else "💥"
        print(f"{status_icon} {test_name}: {status}")
        if error and status != "BAŞARILI":
            print(f"    └─ Hata: {error}")
    
    print(f"\n📈 GENEL BAŞARI ORANI:")
    total_tests = passed_tests + failed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"  • Başarılı testler: {passed_tests}/{total_tests}")
    print(f"  • Başarı oranı: %{success_rate:.1f}")
    
    if success_rate >= 90:
        print("  🎉 Mükemmel! Annotation Analyzer tamamen hazır")
        return True
    elif success_rate >= 75:
        print("  👍 İyi! Küçük düzeltmeler yeterli")
        return True
    elif success_rate >= 50:
        print("  ⚠️ Orta! Önemli sorunlar var, düzeltme gerekli")
        return False
    else:
        print("  🚨 Kritik! Major sorunlar var, kapsamlı düzeltme gerekli")
        return False

if __name__ == "__main__":
    try:
        # Ana test süitini çalıştır
        success = run_annotation_analyzer_tests()
        
        # Exit code ayarla
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Testler kullanıcı tarafından durduruldu")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Beklenmedik hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
