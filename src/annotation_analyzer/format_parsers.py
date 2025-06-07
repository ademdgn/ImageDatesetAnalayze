#!/usr/bin/env python3
"""
Annotation Format Parser'ları

Bu modül farklı annotation formatlarını parse eden sınıfları içerir.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import warnings

class YOLOParser:
    """YOLO format annotation parser"""
    
    def __init__(self, class_names: List[str] = None):
        """
        YOLO Parser başlat
        
        Args:
            class_names: Sınıf isimleri listesi
        """
        self.class_names = class_names or []
    
    def parse_annotation_file(self, annotation_path: str) -> Dict[str, Any]:
        """
        YOLO annotation dosyasını parse et
        
        Args:
            annotation_path: Annotation dosyası yolu
            
        Returns:
            Parse edilmiş annotation verisi
        """
        try:
            annotations = []
            
            with open(annotation_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split()
                if len(parts) != 5:
                    warnings.warn(f"YOLO format hatası {annotation_path}:{line_num+1} - 5 değer bekleniyor, {len(parts)} bulundu")
                    continue
                
                try:
                    class_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])
                    
                    # Koordinat sınırlarını kontrol et
                    if not (0 <= x_center <= 1 and 0 <= y_center <= 1 and
                           0 < width <= 1 and 0 < height <= 1):
                        warnings.warn(f"YOLO koordinat sınır aşımı {annotation_path}:{line_num+1}")
                        continue
                    
                    annotation = {
                        'class_id': class_id,
                        'class_name': self.get_class_name(class_id),
                        'bbox': [x_center, y_center, width, height],
                        'format': 'yolo',
                        'area': width * height,  # Normalized area
                        'line_number': line_num + 1
                    }
                    
                    annotations.append(annotation)
                    
                except ValueError as e:
                    warnings.warn(f"YOLO parse hatası {annotation_path}:{line_num+1} - {e}")
                    continue
            
            return {
                'file_path': annotation_path,
                'format': 'yolo',
                'annotations': annotations,
                'total_objects': len(annotations),
                'class_distribution': self._calculate_class_distribution(annotations),
                'parsing_errors': 0  # Bu implementasyonda error count tutmuyoruz
            }
            
        except Exception as e:
            return {
                'file_path': annotation_path,
                'format': 'yolo',
                'error': str(e),
                'parsing_failed': True
            }
    
    def get_class_name(self, class_id: int) -> str:
        """Sınıf ID'sine göre sınıf ismini al"""
        if 0 <= class_id < len(self.class_names):
            return self.class_names[class_id]
        return f"class_{class_id}"
    
    def _calculate_class_distribution(self, annotations: List[Dict]) -> Dict[str, int]:
        """Sınıf dağılımını hesapla"""
        distribution = {}
        for ann in annotations:
            class_name = ann['class_name']
            distribution[class_name] = distribution.get(class_name, 0) + 1
        return distribution


class COCOParser:
    """COCO format annotation parser"""
    
    def __init__(self):
        """COCO Parser başlat"""
        pass
    
    def parse_annotation_file(self, annotation_path: str) -> Dict[str, Any]:
        """
        COCO annotation dosyasını parse et
        
        Args:
            annotation_path: Annotation dosyası yolu
            
        Returns:
            Parse edilmiş annotation verisi
        """
        try:
            with open(annotation_path, 'r', encoding='utf-8') as f:
                coco_data = json.load(f)
            
            # COCO format kontrol
            required_keys = ['images', 'annotations', 'categories']
            for key in required_keys:
                if key not in coco_data:
                    return {
                        'file_path': annotation_path,
                        'format': 'coco',
                        'error': f"Missing required key: {key}",
                        'parsing_failed': True
                    }
            
            # Kategorileri indexle
            categories = {cat['id']: cat for cat in coco_data['categories']}
            
            # Görüntüleri indexle
            images = {img['id']: img for img in coco_data['images']}
            
            # Annotation'ları parse et
            parsed_annotations = []
            for ann in coco_data['annotations']:
                try:
                    image_info = images.get(ann['image_id'])
                    category_info = categories.get(ann['category_id'])
                    
                    if not image_info or not category_info:
                        continue
                    
                    bbox = ann['bbox']  # [x, y, width, height]
                    area = ann.get('area', bbox[2] * bbox[3])
                    
                    parsed_ann = {
                        'class_id': ann['category_id'],
                        'class_name': category_info['name'],
                        'bbox': bbox,
                        'format': 'coco',
                        'area': area,
                        'image_id': ann['image_id'],
                        'image_filename': image_info['file_name'],
                        'image_width': image_info['width'],
                        'image_height': image_info['height'],
                        'annotation_id': ann['id']
                    }
                    
                    # Opsiyonel alanlar
                    if 'iscrowd' in ann:
                        parsed_ann['is_crowd'] = ann['iscrowd']
                    if 'segmentation' in ann:
                        parsed_ann['has_segmentation'] = True
                    
                    parsed_annotations.append(parsed_ann)
                    
                except Exception as e:
                    warnings.warn(f"COCO annotation parse hatası: {e}")
                    continue
            
            return {
                'file_path': annotation_path,
                'format': 'coco',
                'annotations': parsed_annotations,
                'total_objects': len(parsed_annotations),
                'total_images': len(images),
                'total_categories': len(categories),
                'categories': categories,
                'images': images,
                'class_distribution': self._calculate_class_distribution(parsed_annotations)
            }
            
        except Exception as e:
            return {
                'file_path': annotation_path,
                'format': 'coco',
                'error': str(e),
                'parsing_failed': True
            }
    
    def _calculate_class_distribution(self, annotations: List[Dict]) -> Dict[str, int]:
        """Sınıf dağılımını hesapla"""
        distribution = {}
        for ann in annotations:
            class_name = ann['class_name']
            distribution[class_name] = distribution.get(class_name, 0) + 1
        return distribution


class PascalVOCParser:
    """Pascal VOC format annotation parser"""
    
    def __init__(self):
        """Pascal VOC Parser başlat"""
        pass
    
    def parse_annotation_file(self, annotation_path: str) -> Dict[str, Any]:
        """
        Pascal VOC annotation dosyasını parse et
        
        Args:
            annotation_path: Annotation dosyası yolu
            
        Returns:
            Parse edilmiş annotation verisi
        """
        try:
            tree = ET.parse(annotation_path)
            root = tree.getroot()
            
            # Temel görüntü bilgileri
            filename = root.find('filename')
            filename = filename.text if filename is not None else ""
            
            size_elem = root.find('size')
            if size_elem is not None:
                width = int(size_elem.find('width').text)
                height = int(size_elem.find('height').text)
                depth = int(size_elem.find('depth').text) if size_elem.find('depth') is not None else 3
            else:
                width = height = depth = 0
            
            # Object'leri parse et
            annotations = []
            objects = root.findall('object')
            
            for obj in objects:
                try:
                    # Sınıf bilgisi
                    name_elem = obj.find('name')
                    class_name = name_elem.text if name_elem is not None else "unknown"
                    
                    # Difficulty
                    difficult_elem = obj.find('difficult')
                    difficult = bool(int(difficult_elem.text)) if difficult_elem is not None else False
                    
                    # Truncated
                    truncated_elem = obj.find('truncated')
                    truncated = bool(int(truncated_elem.text)) if truncated_elem is not None else False
                    
                    # Bounding box
                    bndbox = obj.find('bndbox')
                    if bndbox is not None:
                        xmin = float(bndbox.find('xmin').text)
                        ymin = float(bndbox.find('ymin').text)
                        xmax = float(bndbox.find('xmax').text)
                        ymax = float(bndbox.find('ymax').text)
                        
                        # Area hesapla
                        area = (xmax - xmin) * (ymax - ymin)
                        
                        annotation = {
                            'class_name': class_name,
                            'bbox': [xmin, ymin, xmax, ymax],
                            'format': 'pascal_voc',
                            'area': area,
                            'difficult': difficult,
                            'truncated': truncated,
                            'image_width': width,
                            'image_height': height
                        }
                        
                        annotations.append(annotation)
                        
                except Exception as e:
                    warnings.warn(f"Pascal VOC object parse hatası: {e}")
                    continue
            
            return {
                'file_path': annotation_path,
                'format': 'pascal_voc',
                'filename': filename,
                'image_width': width,
                'image_height': height,
                'image_depth': depth,
                'annotations': annotations,
                'total_objects': len(annotations),
                'class_distribution': self._calculate_class_distribution(annotations)
            }
            
        except Exception as e:
            return {
                'file_path': annotation_path,
                'format': 'pascal_voc',
                'error': str(e),
                'parsing_failed': True
            }
    
    def _calculate_class_distribution(self, annotations: List[Dict]) -> Dict[str, int]:
        """Sınıf dağılımını hesapla"""
        distribution = {}
        for ann in annotations:
            class_name = ann['class_name']
            distribution[class_name] = distribution.get(class_name, 0) + 1
        return distribution


class LabelMeParser:
    """LabelMe format annotation parser"""
    
    def __init__(self):
        """LabelMe Parser başlat"""
        pass
    
    def parse_annotation_file(self, annotation_path: str) -> Dict[str, Any]:
        """
        LabelMe annotation dosyasını parse et
        
        Args:
            annotation_path: Annotation dosyası yolu
            
        Returns:
            Parse edilmiş annotation verisi
        """
        try:
            with open(annotation_path, 'r', encoding='utf-8') as f:
                labelme_data = json.load(f)
            
            # LabelMe format kontrol
            if 'shapes' not in labelme_data:
                return {
                    'file_path': annotation_path,
                    'format': 'labelme',
                    'error': "Missing 'shapes' key",
                    'parsing_failed': True
                }
            
            # Temel görüntü bilgileri
            image_path = labelme_data.get('imagePath', '')
            image_width = labelme_data.get('imageWidth', 0)
            image_height = labelme_data.get('imageHeight', 0)
            
            # Shape'leri parse et
            annotations = []
            for shape in labelme_data['shapes']:
                try:
                    label = shape.get('label', 'unknown')
                    shape_type = shape.get('shape_type', 'rectangle')
                    points = shape.get('points', [])
                    
                    # Sadece rectangle shape'leri destekle (bounding box için)
                    if shape_type == 'rectangle' and len(points) == 2:
                        # İki nokta: [[x1, y1], [x2, y2]]
                        x1, y1 = points[0]
                        x2, y2 = points[1]
                        
                        # Min-max koordinatlarını hesapla
                        xmin = min(x1, x2)
                        ymin = min(y1, y2)
                        xmax = max(x1, x2)
                        ymax = max(y1, y2)
                        
                        area = (xmax - xmin) * (ymax - ymin)
                        
                        annotation = {
                            'class_name': label,
                            'bbox': [xmin, ymin, xmax, ymax],
                            'format': 'labelme',
                            'area': area,
                            'shape_type': shape_type,
                            'image_width': image_width,
                            'image_height': image_height
                        }
                        
                        # Opsiyonel alanlar
                        if 'group_id' in shape:
                            annotation['group_id'] = shape['group_id']
                        if 'flags' in shape:
                            annotation['flags'] = shape['flags']
                        
                        annotations.append(annotation)
                        
                    elif shape_type == 'polygon':
                        # Polygon için bounding box hesapla
                        if len(points) >= 3:
                            x_coords = [p[0] for p in points]
                            y_coords = [p[1] for p in points]
                            
                            xmin = min(x_coords)
                            ymin = min(y_coords)
                            xmax = max(x_coords)
                            ymax = max(y_coords)
                            
                            area = (xmax - xmin) * (ymax - ymin)
                            
                            annotation = {
                                'class_name': label,
                                'bbox': [xmin, ymin, xmax, ymax],
                                'format': 'labelme',
                                'area': area,
                                'shape_type': shape_type,
                                'polygon_points': points,
                                'image_width': image_width,
                                'image_height': image_height
                            }
                            
                            annotations.append(annotation)
                        
                except Exception as e:
                    warnings.warn(f"LabelMe shape parse hatası: {e}")
                    continue
            
            return {
                'file_path': annotation_path,
                'format': 'labelme',
                'image_path': image_path,
                'image_width': image_width,
                'image_height': image_height,
                'annotations': annotations,
                'total_objects': len(annotations),
                'class_distribution': self._calculate_class_distribution(annotations)
            }
            
        except Exception as e:
            return {
                'file_path': annotation_path,
                'format': 'labelme',
                'error': str(e),
                'parsing_failed': True
            }
    
    def _calculate_class_distribution(self, annotations: List[Dict]) -> Dict[str, int]:
        """Sınıf dağılımını hesapla"""
        distribution = {}
        for ann in annotations:
            class_name = ann['class_name']
            distribution[class_name] = distribution.get(class_name, 0) + 1
        return distribution


class FormatParserFactory:
    """Annotation format parser factory"""
    
    @staticmethod
    def create_parser(format_type: str, **kwargs) -> Any:
        """
        Format tipine göre uygun parser oluştur
        
        Args:
            format_type: Annotation formatı
            **kwargs: Parser-specific parametreler
            
        Returns:
            Uygun parser instance'ı
        """
        parsers = {
            'yolo': YOLOParser,
            'coco': COCOParser,
            'pascal_voc': PascalVOCParser,
            'labelme': LabelMeParser
        }
        
        parser_class = parsers.get(format_type.lower())
        if not parser_class:
            raise ValueError(f"Desteklenmeyen format: {format_type}")
        
        # YOLO parser için class_names parametresi
        if format_type.lower() == 'yolo':
            class_names = kwargs.get('class_names', [])
            return parser_class(class_names)
        else:
            return parser_class()
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Desteklenen formatları listele"""
        return ['yolo', 'coco', 'pascal_voc', 'labelme']


def parse_annotation_file(annotation_path: str, format_type: str = 'auto', 
                         class_names: List[str] = None) -> Dict[str, Any]:
    """
    Annotation dosyasını belirtilen formatta parse et
    
    Args:
        annotation_path: Annotation dosyası yolu
        format_type: Annotation formatı ('auto' for auto-detection)
        class_names: Sınıf isimleri (YOLO format için)
        
    Returns:
        Parse edilmiş annotation verisi
    """
    try:
        # Auto-detection
        if format_type == 'auto':
            from .base_analyzer import BaseAnnotationAnalyzer
            detector = BaseAnnotationAnalyzer()
            format_type = detector.detect_annotation_format(annotation_path)
            
            if not format_type or format_type.startswith('unknown'):
                return {
                    'file_path': annotation_path,
                    'error': 'Format detection failed',
                    'parsing_failed': True
                }
        
        # Parser oluştur ve parse et
        parser = FormatParserFactory.create_parser(format_type, class_names=class_names)
        return parser.parse_annotation_file(annotation_path)
        
    except Exception as e:
        return {
            'file_path': annotation_path,
            'error': str(e),
            'parsing_failed': True
        }
