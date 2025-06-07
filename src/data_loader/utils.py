#!/usr/bin/env python3
"""
Veri Yükleme Yardımcı Fonksiyonları

Bu modül tüm format loader'lar tarafından kullanılan ortak fonksiyonları içerir.
"""

import os
import json
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import logging
from PIL import Image
import numpy as np


class FileUtils:
    """Dosya işleme yardımcı sınıfı"""
    
    # Desteklenen görüntü formatları
    SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    
    @staticmethod
    def find_image_file(filename: str, search_dir: Path, case_sensitive: bool = False) -> Optional[Path]:
        """
        Görüntü dosyasını farklı dizinlerde ve uzantılarda ara
        
        Args:
            filename (str): Aranacak dosya adı
            search_dir (Path): Arama dizini
            case_sensitive (bool): Büyük/küçük harf duyarlılığı
            
        Returns:
            Optional[Path]: Bulunan dosya yolu veya None
        """
        if not search_dir.exists():
            return None
        
        # Doğrudan dosya yolu kontrol et
        direct_path = search_dir / filename
        if direct_path.exists():
            return direct_path
        
        # Büyük/küçük harf varyasyonları dene
        if not case_sensitive:
            for file in search_dir.glob('*'):
                if file.name.lower() == filename.lower():
                    return file
        
        # Farklı uzantılarla dene
        base_name = Path(filename).stem
        for ext in FileUtils.SUPPORTED_IMAGE_EXTENSIONS:
            # Normal uzantı
            test_path = search_dir / f"{base_name}{ext}"
            if test_path.exists():
                return test_path
            
            # Büyük harf uzantı
            test_path = search_dir / f"{base_name}{ext.upper()}"
            if test_path.exists():
                return test_path
        
        # Alt dizinlerde ara
        common_image_dirs = ['images', 'imgs', 'JPEGImages', 'data', 'img']
        for img_dir in common_image_dirs:
            img_subdir = search_dir / img_dir
            if img_subdir.exists():
                # Doğrudan dosya
                direct_path = img_subdir / filename
                if direct_path.exists():
                    return direct_path
                
                # Farklı uzantılarla
                for ext in FileUtils.SUPPORTED_IMAGE_EXTENSIONS:
                    test_path = img_subdir / f"{base_name}{ext}"
                    if test_path.exists():
                        return test_path
                    
                    test_path = img_subdir / f"{base_name}{ext.upper()}"
                    if test_path.exists():
                        return test_path
        
        return None
    
    @staticmethod
    def find_files_by_pattern(directory: Path, pattern: str, recursive: bool = True) -> List[Path]:
        """
        Pattern'e göre dosyaları bul
        
        Args:
            directory (Path): Arama dizini
            pattern (str): Arama pattern'i (glob pattern)
            recursive (bool): Alt dizinlerde de ara
            
        Returns:
            List[Path]: Bulunan dosyalar
        """
        if not directory.exists():
            return []
        
        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))
    
    @staticmethod
    def get_image_info(img_path: Path) -> Dict[str, Any]:
        """
        Görüntü dosyasından metadata bilgileri al
        
        Args:
            img_path (Path): Görüntü dosyası yolu
            
        Returns:
            Dict[str, Any]: Görüntü bilgileri
        """
        try:
            with Image.open(img_path) as img:
                width, height = img.size
                mode = img.mode
                format_type = img.format
            
            file_size = img_path.stat().st_size
            
            return {
                'width': width,
                'height': height,
                'channels': len(mode) if mode and mode != 'P' else 3,
                'mode': mode,
                'format': format_type,
                'file_size': file_size,
                'file_size_mb': file_size / (1024 * 1024),
                'aspect_ratio': width / height if height > 0 else 0,
                'total_pixels': width * height,
                'error': None
            }
        except Exception as e:
            return {
                'width': 0,
                'height': 0,
                'channels': 3,
                'mode': 'RGB',
                'format': None,
                'file_size': 0,
                'file_size_mb': 0,
                'aspect_ratio': 0,
                'total_pixels': 0,
                'error': str(e)
            }
    
    @staticmethod
    def is_valid_image(img_path: Path) -> bool:
        """
        Görüntü dosyasının geçerli olup olmadığını kontrol et
        
        Args:
            img_path (Path): Görüntü dosyası yolu
            
        Returns:
            bool: Geçerli ise True
        """
        try:
            with Image.open(img_path) as img:
                img.verify()  # Dosyayı doğrula
            return True
        except Exception:
            return False


class ConfigUtils:
    """Konfigürasyon dosyası işlemleri"""
    
    @staticmethod
    def load_yaml_config(file_path: Path) -> Optional[Dict[str, Any]]:
        """
        YAML konfigürasyon dosyasını yükle
        
        Args:
            file_path (Path): YAML dosyası yolu
            
        Returns:
            Optional[Dict]: Yüklenen konfigürasyon veya None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.getLogger(__name__).warning(f"YAML yükleme hatası {file_path}: {e}")
            return None
    
    @staticmethod
    def load_json_config(file_path: Path) -> Optional[Dict[str, Any]]:
        """
        JSON konfigürasyon dosyasını yükle
        
        Args:
            file_path (Path): JSON dosyası yolu
            
        Returns:
            Optional[Dict]: Yüklenen konfigürasyon veya None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.getLogger(__name__).warning(f"JSON yükleme hatası {file_path}: {e}")
            return None
    
    @staticmethod
    def load_text_lines(file_path: Path, strip_empty: bool = True) -> List[str]:
        """
        Text dosyasını satır satır yükle
        
        Args:
            file_path (Path): Text dosyası yolu
            strip_empty (bool): Boş satırları kaldır
            
        Returns:
            List[str]: Dosya satırları
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Satırları temizle
            lines = [line.strip() for line in lines]
            
            if strip_empty:
                lines = [line for line in lines if line]
            
            return lines
        except Exception as e:
            logging.getLogger(__name__).warning(f"Text dosyası yükleme hatası {file_path}: {e}")
            return []


class CoordinateUtils:
    """Koordinat dönüştürme yardımcıları"""
    
    @staticmethod
    def normalize_bbox(bbox: List[float], img_width: int, img_height: int) -> List[float]:
        """
        Mutlak koordinatları normalize et (0-1 arası)
        
        Args:
            bbox (List[float]): [x1, y1, x2, y2] formatında bbox
            img_width (int): Görüntü genişliği
            img_height (int): Görüntü yüksekliği
            
        Returns:
            List[float]: [x_center, y_center, width, height] normalize edilmiş
        """
        x1, y1, x2, y2 = bbox
        
        # YOLO formatına dönüştür (center, width, height)
        x_center = (x1 + x2) / 2.0 / img_width
        y_center = (y1 + y2) / 2.0 / img_height
        width = (x2 - x1) / img_width
        height = (y2 - y1) / img_height
        
        return [x_center, y_center, width, height]
    
    @staticmethod
    def denormalize_bbox(normalized_bbox: List[float], img_width: int, img_height: int) -> List[float]:
        """
        Normalize edilmiş koordinatları mutlak koordinatlara çevir
        
        Args:
            normalized_bbox (List[float]): [x_center, y_center, width, height] normalize
            img_width (int): Görüntü genişliği
            img_height (int): Görüntü yüksekliği
            
        Returns:
            List[float]: [x1, y1, x2, y2] mutlak koordinatlar
        """
        x_center, y_center, width, height = normalized_bbox
        
        # Mutlak koordinatları hesapla
        abs_width = width * img_width
        abs_height = height * img_height
        abs_x_center = x_center * img_width
        abs_y_center = y_center * img_height
        
        # [x1, y1, x2, y2] formatına çevir
        x1 = abs_x_center - abs_width / 2
        y1 = abs_y_center - abs_height / 2
        x2 = abs_x_center + abs_width / 2
        y2 = abs_y_center + abs_height / 2
        
        return [x1, y1, x2, y2]
    
    @staticmethod
    def convert_coco_to_standard(coco_bbox: List[float]) -> List[float]:
        """
        COCO formatından [x1, y1, x2, y2] formatına çevir
        
        Args:
            coco_bbox (List[float]): [x, y, width, height] COCO format
            
        Returns:
            List[float]: [x1, y1, x2, y2] standart format
        """
        x, y, width, height = coco_bbox
        return [x, y, x + width, y + height]
    
    @staticmethod
    def convert_standard_to_coco(bbox: List[float]) -> List[float]:
        """
        [x1, y1, x2, y2] formatından COCO formatına çevir
        
        Args:
            bbox (List[float]): [x1, y1, x2, y2] standart format
            
        Returns:
            List[float]: [x, y, width, height] COCO format
        """
        x1, y1, x2, y2 = bbox
        return [x1, y1, x2 - x1, y2 - y1]
    
    @staticmethod
    def calculate_bbox_area(bbox: List[float]) -> float:
        """
        Bounding box alanını hesapla
        
        Args:
            bbox (List[float]): [x1, y1, x2, y2] formatında bbox
            
        Returns:
            float: Bbox alanı
        """
        if len(bbox) < 4:
            return 0.0
        
        x1, y1, x2, y2 = bbox[:4]
        width = max(0, x2 - x1)
        height = max(0, y2 - y1)
        return width * height
    
    @staticmethod
    def is_valid_bbox(bbox: List[float], img_width: int = None, img_height: int = None) -> bool:
        """
        Bounding box'ın geçerli olup olmadığını kontrol et
        
        Args:
            bbox (List[float]): [x1, y1, x2, y2] formatında bbox
            img_width (int, optional): Görüntü genişliği (sınır kontrolü için)
            img_height (int, optional): Görüntü yüksekliği (sınır kontrolü için)
            
        Returns:
            bool: Geçerli ise True
        """
        if len(bbox) < 4:
            return False
        
        x1, y1, x2, y2 = bbox[:4]
        
        # Temel geçerlilik kontrolü
        if x2 <= x1 or y2 <= y1:
            return False
        
        # Negatif koordinat kontrolü
        if x1 < 0 or y1 < 0:
            return False
        
        # Görüntü sınırları kontrolü
        if img_width and img_height:
            if x2 > img_width or y2 > img_height:
                return False
        
        return True


class ValidationUtils:
    """Doğrulama yardımcıları"""
    
    @staticmethod
    def check_dataset_structure(dataset_path: Path, format_type: str) -> Dict[str, Any]:
        """
        Veri seti yapısını kontrol et
        
        Args:
            dataset_path (Path): Veri seti ana dizini
            format_type (str): Format tipi (yolo, coco, vs)
            
        Returns:
            Dict[str, Any]: Yapı kontrolü sonuçları
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'found_directories': [],
            'found_files': []
        }
        
        if not dataset_path.exists():
            result['valid'] = False
            result['errors'].append(f"Dataset dizini bulunamadı: {dataset_path}")
            return result
        
        # Dizin içeriğini listele
        for item in dataset_path.iterdir():
            if item.is_dir():
                result['found_directories'].append(item.name)
            else:
                result['found_files'].append(item.name)
        
        # Format'a özel kontroller
        if format_type == 'yolo':
            ValidationUtils._check_yolo_structure(dataset_path, result)
        elif format_type == 'coco':
            ValidationUtils._check_coco_structure(dataset_path, result)
        elif format_type == 'pascal_voc':
            ValidationUtils._check_pascal_structure(dataset_path, result)
        
        return result
    
    @staticmethod
    def _check_yolo_structure(dataset_path: Path, result: Dict):
        """YOLO yapı kontrolü"""
        # Görüntü dizinlerini ara
        image_dirs = ['images', 'imgs', 'data']
        found_image_dir = False
        
        for img_dir in image_dirs:
            if (dataset_path / img_dir).exists():
                found_image_dir = True
                break
        
        # Ana dizinde görüntü var mı kontrol et
        if not found_image_dir:
            img_files = [f for f in dataset_path.glob('*') 
                        if f.suffix.lower() in FileUtils.SUPPORTED_IMAGE_EXTENSIONS]
            if img_files:
                found_image_dir = True
        
        if not found_image_dir:
            result['warnings'].append("YOLO formatı için görüntü dizini bulunamadı")
        
        # Label dizinlerini ara
        label_dirs = ['labels', 'annotations', 'ann']
        found_label_dir = False
        
        for label_dir in label_dirs:
            if (dataset_path / label_dir).exists():
                found_label_dir = True
                break
        
        # Ana dizinde .txt dosyaları var mı
        if not found_label_dir:
            txt_files = list(dataset_path.glob('*.txt'))
            if txt_files and not any(f.name in ['classes.txt', 'names.txt'] for f in txt_files):
                found_label_dir = True
        
        if not found_label_dir:
            result['warnings'].append("YOLO formatı için label dizini bulunamadı")
        
        # Classes dosyasını kontrol et
        class_files = ['classes.txt', 'names.txt', 'class_names.txt']
        found_class_file = any((dataset_path / cf).exists() for cf in class_files)
        
        if not found_class_file:
            # YAML config kontrol et
            yaml_files = list(dataset_path.glob('*.yaml')) + list(dataset_path.glob('*.yml'))
            if not yaml_files:
                result['warnings'].append("YOLO formatı için sınıf tanım dosyası bulunamadı")
    
    @staticmethod
    def _check_coco_structure(dataset_path: Path, result: Dict):
        """COCO yapı kontrolü"""
        # JSON annotation dosyasını ara
        json_files = list(dataset_path.rglob('*.json'))
        
        if not json_files:
            result['errors'].append("COCO formatı için JSON annotation dosyası bulunamadı")
        
        # Annotations dizinini kontrol et
        if not (dataset_path / 'annotations').exists():
            result['warnings'].append("COCO formatı için 'annotations' dizini bulunamadı")
    
    @staticmethod
    def _check_pascal_structure(dataset_path: Path, result: Dict):
        """Pascal VOC yapı kontrolü"""
        # XML dosyalarını ara
        xml_files = list(dataset_path.rglob('*.xml'))
        
        if not xml_files:
            result['errors'].append("Pascal VOC formatı için XML dosyaları bulunamadı")
        
        # Standart dizinleri kontrol et
        expected_dirs = ['Annotations', 'JPEGImages']
        for exp_dir in expected_dirs:
            if not (dataset_path / exp_dir).exists():
                result['warnings'].append(f"Pascal VOC formatı için '{exp_dir}' dizini bulunamadı")


class StatUtils:
    """İstatistik hesaplama yardımcıları"""
    
    @staticmethod
    def calculate_basic_stats(values: List[Union[int, float]]) -> Dict[str, float]:
        """
        Temel istatistikleri hesapla
        
        Args:
            values (List): Sayısal değerler listesi
            
        Returns:
            Dict[str, float]: İstatistik sonuçları
        """
        if not values:
            return {
                'count': 0,
                'mean': 0,
                'median': 0,
                'std': 0,
                'min': 0,
                'max': 0,
                'sum': 0
            }
        
        values = np.array(values)
        return {
            'count': len(values),
            'mean': float(np.mean(values)),
            'median': float(np.median(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'sum': float(np.sum(values))
        }
    
    @staticmethod
    def calculate_class_imbalance_ratio(class_counts: Dict[int, int]) -> float:
        """
        Sınıf dengesizlik oranını hesapla
        
        Args:
            class_counts (Dict[int, int]): Sınıf ID -> sayı mapping
            
        Returns:
            float: İmbalance oranı (max/min)
        """
        if not class_counts or len(class_counts) < 2:
            return 1.0
        
        counts = list(class_counts.values())
        max_count = max(counts)
        min_count = min(counts)
        
        return max_count / min_count if min_count > 0 else float('inf')


# Logger yapılandırması
def setup_logger(name: str, level: str = 'INFO') -> logging.Logger:
    """
    Logger kurulumu
    
    Args:
        name (str): Logger adı
        level (str): Log seviyesi
        
    Returns:
        logging.Logger: Yapılandırılmış logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Eğer handler yoksa ekle
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
