#!/usr/bin/env python3
"""
Görüntü Kalite Metrikleri Hesaplayıcısı

Bu modül görüntü kalitesi metriklerini hesaplayan fonksiyonları içerir.
"""

import cv2
import numpy as np
from PIL import Image, ImageStat
from typing import Dict, Tuple, Any

class QualityMetricsCalculator:
    """Görüntü kalitesi metriklerini hesaplayan sınıf"""
    
    def __init__(self, config: Dict = None):
        """
        QualityMetricsCalculator sınıfını başlat
        
        Args:
            config: Konfigürasyon parametreleri
        """
        self.config = config or {}
        
    def calculate_color_statistics(self, pil_image: Image.Image, cv_image: np.ndarray) -> Dict[str, float]:
        """
        Renk istatistiklerini hesapla
        
        Args:
            pil_image: PIL formatında görüntü
            cv_image: OpenCV formatında görüntü
            
        Returns:
            Renk istatistikleri sözlüğü
        """
        try:
            # PIL ile temel istatistikler
            stat = ImageStat.Stat(pil_image)
            
            # HSV renk uzayına dönüştür
            hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            
            stats = {
                'red_mean': float(stat.mean[0]) if len(stat.mean) > 0 else 0.0,
                'green_mean': float(stat.mean[1]) if len(stat.mean) > 1 else 0.0,
                'blue_mean': float(stat.mean[2]) if len(stat.mean) > 2 else 0.0,
                'red_std': float(stat.stddev[0]) if len(stat.stddev) > 0 else 0.0,
                'green_std': float(stat.stddev[1]) if len(stat.stddev) > 1 else 0.0,
                'blue_std': float(stat.stddev[2]) if len(stat.stddev) > 2 else 0.0,
                'hue_mean': float(np.mean(hsv_image[:,:,0])),
                'saturation_mean': float(np.mean(hsv_image[:,:,1])),
                'value_mean': float(np.mean(hsv_image[:,:,2])),
            }
            
            return stats
        except Exception as e:
            print(f"⚠️ Renk istatistikleri hesaplama hatası: {e}")
            return {
                'red_mean': 0.0, 'green_mean': 0.0, 'blue_mean': 0.0,
                'red_std': 0.0, 'green_std': 0.0, 'blue_std': 0.0,
                'hue_mean': 0.0, 'saturation_mean': 0.0, 'value_mean': 0.0
            }
    
    def calculate_blur_score(self, image: np.ndarray) -> float:
        """
        Laplacian variance kullanarak bulanıklık skorunu hesapla
        
        Args:
            image: OpenCV formatında görüntü
            
        Returns:
            Bulanıklık skoru
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            return float(blur_score)
        except Exception as e:
            print(f"⚠️ Bulanıklık skoru hesaplama hatası: {e}")
            return 0.0
    
    def calculate_brightness_stats(self, image: np.ndarray) -> Dict[str, float]:
        """
        Parlaklık istatistiklerini hesapla
        
        Args:
            image: OpenCV formatında görüntü
            
        Returns:
            Parlaklık istatistikleri sözlüğü
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return {
                'mean': float(np.mean(gray)),
                'std': float(np.std(gray)),
                'min': float(np.min(gray)),
                'max': float(np.max(gray))
            }
        except Exception as e:
            print(f"⚠️ Parlaklık istatistikleri hesaplama hatası: {e}")
            return {'mean': 128.0, 'std': 0.0, 'min': 0.0, 'max': 255.0}
    
    def calculate_contrast_score(self, image: np.ndarray) -> float:
        """
        RMS kontrast hesapla
        
        Args:
            image: OpenCV formatında görüntü
            
        Returns:
            Kontrast skoru
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            mean = np.mean(gray)
            contrast = np.sqrt(np.mean((gray - mean) ** 2))
            return float(contrast)
        except Exception as e:
            print(f"⚠️ Kontrast skoru hesaplama hatası: {e}")
            return 0.0
    
    def calculate_noise_score(self, image: np.ndarray) -> float:
        """
        Noise seviyesini tahmin et
        
        Args:
            image: OpenCV formatında görüntü
            
        Returns:
            Noise skoru
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Gaussian blur uygula ve farkı hesapla
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            noise = cv2.absdiff(gray, blurred)
            return float(np.mean(noise))
        except Exception as e:
            print(f"⚠️ Noise skoru hesaplama hatası: {e}")
            return 0.0
    
    def calculate_edge_density(self, image: np.ndarray) -> float:
        """
        Kenar yoğunluğunu hesapla
        
        Args:
            image: OpenCV formatında görüntü
            
        Returns:
            Kenar yoğunluğu
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            return float(edge_density)
        except Exception as e:
            print(f"⚠️ Kenar yoğunluğu hesaplama hatası: {e}")
            return 0.0
    
    def calculate_color_diversity(self, image: np.ndarray) -> float:
        """
        Renk çeşitliliğini hesapla
        
        Args:
            image: OpenCV formatında görüntü
            
        Returns:
            Renk çeşitliliği skoru
        """
        try:
            # Görüntüyü küçült (performans için)
            small_image = cv2.resize(image, (100, 100))
            pixels = small_image.reshape(-1, 3)
            
            # Benzersiz renk sayısını hesapla
            unique_colors = len(np.unique(pixels, axis=0))
            max_possible_colors = pixels.shape[0]
            
            diversity = unique_colors / max_possible_colors
            return float(diversity)
        except Exception as e:
            print(f"⚠️ Renk çeşitliliği hesaplama hatası: {e}")
            return 0.0
    
    def calculate_sharpness_score(self, image: np.ndarray) -> float:
        """
        Sobel operatörü kullanarak keskinlik skorunu hesapla
        
        Args:
            image: OpenCV formatında görüntü
            
        Returns:
            Keskinlik skoru
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Sobel kenar tespiti
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Magnitude hesapla
            magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            sharpness = np.mean(magnitude)
            
            return float(sharpness)
        except Exception as e:
            print(f"⚠️ Keskinlik skoru hesaplama hatası: {e}")
            return 0.0
    
    def calculate_histogram_features(self, image: np.ndarray) -> Dict[str, float]:
        """
        Histogram tabanlı özellikler hesapla
        
        Args:
            image: OpenCV formatında görüntü
            
        Returns:
            Histogram özellikleri sözlüğü
        """
        try:
            # RGB kanalları için histogram hesapla
            histograms = []
            for i in range(3):
                hist = cv2.calcHist([image], [i], None, [256], [0, 256])
                histograms.append(hist.flatten())
            
            features = {}
            
            for i, color in enumerate(['blue', 'green', 'red']):
                hist = histograms[i]
                
                # Histogram istatistikleri
                features[f'{color}_hist_mean'] = float(np.mean(hist))
                features[f'{color}_hist_std'] = float(np.std(hist))
                features[f'{color}_hist_skew'] = float(self._calculate_skewness(hist))
                features[f'{color}_hist_kurt'] = float(self._calculate_kurtosis(hist))
            
            return features
        except Exception as e:
            print(f"⚠️ Histogram özellikleri hesaplama hatası: {e}")
            return {}
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Skewness (çarpıklık) hesapla"""
        try:
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0.0
            skew = np.mean(((data - mean) / std) ** 3)
            return float(skew)
        except:
            return 0.0
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Kurtosis (basıklık) hesapla"""
        try:
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0.0
            kurt = np.mean(((data - mean) / std) ** 4) - 3  # -3 for excess kurtosis
            return float(kurt)
        except:
            return 0.0
    
    def calculate_overall_quality_score(self, metrics: Dict[str, float], 
                                      config: Dict = None) -> float:
        """
        Genel kalite skorunu hesapla (0-100)
        
        Args:
            metrics: Hesaplanmış metrikler
            config: Skorlama konfigürasyonu
            
        Returns:
            Genel kalite skoru
        """
        try:
            config = config or self.config
            
            # Metrikleri normalize et
            blur_score = metrics.get('blur_score', 0)
            brightness_mean = metrics.get('brightness_mean', 128)
            contrast_score = metrics.get('contrast_score', 0)
            noise_score = metrics.get('noise_score', 0)
            edge_density = metrics.get('edge_density', 0)
            
            # Normalize edilmiş skorlar
            blur_norm = min(blur_score / 500.0, 1.0)  # 500+ iyi kabul edilir
            brightness_norm = 1.0 - abs(brightness_mean - 127.5) / 127.5
            contrast_norm = min(contrast_score / 50.0, 1.0)  # 50+ iyi kontrast
            noise_norm = max(0, 1.0 - noise_score / 20.0)  # Düşük noise iyi
            edge_norm = min(edge_density * 10, 1.0)  # Kenar yoğunluğu
            
            # Ağırlıklı ortalama
            weights = config.get('quality_weights', {
                'blur': 0.25,
                'brightness': 0.20,
                'contrast': 0.25,
                'noise': 0.15,
                'edge': 0.15
            })
            
            quality = (
                blur_norm * weights.get('blur', 0.25) +
                brightness_norm * weights.get('brightness', 0.20) +
                contrast_norm * weights.get('contrast', 0.25) +
                noise_norm * weights.get('noise', 0.15) +
                edge_norm * weights.get('edge', 0.15)
            ) * 100
            
            return round(float(quality), 2)
        except Exception as e:
            print(f"⚠️ Kalite skoru hesaplama hatası: {e}")
            return 50.0  # Varsayılan orta kalite
    
    def calculate_all_metrics(self, pil_image: Image.Image, cv_image: np.ndarray) -> Dict[str, Any]:
        """
        Tüm kalite metriklerini hesapla
        
        Args:
            pil_image: PIL formatında görüntü
            cv_image: OpenCV formatında görüntü
            
        Returns:
            Tüm metrikler sözlüğü
        """
        # Renk istatistikleri
        color_stats = self.calculate_color_statistics(pil_image, cv_image)
        
        # Kalite metrikleri
        blur_score = self.calculate_blur_score(cv_image)
        brightness_stats = self.calculate_brightness_stats(cv_image)
        contrast_score = self.calculate_contrast_score(cv_image)
        noise_score = self.calculate_noise_score(cv_image)
        edge_density = self.calculate_edge_density(cv_image)
        color_diversity = self.calculate_color_diversity(cv_image)
        sharpness_score = self.calculate_sharpness_score(cv_image)
        histogram_features = self.calculate_histogram_features(cv_image)
        
        # Tüm metrikleri birleştir
        all_metrics = {
            # Temel kalite metrikleri
            'blur_score': blur_score,
            'brightness_mean': brightness_stats['mean'],
            'brightness_std': brightness_stats['std'],
            'brightness_min': brightness_stats['min'],
            'brightness_max': brightness_stats['max'],
            'contrast_score': contrast_score,
            'noise_score': noise_score,
            'edge_density': edge_density,
            'color_diversity': color_diversity,
            'sharpness_score': sharpness_score,
            
            # Boolean kalite kontrolleri
            'is_blurry': blur_score < self.config.get('blur_threshold', 100.0),
            'is_too_dark': brightness_stats['mean'] < self.config.get('min_brightness', 30),
            'is_too_bright': brightness_stats['mean'] > self.config.get('max_brightness', 225),
            
            # Renk istatistikleri
            **color_stats,
            
            # Histogram özellikleri
            **histogram_features
        }
        
        # Genel kalite skoru
        all_metrics['quality_score'] = self.calculate_overall_quality_score(all_metrics)
        
        return all_metrics
