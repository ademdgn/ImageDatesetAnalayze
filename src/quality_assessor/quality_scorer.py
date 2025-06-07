"""
Quality Scorer Module
Gelişmiş kalite skorlama algoritmaları
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from collections import defaultdict
import math

logger = logging.getLogger(__name__)

@dataclass
class QualityWeights:
    """Kalite skorlama ağırlıkları"""
    image_quality: float = 0.25
    annotation_quality: float = 0.25
    completeness: float = 0.20
    diversity: float = 0.15
    consistency: float = 0.15
    
    def normalize(self):
        """Ağırlıkları normalize et"""
        total = (self.image_quality + self.annotation_quality + 
                self.completeness + self.diversity + self.consistency)
        if total > 0:
            self.image_quality /= total
            self.annotation_quality /= total
            self.completeness /= total
            self.diversity /= total
            self.consistency /= total

class QualityScorer:
    """
    Veri seti kalite skorlama algoritmaları
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        self.weights = QualityWeights(**self.config.get('weights', {}))
        self.weights.normalize()
        
    def _get_default_config(self) -> Dict:
        """Varsayılan konfigürasyon"""
        return {
            'weights': {
                'image_quality': 0.25,
                'annotation_quality': 0.25,
                'completeness': 0.20,
                'diversity': 0.15,
                'consistency': 0.15
            },
            'thresholds': {
                'excellent_threshold': 90,
                'good_threshold': 75,
                'fair_threshold': 60,
                'poor_threshold': 40
            },
            'penalties': {
                'missing_files': 30,
                'corrupted_files': 20,
                'low_resolution': 15,
                'class_imbalance': 25,
                'inconsistent_annotations': 20
            },
            'bonuses': {
                'high_diversity': 10,
                'consistent_quality': 5,
                'rich_annotations': 8
            }
        }
    
    def calculate_quality_score(self, analysis_results: Dict) -> Dict[str, float]:
        """
        Kapsamlı kalite skoru hesapla
        
        Args:
            analysis_results: Tüm analiz sonuçları
            
        Returns:
            Dict: Detaylı kalite skorları
        """
        scores = {}
        
        try:
            # 1. Görüntü kalitesi skoru
            scores['image_quality_score'] = self._calculate_image_quality_score(
                analysis_results.get('image_analysis', {})
            )
            
            # 2. Annotation kalitesi skoru
            scores['annotation_quality_score'] = self._calculate_annotation_quality_score(
                analysis_results.get('annotation_analysis', {})
            )
            
            # 3. Eksiksizlik skoru
            scores['completeness_score'] = self._calculate_completeness_score(
                analysis_results.get('completeness_analysis', {})
            )
            
            # 4. Çeşitlilik skoru
            scores['diversity_score'] = self._calculate_diversity_score(
                analysis_results.get('image_analysis', {}),
                analysis_results.get('annotation_analysis', {})
            )
            
            # 5. Tutarlılık skoru
            scores['consistency_score'] = self._calculate_consistency_score(
                analysis_results.get('image_analysis', {}),
                analysis_results.get('annotation_analysis', {})
            )
            
            # 6. Genel skor hesapla
            scores['overall_score'] = self._calculate_overall_score(scores)
            
            # 7. Detaylı alt skorları hesapla
            detailed_scores = self._calculate_detailed_scores(analysis_results)
            scores.update(detailed_scores)
            
        except Exception as e:
            logger.error(f"Kalite skoru hesaplama hatası: {str(e)}")
            scores = self._get_default_scores()
            
        return scores
    
    def _calculate_image_quality_score(self, image_analysis: Dict) -> float:
        """Görüntü kalitesi skoru hesapla"""
        try:
            base_score = 100.0
            
            # Çözünürlük skoru
            resolution_score = image_analysis.get('resolution_score', 80)
            resolution_weight = 0.3
            
            # Görüntü kalite metrikleri
            avg_sharpness = image_analysis.get('average_sharpness', 50)
            avg_brightness = image_analysis.get('average_brightness', 128)
            avg_contrast = image_analysis.get('average_contrast', 50)
            
            # Normalleştirme
            sharpness_score = min(100, (avg_sharpness / 100) * 100) if avg_sharpness > 0 else 50
            brightness_score = self._normalize_brightness_score(avg_brightness)
            contrast_score = min(100, (avg_contrast / 100) * 100) if avg_contrast > 0 else 50
            
            # Weighted average
            quality_score = (
                resolution_score * resolution_weight +
                sharpness_score * 0.25 +
                brightness_score * 0.25 +
                contrast_score * 0.2
            )
            
            # Penaltiler
            corrupted_ratio = image_analysis.get('corrupted_images_ratio', 0)
            if corrupted_ratio > 0:
                quality_score -= corrupted_ratio * self.config['penalties']['corrupted_files']
            
            low_quality_ratio = image_analysis.get('low_quality_ratio', 0)
            if low_quality_ratio > 0.1:  # %10'dan fazla düşük kalite
                quality_score -= (low_quality_ratio - 0.1) * 50
            
            return max(0, min(100, quality_score))
            
        except Exception as e:
            logger.error(f"Görüntü kalitesi skoru hesaplama hatası: {str(e)}")
            return 50.0
    
    def _calculate_annotation_quality_score(self, annotation_analysis: Dict) -> float:
        """Annotation kalitesi skoru hesapla"""
        try:
            base_score = 100.0
            
            # Sınıf dağılımı skoru
            class_balance_score = annotation_analysis.get('class_balance_score', 70)
            
            # Bounding box kalitesi
            bbox_quality = annotation_analysis.get('bbox_quality_score', 80)
            
            # Annotation tutarlılığı
            consistency_score = annotation_analysis.get('annotation_consistency_score', 85)
            
            # Weighted average
            quality_score = (
                class_balance_score * 0.4 +
                bbox_quality * 0.35 +
                consistency_score * 0.25
            )
            
            # Penaltiler
            missing_annotations_ratio = annotation_analysis.get('missing_annotations_ratio', 0)
            if missing_annotations_ratio > 0:
                quality_score -= missing_annotations_ratio * self.config['penalties']['missing_files']
            
            invalid_annotations_ratio = annotation_analysis.get('invalid_annotations_ratio', 0)
            if invalid_annotations_ratio > 0:
                quality_score -= invalid_annotations_ratio * self.config['penalties']['inconsistent_annotations']
            
            # Bonuslar
            if annotation_analysis.get('has_rich_annotations', False):
                quality_score += self.config['bonuses']['rich_annotations']
            
            return max(0, min(100, quality_score))
            
        except Exception as e:
            logger.error(f"Annotation kalitesi skoru hesaplama hatası: {str(e)}")
            return 50.0
    
    def _calculate_completeness_score(self, completeness_analysis: Dict) -> float:
        """Eksiksizlik skoru hesapla"""
        try:
            # Doğrudan completeness_checker'dan gelen skoru kullan
            base_score = completeness_analysis.get('completeness_score', 80)
            
            # Ek değerlendirmeler
            matching_ratio = completeness_analysis.get('matching_ratio', 1.0)
            if matching_ratio < 1.0:
                base_score *= matching_ratio
            
            # File integrity bonusu
            corrupted_files = (len(completeness_analysis.get('corrupted_images', [])) + 
                             len(completeness_analysis.get('corrupted_annotations', [])))
            total_files = (completeness_analysis.get('total_images', 0) + 
                          completeness_analysis.get('total_annotations', 0))
            
            if total_files > 0:
                corruption_ratio = corrupted_files / total_files
                base_score -= corruption_ratio * 30
            
            return max(0, min(100, base_score))
            
        except Exception as e:
            logger.error(f"Eksiksizlik skoru hesaplama hatası: {str(e)}")
            return 70.0
    
    def _calculate_diversity_score(self, image_analysis: Dict, annotation_analysis: Dict) -> float:
        """Çeşitlilik skoru hesapla"""
        try:
            diversity_score = 100.0
            
            # Görüntü çeşitliliği
            resolution_diversity = image_analysis.get('resolution_diversity_score', 70)
            color_diversity = image_analysis.get('color_diversity_score', 80)
            
            # Sınıf çeşitliliği
            class_count = annotation_analysis.get('num_classes', 1)
            class_diversity = min(100, (class_count / 10) * 100)  # 10 sınıf = 100 puan
            
            # Bbox boyut çeşitliliği
            bbox_size_diversity = annotation_analysis.get('bbox_size_diversity_score', 75)
            
            # Weighted average
            diversity_score = (
                resolution_diversity * 0.25 +
                color_diversity * 0.25 +
                class_diversity * 0.3 +
                bbox_size_diversity * 0.2
            )
            
            # Az sınıf cezası
            if class_count < 3:
                diversity_score -= (3 - class_count) * 15
            
            # Yüksek çeşitlilik bonusu
            if diversity_score > 85:
                diversity_score += self.config['bonuses']['high_diversity']
            
            return max(0, min(100, diversity_score))
            
        except Exception as e:
            logger.error(f"Çeşitlilik skoru hesaplama hatası: {str(e)}")
            return 60.0
    
    def _calculate_consistency_score(self, image_analysis: Dict, annotation_analysis: Dict) -> float:
        """Tutarlılık skoru hesapla"""
        try:
            consistency_score = 100.0
            
            # Görüntü kalitesi tutarlılığı
            quality_std = image_analysis.get('quality_standard_deviation', 0)
            if quality_std > 0:
                quality_consistency = max(0, 100 - (quality_std * 2))
            else:
                quality_consistency = 80
            
            # Çözünürlük tutarlılığı
            resolution_std = image_analysis.get('resolution_standard_deviation', 0)
            if resolution_std > 0:
                resolution_consistency = max(0, 100 - (resolution_std / 100))
            else:
                resolution_consistency = 80
            
            # Annotation tutarlılığı
            annotation_consistency = annotation_analysis.get('annotation_consistency_score', 85)
            
            # Bbox boyut tutarlılığı
            bbox_consistency = annotation_analysis.get('bbox_consistency_score', 80)
            
            # Weighted average
            consistency_score = (
                quality_consistency * 0.3 +
                resolution_consistency * 0.25 +
                annotation_consistency * 0.25 +
                bbox_consistency * 0.2
            )
            
            # Tutarlı kalite bonusu
            if consistency_score > 90:
                consistency_score += self.config['bonuses']['consistent_quality']
            
            return max(0, min(100, consistency_score))
            
        except Exception as e:
            logger.error(f"Tutarlılık skoru hesaplama hatası: {str(e)}")
            return 70.0
    
    def _calculate_overall_score(self, component_scores: Dict[str, float]) -> float:
        """Genel kalite skoru hesapla"""
        try:
            overall_score = (
                component_scores.get('image_quality_score', 0) * self.weights.image_quality +
                component_scores.get('annotation_quality_score', 0) * self.weights.annotation_quality +
                component_scores.get('completeness_score', 0) * self.weights.completeness +
                component_scores.get('diversity_score', 0) * self.weights.diversity +
                component_scores.get('consistency_score', 0) * self.weights.consistency
            )
            
            return max(0, min(100, overall_score))
            
        except Exception as e:
            logger.error(f"Genel skor hesaplama hatası: {str(e)}")
            return 50.0
    
    def _calculate_detailed_scores(self, analysis_results: Dict) -> Dict[str, float]:
        """Detaylı alt skorları hesapla"""
        detailed_scores = {}
        
        try:
            # Görüntü alt skorları
            image_analysis = analysis_results.get('image_analysis', {})
            detailed_scores['image_resolution_score'] = image_analysis.get('resolution_score', 80)
            detailed_scores['image_sharpness_score'] = self._normalize_score(image_analysis.get('average_sharpness', 50))
            detailed_scores['image_brightness_score'] = self._normalize_brightness_score(image_analysis.get('average_brightness', 128))
            detailed_scores['image_contrast_score'] = self._normalize_score(image_analysis.get('average_contrast', 50))
            
            # Annotation alt skorları
            annotation_analysis = analysis_results.get('annotation_analysis', {})
            detailed_scores['class_balance_score'] = annotation_analysis.get('class_balance_score', 70)
            detailed_scores['bbox_quality_score'] = annotation_analysis.get('bbox_quality_score', 80)
            detailed_scores['annotation_accuracy_score'] = annotation_analysis.get('annotation_consistency_score', 85)
            
            # Completeness alt skorları
            completeness_analysis = analysis_results.get('completeness_analysis', {})
            detailed_scores['file_matching_score'] = completeness_analysis.get('matching_ratio', 1.0) * 100
            detailed_scores['file_integrity_score'] = self._calculate_file_integrity_score(completeness_analysis)
            detailed_scores['directory_structure_score'] = completeness_analysis.get('directory_structure_score', 100)
            detailed_scores['naming_convention_score'] = completeness_analysis.get('naming_score', 100)
            
        except Exception as e:
            logger.error(f"Detaylı skor hesaplama hatası: {str(e)}")
            
        return detailed_scores
    
    def _calculate_file_integrity_score(self, completeness_analysis: Dict) -> float:
        """Dosya bütünlüğü skoru hesapla"""
        try:
            corrupted_images = len(completeness_analysis.get('corrupted_images', []))
            corrupted_annotations = len(completeness_analysis.get('corrupted_annotations', []))
            total_images = completeness_analysis.get('total_images', 0)
            total_annotations = completeness_analysis.get('total_annotations', 0)
            
            total_files = total_images + total_annotations
            corrupted_files = corrupted_images + corrupted_annotations
            
            if total_files == 0:
                return 100.0
                
            integrity_ratio = 1.0 - (corrupted_files / total_files)
            return max(0, min(100, integrity_ratio * 100))
            
        except Exception:
            return 85.0
    
    def _normalize_score(self, value: float, min_val: float = 0, max_val: float = 100) -> float:
        """Skoru normalize et"""
        if max_val == min_val:
            return 50.0
        normalized = ((value - min_val) / (max_val - min_val)) * 100
        return max(0, min(100, normalized))
    
    def _normalize_brightness_score(self, brightness: float) -> float:
        """Parlaklık skorunu normalize et (ideal 128 civarı)"""
        try:
            # İdeal parlaklık 128 (0-255 aralığında)
            ideal_brightness = 128
            diff = abs(brightness - ideal_brightness)
            
            # Maksimum sapma 128 olabilir
            score = max(0, 100 - (diff / 128) * 100)
            return score
            
        except Exception:
            return 50.0
    
    def _get_default_scores(self) -> Dict[str, float]:
        """Hata durumunda varsayılan skorları döndür"""
        return {
            'overall_score': 50.0,
            'image_quality_score': 50.0,
            'annotation_quality_score': 50.0,
            'completeness_score': 50.0,
            'diversity_score': 50.0,
            'consistency_score': 50.0,
            'image_resolution_score': 50.0,
            'image_sharpness_score': 50.0,
            'image_brightness_score': 50.0,
            'image_contrast_score': 50.0,
            'class_balance_score': 50.0,
            'bbox_quality_score': 50.0,
            'annotation_accuracy_score': 50.0,
            'file_matching_score': 50.0,
            'file_integrity_score': 50.0,
            'directory_structure_score': 50.0,
            'naming_convention_score': 50.0
        }
    
    def calculate_grade(self, overall_score: float) -> str:
        """Skordan harf notu hesapla"""
        thresholds = self.config['thresholds']
        
        if overall_score >= thresholds['excellent_threshold']:
            return 'A'
        elif overall_score >= thresholds['good_threshold']:
            return 'B'
        elif overall_score >= thresholds['fair_threshold']:
            return 'C'
        else:
            return 'D'
    
    def get_quality_level(self, overall_score: float) -> str:
        """Skordan kalite seviyesi belirle"""
        thresholds = self.config['thresholds']
        
        if overall_score >= thresholds['excellent_threshold']:
            return 'Excellent'
        elif overall_score >= thresholds['good_threshold']:
            return 'Good'
        elif overall_score >= thresholds['fair_threshold']:
            return 'Fair'
        elif overall_score >= thresholds['poor_threshold']:
            return 'Poor'
        else:
            return 'Very Poor'
    
    def identify_improvement_areas(self, component_scores: Dict[str, float]) -> List[Tuple[str, float, str]]:
        """İyileştirme alanlarını belirle"""
        improvement_areas = []
        
        threshold = 70.0  # Bu değerin altındaki skorlar iyileştirme gerektirir
        
        score_descriptions = {
            'image_quality_score': 'Görüntü Kalitesi',
            'annotation_quality_score': 'Annotation Kalitesi',
            'completeness_score': 'Veri Eksiksizliği',
            'diversity_score': 'Veri Çeşitliliği',
            'consistency_score': 'Veri Tutarlılığı'
        }
        
        for score_key, description in score_descriptions.items():
            score = component_scores.get(score_key, 0)
            if score < threshold:
                priority = 'Yüksek' if score < 50 else 'Orta' if score < 60 else 'Düşük'
                improvement_areas.append((description, score, priority))
        
        # Önceliğe göre sırala (düşük skorlar önce)
        improvement_areas.sort(key=lambda x: x[1])
        
        return improvement_areas
    
    def calculate_improvement_potential(self, current_scores: Dict[str, float]) -> Dict[str, float]:
        """İyileştirme potansiyelini hesapla"""
        potential = {}
        
        for key, current_score in current_scores.items():
            if 'score' in key:
                # Maksimum potansiyel iyileştirme
                max_improvement = 100 - current_score
                
                # Gerçekçi iyileştirme (maksimumun %70'i)
                realistic_improvement = max_improvement * 0.7
                
                potential[key.replace('_score', '_potential')] = realistic_improvement
        
        return potential
    
    def generate_score_summary(self, scores: Dict[str, float]) -> str:
        """Skor özetini oluştur"""
        overall_score = scores.get('overall_score', 0)
        grade = self.calculate_grade(overall_score)
        quality_level = self.get_quality_level(overall_score)
        
        summary = []
        summary.append(f"📊 OVERALL QUALITY SCORE: {overall_score:.1f}/100 (Grade: {grade})")
        summary.append(f"🎯 QUALITY LEVEL: {quality_level}")
        summary.append("\n📈 COMPONENT BREAKDOWN:")
        summary.append(f"   🖼️  Image Quality:     {scores.get('image_quality_score', 0):.1f}/100")
        summary.append(f"   🏷️  Annotation Quality: {scores.get('annotation_quality_score', 0):.1f}/100")
        summary.append(f"   ✅ Completeness:      {scores.get('completeness_score', 0):.1f}/100")
        summary.append(f"   🎨 Diversity:         {scores.get('diversity_score', 0):.1f}/100")
        summary.append(f"   🔄 Consistency:       {scores.get('consistency_score', 0):.1f}/100")
        
        # İyileştirme alanları
        component_scores = {
            'image_quality_score': scores.get('image_quality_score', 0),
            'annotation_quality_score': scores.get('annotation_quality_score', 0),
            'completeness_score': scores.get('completeness_score', 0),
            'diversity_score': scores.get('diversity_score', 0),
            'consistency_score': scores.get('consistency_score', 0)
        }
        
        improvement_areas = self.identify_improvement_areas(component_scores)
        
        if improvement_areas:
            summary.append("\n🎯 AREAS FOR IMPROVEMENT:")
            for area, score, priority in improvement_areas[:3]:
                summary.append(f"   • {area}: {score:.1f}/100 (Priority: {priority})")
        
        return "\n".join(summary)
