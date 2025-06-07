#!/usr/bin/env python3
"""
Backward Compatibility Wrapper

Bu dosya eski main.py'nin DatasetLoader import'unu desteklemek için wrapper görevi görür.
"""

# Yeni modüler yapıdan ana sınıfları import et
from .data_loader import DatasetLoader, load_dataset, quick_validate
from .data_loader.yolo_loader import YOLODatasetLoader
from .data_loader.validator import DatasetValidator

# Backward compatibility için eski import'ları destekle
__all__ = [
    'DatasetLoader',
    'YOLODatasetLoader',
    'DatasetValidator', 
    'load_dataset',
    'quick_validate'
]
