"""
Main Quality Assessor Module
Ana kalite değerlendirme modülü - Tüm bileşenleri koordine eder
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import logging
import json
from datetime import datetime

# Kendi modüllerimizi import et
from .base_assessor import BaseQualityAssessor, QualityMetrics
from .completeness_checker import CompletenessChecker
from .quality_scorer import QualityScorer
from .recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

class DatasetQualityAssessor(BaseQualityAssessor):
    """
    Ana veri seti kalite değerlendirici sınıfı
    Tüm analiz modüllerini koordine eder ve kapsamlı değerlendirme yapar
    """
    
    def __init__(self, dataset_path: str, config: Optional[Dict] = None):
        super().__init__(config)
        
        self.dataset_path = Path(dataset_path)
        self.completeness_checker = CompletenessChecker(config)
        self.quality_scorer = QualityScorer(config)
        self.recommendation_engine = RecommendationEngine(config)
        
        # Analiz sonuçlarını saklamak için
        self.analysis_results = {}
        self.quality_metrics = None
        
        logger.info(f"DatasetQualityAssessor initialized for: {dataset_path}")
    
    def assess_quality(self, 
                      image_analysis: Optional[Dict] = None,
                      annotation_analysis: Optional[Dict] = None,
                      use_cache: bool = True) -> QualityMetrics:
        """
        Kapsamlı veri seti kalite değerlendirmesi yap
        
        Args:
            image_analysis: Önceden yapılmış görüntü analizi sonuçları
            annotation_analysis: Önceden yapılmış annotation analizi sonuçları
            use_cache: Cache kullanılsın mı
            
        Returns:
            QualityMetrics: Detaylı kalite metrikleri
        """
        logger.info("Veri seti kalite değerlendirmesi başlatılıyor...")
        
        try:
            # 1. Eksiksizlik kontrolü (önce bu yapılmalı)
            logger.info("1/4 - Eksiksizlik kontrolü yapılıyor...")
            completeness_results = self.completeness_checker.check_completeness(self.dataset_path)
            self.analysis_results['completeness_analysis'] = completeness_results
            
            # 2. Görüntü analizi sonuçlarını kullan
            if image_analysis:
                logger.info("2/4 - Görüntü analizi sonuçları alındı...")
                self.analysis_results['image_analysis'] = image_analysis
            else:
                logger.warning("Görüntü analizi sonuçları verilmedi, varsayılan değerler kullanılacak")
                self.analysis_results['image_analysis'] = self._get_default_image_analysis()
            
            # 3. Annotation analizi sonuçlarını kullan
            if annotation_analysis:
                logger.info("3/4 - Annotation analizi sonuçları alındı...")
                self.analysis_results['annotation_analysis'] = annotation_analysis
            else:
                logger.warning("Annotation analizi sonuçları verilmedi, varsayılan değerler kullanılacak")
                self.analysis_results['annotation_analysis'] = self._get_default_annotation_analysis()
            
            # 4. Kalite skorlarını hesapla
            logger.info("4/4 - Kalite skorları hesaplanıyor...")
            quality_scores = self.quality_scorer.calculate_quality_score(self.analysis_results)
            
            # 5. QualityMetrics nesnesini oluştur
            self.quality_metrics = self._create_quality_metrics(quality_scores)
            
            logger.info(f"Kalite değerlendirmesi tamamlandı. Genel skor: {self.quality_metrics.overall_score:.1f}/100")
            
            return self.quality_metrics
            
        except Exception as e:
            logger.error(f"Kalite değerlendirme hatası: {str(e)}")
            return self._create_error_metrics(str(e))
    
    def _create_quality_metrics(self, quality_scores: Dict[str, float]) -> QualityMetrics:
        """Kalite skorlarından QualityMetrics nesnesi oluştur"""
        try:
            # Temel skorlar
            overall_score = quality_scores.get('overall_score', 0)
            image_quality_score = quality_scores.get('image_quality_score', 0)
            annotation_quality_score = quality_scores.get('annotation_quality_score', 0)
            completeness_score = quality_scores.get('completeness_score', 0)
            diversity_score = quality_scores.get('diversity_score', 0)
            consistency_score = quality_scores.get('consistency_score', 0)
            
            # Detaylı metrikler
            completeness_analysis = self.analysis_results.get('completeness_analysis', {})
            annotation_analysis = self.analysis_results.get('annotation_analysis', {})
            
            total_images = completeness_analysis.get('total_images', 0)
            total_annotations = completeness_analysis.get('total_annotations', 0)
            num_classes = annotation_analysis.get('num_classes', 0)
            
            # Alt skorlar
            class_balance_score = quality_scores.get('class_balance_score', 0)
            image_resolution_score = quality_scores.get('image_resolution_score', 0)
            annotation_accuracy_score = quality_scores.get('annotation_accuracy_score', 0)
            
            # Sorun tespiti
            issues_found = self._identify_issues()
            
            # Önerileri oluştur
            recommendations = self.recommendation_engine.generate_recommendations(
                self.analysis_results, quality_scores, issues_found
            )
            
            # Harf notu belirle
            dataset_grade = self.quality_scorer.calculate_grade(overall_score)
            
            return QualityMetrics(
                overall_score=overall_score,
                image_quality_score=image_quality_score,
                annotation_quality_score=annotation_quality_score,
                completeness_score=completeness_score,
                diversity_score=diversity_score,
                consistency_score=consistency_score,
                total_images=total_images,
                total_annotations=total_annotations,
                num_classes=num_classes,
                class_balance_score=class_balance_score,
                image_resolution_score=image_resolution_score,
                annotation_accuracy_score=annotation_accuracy_score,
                issues_found=issues_found,
                recommendations=recommendations,
                dataset_grade=dataset_grade
            )
            
        except Exception as e:
            logger.error(f"QualityMetrics oluşturma hatası: {str(e)}")
            return self._create_error_metrics(str(e))
    
    def _identify_issues(self) -> List[str]:
        """Veri setindeki sorunları tespit et"""
        issues = []
        
        try:
            # Completeness sorunları
            completeness_analysis = self.analysis_results.get('completeness_analysis', {})
            
            missing_images = completeness_analysis.get('missing_images', [])
            if missing_images:
                issues.append(f"{len(missing_images)} adet eksik görüntü tespit edildi")
            
            missing_annotations = completeness_analysis.get('missing_annotations', [])
            if missing_annotations:
                issues.append(f"{len(missing_annotations)} adet eksik annotation tespit edildi")
            
            corrupted_images = completeness_analysis.get('corrupted_images', [])
            if corrupted_images:
                issues.append(f"{len(corrupted_images)} adet bozuk görüntü tespit edildi")
            
            corrupted_annotations = completeness_analysis.get('corrupted_annotations', [])
            if corrupted_annotations:
                issues.append(f"{len(corrupted_annotations)} adet bozuk annotation tespit edildi")
            
            # Görüntü kalitesi sorunları
            image_analysis = self.analysis_results.get('image_analysis', {})
            
            low_resolution_ratio = image_analysis.get('low_resolution_ratio', 0)
            if low_resolution_ratio > 0.1:
                issues.append(f"Görüntülerin %{low_resolution_ratio*100:.1f}'i düşük çözünürlüklü")
            
            low_quality_ratio = image_analysis.get('low_quality_ratio', 0)
            if low_quality_ratio > 0.1:
                issues.append(f"Görüntülerin %{low_quality_ratio*100:.1f}'i düşük kaliteli")
            
            # Annotation sorunları
            annotation_analysis = self.analysis_results.get('annotation_analysis', {})
            
            class_imbalance_ratio = annotation_analysis.get('class_imbalance_ratio', 0)
            if class_imbalance_ratio > 0.8:
                issues.append(f"Sınıf dengesizliği yüksek: %{class_imbalance_ratio*100:.1f}")
            
            invalid_bbox_ratio = annotation_analysis.get('invalid_bbox_ratio', 0)
            if invalid_bbox_ratio > 0.05:
                issues.append(f"Geçersiz bounding box oranı: %{invalid_bbox_ratio*100:.1f}")
            
            # Minimum gereksinimler kontrolü
            requirements_met, requirement_issues = self.validate_minimum_requirements({
                'total_images': completeness_analysis.get('total_images', 0),
                'class_counts': annotation_analysis.get('class_counts', {}),
                'average_resolution': image_analysis.get('average_resolution', 0),
                'class_imbalance_ratio': class_imbalance_ratio
            })
            
            if not requirements_met:
                issues.extend(requirement_issues)
            
        except Exception as e:
            logger.error(f"Sorun tespiti hatası: {str(e)}")
            issues.append(f"Analiz sırasında hata oluştu: {str(e)}")
        
        return issues
    
    def _create_error_metrics(self, error_message: str) -> QualityMetrics:
        """Hata durumunda varsayılan metrikler oluştur"""
        return QualityMetrics(
            overall_score=0.0,
            image_quality_score=0.0,
            annotation_quality_score=0.0,
            completeness_score=0.0,
            diversity_score=0.0,
            consistency_score=0.0,
            total_images=0,
            total_annotations=0,
            num_classes=0,
            class_balance_score=0.0,
            image_resolution_score=0.0,
            annotation_accuracy_score=0.0,
            issues_found=[f"Kritik hata: {error_message}"],
            recommendations=["Veri seti yapısını kontrol edin", "Teknik destek alın"],
            dataset_grade='F'
        )
    
    def _get_default_image_analysis(self) -> Dict:
        """Varsayılan görüntü analizi sonuçları"""
        return {
            'total_images': 0,
            'average_resolution': 0,
            'resolution_score': 50,
            'average_sharpness': 50,
            'average_brightness': 128,
            'average_contrast': 50,
            'corrupted_images_ratio': 0,
            'low_quality_ratio': 0,
            'low_resolution_ratio': 0,
            'resolution_diversity_score': 50,
            'color_diversity_score': 50,
            'quality_standard_deviation': 0,
            'resolution_standard_deviation': 0
        }
    
    def _get_default_annotation_analysis(self) -> Dict:
        """Varsayılan annotation analizi sonuçları"""
        return {
            'total_annotations': 0,
            'num_classes': 0,
            'class_counts': {},
            'class_balance_score': 50,
            'bbox_quality_score': 50,
            'annotation_consistency_score': 50,
            'class_imbalance_ratio': 0,
            'invalid_bbox_ratio': 0,
            'missing_annotations_ratio': 0,
            'invalid_annotations_ratio': 0,
            'bbox_size_diversity_score': 50,
            'bbox_consistency_score': 50,
            'has_rich_annotations': False
        }
    
    def generate_detailed_report(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Detaylı analiz raporu oluştur
        
        Args:
            output_path: Rapor kayıt yolu (opsiyonel)
            
        Returns:
            Dict: Detaylı rapor
        """
        if not self.quality_metrics:
            logger.warning("Kalite değerlendirmesi yapılmamış, önce assess_quality() çağırın")
            return {}
        
        report = {
            'metadata': {
                'assessment_date': datetime.now().isoformat(),
                'dataset_path': str(self.dataset_path),
                'assessor_version': '1.0.0'
            },
            'summary': {
                'overall_score': self.quality_metrics.overall_score,
                'dataset_grade': self.quality_metrics.dataset_grade,
                'quality_level': self.quality_scorer.get_quality_level(self.quality_metrics.overall_score)
            },
            'detailed_scores': self.quality_metrics.to_dict(),
            'analysis_results': self.analysis_results,
            'improvement_areas': self.quality_scorer.identify_improvement_areas({
                'image_quality_score': self.quality_metrics.image_quality_score,
                'annotation_quality_score': self.quality_metrics.annotation_quality_score,
                'completeness_score': self.quality_metrics.completeness_score,
                'diversity_score': self.quality_metrics.diversity_score,
                'consistency_score': self.quality_metrics.consistency_score
            }),
            'recommendations': {
                'high_priority': [r for r in self.quality_metrics.recommendations[:5]],
                'all_recommendations': self.quality_metrics.recommendations
            }
        }
        
        # Raporu kaydet
        if output_path:
            try:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False, default=str)
                
                logger.info(f"Detaylı rapor kaydedildi: {output_path}")
                
            except Exception as e:
                logger.error(f"Rapor kaydetme hatası: {str(e)}")
        
        return report
    
    def compare_with_baseline(self, baseline_metrics: QualityMetrics) -> Dict[str, Any]:
        """
        Baseline ile karşılaştırma yap
        
        Args:
            baseline_metrics: Baseline kalite metrikleri
            
        Returns:
            Dict: Karşılaştırma sonuçları
        """
        if not self.quality_metrics:
            logger.warning("Kalite değerlendirmesi yapılmamış")
            return {}
        
        comparison = self.compare_assessments(baseline_metrics, self.quality_metrics)
        
        comparison_report = {
            'improvements': [],
            'deteriorations': [],
            'recommendations': []
        }
        
        # İyileşmeleri tespit et
        for key, diff in comparison.items():
            if 'diff' in key and diff > 5:  # 5 puan üstü iyileşme
                metric_name = key.replace('_diff', '').replace('_', ' ').title()
                comparison_report['improvements'].append(f"{metric_name}: +{diff:.1f} puan")
        
        # Kötüleşmeleri tespit et
        for key, diff in comparison.items():
            if 'diff' in key and diff < -5:  # 5 puan altı kötüleşme
                metric_name = key.replace('_diff', '').replace('_', ' ').title()
                comparison_report['deteriorations'].append(f"{metric_name}: {diff:.1f} puan")
        
        # Karşılaştırma önerileri
        if comparison['overall_score_diff'] < 0:
            comparison_report['recommendations'].append("Genel kalite skoru düştü, detaylı inceleme gerekli")
        
        if comparison['images_diff'] > 0:
            comparison_report['recommendations'].append("Yeni görüntüler eklendi, kalite kontrolü yapın")
        
        return comparison_report
    
    def get_quality_trend(self, historical_assessments: List[QualityMetrics]) -> Dict[str, Any]:
        """
        Kalite trend analizi yap
        
        Args:
            historical_assessments: Geçmiş değerlendirmeler
            
        Returns:
            Dict: Trend analizi sonuçları
        """
        if not historical_assessments:
            return {}
        
        # Zamansal trend hesapla
        overall_scores = [m.overall_score for m in historical_assessments]
        
        if len(overall_scores) > 1:
            # Linear trend hesapla
            x = np.arange(len(overall_scores))
            slope = np.polyfit(x, overall_scores, 1)[0]
            
            trend_direction = 'improving' if slope > 1 else 'declining' if slope < -1 else 'stable'
        else:
            trend_direction = 'insufficient_data'
            slope = 0
        
        return {
            'trend_direction': trend_direction,
            'trend_slope': slope,
            'score_history': overall_scores,
            'best_score': max(overall_scores),
            'worst_score': min(overall_scores),
            'average_score': np.mean(overall_scores),
            'score_variance': np.var(overall_scores)
        }
    
    def export_summary_report(self, output_path: str, format_type: str = 'json') -> bool:
        """
        Özet raporu farklı formatlarda export et
        
        Args:
            output_path: Çıktı dosya yolu
            format_type: Format türü ('json', 'csv', 'txt')
            
        Returns:
            bool: Export başarılı mı
        """
        if not self.quality_metrics:
            logger.warning("Kalite değerlendirmesi yapılmamış")
            return False
        
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type.lower() == 'json':
                return self.save_assessment(str(output_file), self.quality_metrics)
            
            elif format_type.lower() == 'csv':
                # CSV formatında kaydet
                df = pd.DataFrame([self.quality_metrics.to_dict()])
                df.to_csv(output_file, index=False)
                return True
            
            elif format_type.lower() == 'txt':
                # Text formatında özet kaydet
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(self.quality_scorer.generate_score_summary(self.quality_metrics.to_dict()))
                return True
            
            else:
                logger.error(f"Desteklenmeyen format: {format_type}")
                return False
                
        except Exception as e:
            logger.error(f"Export hatası: {str(e)}")
            return False
    
    def get_analysis_results(self) -> Dict[str, Any]:
        """Analiz sonuçlarını döndür"""
        return self.analysis_results.copy()
    
    def get_quality_metrics(self) -> Optional[QualityMetrics]:
        """Kalite metriklerini döndür"""
        return self.quality_metrics
    
    def reset_assessment(self):
        """Değerlendirmeyi sıfırla"""
        self.analysis_results = {}
        self.quality_metrics = None
        logger.info("Değerlendirme sıfırlandı")
