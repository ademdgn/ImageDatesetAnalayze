# Görüntü Veri Seti Analiz ve Değerlendirme Projesi
## Detaylı Proje Taslağı ve Geliştirme Rehberi

### 🎯 Proje Amacı
Bu proje, görüntü veri setlerinin kalitesini analiz eden, nesne tespiti (object detection) verilerini değerlendiren ve veri setinin yeterliliğini raporlayan kapsamlı bir analiz aracı geliştirmeyi hedeflemektedir.

---

## 📋 Proje Özellikleri

### Temel Fonksiyonlar
- **Veri Seti Yükleme ve Analizi**: Farklı formatlarda veri setlerini destekleme
- **Nesne Tespiti Analizi**: YOLO, COCO, Pascal VOC formatları desteği
- **Sınıf Dağılımı Analizi**: Class imbalance tespiti ve görselleştirme
- **Veri Kalitesi Değerlendirmesi**: Görüntü kalitesi, annotation kalitesi analizi
- **İstatistiksel Raporlama**: Detaylı grafikler ve metrikler
- **Otomatik Öneriler**: Veri setini iyileştirme önerileri

---

## 🛠️ Teknoloji Stack'i

### Python Kütüphaneleri
```python
# Temel kütüphaneler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Görüntü işleme
import cv2
import PIL
from PIL import Image, ImageStat
import albumentations as A

# Machine Learning
import sklearn
from sklearn.cluster import KMeans
from sklearn.metrics import classification_report

# Veri analizi
import json
import xml.etree.ElementTree as ET
import yaml
import os
from pathlib import Path
```

---

## 📁 Proje Yapısı

```
veri_analiz_projesi/
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py          # Veri yükleme modülü
│   ├── image_analyzer.py       # Görüntü analiz modülü
│   ├── annotation_analyzer.py  # Annotation analiz modülü
│   ├── quality_assessor.py     # Kalite değerlendirme modülü
│   ├── visualizer.py          # Görselleştirme modülü
│   └── report_generator.py    # Rapor oluşturma modülü
│
├── data/
│   ├── input/                 # Girdi veri seti
│   ├── processed/             # İşlenmiş veriler
│   └── output/               # Çıktı raporları
│
├── notebooks/
│   └── analysis_demo.ipynb   # Demo notebook
│
├── config/
│   └── config.yaml          # Konfigürasyon dosyası
│
├── requirements.txt
├── README.md
└── main.py                  # Ana çalıştırma dosyası
```

---

## 🔧 Detaylı Geliştirme Adımları

### Adım 1: Proje Kurulumu ve Temel Yapı
```bash
# Sanal ortam oluşturma
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Gerekli kütüphaneleri yükleme
pip install -r requirements.txt
```

### Adım 2: Veri Yükleme Modülü (data_loader.py)
```python
class DatasetLoader:
    def __init__(self, dataset_path, annotation_format='yolo'):
        self.dataset_path = dataset_path
        self.annotation_format = annotation_format
        
    def load_images(self):
        """Görüntüleri yükle ve temel bilgileri çıkar"""
        pass
        
    def load_annotations(self):
        """Annotation dosyalarını formatına göre yükle"""
        pass
        
    def validate_dataset(self):
        """Veri seti tutarlılığını kontrol et"""
        pass
```

### Adım 3: Görüntü Analiz Modülü (image_analyzer.py)
```python
class ImageAnalyzer:
    def analyze_image_properties(self, image_path):
        """Görüntü özelliklerini analiz et"""
        # - Çözünürlük analizi
        # - Renk dağılımı
        # - Parlaklık/kontrast
        # - Bulanıklık tespiti
        pass
        
    def detect_anomalies(self, images):
        """Anormal görüntüleri tespit et"""
        pass
        
    def calculate_diversity_metrics(self, images):
        """Görüntü çeşitliliği metriklerini hesapla"""
        pass
```

### Adım 4: Annotation Analiz Modülü (annotation_analyzer.py)
```python
class AnnotationAnalyzer:
    def analyze_class_distribution(self, annotations):
        """Sınıf dağılımını analiz et"""
        pass
        
    def calculate_bbox_statistics(self, annotations):
        """Bounding box istatistiklerini hesapla"""
        pass
        
    def detect_annotation_quality_issues(self, annotations):
        """Annotation kalite sorunlarını tespit et"""
        pass
```

### Adım 5: Kalite Değerlendirme Modülü (quality_assessor.py)
```python
class QualityAssessor:
    def assess_dataset_completeness(self):
        """Veri seti eksiksizliğini değerlendir"""
        pass
        
    def evaluate_annotation_quality(self):
        """Annotation kalitesini değerlendir"""
        pass
        
    def calculate_dataset_score(self):
        """Genel veri seti skoru hesapla"""
        pass
```

---

## 📊 Analiz Metrikleri ve Değerlendirme Kriterleri

### Görüntü Kalitesi Metrikleri
1. **Çözünürlük Analizi**
   - Minimum/maksimum/ortalama çözünürlük
   - Çözünürlük dağılımı grafiği
   - Düşük çözünürlüklü görüntü oranı

2. **Görüntü Kalite Skorları**
   - Bulanıklık skoru (Laplacian variance)
   - Parlaklık dağılımı
   - Kontrast analizi
   - Renk kanalı dağılımları

### Annotation Kalitesi Metrikleri
1. **Sınıf Dağılımı**
   - Class imbalance oranı
   - Minimum sample sayısı kontrolü
   - Sınıf başına örnek sayısı grafikleri

2. **Bounding Box Analizi**
   - Bbox boyut dağılımları
   - Aspect ratio analizi
   - Overlap/IoU istatistikleri
   - Eksik/hatalı annotation tespiti

### Veri Seti Yeterlilik Kriterleri
1. **Minimum Gereksinimler**
   - Sınıf başına minimum 100 örnek
   - Toplam veri boyutu > 1000 görüntü
   - Class imbalance < %80

2. **Kalite Skorları**
   - A (90-100): Mükemmel veri seti
   - B (75-89): İyi kalite, minor iyileştirmeler
   - C (60-74): Orta kalite, önemli iyileştirmeler gerekli
   - D (0-59): Yetersiz, major iyileştirmeler gerekli

---

## 📈 Görselleştirme Çıktıları

### 1. Dashboard Ana Sayfası
- Veri seti özet kartları
- Genel kalite skoru
- Hızlı metrikler

### 2. Sınıf Dağılımı Grafikleri
- Bar chart: Sınıf başına örnek sayısı
- Pie chart: Sınıf oranları
- Heatmap: Sınıf co-occurrence matrisi

### 3. Görüntü Kalitesi Analizi
- Histogram: Çözünürlük dağılımı
- Scatter plot: Genişlik vs yükseklik
- Box plot: Kalite skorları dağılımı

### 4. Annotation İstatistikleri
- Bbox boyut dağılımları
- Density plot: Annotation yoğunluğu
- Timeline: Veri toplama süreci (eğer tarih var ise)

---

## 🚀 Kullanım Senaryoları

### Senaryo 1: Yeni Veri Seti Değerlendirmesi
```python
# Ana kullanım
analyzer = DatasetQualityAnalyzer('path/to/dataset')
report = analyzer.generate_full_report()
print(f"Veri seti kalite skoru: {report['overall_score']}")
```

### Senaryo 2: Karşılaştırmalı Analiz
```python
# İki veri setini karşılaştır
analyzer.compare_datasets(['dataset1_path', 'dataset2_path'])
```

### Senaryo 3: İyileştirme Önerileri
```python
# Otomatik öneriler al
suggestions = analyzer.get_improvement_suggestions()
```

---

## 📋 Geliştirme Kontrol Listesi

### Temel Fonksiyonlar ✅
- [ ] Veri yükleme modülü
- [ ] Görüntü analiz fonksiyonları
- [ ] Annotation parsing (YOLO, COCO, XML)
- [ ] Temel istatistik hesaplamaları
- [ ] Görselleştirme modülü

### İleri Düzey Özellikler ✅
- [ ] Anomali tespiti
- [ ] Kalite skorlama algoritması
- [ ] İnteraktif dashboard
- [ ] Otomatik rapor oluşturma
- [ ] Çoklu format desteği

### Test ve Dokümantasyon ✅
- [ ] Unit testler
- [ ] Kullanım dokümantasyonu
- [ ] API dokümantasyonu
- [ ] Örnek veri setleri
- [ ] Performance benchmarkları

---

## 🔄 Proje Geliştirme Süreci

### Hafta 1: Temel Altyapı
- Proje yapısını oluştur
- Temel veri yükleme fonksiyonlarını geliştir
- Basit görüntü analiz fonksiyonları

### Hafta 2: Analiz Modülleri
- Annotation parsing modülleri
- İstatistiksel analiz fonksiyonları
- Temel görselleştirmeler

### Hafta 3: Kalite Değerlendirme
- Kalite skorlama algoritmaları
- Anomali tespit mekanizmaları
- İyileştirme önerisi motoru

### Hafta 4: UI ve Raporlama
- İnteraktif dashboard
- PDF rapor oluşturma
- Final testler ve dokümantasyon

---

## 🎯 Beklenen Çıktılar

### Otomatik Rapor İçeriği
1. **Executive Summary**
   - Genel kalite skoru
   - Ana bulgular
   - Kritik öneriler

2. **Detaylı Analiz**
   - Sınıf dağılımı analizi
   - Görüntü kalitesi değerlendirmesi
   - Annotation kalite raporu

3. **Görsel Özetler**
   - Grafikler ve charts
   - Sample görüntüler
   - Karşılaştırma tabloları

4. **Actionable Insights**
   - Spesifik iyileştirme önerileri
   - Öncelik sıralaması
   - Implementation önerileri

---

## 🚀 Kurulum ve Çalıştırma Talimatları

### Hızlı Başlangıç
```bash
# Repository'yi klonla
git clone [repo-url]
cd veri_analiz_projesi

# Bağımlılıkları yükle
pip install -r requirements.txt

# Ana programı çalıştır
python main.py --dataset_path "your/dataset/path" --format "yolo"
```

### Konfigürasyon
`config/config.yaml` dosyasından analiz parametrelerini özelleştirin:
```yaml
analysis:
  min_samples_per_class: 50
  quality_threshold: 0.7
  image_size_threshold: 224
  
visualization:
  figure_size: [12, 8]
  color_palette: "viridis"
  save_plots: true
```

Bu detaylı taslak ile birlikte, projenizi adım adım geliştirebilir ve Claude'a her modülü ayrı ayrı kodlatabilirsiniz. Hangi bölümden başlamak istersiniz?