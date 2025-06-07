#!/usr/bin/env python3
"""
Annotation Kalite Kontrol Modülü

Bu modül annotation'ların kalitesini değerlendirir ve
tutarlılık kontrolü yapar.
"""

import numpy as np
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict
import os
from pathlib import Path

class AnnotationQualityChecker:
    """Annotation kalite kontrolü yapan sınıf"""
    
    def __init__(self, config: Dict = None):
        """
        AnnotationQualityChecker sınıfını başlat
        
        Args:
            config: Konfigürasyon parametreleri
        """
        self.config = config or {}
        self.min_bbox_area = self.config.get('min_bbox_area', 100)
        self.min_annotation_iou = self.config.get('min_annotation_iou', 0.3)
        
    def check_annotation_quality(self, annotations_data: List[Dict], 
                                image_paths: List[str] = None) -> Dict[str, Any]:
        """
        Annotation kalitesini kapsamlı kontrol et
        
        Args:
            annotations_data: Parse edilmiş annotation verileri
            image_paths: Görüntü dosyası yolları (opsiyonel)
            
        Returns:
            Kalite kontrol sonuçları
        """
        if not annotations_data:
            return {'error': 'No annotation data provided'}
        
        # Kalite kontrolleri
        format_consistency = self._check_format_consistency(annotations_data)
        file_consistency = self._check_file_consistency(annotations_data, image_paths)
        bbox_validity = self._check_bbox_validity(annotations_data)
        class_consistency = self._check_class_consistency(annotations_data)
        annotation_completeness = self._check_annotation_completeness(annotations_data)
        
        # Genel kalite skoru
        overall_score = self._calculate_overall_quality_score(
            format_consistency, file_consistency, bbox_validity, 
            class_consistency, annotation_completeness
        )
        
        # Öneriler
        recommendations = self._generate_quality_recommendations(
            format_consistency, file_consistency, bbox_validity,
            class_consistency, annotation_completeness
        )
        
        return {
            'format_consistency': format_consistency,
            'file_consistency': file_consistency,
            'bbox_validity': bbox_validity,
            'class_consistency': class_consistency,
            'annotation_completeness': annotation_completeness,
            'overall_quality_score': overall_score,
            'quality_grade': self._grade_quality_score(overall_score),
            'recommendations': recommendations
        }
    
    def _check_format_consistency(self, annotations_data: List[Dict]) -> Dict[str, Any]:
        """Format tutarlılığı kontrol et"""
        formats = []
        format_errors = []
        
        for data in annotations_data:
            if data.get('parsing_failed', False):
                format_errors.append({
                    'file_path': data.get('file_path', 'unknown'),
                    'error': data.get('error', 'Unknown parsing error')
                })
                continue
            
            file_format = data.get('format', 'unknown')
            formats.append(file_format)
        
        # Format çeşitliliği
        unique_formats = set(formats)
        most_common_format = max(set(formats), key=formats.count) if formats else 'unknown'
        
        # Format tutarlılığı skoru
        if len(unique_formats) == 1:
            consistency_score = 100
        elif len(unique_formats) == 2:
            consistency_score = 80
        else:
            consistency_score = 60
        
        return {
            'total_files': len(annotations_data),
            'successful_parses': len(formats),
            'failed_parses': len(format_errors),
            'success_rate': (len(formats) / len(annotations_data)) * 100 if annotations_data else 0,
            'unique_formats': list(unique_formats),
            'most_common_format': most_common_format,
            'consistency_score': consistency_score,
            'format_errors': format_errors
        }
    
    def _check_file_consistency(self, annotations_data: List[Dict], 
                               image_paths: List[str] = None) -> Dict[str, Any]:
        """Dosya tutarlılığı kontrol et"""
        annotation_files = set()
        missing_annotations = []
        orphaned_annotations = []
        
        # Annotation dosyalarını topla
        for data in annotations_data:
            if not data.get('parsing_failed', False):
                file_path = data.get('file_path', '')
                if file_path:
                    annotation_files.add(file_path)
        
        file_consistency = {
            'total_annotation_files': len(annotation_files),
            'missing_annotations': len(missing_annotations),
            'orphaned_annotations': len(orphaned_annotations)
        }
        
        # Eğer görüntü yolları verilmişse, dosya eşleştirmesi yap
        if image_paths:
            image_files = set()
            for img_path in image_paths:
                img_path_obj = Path(img_path)
                # Annotation dosyası adını tahmin et
                possible_ann_path = img_path_obj.with_suffix('.txt')
                image_files.add(str(possible_ann_path))
            
            # Eksik annotation'ları bul
            missing_annotations = list(image_files - annotation_files)
            
            # Orphan annotation'ları bul (görüntüsü olmayan)
            orphaned_annotations = list(annotation_files - image_files)
            
            file_consistency.update({
                'total_image_files': len(image_paths),
                'missing_annotations': len(missing_annotations),
                'orphaned_annotations': len(orphaned_annotations),
                'file_match_rate': (len(annotation_files & image_files) / len(image_files)) * 100 if image_files else 0,
                'missing_annotation_files': missing_annotations[:10],  # İlk 10 tanesini göster
                'orphaned_annotation_files': orphaned_annotations[:10]
            })
        
        return file_consistency
    
    def _check_bbox_validity(self, annotations_data: List[Dict]) -> Dict[str, Any]:
        """Bounding box geçerliliği kontrol et"""
        total_bboxes = 0
        valid_bboxes = 0
        invalid_bboxes = []
        bbox_issues = {
            'negative_coordinates': 0,
            'out_of_bounds': 0,
            'zero_area': 0,
            'invalid_format': 0,
            'extreme_aspect_ratio': 0
        }
        
        for data in annotations_data:
            if data.get('parsing_failed', False):
                continue
            
            annotations = data.get('annotations', [])
            file_path = data.get('file_path', 'unknown')
            
            for i, ann in enumerate(annotations):
                total_bboxes += 1
                bbox = ann.get('bbox', [])
                format_type = ann.get('format', 'yolo')
                
                # Bbox geçerliliği kontrol et
                is_valid, issues = self._validate_single_bbox(bbox, format_type)
                
                if is_valid:
                    valid_bboxes += 1
                else:
                    invalid_bboxes.append({
                        'file_path': file_path,
                        'annotation_index': i,
                        'bbox': bbox,
                        'issues': issues
                    })
                    
                    # Issue sayılarını güncelle
                    for issue in issues:
                        if issue in bbox_issues:
                            bbox_issues[issue] += 1
        
        validity_rate = (valid_bboxes / total_bboxes) * 100 if total_bboxes > 0 else 100
        
        return {
            'total_bboxes': total_bboxes,
            'valid_bboxes': valid_bboxes,
            'invalid_bboxes': len(invalid_bboxes),
            'validity_rate': validity_rate,
            'bbox_issues': bbox_issues,
            'invalid_bbox_details': invalid_bboxes[:20]  # İlk 20 invalid bbox
        }
    
    def _validate_single_bbox(self, bbox: List[float], format_type: str) -> Tuple[bool, List[str]]:
        """Tek bir bbox'ı doğrula"""
        issues = []
        
        if len(bbox) != 4:
            issues.append('invalid_format')
            return False, issues
        
        try:
            x1, y1, x2, y2 = bbox
            
            if format_type == 'yolo':
                # YOLO format: x_center, y_center, width, height (normalized)
                x_center, y_center, width, height = x1, y1, x2, y2
                
                # Koordinat sınırları kontrol et
                if not (0 <= x_center <= 1 and 0 <= y_center <= 1):
                    issues.append('out_of_bounds')
                
                # Boyut kontrolleri
                if width <= 0 or height <= 0:
                    issues.append('zero_area')
                
                if width > 1 or height > 1:
                    issues.append('out_of_bounds')
                
                # Aspect ratio kontrol et
                if height > 0:
                    aspect_ratio = width / height
                    if aspect_ratio < 0.01 or aspect_ratio > 100:
                        issues.append('extreme_aspect_ratio')
                
            elif format_type in ['pascal_voc', 'labelme']:
                # Pascal VOC format: xmin, ymin, xmax, ymax
                xmin, ymin, xmax, ymax = x1, y1, x2, y2
                
                # Negatif koordinat kontrol et
                if xmin < 0 or ymin < 0 or xmax < 0 or ymax < 0:
                    issues.append('negative_coordinates')
                
                # Boyut kontrolleri
                if xmin >= xmax or ymin >= ymax:
                    issues.append('zero_area')
                
                # Aspect ratio kontrol et
                width = xmax - xmin
                height = ymax - ymin
                if height > 0:
                    aspect_ratio = width / height
                    if aspect_ratio < 0.01 or aspect_ratio > 100:
                        issues.append('extreme_aspect_ratio')
            
            elif format_type == 'coco':
                # COCO format: x, y, width, height
                x, y, width, height = x1, y1, x2, y2
                
                # Negatif koordinat kontrol et
                if x < 0 or y < 0:
                    issues.append('negative_coordinates')
                
                # Boyut kontrolleri
                if width <= 0 or height <= 0:
                    issues.append('zero_area')
                
                # Aspect ratio kontrol et
                if height > 0:
                    aspect_ratio = width / height
                    if aspect_ratio < 0.01 or aspect_ratio > 100:
                        issues.append('extreme_aspect_ratio')
            
        except (ValueError, TypeError):
            issues.append('invalid_format')
        
        return len(issues) == 0, issues
    
    def _check_class_consistency(self, annotations_data: List[Dict]) -> Dict[str, Any]:
        """Sınıf tutarlılığı kontrol et"""
        all_classes = set()
        class_usage = defaultdict(int)
        inconsistent_classes = []
        
        for data in annotations_data:
            if data.get('parsing_failed', False):
                continue
            
            annotations = data.get('annotations', [])
            
            for ann in annotations:
                class_name = ann.get('class_name', 'unknown')
                class_id = ann.get('class_id')
                
                all_classes.add(class_name)
                class_usage[class_name] += 1
                
                # Sınıf ID ve isim tutarlılığı kontrol et (YOLO için)
                if class_id is not None:
                    # Aynı class_id'nin farklı isimlerle kullanılıp kullanılmadığını kontrol et
                    # Bu kontrol daha karmaşık olabilir, şimdilik basit tutuyoruz
                    pass
        
        # Nadir kullanılan sınıfları tespit et
        rare_classes = [cls for cls, count in class_usage.items() if count < 5]
        
        # Class naming consistency kontrol et
        naming_issues = self._check_class_naming_consistency(list(all_classes))
        
        return {
            'total_unique_classes': len(all_classes),
            'class_usage_distribution': dict(class_usage),
            'rare_classes': rare_classes,
            'rare_class_count': len(rare_classes),
            'naming_issues': naming_issues,
            'inconsistent_classes': inconsistent_classes
        }
    
    def _check_class_naming_consistency(self, class_names: List[str]) -> Dict[str, Any]:
        """Sınıf isimlendirme tutarlılığı kontrol et"""
        issues = {
            'mixed_case': [],
            'special_characters': [],
            'whitespace_issues': [],
            'numeric_only': []
        }
        
        for class_name in class_names:
            # Mixed case kontrol et
            if class_name != class_name.lower() and class_name != class_name.upper():
                if any(c.isupper() for c in class_name) and any(c.islower() for c in class_name):
                    issues['mixed_case'].append(class_name)
            
            # Özel karakter kontrol et
            if any(not (c.isalnum() or c in ['_', '-']) for c in class_name):
                issues['special_characters'].append(class_name)
            
            # Whitespace kontrol et
            if class_name != class_name.strip() or '  ' in class_name:
                issues['whitespace_issues'].append(class_name)
            
            # Sadece sayı kontrol et
            if class_name.isdigit():
                issues['numeric_only'].append(class_name)
        
        return issues
    
    def _check_annotation_completeness(self, annotations_data: List[Dict]) -> Dict[str, Any]:
        """Annotation eksiksizliği kontrol et"""
        total_files = len(annotations_data)
        files_with_annotations = 0
        empty_files = []
        sparse_files = []  # Az annotation'ı olan dosyalar
        
        annotation_counts = []
        
        for data in annotations_data:
            if data.get('parsing_failed', False):
                empty_files.append(data.get('file_path', 'unknown'))
                continue
            
            annotations = data.get('annotations', [])
            annotation_count = len(annotations)
            annotation_counts.append(annotation_count)
            
            if annotation_count == 0:
                empty_files.append(data.get('file_path', 'unknown'))
            elif annotation_count < 3:  # 3'ten az annotation
                sparse_files.append({
                    'file_path': data.get('file_path', 'unknown'),
                    'annotation_count': annotation_count
                })
            else:
                files_with_annotations += 1
        
        # İstatistikler
        avg_annotations = np.mean(annotation_counts) if annotation_counts else 0
        median_annotations = np.median(annotation_counts) if annotation_counts else 0
        
        completeness_score = (files_with_annotations / total_files) * 100 if total_files > 0 else 100
        
        return {
            'total_files': total_files,
            'files_with_annotations': files_with_annotations,
            'empty_files': len(empty_files),
            'sparse_files': len(sparse_files),
            'completeness_score': completeness_score,
            'average_annotations_per_file': avg_annotations,
            'median_annotations_per_file': median_annotations,
            'empty_file_list': empty_files[:10],  # İlk 10 empty file
            'sparse_file_list': sparse_files[:10]  # İlk 10 sparse file
        }
    
    def _calculate_overall_quality_score(self, format_consistency: Dict,
                                       file_consistency: Dict,
                                       bbox_validity: Dict,
                                       class_consistency: Dict,
                                       annotation_completeness: Dict) -> float:
        """Genel kalite skoru hesapla (0-100)"""
        scores = []
        weights = []
        
        # Format consistency skoru (ağırlık: 0.2)
        format_score = format_consistency.get('success_rate', 0)
        scores.append(format_score)
        weights.append(0.2)
        
        # File consistency skoru (ağırlık: 0.15)
        file_score = file_consistency.get('file_match_rate', 100)
        scores.append(file_score)
        weights.append(0.15)
        
        # Bbox validity skoru (ağırlık: 0.3)
        bbox_score = bbox_validity.get('validity_rate', 0)
        scores.append(bbox_score)
        weights.append(0.3)
        
        # Class consistency skoru (ağırlık: 0.1)
        # Basit skor: nadir sınıf oranı
        total_classes = class_consistency.get('total_unique_classes', 1)
        rare_classes = class_consistency.get('rare_class_count', 0)
        class_score = max(0, (1 - rare_classes / total_classes) * 100)
        scores.append(class_score)
        weights.append(0.1)
        
        # Annotation completeness skoru (ağırlık: 0.25)
        completeness_score = annotation_completeness.get('completeness_score', 0)
        scores.append(completeness_score)
        weights.append(0.25)
        
        # Ağırlıklı ortalama
        overall_score = sum(score * weight for score, weight in zip(scores, weights))
        
        return round(overall_score, 2)
    
    def _grade_quality_score(self, score: float) -> str:
        """Kalite skorunu harf notuna dönüştür"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_quality_recommendations(self, format_consistency: Dict,
                                        file_consistency: Dict,
                                        bbox_validity: Dict,
                                        class_consistency: Dict,
                                        annotation_completeness: Dict) -> List[str]:
        """Kalite iyileştirme önerileri oluştur"""
        recommendations = []
        
        # Format consistency önerileri
        success_rate = format_consistency.get('success_rate', 100)
        if success_rate < 95:
            failed_count = format_consistency.get('failed_parses', 0)
            recommendations.append(
                f"📄 {failed_count} dosya parse edilemedi. Format tutarlılığını kontrol edin."
            )
        
        # File consistency önerileri
        missing_count = file_consistency.get('missing_annotations', 0)
        if missing_count > 0:
            recommendations.append(
                f"📂 {missing_count} görüntü için annotation dosyası eksik."
            )
        
        orphaned_count = file_consistency.get('orphaned_annotations', 0)
        if orphaned_count > 0:
            recommendations.append(
                f"🗃️ {orphaned_count} annotation dosyasının görüntüsü eksik."
            )
        
        # Bbox validity önerileri
        validity_rate = bbox_validity.get('validity_rate', 100)
        if validity_rate < 95:
            invalid_count = bbox_validity.get('invalid_bboxes', 0)
            recommendations.append(
                f"📐 {invalid_count} geçersiz bounding box tespit edildi. Annotation'ları kontrol edin."
            )
        
        # Class consistency önerileri
        rare_classes = class_consistency.get('rare_class_count', 0)
        if rare_classes > 0:
            recommendations.append(
                f"🏷️ {rare_classes} nadir kullanılan sınıf var. Bu sınıflar için daha fazla veri toplayın."
            )
        
        # Annotation completeness önerileri
        completeness_score = annotation_completeness.get('completeness_score', 100)
        if completeness_score < 90:
            empty_files = annotation_completeness.get('empty_files', 0)
            recommendations.append(
                f"📝 {empty_files} dosyada annotation eksik. Tüm görüntüleri annotate edin."
            )
        
        if not recommendations:
            recommendations.append("✅ Annotation kalitesi genel olarak iyi durumda.")
        
        return recommendations
