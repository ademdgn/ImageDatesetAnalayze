#!/usr/bin/env python3
"""
Ana Görüntü Analiz Modülü

Bu modül tüm görüntü analiz bileşenlerini birleştiren ana sınıfı içerir.
"""

from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

# Alt modülleri import et
from .base_analyzer import BaseImageAnalyzer
from .quality_metrics import QualityMetricsCalculator
from .anomaly_detector import AnomalyDetector
from .statistics_calculator import StatisticsCalculator

class ImageAnalyzer(BaseImageAnalyzer):
    """Kapsamlı görüntü analizi yapan ana sınıf"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        ImageAnalyzer sınıfını başlat
        
        Args:
            config: Analiz konfigürasyonu
        """
        super().__init__(config)
        
        # Alt bileşenleri başlat
        self.quality_calculator = QualityMetricsCalculator(config)
        self.anomaly_detector = AnomalyDetector(config)
        self.statistics_calculator = StatisticsCalculator(config)
        
        # Sonuç depolama
        self.analysis_results = {}
        self.image_features = []
        
    def analyze_image_properties(self, image_path: str) -> Dict[str, Any]:
        """
        Tek bir görüntünün tüm özelliklerini analiz et
        
        Args:
            image_path: Görüntü dosyası yolu
            
        Returns:
            Görüntü özellikleri sözlüğü
        """
        try:
            # Görüntüyü yükle
            pil_image, cv_image = self.load_image(image_path)
            if pil_image is None or cv_image is None:
                return {
                    'file_path': str(image_path),
                    'error': 'Görüntü yüklenemedi',
                    'analysis_failed': True
                }
            
            # Temel özellikler
            properties = self.get_basic_properties(image_path, pil_image)
            
            # Kalite metrikleri
            quality_metrics = self.quality_calculator.calculate_all_metrics(pil_image, cv_image)
            
            # Tüm özellikleri birleştir
            properties.update(quality_metrics)
            
            return properties
            
        except Exception as e:
            return {
                'file_path': str(image_path),
                'error': str(e),
                'analysis_failed': True
            }
    
    def analyze_dataset_images(self, image_paths: List[str], 
                             progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Tüm veri seti görüntülerini analiz et
        
        Args:
            image_paths: Görüntü dosyası yolları listesi
            progress_callback: İlerleme callback fonksiyonu
            
        Returns:
            Kapsamlı analiz sonuçları sözlüğü
        """
        print(f"🔍 {len(image_paths)} görüntü analiz ediliyor...")
        
        all_properties = []
        failed_images = []
        
        # Her görüntüyü analiz et
        for i, image_path in enumerate(image_paths):
            if progress_callback:
                progress_callback(i + 1, len(image_paths))
            else:
                self.progress_callback(i + 1, len(image_paths), "Görüntüler analiz ediliyor")
            
            properties = self.analyze_image_properties(image_path)
            
            if properties.get('analysis_failed', False):
                failed_images.append(properties)
            else:
                all_properties.append(properties)
                # Feature vektörü oluştur
                feature_vector = self._extract_feature_vector(properties)
                self.image_features.append(feature_vector)
        
        print(f"\n✅ {len(all_properties)} görüntü başarıyla analiz edildi")
        if failed_images:
            print(f"❌ {len(failed_images)} görüntü analiz edilemedi")
        
        # Kapsamlı analiz yap
        return self._perform_comprehensive_analysis(all_properties, failed_images)
    
    def _extract_feature_vector(self, properties: Dict) -> List[float]:
        """
        Görüntü özelliklerinden feature vektörü çıkar
        
        Args:
            properties: Görüntü özellikleri
            
        Returns:
            Feature vektörü
        """
        return [
            properties.get('width', 0),
            properties.get('height', 0),
            properties.get('aspect_ratio', 0),
            properties.get('brightness_mean', 0),
            properties.get('contrast_score', 0),
            properties.get('blur_score', 0),
            properties.get('edge_density', 0),
            properties.get('color_diversity', 0),
            properties.get('red_mean', 0),
            properties.get('green_mean', 0),
            properties.get('blue_mean', 0),
            properties.get('saturation_mean', 0),
            properties.get('sharpness_score', 0),
            properties.get('noise_score', 0)
        ]
    
    def _perform_comprehensive_analysis(self, properties_list: List[Dict], 
                                      failed_images: List[Dict]) -> Dict[str, Any]:
        """
        Kapsamlı veri seti analizi yap
        
        Args:
            properties_list: Başarılı analiz edilen görüntü özellikleri
            failed_images: Başarısız analiz edilen görüntüler
            
        Returns:
            Kapsamlı analiz sonuçları
        """
        print("📊 Veri seti istatistikleri hesaplanıyor...")
        
        # Temel istatistikler
        dataset_stats = self.statistics_calculator.calculate_dataset_statistics(properties_list)
        
        # Çeşitlilik metrikleri
        diversity_metrics = self.statistics_calculator.calculate_diversity_metrics(properties_list)
        
        # Kalite özeti
        quality_summary = self.statistics_calculator.generate_quality_summary(properties_list)
        
        # Korelasyon analizi
        correlations = self.statistics_calculator.calculate_correlations(properties_list)
        
        print("🔍 Anomaliler tespit ediliyor...")
        
        # Anomali tespiti
        anomaly_results = self.anomaly_detector.detect_all_anomalies(
            properties_list, self.image_features
        )
        
        print("💡 Öneriler oluşturuluyor...")
        
        # Öneriler
        recommendations = self.statistics_calculator.generate_recommendations(
            properties_list, anomaly_results, diversity_metrics
        )
        
        # Sonuçları birleştir
        results = {
            # Temel bilgiler
            'total_images': len(properties_list) + len(failed_images),
            'analyzed_images': len(properties_list),
            'failed_images': len(failed_images),
            'success_rate': len(properties_list) / (len(properties_list) + len(failed_images)) if (len(properties_list) + len(failed_images)) > 0 else 0,
            
            # Detaylı analizler
            'dataset_statistics': dataset_stats,
            'quality_summary': quality_summary,
            'diversity_metrics': diversity_metrics,
            'correlations': correlations,
            'anomaly_results': anomaly_results,
            
            # Ham veriler
            'image_properties': properties_list,
            'failed_analyses': failed_images,
            'feature_vectors': self.image_features,
            
            # Öneriler ve özet
            'recommendations': recommendations,
            'analysis_summary': self._generate_analysis_summary(
                properties_list, quality_summary, diversity_metrics, anomaly_results
            )
        }
        
        # Sonuçları depola
        self.analysis_results = results
        return results
    
    def _generate_analysis_summary(self, properties_list: List[Dict], 
                                 quality_summary: Dict, diversity_metrics: Dict,
                                 anomaly_results: Dict) -> Dict[str, Any]:
        """
        Analiz özeti oluştur
        
        Args:
            properties_list: Görüntü özellikleri listesi
            quality_summary: Kalite özeti
            diversity_metrics: Çeşitlilik metrikleri
            anomaly_results: Anomali sonuçları
            
        Returns:
            Analiz özeti sözlüğü
        """
        total_images = len(properties_list)
        
        # Genel kalite değerlendirmesi
        avg_quality = quality_summary.get('statistics', {}).get('mean', 0)
        quality_grade = quality_summary.get('overall_grade', 'F')
        
        # Çeşitlilik skoru
        diversity_score = diversity_metrics.get('overall_diversity_score', 0)
        
        # Anomali oranı
        anomaly_rate = anomaly_results.get('summary', {}).get('anomaly_rate', 0)
        
        # Genel skor hesapla (0-100)
        overall_score = self._calculate_overall_dataset_score(
            avg_quality, diversity_score, anomaly_rate
        )
        
        return {
            'total_images': total_images,
            'average_quality_score': round(avg_quality, 2),
            'quality_grade': quality_grade,
            'diversity_score': round(diversity_score, 3),
            'anomaly_rate': round(anomaly_rate, 2),
            'overall_dataset_score': round(overall_score, 2),
            'dataset_health': self._get_dataset_health_status(overall_score),
            'key_insights': self._generate_key_insights(
                properties_list, quality_summary, diversity_metrics, anomaly_results
            )
        }
    
    def _calculate_overall_dataset_score(self, quality_score: float, 
                                       diversity_score: float, 
                                       anomaly_rate: float) -> float:
        """
        Genel veri seti skoru hesapla
        
        Args:
            quality_score: Ortalama kalite skoru
            diversity_score: Çeşitlilik skoru
            anomaly_rate: Anomali oranı
            
        Returns:
            Genel skor (0-100)
        """
        # Skorları normalize et
        quality_norm = quality_score / 100.0
        diversity_norm = min(diversity_score, 1.0)
        anomaly_penalty = max(0, 1.0 - (anomaly_rate / 100.0))
        
        # Ağırlıklı ortalama
        weights = self.config.get('overall_score_weights', {
            'quality': 0.5,
            'diversity': 0.3,
            'anomaly_penalty': 0.2
        })
        
        overall_score = (
            quality_norm * weights.get('quality', 0.5) +
            diversity_norm * weights.get('diversity', 0.3) +
            anomaly_penalty * weights.get('anomaly_penalty', 0.2)
        ) * 100
        
        return overall_score
    
    def _get_dataset_health_status(self, overall_score: float) -> str:
        """
        Genel skora göre veri seti sağlık durumu
        
        Args:
            overall_score: Genel skor
            
        Returns:
            Sağlık durumu string'i
        """
        if overall_score >= 85:
            return "Mükemmel"
        elif overall_score >= 75:
            return "İyi"
        elif overall_score >= 65:
            return "Orta"
        elif overall_score >= 50:
            return "Zayıf"
        else:
            return "Yetersiz"
    
    def _generate_key_insights(self, properties_list: List[Dict], 
                             quality_summary: Dict, diversity_metrics: Dict,
                             anomaly_results: Dict) -> List[str]:
        """
        Anahtar bulgular oluştur
        
        Args:
            properties_list: Görüntü özellikleri listesi
            quality_summary: Kalite özeti
            diversity_metrics: Çeşitlilik metrikleri
            anomaly_results: Anomali sonuçları
            
        Returns:
            Anahtar bulgular listesi
        """
        insights = []
        
        total_images = len(properties_list)
        
        # Veri boyutu değerlendirmesi
        if total_images < 100:
            insights.append(f"📊 Küçük veri seti ({total_images} görüntü) - Daha fazla veri gerekebilir")
        elif total_images < 1000:
            insights.append(f"📊 Orta boyutlu veri seti ({total_images} görüntü)")
        else:
            insights.append(f"📊 Büyük veri seti ({total_images} görüntü)")
        
        # Kalite değerlendirmesi
        quality_dist = quality_summary.get('distribution', {})
        excellent_pct = quality_dist.get('excellent', {}).get('percentage', 0)
        poor_pct = quality_dist.get('poor', {}).get('percentage', 0)
        
        if excellent_pct > 50:
            insights.append(f"✨ %{excellent_pct:.1f} mükemmel kaliteli görüntü")
        if poor_pct > 10:
            insights.append(f"⚠️ %{poor_pct:.1f} düşük kaliteli görüntü")
        
        # Çeşitlilik değerlendirmesi
        resolution_diversity = diversity_metrics.get('resolution_diversity', 0)
        if resolution_diversity > 0.7:
            insights.append("🌈 Yüksek çözünürlük çeşitliliği")
        elif resolution_diversity < 0.3:
            insights.append("📐 Düşük çözünürlük çeşitliliği")
        
        # Anomali değerlendirmesi
        anomaly_summary = anomaly_results.get('summary', {})
        total_anomalies = anomaly_summary.get('total_anomalies', 0)
        if total_anomalies > 0:
            insights.append(f"🔍 {total_anomalies} anomali tespit edildi")
        
        # Format analizi
        if 'dataset_statistics' in self.analysis_results:
            format_dist = self.analysis_results['dataset_statistics'].get('format_distribution', {})
            unique_formats = format_dist.get('unique_formats', 0)
            if unique_formats > 3:
                insights.append(f"🔧 {unique_formats} farklı format kullanılıyor")
        
        return insights
    
    def get_analysis_summary_text(self) -> str:
        """
        Analiz özetini metin olarak al
        
        Returns:
            Metin formatında analiz özeti
        """
        if not self.analysis_results:
            return "Henüz analiz yapılmadı."
        
        summary = self.analysis_results.get('analysis_summary', {})
        
        text = f"""
🔍 VERİ SETİ ANALİZ ÖZETİ
{'='*50}

📊 Temel Bilgiler:
• Toplam görüntü: {summary.get('total_images', 0)}
• Ortalama kalite: {summary.get('average_quality_score', 0)}/100 (Not: {summary.get('quality_grade', 'F')})
• Çeşitlilik skoru: {summary.get('diversity_score', 0):.3f}
• Anomali oranı: %{summary.get('anomaly_rate', 0)}

🎯 Genel Değerlendirme:
• Veri seti skoru: {summary.get('overall_dataset_score', 0)}/100
• Sağlık durumu: {summary.get('dataset_health', 'Bilinmiyor')}

💡 Anahtar Bulgular:
"""
        
        for insight in summary.get('key_insights', []):
            text += f"• {insight}\n"
        
        text += f"\n🔧 Öneriler:\n"
        for recommendation in self.analysis_results.get('recommendations', []):
            text += f"• {recommendation}\n"
        
        return text
    
    def save_analysis_results(self, output_path: str) -> bool:
        """
        Analiz sonuçlarını JSON dosyasına kaydet
        
        Args:
            output_path: Çıktı dosyası yolu
            
        Returns:
            Başarı durumu
        """
        try:
            import json
            
            # Çıktı dizinini oluştur
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # NumPy array'leri listlere dönüştür
            results_copy = self._prepare_results_for_json(self.analysis_results)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results_copy, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Analiz sonuçları kaydedildi: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Sonuçlar kaydedilirken hata: {e}")
            return False
    
    def _prepare_results_for_json(self, data: Any) -> Any:
        """
        JSON serileştirme için veriyi hazırla
        
        Args:
            data: Serileştirilecek veri
            
        Returns:
            JSON uyumlu veri
        """
        import numpy as np
        
        if isinstance(data, dict):
            return {key: self._prepare_results_for_json(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._prepare_results_for_json(item) for item in data]
        elif isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, (np.int64, np.int32)):
            return int(data)
        elif isinstance(data, (np.float64, np.float32)):
            return float(data)
        else:
            return data
    
    def quick_analyze_sample(self, image_paths: List[str], 
                           sample_size: int = 50) -> Dict[str, Any]:
        """
        Hızlı örnek analizi yap
        
        Args:
            image_paths: Tüm görüntü yolları
            sample_size: Analiz edilecek örnek boyutu
            
        Returns:
            Hızlı analiz sonuçları
        """
        import random
        
        # Rastgele örnek seç
        if len(image_paths) <= sample_size:
            sample_paths = image_paths
        else:
            sample_paths = random.sample(image_paths, sample_size)
        
        print(f"🚀 Hızlı analiz: {len(sample_paths)} görüntü örneği")
        
        # Analiz yap
        results = self.analyze_dataset_images(sample_paths)
        
        # Örnek analizi olduğunu belirt
        results['is_sample_analysis'] = True
        results['sample_size'] = len(sample_paths)
        results['total_available'] = len(image_paths)
        results['sample_ratio'] = len(sample_paths) / len(image_paths)
        
        return results
