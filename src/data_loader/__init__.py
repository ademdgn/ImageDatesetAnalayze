#!/usr/bin/env python3
"""
Veri Yükleme Modülleri Ana Koordinatörü

Bu modül factory pattern kullanarak uygun loader'ı seçer ve ortak interface sağlar.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union
import logging

from .utils import ValidationUtils, setup_logger
from .base_loader import BaseDatasetLoader
from .yolo_loader import YOLODatasetLoader
from .validator import DatasetValidator


class DatasetLoader:
    """
    Ana veri seti yükleme sınıfı
    
    Factory pattern kullanarak uygun format loader'ını seçer ve
    tüm veri seti işlemlerini koordine eder.
    """
    
    # Desteklenen formatlar ve karşılık gelen loader sınıfları
    SUPPORTED_FORMATS = {
        'yolo': YOLODatasetLoader,
        # 'coco': COCODatasetLoader,
        # 'pascal_voc': PascalVOCDatasetLoader,
        # 'labelme': LabelMeDatasetLoader,
    }
    
    def __init__(self, dataset_path: str, annotation_format: str = 'auto', config: Dict[str, Any] = None):
        """
        DatasetLoader initialize
        
        Args:
            dataset_path (str): Veri seti ana dizini
            annotation_format (str): Annotation formatı ('auto', 'yolo', 'coco', vs) 
            config (Dict[str, Any], optional): Konfigürasyon ayarları
        """
        self.dataset_path = Path(dataset_path)
        self.annotation_format = annotation_format.lower()
        self.config = config or {}
        self.logger = setup_logger(self.__class__.__name__)
        
        # Veri yapıları
        self.loader: Optional[BaseDatasetLoader] = None
        self.validator: Optional[DatasetValidator] = None
        self.images_info: List[Dict[str, Any]] = []
        self.annotations_info: List[Dict[str, Any]] = []
        self.classes_info: Dict[int, str] = {}
        self.validation_results: Dict[str, Any] = {}
        
        # Dizin kontrolü
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Veri seti dizini bulunamadı: {dataset_path}")
        
        # Format tespiti
        if self.annotation_format == 'auto':
            self.annotation_format = self._detect_format()
            self.logger.info(f"Otomatik format tespiti: {self.annotation_format}")
        
        # Format doğrulaması
        if self.annotation_format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Desteklenmeyen format: {self.annotation_format}. "
                f"Desteklenen formatlar: {list(self.SUPPORTED_FORMATS.keys())}"
            )
        
        # Uygun loader'ı seç
        loader_class = self.SUPPORTED_FORMATS[self.annotation_format]
        self.logger.debug(f"Loader class seçiliyor: {loader_class.__name__}")
        self.loader = loader_class(str(self.dataset_path), self.config)  # config param eklendi
        self.logger.debug(f"Loader oluşturuldu: {self.loader}")
        
        # Validator'ı başlat
        self.validator = DatasetValidator(self.config)
        
        self.logger.info(f"DatasetLoader başlatıldı - Format: {self.annotation_format}, Dizin: {dataset_path}")
    
    def load_dataset(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Veri setini yükle
        
        Returns:
            Tuple[List[Dict], List[Dict]]: (images_info, annotations_info)
        """
        # Debug bilgisi
        self.logger.debug(f"load_dataset çağrıldı - self.loader: {self.loader}")
        self.logger.debug(f"self.loader type: {type(self.loader)}")
        self.logger.debug(f"self.loader is None: {self.loader is None}")
        self.logger.debug(f"bool(self.loader): {bool(self.loader)}")
        
        # self.loader object'ini kontrol et (None değil mi?)
        if self.loader is None:
            self.logger.error(f"Loader kontrolü başarısız - self.loader None!")
            raise RuntimeError("Loader başlatılmamış")
        
        try:
            self.logger.info("Veri seti yükleme başlıyor...")
            
            # Loader ile veri setini yükle
            self.images_info, self.annotations_info = self.loader.load_dataset()
            self.classes_info = self.loader.classes_info
            
            self.logger.info(f"Veri seti yüklendi - {len(self.images_info)} görüntü, {len(self.annotations_info)} annotation")
            return self.images_info, self.annotations_info
            
        except Exception as e:
            self.logger.error(f"Veri seti yükleme hatası: {str(e)}")
            raise
    
    def validate_dataset(self) -> Dict[str, Any]:
        """
        Veri setini doğrula
        
        Returns:
            Dict[str, Any]: Doğrulama sonuçları
        """
        if self.validator is None:
            raise RuntimeError("Validator başlatılmamış")
        
        if not self.images_info:
            self.logger.warning("Veri seti henüz yüklenmemiş, önce load_dataset() çağrılıyor...")
            self.load_dataset()
        
        try:
            self.logger.info("Veri seti doğrulaması başlıyor...")
            
            self.validation_results = self.validator.validate_dataset(
                self.images_info, 
                self.annotations_info, 
                self.classes_info
            )
            
            # Sonuçları logla
            score = self.validation_results['overall_score']
            is_valid = self.validation_results['is_valid']
            
            self.logger.info(f"Doğrulama tamamlandı - Skor: {score:.1f}/100, Geçerli: {is_valid}")
            
            return self.validation_results
            
        except Exception as e:
            self.logger.error(f"Doğrulama hatası: {str(e)}")
            raise
    
    def get_basic_statistics(self) -> Dict[str, Any]:
        """
        Temel istatistikleri al
        
        Returns:
            Dict[str, Any]: İstatistik sonuçları
        """
        if self.loader is None:
            raise RuntimeError("Loader başlatılmamış")
        
        if not self.images_info:
            self.load_dataset()
        
        return self.loader.get_basic_statistics()
    
    def _detect_format(self) -> str:
        """
        Veri seti formatını otomatik tespit et
        
        Returns:
            str: Tespit edilen format
        """
        self.logger.info("Format otomatik tespiti başlıyor...")
        
        # Her format için yapı kontrolü yap
        format_scores = {}
        
        for format_name in self.SUPPORTED_FORMATS.keys():
            try:
                structure_check = ValidationUtils.check_dataset_structure(
                    self.dataset_path, format_name
                )
                
                # Skor hesapla (basit heuristic)
                score = 0
                
                if structure_check['valid']:
                    score += 50
                
                # Hata sayısına göre skor azalt
                score -= len(structure_check['errors']) * 20
                score -= len(structure_check['warnings']) * 5
                
                # Format özel kontroller
                if format_name == 'yolo':
                    score += self._score_yolo_indicators()
                
                format_scores[format_name] = max(0, score)
                
            except Exception as e:
                self.logger.debug(f"Format {format_name} kontrolü başarısız: {e}")
                format_scores[format_name] = 0
        
        # En yüksek skorlu formatı seç
        if not format_scores or max(format_scores.values()) == 0:
            self.logger.warning("Hiçbir format tespit edilemedi, YOLO varsayılan olarak seçiliyor")
            return 'yolo'
        
        detected_format = max(format_scores, key=format_scores.get)
        self.logger.info(f"Format tespit edildi: {detected_format} (skor: {format_scores[detected_format]})")
        
        return detected_format
    
    def _score_yolo_indicators(self) -> int:
        """YOLO format göstergelerini skorla"""
        score = 0
        
        # Images/labels dizin yapısı
        if (self.dataset_path / 'images').exists():
            score += 20
        if (self.dataset_path / 'labels').exists():
            score += 20
        
        # Classes.txt dosyası
        class_files = ['classes.txt', 'names.txt', 'class_names.txt']
        if any((self.dataset_path / cf).exists() for cf in class_files):
            score += 15
        
        # YAML config dosyası
        yaml_files = list(self.dataset_path.glob('*.yaml')) + list(self.dataset_path.glob('*.yml'))
        if yaml_files:
            score += 10
        
        # .txt label dosyaları
        txt_files = [f for f in self.dataset_path.rglob('*.txt') 
                    if f.name not in class_files]
        if txt_files:
            score += 15
        
        return score
    
    def __len__(self) -> int:
        """Veri setindeki görüntü sayısını döndür"""
        return len(self.images_info)
    
    def __repr__(self) -> str:
        """String representation"""
        return (f"DatasetLoader("
                f"path='{self.dataset_path}', "
                f"format='{self.annotation_format}', "
                f"images={len(self.images_info)}, "
                f"annotations={len(self.annotations_info)}, "
                f"classes={len(self.classes_info)})")


# Convenience functions
def load_dataset(dataset_path: str, annotation_format: str = 'auto', config: Dict[str, Any] = None) -> DatasetLoader:
    """
    Veri seti yükleme için convenience function
    
    Args:
        dataset_path (str): Veri seti yolu
        annotation_format (str): Format ('auto', 'yolo', 'coco', vs)
        config (Dict[str, Any], optional): Konfigürasyon
        
    Returns:
        DatasetLoader: Yüklenmiş veri seti loader'ı
    """
    try:
        loader = DatasetLoader(dataset_path, annotation_format, config)
        loader.load_dataset()
        return loader
    except Exception as e:
        # Hata durumunda boş loader döndür
        print(f"Veri seti yükleme hatası: {e}")
        raise


def quick_validate(dataset_path: str, annotation_format: str = 'auto', config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Hızlı veri seti doğrulaması için convenience function
    
    Args:
        dataset_path (str): Veri seti yolu
        annotation_format (str): Format ('auto', 'yolo', 'coco', vs)
        config (Dict[str, Any], optional): Konfigürasyon
        
    Returns:
        Dict[str, Any]: Doğrulama sonuçları
    """
    try:
        loader = DatasetLoader(dataset_path, annotation_format, config)
        loader.load_dataset()  # Bu eksikti!
        return loader.validate_dataset()
    except Exception as e:
        return {
            'is_valid': False,
            'overall_score': 0.0,
            'errors': [f'Hızlı doğrulama hatası: {str(e)}'],
            'warnings': [],
            'recommendations': ['Veri seti yolunu ve formatını kontrol edin']
        }


# Module level exports
__all__ = [
    'DatasetLoader',
    'YOLODatasetLoader', 
    'DatasetValidator',
    'load_dataset',
    'quick_validate'
]
