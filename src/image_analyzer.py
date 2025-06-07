#!/usr/bin/env python3
"""
Backward Compatibility Wrapper

Bu dosya eski main.py'nin ImageAnalyzer import'unu desteklemek için wrapper görevi görür.
"""

# Yeni modüler yapıdan ana sınıfları import et
from .image_analyzer.image_analyzer import ImageAnalyzer
from .image_analyzer.base_analyzer import BaseImageAnalyzer
from .image_analyzer.quality_metrics import QualityMetricsCalculator
from .image_analyzer.anomaly_detector import AnomalyDetector
from .image_analyzer.statistics_calculator import StatisticsCalculator
from .image_analyzer import create_image_analyzer, quick_image_analysis

# Backward compatibility için eski import'ları destekle
__all__ = [
    'ImageAnalyzer',
    'BaseImageAnalyzer', 
    'QualityMetricsCalculator',
    'AnomalyDetector',
    'StatisticsCalculator',
    'create_image_analyzer',
    'quick_image_analysis'
]
