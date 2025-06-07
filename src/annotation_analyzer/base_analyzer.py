#!/usr/bin/env python3
"""
Temel Annotation Analiz Sınıfı

Bu modül annotation analizi için temel sınıf ve metodları içerir.
"""

import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from abc import ABC, abstractmethod

class BaseAnnotationAnalyzer(ABC):
    """Annotation analizörleri için temel sınıf"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        BaseAnnotationAnalyzer sınıfını başlat
        
        Args:
            config: Analiz konfigürasyonu
        """
        self.config = config or {}
        self._setup_config()
        
        # Desteklenen formatlar
        self.supported_formats = ['yolo', 'coco', 'pascal_voc', 'labelme']
        
        # Sonuç depolama
        self.annotations_data = {}
        self.class_names = []
        
    def _setup_config(self):
        """Konfigürasyon ayarlarını başlat"""
        self.min_bbox_area = self.config.get('min_bbox_area', 100)
        self.max_bbox_area = self.config.get('max_bbox_area', 500000)
        self.min_samples_per_class = self.config.get('min_samples_per_class', 10)
        self.max_class_imbalance = self.config.get('max_class_imbalance', 0.8)
        
    def detect_annotation_format(self, annotation_path: str) -> Optional[str]:
        """
        Annotation dosyasının formatını otomatik tespit et
        
        Args:
            annotation_path: Annotation dosyası yolu
            
        Returns:
            Tespit edilen format string'i veya None
        """
        try:
            file_path = Path(annotation_path)
            
            if not file_path.exists():
                return None
            
            # Dosya uzantısına göre format tahmini
            if file_path.suffix.lower() == '.txt':
                return self._detect_text_format(file_path)
            elif file_path.suffix.lower() == '.xml':
                return self._detect_xml_format(file_path)
            elif file_path.suffix.lower() == '.json':
                return self._detect_json_format(file_path)
            
        except Exception as e:
            print(f"⚠️ Format tespiti hatası {annotation_path}: {e}")
            
        return None
    
    def _detect_text_format(self, file_path: Path) -> Optional[str]:
        """Text dosyasının formatını tespit et (muhtemelen YOLO)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                return None
            
            # YOLO format kontrol et
            for line in lines[:5]:  # İlk 5 satırı kontrol et
                line = line.strip()
                if line:
                    parts = line.split()
                    if len(parts) == 5:  # class_id x_center y_center width height
                        try:
                            # Tüm değerlerin numeric olduğunu kontrol et
                            class_id = int(parts[0])
                            coords = [float(x) for x in parts[1:5]]
                            # YOLO formatında koordinatlar 0-1 arasında olmalı
                            if all(0 <= coord <= 1 for coord in coords):
                                return 'yolo'
                        except ValueError:
                            continue
            
            return 'unknown_text'
            
        except Exception:
            return None
    
    def _detect_xml_format(self, file_path: Path) -> Optional[str]:
        """XML dosyasının formatını tespit et (muhtemelen Pascal VOC)"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Pascal VOC format kontrol et
            if root.tag == 'annotation':
                if root.find('object') is not None:
                    return 'pascal_voc'
            
            return 'unknown_xml'
            
        except Exception:
            return None
    
    def _detect_json_format(self, file_path: Path) -> Optional[str]:
        """JSON dosyasının formatını tespit et"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # COCO format kontrol et
            if isinstance(data, dict):
                if 'images' in data and 'annotations' in data and 'categories' in data:
                    return 'coco'
                
                # LabelMe format kontrol et
                if 'shapes' in data and 'imagePath' in data:
                    return 'labelme'
            
            return 'unknown_json'
            
        except Exception:
            return None
    
    def load_class_names(self, class_file_path: Optional[str] = None) -> List[str]:
        """
        Sınıf isimlerini yükle
        
        Args:
            class_file_path: Sınıf dosyası yolu (opsiyonel)
            
        Returns:
            Sınıf isimleri listesi
        """
        try:
            if class_file_path and Path(class_file_path).exists():
                with open(class_file_path, 'r', encoding='utf-8') as f:
                    class_names = [line.strip() for line in f.readlines() if line.strip()]
                self.class_names = class_names
                return class_names
            else:
                # Varsayılan sınıf isimleri
                self.class_names = [f"class_{i}" for i in range(100)]  # 0-99 arası
                return self.class_names
                
        except Exception as e:
            print(f"⚠️ Sınıf isimleri yükleme hatası: {e}")
            self.class_names = [f"class_{i}" for i in range(100)]
            return self.class_names
    
    def get_class_name(self, class_id: int) -> str:
        """
        Sınıf ID'sine göre sınıf ismini al
        
        Args:
            class_id: Sınıf ID'si
            
        Returns:
            Sınıf ismi
        """
        if 0 <= class_id < len(self.class_names):
            return self.class_names[class_id]
        else:
            return f"class_{class_id}"
    
    def validate_bbox(self, bbox: List[float], format_type: str = 'yolo') -> bool:
        """
        Bounding box'ın geçerliliğini kontrol et
        
        Args:
            bbox: Bounding box koordinatları
            format_type: Koordinat formatı
            
        Returns:
            Geçerlilik durumu
        """
        try:
            if len(bbox) != 4:
                return False
            
            if format_type == 'yolo':
                # YOLO: x_center, y_center, width, height (0-1 normalized)
                x_center, y_center, width, height = bbox
                return (0 <= x_center <= 1 and 0 <= y_center <= 1 and
                        0 < width <= 1 and 0 < height <= 1)
            
            elif format_type == 'pascal_voc':
                # Pascal VOC: xmin, ymin, xmax, ymax (pixel coordinates)
                xmin, ymin, xmax, ymax = bbox
                return xmin < xmax and ymin < ymax and xmin >= 0 and ymin >= 0
            
            elif format_type == 'coco':
                # COCO: x, y, width, height (pixel coordinates)
                x, y, width, height = bbox
                return x >= 0 and y >= 0 and width > 0 and height > 0
            
            return False
            
        except Exception:
            return False
    
    def convert_bbox_format(self, bbox: List[float], from_format: str, 
                          to_format: str, image_width: int = 1, 
                          image_height: int = 1) -> List[float]:
        """
        Bounding box formatını dönüştür
        
        Args:
            bbox: Kaynak bounding box
            from_format: Kaynak format
            to_format: Hedef format
            image_width: Görüntü genişliği (pixel dönüşümü için)
            image_height: Görüntü yüksekliği (pixel dönüşümü için)
            
        Returns:
            Dönüştürülmüş bounding box
        """
        try:
            if from_format == to_format:
                return bbox.copy()
            
            # Önce normalized koordinatlara dönüştür
            if from_format == 'yolo':
                # YOLO zaten normalized
                x_center, y_center, width, height = bbox
                x_min = x_center - width / 2
                y_min = y_center - height / 2
                x_max = x_center + width / 2
                y_max = y_center + height / 2
                
            elif from_format == 'pascal_voc':
                # Pascal VOC'tan normalized'a
                x_min, y_min, x_max, y_max = bbox
                x_min /= image_width
                y_min /= image_height
                x_max /= image_width
                y_max /= image_height
                
            elif from_format == 'coco':
                # COCO'dan normalized'a
                x, y, width, height = bbox
                x_min = x / image_width
                y_min = y / image_height
                x_max = (x + width) / image_width
                y_max = (y + height) / image_height
            
            # Hedef formata dönüştür
            if to_format == 'yolo':
                width = x_max - x_min
                height = y_max - y_min
                x_center = x_min + width / 2
                y_center = y_min + height / 2
                return [x_center, y_center, width, height]
                
            elif to_format == 'pascal_voc':
                return [x_min * image_width, y_min * image_height,
                       x_max * image_width, y_max * image_height]
                       
            elif to_format == 'coco':
                width = (x_max - x_min) * image_width
                height = (y_max - y_min) * image_height
                return [x_min * image_width, y_min * image_height, width, height]
            
            return bbox.copy()
            
        except Exception as e:
            print(f"⚠️ Bbox format dönüştürme hatası: {e}")
            return bbox.copy()
    
    def calculate_bbox_area(self, bbox: List[float], format_type: str = 'yolo',
                           image_width: int = 1, image_height: int = 1) -> float:
        """
        Bounding box alanını hesapla
        
        Args:
            bbox: Bounding box koordinatları
            format_type: Koordinat formatı
            image_width: Görüntü genişliği
            image_height: Görüntü yüksekliği
            
        Returns:
            Bounding box alanı
        """
        try:
            if format_type == 'yolo':
                _, _, width, height = bbox
                return width * height * image_width * image_height
            
            elif format_type == 'pascal_voc':
                xmin, ymin, xmax, ymax = bbox
                return (xmax - xmin) * (ymax - ymin)
            
            elif format_type == 'coco':
                _, _, width, height = bbox
                return width * height
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def calculate_bbox_iou(self, bbox1: List[float], bbox2: List[float],
                          format_type: str = 'yolo') -> float:
        """
        İki bounding box arasındaki IoU'yu hesapla
        
        Args:
            bbox1: İlk bounding box
            bbox2: İkinci bounding box
            format_type: Koordinat formatı
            
        Returns:
            IoU değeri (0-1 arası)
        """
        try:
            # Her iki bbox'ı da pascal_voc formatına dönüştür
            if format_type == 'yolo':
                # YOLO'dan pascal_voc'a dönüştür (normalized koordinatlar varsayarak)
                def yolo_to_pascal(bbox):
                    x_center, y_center, width, height = bbox
                    x_min = x_center - width / 2
                    y_min = y_center - height / 2
                    x_max = x_center + width / 2
                    y_max = y_center + height / 2
                    return [x_min, y_min, x_max, y_max]
                
                bbox1 = yolo_to_pascal(bbox1)
                bbox2 = yolo_to_pascal(bbox2)
            
            # IoU hesapla
            x1_min, y1_min, x1_max, y1_max = bbox1
            x2_min, y2_min, x2_max, y2_max = bbox2
            
            # Intersection alanı
            inter_x_min = max(x1_min, x2_min)
            inter_y_min = max(y1_min, y2_min)
            inter_x_max = min(x1_max, x2_max)
            inter_y_max = min(y1_max, y2_max)
            
            if inter_x_min >= inter_x_max or inter_y_min >= inter_y_max:
                return 0.0
            
            inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
            
            # Union alanı
            area1 = (x1_max - x1_min) * (y1_max - y1_min)
            area2 = (x2_max - x2_min) * (y2_max - y2_min)
            union_area = area1 + area2 - inter_area
            
            if union_area <= 0:
                return 0.0
            
            return inter_area / union_area
            
        except Exception:
            return 0.0
    
    @abstractmethod
    def load_annotations(self, annotation_path: str) -> Dict[str, Any]:
        """
        Annotation dosyasını yükle (alt sınıflar tarafından implement edilmeli)
        
        Args:
            annotation_path: Annotation dosyası yolu
            
        Returns:
            Annotation verisi sözlüğü
        """
        pass
    
    def progress_callback(self, current: int, total: int, message: str = "İşleniyor"):
        """
        İlerleme durumu callback fonksiyonu
        
        Args:
            current: Mevcut işlem sayısı
            total: Toplam işlem sayısı
            message: Gösterilecek mesaj
        """
        percentage = (current / total) * 100
        print(f"\r{message}: {current}/{total} ({percentage:.1f}%)", end="", flush=True)
        
        if current == total:
            print()  # Yeni satır
    
    def find_annotation_files(self, dataset_path: str, 
                            annotation_format: str = 'auto') -> List[str]:
        """
        Dataset dizinindeki annotation dosyalarını bul
        
        Args:
            dataset_path: Dataset ana dizini
            annotation_format: Annotation formatı ('auto' for auto-detection)
            
        Returns:
            Annotation dosyası yolları listesi
        """
        annotation_files = []
        dataset_path = Path(dataset_path)
        
        # Format-specific dosya uzantıları
        extensions = {
            'yolo': ['.txt'],
            'pascal_voc': ['.xml'],
            'coco': ['.json'],
            'labelme': ['.json'],
            'auto': ['.txt', '.xml', '.json']
        }
        
        target_extensions = extensions.get(annotation_format, ['.txt', '.xml', '.json'])
        
        # Annotation dosyalarını bul
        for ext in target_extensions:
            annotation_files.extend(dataset_path.rglob(f"*{ext}"))
        
        return [str(f) for f in annotation_files]
