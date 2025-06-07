#!/usr/bin/env python3
"""
Ana Annotation Analiz Modülü

Bu modül tüm annotation analiz bileşenlerini birleştiren ana sınıfı içerir.
"""

from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

# Alt modülleri import et
from .base_analyzer import BaseAnnotationAnalyzer
from .format_parsers import FormatParserFactory, parse_annotation_file
from .class_distribution import ClassDistributionAnalyzer
from .bbox_analyzer import BoundingBoxAnalyzer
from .quality_checker import AnnotationQualityChecker

class AnnotationAnalyzer(BaseAnnotationAnalyzer):
    """Kapsamlı annotation analizi yapan ana sınıf"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        AnnotationAnalyzer sınıfını başlat
        
        Args:
            config: Analiz konfigürasyonu
        """
        super().__init__(config)
        
        # Alt bileşenleri başlat
        self.class_analyzer = ClassDistributionAnalyzer(config)
        self.bbox_analyzer = BoundingBoxAnalyzer(config)
        self.quality_checker = AnnotationQualityChecker(config)
        
        # Sonuç depolama
        self.analysis_results = {}
        self.annotation_data = []
        
    def load_annotations(self, annotation_path: str) -> Dict[str, Any]:
        """
        Tek annotation dosyasını yükle
        
        Args:
            annotation_path: Annotation dosyası yolu
            
        Returns:
            Parse edilmiş annotation verisi
        """
        # Format'ı auto-detect et
        format_type = self.detect_annotation_format(annotation_path)
        
        if not format_type or format_type.startswith('unknown'):
            # Varsayılan olarak YOLO format'ını dene
            format_type = 'yolo'
        
        # Parse et
        return parse_annotation_file(annotation_path, format_type, self.class_names)
    
    def analyze_dataset_annotations(self, annotation_paths: List[str],
                                  image_paths: List[str] = None,
                                  progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Tüm veri seti annotation'larını analiz et
        
        Args:
            annotation_paths: Annotation dosyası yolları listesi
            image_paths: Görüntü dosyası yolları (opsiyonel)
            progress_callback: İlerleme callback fonksiyonu
            
        Returns:
            Kapsamlı annotation analizi sonuçları
        """
        print(f"📝 {len(annotation_paths)} annotation dosyası analiz ediliyor...")
        
        # Annotation dosyalarını yükle
        annotation_data = []
        failed_files = []
        
        for i, ann_path in enumerate(annotation_paths):
            if progress_callback:
                progress_callback(i + 1, len(annotation_paths))
            else:
                self.progress_callback(i + 1, len(annotation_paths), "Annotation'lar yükleniyor")
            
            parsed_data = self.load_annotations(ann_path)
            
            if parsed_data.get('parsing_failed', False):
                failed_files.append(parsed_data)
            else:
                annotation_data.append(parsed_data)
        
        print(f"\n✅ {len(annotation_data)} annotation dosyası başarıyla yüklendi")
        if failed_files:
            print(f"❌ {len(failed_files)} dosya yüklenemedi")
        
        # Analiz sonuçlarını depola
        self.annotation_data = annotation_data
        
        # Kapsamlı analiz yap
        return self._perform_comprehensive_annotation_analysis(
            annotation_data, failed_files, image_paths
        )
    
    def _perform_comprehensive_annotation_analysis(self, annotation_data: List[Dict],
                                                 failed_files: List[Dict],
                                                 image_paths: List[str] = None) -> Dict[str, Any]:
        """
        Kapsamlı annotation analizi yap
        
        Args:
            annotation_data: Başarılı parse edilmiş annotation verileri
            failed_files: Başarısız parse edilmiş dosyalar
            image_paths: Görüntü dosyası yolları
            
        Returns:
            Kapsamlı analiz sonuçları
        """
        print("📊 Annotation istatistikleri hesaplanıyor...")
        
        # Sınıf dağılımı analizi
        class_analysis = self.class_analyzer.analyze_class_distribution(annotation_data)
        
        print("📐 Bounding box analizi yapılıyor...")
        
        # Bounding box analizi
        bbox_analysis = self.bbox_analyzer.analyze_bboxes(annotation_data)
        
        print("🔍 Kalite kontrolü yapılıyor...")
        
        # Kalite kontrolü
        quality_analysis = self.quality_checker.check_annotation_quality(
            annotation_data + failed_files, image_paths
        )
        
        print("💡 Öneriler oluşturuluyor...")
        
        # Genel öneriler
        recommendations = self._generate_comprehensive_recommendations(
            class_analysis, bbox_analysis, quality_analysis
        )
        
        # Format analizi
        format_analysis = self._analyze_formats(annotation_data + failed_files)
        
        # Sonuçları birleştir
        results = {
            # Temel bilgiler
            'total_annotation_files': len(annotation_data) + len(failed_files),
            'successfully_parsed': len(annotation_data),
            'failed_to_parse': len(failed_files),
            'parse_success_rate': len(annotation_data) / (len(annotation_data) + len(failed_files)) * 100 
                                if (len(annotation_data) + len(failed_files)) > 0 else 0,
            
            # Detaylı analizler
            'format_analysis': format_analysis,
            'class_analysis': class_analysis,
            'bbox_analysis': bbox_analysis,
            'quality_analysis': quality_analysis,
            
            # Ham veriler
            'annotation_data': annotation_data,
            'failed_files': failed_files,
            
            # Öneriler ve özet
            'recommendations': recommendations,
            'analysis_summary': self._generate_analysis_summary(
                annotation_data, class_analysis, bbox_analysis, quality_analysis
            )
        }
        
        # Sonuçları depola
        self.analysis_results = results
        return results
    
    def _analyze_formats(self, all_annotation_data: List[Dict]) -> Dict[str, Any]:
        """Annotation formatlarını analiz et"""
        format_counts = {}
        total_files = len(all_annotation_data)
        
        for data in all_annotation_data:
            format_type = data.get('format', 'unknown')
            format_counts[format_type] = format_counts.get(format_type, 0) + 1
        
        # En yaygın format
        most_common_format = max(format_counts.items(), key=lambda x: x[1]) if format_counts else ('unknown', 0)
        
        # Format dağılımı
        format_distribution = []
        for fmt, count in format_counts.items():
            format_distribution.append({
                'format': fmt,
                'count': count,
                'percentage': (count / total_files) * 100 if total_files > 0 else 0
            })
        
        return {
            'total_files': total_files,
            'unique_formats': len(format_counts),
            'format_counts': format_counts,
            'format_distribution': format_distribution,
            'most_common_format': most_common_format[0],
            'most_common_count': most_common_format[1],
            'format_consistency': len(format_counts) == 1  # Tek format kullanılıyor mu?
        }
    
    def _generate_comprehensive_recommendations(self, class_analysis: Dict,
                                              bbox_analysis: Dict,
                                              quality_analysis: Dict) -> List[str]:
        """Kapsamlı öneriler oluştur"""
        recommendations = []
        
        # Sınıf analizi önerileri
        class_recommendations = class_analysis.get('recommendations', [])
        recommendations.extend(class_recommendations)
        
        # Bbox analizi önerileri
        bbox_recommendations = bbox_analysis.get('recommendations', [])
        recommendations.extend(bbox_recommendations)
        
        # Kalite analizi önerileri
        quality_recommendations = quality_analysis.get('recommendations', [])
        recommendations.extend(quality_recommendations)
        
        # Genel değerlendirme
        if not recommendations:
            recommendations.append("✨ Annotation'lar genel olarak iyi durumda görünüyor!")
        
        # Duplikasyon temizle ve sırala
        unique_recommendations = list(dict.fromkeys(recommendations))
        
        return unique_recommendations
    
    def _generate_analysis_summary(self, annotation_data: List[Dict],
                                 class_analysis: Dict, bbox_analysis: Dict,
                                 quality_analysis: Dict) -> Dict[str, Any]:
        """Analiz özeti oluştur"""
        
        # Temel istatistikler
        total_annotations = sum(len(data.get('annotations', [])) for data in annotation_data)
        total_classes = class_analysis.get('total_classes', 0)
        
        # Kalite skorları
        class_balance_score = self.class_analyzer.calculate_balance_score(
            class_analysis.get('class_counts', {})
        ) if hasattr(self.class_analyzer, 'calculate_balance_score') else 75
        
        bbox_quality_score = bbox_analysis.get('quality_assessment', {}).get('quality_score', 75)
        overall_quality_score = quality_analysis.get('overall_quality_score', 75)
        
        # Genel annotation skoru hesapla
        annotation_score = (class_balance_score * 0.3 + bbox_quality_score * 0.4 + overall_quality_score * 0.3)
        
        return {
            'total_annotation_files': len(annotation_data),
            'total_annotations': total_annotations,
            'total_classes': total_classes,
            'average_annotations_per_file': total_annotations / len(annotation_data) if annotation_data else 0,
            
            # Kalite skorları
            'class_balance_score': round(class_balance_score, 2),
            'bbox_quality_score': round(bbox_quality_score, 2),
            'overall_quality_score': round(overall_quality_score, 2),
            'annotation_score': round(annotation_score, 2),
            'annotation_grade': self._grade_score(annotation_score),
            
            # Anahtar bulgular
            'key_findings': self._generate_key_findings(
                class_analysis, bbox_analysis, quality_analysis
            )
        }
    
    def _grade_score(self, score: float) -> str:
        """Skoru harf notuna dönüştür"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_key_findings(self, class_analysis: Dict, bbox_analysis: Dict,
                             quality_analysis: Dict) -> List[str]:
        """Anahtar bulgular oluştur"""
        findings = []
        
        # Sınıf dağılımı bulguları
        total_classes = class_analysis.get('total_classes', 0)
        if total_classes > 0:
            imbalance_severity = class_analysis.get('imbalance_analysis', {}).get('imbalance_severity', 'unknown')
            if imbalance_severity == 'balanced':
                findings.append("✅ Sınıf dağılımı dengeli")
            elif imbalance_severity in ['moderate_imbalance', 'severe_imbalance']:
                findings.append("⚠️ Sınıf dengesizliği mevcut")
        
        # Bbox bulguları
        total_bboxes = bbox_analysis.get('total_bboxes', 0)
        if total_bboxes > 0:
            findings.append(f"📦 {total_bboxes} bounding box analiz edildi")
        
        # Kalite bulguları
        overall_quality = quality_analysis.get('overall_quality_score', 0)
        if overall_quality >= 85:
            findings.append("🏆 Yüksek annotation kalitesi")
        elif overall_quality < 70:
            findings.append("🔧 Annotation kalitesi iyileştirilebilir")
        
        # Format bulguları
        if len(self.analysis_results.get('format_analysis', {}).get('format_counts', {})) > 1:
            findings.append("🔄 Çoklu annotation formatı kullanılıyor")
        
        return findings
    
    def get_annotation_summary_text(self) -> str:
        """Annotation analiz özetini metin olarak al"""
        if not self.analysis_results:
            return "Henüz annotation analizi yapılmadı."
        
        summary = self.analysis_results.get('analysis_summary', {})
        
        text = f"""
📝 ANNOTATION ANALİZ ÖZETİ
{'='*50}

📊 Temel Bilgiler:
• Toplam annotation dosyası: {summary.get('total_annotation_files', 0)}
• Toplam annotation: {summary.get('total_annotations', 0)}
• Toplam sınıf sayısı: {summary.get('total_classes', 0)}
• Dosya başına ortalama annotation: {summary.get('average_annotations_per_file', 0):.1f}

🎯 Kalite Skorları:
• Sınıf dengesi: {summary.get('class_balance_score', 0)}/100
• Bbox kalitesi: {summary.get('bbox_quality_score', 0)}/100
• Genel kalite: {summary.get('overall_quality_score', 0)}/100
• Annotation skoru: {summary.get('annotation_score', 0)}/100 (Not: {summary.get('annotation_grade', 'F')})

💡 Anahtar Bulgular:
"""
        
        for finding in summary.get('key_findings', []):
            text += f"• {finding}\n"
        
        text += f"\n🔧 Öneriler:\n"
        for recommendation in self.analysis_results.get('recommendations', [])[:5]:  # İlk 5 öneri
            text += f"• {recommendation}\n"
        
        return text
    
    def save_annotation_results(self, output_path: str) -> bool:
        """
        Annotation analiz sonuçlarını JSON dosyasına kaydet
        
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
            
            print(f"✅ Annotation analiz sonuçları kaydedildi: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Sonuçlar kaydedilirken hata: {e}")
            return False
    
    def _prepare_results_for_json(self, data: Any) -> Any:
        """JSON serileştirme için veriyi hazırla"""
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
    
    def find_annotation_files_in_dataset(self, dataset_path: str, 
                                       annotation_format: str = 'auto') -> List[str]:
        """
        Dataset dizinindeki annotation dosyalarını bul
        
        Args:
            dataset_path: Dataset ana dizini
            annotation_format: Annotation formatı
            
        Returns:
            Bulunan annotation dosyaları listesi
        """
        return self.find_annotation_files(dataset_path, annotation_format)
    
    def quick_annotation_analysis(self, annotation_paths: List[str], 
                                sample_size: int = 50) -> Dict[str, Any]:
        """
        Hızlı annotation analizi yap
        
        Args:
            annotation_paths: Tüm annotation yolları
            sample_size: Analiz edilecek örnek boyutu
            
        Returns:
            Hızlı analiz sonuçları
        """
        import random
        
        # Rastgele örnek seç
        if len(annotation_paths) <= sample_size:
            sample_paths = annotation_paths
        else:
            sample_paths = random.sample(annotation_paths, sample_size)
        
        print(f"🚀 Hızlı annotation analizi: {len(sample_paths)} dosya örneği")
        
        # Analiz yap
        results = self.analyze_dataset_annotations(sample_paths)
        
        # Örnek analizi olduğunu belirt
        results['is_sample_analysis'] = True
        results['sample_size'] = len(sample_paths)
        results['total_available'] = len(annotation_paths)
        results['sample_ratio'] = len(sample_paths) / len(annotation_paths)
        
        return results
