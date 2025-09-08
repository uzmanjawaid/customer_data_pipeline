# Customer Data Pipeline

A robust e-commerce analytics data pipeline that fetches, processes, and standardizes customer data from third-party APIs with comprehensive error handling and data quality management.

## ��� Features

- **Robust API Client**: Handles pagination, retries, rate limiting, and network failures
- **Data Processing**: Transforms raw API data into analytics-ready format with business logic
- **Data Quality**: Comprehensive scoring and validation with edge case handling
- **Export & Reporting**: JSON export with metadata and detailed summary statistics
- **Production Ready**: Comprehensive logging, error handling, and test coverage
- **Type Safety**: Full Pydantic model validation and type hints

## ��� Project Structure

```
customer_data_pipeline/
├── src/
│   ├── __init__.py
│   ├── models.py              # Pydantic data models
│   ├── api_client.py          # Robust API client with retry logic
│   ├── data_processor.py      # Data transformation and business logic
│   ├── exporter.py            # JSON export and reporting
│   └── main.py                # Main orchestration script
├── tests/
│   ├── __init__.py
│   ├── test_api_client.py     # API client tests
│   ├── test_data_processor.py # Data processor tests
│   └── test_integration.py    # End-to-end integration tests
├── output/                    # Generated output files
├── requirements.txt           # Python dependencies
├── pipeline.log              # Application logs
└── README.md                 # This file
```

## ��️ Installation

1. **Clone/Navigate to the project directory:**
   ```bash
   cd customer_data_pipeline
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## ��� Usage

### Running the Complete Pipeline

Execute the main pipeline script to fetch, process, and export customer data:

```bash
python -m src.main
```

This will:
1. Fetch customer data from the reqres.in API
2. Process and transform the data with business logic
3. Generate comprehensive reports
4. Export results to the `output/` directory

### Expected Output

The pipeline generates the following files:

- **`output/processed_customers.json`**: Complete customer data with metadata
- **`output/summary_report.json`**: Detailed analytics and statistics
- **`pipeline.log`**: Comprehensive execution logs

### Sample Output Structure

**Processed Customer Data:**
```json
{
  "metadata": {
    "total_customers": 12,
    "export_timestamp": "2024-01-20T15:30:00Z",
    "data_quality_summary": {
      "high_quality": 10,
      "medium_quality": 2,
      "low_quality": 0
    }
  },
  "customers": [
    {
      "customer_id": 1,
      "full_name": "George Bluth",
      "email_domain": "reqres.in",
      "engagement_level": "high",
      "activity_status": "active",
      "acquisition_channel": "website",
      "market_segment": "US-West",
      "customer_tier": "premium",
      "data_quality_score": 100
    }
  ]
}
```

## ��� Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_api_client.py -v
pytest tests/test_data_processor.py -v
pytest tests/test_integration.py -v

# Run tests with coverage
pip install pytest-cov
pytest tests/ --cov=src --cov-report=html
```

## ���️ Architecture

### Components

1. **CustomerAPIClient** (`src/api_client.py`)
   - Handles API communication with retry logic
   - Implements exponential backoff for failures
   - Manages pagination and rate limiting
   - Deduplicates customer records

2. **CustomerDataProcessor** (`src/data_processor.py`)
   - Transforms raw API data to business format
   - Generates business logic fields (engagement, segments, etc.)
   - Calculates data quality scores
   - Handles edge cases and missing data

3. **DataExporter** (`src/exporter.py`)
   - Exports processed data to JSON format
   - Generates comprehensive summary reports
   - Provides detailed analytics and statistics

4. **Data Models** (`src/models.py`)
   - Pydantic models for type safety and validation
   - Enums for business logic categories
   - Complete data schemas for API and export

### Error Handling Strategy

- **API Failures**: Retry with exponential backoff (1s, 2s, 4s)
- **Rate Limiting**: Special handling for 429 responses
- **Data Quality**: Graceful degradation for missing/invalid fields
- **Logging**: Comprehensive logging at all levels
- **Validation**: Pydantic model validation throughout

### Data Quality Scoring

- **Perfect Score (100)**: All fields present and valid
- **Deductions**: -10 points per missing/invalid field
- **Email Validation**: Additional validation for email format
- **Duplicate Handling**: Keep highest quality score

## ��� Configuration

Key configuration options in `src/main.py`:

```python
# API Configuration
base_url = "https://reqres.in"
api_key = "reqres-free-v1"

# Retry Configuration
max_retries = 3

# Random Seed for Reproducible Results
seed = 42
```

## ��� Business Logic

### Generated Fields

The pipeline enriches raw customer data with business intelligence:

- **Engagement Level**: High/Medium/Low (weighted random distribution)
- **Activity Status**: Active/Inactive (80%/20% distribution)
- **Acquisition Channel**: Website/Mobile/Email (50%/30%/20%)
- **Market Segment**: US-West/US-East/EU/APAC (regional distribution)
- **Customer Tier**: Basic/Premium/Enterprise (60%/30%/10%)

### Data Transformations

- **Full Name**: Combines first_name + last_name
- **Email Domain**: Extracts domain from email (with validation)
- **Data Quality Score**: Calculated based on field completeness
- **Deduplication**: Based on customer ID with quality preference

## ��� API Simulation

The pipeline simulates real-world API challenges:

- **20% Failure Rate**: Random HTTP 500/503 errors
- **Rate Limiting**: Simulated 429 responses
- **Network Delays**: Realistic response times
- **Pagination**: Multi-page data retrieval

## ��� Monitoring & Observability

### Logging

Comprehensive logging includes:
- API request/response details
- Retry attempts and failures
- Data processing statistics
- Quality score distributions
- Performance metrics

### Metrics Tracked

- Total customers processed
- API success/failure rates
- Retry attempt counts
- Data quality distributions
- Processing times per stage

## ��� Troubleshooting

### Common Issues

1. **API Timeouts**: Increase retry count or timeout values
2. **Rate Limiting**: Reduce request frequency or increase backoff
3. **Data Quality Issues**: Check field mappings and validation rules
4. **Memory Usage**: Process data in chunks for large datasets

### Debug Mode

Enable debug logging by modifying the log level:

```python
logging.basicConfig(level=logging.DEBUG)
```

## ��� Advanced Features (Future Enhancements)

### Planned Improvements

1. **Async Processing**: Use `asyncio` for concurrent API calls
2. **Caching**: Redis integration for API response caching
3. **Monitoring**: Prometheus metrics and Grafana dashboards
4. **Configuration**: Environment-based configuration management
5. **Data Validation**: Enhanced Pydantic validation rules

### Performance Optimizations

- Implement connection pooling
- Add progress tracking for large datasets
- Optimize memory usage for batch processing
- Add database storage options

## ��� Requirements

- Python 3.8+
- Internet connection (for API access)
- ~50MB free disk space (for output files)

### Dependencies

- `requests>=2.31.0`: HTTP client with retry capabilities
- `pydantic>=2.4.0`: Data validation and settings management
- `pytest>=7.4.0`: Testing framework
- `pytest-mock>=3.11.0`: Mocking for tests

## ��� Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes with proper tests
4. Run the test suite (`pytest tests/`)
5. Submit a pull request

## ��� License

This project is for demonstration purposes.

## ��� Support

For questions or issues:
1. Check the logs in `pipeline.log`
2. Review the test cases for usage examples
3. Examine the integration tests for end-to-end scenarios

---

**Note**: This pipeline uses the public reqres.in API for demonstration. In production, replace with your actual customer data API endpoints and authentication.
