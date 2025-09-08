#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main orchestration script for the customer data pipeline.
"""
import logging
import sys
from pathlib import Path

from .api_client import CustomerAPIClient
from .data_processor import CustomerDataProcessor
from .exporter import DataExporter


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('pipeline.log')
        ]
    )


def main():
    """
    Main function to orchestrate the entire data pipeline.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=== Starting Customer Data Pipeline ===")
    
    try:
        # Configuration
        base_url = "https://reqres.in"
        api_key = "reqres-free-v1"
        
        # Initialize components
        logger.info("Initializing pipeline components...")
        api_client = CustomerAPIClient(base_url=base_url, api_key=api_key, max_retries=3)
        data_processor = CustomerDataProcessor(seed=42)  # Fixed seed for reproducible results
        exporter = DataExporter()
        
        # Step 1: Fetch customer data
        logger.info("Step 1: Fetching customer data from API...")
        raw_customers = api_client.fetch_all_customers()
        logger.info(f"Fetched {len(raw_customers)} raw customers")
        
        # Step 2: Process and transform data
        logger.info("Step 2: Processing and transforming customer data...")
        processed_customers = data_processor.process_customers(raw_customers)
        logger.info(f"Processed {len(processed_customers)} customers")
        
        # Step 3: Generate summary report
        logger.info("Step 3: Generating summary report...")
        summary = exporter.generate_summary_report(processed_customers)
        
        # Log summary statistics
        logger.info("=== PIPELINE SUMMARY ===")
        logger.info(f"Total customers processed: {summary['total_customers']}")
        logger.info(f"Average quality score: {summary['average_quality_score']}")
        logger.info(f"Data quality distribution: {summary['data_quality_summary']}")
        logger.info(f"Engagement levels: {summary['engagement_distribution']}")
        logger.info(f"Activity status: {summary['activity_distribution']}")
        
        # Step 4: Export data
        logger.info("Step 4: Exporting processed data...")
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Export customers data
        customers_file = output_dir / "processed_customers.json"
        exporter.export_customers(processed_customers, str(customers_file))
        
        # Export summary report
        summary_file = output_dir / "summary_report.json"
        exporter.save_summary_report(processed_customers, str(summary_file))
        
        logger.info("=== Pipeline completed successfully! ===")
        logger.info(f"Output files:")
        logger.info(f"  - Customer data: {customers_file}")
        logger.info(f"  - Summary report: {summary_file}")
        logger.info(f"  - Pipeline log: pipeline.log")
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        raise


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Customer data pipeline completed successfully!")
            print("��� Check the 'output' directory for results")
        else:
            print("\n❌ Pipeline failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        sys.exit(1)
