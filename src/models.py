"""
Data models for the e-commerce analytics data pipeline.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum


class EngagementLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class ActivityStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNKNOWN = "unknown"


class AcquisitionChannel(str, Enum):
    WEBSITE = "website"
    MOBILE_APP = "mobile_app"
    EMAIL_CAMPAIGN = "email_campaign"


class MarketSegment(str, Enum):
    US_WEST = "US-West"
    US_EAST = "US-East"
    EU_CENTRAL = "EU-Central"
    APAC = "APAC"


class CustomerTier(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class RawCustomer(BaseModel):
    """Raw customer data from the API."""
    id: int
    email: str
    first_name: str
    last_name: str
    avatar: str


class ProcessedCustomer(BaseModel):
    """Processed customer data for analytics."""
    customer_id: int
    full_name: str
    email_domain: str
    engagement_level: EngagementLevel
    activity_status: ActivityStatus
    acquisition_channel: AcquisitionChannel
    market_segment: MarketSegment
    customer_tier: CustomerTier
    data_quality_score: int = Field(ge=0, le=100)


class APIResponse(BaseModel):
    """API response structure from reqres.in."""
    page: int
    per_page: int
    total: int
    total_pages: int
    data: List[RawCustomer]


class DataQualitySummary(BaseModel):
    """Summary of data quality metrics."""
    high_quality: int = 0  # score >= 90
    medium_quality: int = 0  # score >= 70
    low_quality: int = 0  # score < 70


class ExportMetadata(BaseModel):
    """Metadata for exported data."""
    total_customers: int
    export_timestamp: datetime
    data_quality_summary: DataQualitySummary


class CustomerExport(BaseModel):
    """Complete export structure."""
    metadata: ExportMetadata
    customers: List[ProcessedCustomer]
