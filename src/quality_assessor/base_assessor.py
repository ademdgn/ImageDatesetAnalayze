"""
Base Quality Assessor Module
Temel kalite değerlendirme fonksiyonalitesi
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
from pathlib import Path

# Logger konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class QualityMetrics:
    """Kalite metriklerini tutan veri sınıfı"""
    overall_score: float
    image_quality_score: float
    annotation_quality_score: float
    completeness_score: float
    diversity_score: float
    consistency_score: float
    
    # Detaylı metrikler
    total_images: int
    total_annotations: int
    num_classes: int
    class_balance_score: float
    image_resolution_score: float
    annotation_accuracy_score: float
    
    # Ek bilgiler
    issues_found: List[str]
    recommendations: List[str]
    dataset_grade: str  # A, B, C, D
    
    def to_dict(self) -> Dict[str, Any]:
        """Metrikleri dictionary'ye dönüştür"""
        return {
            'overall_score': self.overall_score,
            'image_quality_score': self.image_quality_score,
            'annotation_quality_score': self.annotation_quality_score,
            'completeness_score': self.completeness_score,
            'diversity_score': self.diversity_score,
            'consistency_score': self.consistency_score,
            'total_images': self.total_images,
            'total_annotations': self.total_annotations,
            'num_classes': self.num_classes,
            'class_balance_score': self.class_balance_score,
            'image_resolution_score': self.image_resolution_score,
            'annotation_accuracy_score': self.annotation_accuracy_score,
            'issues_found': self.issues_found,
            'recommendations': self.recommendations,
            'dataset_grade': self.dataset_grade
        }

class BaseQualityAssessor(ABC):
    """
    Temel kalite değerlendirici sınıfı
    Tüm kalite değerlendirme modülleri bu sınıftan türetilecek
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        self.metrics = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def _get_default_config(self) -> Dict:
        """Varsayılan konfigürasyonu döndür"""
        return {
            'quality_thresholds': {
                'excellent': 90,
                'good': 75,
                'fair': 60,
                'poor': 0
            },
            'minimum_requirements': {
                'min_images_per_class': 50,
                'min_total_images': 500,
                'min_resolution': 224,
                'max_class_imbalance': 0.8
            },
            'weights': {
                'image_quality': 0.25,
                'annotation_quality': 0.25,
                'completeness': 0.20,
                'diversity': 0.15,
                'consistency': 0.15
            }
        }
    
    @abstractmethod
    def assess_quality(self, data: Dict[str, Any]) -> QualityMetrics:
        """
        Ana kalite değerlendirme metodu
        Alt sınıflar bu metodu implement etmeli
        """
        pass
    
    def calculate_overall_score(self, component_scores: Dict[str, float]) -> float:
        """
        Bileşen skorlarından genel skoru hesapla
        
        Args:
            component_scores: Bileşen skorları
            
        Returns:
            float: Genel kalite skoru (0-100)
        """
        weights = self.config['weights']
        overall_score = 0
        
        for component, score in component_scores.items():
            weight = weights.get(component, 0)
            overall_score += score * weight
            
        return min(100, max(0, overall_score))
    
    def determine_grade(self, overall_score: float) -> str:
        """
        Genel skordan harf notu belirle
        
        Args:
            overall_score: Genel kalite skoru
            
        Returns:
            str: Harf notu (A, B, C, D)
        """
        thresholds = self.config['quality_thresholds']
        
        if overall_score >= thresholds['excellent']:
            return 'A'
        elif overall_score >= thresholds['good']:
            return 'B'
        elif overall_score >= thresholds['fair']:
            return 'C'
        else:
            return 'D'
    
    def validate_minimum_requirements(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Minimum gereksinimleri kontrol et
        
        Args:
            data: Veri seti bilgileri
            
        Returns:
            Tuple[bool, List[str]]: (Gereksinimler karşılandı mı, Eksikler listesi)
        """
        requirements = self.config['minimum_requirements']
        issues = []
        
        # Minimum görüntü sayısı kontrolü
        total_images = data.get('total_images', 0)
        if total_images < requirements['min_total_images']:
            issues.append(f"Toplam görüntü sayısı yetersiz: {total_images} < {requirements['min_total_images']}")
        
        # Sınıf başına minimum görüntü kontrolü
        class_counts = data.get('class_counts', {})
        min_per_class = requirements['min_images_per_class']
        
        for class_name, count in class_counts.items():
            if count < min_per_class:
                issues.append(f"'{class_name}' sınıfı için yetersiz örnek: {count} < {min_per_class}")
        
        # Minimum çözünürlük kontrolü
        avg_resolution = data.get('average_resolution', 0)
        if avg_resolution < requirements['min_resolution']:
            issues.append(f"Ortalama çözünürlük düşük: {avg_resolution} < {requirements['min_resolution']}")
        
        # Class imbalance kontrolü
        class_imbalance = data.get('class_imbalance_ratio', 0)
        max_imbalance = requirements['max_class_imbalance']
        if class_imbalance > max_imbalance:
            issues.append(f"Sınıf dengesizliği yüksek: {class_imbalance:.2f} > {max_imbalance}")
        
        return len(issues) == 0, issues
    
    def generate_recommendations(self, issues: List[str], metrics: QualityMetrics) -> List[str]:
        """
        Tespit edilen sorunlara göre öneriler oluştur
        
        Args:
            issues: Tespit edilen sorunlar
            metrics: Kalite metrikleri
            
        Returns:
            List[str]: Öneriler listesi
        """
        recommendations = []
        
        # Görüntü kalitesi önerileri
        if metrics.image_quality_score < 70:
            recommendations.append("Görüntü kalitesini artırmak için düşük kaliteli görüntüleri filtreleyin")
            recommendations.append("Görüntü ön işleme teknikleri (denoising, sharpening) uygulayın")
        
        # Annotation kalitesi önerileri
        if metrics.annotation_quality_score < 70:
            recommendations.append("Annotation kalitesini artırmak için manuel review yapın")
            recommendations.append("Tutarsız annotation'ları düzeltin")
        
        # Sınıf dengesizliği önerileri
        if metrics.class_balance_score < 70:
            recommendations.append("Az temsil edilen sınıflar için daha fazla veri toplayın")
            recommendations.append("Data augmentation teknikleri kullanın")
        
        # Eksiklik önerileri
        if metrics.completeness_score < 80:
            recommendations.append("Eksik annotation'ları tamamlayın")
            recommendations.append("Veri seti tutarlılığını kontrol edin")
        
        # Çeşitlilik önerileri
        if metrics.diversity_score < 70:
            recommendations.append("Farklı senaryolardan daha fazla veri ekleyin")
            recommendations.append("Görüntü çeşitliliğini artırmak için farklı açılar/ışık koşulları kullanın")
        
        return recommendations
    
    def save_assessment(self, output_path: str, metrics: QualityMetrics) -> bool:
        """
        Değerlendirme sonuçlarını kaydet
        
        Args:
            output_path: Çıktı dosya yolu
            metrics: Kalite metrikleri
            
        Returns:
            bool: Kayıt başarılı mı
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # JSON formatında kaydet
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(metrics.to_dict(), f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Değerlendirme sonuçları kaydedildi: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Kayıt hatası: {str(e)}")
            return False
    
    def load_assessment(self, input_path: str) -> Optional[QualityMetrics]:
        """
        Kaydedilmiş değerlendirme sonuçlarını yükle
        
        Args:
            input_path: Giriş dosya yolu
            
        Returns:
            Optional[QualityMetrics]: Yüklenen metrikler
        """
        try:
            import json
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # QualityMetrics nesnesine dönüştür
            return QualityMetrics(**data)
            
        except Exception as e:
            self.logger.error(f"Yükleme hatası: {str(e)}")
            return None
    
    def compare_assessments(self, 
                          metrics1: QualityMetrics, 
                          metrics2: QualityMetrics) -> Dict[str, float]:
        """
        İki değerlendirmeyi karşılaştır
        
        Args:
            metrics1: İlk metrikler
            metrics2: İkinci metrikler
            
        Returns:
            Dict[str, float]: Karşılaştırma sonuçları
        """
        comparison = {}
        
        # Ana skorları karşılaştır
        comparison['overall_score_diff'] = metrics2.overall_score - metrics1.overall_score
        comparison['image_quality_diff'] = metrics2.image_quality_score - metrics1.image_quality_score
        comparison['annotation_quality_diff'] = metrics2.annotation_quality_score - metrics1.annotation_quality_score
        comparison['completeness_diff'] = metrics2.completeness_score - metrics1.completeness_score
        comparison['diversity_diff'] = metrics2.diversity_score - metrics1.diversity_score
        comparison['consistency_diff'] = metrics2.consistency_score - metrics1.consistency_score
        
        # Sayısal değerleri karşılaştır
        comparison['images_diff'] = metrics2.total_images - metrics1.total_images
        comparison['annotations_diff'] = metrics2.total_annotations - metrics1.total_annotations
        comparison['classes_diff'] = metrics2.num_classes - metrics1.num_classes
        
        return comparison
    
    def print_summary(self, metrics: QualityMetrics) -> None:
        """
        Değerlendirme özetini yazdır
        
        Args:
            metrics: Kalite metrikleri
        """
        print("\n" + "="*60)
        print("           DATASET QUALITY ASSESSMENT SUMMARY")
        print("="*60)
        
        print(f"\n🎯 OVERALL GRADE: {metrics.dataset_grade}")
        print(f"📊 OVERALL SCORE: {metrics.overall_score:.1f}/100")
        
        print(f"\n📈 COMPONENT SCORES:")
        print(f"   🖼️  Image Quality:     {metrics.image_quality_score:.1f}/100")
        print(f"   🏷️  Annotation Quality: {metrics.annotation_quality_score:.1f}/100")
        print(f"   ✅ Completeness:      {metrics.completeness_score:.1f}/100")
        print(f"   🎨 Diversity:         {metrics.diversity_score:.1f}/100")
        print(f"   🔄 Consistency:       {metrics.consistency_score:.1f}/100")
        
        print(f"\n📊 DATASET STATISTICS:")
        print(f"   📁 Total Images:      {metrics.total_images:,}")
        print(f"   🏷️  Total Annotations: {metrics.total_annotations:,}")
        print(f"   📂 Number of Classes: {metrics.num_classes}")
        
        if metrics.issues_found:
            print(f"\n⚠️  ISSUES FOUND ({len(metrics.issues_found)}):")
            for i, issue in enumerate(metrics.issues_found[:5], 1):
                print(f"   {i}. {issue}")
            if len(metrics.issues_found) > 5:
                print(f"   ... ve {len(metrics.issues_found) - 5} tane daha")
        
        if metrics.recommendations:
            print(f"\n💡 TOP RECOMMENDATIONS ({len(metrics.recommendations)}):")
            for i, rec in enumerate(metrics.recommendations[:5], 1):
                print(f"   {i}. {rec}")
            if len(metrics.recommendations) > 5:
                print(f"   ... ve {len(metrics.recommendations) - 5} tane daha")
        
        print("\n" + "="*60)
