#!/usr/bin/env python3
"""
Temel Görüntü Analiz Sınıfı

Bu modül görüntü analizi için temel sınıf ve metodları içerir.
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageStat
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod

class BaseImageAnalyzer(ABC):
    """Görüntü analizörleri için temel sınıf"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        BaseImageAnalyzer sınıfını başlat
        
        Args:
            config: Analiz konfigürasyonu
        """
        self.config = config or {}
        self._setup_thresholds()
        
    def _setup_thresholds(self):
        """Eşik değerlerini ayarla"""
        self.blur_threshold = self.config.get('blur_threshold', 100.0)
        self.min_brightness = self.config.get('min_brightness', 30)
        self.max_brightness = self.config.get('max_brightness', 225)
        self.min_image_size = self.config.get('min_image_size', 224)
        self.max_image_size = self.config.get('max_image_size', 4096)
        
    def load_image(self, image_path: str) -> Tuple[Optional[Image.Image], Optional[np.ndarray]]:
        """
        Görüntüyü PIL ve OpenCV formatlarında yükle
        
        Args:
            image_path: Görüntü dosyası yolu
            
        Returns:
            (PIL Image, OpenCV ndarray) tuple'ı
        """
        try:
            # PIL ile yükle
            pil_image = Image.open(image_path)
            
            # OpenCV ile yükle
            cv_image = cv2.imread(image_path)
            if cv_image is None:
                raise ValueError(f"OpenCV görüntü yükleyemedi: {image_path}")
            
            return pil_image, cv_image
        
        except Exception as e:
            print(f"⚠️ Görüntü yükleme hatası {image_path}: {e}")
            return None, None
    
    def get_basic_properties(self, image_path: str, pil_image: Image.Image) -> Dict[str, Any]:
        """
        Temel görüntü özelliklerini al
        
        Args:
            image_path: Görüntü dosyası yolu
            pil_image: PIL formatında görüntü
            
        Returns:
            Temel özellikler sözlüğü
        """
        width, height = pil_image.size
        channels = len(pil_image.getbands()) if hasattr(pil_image, 'getbands') else 3
        file_size = os.path.getsize(image_path)
        path_obj = Path(image_path)
        
        return {
            'file_path': str(image_path),
            'filename': path_obj.name,
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 3),
            
            # Boyut bilgileri
            'width': width,
            'height': height,
            'channels': channels,
            'aspect_ratio': round(width / height, 3),
            'total_pixels': width * height,
            'megapixels': round((width * height) / 1_000_000, 2),
            
            # Format bilgileri
            'format': pil_image.format or "Unknown",
            'mode': pil_image.mode,
            
            # Boyut uygunluğu
            'size_appropriate': self.min_image_size <= min(width, height) <= self.max_image_size,
            'is_too_small': min(width, height) < self.min_image_size,
            'is_too_large': max(width, height) > self.max_image_size,
        }
    
    @abstractmethod
    def analyze_image_properties(self, image_path: str) -> Dict[str, Any]:
        """
        Görüntü özelliklerini analiz et (alt sınıflar tarafından implement edilmeli)
        
        Args:
            image_path: Görüntü dosyası yolu
            
        Returns:
            Analiz sonuçları sözlüğü
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
