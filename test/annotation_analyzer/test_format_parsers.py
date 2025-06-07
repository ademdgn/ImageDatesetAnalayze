#!/usr/bin/env python3
"""
Test Format Parsers - Format Parser Testleri

Bu modül annotation format parser'larını test eder.
"""

import sys
from pathlib import Path

# Ana dizini path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..utils import (
    create_test_annotation_dataset,
    print_test_header,
    print_test_result,
    cleanup_temp_directory
)

def test_format_parsers():
    """Format parser'ları test et"""
    print_test_header("FORMAT PARSER TESTLERİ")
    
    try:
        from src.annotation_analyzer.format_parsers import YOLOParser, COCOParser, PascalVOCParser
        
        # Test dataset oluştur
        temp_dir, annotation_paths, class_names = create_test_annotation_dataset(5)
        
        tests_passed = 0
        tests_total = 0
        
        # YOLO Parser test
        print("🔤 YOLO Parser testi...")
        tests_total += 1
        try:
            yolo_parser = YOLOParser(class_names)
            yolo_files = [p for p in annotation_paths if p.endswith('.txt')]
            
            if yolo_files:
                test_file = yolo_files[0]
                result = yolo_parser.parse_annotation_file(test_file)
                
                if result.get('parsing_failed', False):
                    print_test_result("YOLO Parser", False, result.get('error'))
                else:
                    print(f"  ✓ Format: {result.get('format')}")
                    print(f"  ✓ Annotation sayısı: {result.get('total_objects')}")
                    print(f"  ✓ Sınıf dağılımı: {result.get('class_distribution')}")
                    print_test_result("YOLO Parser", True)
                    tests_passed += 1
            else:
                print_test_result("YOLO Parser", False, "YOLO dosyası bulunamadı")
        except Exception as e:
            print_test_result("YOLO Parser", False, str(e))
        
        # COCO Parser test
        print("\n🗂️ COCO Parser testi...")
        tests_total += 1
        try:
            coco_parser = COCOParser()
            coco_files = [p for p in annotation_paths if p.endswith('.json')]
            
            if coco_files:
                test_file = coco_files[0]
                result = coco_parser.parse_annotation_file(test_file)
                
                if result.get('parsing_failed', False):
                    print_test_result("COCO Parser", False, result.get('error'))
                else:
                    print(f"  ✓ Format: {result.get('format')}")
                    print(f"  ✓ Annotation sayısı: {result.get('total_objects')}")
                    print(f"  ✓ Görüntü sayısı: {result.get('total_images')}")
                    print(f"  ✓ Kategori sayısı: {result.get('total_categories')}")
                    print_test_result("COCO Parser", True)
                    tests_passed += 1
            else:
                print_test_result("COCO Parser", False, "COCO dosyası bulunamadı")
        except Exception as e:
            print_test_result("COCO Parser", False, str(e))
        
        # Pascal VOC Parser test
        print("\n📋 Pascal VOC Parser testi...")
        tests_total += 1
        try:
            voc_parser = PascalVOCParser()
            voc_files = [p for p in annotation_paths if p.endswith('.xml')]
            
            if voc_files:
                test_file = voc_files[0]
                result = voc_parser.parse_annotation_file(test_file)
                
                if result.get('parsing_failed', False):
                    print_test_result("Pascal VOC Parser", False, result.get('error'))
                else:
                    print(f"  ✓ Format: {result.get('format')}")
                    print(f"  ✓ Annotation sayısı: {result.get('total_objects')}")
                    print(f"  ✓ Dosya adı: {result.get('filename')}")
                    print_test_result("Pascal VOC Parser", True)
                    tests_passed += 1
            else:
                print_test_result("Pascal VOC Parser", False, "VOC dosyası bulunamadı")
        except Exception as e:
            print_test_result("Pascal VOC Parser", False, str(e))
        
        # Temizlik
        cleanup_temp_directory(temp_dir)
        
        print(f"\n📊 Format Parser Test Sonuçları: {tests_passed}/{tests_total} başarılı")
        return tests_passed == tests_total
        
    except ImportError as e:
        print_test_result("Format Parser Import", False, str(e))
        return False
    except Exception as e:
        print_test_result("Format Parser Test", False, str(e))
        return False

if __name__ == "__main__":
    success = test_format_parsers()
    sys.exit(0 if success else 1)
