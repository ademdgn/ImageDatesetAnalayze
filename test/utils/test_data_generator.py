#!/usr/bin/env python3
"""
Test Utilities - Annotation Analyzer Testleri için Yardımcı Fonksiyonlar

Bu modül test verisi oluşturma ve test yardımcı fonksiyonlarını içerir.
"""

import tempfile
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def create_test_yolo_annotation(class_id=0, x_center=0.5, y_center=0.5, 
                               width=0.3, height=0.2):
    """Test için YOLO annotation satırı oluştur"""
    return f"{class_id} {x_center} {y_center} {width} {height}"

def create_test_yolo_file(file_path, annotations):
    """Test için YOLO annotation dosyası oluştur"""
    with open(file_path, 'w') as f:
        for ann in annotations:
            f.write(ann + '\n')

def create_test_coco_annotation():
    """Test için COCO annotation oluştur"""
    coco_data = {
        "images": [
            {
                "id": 1,
                "file_name": "test_image_001.jpg",
                "width": 640,
                "height": 480
            },
            {
                "id": 2,
                "file_name": "test_image_002.jpg", 
                "width": 800,
                "height": 600
            }
        ],
        "annotations": [
            {
                "id": 1,
                "image_id": 1,
                "category_id": 1,
                "bbox": [100, 100, 50, 75],
                "area": 3750,
                "iscrowd": 0
            },
            {
                "id": 2,
                "image_id": 1,
                "category_id": 2,
                "bbox": [200, 150, 80, 60],
                "area": 4800,
                "iscrowd": 0
            },
            {
                "id": 3,
                "image_id": 2,
                "category_id": 1,
                "bbox": [300, 200, 100, 120],
                "area": 12000,
                "iscrowd": 0
            }
        ],
        "categories": [
            {
                "id": 1,
                "name": "person",
                "supercategory": "human"
            },
            {
                "id": 2,
                "name": "car",
                "supercategory": "vehicle"
            }
        ]
    }
    return coco_data

def create_test_pascal_voc_annotation():
    """Test için Pascal VOC annotation oluştur"""
    annotation = ET.Element("annotation")
    
    # Filename
    filename = ET.SubElement(annotation, "filename")
    filename.text = "test_image.jpg"
    
    # Size
    size = ET.SubElement(annotation, "size")
    width = ET.SubElement(size, "width")
    width.text = "640"
    height = ET.SubElement(size, "height")
    height.text = "480"
    depth = ET.SubElement(size, "depth")
    depth.text = "3"
    
    # Objects
    obj1 = ET.SubElement(annotation, "object")
    name1 = ET.SubElement(obj1, "name")
    name1.text = "person"
    difficult1 = ET.SubElement(obj1, "difficult")
    difficult1.text = "0"
    bndbox1 = ET.SubElement(obj1, "bndbox")
    xmin1 = ET.SubElement(bndbox1, "xmin")
    xmin1.text = "100"
    ymin1 = ET.SubElement(bndbox1, "ymin")
    ymin1.text = "100"
    xmax1 = ET.SubElement(bndbox1, "xmax")
    xmax1.text = "200"
    ymax1 = ET.SubElement(bndbox1, "ymax")
    ymax1.text = "180"
    
    obj2 = ET.SubElement(annotation, "object")
    name2 = ET.SubElement(obj2, "name")
    name2.text = "car"
    difficult2 = ET.SubElement(obj2, "difficult")
    difficult2.text = "0"
    bndbox2 = ET.SubElement(obj2, "bndbox")
    xmin2 = ET.SubElement(bndbox2, "xmin")
    xmin2.text = "300"
    ymin2 = ET.SubElement(bndbox2, "ymin")
    ymin2.text = "200"
    xmax2 = ET.SubElement(bndbox2, "xmax")
    xmax2.text = "400"
    ymax2 = ET.SubElement(bndbox2, "ymax")
    ymax2.text = "300"
    
    return annotation

def create_test_annotation_dataset(num_files=10):
    """
    Test için çeşitli formatlarda annotation dataset'i oluştur
    
    Args:
        num_files: Oluşturulacak dosya sayısı
        
    Returns:
        (temp_dir, annotation_paths, class_names) tuple'ı
    """
    temp_dir = tempfile.mkdtemp(prefix="test_annotations_")
    annotation_paths = []
    class_names = ["person", "car", "bicycle", "dog", "cat"]
    
    print(f"📁 Geçici annotation dataset'i oluşturuluyor: {temp_dir}")
    
    for i in range(num_files):
        # Çeşitli test senaryoları
        scenarios = [
            # Normal YOLO annotations
            {
                'format': 'yolo',
                'annotations': [
                    create_test_yolo_annotation(0, 0.5, 0.5, 0.3, 0.2),
                    create_test_yolo_annotation(1, 0.2, 0.3, 0.15, 0.25),
                ]
            },
            # Tek annotation
            {
                'format': 'yolo',
                'annotations': [
                    create_test_yolo_annotation(2, 0.7, 0.6, 0.2, 0.3)
                ]
            },
            # Çok annotation'lı
            {
                'format': 'yolo',
                'annotations': [
                    create_test_yolo_annotation(0, 0.1, 0.1, 0.1, 0.1),
                    create_test_yolo_annotation(1, 0.5, 0.5, 0.2, 0.3),
                    create_test_yolo_annotation(2, 0.8, 0.8, 0.15, 0.15),
                    create_test_yolo_annotation(3, 0.3, 0.7, 0.25, 0.2),
                ]
            },
            # Edge case'ler
            {
                'format': 'yolo',
                'annotations': [
                    create_test_yolo_annotation(0, 0.95, 0.95, 0.1, 0.1),  # Edge'e yakın
                    create_test_yolo_annotation(1, 0.05, 0.05, 0.1, 0.1),  # Corner'da
                ]
            },
            # Büyük objeler
            {
                'format': 'yolo',
                'annotations': [
                    create_test_yolo_annotation(4, 0.5, 0.5, 0.8, 0.6),  # Büyük obje
                ]
            },
        ]
        
        scenario = scenarios[i % len(scenarios)]
        
        if scenario['format'] == 'yolo':
            # YOLO dosyası oluştur
            ann_path = Path(temp_dir) / f"annotation_{i:03d}.txt"
            create_test_yolo_file(ann_path, scenario['annotations'])
            annotation_paths.append(str(ann_path))
    
    # Birkaç COCO dosyası ekle
    for i in range(2):
        coco_data = create_test_coco_annotation()
        coco_path = Path(temp_dir) / f"coco_annotation_{i}.json"
        with open(coco_path, 'w') as f:
            json.dump(coco_data, f, indent=2)
        annotation_paths.append(str(coco_path))
    
    # Birkaç Pascal VOC dosyası ekle
    for i in range(2):
        voc_data = create_test_pascal_voc_annotation()
        voc_path = Path(temp_dir) / f"voc_annotation_{i}.xml"
        ET.ElementTree(voc_data).write(voc_path)
        annotation_paths.append(str(voc_path))
    
    # Class names dosyası oluştur
    classes_path = Path(temp_dir) / "classes.txt"
    with open(classes_path, 'w') as f:
        for class_name in class_names:
            f.write(f"{class_name}\n")
    
    print(f"✅ {len(annotation_paths)} annotation dosyası oluşturuldu")
    return temp_dir, annotation_paths, class_names

def create_edge_case_dataset():
    """Edge case'ler için test dataset oluştur"""
    temp_dir = tempfile.mkdtemp(prefix="edge_case_tests_")
    
    edge_cases = [
        # Boş annotation dosyası
        {
            'name': 'empty_file.txt',
            'content': ''
        },
        # Hatalı format
        {
            'name': 'invalid_format.txt',
            'content': 'invalid content\nmore invalid\n'
        },
        # Çok büyük koordinatlar
        {
            'name': 'invalid_coords.txt',
            'content': '0 1.5 1.2 0.3 0.2\n1 -0.1 0.5 0.3 0.2\n'
        },
        # Eksik değerler
        {
            'name': 'incomplete_data.txt',
            'content': '0 0.5 0.5\n1 0.2\n'
        },
        # Çok fazla değer
        {
            'name': 'too_many_values.txt',
            'content': '0 0.5 0.5 0.3 0.2 0.1 0.9\n'
        }
    ]
    
    edge_case_files = []
    
    for case in edge_cases:
        file_path = Path(temp_dir) / case['name']
        with open(file_path, 'w') as f:
            f.write(case['content'])
        edge_case_files.append(str(file_path))
    
    return temp_dir, edge_case_files, edge_cases

def print_test_header(test_name):
    """Test başlığı yazdır"""
    print("\n" + "="*60)
    print(f"🧪 {test_name}")
    print("="*60)

def print_test_result(test_name, success, details=None):
    """Test sonucunu yazdır"""
    icon = "✅" if success else "❌"
    print(f"{icon} {test_name}: {'BAŞARILI' if success else 'BAŞARISIZ'}")
    if details and not success:
        print(f"   └─ {details}")

def cleanup_temp_directory(temp_dir):
    """Geçici dizini temizle"""
    import shutil
    try:
        shutil.rmtree(temp_dir)
        return True
    except Exception as e:
        print(f"⚠️ Temizlik hatası: {e}")
        return False
