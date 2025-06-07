#!/usr/bin/env python3
"""
İstatistik Hesaplayıcı Modülü

Bu modül veri seti istatistiklerini ve çeşitlilik metriklerini hesaplar.
"""

import numpy as np
from typing import Dict, List, Tuple, Any
from collections import Counter

class StatisticsCalculator:
    """Veri seti istatistiklerini hesaplayan sınıf"""
    
    def __init__(self, config: Dict = None):
        """
        StatisticsCalculator sınıfını başlat
        
        Args:
            config: Konfigürasyon parametreleri
        """
        self.config = config or {}
    
    def calculate_dataset_statistics(self, properties_list: List[Dict]) -> Dict[str, Any]:
        """
        Veri seti istatistiklerini hesapla
        
        Args:
            properties_list: Görüntü özellikleri listesi
            
        Returns:
            Veri seti istatistikleri sözlüğü
        """
        if not properties_list:
            return {}
        
        # Numerik alanları topla
        numeric_fields = [
            'width', 'height', 'aspect_ratio', 'file_size_mb', 'megapixels',
            'brightness_mean', 'contrast_score', 'blur_score', 'quality_score',
            'edge_density', 'color_diversity', 'noise_score', 'sharpness_score'
        ]
        
        stats = {}
        
        # Numerik alanlar için istatistikler
        for field in numeric_fields:
            values = [p.get(field, 0) for p in properties_list if field in p and p[field] is not None]
            if values:
                stats[field] = self._calculate_numeric_stats(values)
        
        # Boolean alanları say
        boolean_fields = [
            'is_blurry', 'is_too_dark', 'is_too_bright', 'is_too_small', 'is_too_large'
        ]
        
        for field in boolean_fields:
            values = [p.get(field, False) for p in properties_list if field in p]
            if values:                                                                                                                                       
                stats[field] = self._calculate_boolean_stats(values)
        
        # Çözünürlük analizi
        stats['resolution_analysis'] = self._analyze_resolutions(properties_list)
        
        # Format dağılımı
        stats['format_distribution'] = self._analyze_formats(properties_list)
        
        # Aspect ratio dağılımı
        stats['aspect_ratio_distribution'] = self._analyze_aspect_ratios(properties_list)
        
        # Dosya boyutu dağılımı
        stats['file_size_distribution'] = self._analyze_file_sizes(properties_list)
        
        return stats
    
    def _calculate_numeric_stats(self, values: List[float]) -> Dict[str, float]:
        """Numerik değerler için istatistik hesapla"""
        values = np.array(values)
        
        return {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'median': float(np.median(values)),
            'q25': float(np.percentile(values, 25)),
            'q75': float(np.percentile(values, 75)),
            'iqr': float(np.percentile(values, 75) - np.percentile(values, 25)),
            'cv': float(np.std(values) / (np.mean(values) + 1e-6)),  # Coefficient of variation
            'range': float(np.max(values) - np.min(values))
        }
    
    def _calculate_boolean_stats(self, values: List[bool]) -> Dict[str, Any]:
        """Boolean değerler için istatistik hesapla"""
        true_count = sum(values)
        total_count = len(values)
        
        return {
            'count': true_count,
            'total': total_count,
            'percentage': (true_count / total_count) * 100 if total_count > 0 else 0,
            'ratio': true_count / total_count if total_count > 0 else 0
        }
    
    def _analyze_resolutions(self, properties_list: List[Dict]) -> Dict[str, Any]:
        """Çözünürlük analizi yap"""
        resolutions = [(p.get('width', 0), p.get('height', 0)) for p in properties_list]
        resolution_strings = [f"{w}x{h}" for w, h in resolutions]
        
        # En yaygın çözünürlükler
        resolution_counts = Counter(resolution_strings)
        most_common = resolution_counts.most_common(10)
        
        # Çözünürlük çeşitliliği
        unique_resolutions = len(set(resolutions))
        total_images = len(properties_list)
        diversity_ratio = unique_resolutions / total_images if total_images > 0 else 0
        
        # Standart çözünürlükler
        standard_resolutions = {
            '640x480': 'VGA',
            '800x600': 'SVGA',
            '1024x768': 'XGA',
            '1280x720': 'HD',
            '1920x1080': 'Full HD',
            '2560x1440': '1440p',
            '3840x2160': '4K UHD'
        }
        
        standard_res_count = 0
        for res_str in resolution_strings:
            if res_str in standard_resolutions:
                standard_res_count += 1
        
        return {
            'unique_resolutions': unique_resolutions,
            'diversity_ratio': diversity_ratio,
            'most_common_resolutions': [
                {
                    'resolution': res,
                    'count': count,
                    'percentage': (count / total_images) * 100
                }
                for res, count in most_common
            ],
            'standard_resolution_count': standard_res_count,
            'standard_resolution_percentage': (standard_res_count / total_images) * 100 if total_images > 0 else 0
        }
    
    def _analyze_formats(self, properties_list: List[Dict]) -> Dict[str, Any]:
        """Format analizi yap"""
        formats = [p.get('format', 'Unknown') for p in properties_list]
        format_counts = Counter(formats)
        total_images = len(properties_list)
        
        format_distribution = []
        for fmt, count in format_counts.most_common():
            format_distribution.append({
                'format': fmt,
                'count': count,
                'percentage': (count / total_images) * 100
            })
        
        # Format çeşitliliği
        unique_formats = len(format_counts)
        
        return {
            'unique_formats': unique_formats,
            'distribution': format_distribution,
            'dominant_format': format_counts.most_common(1)[0] if format_counts else ('Unknown', 0)
        }
    
    def _analyze_aspect_ratios(self, properties_list: List[Dict]) -> Dict[str, Any]:
        """Aspect ratio analizi yap"""
        aspect_ratios = [p.get('aspect_ratio', 1.0) for p in properties_list if p.get('aspect_ratio')]
        
        if not aspect_ratios:
            return {}
        
        # Yaygın aspect ratio'ları kategorize et
        categories = {
            'Square (1:1)': lambda x: 0.95 <= x <= 1.05,
            'Portrait (3:4)': lambda x: 0.70 <= x <= 0.80,
            'Landscape (4:3)': lambda x: 1.25 <= x <= 1.35,
            'Widescreen (16:9)': lambda x: 1.70 <= x <= 1.85,
            'Ultra-wide (21:9)': lambda x: 2.25 <= x <= 2.40,
            'Other': lambda x: True  # Catch-all
        }
        
        category_counts = {cat: 0 for cat in categories.keys()}
        category_counts['Other'] = 0
        
        for ratio in aspect_ratios:
            categorized = False
            for category, condition in categories.items():
                if category != 'Other' and condition(ratio):
                    category_counts[category] += 1
                    categorized = True
                    break
            if not categorized:
                category_counts['Other'] += 1
        
        total_images = len(properties_list)
        
        return {
            'statistics': self._calculate_numeric_stats(aspect_ratios),
            'categories': [
                {
                    'category': category,
                    'count': count,
                    'percentage': (count / total_images) * 100
                }
                for category, count in category_counts.items()
                if count > 0
            ]
        }
    
    def _analyze_file_sizes(self, properties_list: List[Dict]) -> Dict[str, Any]:
        """Dosya boyutu analizi yap"""
        file_sizes_mb = [p.get('file_size_mb', 0) for p in properties_list if p.get('file_size_mb')]
        
        if not file_sizes_mb:
            return {}
        
        # Boyut kategorileri
        categories = {
            'Very Small (<0.1 MB)': lambda x: x < 0.1,
            'Small (0.1-0.5 MB)': lambda x: 0.1 <= x < 0.5,
            'Medium (0.5-2 MB)': lambda x: 0.5 <= x < 2.0,
            'Large (2-5 MB)': lambda x: 2.0 <= x < 5.0,
            'Very Large (5-10 MB)': lambda x: 5.0 <= x < 10.0,
            'Huge (>10 MB)': lambda x: x >= 10.0
        }
        
        category_counts = {cat: 0 for cat in categories.keys()}
        
        for size in file_sizes_mb:
            for category, condition in categories.items():
                if condition(size):
                    category_counts[category] += 1
                    break
        
        total_images = len(properties_list)
        total_size_mb = sum(file_sizes_mb)
        
        return {
            'statistics': self._calculate_numeric_stats(file_sizes_mb),
            'total_size_mb': total_size_mb,
            'total_size_gb': total_size_mb / 1024,
            'average_size_mb': total_size_mb / len(file_sizes_mb),
            'categories': [
                {
                    'category': category,
                    'count': count,
                    'percentage': (count / total_images) * 100
                }
                for category, count in category_counts.items()
                if count > 0
            ]
        }
    
    def calculate_diversity_metrics(self, properties_list: List[Dict]) -> Dict[str, float]:
        """
        Veri seti çeşitlilik metriklerini hesapla
        
        Args:
            properties_list: Görüntü özellikleri listesi
            
        Returns:
            Çeşitlilik metrikleri sözlüğü
        """
        if not properties_list:
            return {}
        
        metrics = {}
        
        # Çözünürlük çeşitliliği
        resolutions = set((p.get('width', 0), p.get('height', 0)) for p in properties_list)
        metrics['resolution_diversity'] = len(resolutions) / len(properties_list)
        
        # Aspect ratio çeşitliliği
        aspect_ratios = [p.get('aspect_ratio', 1.0) for p in properties_list]
        metrics['aspect_ratio_std'] = float(np.std(aspect_ratios))
        
        # Parlaklık çeşitliliği
        brightness_values = [p.get('brightness_mean', 128) for p in properties_list]
        metrics['brightness_std'] = float(np.std(brightness_values))
        metrics['brightness_cv'] = float(np.std(brightness_values) / (np.mean(brightness_values) + 1e-6))
        
        # Renk çeşitliliği
        color_diversity_values = [p.get('color_diversity', 0) for p in properties_list]
        metrics['avg_color_diversity'] = float(np.mean(color_diversity_values))
        metrics['color_diversity_std'] = float(np.std(color_diversity_values))
        
        # Dosya boyutu çeşitliliği
        file_sizes = [p.get('file_size_mb', 0) for p in properties_list]
        metrics['file_size_cv'] = float(np.std(file_sizes) / (np.mean(file_sizes) + 1e-6))
        
        # Kontrast çeşitliliği
        contrast_values = [p.get('contrast_score', 0) for p in properties_list]
        metrics['contrast_std'] = float(np.std(contrast_values))
        
        # Format çeşitliliği
        formats = [p.get('format', 'Unknown') for p in properties_list]
        unique_formats = len(set(formats))
        metrics['format_diversity'] = unique_formats / len(properties_list)
        
        # Genel çeşitlilik skoru
        diversity_components = [
            min(metrics['resolution_diversity'], 1.0),
            min(metrics['aspect_ratio_std'] / 2.0, 1.0),
            min(metrics['brightness_std'] / 50.0, 1.0),
            min(metrics['avg_color_diversity'], 1.0),
            min(metrics['file_size_cv'], 1.0),
            min(metrics['format_diversity'], 1.0)
        ]
        
        metrics['overall_diversity_score'] = float(np.mean(diversity_components))
        
        return metrics
    
    def generate_quality_summary(self, properties_list: List[Dict]) -> Dict[str, Any]:
        """
        Kalite özeti oluştur
        
        Args:
            properties_list: Görüntü özellikleri listesi
            
        Returns:
            Kalite özeti sözlüğü
        """
        if not properties_list:
            return {}
        
        quality_scores = [p.get('quality_score', 0) for p in properties_list]
        
        # Kalite kategorileri (config'den alınabilir)
        thresholds = self.config.get('quality_thresholds', {
            'excellent': 90,
            'good': 75,
            'fair': 60
        })
        
        excellent = len([q for q in quality_scores if q >= thresholds['excellent']])
        good = len([q for q in quality_scores if thresholds['good'] <= q < thresholds['excellent']])
        fair = len([q for q in quality_scores if thresholds['fair'] <= q < thresholds['good']])
        poor = len([q for q in quality_scores if q < thresholds['fair']])
        
        total = len(quality_scores)
        
        # Kalite skoru istatistikleri
        quality_stats = self._calculate_numeric_stats(quality_scores)
        
        return {
            'statistics': quality_stats,
            'distribution': {
                'excellent': {'count': excellent, 'percentage': (excellent/total)*100},
                'good': {'count': good, 'percentage': (good/total)*100},
                'fair': {'count': fair, 'percentage': (fair/total)*100},
                'poor': {'count': poor, 'percentage': (poor/total)*100}
            },
            'overall_grade': self._calculate_overall_grade(quality_stats['mean'])
        }
    
    def _calculate_overall_grade(self, average_quality: float) -> str:
        """Ortalama kalite skoruna göre genel not hesapla"""
        if average_quality >= 90:
            return 'A'
        elif average_quality >= 80:
            return 'B'
        elif average_quality >= 70:
            return 'C'
        elif average_quality >= 60:
            return 'D'
        else:
            return 'F'
    
    def calculate_correlations(self, properties_list: List[Dict]) -> Dict[str, float]:
        """
        Görüntü özellikleri arasındaki korelasyonları hesapla
        
        Args:
            properties_list: Görüntü özellikleri listesi
            
        Returns:
            Korelasyon katsayıları sözlüğü
        """
        if len(properties_list) < 2:
            return {}
        
        # İlgilenilen özellik çiftleri
        feature_pairs = [
            ('file_size_mb', 'megapixels'),
            ('width', 'height'),
            ('brightness_mean', 'contrast_score'),
            ('blur_score', 'sharpness_score'),
            ('quality_score', 'contrast_score'),
            ('quality_score', 'blur_score'),
            ('edge_density', 'sharpness_score'),
            ('noise_score', 'quality_score')
        ]
        
        correlations = {}
        
        for feature1, feature2 in feature_pairs:
            values1 = [p.get(feature1, 0) for p in properties_list if feature1 in p and feature2 in p]
            values2 = [p.get(feature2, 0) for p in properties_list if feature1 in p and feature2 in p]
            
            if len(values1) >= 2 and len(values2) >= 2:
                try:
                    correlation = np.corrcoef(values1, values2)[0, 1]
                    if not np.isnan(correlation):
                        correlations[f"{feature1}_vs_{feature2}"] = float(correlation)
                except:
                    pass
        
        return correlations
    
    def generate_recommendations(self, properties_list: List[Dict], 
                               anomaly_results: Dict = None,
                               diversity_metrics: Dict = None) -> List[str]:
        """
        İyileştirme önerileri oluştur
        
        Args:
            properties_list: Görüntü özellikleri listesi
            anomaly_results: Anomali tespit sonuçları
            diversity_metrics: Çeşitlilik metrikleri
            
        Returns:
            Öneri listesi
        """
        recommendations = []
        
        if not properties_list:
            return ["❌ Analiz edilebilir görüntü bulunamadı"]
        
        # Kalite tabanlı öneriler
        quality_summary = self.generate_quality_summary(properties_list)
        avg_quality = quality_summary.get('statistics', {}).get('mean', 50)
        
        if avg_quality < 60:
            recommendations.append("🔴 Genel görüntü kalitesi düşük. Daha yüksek kaliteli görüntüler ekleyin.")
        elif avg_quality < 75:
            recommendations.append("🟡 Görüntü kalitesi orta seviyede. Kalite iyileştirmesi yapılabilir.")
        else:
            recommendations.append("✅ Görüntü kalitesi iyi seviyede.")
        
        # Anomali tabanlı öneriler
        if anomaly_results:
            total_anomalies = anomaly_results.get('summary', {}).get('total_anomalies', 0)
            anomaly_rate = anomaly_results.get('summary', {}).get('anomaly_rate', 0)
            
            if anomaly_rate > 15:
                recommendations.append(f"⚠️ Yüksek anomali oranı (%{anomaly_rate:.1f}). Veri temizliği gerekli.")
            elif anomaly_rate > 5:
                recommendations.append(f"🔍 Orta seviyede anomali tespit edildi (%{anomaly_rate:.1f}). İncelenmesi önerilir.")
        
        # Çeşitlilik tabanlı öneriler
        if diversity_metrics:
            resolution_diversity = diversity_metrics.get('resolution_diversity', 0)
            if resolution_diversity < 0.3:
                recommendations.append("📐 Çözünürlük çeşitliliği düşük. Farklı boyutlarda görüntüler ekleyin.")
            
            brightness_std = diversity_metrics.get('brightness_std', 0)
            if brightness_std < 20:
                recommendations.append("💡 Parlaklık çeşitliliği düşük. Farklı aydınlatma koşullarında görüntüler ekleyin.")
            
            overall_diversity = diversity_metrics.get('overall_diversity_score', 0)
            if overall_diversity < 0.5:
                recommendations.append("🌈 Genel çeşitlilik düşük. Daha çeşitli görüntüler ekleyin.")
        
        # Boyut tabanlı öneriler
        stats = self.calculate_dataset_statistics(properties_list)
        
        # Bulanık görüntü kontrolü
        blur_stats = stats.get('is_blurry', {})
        if blur_stats.get('percentage', 0) > 5:
            recommendations.append(f"🌫️ %{blur_stats['percentage']:.1f} bulanık görüntü tespit edildi. Bu görüntüleri temizleyin.")
        
        # Dosya boyutu optimizasyonu
        file_size_stats = stats.get('file_size_mb', {})
        if file_size_stats:
            avg_size = file_size_stats.get('mean', 0)
            if avg_size > 5:
                recommendations.append("💾 Ortalama dosya boyutu yüksek. Sıkıştırma düşünün.")
            elif avg_size < 0.1:
                recommendations.append("📷 Ortalama dosya boyutu çok düşük. Kalite kaybı olabilir.")
        
        # Format çeşitliliği
        format_stats = stats.get('format_distribution', {})
        if format_stats.get('unique_formats', 0) > 3:
            recommendations.append("🔧 Çok fazla farklı format var. Format standardizasyonu düşünün.")
        
        if not recommendations:
            recommendations.append("✨ Veri seti genel olarak iyi durumda görünüyor!")
        
        return recommendations
