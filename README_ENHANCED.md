# 🎯 Enhanced Dataset Quality Analysis System

Gelişmiş, modüler veri seti kalite analiz sistemi. Görüntü veri setlerinin kapsamlı kalite değerlendirmesi, akıllı skorlama ve otomatik öneri sistemi.

## 🚀 Özellikler

### 🔍 Kapsamlı Analiz
- **Görüntü Kalitesi**: Çözünürlük, netlik, parlaklık, kontrast analizi
- **Annotation Kalitesi**: Sınıf dağılımı, bounding box kalitesi, tutarlılık
- **Eksiksizlik Kontrolü**: Dosya bütünlüğü, eşleşme oranları
- **Çeşitlilik Değerlendirmesi**: Veri zenginliği ve dağılım analizi
- **Tutarlılık Kontrolü**: Standardizasyon ve kalite tutarlılığı

### 🧠 Akıllı Sistemler
- **Pipeline Tabanlı İşleme**: Modüler, ölçeklenebilir analiz süreci
- **Otomatik Skorlama**: Çok boyutlu kalite skorlama algoritması
- **Öneri Motoru**: Veri setini iyileştirmek için akıllı öneriler
- **Karşılaştırma Sistemi**: Baseline ile performans karşılaştırması

### 📊 Raporlama
- **Çoklu Format**: JSON, TXT, CSV, Yönetici Özeti
- **Görselleştirme**: Detaylı grafikler ve metrikler
- **İnteraktif Raporlar**: Karar vericiler için özel formatlar

## 📦 Kurulum

```bash
# Repository'yi klonlayın
git clone [repository-url]
cd ImageDatasetAnalyze

# Gerekli paketleri yükleyin
pip install -r requirements.txt

# Test sistemi çalıştırın
python test_enhanced_system.py
```

## 🎮 Kullanım

### Hızlı Değerlendirme
```bash
python enhanced_main.py --dataset_path ./data/my_dataset --quick
```

### Kapsamlı Analiz
```bash
python enhanced_main.py --dataset_path ./data/my_dataset --comprehensive
```

### Format Belirtme
```bash
python enhanced_main.py --dataset_path ./data/my_dataset --format yolo --comprehensive
```

### Özel Çıktı Dizini
```bash
python enhanced_main.py --dataset_path ./data/my_dataset --output ./custom_reports
```

### Detaylı Log
```bash
python enhanced_main.py --dataset_path ./data/my_dataset --verbose --comprehensive
```

### Yönetici Özeti
```bash
python enhanced_main.py --dataset_path ./data/my_dataset --executive-summary
```

## 📁 Proje Yapısı

```
ImageDatasetAnalyze/
├── src/
│   ├── enhanced_analyzer/           # Ana gelişmiş sistem
│   │   ├── core_analyzer.py        # Ana analiz motoru
│   │   ├── config_manager.py       # Konfigürasyon yönetimi
│   │   ├── report_manager.py       # Rapor yönetimi
│   │   └── analysis_pipeline.py    # Pipeline sistemi
│   ├── quality_assessor/           # Kalite değerlendirme
│   │   ├── base_assessor.py        # Temel assessor
│   │   ├── quality_scorer.py       # Skorlama algoritmaları
│   │   ├── completeness_checker.py # Eksiksizlik kontrolü
│   │   └── recommendation_engine.py # Öneri motoru
│   ├── data_loader.py              # Veri yükleme
│   └── image_analyzer.py           # Görüntü analizi
├── config/
│   └── config.yaml                 # Konfigürasyon
├── data/
│   ├── input/                      # Giriş veri setleri
│   └── output/                     # Analiz sonuçları
├── enhanced_main.py                # Ana çalıştırma dosyası
└── test_enhanced_system.py         # Test sistemi
```

## 🔧 Konfigürasyon

`config/config.yaml` dosyasından sistem ayarlarını özelleştirebilirsiniz:

```yaml
analysis:
  min_samples_per_class: 50
  quality_threshold: 0.7
  image_size_threshold: 224

quality_scoring:
  weights:
    image_quality: 0.25
    annotation_quality: 0.25
    completeness: 0.20
    diversity: 0.15
    consistency: 0.15

output:
  reports_dir: 'data/output'
  save_detailed_report: true
  save_summary_report: true
```

## 📊 Çıktı Formatları

### 1. Hızlı Değerlendirme
- Temel istatistikler
- Hızlı kalite skoru (0-100)
- Genel durum değerlendirmesi

### 2. Kapsamlı Analiz
- Detaylı kalite metrikleri
- Bileşen bazlı skorlar
- Otomatik öneriler
- Pipeline performans analizi
- Çoklu rapor formatları

### 3. Yönetici Özeti
- İş seviyesi özet
- Karar destek bilgileri
- Aksiyonlar ve öncelikler
- Risk değerlendirmesi

## 📈 Kalite Metrikleri

### Skorlama Sistemi
- **A (90-100)**: Mükemmel - Üretim için hazır
- **B (75-89)**: İyi - Minor iyileştirmeler
- **C (60-74)**: Orta - Önemli iyileştirmeler gerekli
- **D (0-59)**: Düşük - Major revizyonlar gerekli

### Değerlendirme Kriterleri
1. **Görüntü Kalitesi**: Çözünürlük, netlik, parlaklık, kontrast
2. **Annotation Kalitesi**: Sınıf denge, bbox kalitesi, tutarlılık
3. **Eksiksizlik**: Dosya bütünlüğü, eşleşme oranları
4. **Çeşitlilik**: Veri zenginliği, dağılım çeşitliliği
5. **Tutarlılık**: Standardizasyon, kalite tutarlılığı

## 🔧 Desteklenen Formatlar

- **YOLO** (.txt): class_id x_center y_center width height
- **COCO** (.json): Microsoft COCO format
- **Pascal VOC** (.xml): Visual Object Classes format
- **LabelMe** (.json): LabelMe annotation format
- **Auto-detect**: Otomatik format algılama

## 📚 API Kullanımı

### Python API
```python
from src.enhanced_analyzer import EnhancedDatasetAnalyzer

# Analyzer'ı başlat
analyzer = EnhancedDatasetAnalyzer(
    dataset_path="./data/my_dataset",
    annotation_format="yolo"
)

# Hızlı değerlendirme
quick_result = analyzer.run_quick_assessment()
print(f"Hızlı Skor: {quick_result['quick_score']}/100")

# Kapsamlı analiz
full_result = analyzer.run_comprehensive_analysis()
print(f"Genel Skor: {full_result['quality_metrics'].overall_score}/100")
```

### Konfigürasyon Yönetimi
```python
from src.enhanced_analyzer.config_manager import ConfigManager

config_manager = ConfigManager()
config = config_manager.load_config()

# Ayarları güncelle
config_manager.set_value('analysis.quality_threshold', 0.8)
config_manager.save_config('my_config.yaml')
```

## 🧪 Test

### Sistem Testleri
```bash
# Tüm bileşenleri test et
python test_enhanced_system.py
```

### Test Kapsamı
- ✅ Modül import testleri
- ✅ Config yönetimi testleri
- ✅ Pipeline sistem testleri
- ✅ Enhanced analyzer testleri
- ✅ Entegrasyon testleri

## 📊 Performans

### Benchmarklar
- **Hızlı Değerlendirme**: ~30 saniye (1000 görüntü)
- **Kapsamlı Analiz**: ~5-10 dakika (1000 görüntü)
- **Bellek Kullanımı**: ~2-4 GB (büyük veri setleri için)

### Optimizasyon İpuçları
- Büyük veri setleri için batch processing kullanın
- SSD kullanımı I/O performansını artırır
- Paralel işleme için `max_workers` ayarını optimize edin

## 🔍 Sorun Giderme

### Sık Karşılaşılan Sorunlar

**Import hatası**:
```bash
ModuleNotFoundError: No module named 'src'
```
Çözüm: Proje ana dizininden çalıştırdığınızdan emin olun.

**Veri seti bulunamadı**:
```bash
Dataset directory not found
```
Çözüm: Veri seti yolunu kontrol edin ve mutlak yol kullanmayı deneyin.

**Bellek hatası**:
```bash
MemoryError: Unable to allocate array
```
Çözüm: Config dosyasında `batch_size` ve `memory_limit_gb` ayarlarını azaltın.

### Debug Modu
```bash
python enhanced_main.py --dataset_path ./data --verbose --comprehensive
```

## 👥 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Ayrıntılar için `LICENSE` dosyasına bakın.

## 🚀 Geliştirme Yol Haritası

### v1.1 (Planlanan)
- [ ] Web arayüzü
- [ ] Real-time monitoring
- [ ] API endpoint'leri
- [ ] Docker containerization

### v1.2 (Gelecek)
- [ ] Machine learning model performans analizi
- [ ] Benchmark karşılaştırma
- [ ] Otomatik veri augmentation önerileri
- [ ] Cloud storage entegrasyonu

## 📞 Destek

Sorularınız için:
- GitHub Issues kullanın
- Dokümantasyonu kontrol edin
- Test sistemini çalıştırın: `python test_enhanced_system.py`

---

**🎉 Enhanced Dataset Quality Analysis System ile veri setlerinizin kalitesini bir üst seviyeye taşıyın!**
