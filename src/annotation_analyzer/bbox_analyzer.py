#!/usr/bin/env python3
"""
Bounding Box Analiz Modülü

Bu modül bounding box'ların boyut, konum ve kalitesini analiz eder.
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import math

class BoundingBoxAnalyzer:
    """Bounding box analizi yapan sınıf"""
    
    def __init__(self, config: Dict = None):
        """
        BoundingBoxAnalyzer sınıfını başlat
        
        Args:
            config: Konfigürasyon parametreleri
        """
        self.config = config or {}
        self.min_bbox_area = self.config.get('min_bbox_area', 100)
        self.max_bbox_area = self.config.get('max_bbox_area', 500000)
        self.min_bbox_ratio = self.config.get('min_bbox_ratio', 0.1)
        self.max_bbox_ratio = self.config.get('max_bbox_ratio', 10.0)
        
    def analyze_bboxes(self, annotations_data: List[Dict]) -> Dict[str, Any]:
        """
        Bounding box'ları kapsamlı analiz et
        
        Args:
            annotations_data: Parse edilmiş annotation verileri
            
        Returns:
            Bounding box analiz sonuçları
        """
        if not annotations_data:
            return {'error': 'No annotation data provided'}
        
        # Tüm annotation'ları topla
        all_annotations = []
        for data in annotations_data:
            if data.get('parsing_failed', False):
                continue
            all_annotations.extend(data.get('annotations', []))
        
        if not all_annotations:
            return {'error': 'No valid annotations found'}
        
        # Bbox verilerini normalize et
        normalized_bboxes = self._normalize_bboxes(all_annotations)
        
        # Boyut analizi
        size_analysis = self._analyze_bbox_sizes(normalized_bboxes)
        
        # Aspect ratio analizi
        aspect_ratio_analysis = self._analyze_aspect_ratios(normalized_bboxes)
        
        # Konum analizi
        position_analysis = self._analyze_bbox_positions(normalized_bboxes)
        
        # Overlap analizi
        overlap_analysis = self._analyze_bbox_overlaps(normalized_bboxes)
        
        # Sınıf bazlı analiz
        class_based_analysis = self._analyze_by_class(normalized_bboxes)
        
        # Kalite değerlendirmesi
        quality_assessment = self._assess_bbox_quality(normalized_bboxes)
        
        # Öneriler
        recommendations = self._generate_bbox_recommendations(
            size_analysis, aspect_ratio_analysis, quality_assessment
        )
        
        return {
            'total_bboxes': len(normalized_bboxes),
            'size_analysis': size_analysis,
            'aspect_ratio_analysis': aspect_ratio_analysis,
            'position_analysis': position_analysis,
            'overlap_analysis': overlap_analysis,
            'class_based_analysis': class_based_analysis,
            'quality_assessment': quality_assessment,
            'recommendations': recommendations
        }
    
    def _normalize_bboxes(self, annotations: List[Dict]) -> List[Dict]:
        """Bounding box'ları normalize et"""
        normalized = []
        
        for ann in annotations:
            bbox = ann.get('bbox', [])
            if len(bbox) != 4:
                continue
            
            # Format'a göre normalize et
            format_type = ann.get('format', 'yolo')
            
            if format_type == 'yolo':
                # YOLO zaten normalized (0-1)
                x_center, y_center, width, height = bbox
                
                # Area hesapla (normalized)
                area_norm = width * height
                
                # Absolute area hesapla (pixel cinsinden eğer görüntü boyutu varsa)
                img_width = ann.get('image_width', 1)
                img_height = ann.get('image_height', 1)
                area_abs = area_norm * img_width * img_height
                
            elif format_type in ['pascal_voc', 'labelme']:
                # Pascal VOC: [xmin, ymin, xmax, ymax]
                xmin, ymin, xmax, ymax = bbox
                img_width = ann.get('image_width', 1)
                img_height = ann.get('image_height', 1)
                
                # Normalize koordinatlar
                width = (xmax - xmin) / img_width
                height = (ymax - ymin) / img_height
                x_center = (xmin + xmax) / 2 / img_width
                y_center = (ymin + ymax) / 2 / img_height
                
                area_norm = width * height
                area_abs = (xmax - xmin) * (ymax - ymin)
                
            elif format_type == 'coco':
                # COCO: [x, y, width, height]
                x, y, width_abs, height_abs = bbox
                img_width = ann.get('image_width', 1)
                img_height = ann.get('image_height', 1)
                
                # Normalize koordinatlar
                width = width_abs / img_width
                height = height_abs / img_height
                x_center = (x + width_abs / 2) / img_width
                y_center = (y + height_abs / 2) / img_height
                
                area_norm = width * height
                area_abs = width_abs * height_abs
            
            else:
                continue
            
            # Geçerlilik kontrolü
            if not (0 <= x_center <= 1 and 0 <= y_center <= 1 and
                   0 < width <= 1 and 0 < height <= 1):
                continue
            
            normalized_bbox = {
                'class_name': ann.get('class_name', 'unknown'),
                'class_id': ann.get('class_id', 0),
                'x_center': x_center,
                'y_center': y_center,
                'width': width,
                'height': height,
                'area_normalized': area_norm,
                'area_absolute': area_abs,
                'aspect_ratio': width / height if height > 0 else 0,
                'image_width': ann.get('image_width', 1),
                'image_height': ann.get('image_height', 1),
                'source_format': format_type
            }
            
            normalized.append(normalized_bbox)
        
        return normalized
    
    def _generate_bbox_recommendations(self, size_analysis: Dict, 
                                     aspect_ratio_analysis: Dict,
                                     quality_assessment: Dict) -> List[str]:
        """Bounding box için öneriler oluştur"""
        recommendations = []
        
        # Kalite tabanlı öneriler
        quality_score = quality_assessment.get('quality_score', 100)
        
        if quality_score >= 90:
            recommendations.append("✅ Bounding box kalitesi mükemmel.")
        elif quality_score >= 70:
            recommendations.append("🟡 Bounding box kalitesi iyi, küçük iyileştirmeler yapılabilir.")
        else:
            recommendations.append("🔴 Bounding box kalitesi düşük, önemli iyileştirmeler gerekli.")
        
        if not recommendations:
            recommendations.append("✨ Bounding box'lar genel olarak iyi durumda.")
        
        return recommendations
    
    # Diğer metodlar (kısaltılmış hali)
    def _analyze_bbox_sizes(self, bboxes: List[Dict]) -> Dict[str, Any]:
        return {}
    
    def _analyze_aspect_ratios(self, bboxes: List[Dict]) -> Dict[str, Any]:
        return {}
    
    def _analyze_bbox_positions(self, bboxes: List[Dict]) -> Dict[str, Any]:
        return {}
    
    def _analyze_bbox_overlaps(self, bboxes: List[Dict]) -> Dict[str, Any]:
        return {}
    
    def _analyze_by_class(self, bboxes: List[Dict]) -> Dict[str, Any]:
        return {}
    
    def _assess_bbox_quality(self, bboxes: List[Dict]) -> Dict[str, Any]:
        return {'quality_score': 85}
