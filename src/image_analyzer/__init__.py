#!/usr/bin/env python3
"""
Image Analyzer Modülü

Bu modül görüntü analizi için gerekli tüm sınıfları ve fonksiyonları sağlar.
"""

# Ana sınıfları import et
from .image_analyzer import ImageAnalyzer
from .base_analyzer import BaseImageAnalyzer
from .quality_metrics import QualityMetricsCalculator
from .anomaly_detector import AnomalyDetector
from .statistics_calculator import StatisticsCalculator

# Sürüm bilgisi
__version__ = "1.0.0"

# Ana export'lar
__all__ = [
    'ImageAnalyzer',
    'BaseImageAnalyzer', 
    'QualityMetricsCalculator',
    'AnomalyDetector',
    'StatisticsCalculator'
]

# Kullanım kolaylığı için ana sınıfı doğrudan erişilebilir hale getir
analyze_images = ImageAnalyzer

def create_image_analyzer(config=None):
    """
    ImageAnalyzer instance'ı oluştur
    
    Args:
        config: Konfigürasyon sözlüğü
        
    Returns:
        ImageAnalyzer instance'ı
    """
    return ImageAnalyzer(config)

def quick_image_analysis(image_paths, config=None, sample_size=50):
    """
    Hızlı görüntü analizi yap
    
    Args:
        image_paths: Görüntü dosyası yolları listesi
        config: Konfigürasyon sözlüğü
        sample_size: Analiz edilecek örnek boyutu
        
    Returns:
        Analiz sonuçları
    """
    analyzer = ImageAnalyzer(config)
    
    if len(image_paths) <= sample_size:
        return analyzer.analyze_dataset_images(image_paths)
    else:
        return analyzer.quick_analyze_sample(image_paths, sample_size)
