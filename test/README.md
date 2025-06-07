# Image Dataset Analyzer - Test Suite

Bu klasör Image Dataset Analyzer projesi için modüler test yapısını içerir.

## 📁 Test Yapısı

```
test/
├── __init__.py                     # Ana test paketi
├── test_config.yaml               # Test konfigürasyonu
├── run_tests.py                   # Ana test çalıştırıcı (kök dizinde)
│
├── annotation_analyzer/           # Annotation analyzer testleri
│   ├── __init__.py
│   ├── test_imports.py            # Import testleri
│   ├── test_format_parsers.py     # Format parser testleri
│   ├── test_class_distribution.py # Sınıf dağılımı testleri
│   └── test_runner.py             # Annotation analyzer test runner
│
├── utils/                         # Test yardımcı fonksiyonları
│   ├── __init__.py
│   └── test_data_generator.py     # Test verisi oluşturma
│
├── image_analyzer/                # Image analyzer testleri (gelecek)
└── data_loader/                   # Data loader testleri (gelecek)
```

## 🚀 Testleri Çalıştırma

### Tüm Testleri Çalıştır
```bash
python run_tests.py
```

### Sadece Annotation Analyzer Testleri
```bash
python run_tests.py --module annotation_analyzer
```

### Detaylı Çıktı ile
```bash
python run_tests.py --verbose
```

### Belirli Test Modülü
```bash
# Annotation analyzer testleri
python -m test.annotation_analyzer.test_runner

# Sadece import testleri
python -m test.annotation_analyzer.test_imports

# Sadece format parser testleri
python -m test.annotation_analyzer.test_format_parsers
```

## 🧪 Test Modülleri

### 1. Import Testleri (`test_imports.py`)
- Tüm annotation analyzer modüllerinin import edilebilirliğini test eder
- Eksik modülleri ve import hatalarını tespit eder

### 2. Format Parser Testleri (`test_format_parsers.py`)
- YOLO, COCO, Pascal VOC format parser'larını test eder
- Test annotation dosyaları oluşturur ve parse işlemini doğrular

### 3. Sınıf Dağılımı Testleri (`test_class_distribution.py`)
- Sınıf dağılımı analiz modülünü test eder
- Class imbalance analizi ve öneriler test edilir

### 4. Test Utilities (`utils/`)
- Test verisi oluşturma fonksiyonları
- Geçici dosya ve klasör yönetimi
- Test sonuç raporlama yardımcıları

## 📊 Test Sonuçları

Test sonuçları aşağıdaki formatta raporlanır:

```
✅ Test Adı: BAŞARILI
❌ Test Adı: BAŞARISIZ
💥 Test Adı: HATA

📈 GENEL BAŞARI ORANI:
  • Başarılı testler: X/Y
  • Başarı oranı: %Z
```

### Başarı Kriterleri
- **90%+ :** 🎉 Mükemmel! Tamamen hazır
- **75-89%:** 👍 İyi! Küçük düzeltmeler yeterli  
- **50-74%:** ⚠️ Orta! Önemli sorunlar var
- **<50% :** 🚨 Kritik! Major düzeltmeler gerekli

## 🔧 Test Konfigürasyonu

`test_config.yaml` dosyasında test ayarları yapılandırılabilir:

```yaml
test_config:
  verbose: false
  timeout: 300
  annotation_analyzer:
    sample_dataset_size: 10
    performance_tests: true
```

## 📝 Yeni Test Ekleme

### Yeni Test Modülü Ekleme
1. `test/` altında yeni klasör oluştur
2. `__init__.py` ve test dosyalarını ekle
3. `run_tests.py` içine modülü dahil et

### Yeni Test Fonksiyonu Ekleme
1. İlgili test modülünde yeni fonksiyon oluştur
2. `test_runner.py` içine fonksiyonu ekle
3. Test utilities kullanarak temiz kod yaz

## 🛠️ Test Geliştirme İpuçları

### Test Verisi Oluşturma
```python
from test.utils import create_test_annotation_dataset

temp_dir, annotation_paths, class_names = create_test_annotation_dataset(10)
```

### Test Sonucu Raporlama
```python
from test.utils import print_test_result

print_test_result("Test Adı", success=True)
print_test_result("Test Adı", success=False, details="Hata detayı")
```

### Temizlik İşlemleri
```python
from test.utils import cleanup_temp_directory

cleanup_temp_directory(temp_dir)
```

## 🔍 Hata Ayıklama

### Verbose Mod
Detaylı hata mesajları için `--verbose` bayrağını kullanın.

### Manuel Test
Belirli testleri manuel olarak çalıştırarak hata ayıklayın:

```python
python -c "
from test.annotation_analyzer.test_imports import test_imports
result = test_imports()
print(f'Sonuç: {result}')
"
```

### Log Dosyaları
Test çıktıları konsola yazdırılır. Gerekirse log dosyasına yönlendirin:

```bash
python run_tests.py > test_results.log 2>&1
```

## 📋 TODO

- [ ] Image analyzer testleri
- [ ] Data loader testleri  
- [ ] Performance benchmark testleri
- [ ] Integration testleri
- [ ] CI/CD pipeline integration
- [ ] Test coverage raporlama
- [ ] Automated test report generation
