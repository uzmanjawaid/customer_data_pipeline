"""
Data processor for transforming raw customer data into analytics-ready format.
"""
import random
import logging
import re
from typing import List, Dict
from urllib.parse import urlparse

from .models import (
    ProcessedCustomer, EngagementLevel, ActivityStatus, 
    AcquisitionChannel, MarketSegment, CustomerTier
)


class CustomerDataProcessor:
    """
    Processes and transforms raw customer data with business logic.
    """
    
    def __init__(self, seed: int = None):
        """
        Initialize the data processor.
        
        Args:
            seed: Random seed for reproducible results
        """
        if seed is not None:
            random.seed(seed)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def process_customers(self, raw_customers: List[Dict]) -> List[Dict]:
        """
        Transform raw customer data into analytics-ready format.
        
        Args:
            raw_customers: List of raw customer dictionaries
            
        Returns:
            List of processed customer dictionaries
        """
        processed_customers = []
        
        self.logger.info(f"Processing {len(raw_customers)} customers...")
        
        for raw_customer in raw_customers:
            try:
                processed_customer = self._process_single_customer(raw_customer)
                processed_customers.append(processed_customer.model_dump())
                
            except Exception as e:
                self.logger.error(f"Failed to process customer {raw_customer.get('id', 'unknown')}: {e}")
                # Continue processing other customers
                continue
        
        # Handle duplicates by keeping the one with highest data quality score
        unique_customers = self._handle_duplicates(processed_customers)
        
        self.logger.info(f"Successfully processed {len(unique_customers)} unique customers")
        return unique_customers
    
    def _process_single_customer(self, raw_customer: Dict) -> ProcessedCustomer:
        """
        Process a single customer record.
        
        Args:
            raw_customer: Raw customer dictionary
            
        Returns:
            ProcessedCustomer object
        """
        # Extract basic fields
        customer_id = raw_customer.get('id')
        first_name = raw_customer.get('first_name', '').strip()
        last_name = raw_customer.get('last_name', '').strip()
        email = raw_customer.get('email', '').strip()
        
        # Build full name
        full_name = self._build_full_name(first_name, last_name)
        
        # Extract email domain
        email_domain = self._extract_email_domain(email)
        
        # Generate business fields
        engagement_level = self._generate_engagement_level()
        activity_status = self._generate_activity_status()
        acquisition_channel = self._generate_acquisition_channel()
        market_segment = self._generate_market_segment()
        customer_tier = self._generate_customer_tier()
        
        # Calculate data quality score
        data_quality_score = self._calculate_data_quality_score(raw_customer)
        
        return ProcessedCustomer(
            customer_id=customer_id,
            full_name=full_name,
            email_domain=email_domain,
            engagement_level=engagement_level,
            activity_status=activity_status,
            acquisition_channel=acquisition_channel,
            market_segment=market_segment,
            customer_tier=customer_tier,
            data_quality_score=data_quality_score
        )
    
    def _build_full_name(self, first_name: str, last_name: str) -> str:
        """Build full name from first and last name."""
        names = []
        if first_name:
            names.append(first_name)
        if last_name:
            names.append(last_name)
        
        if not names:
            return "Unknown Name"
        
        return " ".join(names)
    
    def _extract_email_domain(self, email: str) -> str:
        """
        Extract domain from email address.
        
        Args:
            email: Email address
            
        Returns:
            Email domain or "unknown" if invalid
        """
        if not email:
            return "unknown"
        
        # Simple email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            self.logger.warning(f"Invalid email format: {email}")
            return "unknown"
        
        try:
            domain = email.split('@')[1].lower()
            return domain
        except (IndexError, AttributeError):
            self.logger.warning(f"Could not extract domain from email: {email}")
            return "unknown"
    
    def _generate_engagement_level(self) -> EngagementLevel:
        """Generate random engagement level with realistic distribution."""
        choices = [
            (EngagementLevel.HIGH, 0.3),
            (EngagementLevel.MEDIUM, 0.5),
            (EngagementLevel.LOW, 0.2)
        ]
        return self._weighted_choice(choices)
    
    def _generate_activity_status(self) -> ActivityStatus:
        """Generate random activity status with realistic distribution."""
        choices = [
            (ActivityStatus.ACTIVE, 0.8),
            (ActivityStatus.INACTIVE, 0.2)
        ]
        return self._weighted_choice(choices)
    
    def _generate_acquisition_channel(self) -> AcquisitionChannel:
        """Generate random acquisition channel with realistic distribution."""
        choices = [
            (AcquisitionChannel.WEBSITE, 0.5),
            (AcquisitionChannel.MOBILE_APP, 0.3),
            (AcquisitionChannel.EMAIL_CAMPAIGN, 0.2)
        ]
        return self._weighted_choice(choices)
    
    def _generate_market_segment(self) -> MarketSegment:
        """Generate random market segment with realistic distribution."""
        choices = [
            (MarketSegment.US_WEST, 0.3),
            (MarketSegment.US_EAST, 0.3),
            (MarketSegment.EU_CENTRAL, 0.25),
            (MarketSegment.APAC, 0.15)
        ]
        return self._weighted_choice(choices)
    
    def _generate_customer_tier(self) -> CustomerTier:
        """Generate random customer tier with realistic distribution."""
        choices = [
            (CustomerTier.BASIC, 0.6),
            (CustomerTier.PREMIUM, 0.3),
            (CustomerTier.ENTERPRISE, 0.1)
        ]
        return self._weighted_choice(choices)
    
    def _weighted_choice(self, choices: List[tuple]) -> any:
        """
        Make a weighted random choice.
        
        Args:
            choices: List of (value, weight) tuples
            
        Returns:
            Chosen value
        """
        total_weight = sum(weight for _, weight in choices)
        r = random.uniform(0, total_weight)
        
        cumulative_weight = 0
        for value, weight in choices:
            cumulative_weight += weight
            if r <= cumulative_weight:
                return value
        
        # Fallback to last choice
        return choices[-1][0]
    
    def _calculate_data_quality_score(self, raw_customer: Dict) -> int:
        """
        Calculate data quality score based on completeness and validity.
        
        Args:
            raw_customer: Raw customer dictionary
            
        Returns:
            Quality score (0-100)
        """
        score = 100
        required_fields = ['id', 'email', 'first_name', 'last_name', 'avatar']
        
        for field in required_fields:
            value = raw_customer.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                score -= 10
                self.logger.debug(f"Missing or empty field '{field}' for customer {raw_customer.get('id')}")
        
        # Additional validation for email format
        email = raw_customer.get('email', '').strip()
        if email and self._extract_email_domain(email) == "unknown":
            score -= 10
            self.logger.debug(f"Invalid email format for customer {raw_customer.get('id')}")
        
        return max(0, score)
    
    def _handle_duplicates(self, customers: List[Dict]) -> List[Dict]:
        """
        Handle duplicate customers by keeping the one with highest quality score.
        
        Args:
            customers: List of processed customer dictionaries
            
        Returns:
            List of unique customers
        """
        customer_map = {}
        
        for customer in customers:
            customer_id = customer['customer_id']
            
            if customer_id not in customer_map:
                customer_map[customer_id] = customer
            else:
                # Keep the one with higher data quality score
                existing_score = customer_map[customer_id]['data_quality_score']
                new_score = customer['data_quality_score']
                
                if new_score > existing_score:
                    self.logger.info(f"Replacing duplicate customer {customer_id} with higher quality record")
                    customer_map[customer_id] = customer
                else:
                    self.logger.info(f"Keeping existing customer {customer_id} with higher quality record")
        
        return list(customer_map.values())
