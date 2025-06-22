# 🔍 Görüntü Veri Seti Kalite Analizi

Bu proje, görüntü veri setlerinin kalitesini analiz eden, nesne tespiti (object detection) verilerini değerlendiren ve veri setinin yeterliliğini raporlayan kapsamlı bir analiz aracıdır.

## 🎯 Özellikler

- **Çoklu Format Desteği**: YOLO, COCO, Pascal VOC, LabelMe formatları
- **Kapsamlı Analiz**: Görüntü kalitesi, annotation kalitesi, sınıf dağılımı
- **Görselleştirme**: İnteraktif grafikler ve detaylı raporlar
- **Otomatik Skorlama**: Veri seti kalite puanı ve iyileştirme önerileri
- **Hızlı ve Detay Modları**: İhtiyaca göre hızlı veya detaylı analiz

## 📋 Kurulum

### Gereksinimler
- Python 3.8+
- Pip package manager

### Kurulum Adımları

```bash
# Repository'yi klonlayın
git clone [repository-url]
cd ImageDatasetAnalyze

# Sanal ortam oluşturun (önerilen)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Gerekli paketleri yükleyin
pip install -r requirements.txt
```

## 🚀 Kullanım

### Temel Kullanım

```bash
# Tam analiz
python main.py --dataset_path "path/to/your/dataset" --format yolo

# Hızlı analiz (sadece temel istatistikler)
python main.py --dataset_path "path/to/your/dataset" --format yolo --quick

# Farklı annotation formatı
python main.py --dataset_path "path/to/your/dataset" --format coco
```

### Parametre Seçenekleri

- `--dataset_path`: Veri seti dizin yolu (zorunlu)
- `--format`: Annotation formatı (yolo, coco, pascal_voc, labelme)
- `--config`: Konfigürasyon dosyası yolu
- `--quick`: Hızlı analiz modu
- `--output`: Çıktı dizini

### Python API Kullanımı

```python
from src import DatasetQualityAnalyzer

# Analyzer oluştur
analyzer = DatasetQualityAnalyzer(
    dataset_path="path/to/dataset",
    annotation_format="yolo"
)

# Tam analiz çalıştır
report_path = analyzer.run_full_analysis()

# Hızlı analiz
basic_stats = analyzer.quick_analysis()
```

## 📊 Analiz Metrikleri

### Görüntü Kalitesi
- Çözünürlük dağılımı
- Parlaklık/kontrast analizi
- Bulanıklık tespiti
- Renk kanalı dağılımları

### Annotation Kalitesi
- Sınıf dağılımı ve imbalance
- Bounding box istatistikleri
- Annotation tutarlılık kontrolü
- IoU analizleri

### Veri Seti Değerlendirmesi
- Genel kalite skoru (A-D arası)
- Sınıf başına yeterlilik
- Çeşitlilik metrikleri
- İyileştirme önerileri

## 📁 Veri Seti Formatları

### YOLO Format
```
dataset/
├── images/
│   ├── train/
│   └── val/
├── labels/
│   ├── train/
│   └── val/
└── classes.txt
```

### COCO Format
```
dataset/
├── images/
└── annotations/
    └── instances.json
```

### Pascal VOC Format
```
dataset/
├── JPEGImages/
└── Annotations/
```

## ⚙️ Konfigürasyon

`config/config.yaml` dosyasından analiz parametrelerini özelleştirebilirsiniz:

```yaml
analysis:
  min_samples_per_class: 50
  quality_threshold: 0.7
  max_class_imbalance: 0.8

visualization:
  figure_size: [12, 8]
  color_palette: "viridis"
  save_plots: true

reporting:
  format: "html"
  output_dir: "data/output"
```

## 📈 Çıktı Raporları

Analiz sonucunda şu dosyalar oluşturulur:

- **HTML Raporu**: Detaylı analiz sonuçları ve grafikler
- **Görselleştirmeler**: PNG/PDF formatında grafikler
- **JSON Sonuçları**: Ham analiz verileri
- **Öneri Raporu**: İyileştirme önerileri

## 🎯 Kalite Skorları

- **A (90-100)**: Mükemmel veri seti
- **B (75-89)**: İyi kalite, minor iyileştirmeler
- **C (60-74)**: Orta kalite, önemli iyileştirmeler gerekli
- **D (0-59)**: Yetersiz, major iyileştirmeler gerekli

## 🔧 Geliştirme

### Test Çalıştırma
```bash
pytest tests/
```

### Katkıda Bulunma
1. Fork'layın
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Destek

Sorularınız için:
- Issue oluşturun
- E-mail: adem.dogan6771@gmail.com

## 📋 Changelog

### v1.0.0
- İlk sürüm
- HTML rapor desteği
- Çoklu format desteği
