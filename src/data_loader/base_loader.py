#!/usr/bin/env python3
"""
Temel Veri Yükleme Sınıfı

Bu modül tüm format loader'lar için ortak interface ve fonksiyonları sağlar.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import logging
import pandas as pd
import numpy as np
from collections import Counter

from .utils import FileUtils, CoordinateUtils, StatUtils, setup_logger


class BaseDatasetLoader(ABC):
    """Tüm dataset loader'lar için abstract base class"""
    
    def __init__(self, dataset_path: str, config: Dict[str, Any] = None):
        """
        Base loader initialize
        
        Args:
            dataset_path (str): Veri seti ana dizini
            config (Dict[str, Any], optional): Konfigürasyon ayarları
        """
        self.dataset_path = Path(dataset_path)
        self.config = config or {}
        self.logger = setup_logger(self.__class__.__name__)
        
        # Veri yapıları
        self.images_info: List[Dict[str, Any]] = []
        self.annotations_info: List[Dict[str, Any]] = []
        self.classes_info: Dict[int, str] = {}
        self.dataset_stats: Dict[str, Any] = {}
        
        # Dizin kontrolü
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Veri seti dizini bulunamadı: {dataset_path}")
        
        self.logger.info(f"{self.__class__.__name__} başlatıldı - Dizin: {dataset_path}")
    
    @abstractmethod
    def load_dataset(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Veri setini yükle (Alt sınıflarda implement edilmeli)
        
        Returns:
            Tuple[List[Dict], List[Dict]]: (images_info, annotations_info)
        """
        pass
    
    @abstractmethod
    def get_format_name(self) -> str:
        """
        Format adını döndür
        
        Returns:
            str: Format adı (örn: 'yolo', 'coco')
        """
        pass
    
    def get_image_info(self, img_path: Path, split: str = 'all', additional_info: Dict = None) -> Dict[str, Any]:
        """
        Görüntü bilgilerini al
        
        Args:
            img_path (Path): Görüntü dosyası yolu
            split (str): Veri seti bölümü (train/val/test)
            additional_info (Dict): Ek bilgiler
            
        Returns:
            Dict[str, Any]: Görüntü bilgileri
        """
        # Temel görüntü bilgileri
        img_info = FileUtils.get_image_info(img_path)
        
        # Standart alanları ekle
        base_info = {
            'id': img_path.stem,
            'path': img_path,
            'filename': img_path.name,
            'split': split,
            'format': self.get_format_name()
        }
        
        # Birleştir
        result = {**base_info, **img_info}
        
        # Ek bilgileri ekle
        if additional_info:
            result.update(additional_info)
        
        return result
    
    def create_annotation_dict(self, 
                             image_id: str,
                             image_path: str,
                             class_id: int,
                             class_name: str,
                             bbox: List[float],
                             additional_fields: Dict = None) -> Dict[str, Any]:
        """
        Standart annotation dict oluştur
        
        Args:
            image_id (str): Görüntü ID
            image_path (str): Görüntü dosya yolu
            class_id (int): Sınıf ID
            class_name (str): Sınıf adı
            bbox (List[float]): Bounding box [x1, y1, x2, y2]
            additional_fields (Dict): Ek alanlar
            
        Returns:
            Dict[str, Any]: Annotation bilgisi
        """
        annotation = {
            'image_id': image_id,
            'image_path': image_path,
            'class_id': class_id,
            'class_name': class_name,
            'bbox': bbox,
            'area': CoordinateUtils.calculate_bbox_area(bbox),
            'format': self.get_format_name()
        }
        
        # Ek alanları ekle
        if additional_fields:
            annotation.update(additional_fields)
        
        return annotation
    
    def get_basic_statistics(self) -> Dict[str, Any]:
        """
        Temel veri seti istatistiklerini hesapla
        
        Returns:
            Dict[str, Any]: İstatistik sonuçları
        """
        stats = {
            'total_images': len(self.images_info),
            'total_annotations': len(self.annotations_info),
            'num_classes': len(self.classes_info),
            'classes': dict(self.classes_info),
            'annotation_format': self.get_format_name(),
            'dataset_path': str(self.dataset_path)
        }
        
        return stats
    
    def get_class_distribution(self) -> pd.DataFrame:
        """
        Sınıf dağılımını DataFrame olarak döndür
        
        Returns:
            pd.DataFrame: Sınıf dağılımı
        """
        if not self.annotations_info:
            return pd.DataFrame()
        
        class_counts = Counter(ann['class_id'] for ann in self.annotations_info if 'class_id' in ann)
        
        df_data = []
        total_annotations = len(self.annotations_info)
        
        for class_id, count in class_counts.items():
            class_name = self.classes_info.get(class_id, f'class_{class_id}')
            percentage = (count / total_annotations) * 100
            
            df_data.append({
                'class_id': class_id,
                'class_name': class_name,
                'count': count,
                'percentage': percentage
            })
        
        df = pd.DataFrame(df_data)
        return df.sort_values('count', ascending=False).reset_index(drop=True)
    
    def __len__(self) -> int:
        """Veri setindeki görüntü sayısını döndür"""
        return len(self.images_info)
    
    def __repr__(self) -> str:
        """String representation"""
        return (f"{self.__class__.__name__}("
                f"path='{self.dataset_path}', "
                f"images={len(self.images_info)}, "
                f"annotations={len(self.annotations_info)}, "
                f"classes={len(self.classes_info)})")
