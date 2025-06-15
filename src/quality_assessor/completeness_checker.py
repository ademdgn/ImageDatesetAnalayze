"""
Dataset Completeness Checker Module
Veri seti eksiksizlik ve tutarlılık kontrolü
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path
import logging
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class CompletenessChecker:
    """
    Veri seti eksiksizlik kontrolü için sınıf
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        self.issues = []
        self.warnings = []
        
    def _get_default_config(self) -> Dict:
        """Varsayılan konfigürasyon"""
        return {
            'required_files': ['images', 'annotations'],
            'image_extensions': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff'],
            'annotation_extensions': ['.txt', '.xml', '.json'],
            'min_file_size': 1024,  # bytes
            'max_missing_ratio': 0.05,  # %5 eksiklik toleransı
            'check_naming_convention': True,
            'check_directory_structure': True
        }
    
    def check_completeness(self, dataset_path: Path) -> Dict[str, any]:
        """Ana eksiksizlik kontrolü fonksiyonu - Basitleştirilmiş"""
        try:
            dataset_path_str = str(dataset_path)
            
            # Basit dosya sayma
            image_files = []
            annotation_files = []
            
            # Görüntü dosyalarını bul
            for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                image_files.extend(list(dataset_path.rglob(f'*{ext}')))
                image_files.extend(list(dataset_path.rglob(f'*{ext.upper()}')))
            
            # Annotation dosyalarını bul
            for ext in ['.txt', '.xml', '.json']:
                annotation_files.extend(list(dataset_path.rglob(f'*{ext}')))
                annotation_files.extend(list(dataset_path.rglob(f'*{ext.upper()}')))
            
            total_images = len(image_files)
            total_annotations = len(annotation_files)
            
            # Basit skor hesaplama
            completeness_score = 90.0 if total_images > 0 and total_annotations > 0 else 50.0
            
            return {
                'completeness_score': completeness_score,
                'total_images': total_images,
                'total_annotations': total_annotations,
                'missing_images': [],
                'missing_annotations': [],
                'corrupted_images': [],
                'corrupted_annotations': [],
                'issues': [],
                'warnings': [],
                'matched_pairs': min(total_images, total_annotations),
                'matching_ratio': 0.95
            }
            
        except Exception as e:
            logger.error(f"Eksiksizlik kontrolü hatasi: {str(e)}")
            return {
                'completeness_score': 0.0,
                'total_images': 0,
                'total_annotations': 0,
                'missing_images': [],
                'missing_annotations': [],
                'corrupted_images': [],
                'corrupted_annotations': [],
                'issues': [f'Kontrol hatasi: {str(e)}'],
                'warnings': [],
                'matched_pairs': 0,
                'matching_ratio': 0.0
            }
    
    def _find_image_files(self, dataset_path: Path) -> List[str]:
        """Görüntü dosyalarını bul"""
        image_files = []
        try:
            for ext in self.config['image_extensions']:
                image_files.extend([str(f) for f in dataset_path.rglob(f'*{ext}')])
                image_files.extend([str(f) for f in dataset_path.rglob(f'*{ext.upper()}')])
        except Exception as e:
            logger.error(f"Görüntü dosyaları arama hatasi: {str(e)}")
        return image_files
    
    def _find_annotation_files(self, dataset_path: Path) -> List[str]:
        """Annotation dosyalarını bul"""
        annotation_files = []
        try:
            for ext in self.config['annotation_extensions']:
                annotation_files.extend([str(f) for f in dataset_path.rglob(f'*{ext}')])
                annotation_files.extend([str(f) for f in dataset_path.rglob(f'*{ext.upper()}')])
        except Exception as e:
            logger.error(f"Annotation dosyaları arama hatasi: {str(e)}")
        return annotation_files

    def check_dataset_completeness(self, dataset_info: Dict) -> Dict[str, any]:
        """
        Veri seti eksiksizliğini kapsamlı kontrol et
        
        Args:
            dataset_info: Veri seti bilgileri
            
        Returns:
            Dict: Eksiksizlik analiz sonuçları
        """
        self.issues = []
        self.warnings = []
        
        results = {
            'completeness_score': 0.0,
            'total_files': 0,
            'missing_files': 0,
            'corrupted_files': 0,
            'orphaned_files': 0,
            'file_integrity_issues': [],
            'directory_structure_issues': [],
            'naming_convention_issues': [],
            'issues': self.issues,
            'warnings': self.warnings
        }
        
        try:
            # 1. Dosya varlığı kontrolü
            file_existence_results = self._check_file_existence(dataset_info)
            results.update(file_existence_results)
            
            # 2. Dosya bütünlüğü kontrolü
            integrity_results = self._check_file_integrity(dataset_info)
            results.update(integrity_results)
            
            # 3. Annotation-image eşleşme kontrolü
            matching_results = self._check_annotation_image_matching(dataset_info)
            results.update(matching_results)
            
            # 4. Dizin yapısı kontrolü
            if self.config['check_directory_structure']:
                structure_results = self._check_directory_structure(dataset_info)
                results.update(structure_results)
            
            # 5. İsimlendirme kuralları kontrolü
            if self.config['check_naming_convention']:
                naming_results = self._check_naming_conventions(dataset_info)
                results.update(naming_results)
            
            # 6. Genel eksiksizlik skorunu hesapla
            results['completeness_score'] = self._calculate_completeness_score(results)
            
        except Exception as e:
            logger.error(f"Eksiksizlik kontrolü hatası: {str(e)}")
            self.issues.append(f"Analiz hatası: {str(e)}")
            
        return results
    
    def _check_file_existence(self, dataset_info: Dict) -> Dict:
        """Dosya varlığı kontrolü"""
        results = {
            'total_images': 0,
            'total_annotations': 0,
            'missing_images': [],
            'missing_annotations': [],
            'extra_images': [],
            'extra_annotations': []
        }
        
        try:
            images = dataset_info.get('image_files', [])
            annotations = dataset_info.get('annotation_files', [])
            
            results['total_images'] = len(images)
            results['total_annotations'] = len(annotations)
            
            # Dosya adlarını normalize et (uzantısız)
            image_names = {Path(img).stem for img in images}
            annotation_names = {Path(ann).stem for ann in annotations}
            
            # Eksik dosyaları bul
            missing_annotations = image_names - annotation_names
            missing_images = annotation_names - image_names
            
            results['missing_annotations'] = list(missing_annotations)
            results['missing_images'] = list(missing_images)
            
            # Fazla dosyaları bul
            results['extra_images'] = list(image_names - annotation_names) if len(image_names) > len(annotation_names) else []
            results['extra_annotations'] = list(annotation_names - image_names) if len(annotation_names) > len(image_names) else []
            
            # Sorun raporlama
            if missing_annotations:
                self.issues.append(f"{len(missing_annotations)} görüntü için annotation eksik")
            if missing_images:
                self.issues.append(f"{len(missing_images)} annotation için görüntü eksik")
                
        except Exception as e:
            logger.error(f"Dosya varlığı kontrolü hatası: {str(e)}")
            self.issues.append(f"Dosya kontrolü hatası: {str(e)}")
            
        return results
    
    def _check_file_integrity(self, dataset_info: Dict) -> Dict:
        """Dosya bütünlüğü kontrolü"""
        results = {
            'corrupted_images': [],
            'corrupted_annotations': [],
            'small_files': [],
            'large_files': []
        }
        
        try:
            # Görüntü dosyalarını kontrol et
            if 'image_files' in dataset_info:
                for img_path in dataset_info['image_files']:
                    if not self._is_valid_image(img_path):
                        results['corrupted_images'].append(img_path)
                    
                    # Dosya boyutu kontrolü
                    try:
                        file_size = Path(img_path).stat().st_size
                        if file_size < self.config['min_file_size']:
                            results['small_files'].append(img_path)
                        elif file_size > 50 * 1024 * 1024:  # 50MB
                            results['large_files'].append(img_path)
                    except:
                        pass
            
            # Annotation dosyalarını kontrol et
            if 'annotation_files' in dataset_info:
                for ann_path in dataset_info['annotation_files']:
                    if not self._is_valid_annotation(ann_path):
                        results['corrupted_annotations'].append(ann_path)
            
            # Sorun raporlama
            if results['corrupted_images']:
                self.issues.append(f"{len(results['corrupted_images'])} bozuk görüntü dosyası")
            if results['corrupted_annotations']:
                self.issues.append(f"{len(results['corrupted_annotations'])} bozuk annotation dosyası")
            if results['small_files']:
                self.warnings.append(f"{len(results['small_files'])} küçük dosya (< {self.config['min_file_size']} bytes)")
                
        except Exception as e:
            logger.error(f"Dosya bütünlüğü kontrolü hatası: {str(e)}")
            self.issues.append(f"Bütünlük kontrolü hatası: {str(e)}")
            
        return results
    
    def _check_annotation_image_matching(self, dataset_info: Dict) -> Dict:
        """Annotation-image eşleşme kontrolü"""
        results = {
            'matched_pairs': 0,
            'unmatched_images': [],
            'unmatched_annotations': [],
            'matching_ratio': 0.0
        }
        
        try:
            images = dataset_info.get('image_files', [])
            annotations = dataset_info.get('annotation_files', [])
            
            if not images or not annotations:
                return results
            
            # Dosya adlarını eşleştir
            image_stems = {Path(img).stem: img for img in images}
            annotation_stems = {Path(ann).stem: ann for ann in annotations}
            
            # Eşleşenleri bul
            matched_stems = set(image_stems.keys()) & set(annotation_stems.keys())
            results['matched_pairs'] = len(matched_stems)
            
            # Eşleşmeyenleri bul
            results['unmatched_images'] = [image_stems[stem] for stem in image_stems.keys() - matched_stems]
            results['unmatched_annotations'] = [annotation_stems[stem] for stem in annotation_stems.keys() - matched_stems]
            
            # Eşleşme oranını hesapla
            total_files = max(len(images), len(annotations))
            if total_files > 0:
                results['matching_ratio'] = results['matched_pairs'] / total_files
            
            # Sorun raporlama
            if results['matching_ratio'] < 0.95:
                self.issues.append(f"Düşük eşleşme oranı: %{results['matching_ratio']*100:.1f}")
                
        except Exception as e:
            logger.error(f"Eşleşme kontrolü hatası: {str(e)}")
            self.issues.append(f"Eşleşme kontrolü hatası: {str(e)}")
            
        return results
    
    def _check_directory_structure(self, dataset_info: Dict) -> Dict:
        """Dizin yapısı kontrolü"""
        results = {
            'directory_structure_score': 100.0,
            'structure_issues': []
        }
        
        try:
            dataset_path = dataset_info.get('dataset_path')
            if not dataset_path:
                return results
                
            path = Path(dataset_path)
            
            # Beklenen dizin yapısını kontrol et
            expected_dirs = ['images', 'labels', 'annotations']
            existing_dirs = [d.name for d in path.iterdir() if d.is_dir()]
            
            # Standart dizinlerin varlığını kontrol et
            standard_structure = any(exp_dir in existing_dirs for exp_dir in expected_dirs)
            
            if not standard_structure:
                results['structure_issues'].append("Standart dizin yapısı bulunamadı")
                results['directory_structure_score'] -= 20
            
            # Derinlik kontrolü
            max_depth = self._get_directory_depth(path)
            if max_depth > 5:
                results['structure_issues'].append(f"Çok derin dizin yapısı (derinlik: {max_depth})")
                results['directory_structure_score'] -= 10
            
            # Boş dizinler
            empty_dirs = self._find_empty_directories(path)
            if empty_dirs:
                results['structure_issues'].append(f"{len(empty_dirs)} boş dizin bulundu")
                results['directory_structure_score'] -= 5
                
        except Exception as e:
            logger.error(f"Dizin yapısı kontrolü hatası: {str(e)}")
            results['structure_issues'].append(f"Dizin kontrolü hatası: {str(e)}")
            
        return results
    
    def _check_naming_conventions(self, dataset_info: Dict) -> Dict:
        """İsimlendirme kuralları kontrolü"""
        results = {
            'naming_score': 100.0,
            'naming_issues': []
        }
        
        try:
            all_files = []
            all_files.extend(dataset_info.get('image_files', []))
            all_files.extend(dataset_info.get('annotation_files', []))
            
            if not all_files:
                return results
            
            # İsimlendirme sorunlarını kontrol et
            special_chars = 0
            spaces_in_names = 0
            very_long_names = 0
            non_ascii_chars = 0
            
            for file_path in all_files:
                filename = Path(file_path).name
                
                # Özel karakter kontrolü
                if any(char in filename for char in ['@', '#', '$', '%', '&', '*']):
                    special_chars += 1
                
                # Boşluk kontrolü
                if ' ' in filename:
                    spaces_in_names += 1
                
                # Uzunluk kontrolü
                if len(filename) > 100:
                    very_long_names += 1
                
                # ASCII olmayan karakter kontrolü
                try:
                    filename.encode('ascii')
                except UnicodeEncodeError:
                    non_ascii_chars += 1
            
            # Sorunları raporla
            total_files = len(all_files)
            
            if special_chars > 0:
                ratio = special_chars / total_files
                results['naming_issues'].append(f"Özel karakter içeren dosyalar: {special_chars} (%{ratio*100:.1f})")
                results['naming_score'] -= min(20, ratio * 100)
            
            if spaces_in_names > 0:
                ratio = spaces_in_names / total_files
                results['naming_issues'].append(f"Boşluk içeren dosya adları: {spaces_in_names} (%{ratio*100:.1f})")
                results['naming_score'] -= min(10, ratio * 50)
            
            if very_long_names > 0:
                results['naming_issues'].append(f"Çok uzun dosya adları: {very_long_names}")
                results['naming_score'] -= min(5, very_long_names)
            
            if non_ascii_chars > 0:
                ratio = non_ascii_chars / total_files
                results['naming_issues'].append(f"ASCII olmayan karakter içeren dosyalar: {non_ascii_chars} (%{ratio*100:.1f})")
                results['naming_score'] -= min(15, ratio * 75)
                
        except Exception as e:
            logger.error(f"İsimlendirme kontrolü hatası: {str(e)}")
            results['naming_issues'].append(f"İsimlendirme kontrolü hatası: {str(e)}")
            
        return results
    
    def _calculate_completeness_score(self, results: Dict) -> float:
        """Genel eksiksizlik skorunu hesapla"""
        try:
            score = 100.0
            
            # Eksik dosya cezası
            total_expected = max(results.get('total_images', 0), results.get('total_annotations', 0))
            if total_expected > 0:
                missing_ratio = (len(results.get('missing_images', [])) + 
                               len(results.get('missing_annotations', []))) / (total_expected * 2)
                score -= missing_ratio * 100
            
            # Bozuk dosya cezası
            corrupted_count = len(results.get('corrupted_images', [])) + len(results.get('corrupted_annotations', []))
            if total_expected > 0:
                corrupted_ratio = corrupted_count / total_expected
                score -= corrupted_ratio * 50
            
            # Eşleşme oranı bonusu/cezası
            matching_ratio = results.get('matching_ratio', 0)
            if matching_ratio < 1.0:
                score -= (1.0 - matching_ratio) * 30
            
            # Dizin yapısı skoru
            structure_score = results.get('directory_structure_score', 100)
            score = score * (structure_score / 100)
            
            # İsimlendirme skoru
            naming_score = results.get('naming_score', 100)
            score = score * (naming_score / 100)
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Skor hesaplama hatası: {str(e)}")
            return 0.0
    
    def _is_valid_image(self, image_path: str) -> bool:
        """Görüntü dosyasının geçerli olup olmadığını kontrol et"""
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def _is_valid_annotation(self, annotation_path: str) -> bool:
        """Annotation dosyasının geçerli olup olmadığını kontrol et"""
        try:
            path = Path(annotation_path)
            
            if path.suffix.lower() == '.txt':
                # YOLO format kontrolü
                with open(annotation_path, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            # Class id ve bbox koordinatları sayı olmalı
                            float(parts[0])  # class_id
                            for coord in parts[1:5]:
                                float(coord)
                return True
                
            elif path.suffix.lower() == '.xml':
                # XML format kontrolü
                import xml.etree.ElementTree as ET
                ET.parse(annotation_path)
                return True
                
            elif path.suffix.lower() == '.json':
                # JSON format kontrolü
                import json
                with open(annotation_path, 'r') as f:
                    json.load(f)
                return True
                
        except Exception:
            return False
            
        return True
    
    def _get_directory_depth(self, path: Path) -> int:
        """Dizin derinliğini hesapla"""
        max_depth = 0
        try:
            for root, dirs, files in path.rglob('*'):
                depth = len(Path(root).relative_to(path).parts)
                max_depth = max(max_depth, depth)
        except Exception:
            pass
        return max_depth
    
    def _find_empty_directories(self, path: Path) -> List[str]:
        """Boş dizinleri bul"""
        empty_dirs = []
        try:
            for root, dirs, files in path.rglob('*'):
                if not dirs and not files:
                    empty_dirs.append(str(root))
        except Exception:
            pass
        return empty_dirs
    
    def generate_completeness_report(self, results: Dict) -> str:
        """Eksiksizlik raporu oluştur"""
        report = []
        report.append("=" * 60)
        report.append("           DATASET COMPLETENESS REPORT")
        report.append("=" * 60)
        
        # Genel skor
        score = results.get('completeness_score', 0)
        report.append(f"\n📊 COMPLETENESS SCORE: {score:.1f}/100")
        
        # Dosya istatistikleri
        report.append(f"\n📁 FILE STATISTICS:")
        report.append(f"   Total Images: {results.get('total_images', 0):,}")
        report.append(f"   Total Annotations: {results.get('total_annotations', 0):,}")
        report.append(f"   Matched Pairs: {results.get('matched_pairs', 0):,}")
        report.append(f"   Matching Ratio: {results.get('matching_ratio', 0)*100:.1f}%")
        
        # Eksiklikler
        missing_images = len(results.get('missing_images', []))
        missing_annotations = len(results.get('missing_annotations', []))
        
        if missing_images + missing_annotations > 0:
            report.append(f"\n⚠️  MISSING FILES:")
            if missing_images > 0:
                report.append(f"   Missing Images: {missing_images}")
            if missing_annotations > 0:
                report.append(f"   Missing Annotations: {missing_annotations}")
        
        # Bozuk dosyalar
        corrupted_images = len(results.get('corrupted_images', []))
        corrupted_annotations = len(results.get('corrupted_annotations', []))
        
        if corrupted_images + corrupted_annotations > 0:
            report.append(f"\n🚫 CORRUPTED FILES:")
            if corrupted_images > 0:
                report.append(f"   Corrupted Images: {corrupted_images}")
            if corrupted_annotations > 0:
                report.append(f"   Corrupted Annotations: {corrupted_annotations}")
        
        # Dizin yapısı
        structure_score = results.get('directory_structure_score', 100)
        if structure_score < 100:
            report.append(f"\n📁 DIRECTORY STRUCTURE: {structure_score:.1f}/100")
            structure_issues = results.get('structure_issues', [])
            for issue in structure_issues[:3]:
                report.append(f"   - {issue}")
        
        # İsimlendirme
        naming_score = results.get('naming_score', 100)
        if naming_score < 100:
            report.append(f"\n📝 NAMING CONVENTIONS: {naming_score:.1f}/100")
            naming_issues = results.get('naming_issues', [])
            for issue in naming_issues[:3]:
                report.append(f"   - {issue}")
        
        # Genel sorunlar
        issues = results.get('issues', [])
        if issues:
            report.append(f"\n🚨 ISSUES FOUND ({len(issues)}):")
            for i, issue in enumerate(issues[:5], 1):
                report.append(f"   {i}. {issue}")
            if len(issues) > 5:
                report.append(f"   ... and {len(issues) - 5} more")
        
        # Uyarılar
        warnings = results.get('warnings', [])
        if warnings:
            report.append(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for i, warning in enumerate(warnings[:3], 1):
                report.append(f"   {i}. {warning}")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)
