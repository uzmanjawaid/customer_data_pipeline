"""
Tests for the CustomerAPIClient class.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from requests.exceptions import HTTPError, RequestException

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.api_client import CustomerAPIClient


class TestCustomerAPIClient:
    """Test cases for CustomerAPIClient."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = CustomerAPIClient(
            base_url="https://test.api",
            api_key="test-key",
            max_retries=2
        )
    
    def test_initialization(self):
        """Test client initialization."""
        assert self.client.base_url == "https://test.api"
        assert self.client.api_key == "test-key"
        assert self.client.max_retries == 2
        assert 'x-api-key' in self.client.session.headers
        assert self.client.session.headers['x-api-key'] == "test-key"
    
    @patch('src.api_client.CustomerAPIClient._fetch_page')
    def test_fetch_all_customers_success(self, mock_fetch_page):
        """Test successful fetching of all customers."""
        # Mock responses for two pages
        mock_fetch_page.side_effect = [
            {
                'page': 1,
                'per_page': 2,
                'total': 3,
                'total_pages': 2,
                'data': [
                    {'id': 1, 'email': 'test1@test.com', 'first_name': 'Test', 'last_name': 'One', 'avatar': 'url1'},
                    {'id': 2, 'email': 'test2@test.com', 'first_name': 'Test', 'last_name': 'Two', 'avatar': 'url2'}
                ]
            },
            {
                'page': 2,
                'per_page': 2,
                'total': 3,
                'total_pages': 2,
                'data': [
                    {'id': 3, 'email': 'test3@test.com', 'first_name': 'Test', 'last_name': 'Three', 'avatar': 'url3'}
                ]
            }
        ]
        
        customers = self.client.fetch_all_customers()
        
        assert len(customers) == 3
        assert mock_fetch_page.call_count == 2
        assert customers[0]['id'] == 1
        assert customers[1]['id'] == 2
        assert customers[2]['id'] == 3
    
    @patch('src.api_client.time.sleep')
    @patch('src.api_client.requests.Session.get')
    def test_fetch_page_retry_on_server_error(self, mock_get, mock_sleep):
        """Test retry logic on server errors."""
        # First call fails with 500, second succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        mock_response_fail.raise_for_status.side_effect = HTTPError(response=mock_response_fail)
        
        mock_response_success = Mock()
        mock_response_success.raise_for_status.return_value = None
        mock_response_success.json.return_value = {
            'page': 1, 'per_page': 1, 'total': 1, 'total_pages': 1,
            'data': [{'id': 1, 'email': 'test@test.com', 'first_name': 'Test', 'last_name': 'User', 'avatar': 'url'}]
        }
        
        mock_get.side_effect = [mock_response_fail, mock_response_success]
        
        # Disable random failures for this test
        with patch('src.api_client.random.random', return_value=0.5):
            result = self.client._fetch_page(1)
        
        assert result['page'] == 1
        assert mock_get.call_count == 2
        assert mock_sleep.called
    
    @patch('src.api_client.time.sleep')
    @patch('src.api_client.requests.Session.get')
    def test_fetch_page_retry_exhaustion(self, mock_get, mock_sleep):
        """Test behavior when all retries are exhausted."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        # Disable random failures for this test
        with patch('src.api_client.random.random', return_value=0.5):
            with pytest.raises(Exception, match="Failed to fetch page 1"):
                self.client._fetch_page(1)
        
        assert mock_get.call_count == 3  # Initial + 2 retries
    
    @patch('src.api_client.time.sleep')
    @patch('src.api_client.requests.Session.get')
    def test_fetch_page_rate_limiting(self, mock_get, mock_sleep):
        """Test handling of rate limiting (429 errors)."""
        mock_response_rate_limited = Mock()
        mock_response_rate_limited.status_code = 429
        mock_response_rate_limited.raise_for_status.side_effect = HTTPError(response=mock_response_rate_limited)
        
        mock_response_success = Mock()
        mock_response_success.raise_for_status.return_value = None
        mock_response_success.json.return_value = {
            'page': 1, 'per_page': 1, 'total': 1, 'total_pages': 1,
            'data': [{'id': 1, 'email': 'test@test.com', 'first_name': 'Test', 'last_name': 'User', 'avatar': 'url'}]
        }
        
        mock_get.side_effect = [mock_response_rate_limited, mock_response_success]
        
        # Disable random failures for this test
        with patch('src.api_client.random.random', return_value=0.5):
            result = self.client._fetch_page(1)
        
        assert result['page'] == 1
        assert mock_sleep.called
    
    def test_deduplicate_customers(self):
        """Test customer deduplication."""
        customers = [
            {'id': 1, 'name': 'John'},
            {'id': 2, 'name': 'Jane'},
            {'id': 1, 'name': 'John Duplicate'},  # Duplicate
            {'id': 3, 'name': 'Bob'}
        ]
        
        unique_customers = self.client._deduplicate_customers(customers)
        
        assert len(unique_customers) == 3
        customer_ids = [c['id'] for c in unique_customers]
        assert customer_ids == [1, 2, 3]
    
    @patch('src.api_client.random.random', return_value=0.9)  # No simulated failures
    @patch('src.api_client.requests.Session.get')
    def test_successful_api_call(self, mock_get):
        """Test successful API call without simulated failures."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'page': 1, 'per_page': 1, 'total': 1, 'total_pages': 1,
            'data': [{'id': 1, 'email': 'test@test.com', 'first_name': 'Test', 'last_name': 'User', 'avatar': 'url'}]
        }
        mock_get.return_value = mock_response
        
        result = self.client._fetch_page(1)
        
        assert result['page'] == 1
        assert mock_get.call_count == 1


if __name__ == '__main__':
    pytest.main([__file__])
