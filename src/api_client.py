"""
Robust API client for fetching customer data with retry logic and error handling.
"""
import requests
import time
import logging
import random
from typing import List, Dict, Optional
from urllib.parse import urljoin

from .models import APIResponse, RawCustomer


class CustomerAPIClient:
    """
    Robust API client that handles pagination, retries, and rate limiting.
    """
    
    def __init__(self, base_url: str, api_key: str, max_retries: int = 3):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the API
            api_key: API key for authentication
            max_retries: Maximum number of retries for failed requests
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        })
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def fetch_all_customers(self) -> List[Dict]:
        """
        Fetch all customers from all pages.
        
        Returns:
            List of all customer dictionaries
            
        Raises:
            Exception: If unable to fetch data after all retries
        """
        all_customers = []
        page = 1
        total_pages = None
        
        self.logger.info("Starting to fetch all customers...")
        
        while total_pages is None or page <= total_pages:
            try:
                self.logger.info(f"Fetching page {page}...")
                response_data = self._fetch_page(page)
                
                if total_pages is None:
                    total_pages = response_data['total_pages']
                    self.logger.info(f"Total pages to fetch: {total_pages}")
                
                # Validate and parse response
                api_response = APIResponse(**response_data)
                
                # Add customers from this page
                for customer in api_response.data:
                    all_customers.append(customer.model_dump())
                
                self.logger.info(f"Successfully fetched page {page} with {len(api_response.data)} customers")
                page += 1
                
                # Add small delay to be respectful to the API
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Failed to fetch page {page}: {e}")
                raise
        
        # Remove duplicates based on customer ID
        unique_customers = self._deduplicate_customers(all_customers)
        
        self.logger.info(f"Fetched {len(unique_customers)} unique customers from {total_pages} pages")
        return unique_customers
    
    def _fetch_page(self, page: int) -> Dict:
        """
        Fetch a single page with retry logic.
        
        Args:
            page: Page number to fetch
            
        Returns:
            API response data
            
        Raises:
            Exception: If all retries are exhausted
        """
        url = urljoin(self.base_url, f"/api/users?page={page}")
        
        for attempt in range(self.max_retries + 1):
            try:
                # Simulate network instability (20% failure rate)
                if random.random() < 0.2:
                    # Simulate different types of failures
                    error_type = random.choice([500, 503, 429])
                    self.logger.warning(f"Simulated {error_type} error on attempt {attempt + 1}")
                    
                    if error_type == 429:
                        # Rate limiting
                        response = requests.Response()
                        response.status_code = 429
                        response._content = b'{"error": "Too Many Requests"}'
                        raise requests.exceptions.HTTPError(response=response)
                    else:
                        # Server errors
                        response = requests.Response()
                        response.status_code = error_type
                        response._content = b'{"error": "Server Error"}'
                        raise requests.exceptions.HTTPError(response=response)
                
                # Make the actual request
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                self.logger.info(f"Successfully fetched page {page} on attempt {attempt + 1}")
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    # Rate limiting - wait longer
                    wait_time = 2 ** attempt + random.uniform(0, 1)
                    self.logger.warning(f"Rate limited on page {page}, attempt {attempt + 1}. Waiting {wait_time:.2f}s")
                    time.sleep(wait_time)
                elif e.response.status_code >= 500:
                    # Server error - exponential backoff
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Server error on page {page}, attempt {attempt + 1}. Waiting {wait_time}s")
                    time.sleep(wait_time)
                else:
                    # Client error - don't retry
                    self.logger.error(f"Client error on page {page}: {e}")
                    raise
                    
            except (requests.exceptions.RequestException, Exception) as e:
                wait_time = 2 ** attempt
                self.logger.warning(f"Request failed on page {page}, attempt {attempt + 1}: {e}. Waiting {wait_time}s")
                time.sleep(wait_time)
            
            # If this was the last attempt, raise an exception
            if attempt == self.max_retries:
                self.logger.error(f"Exhausted all {self.max_retries + 1} attempts for page {page}")
                raise Exception(f"Failed to fetch page {page} after {self.max_retries + 1} attempts")
    
    def _deduplicate_customers(self, customers: List[Dict]) -> List[Dict]:
        """
        Remove duplicate customers based on ID.
        
        Args:
            customers: List of customer dictionaries
            
        Returns:
            List of unique customers
        """
        seen_ids = set()
        unique_customers = []
        
        for customer in customers:
            customer_id = customer.get('id')
            if customer_id not in seen_ids:
                seen_ids.add(customer_id)
                unique_customers.append(customer)
            else:
                self.logger.warning(f"Duplicate customer found with ID: {customer_id}")
        
        return unique_customers
