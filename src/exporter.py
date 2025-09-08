"""
Data exporter for saving processed customer data with metadata and reporting.
"""
import json
import logging
from datetime import datetime
from typing import List, Dict
from pathlib import Path

from .models import CustomerExport, ExportMetadata, DataQualitySummary, ProcessedCustomer


class DataExporter:
    """
    Exports processed customer data to JSON with metadata and summary statistics.
    """
    
    def __init__(self):
        """Initialize the data exporter."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def export_customers(self, customers: List[Dict], output_file: str) -> None:
        """
        Export customers to JSON file with metadata.
        
        Args:
            customers: List of processed customer dictionaries
            output_file: Path to output JSON file
        """
        try:
            # Sort customers by full_name (ascending)
            sorted_customers = sorted(customers, key=lambda x: x.get('full_name', ''))
            
            # Convert to ProcessedCustomer objects for validation
            processed_customers = []
            for customer_data in sorted_customers:
                try:
                    customer = ProcessedCustomer(**customer_data)
                    processed_customers.append(customer)
                except Exception as e:
                    self.logger.warning(f"Invalid customer data, skipping: {e}")
                    continue
            
            # Generate metadata
            metadata = self._generate_metadata(processed_customers)
            
            # Create export structure
            export_data = CustomerExport(
                metadata=metadata,
                customers=processed_customers
            )
            
            # Save to file
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    export_data.model_dump(),
                    f,
                    indent=2,
                    ensure_ascii=False,
                    default=str
                )
            
            self.logger.info(f"Successfully exported {len(processed_customers)} customers to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to export customers: {e}")
            raise
    
    def generate_summary_report(self, customers: List[Dict]) -> Dict:
        """
        Generate summary statistics for the customer data.
        
        Args:
            customers: List of processed customer dictionaries
            
        Returns:
            Dictionary containing summary statistics
        """
        if not customers:
            return {
                "total_customers": 0,
                "data_quality_summary": {
                    "high_quality": 0,
                    "medium_quality": 0,
                    "low_quality": 0
                },
                "engagement_distribution": {},
                "activity_distribution": {},
                "channel_distribution": {},
                "segment_distribution": {},
                "tier_distribution": {},
                "average_quality_score": 0
            }
        
        # Basic statistics
        total_customers = len(customers)
        quality_scores = [c.get('data_quality_score', 0) for c in customers]
        average_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Data quality distribution
        quality_summary = self._calculate_quality_distribution(quality_scores)
        
        # Field distributions
        engagement_dist = self._calculate_field_distribution(customers, 'engagement_level')
        activity_dist = self._calculate_field_distribution(customers, 'activity_status')
        channel_dist = self._calculate_field_distribution(customers, 'acquisition_channel')
        segment_dist = self._calculate_field_distribution(customers, 'market_segment')
        tier_dist = self._calculate_field_distribution(customers, 'customer_tier')
        
        summary = {
            "total_customers": total_customers,
            "data_quality_summary": quality_summary,
            "engagement_distribution": engagement_dist,
            "activity_distribution": activity_dist,
            "channel_distribution": channel_dist,
            "segment_distribution": segment_dist,
            "tier_distribution": tier_dist,
            "average_quality_score": round(average_quality_score, 2)
        }
        
        self.logger.info(f"Generated summary report for {total_customers} customers")
        return summary
    
    def _generate_metadata(self, customers: List[ProcessedCustomer]) -> ExportMetadata:
        """
        Generate metadata for the export.
        
        Args:
            customers: List of ProcessedCustomer objects
            
        Returns:
            ExportMetadata object
        """
        # Calculate data quality summary
        quality_scores = [c.data_quality_score for c in customers]
        quality_summary = DataQualitySummary()
        
        for score in quality_scores:
            if score >= 90:
                quality_summary.high_quality += 1
            elif score >= 70:
                quality_summary.medium_quality += 1
            else:
                quality_summary.low_quality += 1
        
        return ExportMetadata(
            total_customers=len(customers),
            export_timestamp=datetime.utcnow(),
            data_quality_summary=quality_summary
        )
    
    def _calculate_quality_distribution(self, quality_scores: List[int]) -> Dict[str, int]:
        """Calculate distribution of data quality scores."""
        high_quality = sum(1 for score in quality_scores if score >= 90)
        medium_quality = sum(1 for score in quality_scores if 70 <= score < 90)
        low_quality = sum(1 for score in quality_scores if score < 70)
        
        return {
            "high_quality": high_quality,
            "medium_quality": medium_quality,
            "low_quality": low_quality
        }
    
    def _calculate_field_distribution(self, customers: List[Dict], field: str) -> Dict[str, int]:
        """
        Calculate distribution of values for a given field.
        
        Args:
            customers: List of customer dictionaries
            field: Field name to analyze
            
        Returns:
            Dictionary with value counts
        """
        distribution = {}
        
        for customer in customers:
            value = customer.get(field, 'unknown')
            distribution[value] = distribution.get(value, 0) + 1
        
        return distribution
    
    def save_summary_report(self, customers: List[Dict], output_file: str) -> None:
        """
        Save summary report to a separate JSON file.
        
        Args:
            customers: List of processed customer dictionaries
            output_file: Path to output summary file
        """
        try:
            summary = self.generate_summary_report(customers)
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Summary report saved to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save summary report: {e}")
            raise
