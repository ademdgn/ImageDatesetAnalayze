#!/usr/bin/env python3
"""
Enhanced Dataset Quality Analysis System
Modüler gelişmiş veri seti kalite analiz sistemi
"""

import argparse
import sys
import logging
from pathlib import Path

# Enhanced analyzer modülünü import et
from src.enhanced_analyzer import EnhancedDatasetAnalyzer

def create_argument_parser():
    """Komut satırı argüman parser'ını oluştur"""
    parser = argparse.ArgumentParser(
        description="Gelişmiş Görüntü Veri Seti Kalite Analizi - Modüler Sistem",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎯 KULLANIM ÖRNEKLERİ:

Hızlı Değerlendirme:
  python enhanced_main.py --dataset_path ./data/my_dataset --quick

Kapsamlı Analiz:
  python enhanced_main.py --dataset_path ./data/my_dataset --comprehensive

Format Belirtme:
  python enhanced_main.py --dataset_path ./data/my_dataset --format yolo --comprehensive

Özel Çıktı Dizini:
  python enhanced_main.py --dataset_path ./data/my_dataset --output ./custom_reports

Detaylı Log:
  python enhanced_main.py --dataset_path ./data/my_dataset --verbose --comprehensive

📊 ÇIKTI FORMATLARI:
  - JSON: Detaylı analiz sonuçları
  - TXT: İnsan okunabilir özet
  - CSV: Sayısal metrikler
  - Yönetici Özeti: Karar vericiler için özet

🔧 DESTEKLENEN FORMATLAR:
  - YOLO (.txt)
  - COCO (.json)
  - Pascal VOC (.xml)
  - LabelMe (.json)
  - Auto-detect (otomatik algılama)
        """
    )
    
    # Ana parametreler
    parser.add_argument(
        '--dataset_path', 
        type=str, 
        required=True,
        help='Veri seti dizin yolu (zorunlu)'
    )
    
    parser.add_argument(
        '--format', 
        type=str, 
        default='auto',
        choices=['auto', 'yolo', 'coco', 'pascal_voc', 'labelme'],
        help='Annotation formatı (varsayılan: auto)'
    )
    
    # Analiz modları
    analysis_group = parser.add_mutually_exclusive_group()
    analysis_group.add_argument(
        '--quick', 
        action='store_true',
        help='Hızlı değerlendirme modu (sadece temel istatistikler)'
    )
    analysis_group.add_argument(
        '--comprehensive', 
        action='store_true',
        help='Kapsamlı analiz modu (tam pipeline analizi)'
    )
    
    # Konfigürasyon
    parser.add_argument(
        '--config', 
        type=str, 
        default='config/config.yaml',
        help='Konfigürasyon dosyası yolu'
    )
    
    # Çıktı seçenekleri
    parser.add_argument(
        '--output', 
        type=str,
        help='Çıktı dizini (config dosyasındakini override eder)'
    )
    
    # Log seçenekleri
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Detaylı log çıktısı'
    )
    
    parser.add_argument(
        '--quiet', 
        action='store_true',
        help='Sadece hata mesajlarını göster'
    )
    
    # Raporlama seçenekleri
    parser.add_argument(
        '--no-reports', 
        action='store_true',
        help='Rapor dosyalarını kaydetme'
    )
    
    parser.add_argument(
        '--executive-summary', 
        action='store_true',
        help='Yönetici özeti oluştur'
    )
    
    # Temizlik seçenekleri
    parser.add_argument(
        '--cleanup', 
        type=int,
        metavar='N',
        help='Eski raporları temizle (son N tanesini sakla)'
    )
    
    return parser

def setup_logging(verbose: bool = False, quiet: bool = False):
    """Logging sistemini kur"""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    # Log dizinini oluştur
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Logging konfigürasyonu
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / 'enhanced_analysis.log', mode='a')
        ]
    )
    
    return logging.getLogger(__name__)

def validate_arguments(args):
    """Argümanları doğrula"""
    errors = []
    
    # Dataset path kontrolü
    if not Path(args.dataset_path).exists():
        errors.append(f"Veri seti dizini bulunamadı: {args.dataset_path}")
    
    # Config dosyası kontrolü (varsa)
    if args.config and not Path(args.config).exists():
        print(f"⚠️  Konfigürasyon dosyası bulunamadı: {args.config} (varsayılan kullanılacak)")
    
    # Çelişkili parametreler
    if args.verbose and args.quiet:
        errors.append("--verbose ve --quiet parametreleri birlikte kullanılamaz")
    
    return errors

def print_welcome_message():
    """Karşılama mesajını yazdır"""
    print("\n" + "="*80)
    print("🎯 ENHANCED DATASET QUALITY ANALYSIS SYSTEM")
    print("   Gelişmiş Veri Seti Kalite Analiz Sistemi v1.0")
    print("="*80)
    print("🚀 Modüler pipeline tabanlı kapsamlı kalite değerlendirmesi")
    print("📊 Akıllı skorlama ve otomatik öneri sistemi")
    print("📋 Çoklu rapor formatları ve yönetici özetleri")
    print("="*80)

def print_analysis_info(args):
    """Analiz bilgilerini yazdır"""
    print(f"\n📁 Veri Seti: {args.dataset_path}")
    print(f"🏷️  Format: {args.format.upper()}")
    
    if args.quick:
        print("⚡ Mod: Hızlı Değerlendirme")
    elif args.comprehensive:
        print("🔬 Mod: Kapsamlı Analiz")
    else:
        print("🎯 Mod: Standart Analiz (kapsamlı)")
    
    if args.output:
        print(f"📤 Çıktı: {args.output}")
    
    print()

def run_analysis(analyzer, args, logger):
    """Analizi çalıştır"""
    try:
        if args.quick:
            # Hızlı değerlendirme
            logger.info("Hızlı kalite değerlendirmesi başlatılıyor...")
            result = analyzer.run_quick_assessment()
        else:
            # Kapsamlı analiz (varsayılan)
            logger.info("Kapsamlı kalite analizi başlatılıyor...")
            result = analyzer.run_comprehensive_analysis()
        
        return result
        
    except KeyboardInterrupt:
        logger.info("Analiz kullanıcı tarafından durduruldu")
        return {'success': False, 'error': 'Kullanıcı tarafından durduruldu'}
    except Exception as e:
        logger.error(f"Analiz sırasında beklenmeyen hata: {str(e)}")
        return {'success': False, 'error': str(e)}

def print_results(result, args, logger):
    """Sonuçları yazdır"""
    if not result['success']:
        print(f"\n❌ ANALİZ BAŞARISIZ")
        print(f"Hata: {result.get('error', 'Bilinmeyen hata')}")
        return False
    
    # Başarı mesajı
    if args.quick:
        print("\n✅ HIZLI DEĞERLENDİRME TAMAMLANDI!")
        quick_score = result.get('quick_score', 0)
        grade = result.get('grade', 'F')
        print(f"📊 Hızlı Skor: {quick_score:.1f}/100 ({grade})")
    else:
        print("\n🎉 KAPSAMLI ANALİZ TAMAMLANDI!")
        if 'quality_metrics' in result:
            metrics = result['quality_metrics']
            print(f"📊 Genel Skor: {metrics.overall_score:.1f}/100")
            print(f"🎓 Veri Seti Notu: {metrics.dataset_grade}")
    
    # Raporları listele
    if 'report_paths' in result and result['report_paths']:
        print("\n📋 OLUŞTURULAN RAPORLAR:")
        for report_type, path in result['report_paths'].items():
            print(f"   📄 {report_type.replace('_', ' ').title()}: {path}")
    
    # Süre bilgisi
    if 'analysis_duration' in result:
        duration = result['analysis_duration']
        print(f"\n⏱️  Analiz Süresi: {duration:.1f} saniye")
    
    return True

def main():
    """Ana fonksiyon"""
    # Karşılama mesajı
    print_welcome_message()
    
    # Argümanları parse et
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Varsayılan olarak comprehensive analiz yap
    if not args.quick and not args.comprehensive:
        args.comprehensive = True
    
    # Argümanları doğrula
    validation_errors = validate_arguments(args)
    if validation_errors:
        print("❌ PARAMETRE HATALARI:")
        for error in validation_errors:
            print(f"   • {error}")
        sys.exit(1)
    
    # Logging'i kur
    logger = setup_logging(args.verbose, args.quiet)
    
    # Analiz bilgilerini yazdır
    print_analysis_info(args)
    
    try:
        # Enhanced Analyzer'ı başlat
        config = {}
        if args.output:
            config['output'] = {'reports_dir': args.output}
        if args.no_reports:
            config['output'] = {
                'save_detailed_report': False,
                'save_summary_report': False,
                'save_csv_report': False,
                'save_recommendations': False
            }
        
        logger.info(f"Enhanced Analyzer başlatılıyor: {args.dataset_path}")
        analyzer = EnhancedDatasetAnalyzer(
            dataset_path=args.dataset_path,
            annotation_format=args.format,
            config=config
        )
        
        # Temizlik işlemi (varsa)
        if args.cleanup:
            logger.info(f"Eski raporlar temizleniyor (son {args.cleanup} saklanacak)...")
            analyzer.cleanup_old_reports(args.cleanup)
            print(f"🗑️  Eski raporlar temizlendi (son {args.cleanup} saklandı)")
        
        # Analizi çalıştır
        result = run_analysis(analyzer, args, logger)
        
        # Sonuçları yazdır
        success = print_results(result, args, logger)
        
        # Yönetici özeti (istenirse)
        if args.executive_summary and result['success'] and 'quality_metrics' in result:
            summary_path = analyzer.report_manager.save_executive_summary(result['quality_metrics'])
            if summary_path:
                print(f"\n👔 Yönetici özeti kaydedildi: {summary_path}")
        
        # Başarı durumuna göre çıkış kodu
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Kritik sistem hatası: {str(e)}")
        print(f"\n💥 KRİTİK HATA: {str(e)}")
        print("\n🔧 Çözüm önerileri:")
        print("   • Veri seti yolunun doğru olduğundan emin olun")
        print("   • Dosya izinlerini kontrol edin")
        print("   • --verbose parametresi ile detaylı log alın")
        print("   • Konfigürasyon dosyasını kontrol edin")
        sys.exit(1)

if __name__ == "__main__":
    main()
