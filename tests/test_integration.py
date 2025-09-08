"""
Integration tests for the complete pipeline.
"""
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, Mock

import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.main import main
from src.api_client import CustomerAPIClient
from src.data_processor import CustomerDataProcessor
from src.exporter import DataExporter


class TestIntegration:
    """Integration tests for the complete pipeline."""
    
    @patch('src.api_client.CustomerAPIClient.fetch_all_customers')
    @patch('src.main.Path.mkdir')
    def test_end_to_end_pipeline(self, mock_mkdir, mock_fetch):
        """Test the complete end-to-end pipeline."""
        # Mock data
        mock_customers = [
            {
                'id': 1,
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'avatar': 'https://example.com/avatar1.jpg'
            },
            {
                'id': 2,
                'email': 'jane.smith@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'avatar': 'https://example.com/avatar2.jpg'
            }
        ]
        mock_fetch.return_value = mock_customers
        
        # Use temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.main.Path') as mock_path:
                # Mock Path to use temp directory
                mock_output_dir = Mock()
                mock_output_dir.__truediv__ = lambda self, other: Path(temp_dir) / other
                mock_path.return_value = mock_output_dir
                
                # Mock the mkdir call
                mock_mkdir.return_value = None
                
                # Mock file operations
                with patch('builtins.open') as mock_open:
                    mock_file = Mock()
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    # Run the pipeline
                    result = main()
                    
                    assert result is True
                    assert mock_fetch.called
                    assert mock_open.call_count >= 2  # At least 2 files should be written
    
    def test_api_client_data_processor_integration(self):
        """Test integration between API client and data processor."""
        # Create mock API response
        mock_customers = [
            {
                'id': 1,
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'avatar': 'https://example.com/avatar.jpg'
            }
        ]
        
        # Process the data
        processor = CustomerDataProcessor(seed=42)
        processed_customers = processor.process_customers(mock_customers)
        
        assert len(processed_customers) == 1
        assert processed_customers[0]['customer_id'] == 1
        assert processed_customers[0]['full_name'] == 'Test User'
        assert processed_customers[0]['email_domain'] == 'example.com'
        assert processed_customers[0]['data_quality_score'] == 100
    
    def test_data_processor_exporter_integration(self):
        """Test integration between data processor and exporter."""
        # Create processed customer data
        processed_customers = [
            {
                'customer_id': 1,
                'full_name': 'John Doe',
                'email_domain': 'example.com',
                'engagement_level': 'high',
                'activity_status': 'active',
                'acquisition_channel': 'website',
                'market_segment': 'US-West',
                'customer_tier': 'premium',
                'data_quality_score': 100
            }
        ]
        
        # Test exporter
        exporter = DataExporter()
        
        # Test summary generation
        summary = exporter.generate_summary_report(processed_customers)
        
        assert summary['total_customers'] == 1
        assert summary['average_quality_score'] == 100
        assert summary['data_quality_summary']['high_quality'] == 1
        assert summary['engagement_distribution']['high'] == 1
        assert summary['activity_distribution']['active'] == 1
    
    def test_complete_pipeline_with_real_data_structure(self):
        """Test complete pipeline with realistic data structure."""
        # Simulate reqres.in API response structure
        mock_api_data = [
            {
                'id': 1,
                'email': 'george.bluth@reqres.in',
                'first_name': 'George',
                'last_name': 'Bluth',
                'avatar': 'https://reqres.in/img/faces/1-image.jpg'
            },
            {
                'id': 2,
                'email': 'janet.weaver@reqres.in',
                'first_name': 'Janet',
                'last_name': 'Weaver',
                'avatar': 'https://reqres.in/img/faces/2-image.jpg'
            }
        ]
        
        # Process through the pipeline
        processor = CustomerDataProcessor(seed=42)
        processed_customers = processor.process_customers(mock_api_data)
        
        # Verify processing
        assert len(processed_customers) == 2
        
        # Check that all customers have required fields
        for customer in processed_customers:
            assert 'customer_id' in customer
            assert 'full_name' in customer
            assert 'email_domain' in customer
            assert 'engagement_level' in customer
            assert 'activity_status' in customer
            assert 'acquisition_channel' in customer
            assert 'market_segment' in customer
            assert 'customer_tier' in customer
            assert 'data_quality_score' in customer
        
        # Test export functionality
        exporter = DataExporter()
        summary = exporter.generate_summary_report(processed_customers)
        
        assert summary['total_customers'] == 2
        assert isinstance(summary['average_quality_score'], (int, float))
        assert 'data_quality_summary' in summary
        assert 'engagement_distribution' in summary


if __name__ == '__main__':
    pytest.main([__file__])
