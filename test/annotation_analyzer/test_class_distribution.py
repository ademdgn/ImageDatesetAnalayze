#!/usr/bin/env python3
"""
Test Class Distribution - Sınıf Dağılımı Analiz Testleri

Bu modül sınıf dağılımı analiz modülünü test eder.
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

def test_class_distribution_analyzer():
    """Sınıf dağılımı analiz modülünü test et"""
    print_test_header("SINIF DAĞILIMI ANALİZ TESTLERİ")
    
    try:
        from src.annotation_analyzer.class_distribution import ClassDistributionAnalyzer
        from src.annotation_analyzer import AnnotationAnalyzer
        
        # Test dataset oluştur
        temp_dir, annotation_paths, class_names = create_test_annotation_dataset(8)
        
        # Annotation'ları parse et
        analyzer = AnnotationAnalyzer()
        analyzer.load_class_names()
        
        annotation_data = []
        for ann_path in annotation_paths:
            parsed = analyzer.load_annotations(ann_path)
            if not parsed.get('parsing_failed', False):
                annotation_data.append(parsed)
        
        print(f"📂 {len(annotation_data)} annotation dosyası yüklendi")
        
        # Class distribution analizi
        class_analyzer = ClassDistributionAnalyzer()
        class_analysis = class_analyzer.analyze_class_distribution(annotation_data)
        
        if 'error' in class_analysis:
            print_test_result("Sınıf Dağılımı Analizi", False, class_analysis['error'])
            cleanup_temp_directory(temp_dir)
            return False
        
        # Sonuçları kontrol et
        success = True
        required_fields = ['total_annotations', 'total_classes', 'class_counts', 
                          'imbalance_analysis', 'recommendations']
        
        for field in required_fields:
            if field not in class_analysis:
                print_test_result(f"Sınıf Analizi - {field}", False, "Alan bulunamadı")
                success = False
            else:
                print_test_result(f"Sınıf Analizi - {field}", True)
        
        # Detayları yazdır
        if success:
            print(f"  ✓ Toplam annotation: {class_analysis.get('total_annotations')}")
            print(f"  ✓ Toplam sınıf: {class_analysis.get('total_classes')}")
            print(f"  ✓ Sınıf dağılımı: {class_analysis.get('class_counts')}")
            
            # İmbalance analizi
            imbalance = class_analysis.get('imbalance_analysis', {})
            if imbalance:
                print(f"  ✓ İmbalance şiddeti: {imbalance.get('imbalance_severity')}")
                print(f"  ✓ Majority dominance: {imbalance.get('majority_dominance', 0):.3f}")
            
            # Öneriler
            recommendations = class_analysis.get('recommendations', [])
            print(f"  ✓ Öneriler: {len(recommendations)} adet")
        
        # Temizlik
        cleanup_temp_directory(temp_dir)
        
        print_test_result("Sınıf Dağılımı Analizi", success)
        return success
        
    except ImportError as e:
        print_test_result("Sınıf Dağılımı Import", False, str(e))
        return False
    except Exception as e:
        print_test_result("Sınıf Dağılımı Test", False, str(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_class_distribution_analyzer()
    sys.exit(0 if success else 1)
