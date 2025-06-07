"""
Quality Assessor Test Script
Quality Assessor modülünün test edilmesi
"""

import sys
import os
from pathlib import Path

# Src klasörünü path'e ekle
current_dir = Path(__file__).parent
src_dir = current_dir.parent / 'src'
sys.path.insert(0, str(src_dir))

# Gerekli importlar
import logging
from src.quality_assessor import DatasetQualityAssessor

# Logger konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_quality_assessor():
    """Quality Assessor modülünü test et"""
    print("🔍 Quality Assessor Modülü Test Ediliyor...")
    print("=" * 60)
    
    print(current_dir.parent)
    # Veri seti yolu
    dataset_path = current_dir.parent / 'data' / 'input' / 'yolov11_dataset_vol1'
    
    if not dataset_path.exists():
        print(f"❌ Veri seti bulunamadı: {dataset_path}")
        return False
    
    try:
        # Quality Assessor'ı başlat
        print(f"📂 Veri seti yolu: {dataset_path}")
        assessor = DatasetQualityAssessor(str(dataset_path))
        print("✅ DatasetQualityAssessor başarıyla oluşturuldu")
        
        # Basit analiz verisi oluştur (gerçek analiz sonuçları olmadan test için)
        dummy_image_analysis = {
            'total_images': 200,
            'average_resolution': 640,
            'resolution_score': 85,
            'average_sharpness': 45,
            'average_brightness': 128,
            'average_contrast': 60,
            'corrupted_images_ratio': 0.02,
            'low_quality_ratio': 0.08,
            'low_resolution_ratio': 0.05,
            'resolution_diversity_score': 75,
            'color_diversity_score': 80,
            'quality_standard_deviation': 15,
            'resolution_standard_deviation': 50
        }
        
        dummy_annotation_analysis = {
            'total_annotations': 200,
            'num_classes': 5,
            'class_counts': {'class1': 80, 'class2': 60, 'class3': 40, 'class4': 15, 'class5': 5},
            'class_balance_score': 65,
            'bbox_quality_score': 78,
            'annotation_consistency_score': 82,
            'class_imbalance_ratio': 0.4,
            'invalid_bbox_ratio': 0.03,
            'missing_annotations_ratio': 0.01,
            'invalid_annotations_ratio': 0.02,
            'bbox_size_diversity_score': 70,
            'bbox_consistency_score': 75,
            'has_rich_annotations': True
        }
        
        # Kalite değerlendirmesi yap
        print("\n🔍 Kalite değerlendirmesi yapılıyor...")
        quality_metrics = assessor.assess_quality(
            image_analysis=dummy_image_analysis,
            annotation_analysis=dummy_annotation_analysis
        )
        
        print("✅ Kalite değerlendirmesi tamamlandı")
        
        # Sonuçları yazdır
        assessor.print_summary(quality_metrics)
        
        # Detaylı rapor oluştur
        print("\n📄 Detaylı rapor oluşturuluyor...")
        report_path = current_dir.parent / 'data' / 'output' / 'quality_assessment_report.json'
        report = assessor.generate_detailed_report(str(report_path))
        
        if report:
            print(f"✅ Detaylı rapor kaydedildi: {report_path}")
        
        # Özet raporu export et
        print("\n💾 Özet raporu export ediliyor...")
        summary_path = current_dir.parent / 'data' / 'output' / 'quality_summary.txt'
        success = assessor.export_summary_report(str(summary_path), 'txt')
        
        if success:
            print(f"✅ Özet raporu kaydedildi: {summary_path}")
        
        # İyileştirme yol haritası
        recommendations = assessor.recommendation_engine.generate_improvement_roadmap()
        if recommendations:
            print("\n🛣️ İYİLEŞTİRME YOL HARİTASI:")
            print("-" * 40)
            
            if recommendations['immediate_actions']:
                print("🚨 ACIL EYLEMLER:")
                for action in recommendations['immediate_actions']:
                    print(f"   • {action}")
            
            if recommendations['short_term_goals']:
                print("\n📅 KISA VADELİ HEDEFLER:")
                for goal in recommendations['short_term_goals']:
                    print(f"   • {goal}")
            
            if recommendations['long_term_planning']:
                print("\n🔮 UZUN VADELİ PLANLAMA:")
                for plan in recommendations['long_term_planning']:
                    print(f"   • {plan}")
        
        print(f"\n🎉 Test başarıyla tamamlandı!")
        print(f"📊 Genel Kalite Skoru: {quality_metrics.overall_score:.1f}/100")
        print(f"🎓 Veri Seti Notu: {quality_metrics.dataset_grade}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test sırasında hata oluştu: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """Bireysel bileşenleri test et"""
    print("\n🧩 Bireysel Bileşen Testleri...")
    print("=" * 40)
    
    try:
        # Quality Scorer testi
        from src.quality_assessor.quality_scorer import QualityScorer
        scorer = QualityScorer()
        print("✅ QualityScorer başarıyla oluşturuldu")
        
        # Recommendation Engine testi
        from src.quality_assessor.recommendation_engine import RecommendationEngine
        recommender = RecommendationEngine()
        print("✅ RecommendationEngine başarıyla oluşturuldu")
        
        # Completeness Checker testi
        from src.quality_assessor.completeness_checker import CompletenessChecker
        checker = CompletenessChecker()
        print("✅ CompletenessChecker başarıyla oluşturuldu")
        
        return True
        
    except Exception as e:
        print(f"❌ Bileşen testi hatası: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 QUALITY ASSESSOR MODÜLÜ TEST BAŞLANIYOR")
    print("=" * 60)
    
    # Bireysel bileşen testleri
    component_test_success = test_individual_components()
    
    # Ana test
    if component_test_success:
        main_test_success = test_quality_assessor()
        
        if main_test_success:
            print("\n🎉 TÜM TESTLER BAŞARILI!")
        else:
            print("\n❌ ANA TEST BAŞARISIZ!")
    else:
        print("\n❌ BİLEŞEN TESTLERİ BAŞARISIZ!")
