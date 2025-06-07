#!/usr/bin/env python3
"""
Run Tests - Ana Test Çalıştırıcı Script

Bu script proje için tüm testleri çalıştırır.
"""

import sys
import argparse
from pathlib import Path

# Ana dizini path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from test.annotation_analyzer import run_annotation_analyzer_tests

def main():
    """Ana test fonksiyonu"""
    parser = argparse.ArgumentParser(description="Proje Test Çalıştırıcı")
    parser.add_argument(
        "--module", 
        choices=["all", "annotation_analyzer", "image_analyzer", "data_loader"],
        default="all",
        help="Hangi modül testlerini çalıştıracak"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Detaylı çıktı"
    )
    
    args = parser.parse_args()
    
    print("🧪 IMAGE DATASET ANALYZER - TEST SÜİTİ")
    print("=" * 60)
    print(f"Test modülü: {args.module}")
    print(f"Detaylı mod: {args.verbose}")
    print("=" * 60)
    
    success = True
    
    if args.module in ["all", "annotation_analyzer"]:
        print("\n📋 Annotation Analyzer testleri çalıştırılıyor...")
        try:
            success &= run_annotation_analyzer_tests()
        except Exception as e:
            print(f"❌ Annotation Analyzer testleri hatası: {e}")
            success = False
    
    if args.module in ["all", "image_analyzer"]:
        print("\n🖼️ Image Analyzer testleri henüz uygulanmadı...")
        # TODO: Image analyzer testlerini buraya ekle
    
    if args.module in ["all", "data_loader"]:
        print("\n📂 Data Loader testleri henüz uygulanmadı...")
        # TODO: Data loader testlerini buraya ekle
    
    # Genel sonuç
    print("\n" + "=" * 60)
    if success:
        print("🎉 TÜM TESTLER BAŞARILI!")
        print("   Proje testleri geçti ve kullanıma hazır.")
    else:
        print("❌ TESTLER BAŞARISIZ!")
        print("   Lütfen hataları düzeltin ve tekrar deneyin.")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
