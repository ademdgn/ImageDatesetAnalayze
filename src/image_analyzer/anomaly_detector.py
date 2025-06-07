#!/usr/bin/env python3
"""
Anomali Tespit Modülü

Bu modül görüntü veri setlerindeki anormal durumları tespit eder.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class AnomalyDetector:
    """Görüntü anomalilerini tespit eden sınıf"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        AnomalyDetector sınıfını başlat
        
        Args:
            config: Anomali tespit konfigürasyonu
        """
        self.config = config or {}
        self.contamination_rate = self.config.get('contamination_rate', 0.1)
        
    def detect_quality_anomalies(self, properties_list: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Kalite tabanlı anomalileri tespit et
        
        Args:
            properties_list: Görüntü özellikleri listesi
            
        Returns:
            Anomaliler sözlüğü
        """
        anomalies = {
            'quality_issues': [],
            'size_issues': [],
            'brightness_issues': [],
            'blur_issues': []
        }
        
        if not properties_list:
            return anomalies
        
        # Kalite eşik değerleri
        quality_scores = [p.get('quality_score', 50) for p in properties_list]
        quality_threshold = np.percentile(quality_scores, 10)  # Alt %10
        
        # Boyut eşik değerleri
        min_size = self.config.get('min_image_size', 224)
        max_size = self.config.get('max_image_size', 4096)
        
        # Parlaklık eşik değerleri
        min_brightness = self.config.get('min_brightness', 30)
        max_brightness = self.config.get('max_brightness', 225)
        
        # Bulanıklık eşik değeri
        blur_threshold = self.config.get('blur_threshold', 100.0)
        
        for prop in properties_list:
            file_path = prop.get('file_path', 'Unknown')
            
            # Düşük kaliteli görüntüler
            quality_score = prop.get('quality_score', 50)
            if quality_score < quality_threshold:
                anomalies['quality_issues'].append({
                    'file_path': file_path,
                    'issue': 'Low quality score',
                    'quality_score': quality_score,
                    'threshold': quality_threshold,
                    'severity': 'high' if quality_score < quality_threshold * 0.7 else 'medium'
                })
            
            # Boyut sorunları
            width = prop.get('width', 0)
            height = prop.get('height', 0)
            min_dimension = min(width, height)
            max_dimension = max(width, height)
            
            if min_dimension < min_size:
                anomalies['size_issues'].append({
                    'file_path': file_path,
                    'issue': 'Image too small',
                    'size': f"{width}x{height}",
                    'min_dimension': min_dimension,
                    'threshold': min_size,
                    'severity': 'high' if min_dimension < min_size * 0.5 else 'medium'
                })
            
            if max_dimension > max_size:
                anomalies['size_issues'].append({
                    'file_path': file_path,
                    'issue': 'Image too large',
                    'size': f"{width}x{height}",
                    'max_dimension': max_dimension,
                    'threshold': max_size,
                    'severity': 'medium'
                })
            
            # Parlaklık sorunları
            brightness = prop.get('brightness_mean', 128)
            if brightness < min_brightness:
                anomalies['brightness_issues'].append({
                    'file_path': file_path,
                    'issue': 'Too dark',
                    'brightness': brightness,
                    'threshold': min_brightness,
                    'severity': 'high' if brightness < min_brightness * 0.7 else 'medium'
                })
            
            if brightness > max_brightness:
                anomalies['brightness_issues'].append({
                    'file_path': file_path,
                    'issue': 'Too bright',
                    'brightness': brightness,
                    'threshold': max_brightness,
                    'severity': 'high' if brightness > max_brightness * 1.1 else 'medium'
                })
            
            # Bulanık görüntüler
            blur_score = prop.get('blur_score', 0)
            if blur_score < blur_threshold:
                anomalies['blur_issues'].append({
                    'file_path': file_path,
                    'issue': 'Blurry image',
                    'blur_score': blur_score,
                    'threshold': blur_threshold,
                    'severity': 'high' if blur_score < blur_threshold * 0.5 else 'medium'
                })
        
        return anomalies
    
    def detect_statistical_outliers(self, properties_list: List[Dict]) -> List[Dict]:
        """
        İstatistiksel outlier'ları tespit et
        
        Args:
            properties_list: Görüntü özellikleri listesi
            
        Returns:
            Outlier'lar listesi
        """
        if len(properties_list) < 5:
            return []
        
        outliers = []
        
        # Z-score tabanlı outlier tespiti
        numeric_fields = [
            'width', 'height', 'aspect_ratio', 'file_size_mb',
            'brightness_mean', 'contrast_score', 'blur_score',
            'edge_density', 'color_diversity'
        ]
        
        for field in numeric_fields:
            values = [p.get(field, 0) for p in properties_list if field in p]
            if len(values) < 5:
                continue
                
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            if std_val == 0:
                continue
            
            z_threshold = self.config.get('z_score_threshold', 3.0)
            
            for i, prop in enumerate(properties_list):
                if field not in prop:
                    continue
                    
                z_score = abs((prop[field] - mean_val) / std_val)
                
                if z_score > z_threshold:
                    outliers.append({
                        'file_path': prop.get('file_path', 'Unknown'),
                        'issue': f'Statistical outlier in {field}',
                        'field': field,
                        'value': prop[field],
                        'z_score': round(z_score, 2),
                        'mean': round(mean_val, 2),
                        'std': round(std_val, 2),
                        'severity': 'high' if z_score > z_threshold * 1.5 else 'medium'
                    })
        
        return outliers
    
    def detect_feature_outliers(self, feature_vectors: List[List[float]], 
                              properties_list: List[Dict]) -> List[Dict]:
        """
        Feature vektörlerini kullanarak outlier tespit et
        
        Args:
            feature_vectors: Feature vektörleri listesi
            properties_list: Görüntü özellikleri listesi
            
        Returns:
            Feature outlier'ları listesi
        """
        try:
            from sklearn.ensemble import IsolationForest
            
            if len(feature_vectors) < 5:
                return []
            
            # Feature'ları normalize et
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(feature_vectors)
            
            # Isolation Forest kullan
            iso_forest = IsolationForest(
                contamination=self.contamination_rate, 
                random_state=42,
                n_estimators=100
            )
            outlier_labels = iso_forest.fit_predict(features_scaled)
            
            # Outlier'ları topla
            outliers = []
            for i, label in enumerate(outlier_labels):
                if label == -1 and i < len(properties_list):
                    outlier_score = iso_forest.decision_function([features_scaled[i]])[0]
                    outliers.append({
                        'file_path': properties_list[i].get('file_path', 'Unknown'),
                        'issue': 'Feature space outlier',
                        'outlier_score': round(outlier_score, 4),
                        'outlier_index': i,
                        'severity': 'medium'
                    })
            
            return outliers
            
        except ImportError:
            print("⚠️ sklearn yüklü değil, feature-based outlier detection atlanıyor")
            return []
        except Exception as e:
            print(f"⚠️ Feature outlier detection hatası: {e}")
            return []
    
    def detect_duplicate_candidates(self, properties_list: List[Dict], 
                                   similarity_threshold: float = 0.95) -> List[Dict]:
        """
        Potansiyel duplikate görüntüleri tespit et
        
        Args:
            properties_list: Görüntü özellikleri listesi
            similarity_threshold: Benzerlik eşik değeri
            
        Returns:
            Duplikate adayları listesi
        """
        duplicates = []
        
        if len(properties_list) < 2:
            return duplicates
        
        # Dosya boyutu ve çözünürlük tabanlı benzerlik kontrolü
        for i in range(len(properties_list)):
            for j in range(i + 1, len(properties_list)):
                prop1 = properties_list[i]
                prop2 = properties_list[j]
                
                # Aynı boyut ve benzer dosya boyutu
                if (prop1.get('width') == prop2.get('width') and 
                    prop1.get('height') == prop2.get('height')):
                    
                    size1 = prop1.get('file_size_bytes', 0)
                    size2 = prop2.get('file_size_bytes', 0)
                    
                    if size1 > 0 and size2 > 0:
                        size_similarity = min(size1, size2) / max(size1, size2)
                        
                        if size_similarity > similarity_threshold:
                            duplicates.append({
                                'file_path_1': prop1.get('file_path', 'Unknown'),
                                'file_path_2': prop2.get('file_path', 'Unknown'),
                                'issue': 'Potential duplicate',
                                'similarity_score': round(size_similarity, 3),
                                'size_1': size1,
                                'size_2': size2,
                                'resolution': f"{prop1.get('width')}x{prop1.get('height')}",
                                'severity': 'medium'
                            })
        
        return duplicates
    
    def detect_format_anomalies(self, properties_list: List[Dict]) -> List[Dict]:
        """
        Format anomalilerini tespit et
        
        Args:
            properties_list: Görüntü özellikleri listesi
            
        Returns:
            Format anomalileri listesi
        """
        anomalies = []
        
        if not properties_list:
            return anomalies
        
        # Format dağılımını analiz et
        formats = [p.get('format', 'Unknown') for p in properties_list]
        format_counts = {}
        for fmt in formats:
            format_counts[fmt] = format_counts.get(fmt, 0) + 1
        
        total_images = len(properties_list)
        
        # Nadir formatları tespit et
        rare_threshold = max(1, total_images * 0.05)  # %5'in altında
        
        for prop in properties_list:
            fmt = prop.get('format', 'Unknown')
            count = format_counts.get(fmt, 0)
            
            if count < rare_threshold:
                anomalies.append({
                    'file_path': prop.get('file_path', 'Unknown'),
                    'issue': 'Rare image format',
                    'format': fmt,
                    'count': count,
                    'percentage': round((count / total_images) * 100, 2),
                    'severity': 'low'
                })
        
        return anomalies
    
    def detect_all_anomalies(self, properties_list: List[Dict], 
                           feature_vectors: Optional[List[List[float]]] = None) -> Dict[str, Any]:
        """
        Tüm anomali türlerini tespit et
        
        Args:
            properties_list: Görüntü özellikleri listesi
            feature_vectors: Feature vektörleri (opsiyonel)
            
        Returns:
            Tüm anomaliler sözlüğü
        """
        print("🔍 Anomaliler tespit ediliyor...")
        
        # Kalite anomalileri
        quality_anomalies = self.detect_quality_anomalies(properties_list)
        
        # İstatistiksel outlier'lar
        statistical_outliers = self.detect_statistical_outliers(properties_list)
        
        # Feature outlier'lar (eğer feature vektörleri varsa)
        feature_outliers = []
        if feature_vectors:
            feature_outliers = self.detect_feature_outliers(feature_vectors, properties_list)
        
        # Duplikate adayları
        duplicate_candidates = self.detect_duplicate_candidates(properties_list)
        
        # Format anomalileri
        format_anomalies = self.detect_format_anomalies(properties_list)
        
        # Tüm anomalileri birleştir
        all_anomalies = {
            **quality_anomalies,
            'statistical_outliers': statistical_outliers,
            'feature_outliers': feature_outliers,
            'duplicate_candidates': duplicate_candidates,
            'format_anomalies': format_anomalies
        }
        
        # Anomali özeti
        total_anomalies = sum(len(anomaly_list) for anomaly_list in all_anomalies.values())
        
        anomaly_summary = {
            'total_anomalies': total_anomalies,
            'anomaly_rate': (total_anomalies / len(properties_list)) * 100 if properties_list else 0,
            'anomaly_types': {
                'quality_issues': len(quality_anomalies.get('quality_issues', [])),
                'size_issues': len(quality_anomalies.get('size_issues', [])),
                'brightness_issues': len(quality_anomalies.get('brightness_issues', [])),
                'blur_issues': len(quality_anomalies.get('blur_issues', [])),
                'statistical_outliers': len(statistical_outliers),
                'feature_outliers': len(feature_outliers),
                'duplicate_candidates': len(duplicate_candidates),
                'format_anomalies': len(format_anomalies)
            }
        }
        
        return {
            'anomalies': all_anomalies,
            'summary': anomaly_summary
        }
    
    def get_anomaly_severity_distribution(self, anomaly_results: Dict[str, Any]) -> Dict[str, int]:
        """
        Anomali şiddet dağılımını al
        
        Args:
            anomaly_results: Anomali tespit sonuçları
            
        Returns:
            Şiddet dağılımı sözlüğü
        """
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        
        anomalies = anomaly_results.get('anomalies', {})
        
        for anomaly_type, anomaly_list in anomalies.items():
            if isinstance(anomaly_list, list):
                for anomaly in anomaly_list:
                    severity = anomaly.get('severity', 'medium')
                    if severity in severity_counts:
                        severity_counts[severity] += 1
        
        return severity_counts
    
    def generate_anomaly_report(self, anomaly_results: Dict[str, Any]) -> List[str]:
        """
        Anomali raporu oluştur
        
        Args:
            anomaly_results: Anomali tespit sonuçları
            
        Returns:
            Rapor mesajları listesi
        """
        report = []
        
        summary = anomaly_results.get('summary', {})
        total_anomalies = summary.get('total_anomalies', 0)
        anomaly_rate = summary.get('anomaly_rate', 0)
        
        # Genel durum
        if total_anomalies == 0:
            report.append("✅ Hiç anomali tespit edilmedi. Veri seti temiz görünüyor.")
        elif anomaly_rate < 5:
            report.append(f"✅ Az sayıda anomali tespit edildi ({total_anomalies} adet, %{anomaly_rate:.1f}). Kabul edilebilir seviyede.")
        elif anomaly_rate < 15:
            report.append(f"⚠️ Orta seviyede anomali tespit edildi ({total_anomalies} adet, %{anomaly_rate:.1f}). İncelenmesi önerilir.")
        else:
            report.append(f"🔴 Yüksek seviyede anomali tespit edildi ({total_anomalies} adet, %{anomaly_rate:.1f}). Veri temizliği gerekli.")
        
        # Anomali türleri
        anomaly_types = summary.get('anomaly_types', {})
        
        for anomaly_type, count in anomaly_types.items():
            if count > 0:
                type_name = anomaly_type.replace('_', ' ').title()
                report.append(f"• {type_name}: {count} adet")
        
        # Şiddet dağılımı
        severity_dist = self.get_anomaly_severity_distribution(anomaly_results)
        if any(severity_dist.values()):
            report.append("\n📊 Şiddet Dağılımı:")
            if severity_dist['high'] > 0:
                report.append(f"🔴 Yüksek: {severity_dist['high']} adet")
            if severity_dist['medium'] > 0:
                report.append(f"🟡 Orta: {severity_dist['medium']} adet")
            if severity_dist['low'] > 0:
                report.append(f"🟢 Düşük: {severity_dist['low']} adet")
        
        return report
