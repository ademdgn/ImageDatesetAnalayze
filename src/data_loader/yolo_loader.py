#!/usr/bin/env python3
"""
YOLO Format Veri Yükleme Modülü

Bu modül YOLO formatındaki veri setlerini yükler ve parse eder.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import yaml
import numpy as np
from collections import Counter

from .base_loader import BaseDatasetLoader
from .utils import FileUtils, CoordinateUtils, ConfigUtils


class YOLODatasetLoader(BaseDatasetLoader):
    """YOLO formatı için veri yükleme sınıfı"""
    
    def get_format_name(self) -> str:
        """Format adını döndür"""
        return 'yolo'
    
    def load_dataset(self) -> Tuple[List[Dict], List[Dict]]:
        """
        YOLO formatındaki veri setini yükle
        
        Returns:
            Tuple[List[Dict], List[Dict]]: (images_info, annotations_info)
        """
        self.logger.info("YOLO formatında veri seti yükleniyor...")
        
        try:
            # YOLO veri seti yapısını analiz et
            structure = self._analyze_yolo_structure()
            
            # Sınıf bilgilerini yükle
            self._load_classes()
            
            # Görüntü ve annotation'ları yükle
            images_info, annotations_info = self._load_images_and_annotations(structure)
            
            self.images_info = images_info
            self.annotations_info = annotations_info
            
            # Sınıf bilgileri eksikse annotation'lardan çıkar
            if not self.classes_info and annotations_info:
                self.classes_info = self.extract_classes_from_annotations()
                self.update_annotation_class_ids()
            
            self.logger.info(f"YOLO veri seti yüklendi - {len(images_info)} görüntü, {len(annotations_info)} annotation")
            return images_info, annotations_info
            
        except Exception as e:
            self.logger.error(f"YOLO veri seti yükleme hatası: {str(e)}")
            raise
    
    def _analyze_yolo_structure(self) -> Dict[str, Any]:
        """YOLO veri seti yapısını analiz et"""
        structure = {
            'image_dirs': [],
            'label_dirs': [],
            'has_splits': False,
            'splits': []
        }
        
        # Potansiyel görüntü dizinlerini kontrol et
        possible_image_dirs = ['images', 'imgs', 'data', 'img']
        possible_label_dirs = ['labels', 'annotations', 'ann', 'txt']
        
        # Ana dizinde görüntü dizinlerini ara
        for dir_name in possible_image_dirs:
            potential_dir = self.dataset_path / dir_name
            if potential_dir.exists():
                structure['image_dirs'].append(potential_dir)
        
        # Ana dizinde label dizinlerini ara
        for dir_name in possible_label_dirs:
            potential_dir = self.dataset_path / dir_name
            if potential_dir.exists():
                structure['label_dirs'].append(potential_dir)
        
        # Eğer hiç dizin bulunamazsa ana dizini kullan
        if not structure['image_dirs']:
            # Ana dizinde görüntü dosyası var mı kontrol et
            image_files = []
            for ext in FileUtils.SUPPORTED_IMAGE_EXTENSIONS:
                image_files.extend(self.dataset_path.glob(f'*{ext}'))
                image_files.extend(self.dataset_path.glob(f'*{ext.upper()}'))
            
            if image_files:
                structure['image_dirs'].append(self.dataset_path)
        
        if not structure['label_dirs']:
            # Ana dizinde txt dosyaları var mı kontrol et
            txt_files = [f for f in self.dataset_path.glob('*.txt') 
                        if f.name not in ['classes.txt', 'names.txt', 'class_names.txt']]
            if txt_files:
                structure['label_dirs'].append(self.dataset_path)
        
        # Train/val/test split'lerini kontrol et
        if structure['image_dirs']:
            main_image_dir = structure['image_dirs'][0]
            
            # Split dizinlerini kontrol et
            split_names = ['train', 'val', 'test', 'valid']
            for split_name in split_names:
                split_dir = main_image_dir / split_name
                if split_dir.exists():
                    structure['has_splits'] = True
                    structure['splits'].append(split_name)
        
        return structure
    
    def _load_classes(self):
        """YOLO sınıf bilgilerini yükle"""
        # Önce text dosyalarını kontrol et
        class_files = ['classes.txt', 'names.txt', 'class_names.txt', 'labels.txt']
        
        for class_file in class_files:
            class_path = self.dataset_path / class_file
            if class_path.exists():
                try:
                    classes = ConfigUtils.load_text_lines(class_path)
                    if classes:
                        self.classes_info = {i: name for i, name in enumerate(classes)}
                        self.logger.info(f"Sınıflar {class_file}'dan yüklendi: {len(classes)} sınıf")
                        return
                except Exception as e:
                    self.logger.warning(f"Sınıf dosyası okuma hatası {class_file}: {e}")
        
        # YAML config dosyalarını kontrol et
        yaml_files = FileUtils.find_files_by_pattern(self.dataset_path, '*.yaml', recursive=False)
        yaml_files.extend(FileUtils.find_files_by_pattern(self.dataset_path, '*.yml', recursive=False))
        
        for yaml_file in yaml_files:
            try:
                config = ConfigUtils.load_yaml_config(yaml_file)
                if config and 'names' in config:
                    names = config['names']
                    
                    if isinstance(names, list):
                        self.classes_info = {i: name for i, name in enumerate(names)}
                    elif isinstance(names, dict):
                        # Dict'ten int key'lere dönüştür
                        self.classes_info = {int(k): v for k, v in names.items()}
                    
                    if self.classes_info:
                        self.logger.info(f"Sınıflar {yaml_file.name}'dan yüklendi: {len(self.classes_info)} sınıf")
                        return
                        
            except Exception as e:
                self.logger.warning(f"YAML config okuma hatası {yaml_file}: {e}")
        
        self.logger.warning("Sınıf bilgisi bulunamadı, annotation'lardan çıkarılacak")
    
    def _load_images_and_annotations(self, structure: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
        """Görüntü ve annotation'ları yükle"""
        images_info = []
        annotations_info = []
        
        if not structure['image_dirs']:
            raise FileNotFoundError("YOLO veri setinde görüntü dizini bulunamadı")
        
        # Split'li yapı var mı?
        if structure['has_splits']:
            # Her split için ayrı ayrı işle
            for split_name in structure['splits']:
                split_images, split_annotations = self._load_split_data(structure, split_name)
                images_info.extend(split_images)
                annotations_info.extend(split_annotations)
        else:
            # Tek dizin yapısı
            split_images, split_annotations = self._load_split_data(structure, 'all')
            images_info.extend(split_images)
            annotations_info.extend(split_annotations)
        
        return images_info, annotations_info
    
    def _load_split_data(self, structure: Dict[str, Any], split_name: str) -> Tuple[List[Dict], List[Dict]]:
        """Belirli bir split için veri yükle"""
        images_info = []
        annotations_info = []
        
        # Görüntü dizinini belirle
        main_image_dir = structure['image_dirs'][0]
        if split_name == 'all':
            image_dir = main_image_dir
        else:
            image_dir = main_image_dir / split_name
        
        # Label dizinini belirle
        label_dir = None
        if structure['label_dirs']:
            main_label_dir = structure['label_dirs'][0]
            if split_name == 'all':
                label_dir = main_label_dir
            else:
                potential_label_dir = main_label_dir / split_name
                if potential_label_dir.exists():
                    label_dir = potential_label_dir
        
        # Görüntü dosyalarını bul
        image_files = []
        if image_dir.exists():
            for ext in FileUtils.SUPPORTED_IMAGE_EXTENSIONS:
                image_files.extend(image_dir.glob(f'*{ext}'))
                image_files.extend(image_dir.glob(f'*{ext.upper()}'))
        
        # Her görüntü için işlem yap
        for img_path in image_files:
            # Görüntü bilgilerini al
            img_info = self.get_image_info(img_path, split_name)
            images_info.append(img_info)
            
            # Karşılık gelen annotation dosyasını bul
            if label_dir:
                label_path = label_dir / f"{img_path.stem}.txt"
                if label_path.exists():
                    annotations = self._parse_yolo_annotation_file(label_path, img_info)
                    annotations_info.extend(annotations)
        
        return images_info, annotations_info
    
    def _parse_yolo_annotation_file(self, label_path: Path, img_info: Dict) -> List[Dict]:
        """YOLO annotation dosyasını parse et"""
        annotations = []
        
        try:
            lines = ConfigUtils.load_text_lines(label_path)
            
            for line_idx, line in enumerate(lines):
                if not line.strip():
                    continue
                
                try:
                    annotation = self._parse_yolo_line(line, img_info, label_path, line_idx)
                    if annotation:
                        annotations.append(annotation)
                except Exception as e:
                    self.logger.warning(f"Annotation parse hatası {label_path}:{line_idx+1}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Label dosyası okuma hatası {label_path}: {e}")
        
        return annotations
    
    def _parse_yolo_line(self, line: str, img_info: Dict, label_path: Path, line_idx: int) -> Optional[Dict]:
        """YOLO annotation satırını parse et"""
        parts = line.strip().split()
        
        if len(parts) < 5:
            return None
        
        try:
            # YOLO format: class_id x_center y_center width height [confidence]
            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])
            
            # Confidence skoru (opsiyonel)
            confidence = float(parts[5]) if len(parts) > 5 else 1.0
            
            # Mutlak koordinatlara dönüştür
            img_width = img_info['width']
            img_height = img_info['height']
            
            if img_width <= 0 or img_height <= 0:
                return None
            
            # Absolute coordinates hesapla
            bbox = CoordinateUtils.denormalize_bbox(
                [x_center, y_center, width, height],
                img_width,
                img_height
            )
            
            # Bbox geçerliliğini kontrol et
            if not CoordinateUtils.is_valid_bbox(bbox, img_width, img_height):
                return None
            
            # Sınıf adını al
            class_name = self.classes_info.get(class_id, f'class_{class_id}')
            
            # Annotation dict oluştur
            annotation = self.create_annotation_dict(
                image_id=img_info['id'],
                image_path=str(img_info['path']),
                class_id=class_id,
                class_name=class_name,
                bbox=bbox,
                additional_fields={
                    'bbox_normalized': [x_center, y_center, width, height],
                    'confidence': confidence,
                    'annotation_file': str(label_path),
                    'line_number': line_idx + 1
                }
            )
            
            return annotation
            
        except ValueError:
            return None
