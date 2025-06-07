#!/usr/bin/env python3
"""
Sınıf Dağılımı Analiz Modülü

Bu modül annotation'lardaki sınıf dağılımını analiz eder ve
class imbalance tespiti yapar.
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from collections import Counter
import math

class ClassDistributionAnalyzer:
    """Sınıf dağılımı analizi yapan sınıf"""
    
    def __init__(self, config: Dict = None):
        """
        ClassDistributionAnalyzer sınıfını başlat
        
        Args:
            config: Konfigürasyon parametreleri
        """
        self.config = config or {}
        self.min_samples_per_class = self.config.get('min_samples_per_class', 10)
        self.max_class_imbalance = self.config.get('max_class_imbalance', 0.8)
        
    def analyze_class_distribution(self, annotations_data: List[Dict]) -> Dict[str, Any]:
        """
        Sınıf dağılımını kapsamlı olarak analiz et
        
        Args:
            annotations_data: Parse edilmiş annotation verileri
            
        Returns:
            Sınıf dağılımı analiz sonuçları
        """
        if not annotations_data:
            return {'error': 'No annotation data provided'}
        
        # Tüm annotation'ları topla
        all_annotations = []
        for data in annotations_data:
            if data.get('parsing_failed', False):
                continue
            all_annotations.extend(data.get('annotations', []))
        
        if not all_annotations:
            return {'error': 'No valid annotations found'}
        
        # Sınıf sayılarını hesapla
        class_counts = self._count_classes(all_annotations)
        
        # Dağılım istatistikleri
        distribution_stats = self._calculate_distribution_stats(class_counts)
        
        # Class imbalance analizi
        imbalance_analysis = self._analyze_class_imbalance(class_counts)
        
        # Sınıf kalitesi değerlendirmesi
        class_quality = self._evaluate_class_quality(class_counts, all_annotations)
        
        # Öneriler
        recommendations = self._generate_class_recommendations(
            class_counts, distribution_stats, imbalance_analysis
        )
        
        return {
            'total_annotations': len(all_annotations),
            'total_classes': len(class_counts),
            'class_counts': class_counts,
            'distribution_stats': distribution_stats,
            'imbalance_analysis': imbalance_analysis,
            'class_quality': class_quality,
            'recommendations': recommendations
        }
    
    def _count_classes(self, annotations: List[Dict]) -> Dict[str, int]:
        """Sınıfları say"""
        class_counts = Counter()
        
        for ann in annotations:
            class_name = ann.get('class_name', 'unknown')
            class_counts[class_name] += 1
        
        return dict(class_counts)
    
    def _calculate_distribution_stats(self, class_counts: Dict[str, int]) -> Dict[str, Any]:
        """Dağılım istatistiklerini hesapla"""
        if not class_counts:
            return {}
        
        counts = list(class_counts.values())
        total_samples = sum(counts)
        
        # Temel istatistikler
        stats = {
            'mean': np.mean(counts),
            'median': np.median(counts),
            'std': np.std(counts),
            'min': min(counts),
            'max': max(counts),
            'range': max(counts) - min(counts),
            'cv': np.std(counts) / np.mean(counts) if np.mean(counts) > 0 else 0
        }
        
        # Yüzdelik dilimler
        stats.update({
            'q25': np.percentile(counts, 25),
            'q75': np.percentile(counts, 75),
            'iqr': np.percentile(counts, 75) - np.percentile(counts, 25)
        })
        
        # En yaygın ve en nadir sınıflar
        sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
        
        stats['most_common'] = {
            'class': sorted_classes[0][0],
            'count': sorted_classes[0][1],
            'percentage': (sorted_classes[0][1] / total_samples) * 100
        }
        
        stats['least_common'] = {
            'class': sorted_classes[-1][0],
            'count': sorted_classes[-1][1],
            'percentage': (sorted_classes[-1][1] / total_samples) * 100
        }
        
        # Sınıf yüzdeleri
        class_percentages = {}
        for class_name, count in class_counts.items():
            class_percentages[class_name] = {
                'count': count,
                'percentage': (count / total_samples) * 100
            }
        
        stats['class_percentages'] = class_percentages
        
        return stats
    
    def _analyze_class_imbalance(self, class_counts: Dict[str, int]) -> Dict[str, Any]:
        """Class imbalance analizi yap"""
        if not class_counts:
            return {}
        
        counts = list(class_counts.values())
        total_samples = sum(counts)
        max_count = max(counts)
        min_count = min(counts)
        
        # İmbalance ratio (en çok / en az)
        imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
        
        # Majority class dominance
        majority_dominance = max_count / total_samples
        
        # Gini impurity (diversity ölçüsü)
        gini_impurity = self._calculate_gini_impurity(counts, total_samples)
        
        # Shannon entropy (diversity ölçüsü)
        shannon_entropy = self._calculate_shannon_entropy(counts, total_samples)
        
        # Class imbalance severity
        severity = self._classify_imbalance_severity(imbalance_ratio, majority_dominance)
        
        # Problematic classes
        problematic_classes = self._identify_problematic_classes(class_counts, total_samples)
        
        return {
            'imbalance_ratio': imbalance_ratio,
            'majority_dominance': majority_dominance,
            'gini_impurity': gini_impurity,
            'shannon_entropy': shannon_entropy,
            'normalized_entropy': shannon_entropy / math.log(len(class_counts)) if len(class_counts) > 1 else 0,
            'imbalance_severity': severity,
            'is_balanced': severity == 'balanced',
            'problematic_classes': problematic_classes
        }
    
    def _calculate_gini_impurity(self, counts: List[int], total: int) -> float:
        """Gini impurity hesapla"""
        if total == 0:
            return 0.0
        
        gini = 1.0
        for count in counts:
            prob = count / total
            gini -= prob ** 2
        
        return gini
    
    def _calculate_shannon_entropy(self, counts: List[int], total: int) -> float:
        """Shannon entropy hesapla"""
        if total == 0:
            return 0.0
        
        entropy = 0.0
        for count in counts:
            if count > 0:
                prob = count / total
                entropy -= prob * math.log2(prob)
        
        return entropy
    
    def _classify_imbalance_severity(self, imbalance_ratio: float, 
                                   majority_dominance: float) -> str:
        """İmbalance şiddetini sınıflandır"""
        if imbalance_ratio <= 2 and majority_dominance <= 0.4:
            return 'balanced'
        elif imbalance_ratio <= 5 and majority_dominance <= 0.6:
            return 'mild_imbalance'
        elif imbalance_ratio <= 20 and majority_dominance <= 0.8:
            return 'moderate_imbalance'
        else:
            return 'severe_imbalance'
    
    def _identify_problematic_classes(self, class_counts: Dict[str, int], 
                                    total_samples: int) -> Dict[str, List[str]]:
        """Problemli sınıfları tespit et"""
        problematic = {
            'underrepresented': [],  # Az temsil edilen
            'overrepresented': [],   # Aşırı temsil edilen
            'insufficient_samples': [] # Yetersiz örnek
        }
        
        # Thresholds
        min_percentage = (self.min_samples_per_class / total_samples) * 100
        expected_percentage = 100 / len(class_counts)  # Eşit dağılım beklentisi
        
        for class_name, count in class_counts.items():
            percentage = (count / total_samples) * 100
            
            # Yetersiz örnek
            if count < self.min_samples_per_class:
                problematic['insufficient_samples'].append(class_name)
            
            # Az temsil
            if percentage < expected_percentage * 0.5:  # Beklenenin yarısından az
                problematic['underrepresented'].append(class_name)
            
            # Aşırı temsil
            if percentage > expected_percentage * 2:  # Beklenenin 2 katından fazla
                problematic['overrepresented'].append(class_name)
        
        return problematic
    
    def _evaluate_class_quality(self, class_counts: Dict[str, int], 
                               annotations: List[Dict]) -> Dict[str, Any]:
        """Sınıf kalitesini değerlendir"""
        quality_scores = {}
        
        for class_name in class_counts:
            class_annotations = [ann for ann in annotations if ann.get('class_name') == class_name]
            
            # Temel kalite metrikleri
            sample_count = len(class_annotations)
            
            # Bbox area dağılımı
            areas = [ann.get('area', 0) for ann in class_annotations if 'area' in ann]
            area_stats = {
                'mean': np.mean(areas) if areas else 0,
                'std': np.std(areas) if areas else 0,
                'cv': np.std(areas) / np.mean(areas) if areas and np.mean(areas) > 0 else 0
            }
            
            # Kalite skoru hesapla
            quality_score = self._calculate_class_quality_score(
                sample_count, area_stats
            )
            
            quality_scores[class_name] = {
                'sample_count': sample_count,
                'area_stats': area_stats,
                'quality_score': quality_score,
                'quality_grade': self._grade_quality_score(quality_score)
            }
        
        return quality_scores
    
    def _calculate_class_quality_score(self, sample_count: int, 
                                     area_stats: Dict) -> float:
        """Sınıf kalite skoru hesapla (0-100)"""
        score = 0.0
        
        # Sample count skoru (50 puan)
        if sample_count >= 100:
            count_score = 50
        elif sample_count >= 50:
            count_score = 40
        elif sample_count >= 20:
            count_score = 30
        elif sample_count >= 10:
            count_score = 20
        else:
            count_score = sample_count * 2  # 0-20 arası
        
        score += count_score
        
        # Area consistency skoru (30 puan)
        cv = area_stats.get('cv', 0)
        if cv < 0.3:  # Düşük varyasyon = iyi
            area_score = 30
        elif cv < 0.5:
            area_score = 25
        elif cv < 0.8:
            area_score = 20
        elif cv < 1.0:
            area_score = 15
        else:
            area_score = 10
        
        score += area_score
        
        # Bonus puanlar (20 puan)
        bonus = 20
        
        # Çok düşük örnek sayısı için ceza
        if sample_count < 5:
            bonus -= 10
        
        # Çok yüksek varyasyon için ceza
        if cv > 1.5:
            bonus -= 10
        
        score += max(0, bonus)
        
        return min(100, max(0, score))
    
    def _grade_quality_score(self, score: float) -> str:
        """Kalite skorunu harf notuna dönüştür"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_class_recommendations(self, class_counts: Dict[str, int],
                                      distribution_stats: Dict,
                                      imbalance_analysis: Dict) -> List[str]:
        """Sınıf dağılımı için öneriler oluştur"""
        recommendations = []
        
        total_samples = sum(class_counts.values())
        severity = imbalance_analysis.get('imbalance_severity', 'unknown')
        
        # Genel durum değerlendirmesi
        if severity == 'balanced':
            recommendations.append("✅ Sınıf dağılımı dengeli görünüyor.")
        elif severity == 'mild_imbalance':
            recommendations.append("🟡 Hafif sınıf dengesizliği mevcut. İzlenmesi önerilir.")
        elif severity == 'moderate_imbalance':
            recommendations.append("🟠 Orta seviyede sınıf dengesizliği. Düzeltme önerilir.")
        else:
            recommendations.append("🔴 Ciddi sınıf dengesizliği tespit edildi. Acil müdahale gerekli.")
        
        # Problematic classes için öneriler
        problematic = imbalance_analysis.get('problematic_classes', {})
        
        insufficient = problematic.get('insufficient_samples', [])
        if insufficient:
            recommendations.append(
                f"📈 Yetersiz örnekli sınıflar ({len(insufficient)} adet): "
                f"{', '.join(insufficient[:3])}{'...' if len(insufficient) > 3 else ''}"
            )
        
        underrepresented = problematic.get('underrepresented', [])
        if underrepresented:
            recommendations.append(
                f"⬆️ Az temsil edilen sınıflar için daha fazla veri toplayın: "
                f"{', '.join(underrepresented[:3])}{'...' if len(underrepresented) > 3 else ''}"
            )
        
        overrepresented = problematic.get('overrepresented', [])
        if overrepresented:
            recommendations.append(
                f"⬇️ Aşırı temsil edilen sınıfları azaltmayı düşünün: "
                f"{', '.join(overrepresented[:3])}{'...' if len(overrepresented) > 3 else ''}"
            )
        
        # İstatistik tabanlı öneriler
        imbalance_ratio = imbalance_analysis.get('imbalance_ratio', 1)
        if imbalance_ratio > 10:
            recommendations.append(
                f"⚖️ İmbalance oranı çok yüksek ({imbalance_ratio:.1f}:1). "
                "Data augmentation veya resampling teknikleri kullanın."
            )
        
        # Sınıf sayısı önerileri
        num_classes = len(class_counts)
        if num_classes < 2:
            recommendations.append("❓ En az 2 sınıf olması önerilir.")
        elif num_classes > 50:
            recommendations.append("🔍 Çok fazla sınıf var. Bazılarını birleştirmeyi düşünün.")
        
        # Minimum sample önerileri
        min_samples = min(class_counts.values())
        if min_samples < 10:
            recommendations.append(
                f"📊 En az temsil edilen sınıfta sadece {min_samples} örnek var. "
                "Sınıf başına minimum 50 örnek önerilir."
            )
        
        if not recommendations:
            recommendations.append("✨ Sınıf dağılımı genel olarak kabul edilebilir durumda.")
        
        return recommendations
    
    def calculate_balance_score(self, class_counts: Dict[str, int]) -> float:
        """
        Genel denge skoru hesapla (0-100)
        
        Args:
            class_counts: Sınıf sayıları
            
        Returns:
            Denge skoru
        """
        if not class_counts or len(class_counts) < 2:
            return 0.0
        
        counts = list(class_counts.values())
        total_samples = sum(counts)
        
        # Perfect balance score (her sınıf eşit dağıtılmış)
        expected_count = total_samples / len(class_counts)
        
        # Mean absolute deviation from expected
        mad = np.mean([abs(count - expected_count) for count in counts])
        
        # Normalize to 0-100 scale
        max_possible_mad = expected_count  # Worst case: one class has all samples
        normalized_mad = mad / max_possible_mad if max_possible_mad > 0 else 0
        
        balance_score = (1 - normalized_mad) * 100
        
        return max(0, min(100, balance_score))
    
    def suggest_rebalancing_strategy(self, class_counts: Dict[str, int]) -> Dict[str, Any]:
        """
        Yeniden dengeleme stratejisi öner
        
        Args:
            class_counts: Sınıf sayıları
            
        Returns:
            Dengeleme stratejisi önerileri
        """
        if not class_counts:
            return {}
        
        total_samples = sum(class_counts.values())
        target_per_class = total_samples // len(class_counts)
        
        strategies = {
            'undersampling': {},  # Azaltılacak sınıflar
            'oversampling': {},   # Artırılacak sınıflar
            'hybrid': {},         # Karma strateji
            'recommended_strategy': 'hybrid'
        }
        
        for class_name, count in class_counts.items():
            if count > target_per_class * 1.5:  # %50 fazla
                strategies['undersampling'][class_name] = {
                    'current': count,
                    'target': target_per_class,
                    'reduce_by': count - target_per_class
                }
            elif count < target_per_class * 0.5:  # %50 az
                strategies['oversampling'][class_name] = {
                    'current': count,
                    'target': target_per_class,
                    'increase_by': target_per_class - count
                }
        
        # Hybrid strategy: moderate adjustments
        for class_name, count in class_counts.items():
            if count != target_per_class:
                strategies['hybrid'][class_name] = {
                    'current': count,
                    'target': target_per_class,
                    'adjustment': target_per_class - count
                }
        
        return strategies
