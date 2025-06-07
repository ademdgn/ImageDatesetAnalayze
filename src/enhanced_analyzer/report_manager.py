"""
Report Manager Module
Rapor yönetimi ve oluşturma
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class ReportManager:
    """Rapor yönetimi sınıfı"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.output_config = config.get('output', {})
        self.reports_dir = Path(self.output_config.get('reports_dir', 'data/output'))
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.timestamp_format = self.output_config.get('timestamp_format', '%Y%m%d_%H%M%S')
        self.timestamp = datetime.now().strftime(self.timestamp_format)
    
    def generate_all_reports(self, 
                           quality_metrics, 
                           analysis_results: Dict[str, Any],
                           quality_assessor) -> Dict[str, Path]:
        """Tüm raporları oluştur"""
        report_paths = {}
        
        try:
            # 1. Detaylı JSON raporu
            if self.output_config.get('save_detailed_report', True):
                detailed_path = self._generate_detailed_report(quality_assessor)
                if detailed_path:
                    report_paths['detailed_report'] = detailed_path
            
            # 2. Özet metin raporu
            if self.output_config.get('save_summary_report', True):
                summary_path = self._generate_summary_report(quality_assessor)
                if summary_path:
                    report_paths['summary_report'] = summary_path
            
            # 3. CSV raporu
            if self.output_config.get('save_csv_report', True):
                csv_path = self._generate_csv_report(quality_assessor)
                if csv_path:
                    report_paths['csv_report'] = csv_path
            
            # 4. Öneriler raporu
            if self.output_config.get('save_recommendations', True):
                recommendations_path = self._generate_recommendations_report(quality_assessor)
                if recommendations_path:
                    report_paths['recommendations'] = recommendations_path
            
            # 5. Analiz meta verisi
            metadata_path = self._generate_metadata_report(analysis_results)
            if metadata_path:
                report_paths['metadata'] = metadata_path
            
            logger.info(f"{len(report_paths)} rapor başarıyla oluşturuldu")
            return report_paths
            
        except Exception as e:
            logger.error(f"Rapor oluşturma hatası: {str(e)}")
            return {}
    
    def _generate_detailed_report(self, quality_assessor) -> Optional[Path]:
        """Detaylı JSON raporu oluştur"""
        try:
            report_path = self.reports_dir / f'detailed_quality_report_{self.timestamp}.json'
            quality_assessor.generate_detailed_report(str(report_path))
            return report_path
        except Exception as e:
            logger.error(f"Detaylı rapor oluşturma hatası: {str(e)}")
            return None
    
    def _generate_summary_report(self, quality_assessor) -> Optional[Path]:
        """Özet metin raporu oluştur"""
        try:
            report_path = self.reports_dir / f'quality_summary_{self.timestamp}.txt'
            success = quality_assessor.export_summary_report(str(report_path), 'txt')
            return report_path if success else None
        except Exception as e:
            logger.error(f"Özet raporu oluşturma hatası: {str(e)}")
            return None
    
    def _generate_csv_report(self, quality_assessor) -> Optional[Path]:
        """CSV raporu oluştur"""
        try:
            report_path = self.reports_dir / f'quality_metrics_{self.timestamp}.csv'
            success = quality_assessor.export_summary_report(str(report_path), 'csv')
            return report_path if success else None
        except Exception as e:
            logger.error(f"CSV raporu oluşturma hatası: {str(e)}")
            return None
    
    def _generate_recommendations_report(self, quality_assessor) -> Optional[Path]:
        """Öneriler raporu oluştur"""
        try:
            if hasattr(quality_assessor, 'recommendation_engine'):
                report_path = self.reports_dir / f'recommendations_{self.timestamp}.json'
                success = quality_assessor.recommendation_engine.export_recommendations(
                    str(report_path), 'json'
                )
                return report_path if success else None
        except Exception as e:
            logger.error(f"Öneriler raporu oluşturma hatası: {str(e)}")
            return None
    
    def _generate_metadata_report(self, analysis_results: Dict[str, Any]) -> Optional[Path]:
        """Analiz meta verisi raporu oluştur"""
        try:
            metadata = {
                'analysis_timestamp': datetime.now().isoformat(),
                'analysis_duration_seconds': analysis_results.get('analysis_duration', 0),
                'dataset_stats': {
                    'total_images': analysis_results.get('basic_stats', {}).get('total_images', 0),
                    'total_annotations': analysis_results.get('basic_stats', {}).get('total_annotations', 0),
                    'num_classes': analysis_results.get('basic_stats', {}).get('num_classes', 0),
                    'class_distribution': analysis_results.get('basic_stats', {}).get('class_distribution', {})
                },
                'system_info': {
                    'analyzer_version': '1.0.0',
                    'config_used': self.config
                }
            }
            
            report_path = self.reports_dir / f'analysis_metadata_{self.timestamp}.json'
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
            
            return report_path
            
        except Exception as e:
            logger.error(f"Metadata raporu oluşturma hatası: {str(e)}")
            return None
    
    def create_executive_summary(self, quality_metrics) -> str:
        """Yönetici özeti oluştur"""
        summary_lines = []
        
        # Ana başlık
        summary_lines.append("📊 VERİ SETİ KALİTE DEĞERLENDİRMESİ - YÖNETİCİ ÖZETİ")
        summary_lines.append("=" * 60)
        
        # Temel metrikler
        summary_lines.append(f"\n🎯 GENEL DURUM:")
        summary_lines.append(f"   Kalite Skoru: {quality_metrics.overall_score:.1f}/100")
        summary_lines.append(f"   Veri Seti Notu: {quality_metrics.dataset_grade}")
        
        # Hızlı değerlendirme
        if quality_metrics.overall_score >= 90:
            status = "✅ ÜRETİME HAZIR"
            recommendation = "Veri seti üretim ortamında kullanılabilir."
        elif quality_metrics.overall_score >= 75:
            status = "⚡ KÜÇÜK İYİLEŞTİRMELER GEREKLİ"
            recommendation = "Minor düzeltmelerle mükemmel hale getirilebilir."
        elif quality_metrics.overall_score >= 60:
            status = "⚠️  ORTA RİSKLİ"
            recommendation = "Önemli iyileştirmeler yapılması önerilir."
        else:
            status = "🚨 YÜKSEKRİSKLİ"
            recommendation = "Major revizyonlar gerekli, üretimde kullanılmamalı."
        
        summary_lines.append(f"\n📈 DURUM: {status}")
        summary_lines.append(f"💡 ÖNERİ: {recommendation}")
        
        # Sayısal veriler
        summary_lines.append(f"\n📊 VERİ SETİ BOYUTU:")
        summary_lines.append(f"   Toplam Görüntü: {quality_metrics.total_images:,}")
        summary_lines.append(f"   Sınıf Sayısı: {quality_metrics.num_classes}")
        
        # Kritik sorunlar (varsa)
        if quality_metrics.issues_found:
            summary_lines.append(f"\n🚨 KRİTİK SORUNLAR ({len(quality_metrics.issues_found)}):")
            for issue in quality_metrics.issues_found[:3]:
                summary_lines.append(f"   • {issue}")
        
        # Öncelikli aksiyonlar
        if quality_metrics.recommendations:
            summary_lines.append(f"\n🎯 ÖNCELİKLİ AKSİYONLAR:")
            for rec in quality_metrics.recommendations[:3]:
                summary_lines.append(f"   • {rec}")
        
        summary_lines.append("\n" + "=" * 60)
        summary_lines.append(f"📅 Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        
        return "\n".join(summary_lines)
    
    def save_executive_summary(self, quality_metrics) -> Optional[Path]:
        """Yönetici özetini dosyaya kaydet"""
        try:
            summary_content = self.create_executive_summary(quality_metrics)
            summary_path = self.reports_dir / f'executive_summary_{self.timestamp}.txt'
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            logger.info(f"Yönetici özeti kaydedildi: {summary_path}")
            return summary_path
            
        except Exception as e:
            logger.error(f"Yönetici özeti kaydetme hatası: {str(e)}")
            return None
    
    def create_comparison_report(self, 
                               current_metrics, 
                               baseline_metrics, 
                               quality_assessor) -> Optional[Path]:
        """Karşılaştırma raporu oluştur"""
        try:
            comparison = quality_assessor.compare_with_baseline(baseline_metrics)
            
            report_content = {
                'comparison_timestamp': datetime.now().isoformat(),
                'current_metrics': current_metrics.to_dict(),
                'baseline_metrics': baseline_metrics.to_dict(),
                'comparison_results': comparison,
                'summary': {
                    'overall_change': current_metrics.overall_score - baseline_metrics.overall_score,
                    'grade_change': f"{baseline_metrics.dataset_grade} → {current_metrics.dataset_grade}",
                    'significant_improvements': comparison.get('improvements', []),
                    'areas_of_concern': comparison.get('deteriorations', [])
                }
            }
            
            report_path = self.reports_dir / f'comparison_report_{self.timestamp}.json'
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_content, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Karşılaştırma raporu kaydedildi: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"Karşılaştırma raporu oluşturma hatası: {str(e)}")
            return None
    
    def get_report_index(self) -> Dict[str, List[str]]:
        """Mevcut raporların indeksini oluştur"""
        index = {
            'detailed_reports': [],
            'summary_reports': [],
            'csv_reports': [],
            'recommendations': [],
            'executive_summaries': [],
            'comparison_reports': []
        }
        
        try:
            for file_path in self.reports_dir.glob('*.json'):
                if 'detailed_quality_report' in file_path.name:
                    index['detailed_reports'].append(str(file_path))
                elif 'recommendations' in file_path.name:
                    index['recommendations'].append(str(file_path))
                elif 'comparison_report' in file_path.name:
                    index['comparison_reports'].append(str(file_path))
            
            for file_path in self.reports_dir.glob('*.txt'):
                if 'quality_summary' in file_path.name:
                    index['summary_reports'].append(str(file_path))
                elif 'executive_summary' in file_path.name:
                    index['executive_summaries'].append(str(file_path))
            
            for file_path in self.reports_dir.glob('*.csv'):
                if 'quality_metrics' in file_path.name:
                    index['csv_reports'].append(str(file_path))
            
            # Dosyaları tarihe göre sırala
            for key in index:
                index[key].sort(reverse=True)
                
        except Exception as e:
            logger.error(f"Rapor indeksi oluşturma hatası: {str(e)}")
        
        return index
    
    def cleanup_old_reports(self, keep_last_n: int = 10):
        """Eski raporları temizle"""
        try:
            index = self.get_report_index()
            deleted_count = 0
            
            for report_type, files in index.items():
                if len(files) > keep_last_n:
                    files_to_delete = files[keep_last_n:]
                    for file_path in files_to_delete:
                        try:
                            Path(file_path).unlink()
                            deleted_count += 1
                        except Exception as e:
                            logger.warning(f"Dosya silinemedi {file_path}: {str(e)}")
            
            if deleted_count > 0:
                logger.info(f"{deleted_count} eski rapor dosyası temizlendi")
                
        except Exception as e:
            logger.error(f"Eski rapor temizleme hatası: {str(e)}")
