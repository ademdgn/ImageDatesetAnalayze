"""
Config Manager Module
Konfigürasyon yönetimi
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """Konfigürasyon yönetimi sınıfı"""
    
    def __init__(self):
        self.config = {}
        self.default_config = self._get_default_config()
    
    def load_config(self, config_path: str = "config/config.yaml") -> Dict[str, Any]:
        """Konfigürasyon dosyasını yükle"""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as file:
                    self.config = yaml.safe_load(file)
                logger.info(f"Konfigürasyon yüklendi: {config_path}")
            else:
                logger.warning(f"Konfigürasyon dosyası bulunamadı: {config_path}")
                self.config = self.default_config.copy()
                
        except yaml.YAMLError as e:
            logger.error(f"Konfigürasyon dosyası okuma hatası: {e}")
            self.config = self.default_config.copy()
        except Exception as e:
            logger.error(f"Beklenmeyen konfigürasyon hatası: {e}")
            self.config = self.default_config.copy()
            
        return self.config
    
    def get_config(self) -> Dict[str, Any]:
        """Mevcut konfigürasyonu döndür"""
        return self.config
    
    def update_config(self, updates: Dict[str, Any]):
        """Konfigürasyonu güncelle"""
        self._deep_update(self.config, updates)
    
    def save_config(self, config_path: str):
        """Konfigürasyonu dosyaya kaydet"""
        try:
            config_file = Path(config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            logger.info(f"Konfigürasyon kaydedildi: {config_path}")
            
        except Exception as e:
            logger.error(f"Konfigürasyon kaydetme hatası: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Varsayılan konfigürasyon"""
        return {
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'logs/quality_assessment.log'
            },
            'analysis': {
                'min_samples_per_class': 50,
                'quality_threshold': 0.7,
                'image_size_threshold': 224,
                'max_file_size_mb': 50,
                'supported_image_formats': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff'],
                'supported_annotation_formats': ['.txt', '.xml', '.json']
            },
            'quality_scoring': {
                'weights': {
                    'image_quality': 0.25,
                    'annotation_quality': 0.25,
                    'completeness': 0.20,
                    'diversity': 0.15,
                    'consistency': 0.15
                },
                'thresholds': {
                    'excellent': 90,
                    'good': 75,
                    'fair': 60,
                    'poor': 40
                }
            },
            'output': {
                'reports_dir': 'data/output',
                'save_detailed_report': True,
                'save_summary_report': True,
                'save_csv_report': True,
                'save_recommendations': True,
                'timestamp_format': '%Y%m%d_%H%M%S'
            },
            'processing': {
                'batch_size': 100,
                'max_workers': 4,
                'memory_limit_gb': 8,
                'timeout_seconds': 300
            }
        }
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """Derin güncelleme yapısı"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get_value(self, key_path: str, default=None):
        """Noktalı yol ile değer al (örn: 'analysis.quality_threshold')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_value(self, key_path: str, value):
        """Noktalı yol ile değer ayarla"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def validate_config(self) -> tuple[bool, list]:
        """Konfigürasyonu doğrula"""
        errors = []
        
        # Gerekli anahtarları kontrol et
        required_keys = [
            'logging.level',
            'analysis.min_samples_per_class',
            'output.reports_dir'
        ]
        
        for key_path in required_keys:
            if self.get_value(key_path) is None:
                errors.append(f"Gerekli konfigürasyon anahtarı eksik: {key_path}")
        
        # Değer aralıklarını kontrol et
        threshold = self.get_value('analysis.quality_threshold', 0)
        if not 0 <= threshold <= 1:
            errors.append("analysis.quality_threshold değeri 0-1 arasında olmalı")
        
        batch_size = self.get_value('processing.batch_size', 0)
        if batch_size <= 0:
            errors.append("processing.batch_size pozitif bir sayı olmalı")
        
        return len(errors) == 0, errors
    
    def setup_logging(self):
        """Logging sistemini konfigürasyona göre kur"""
        log_config = self.config.get('logging', {})
        
        # Log dizinini oluştur
        log_file = log_config.get('file', 'logs/quality_assessment.log')
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Logging konfigürasyonu
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_file, mode='a')
            ]
        )
        
        return logging.getLogger(__name__)
