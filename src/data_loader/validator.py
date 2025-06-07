#!/usr/bin/env python3
"""
Veri Seti Doğrulama Modülü

Bu modül veri setlerinin kalitesini ve tutarlılığını doğrular.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np
from collections import Counter, defaultdict

from .utils import CoordinateUtils, StatUtils, setup_logger


class DatasetValidator:
    """Veri seti doğrulama sınıfı"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Validator initialize
        
        Args:
            config (Dict[str, Any], optional): Doğrulama konfigürasyonu
        """
        self.config = config or {}
        self.logger = setup_logger(self.__class__.__name__)
        
        # Varsayılan eşik değerleri
        self.thresholds = {
            'min_samples_per_class': self.config.get('analysis', {}).get('min_samples_per_class', 10),
            'max_class_imbalance': self.config.get('analysis', {}).get('max_class_imbalance', 20.0),
            'min_image_size': self.config.get('analysis', {}).get('min_image_size', 32),
            'min_bbox_area': self.config.get('analysis', {}).get('min_bbox_area', 1.0)
        }
    
    def validate_dataset(self, images_info: List[Dict], annotations_info: List[Dict], 
                        classes_info: Dict[int, str]) -> Dict[str, Any]:
        """
        Kapsamlı veri seti doğrulaması
        
        Args:
            images_info (List[Dict]): Görüntü bilgileri
            annotations_info (List[Dict]): Annotation bilgileri
            classes_info (Dict[int, str]): Sınıf bilgileri
            
        Returns:
            Dict[str, Any]: Doğrulama sonuçları
        """
        self.logger.info("Kapsamlı veri seti doğrulaması başlıyor...")
        
        validation_results = {
            'is_valid': True,
            'overall_score': 0.0,
            'errors': [],
            'warnings': [],
            'recommendations': [],
            'statistics': {
                'total_images': len(images_info),
                'total_annotations': len(annotations_info),
                'total_classes': len(classes_info)
            },
            'detailed_results': {}
        }
        
        try:
            # 1. Temel yapı doğrulaması
            basic_validation = self._validate_basic_structure(images_info, annotations_info, classes_info)
            validation_results['detailed_results']['basic_structure'] = basic_validation
            
            # 2. Görüntü kalitesi doğrulaması
            image_validation = self._validate_images(images_info)
            validation_results['detailed_results']['image_quality'] = image_validation
            
            # 3. Annotation doğrulaması
            annotation_validation = self._validate_annotations(annotations_info, images_info)
            validation_results['detailed_results']['annotations'] = annotation_validation
            
            # 4. Sınıf dağılımı doğrulaması
            class_validation = self._validate_class_distribution(annotations_info, classes_info)
            validation_results['detailed_results']['class_distribution'] = class_validation
            
            # Sonuçları birleştir
            self._consolidate_validation_results(validation_results)
            
            self.logger.info(f"Veri seti doğrulaması tamamlandı - Skor: {validation_results['overall_score']:.1f}/100")
            
        except Exception as e:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Doğrulama hatası: {str(e)}")
            self.logger.error(f"Doğrulama hatası: {e}")
        
        return validation_results
    
    def _validate_basic_structure(self, images_info: List[Dict], annotations_info: List[Dict], 
                                 classes_info: Dict[int, str]) -> Dict[str, Any]:
        """Temel yapı doğrulaması"""
        result = {
            'score': 100.0,
            'issues': [],
            'stats': {}
        }
        
        # Temel kontroller
        if not images_info:
            result['issues'].append({'type': 'error', 'message': 'Hiç görüntü bulunamadı'})
            result['score'] = 0.0
            return result
        
        if not annotations_info:
            result['issues'].append({'type': 'warning', 'message': 'Hiç annotation bulunamadı'})
            result['score'] -= 30.0
        
        if not classes_info:
            result['issues'].append({'type': 'warning', 'message': 'Sınıf bilgisi bulunamadı'})
            result['score'] -= 20.0
        
        # İstatistikler
        result['stats'] = {
            'images_count': len(images_info),
            'annotations_count': len(annotations_info),
            'classes_count': len(classes_info),
            'avg_annotations_per_image': len(annotations_info) / len(images_info) if images_info else 0
        }
        
        return result
    
    def _validate_images(self, images_info: List[Dict]) -> Dict[str, Any]:
        """Görüntü kalitesi doğrulaması"""
        result = {
            'score': 100.0,
            'issues': [],
            'stats': {}
        }
        
        if not images_info:
            return result
        
        valid_images = [img for img in images_info if img.get('error') is None]
        corrupted_count = len(images_info) - len(valid_images)
        
        # Bozuk görüntü kontrolü
        if corrupted_count > 0:
            corruption_rate = corrupted_count / len(images_info)
            result['issues'].append({
                'type': 'error' if corruption_rate > 0.1 else 'warning',
                'message': f"{corrupted_count} bozuk görüntü tespit edildi ({corruption_rate*100:.1f}%)"
            })
            result['score'] -= min(corruption_rate * 100, 50.0)
        
        if not valid_images:
            result['score'] = 0.0
            return result
        
        # Görüntü boyutu analizi
        sizes = [img['width'] * img['height'] for img in valid_images]
        
        # Çok küçük görüntüler
        small_images = sum(1 for img in valid_images 
                          if img['width'] < self.thresholds['min_image_size'] or 
                             img['height'] < self.thresholds['min_image_size'])
        
        if small_images > 0:
            small_rate = small_images / len(valid_images)
            result['issues'].append({
                'type': 'warning',
                'message': f"{small_images} küçük görüntü ({small_rate*100:.1f}%) - {self.thresholds['min_image_size']}px'den küçük"
            })
            result['score'] -= min(small_rate * 50, 20.0)
        
        # İstatistikler
        result['stats'] = {
            'valid_images': len(valid_images),
            'corrupted_images': corrupted_count,
            'corruption_rate': corrupted_count / len(images_info),
            'size_stats': StatUtils.calculate_basic_stats(sizes),
            'small_images_count': small_images
        }
        
        return result
    
    def _validate_annotations(self, annotations_info: List[Dict], images_info: List[Dict]) -> Dict[str, Any]:
        """Annotation doğrulaması"""
        result = {
            'score': 100.0,
            'issues': [],
            'stats': {}
        }
        
        if not annotations_info:
            result['issues'].append({'type': 'warning', 'message': 'Hiç annotation bulunamadı'})
            result['score'] = 0.0
            return result
        
        # Image dimensions mapping
        image_dimensions = {}
        for img in images_info:
            if img.get('error') is None:
                image_dimensions[img['id']] = (img['width'], img['height'])
        
        # Annotation kalite kontrolleri
        invalid_bboxes = 0
        out_of_bounds = 0
        zero_area = 0
        
        for ann in annotations_info:
            # Bbox kontrolü
            if 'bbox' not in ann or len(ann['bbox']) < 4:
                invalid_bboxes += 1
                continue
            
            bbox = ann['bbox']
            
            # Geçerlilik kontrolü
            if not CoordinateUtils.is_valid_bbox(bbox):
                invalid_bboxes += 1
                continue
            
            # Alan hesaplama
            area = CoordinateUtils.calculate_bbox_area(bbox)
            if area <= 0:
                zero_area += 1
                continue
            
            # Görüntü sınırları kontrolü
            image_id = ann.get('image_id')
            if image_id in image_dimensions:
                img_width, img_height = image_dimensions[image_id]
                if not CoordinateUtils.is_valid_bbox(bbox, img_width, img_height):
                    out_of_bounds += 1
        
        total_annotations = len(annotations_info)
        
        # Hata oranları
        invalid_rate = invalid_bboxes / total_annotations
        out_of_bounds_rate = out_of_bounds / total_annotations
        zero_area_rate = zero_area / total_annotations
        
        # Skorlama
        if invalid_rate > 0.05:  # %5'ten fazla
            result['issues'].append({
                'type': 'error',
                'message': f"{invalid_bboxes} geçersiz bbox ({invalid_rate*100:.1f}%)"
            })
            result['score'] -= min(invalid_rate * 100, 40.0)
        
        if out_of_bounds_rate > 0.01:  # %1'den fazla
            result['issues'].append({
                'type': 'error',
                'message': f"{out_of_bounds} bbox görüntü sınırları dışında ({out_of_bounds_rate*100:.1f}%)"
            })
            result['score'] -= min(out_of_bounds_rate * 200, 30.0)
        
        if zero_area_rate > 0.01:
            result['issues'].append({
                'type': 'error',
                'message': f"{zero_area} sıfır alanlı bbox ({zero_area_rate*100:.1f}%)"
            })
            result['score'] -= min(zero_area_rate * 200, 20.0)
        
        # İstatistikler
        result['stats'] = {
            'total_annotations': total_annotations,
            'valid_annotations': total_annotations - invalid_bboxes - zero_area,
            'invalid_bboxes': invalid_bboxes,
            'out_of_bounds': out_of_bounds,
            'zero_area': zero_area,
            'quality_rates': {
                'invalid_rate': invalid_rate,
                'out_of_bounds_rate': out_of_bounds_rate,
                'zero_area_rate': zero_area_rate
            }
        }
        
        return result
    
    def _validate_class_distribution(self, annotations_info: List[Dict], classes_info: Dict[int, str]) -> Dict[str, Any]:
        """Sınıf dağılımı doğrulaması"""
        result = {
            'score': 100.0,
            'issues': [],
            'stats': {}
        }
        
        if not annotations_info or not classes_info:
            result['score'] = 0.0
            return result
        
        # Sınıf sayıları
        class_counts = Counter(ann['class_id'] for ann in annotations_info if 'class_id' in ann)
        
        if not class_counts:
            result['issues'].append({'type': 'error', 'message': 'Sınıf ID bilgisi eksik'})
            result['score'] = 0.0
            return result
        
        total_annotations = sum(class_counts.values())
        num_classes = len(class_counts)
        
        # Minimum örnek kontrolü
        classes_with_few_samples = [
            (class_id, count) for class_id, count in class_counts.items() 
            if count < self.thresholds['min_samples_per_class']
        ]
        
        if classes_with_few_samples:
            few_samples_rate = len(classes_with_few_samples) / num_classes
            result['issues'].append({
                'type': 'warning',
                'message': f"{len(classes_with_few_samples)} sınıfın {self.thresholds['min_samples_per_class']}'den az örneği var"
            })
            result['score'] -= min(few_samples_rate * 50, 25.0)
        
        # Class imbalance kontrolü
        if num_classes > 1:
            max_count = max(class_counts.values())
            min_count = min(class_counts.values())
            imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
            
            if imbalance_ratio > self.thresholds['max_class_imbalance']:
                result['issues'].append({
                    'type': 'warning',
                    'message': f"Yüksek class imbalance: {imbalance_ratio:.1f}:1"
                })
                # Logaritmik penaltı
                penalty = min(np.log10(imbalance_ratio / self.thresholds['max_class_imbalance']) * 20, 30.0)
                result['score'] -= penalty
        
        # İstatistikler
        counts_list = list(class_counts.values())
        result['stats'] = {
            'num_classes': num_classes,
            'total_annotations': total_annotations,
            'class_counts': dict(class_counts),
            'imbalance_ratio': max(counts_list) / min(counts_list) if len(counts_list) > 1 and min(counts_list) > 0 else 1.0,
            'classes_with_few_samples': len(classes_with_few_samples)
        }
        
        return result
    
    def _consolidate_validation_results(self, validation_results: Dict[str, Any]):
        """Doğrulama sonuçlarını birleştir ve genel skor hesapla"""
        detailed = validation_results['detailed_results']
        
        # Tüm hataları ve uyarıları topla
        all_errors = []
        all_warnings = []
        
        # Skorları topla (ağırlıklı ortalama)
        score_weights = {
            'basic_structure': 0.25,
            'image_quality': 0.25,
            'annotations': 0.35,
            'class_distribution': 0.15
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for category, weight in score_weights.items():
            if category in detailed:
                category_result = detailed[category]
                weighted_score += category_result['score'] * weight
                total_weight += weight
                
                # Issues'ları topla
                for issue in category_result.get('issues', []):
                    if issue['type'] == 'error':
                        all_errors.append(f"[{category.upper()}] {issue['message']}")
                    elif issue['type'] == 'warning':
                        all_warnings.append(f"[{category.upper()}] {issue['message']}")
        
        # Genel skor
        validation_results['overall_score'] = weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Genel durum
        validation_results['is_valid'] = len(all_errors) == 0 and validation_results['overall_score'] >= 60.0
        
        # Sonuçları güncelle
        validation_results['errors'] = all_errors
        validation_results['warnings'] = all_warnings
        
        # Öneriler oluştur
        validation_results['recommendations'] = self._generate_recommendations(validation_results)
    
    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """İyileştirme önerileri oluştur"""
        recommendations = []
        score = validation_results['overall_score']
        detailed = validation_results['detailed_results']
        
        # Skor bazlı genel öneriler
        if score < 60:
            recommendations.append("Veri seti kalitesi düşük - Major iyileştirmeler gerekli")
        elif score < 75:
            recommendations.append("Veri seti orta kalitede - Önemli iyileştirmeler öneriliyor")
        elif score < 90:
            recommendations.append("Veri seti iyi kalitede - Minör iyileştirmeler yapılabilir")
        
        # Kategori bazlı öneriler
        if 'annotations' in detailed and detailed['annotations']['score'] < 80:
            recommendations.append("Annotation kalitesini artırın - Geçersiz bbox'ları düzeltin")
        
        if 'class_distribution' in detailed and detailed['class_distribution']['score'] < 70:
            recommendations.append("Sınıf dağılımını dengeleyín - Az örnekli sınıfları artırın")
        
        if 'image_quality' in detailed and detailed['image_quality']['score'] < 80:
            recommendations.append("Görüntü kalitesini artırın - Bozuk görüntüleri kaldırın")
        
        return recommendations
