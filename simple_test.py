"""
Simple Import Test
Basit import testi
"""

import sys
from pathlib import Path

# Proje dizinini ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("1. Ana modül import testi...")

try:
    from src.data_loader import DatasetLoader
    print("✅ DatasetLoader imported")
except Exception as e:
    print(f"❌ DatasetLoader import failed: {e}")

try:
    from src.image_analyzer import ImageAnalyzer
    print("✅ ImageAnalyzer imported")
except Exception as e:
    print(f"❌ ImageAnalyzer import failed: {e}")

try:
    from src.quality_assessor import DatasetQualityAssessor
    print("✅ DatasetQualityAssessor imported")
except Exception as e:
    print(f"❌ DatasetQualityAssessor import failed: {e}")

print("\n2. Enhanced analyzer import testi...")

try:
    from src.enhanced_analyzer import EnhancedDatasetAnalyzer
    print("✅ EnhancedDatasetAnalyzer imported")
except Exception as e:
    print(f"❌ EnhancedDatasetAnalyzer import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n3. Veri seti kontrolü...")

dataset_path = project_root / 'data' / 'input' / 'yolov11_dataset_vol1'
if dataset_path.exists():
    print(f"✅ Test dataset found: {dataset_path}")
    
    # Görüntü sayısını kontrol et
    train_images = dataset_path / 'train' / 'images'
    if train_images.exists():
        image_count = len(list(train_images.glob('*.jpg')))
        print(f"   📸 Train images: {image_count}")
    
    # Annotation sayısını kontrol et  
    train_labels = dataset_path / 'train' / 'labels'
    if train_labels.exists():
        label_count = len(list(train_labels.glob('*.txt')))
        print(f"   🏷️  Train labels: {label_count}")
        
else:
    print(f"❌ Test dataset not found: {dataset_path}")

print("\n4. Basit DatasetLoader testi...")

try:
    # Sadece import edilebiliyorsa instance oluşturmaya çalış
    if dataset_path.exists():
        loader = DatasetLoader(str(dataset_path), 'yolo')
        print("✅ DatasetLoader instance created")
        
        # Temel istatistikleri al
        stats = loader.get_basic_statistics()
        print(f"✅ Basic stats: {stats}")
        
except Exception as e:
    print(f"❌ DatasetLoader test failed: {e}")
    import traceback
    traceback.print_exc()

print("\nTest completed.")
