"""
Core Enhanced Dataset Analyzer
Ana gelişmiş veri seti analiz motoru
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from ..data_loader import DatasetLoader
from ..image_analyzer import ImageAnalyzer
from ..quality_assessor import DatasetQualityAssessor
from .config_manager import ConfigManager
from .report_manager import ReportManager
from .analysis_pipeline import PipelineBuilder

logger = logging.getLogger(__name__)

class EnhancedDatasetAnalyzer:
    """
    Quality Assessor modülüyle entegre edilmiş gelişmiş veri seti analiz sistemi
    """
    
    def __init__(self, dataset_path: str, annotation_format: str = 'auto', config: Optional[Dict] = None):
        self.dataset_path = Path(dataset_path)
        self.annotation_format = annotation_format
        
        # Konfigürasyon yöneticisini başlat
        self.config_manager = ConfigManager()
        if config:
            self.config_manager.config = config
        else:
            self.config_manager.load_config()
        
        self.config = self.config_manager.get_config()
        
        # Logger'ı kur
        self.logger = self.config_manager.setup_logging()
        
        # Bileşenleri başlat
        self._initialize_components()
        
        self.logger.info(f"EnhancedDatasetAnalyzer başlatıldı: {dataset_path}")
    
    def _initialize_components(self):
        """Analiz bileşenlerini başlat"""
        try:
            # Temel analiz bileşenleri
            self.data_loader = DatasetLoader(str(self.dataset_path), self.annotation_format, self.config)
            self.image_analyzer = ImageAnalyzer(self.config)
            self.quality_assessor = DatasetQualityAssessor(str(self.dataset_path), self.config)
            
            # Gelişmiş yönetim bileşenleri
            self.report_manager = ReportManager(self.config)
            
            # Pipeline builder
            self.pipeline_builder = PipelineBuilder(self.config)
            
            self.logger.info("Tüm bileşenler başarıyla başlatıldı")
            
        except Exception as e:
            self.logger.error(f"Bileşen başlatma hatası: {str(e)}")
            raise
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Kapsamlı pipeline tabanlı analiz"""
        self.logger.info("Kapsamlı pipeline analizi başlatılıyor...")
        
        analysis_start_time = datetime.now()
        
        try:
            # Standard analysis pipeline'ı oluştur
            pipeline = self.pipeline_builder.create_standard_analysis_pipeline(
                data_loader=self.data_loader,
                image_analyzer=self.image_analyzer,
                quality_assessor=self.quality_assessor,
                report_manager=self.report_manager
            )
            
            # Pipeline'ı çalıştır
            pipeline_result = pipeline.run_pipeline(
                quality_assessor=self.quality_assessor  # Rapor oluşturma için gerekli
            )
            
            analysis_duration = (datetime.now() - analysis_start_time).total_seconds()
            
            if not pipeline_result['success']:
                self.logger.error(f"Pipeline başarısız: {pipeline_result.get('failed_steps', [])}")
                raise Exception(f"Analiz pipeline'ı başarısız oldu")
            
            # Sonuçları al
            quality_metrics = pipeline_result['step_results'].get('quality_assessment')
            report_paths = pipeline_result['step_results'].get('report_generation', {})
            
            # Konsola özet yazdır
            if quality_metrics:
                self._print_comprehensive_summary(quality_metrics)
            
            # Yönetici özetini kaydet
            if quality_metrics:
                executive_summary_path = self.report_manager.save_executive_summary(quality_metrics)
                if executive_summary_path:
                    report_paths['executive_summary'] = executive_summary_path
            
            self.logger.info(f"Kapsamlı analiz tamamlandı. Süre: {analysis_duration:.1f} saniye")
            
            return {
                'success': True,
                'quality_metrics': quality_metrics,
                'report_paths': report_paths,
                'pipeline_summary': pipeline_result['pipeline_summary'],
                'analysis_duration': analysis_duration,
                'summary': {
                    'overall_score': quality_metrics.overall_score if quality_metrics else 0,
                    'dataset_grade': quality_metrics.dataset_grade if quality_metrics else 'F',
                    'total_images': quality_metrics.total_images if quality_metrics else 0,
                    'total_annotations': quality_metrics.total_annotations if quality_metrics else 0,
                    'num_classes': quality_metrics.num_classes if quality_metrics else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Kapsamlı analiz hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'analysis_duration': (datetime.now() - analysis_start_time).total_seconds()
            }
    
    def run_quick_assessment(self) -> Dict[str, Any]:
        """Hızlı kalite değerlendirmesi"""
        self.logger.info("Hızlı kalite değerlendirmesi başlatılıyor...")
        
        try:
            # Sadece temel istatistikleri al
            basic_stats = self.data_loader.get_basic_statistics()
            
            # Hızlı skor hesapla
            total_images = basic_stats.get('total_images', 0)
            total_annotations = basic_stats.get('total_annotations', 0)
            num_classes = basic_stats.get('num_classes', 0)
            
            # Basit skor algoritması
            quick_score = self._calculate_quick_score(total_images, total_annotations, num_classes)
            
            # Hızlı grade hesapla
            if quick_score >= 90:
                grade = 'A'
                status = "🌟 Mükemmel"
            elif quick_score >= 75:
                grade = 'B'
                status = "✨ İyi"
            elif quick_score >= 60:
                grade = 'C'
                status = "⚠️  Orta"
            else:
                grade = 'D'
                status = "❌ Düşük"
            
            # Konsola yazdır
            self._print_quick_summary(quick_score, grade, status, basic_stats)
            
            return {
                'success': True,
                'quick_score': quick_score,
                'grade': grade,
                'status': status,
                'basic_stats': basic_stats
            }
            
        except Exception as e:
            self.logger.error(f"Hızlı değerlendirme hatası: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_quick_score(self, total_images: int, total_annotations: int, num_classes: int) -> float:
        """Hızlı skor hesaplama algoritması"""
        score = 50  # Başlangıç skoru
        
        # Görüntü sayısı bonusu
        if total_images >= 1000:
            score += 20
        elif total_images >= 500:
            score += 15
        elif total_images >= 100:
            score += 10
        elif total_images >= 50:
            score += 5
        
        # Annotation eşleşme bonusu
        if total_images > 0:
            matching_ratio = min(total_annotations, total_images) / total_images
            score += matching_ratio * 15
        
        # Sınıf çeşitliliği bonusu
        if num_classes >= 10:
            score += 10
        elif num_classes >= 5:
            score += 8
        elif num_classes >= 3:
            score += 5
        elif num_classes >= 2:
            score += 3
        
        # Minimum veri cezası
        if total_images < 10:
            score -= 30
        elif total_images < 50:
            score -= 15
        
        return max(0, min(100, score))
    
    def _print_comprehensive_summary(self, quality_metrics):
        """Kapsamlı özet yazdır"""
        print("\n" + "="*80)
        print("🎯 KAPSAMLI VERİ SETİ KALİTE DEĞERLENDİRMESİ")
        print("="*80)
        
        # Ana metrikler
        print(f"\n📊 GENEL KALİTE SKORU: {quality_metrics.overall_score:.1f}/100")
        print(f"🎓 VERİ SETİ NOTU: {quality_metrics.dataset_grade}")
        
        # Kalite seviyesi
        if quality_metrics.overall_score >= 90:
            status = "🌟 MÜKEMMEL - Üretim için hazır!"
        elif quality_metrics.overall_score >= 75:
            status = "✨ İYİ - Minor iyileştirmelerle mükemmel olabilir"
        elif quality_metrics.overall_score >= 60:
            status = "⚠️  ORTA - Önemli iyileştirmeler gerekli"
        else:
            status = "❌ DÜŞÜK - Major revizyonlar gerekli"
        
        print(f"\n🎯 DURUM: {status}")
        
        # Veri seti istatistikleri
        print(f"\n📈 VERİ SETİ İSTATİSTİKLERİ:")
        print(f"   📸 Toplam Görüntü: {quality_metrics.total_images:,}")
        print(f"   🏷️  Toplam Annotation: {quality_metrics.total_annotations:,}")
        print(f"   🎯 Sınıf Sayısı: {quality_metrics.num_classes}")
        
        # Kalite bileşenleri
        print(f"\n🔍 KALİTE BİLEŞENLERİ:")
        print(f"   🖼️  Görüntü Kalitesi:     {quality_metrics.image_quality_score:.1f}/100")
        print(f"   🏷️  Annotation Kalitesi:  {quality_metrics.annotation_quality_score:.1f}/100")
        print(f"   ✅ Eksiksizlik:          {quality_metrics.completeness_score:.1f}/100")
        print(f"   🎨 Çeşitlilik:           {quality_metrics.diversity_score:.1f}/100")
        print(f"   🔄 Tutarlılık:           {quality_metrics.consistency_score:.1f}/100")
        
        # En önemli öneriler
        if quality_metrics.recommendations:
            print(f"\n💡 ÖNCELİKLİ ÖNERİLER:")
            for i, rec in enumerate(quality_metrics.recommendations[:3], 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "="*80)
    
    def _print_quick_summary(self, score: float, grade: str, status: str, basic_stats: Dict):
        """Hızlı özet yazdır"""
        print(f"\n🚀 HIZLI KALİTE DEĞERLENDİRMESİ")
        print("=" * 50)
        print(f"📊 Hızlı Skor: {score:.1f}/100")
        print(f"🎓 Not: {grade}")
        print(f"🎯 Durum: {status}")
        print(f"\n📈 VERİ SETİ BOYUTU:")
        print(f"   📸 Görüntü: {basic_stats.get('total_images', 0):,}")
        print(f"   🏷️  Annotation: {basic_stats.get('total_annotations', 0):,}")
        print(f"   🎯 Sınıf: {basic_stats.get('num_classes', 0)}")
        print("\n💡 Detaylı analiz için: --comprehensive parametresini kullanın")
        print("=" * 50)
