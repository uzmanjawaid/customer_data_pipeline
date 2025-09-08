"""
Tests for the CustomerDataProcessor class.
"""
import pytest
from unittest.mock import patch

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.data_processor import CustomerDataProcessor
from src.models import EngagementLevel, ActivityStatus, CustomerTier


class TestCustomerDataProcessor:
    """Test cases for CustomerDataProcessor."""
    
    def setup_method(self):
        """Setup test processor with fixed seed for reproducibility."""
        self.processor = CustomerDataProcessor(seed=42)
    
    def test_initialization(self):
        """Test processor initialization."""
        assert self.processor is not None
    
    def test_process_single_customer_valid_data(self):
        """Test processing a single valid customer."""
        raw_customer = {
            'id': 1,
            'email': 'john.doe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'avatar': 'https://example.com/avatar.jpg'
        }
        
        processed = self.processor._process_single_customer(raw_customer)
        
        assert processed.customer_id == 1
        assert processed.full_name == 'John Doe'
        assert processed.email_domain == 'example.com'
        assert processed.data_quality_score == 100
        assert isinstance(processed.engagement_level, EngagementLevel)
        assert isinstance(processed.activity_status, ActivityStatus)
        assert isinstance(processed.customer_tier, CustomerTier)
    
    def test_build_full_name(self):
        """Test full name building with various inputs."""
        # Both names present
        assert self.processor._build_full_name('John', 'Doe') == 'John Doe'
        
        # Only first name
        assert self.processor._build_full_name('John', '') == 'John'
        
        # Only last name
        assert self.processor._build_full_name('', 'Doe') == 'Doe'
        
        # No names
        assert self.processor._build_full_name('', '') == 'Unknown Name'
        
        # None values
        assert self.processor._build_full_name(None, None) == 'Unknown Name'
    
    def test_extract_email_domain(self):
        """Test email domain extraction."""
        # Valid emails
        assert self.processor._extract_email_domain('user@example.com') == 'example.com'
        assert self.processor._extract_email_domain('test.user@subdomain.example.org') == 'subdomain.example.org'
        
        # Invalid emails
        assert self.processor._extract_email_domain('invalid-email') == 'unknown'
        assert self.processor._extract_email_domain('user@') == 'unknown'
        assert self.processor._extract_email_domain('@domain.com') == 'unknown'
        assert self.processor._extract_email_domain('') == 'unknown'
        assert self.processor._extract_email_domain(None) == 'unknown'
    
    def test_data_quality_score_calculation(self):
        """Test data quality score calculation."""
        # Perfect data
        perfect_customer = {
            'id': 1,
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'avatar': 'https://example.com/avatar.jpg'
        }
        score = self.processor._calculate_data_quality_score(perfect_customer)
        assert score == 100
        
        # Missing fields
        incomplete_customer = {
            'id': 1,
            'email': 'user@example.com',
            'first_name': '',
            'last_name': 'Doe',
            'avatar': ''
        }
        score = self.processor._calculate_data_quality_score(incomplete_customer)
        assert score == 80  # 100 - 10 for empty first_name - 10 for empty avatar
        
        # Invalid email
        invalid_email_customer = {
            'id': 1,
            'email': 'invalid-email',
            'first_name': 'John',
            'last_name': 'Doe',
            'avatar': 'https://example.com/avatar.jpg'
        }
        score = self.processor._calculate_data_quality_score(invalid_email_customer)
        assert score == 90  # 100 - 10 for invalid email
    
    def test_handle_duplicates(self):
        """Test duplicate handling logic."""
        customers = [
            {
                'customer_id': 1,
                'full_name': 'John Doe',
                'data_quality_score': 80,
                'email_domain': 'example.com',
                'engagement_level': 'high',
                'activity_status': 'active',
                'acquisition_channel': 'website',
                'market_segment': 'US-West',
                'customer_tier': 'premium'
            },
            {
                'customer_id': 2,
                'full_name': 'Jane Smith',
                'data_quality_score': 100,
                'email_domain': 'example.com',
                'engagement_level': 'medium',
                'activity_status': 'active',
                'acquisition_channel': 'mobile_app',
                'market_segment': 'US-East',
                'customer_tier': 'basic'
            },
            {
                'customer_id': 1,  # Duplicate
                'full_name': 'John Doe Updated',
                'data_quality_score': 90,  # Higher quality
                'email_domain': 'example.com',
                'engagement_level': 'high',
                'activity_status': 'active',
                'acquisition_channel': 'website',
                'market_segment': 'US-West',
                'customer_tier': 'premium'
            }
        ]
        
        unique_customers = self.processor._handle_duplicates(customers)
        
        assert len(unique_customers) == 2
        # Should keep the duplicate with higher quality score
        john_doe = next(c for c in unique_customers if c['customer_id'] == 1)
        assert john_doe['data_quality_score'] == 90
        assert john_doe['full_name'] == 'John Doe Updated'
    
    def test_process_customers_with_error_handling(self):
        """Test processing multiple customers with error handling."""
        raw_customers = [
            {
                'id': 1,
                'email': 'valid@example.com',
                'first_name': 'Valid',
                'last_name': 'User',
                'avatar': 'url'
            },
            {
                # Missing required field
                'email': 'incomplete@example.com',
                'first_name': 'Incomplete',
                'last_name': 'User',
                'avatar': 'url'
            },
            {
                'id': 2,
                'email': 'another@example.com',
                'first_name': 'Another',
                'last_name': 'User',
                'avatar': 'url'
            }
        ]
        
        processed = self.processor.process_customers(raw_customers)
        
        # Should process valid customers and skip invalid ones
        assert len(processed) == 2
        assert all(c['customer_id'] in [1, 2] for c in processed)
    
    def test_weighted_choice(self):
        """Test weighted random choice logic."""
        choices = [
            ('option1', 0.5),
            ('option2', 0.3),
            ('option3', 0.2)
        ]
        
        # Test that it returns one of the valid options
        result = self.processor._weighted_choice(choices)
        assert result in ['option1', 'option2', 'option3']
        
        # Test with single option
        single_choice = [('only_option', 1.0)]
        result = self.processor._weighted_choice(single_choice)
        assert result == 'only_option'
    
    def test_generate_business_fields(self):
        """Test generation of business logic fields."""
        # Test that all generator methods return valid enum values
        engagement = self.processor._generate_engagement_level()
        assert engagement in EngagementLevel
        
        activity = self.processor._generate_activity_status()
        assert activity in ActivityStatus
        
        tier = self.processor._generate_customer_tier()
        assert tier in CustomerTier


if __name__ == '__main__':
    pytest.main([__file__])
