#!/usr/bin/env python3
"""
Görüntü Analizörü Kapsamlı Test Scripti

Bu script yeni modüler image_analyzer yapısını test eder.
"""

import sys
import os
import tempfile
import numpy as np
from pathlib import Path
from PIL import Image
import cv2

# Ana dizini path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_test_image(width=640, height=480, color_mode='RGB', 
                     noise_level=0, blur_level=0, brightness=128):
    """
    Test için sahte görüntü oluştur
    
    Args:
        width: Görüntü genişliği
        height: Görüntü yüksekliği
        color_mode: Renk modu ('RGB', 'L', vb.)
        noise_level: Noise seviyesi (0-100)
        blur_level: Bulanıklık seviyesi (0-10)
        brightness: Parlaklık seviyesi (0-255)
        
    Returns:
        PIL Image objesi
    """
    # Rastgele görüntü oluştur
    if color_mode == 'RGB':
        low_val = max(0, brightness-50)
        high_val = min(255, brightness+50)
        img_array = np.random.randint(low_val, high_val+1, (height, width, 3), dtype=np.uint8)
    else:
        low_val = max(0, brightness-50)
        high_val = min(255, brightness+50)
        img_array = np.random.randint(low_val, high_val+1, (height, width), dtype=np.uint8)
    
    # Noise ekle
    if noise_level > 0:
        noise = np.random.randint(-noise_level, noise_level, img_array.shape, dtype=np.int16)
        img_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # PIL Image'e dönüştür
    img = Image.fromarray(img_array, mode=color_mode)
    
    # Blur ekle
    if blur_level > 0:
        from PIL import ImageFilter
        img = img.filter(ImageFilter.GaussianBlur(radius=blur_level))
    
    return img

def create_test_dataset(num_images=10):
    """
    Test için geçici dataset oluştur
    
    Args:
        num_images: Oluşturulacak görüntü sayısı
        
    Returns:
        (temp_dir, image_paths) tuple'ı
    """
    temp_dir = tempfile.mkdtemp(prefix="test_dataset_")
    image_paths = []
    
    print(f"📁 Geçici test dataset'i oluşturuluyor: {temp_dir}")
    
    for i in range(num_images):
        # Çeşitli özelliklerde test görüntüleri oluştur
        test_scenarios = [
            {'width': 640, 'height': 480, 'brightness': 128, 'noise_level': 0, 'blur_level': 0},  # Normal
            {'width': 1280, 'height': 720, 'brightness': 180, 'noise_level': 5, 'blur_level': 0},  # Parlak
            {'width': 320, 'height': 240, 'brightness': 60, 'noise_level': 0, 'blur_level': 0},   # Küçük, karanlık
            {'width': 800, 'height': 600, 'brightness': 128, 'noise_level': 20, 'blur_level': 0}, # Noisy
            {'width': 1024, 'height': 768, 'brightness': 128, 'noise_level': 0, 'blur_level': 3}, # Bulanık
        ]
        
        scenario = test_scenarios[i % len(test_scenarios)]
        
        # Test görüntüsü oluştur
        img = create_test_image(**scenario)
        
        # Kaydet
        img_path = Path(temp_dir) / f"test_image_{i:03d}.jpg"
        img.save(img_path, 'JPEG', quality=85)
        image_paths.append(str(img_path))
    
    print(f"✅ {num_images} test görüntüsü oluşturuldu")
    return temp_dir, image_paths

def test_imports():
    """Modül import'larını test et"""
    print("\n" + "="*60)
    print("🔍 MODÜL IMPORT TESTLERİ")
    print("="*60)
    
    try:
        from src.image_analyzer import ImageAnalyzer
        print("✅ ImageAnalyzer import başarılı")
    except ImportError as e:
        print(f"❌ ImageAnalyzer import hatası: {e}")
        return False
    
    try:
        from src.image_analyzer import QualityMetricsCalculator
        print("✅ QualityMetricsCalculator import başarılı")
    except ImportError as e:
        print(f"❌ QualityMetricsCalculator import hatası: {e}")
        return False
    
    try:
        from src.image_analyzer import AnomalyDetector
        print("✅ AnomalyDetector import başarılı")
    except ImportError as e:
        print(f"❌ AnomalyDetector import hatası: {e}")
        return False
    
    try:
        from src.image_analyzer import StatisticsCalculator
        print("✅ StatisticsCalculator import başarılı")
    except ImportError as e:
        print(f"❌ StatisticsCalculator import hatası: {e}")
        return False
    
    try:
        from src.image_analyzer import quick_image_analysis, create_image_analyzer
        print("✅ Yardımcı fonksiyonlar import başarılı")
    except ImportError as e:
        print(f"❌ Yardımcı fonksiyonlar import hatası: {e}")
        return False
    
    return True

def test_basic_image_analysis():
    """Temel görüntü analizi fonksiyonlarını test et"""
    print("\n" + "="*60)
    print("🖼️  TEMEL GÖRÜNTÜ ANALİZİ TESTLERİ")
    print("="*60)
    
    from src.image_analyzer import ImageAnalyzer
    
    # Test görüntüsü oluştur
    temp_dir, image_paths = create_test_dataset(5)
    
    try:
        # Analyzer oluştur
        config = {
            'blur_threshold': 100.0,
            'min_brightness': 30,
            'max_brightness': 225,
            'min_image_size': 200,
            'max_image_size': 2000
        }
        
        analyzer = ImageAnalyzer(config)
        print("✅ ImageAnalyzer oluşturuldu")
        
        # Tek görüntü analizi test et
        test_image = image_paths[0]
        print(f"📸 Test görüntüsü analiz ediliyor: {Path(test_image).name}")
        
        properties = analyzer.analyze_image_properties(test_image)
        
        if properties.get('analysis_failed', False):
            print(f"❌ Görüntü analizi başarısız: {properties.get('error')}")
            return False
        
        # Temel özellikleri kontrol et
        required_properties = [
            'width', 'height', 'file_size_mb', 'quality_score',
            'brightness_mean', 'contrast_score', 'blur_score'
        ]
        
        for prop in required_properties:
            if prop not in properties:
                print(f"❌ Eksik özellik: {prop}")
                return False
            print(f"  ✓ {prop}: {properties[prop]}")
        
        print("✅ Tek görüntü analizi başarılı")
        
        # Temizlik
        import shutil
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Temel analiz testi hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quality_metrics():
    """Kalite metriklerini test et"""
    print("\n" + "="*60)
    print("📊 KALİTE METRİKLERİ TESTLERİ")
    print("="*60)
    
    from src.image_analyzer.quality_metrics import QualityMetricsCalculator
    
    try:
        # Test görüntüsü oluştur
        test_img = create_test_image(640, 480, brightness=128)
        
        # OpenCV formatına dönüştür
        cv_img = cv2.cvtColor(np.array(test_img), cv2.COLOR_RGB2BGR)
        
        # Calculator oluştur
        calc = QualityMetricsCalculator()
        print("✅ QualityMetricsCalculator oluşturuldu")
        
        # Blur score test
        blur_score = calc.calculate_blur_score(cv_img)
        print(f"  ✓ Blur score: {blur_score}")
        assert isinstance(blur_score, float) and blur_score >= 0
        
        # Brightness stats test
        brightness_stats = calc.calculate_brightness_stats(cv_img)
        print(f"  ✓ Brightness: {brightness_stats}")
        assert 'mean' in brightness_stats and 'std' in brightness_stats
        
        # Contrast score test
        contrast_score = calc.calculate_contrast_score(cv_img)
        print(f"  ✓ Contrast: {contrast_score}")
        assert isinstance(contrast_score, float) and contrast_score >= 0
        
        # Color statistics test
        color_stats = calc.calculate_color_statistics(test_img, cv_img)
        print(f"  ✓ Color stats: {len(color_stats)} özellik")
        assert 'red_mean' in color_stats and 'green_mean' in color_stats
        
        # Tüm metrikleri hesapla
        all_metrics = calc.calculate_all_metrics(test_img, cv_img)
        print(f"  ✓ Toplam metrik sayısı: {len(all_metrics)}")
        assert 'quality_score' in all_metrics
        assert 0 <= all_metrics['quality_score'] <= 100
        
        print("✅ Kalite metrikleri testleri başarılı")
        return True
        
    except Exception as e:
        print(f"❌ Kalite metrikleri testi hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_anomaly_detection():
    """Anomali tespiti test et"""
    print("\n" + "="*60)
    print("🔍 ANOMALİ TESPİTİ TESTLERİ")
    print("="*60)
    
    from src.image_analyzer.anomaly_detector import AnomalyDetector
    from src.image_analyzer import ImageAnalyzer
    
    try:
        # Test dataset oluştur (anomalili)
        temp_dir, image_paths = create_test_dataset(10)
        
        # Bazı extreme test görüntüleri ekle
        extreme_scenarios = [
            {'width': 100, 'height': 100, 'brightness': 20},    # Çok küçük, karanlık
            {'width': 2000, 'height': 1500, 'brightness': 240}, # Çok büyük, parlak
            {'width': 640, 'height': 480, 'blur_level': 5},     # Çok bulanık
        ]
        
        for i, scenario in enumerate(extreme_scenarios):
            img = create_test_image(**scenario)
            extreme_path = Path(temp_dir) / f"extreme_{i}.jpg"
            img.save(extreme_path, 'JPEG', quality=85)
            image_paths.append(str(extreme_path))
        
        # Görüntüleri analiz et
        analyzer = ImageAnalyzer()
        print("📸 Test görüntüleri analiz ediliyor...")
        
        properties_list = []
        for img_path in image_paths:
            props = analyzer.analyze_image_properties(img_path)
            if not props.get('analysis_failed', False):
                properties_list.append(props)
        
        print(f"✅ {len(properties_list)} görüntü analiz edildi")
        
        # Anomali detector test
        detector = AnomalyDetector()
        print("🔍 Anomaliler tespit ediliyor...")
        
        # Kalite anomalileri
        quality_anomalies = detector.detect_quality_anomalies(properties_list)
        print(f"  ✓ Kalite anomalileri: {sum(len(v) for v in quality_anomalies.values())} adet")
        
        # İstatistiksel outlier'lar
        statistical_outliers = detector.detect_statistical_outliers(properties_list)
        print(f"  ✓ İstatistiksel outlier'lar: {len(statistical_outliers)} adet")
        
        # Tüm anomaliler
        all_anomalies = detector.detect_all_anomalies(properties_list)
        total_anomalies = all_anomalies['summary']['total_anomalies']
        print(f"  ✓ Toplam anomali sayısı: {total_anomalies}")
        
        # Rapor oluştur
        report = detector.generate_anomaly_report(all_anomalies)
        print(f"  ✓ Anomali raporu: {len(report)} satır")
        
        print("✅ Anomali tespiti testleri başarılı")
        
        # Temizlik
        import shutil
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Anomali tespiti testi hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_statistics_calculator():
    """İstatistik hesaplayıcısını test et"""
    print("\n" + "="*60)
    print("📈 İSTATİSTİK HESAPLAYICI TESTLERİ")
    print("="*60)
    
    from src.image_analyzer.statistics_calculator import StatisticsCalculator
    from src.image_analyzer import ImageAnalyzer
    
    try:
        # Test dataset oluştur
        temp_dir, image_paths = create_test_dataset(8)
        
        # Görüntüleri analiz et
        analyzer = ImageAnalyzer()
        properties_list = []
        
        for img_path in image_paths:
            props = analyzer.analyze_image_properties(img_path)
            if not props.get('analysis_failed', False):
                properties_list.append(props)
        
        # Statistics calculator test
        calc = StatisticsCalculator()
        print("✅ StatisticsCalculator oluşturuldu")
        
        # Dataset istatistikleri
        stats = calc.calculate_dataset_statistics(properties_list)
        print(f"  ✓ Dataset istatistikleri: {len(stats)} kategori")
        
        # Çeşitlilik metrikleri
        diversity = calc.calculate_diversity_metrics(properties_list)
        print(f"  ✓ Çeşitlilik metrikleri: {len(diversity)} metrik")
        assert 'overall_diversity_score' in diversity
        
        # Kalite özeti
        quality_summary = calc.generate_quality_summary(properties_list)
        print(f"  ✓ Kalite özeti: {quality_summary.get('overall_grade', 'N/A')} notu")
        
        # Korelasyonlar
        correlations = calc.calculate_correlations(properties_list)
        print(f"  ✓ Korelasyonlar: {len(correlations)} çift")
        
        # Öneriler
        recommendations = calc.generate_recommendations(properties_list)
        print(f"  ✓ Öneriler: {len(recommendations)} öneri")
        
        print("✅ İstatistik hesaplayıcı testleri başarılı")
        
        # Temizlik
        import shutil
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ İstatistik hesaplayıcı testi hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_dataset_analysis():
    """Tam dataset analizi test et"""
    print("\n" + "="*60)
    print("🎯 TAM DATASET ANALİZİ TESTİ")
    print("="*60)
    
    from src.image_analyzer import ImageAnalyzer
    
    try:
        # Büyük test dataset oluştur
        temp_dir, image_paths = create_test_dataset(15)
        
        # Analyzer oluştur
        config = {
            'blur_threshold': 100.0,
            'min_brightness': 30,
            'max_brightness': 225,
            'quality_thresholds': {
                'excellent': 85,
                'good': 70,
                'fair': 50
            }
        }
        
        analyzer = ImageAnalyzer(config)
        print("✅ Analyzer oluşturuldu")
        
        # Tam analiz yap
        print("🔄 Tam dataset analizi başlatılıyor...")
        results = analyzer.analyze_dataset_images(image_paths)
        
        # Sonuçları kontrol et
        required_sections = [
            'total_images', 'analyzed_images', 'success_rate',
            'dataset_statistics', 'quality_summary', 'diversity_metrics',
            'anomaly_results', 'recommendations', 'analysis_summary'
        ]
        
        for section in required_sections:
            if section not in results:
                print(f"❌ Eksik bölüm: {section}")
                return False
            print(f"  ✓ {section}: ✅")
        
        # Analiz özetini yazdır
        summary = results['analysis_summary']
        print(f"\n📋 ANALİZ ÖZETİ:")
        print(f"  • Toplam görüntü: {summary.get('total_images', 0)}")
        print(f"  • Ortalama kalite: {summary.get('average_quality_score', 0):.1f}/100")
        print(f"  • Kalite notu: {summary.get('quality_grade', 'N/A')}")
        print(f"  • Çeşitlilik skoru: {summary.get('diversity_score', 0):.3f}")
        print(f"  • Dataset skoru: {summary.get('overall_dataset_score', 0):.1f}/100")
        print(f"  • Sağlık durumu: {summary.get('dataset_health', 'N/A')}")
        
        # Önerileri yazdır
        print(f"\n💡 ÖNERİLER:")
        for rec in results['recommendations'][:3]:  # İlk 3 öneri
            print(f"  • {rec}")
        
        # Metin özeti test et
        text_summary = analyzer.get_analysis_summary_text()
        print(f"\n📄 Metin özeti: {len(text_summary)} karakter")
        
        print("✅ Tam dataset analizi testi başarılı")
        
        # Temizlik
        import shutil
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Tam dataset analizi testi hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quick_analysis():
    """Hızlı analiz fonksiyonunu test et"""
    print("\n" + "="*60)
    print("⚡ HIZLI ANALİZ TESTİ")
    print("="*60)
    
    from src.image_analyzer import quick_image_analysis
    
    try:
        # Büyük test dataset oluştur
        temp_dir, image_paths = create_test_dataset(20)
        
        # Hızlı analiz test et
        print("⚡ Hızlı analiz başlatılıyor...")
        results = quick_image_analysis(image_paths, sample_size=10)
        
        # Sonuçları kontrol et
        assert results['is_sample_analysis'] == True
        assert results['sample_size'] <= 10
        assert results['total_available'] == 20
        
        print(f"  ✓ Örnek boyutu: {results['sample_size']}")
        print(f"  ✓ Toplam mevcut: {results['total_available']}")
        print(f"  ✓ Örnekleme oranı: %{results['sample_ratio']*100:.1f}")
        
        print("✅ Hızlı analiz testi başarılı")
        
        # Temizlik
        import shutil
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Hızlı analiz testi hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_real_dataset():
    """Gerçek dataset ile test et (varsa)"""
    print("\n" + "="*60)
    print("🎯 GERÇEK DATASET TESTİ")
    print("="*60)
    
    # Gerçek dataset yolunu kontrol et
    real_dataset_path = Path("data/input/yolov11_dataset_vol1/train/images")
    
    if not real_dataset_path.exists():
        print("⚠️ Gerçek dataset bulunamadı, test atlanıyor")
        return True
    
    from src.image_analyzer import ImageAnalyzer
    
    try:
        # Gerçek görüntüleri bul
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        image_paths = []
        
        for img_file in real_dataset_path.iterdir():
            if img_file.suffix.lower() in image_extensions:
                image_paths.append(str(img_file))
        
        if not image_paths:
            print("⚠️ Gerçek dataset'te görüntü bulunamadı")
            return True
        
        # İlk 5 görüntü ile test et
        test_images = image_paths[:5]
        print(f"📸 {len(test_images)} gerçek görüntü ile test yapılıyor...")
        
        # Analyzer oluştur
        analyzer = ImageAnalyzer()
        
        # Her görüntüyü tek tek test et
        for i, img_path in enumerate(test_images):
            print(f"  {i+1}. {Path(img_path).name}")
            
            properties = analyzer.analyze_image_properties(img_path)
            
            if properties.get('analysis_failed', False):
                print(f"    ❌ Analiz başarısız: {properties.get('error')}")
            else:
                print(f"    ✅ Kalite: {properties.get('quality_score', 0):.1f}/100")
                print(f"    📐 Boyut: {properties.get('width')}x{properties.get('height')}")
        
        print("✅ Gerçek dataset testi başarılı")
        return True
        
    except Exception as e:
        print(f"❌ Gerçek dataset testi hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Tüm testleri çalıştır"""
    print("🧪 GÖRÜNTÜ ANALİZÖRÜ KAPSAMLI TEST SÜİTİ")
    print("="*80)
    
    tests = [
        ("Import Testleri", test_imports),
        ("Temel Görüntü Analizi", test_basic_image_analysis),
        ("Kalite Metrikleri", test_quality_metrics),
        ("Anomali Tespiti", test_anomaly_detection),
        ("İstatistik Hesaplayıcı", test_statistics_calculator),
        ("Tam Dataset Analizi", test_full_dataset_analysis),
        ("Hızlı Analiz", test_quick_analysis),
        ("Gerçek Dataset", test_real_dataset),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔄 {test_name} çalıştırılıyor...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} BAŞARILI")
            else:
                failed += 1
                print(f"❌ {test_name} BAŞARISIZ")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} HATA: {e}")
    
    # Sonuç özeti
    print("\n" + "="*80)
    print("🏁 TEST SONUÇLARI")
    print("="*80)
    print(f"✅ Başarılı: {passed}")
    print(f"❌ Başarısız: {failed}")
    print(f"📊 Başarı oranı: %{(passed/(passed+failed))*100:.1f}")
    
    if failed == 0:
        print("\n🎉 TÜM TESTLER BAŞARILI! Modül production'a hazır.")
    else:
        print(f"\n⚠️ {failed} test başarısız. Sorunları giderdikten sonra tekrar test edin.")
    
    return failed == 0

if __name__ == "__main__":
    print("🚀 Test süiti başlatılıyor...")
    
    # Gerekli kütüphaneleri kontrol et
    required_packages = ['PIL', 'cv2', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Eksik paketler: {missing_packages}")
        print("📦 pip install pillow opencv-python numpy komutu ile yükleyebilirsiniz")
        sys.exit(1)
    
    # Tüm testleri çalıştır
    success = run_all_tests()
    
    sys.exit(0 if success else 1)
