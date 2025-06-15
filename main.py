#!/usr/bin/env python3
"""
Görüntü Veri Seti Kalite Analizi - Ana Çalıştırma Dosyası

Bu dosya, veri seti analiz sürecini başlatır ve sonuçları raporlar.
"""

import argparse
import sys
import logging
from pathlib import Path
import yaml

# Src modüllerini import et
from src.data_loader import DatasetLoader
from src.image_analyzer import ImageAnalyzer
from src.quality_assessor import DatasetQualityAssessor
from src.annotation_analyzer import AnnotationAnalyzer
#from src.visualizer import Visualizer
#from src.report_generator import ReportGenerator


def setup_logging(config):
    """Logging sistemini kur"""
    logging.basicConfig(
        level=getattr(logging, config['logging']['level']),
        format=config['logging']['format'],
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(config['logging']['file'], mode='a')
        ]
    )
    return logging.getLogger(__name__)


def load_config(config_path="config/config.yaml"):
    """Konfigürasyon dosyasını yükle"""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"Konfigürasyon dosyası bulunamadı: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Konfigürasyon dosyası okuma hatası: {e}")
        sys.exit(1)


class DatasetQualityAnalyzer:
    """Ana veri seti kalite analiz sınıfı (Geçici basitleştirilmiş versiyon)"""
    
    def __init__(self, dataset_path, annotation_format='yolo', config=None):
        self.dataset_path = Path(dataset_path)
        self.annotation_format = annotation_format
        self.config = config or {}
        
        
        self.data_loader = DatasetLoader(dataset_path, annotation_format, config)
        self.image_analyzer = ImageAnalyzer(config)
        self.annotation_analyzer = AnnotationAnalyzer(config)
        self.quality_assessor = DatasetQualityAssessor(dataset_path, config)
        # self.visualizer = Visualizer(config)  # Henüz aktif değil
        # self.report_generator = ReportGenerator(config)  # Henüz aktif değil
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def run_full_analysis(self):
        """Tam analiz sürecini çalıştır (Basitleştirilmiş versiyon)"""
        self.logger.info("Veri seti analizi başlatılıyor...")
        
        try:
            # 1. Veri setini yükle
            self.logger.info("Veri seti yükleniyor...")
            images, annotations = self.data_loader.load_dataset()
            
            # 2. Veri seti doğrulaması
            self.logger.info("Veri seti doğrulanıyor...")
            validation_results = self.data_loader.validate_dataset()
            
            # 3. Temel istatistikler
            self.logger.info("Temel istatistikler hesapplanıyor...")
            basic_stats = self.data_loader.get_basic_statistics()

            # 4. Görüntü analizi
            self.logger.info("Görüntü analizi yapılıyor...")
            image_dataset_images_analayse = self.image_analyzer.analyze_dataset_images(images)

            # 5. Görüntü özellikleri analizi
            self.logger.info("Görüntü özellikleri analizi yapılıyor...")
       
            image_analysis_results =  self.image_analyzer.analyze_image_properties(images)

            
            # Basit rapor
            report = {
                'dataset_info': {
                    'total_images': len(images),
                    'total_annotations': len(annotations),
                    'num_classes': len(self.data_loader.classes_info),
                    'format': self.annotation_format
                },
                'image_analysis': image_dataset_images_analayse,
                'validation': validation_results,
                'basic_stats': basic_stats
            }
            
            # Konsola özet yazdır
            self._print_summary(report)
            
            self.logger.info("Analiz tamamlandı")
            return report
            
        except Exception as e:
            self.logger.error(f"Analiz sırasında hata oluştu: {str(e)}")
            raise
    
    def quick_analysis(self):
        """Hızlı analiz (temel metrikleri döndürür)"""
        self.logger.info("Hızlı analiz başlatılıyor...")
        
        try:
            # Veri setini yükle
            images, annotations = self.data_loader.load_dataset()
            
            # Temel istatistikleri hesapla
            basic_stats = self.data_loader.get_basic_statistics()
            
            return basic_stats
        except Exception as e:
            self.logger.error(f"Hızlı analiz hatası: {str(e)}")
            raise
    
    def _print_summary(self, report):
        """Konsola özet yazdır"""
        print("\n" + "="*60)
        print("🎯 VERİ SETİ ANALİZ SONUCU")
        print("="*60)
        
        # Temel bilgiler
        info = report['dataset_info']
        print(f"📊 Format: {info['format'].upper()}")
        print(f"📸 Görüntü sayısı: {info['total_images']}")
        print(f"🏷️  Annotation sayısı: {info['total_annotations']}")
        print(f"🎯 Sınıf sayısı: {info['num_classes']}")
        
        # Doğrulama
        validation = report['validation']
        score = validation['overall_score']
        print(f"\n📈 Kalite Skoru: {score:.1f}/100")
        
        if score >= 90:
            print("✅ Mükemmel kalite!")
        elif score >= 75:
            print("✨ İyi kalite")
        elif score >= 60:
            print("⚠️  Orta kalite - İyileştirmeler öneriliyor")
        else:
            print("❌ Düşük kalite - Major iyileştirmeler gerekli")
        
        # Hatalar ve uyarılar
        if validation.get('errors'):
            print(f"\n❌ Hatalar ({len(validation['errors'])})")
            for error in validation['errors'][:3]:  # İlk 3'ünü göster
                print(f"   • {error}")
        
        if validation.get('warnings'):
            print(f"\n⚠️  Uyarılar ({len(validation['warnings'])})")
            for warning in validation['warnings'][:3]:  # İlk 3'ünü göster
                print(f"   • {warning}")
        
        print("\n" + "="*60)


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description="Görüntü Veri Seti Kalite Analizi"
    )
    parser.add_argument(
        '--dataset_path', 
        type=str, 
        required=True,
        help='Veri seti dizin yolu'
    )
    parser.add_argument(
        '--format', 
        type=str, 
        default='auto',
        choices=['auto', 'yolo', 'coco', 'pascal_voc', 'labelme'],
        help='Annotation formatı (varsayılan: auto)'
    )
    parser.add_argument(
        '--config', 
        type=str, 
        default='config/config.yaml',
        help='Konfigürasyon dosyası yolu'
    )
    parser.add_argument(
        '--quick', 
        action='store_true',
        help='Hızlı analiz modu (sadece temel istatistikler)'
    )
    parser.add_argument(
        '--output', 
        type=str,
        help='Çıktı dizini (config dosyasındakini override eder)'
    )
    
    args = parser.parse_args()
    
    # Konfigürasyonu yükle
    config = load_config(args.config)
    
    # Output dizinini güncelle
    if args.output:
        config['reporting']['output_dir'] = args.output
    
    # Logging'i kur
    logger = setup_logging(config)
    
    # Veri seti yolunu kontrol et
    if not Path(args.dataset_path).exists():
        logger.error(f"Veri seti dizini bulunamadı: {args.dataset_path}")
        sys.exit(1)
    
    try:
        # Analyzer'ı başlat
        analyzer = DatasetQualityAnalyzer(
            dataset_path=args.dataset_path,
            annotation_format=args.format,
            config=config
        )
        
        # Analiz tipine göre çalıştır
        if args.quick:
            results = analyzer.quick_analysis()
            print("Hızlı Analiz Sonuçları:")
            print(f"Toplam görüntü sayısı: {results.get('total_images', 'N/A')}")
            print(f"Toplam annotation sayısı: {results.get('total_annotations', 'N/A')}")
            print(f"Sınıf sayısı: {results.get('num_classes', 'N/A')}")
        else:
            report_path = analyzer.run_full_analysis()
            print(f"✅ Analiz tamamlandı!")
            print(f"📊 Rapor konumu: {report_path}")
            
    except KeyboardInterrupt:
        logger.info("Analiz kullanıcı tarafından durduruldu.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
