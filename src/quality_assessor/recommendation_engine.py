"""
Recommendation Engine Module
İyileştirme önerisi motoru
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Recommendation:
    """Öneri veri sınıfı"""
    category: str
    priority: str  # 'High', 'Medium', 'Low'
    issue: str
    suggestion: str
    expected_improvement: float  # Beklenen skor iyileşmesi
    difficulty: str  # 'Easy', 'Medium', 'Hard'
    estimated_effort: str  # 'Low', 'Medium', 'High'

class RecommendationEngine:
    """
    Veri seti kalitesi için akıllı öneri motoru
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        self.recommendations = []
        
    def _get_default_config(self) -> Dict:
        """Varsayılan konfigürasyon"""
        return {
            'priority_thresholds': {
                'high_priority': 50,
                'medium_priority': 70,
                'low_priority': 85
            },
            'category_weights': {
                'completeness': 1.2,
                'image_quality': 1.1,
                'annotation_quality': 1.1,
                'diversity': 1.0,
                'consistency': 0.9
            }
        }
    
    def generate_recommendations(self, 
                               analysis_results: Dict[str, Any], 
                               quality_scores: Dict[str, float],
                               issues_found: List[str]) -> List[str]:
        """Kapsamlı öneri listesi oluştur"""
        self.recommendations = []
        
        try:
            # Eksiksizlik önerileri
            self._generate_completeness_recommendations(
                analysis_results.get('completeness_analysis', {}),
                quality_scores.get('completeness_score', 0)
            )
            
            # Görüntü kalitesi önerileri
            self._generate_image_quality_recommendations(
                analysis_results.get('image_analysis', {}),
                quality_scores.get('image_quality_score', 0)
            )
            
            # Annotation kalitesi önerileri
            self._generate_annotation_quality_recommendations(
                analysis_results.get('annotation_analysis', {}),
                quality_scores.get('annotation_quality_score', 0)
            )
            
            # Genel öneriler
            self._generate_general_recommendations(quality_scores, issues_found)
            
            return self._sort_and_format_recommendations()
            
        except Exception as e:
            logger.error(f"Öneri üretme hatası: {str(e)}")
            return ["Analiz sonuçları eksik, teknik kontrol gerekli"]
    
    def _generate_completeness_recommendations(self, completeness_analysis: Dict, score: float):
        """Eksiksizlik önerileri"""
        missing_images = completeness_analysis.get('missing_images', [])
        missing_annotations = completeness_analysis.get('missing_annotations', [])
        
        if missing_images:
            self.recommendations.append(Recommendation(
                category='Completeness',
                priority=self._determine_priority(score, 'completeness'),
                issue=f'{len(missing_images)} adet eksik görüntü',
                suggestion='Eksik görüntüleri tamamlayın veya annotation dosyalarını kaldırın',
                expected_improvement=min(20, len(missing_images) * 0.5),
                difficulty='Easy',
                estimated_effort='Low'
            ))
        
        if missing_annotations:
            self.recommendations.append(Recommendation(
                category='Completeness',
                priority=self._determine_priority(score, 'completeness'),
                issue=f'{len(missing_annotations)} adet eksik annotation',
                suggestion='Eksik annotation dosyalarını oluşturun',
                expected_improvement=min(15, len(missing_annotations) * 0.3),
                difficulty='Medium',
                estimated_effort='Medium'
            ))
    
    def _generate_image_quality_recommendations(self, image_analysis: Dict, score: float):
        """Görüntü kalitesi önerileri"""
        avg_resolution = image_analysis.get('average_resolution', 0)
        low_quality_ratio = image_analysis.get('low_quality_ratio', 0)
        
        if avg_resolution < 224:
            self.recommendations.append(Recommendation(
                category='Image Quality',
                priority=self._determine_priority(score, 'image_quality'),
                issue='Düşük çözünürlüklü görüntüler mevcut',
                suggestion='Görüntüleri en az 224x224 piksel çözünürlüğe yükseltin',
                expected_improvement=15.0,
                difficulty='Medium',
                estimated_effort='Medium'
            ))
        
        if low_quality_ratio > 0.1:
            self.recommendations.append(Recommendation(
                category='Image Quality',
                priority='High',
                issue=f'Görüntülerin %{low_quality_ratio*100:.1f}\'i düşük kaliteli',
                suggestion='Bulanık ve bozuk görüntüleri filtreleyin',
                expected_improvement=20.0,
                difficulty='Medium',
                estimated_effort='High'
            ))
    
    def _generate_annotation_quality_recommendations(self, annotation_analysis: Dict, score: float):
        """Annotation kalitesi önerileri"""
        class_imbalance_ratio = annotation_analysis.get('class_imbalance_ratio', 0)
        invalid_bbox_ratio = annotation_analysis.get('invalid_bbox_ratio', 0)
        
        if class_imbalance_ratio > 0.7:
            self.recommendations.append(Recommendation(
                category='Annotation Quality',
                priority=self._determine_priority(score, 'annotation_quality'),
                issue=f'Sınıf dengesizliği yüksek (%{class_imbalance_ratio*100:.1f})',
                suggestion='Az temsil edilen sınıflar için daha fazla veri toplayın',
                expected_improvement=25.0,
                difficulty='Hard',
                estimated_effort='High'
            ))
        
        if invalid_bbox_ratio > 0.05:
            self.recommendations.append(Recommendation(
                category='Annotation Quality',
                priority='High',
                issue=f'Geçersiz bounding box oranı yüksek',
                suggestion='Annotation dosyalarını gözden geçirin ve düzeltin',
                expected_improvement=18.0,
                difficulty='Medium',
                estimated_effort='Medium'
            ))
    
    def _generate_general_recommendations(self, quality_scores: Dict[str, float], issues_found: List[str]):
        """Genel öneriler"""
        overall_score = quality_scores.get('overall_score', 0)
        
        if overall_score < 50:
            self.recommendations.append(Recommendation(
                category='General',
                priority='High',
                issue='Genel veri seti kalitesi çok düşük',
                suggestion='Kapsamlı veri seti yenileme planı oluşturun',
                expected_improvement=30.0,
                difficulty='Hard',
                estimated_effort='High'
            ))
        elif overall_score < 70:
            self.recommendations.append(Recommendation(
                category='General',
                priority='Medium',
                issue='Veri seti kalitesi geliştirilmeli',
                suggestion='Öncelikli iyileştirme alanlarına odaklanın',
                expected_improvement=20.0,
                difficulty='Medium',
                estimated_effort='Medium'
            ))
    
    def _determine_priority(self, score: float, category: str) -> str:
        """Öncelik belirle"""
        thresholds = self.config['priority_thresholds']
        category_weight = self.config['category_weights'].get(category, 1.0)
        adjusted_score = score * category_weight
        
        if adjusted_score < thresholds['high_priority']:
            return 'High'
        elif adjusted_score < thresholds['medium_priority']:
            return 'Medium'
        else:
            return 'Low'
    
    def _sort_and_format_recommendations(self) -> List[str]:
        """Önerileri sırala ve formatla"""
        priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
        
        sorted_recs = sorted(
            self.recommendations,
            key=lambda x: (priority_order[x.priority], x.expected_improvement),
            reverse=True
        )
        
        formatted_recommendations = []
        for rec in sorted_recs:
            improvement_text = f' (+{rec.expected_improvement:.1f} puan)' if rec.expected_improvement > 0 else ''
            formatted_text = f'[{rec.priority}] {rec.category}: {rec.suggestion}{improvement_text}'
            formatted_recommendations.append(formatted_text)
        
        return formatted_recommendations
    
    def get_structured_recommendations(self) -> List[Recommendation]:
        """Yapılandırılmış öneri listesi döndür"""
        return self.recommendations
    
    def generate_improvement_roadmap(self) -> Dict[str, List[str]]:
        """İyileştirme yol haritası oluştur"""
        roadmap = {
            'immediate_actions': [],  # Yüksek öncelik, kolay
            'short_term_goals': [],   # Orta öncelik veya orta zorluk
            'long_term_planning': []  # Düşük öncelik veya zor
        }
        
        for rec in self.recommendations:
            if rec.priority == 'High' and rec.difficulty == 'Easy':
                roadmap['immediate_actions'].append(rec.suggestion)
            elif rec.priority in ['High', 'Medium'] or rec.difficulty == 'Medium':
                roadmap['short_term_goals'].append(rec.suggestion)
            else:
                roadmap['long_term_planning'].append(rec.suggestion)
        
        return roadmap
    
    def export_recommendations(self) -> Dict[str, Any]:
        """Önerileri export formatında döndür"""
        return {
            'structured_recommendations': [rec.__dict__ for rec in self.recommendations],
            'formatted_recommendations': self._sort_and_format_recommendations(),
            'improvement_roadmap': self.generate_improvement_roadmap(),
            'total_recommendations': len(self.recommendations),
            'high_priority_count': len([r for r in self.recommendations if r.priority == 'High']),
            'medium_priority_count': len([r for r in self.recommendations if r.priority == 'Medium']),
            'low_priority_count': len([r for r in self.recommendations if r.priority == 'Low'])
        }
