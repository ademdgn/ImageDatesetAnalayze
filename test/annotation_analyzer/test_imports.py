#!/usr/bin/env python3
"""
Test Import - Annotation Analyzer Import Testleri

Bu modül annotation analyzer modüllerinin import edilebilirliğini test eder.
"""

import sys
from pathlib import Path

# Ana dizini path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..utils import print_test_header, print_test_result

def test_imports():
    """Modül import'larını test et"""
    print_test_header("ANNOTATION ANALYZER IMPORT TESTLERİ")
    
    import_tests = [
        ("AnnotationAnalyzer", "src.annotation_analyzer", "AnnotationAnalyzer"),
        ("FormatParserFactory", "src.annotation_analyzer", "FormatParserFactory"),
        ("ClassDistributionAnalyzer", "src.annotation_analyzer", "ClassDistributionAnalyzer"),
        ("BoundingBoxAnalyzer", "src.annotation_analyzer", "BoundingBoxAnalyzer"),
        ("AnnotationQualityChecker", "src.annotation_analyzer", "AnnotationQualityChecker"),
        ("get_supported_formats", "src.annotation_analyzer", "get_supported_formats"),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, module_name, class_name in import_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print_test_result(f"{test_name} import", True)
            passed += 1
        except ImportError as e:
            print_test_result(f"{test_name} import", False, f"Import hatası: {e}")
            failed += 1
        except AttributeError as e:
            print_test_result(f"{test_name} import", False, f"Attribute hatası: {e}")
            failed += 1
    
    # Desteklenen formatları test et
    try:
        from src.annotation_analyzer import get_supported_formats
        formats = get_supported_formats()
        print(f"✅ Desteklenen formatlar: {formats}")
        passed += 1
    except Exception as e:
        print_test_result("get_supported_formats", False, str(e))
        failed += 1
    
    print(f"\n📊 Import Test Sonuçları: {passed} başarılı, {failed} başarısız")
    return failed == 0

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
