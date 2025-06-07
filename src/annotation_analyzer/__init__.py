#!/usr/bin/env python3
"""
Annotation Analyzer Modülü

Bu modül annotation analizi için gerekli tüm sınıfları ve fonksiyonları sağlar.
"""

# Ana sınıfları import et
from .annotation_analyzer import AnnotationAnalyzer
from .base_analyzer import BaseAnnotationAnalyzer
from .format_parsers import (
    FormatParserFactory, 
    YOLOParser, 
    COCOParser, 
    PascalVOCParser, 
    LabelMeParser,
    parse_annotation_file
)
from .class_distribution import ClassDistributionAnalyzer
from .bbox_analyzer import BoundingBoxAnalyzer
from .quality_checker import AnnotationQualityChecker

# Sürüm bilgisi
__version__ = "1.0.0"

# Ana export'lar
__all__ = [
    'AnnotationAnalyzer',
    'BaseAnnotationAnalyzer',
    'FormatParserFactory',
    'YOLOParser',
    'COCOParser', 
    'PascalVOCParser',
    'LabelMeParser',
    'ClassDistributionAnalyzer',
    'BoundingBoxAnalyzer',
    'AnnotationQualityChecker',
    'parse_annotation_file'
]

# Kullanım kolaylığı için ana sınıfı doğrudan erişilebilir hale getir
analyze_annotations = AnnotationAnalyzer

def create_annotation_analyzer(config=None):
    """
    AnnotationAnalyzer instance'ı oluştur
    
    Args:
        config: Konfigürasyon sözlüğü
        
    Returns:
        AnnotationAnalyzer instance'ı
    """
    return AnnotationAnalyzer(config)

def quick_annotation_analysis(annotation_paths, config=None, sample_size=50):
    """
    Hızlı annotation analizi yap
    
    Args:
        annotation_paths: Annotation dosyası yolları listesi
        config: Konfigürasyon sözlüğü
        sample_size: Analiz edilecek örnek boyutu
        
    Returns:
        Analiz sonuçları
    """
    analyzer = AnnotationAnalyzer(config)
    
    if len(annotation_paths) <= sample_size:
        return analyzer.analyze_dataset_annotations(annotation_paths)
    else:
        return analyzer.quick_annotation_analysis(annotation_paths, sample_size)

def get_supported_formats():
    """
    Desteklenen annotation formatlarını listele
    
    Returns:
        Desteklenen formatlar listesi
    """
    return FormatParserFactory.get_supported_formats()
