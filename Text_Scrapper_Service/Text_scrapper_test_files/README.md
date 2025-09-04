# Scraper API Documentation

## Overview

The Scraper API is a powerful asynchronous web scraping service that extracts text content from client-side rendered websites. It uses FastAPI and Selenium WebDriver to handle JavaScript-heavy websites and provides a non-blocking API for text extraction.

## Features

- 🌐 **Client-Side Rendering Support**: Handles JavaScript-heavy websites using Selenium
- 🚀 **Asynchronous Processing**: Non-blocking API with background job processing
- 📝 **Text Extraction**: Extracts all text content from web pages
- 🔄 **Job Monitoring**: Track scraping progress with unique job IDs
- 🛡️ **Error Handling**: Comprehensive error handling and status reporting
- 📊 **FastAPI Integration**: Modern API with automatic documentation

## How It Works

### 1. Request Processing

The API follows an asynchronous pattern:

1. **Job Creation**: Client submits a URL, receives a job ID immediately
2. **Background Processing**: Scraping runs in the background
3. **Status Monitoring**: Client polls for job status using the job ID
4. **Result Retrieval**: Once completed, results are available via the job ID

### 2. Scraping Process

The core scraping logic:

1. **Browser Setup**: Initializes Chrome WebDriver in headless mode
2. **Page Loading**: Navigates to the target URL
3. **Rendering Wait**: Waits for JavaScript content to render (5 seconds)
4. **Text Extraction**: Uses BeautifulSoup to extract all text content
5. **Cleanup**: Closes browser and returns results

### 3. Text Processing

- Uses `soup.stripped_strings` to get clean text snippets
- Removes extra whitespace and formatting
- Returns a list of text items
- Handles both static and dynamic content

## API Endpoints

### 1. Start Scraping Job
**POST** `/scrape`

Starts a new scraping job.

**Request Body:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "pending",
  "result": null
}
```

### 2. Get Job Status
**GET** `/jobs/{job_id}`

Retrieves the status and results of a scraping job.

**Response (Pending):**
```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "in_progress",
  "result": null
}
```

**Response (Completed):**
```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "completed",
  "result": {
    "url": "https://example.com",
    "text_content": ["Example", "Website", "Content", "..."]
  }
}
```

**Response (Failed):**
```json
{
  "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "failed",
  "result": {
    "error": "Connection timeout"
  }
}
```

### 3. API Documentation
**GET** `/docs`

Interactive API documentation (Swagger UI).

## Usage Examples

### Basic Usage

```python
import requests
import time

# Start scraping job
response = requests.post('http://localhost:8000/scrape', 
                        json={'url': 'https://example.com'})
job_data = response.json()
job_id = job_data['job_id']

# Monitor progress
while True:
    status_response = requests.get(f'http://localhost:8000/jobs/{job_id}')
    status_data = status_response.json()
    
    if status_data['status'] == 'completed':
        text_content = status_data['result']['text_content']
        print(f"Scraped {len(text_content)} text items")
        break
    elif status_data['status'] == 'failed':
        print(f"Error: {status_data['result']['error']}")
        break
    
    time.sleep(2)
```

### Using the Test Script

The included `test_scraper.py` script provides a complete testing framework:

```bash
# Start the API server first
cd Text_Scrapper_Service
python scraper_api.py

# In another terminal, run the test
cd Text_scrapper_test_files
python test_scraper.py
```

The script will:
1. Check if the API server is running
2. Test multiple URLs
3. Monitor job progress
4. Save results to JSON files
5. Provide detailed analysis

## Configuration

### Browser Settings
- **Headless Mode**: Chrome runs without GUI
- **User Agent**: Modern browser user agent string
- **Wait Time**: 5 seconds for JavaScript rendering
- **Chrome Options**: Optimized for scraping

### Timeouts
- **Page Load**: 5 seconds wait for rendering
- **Job Monitoring**: 2 minutes maximum wait time
- **API Requests**: 5-10 seconds timeout

## Output Format

### Text Content Structure
```json
{
  "url": "https://example.com",
  "text_content": [
    "Example Website",
    "Navigation",
    "Home",
    "About",
    "Contact",
    "Main Content",
    "Footer"
  ]
}
```

### Job Status Values
- **pending**: Job created, not yet started
- **in_progress**: Scraping is currently running
- **completed**: Scraping finished successfully
- **failed**: Scraping encountered an error

## Performance Considerations

### Scraping Speed
- **Typical Speed**: 5-10 seconds per page
- **JavaScript Heavy Sites**: May take longer due to rendering wait
- **Large Pages**: More text content = longer processing

### Resource Usage
- **Memory**: Chrome WebDriver uses significant memory
- **CPU**: Browser rendering is CPU intensive
- **Network**: Depends on page size and complexity

### Scalability
- **Concurrent Jobs**: Limited by system resources
- **Queue Management**: Jobs run in background tasks
- **Memory Management**: Browser instances are cleaned up after each job

## Error Handling

### Common Issues
1. **Chrome Driver Not Found**: Install Chrome and ChromeDriver
2. **Network Timeouts**: Check internet connection
3. **Page Load Failures**: Some sites may block scraping
4. **Memory Issues**: Large pages may cause memory problems

### Error Responses
```json
{
  "status": "failed",
  "result": {
    "error": "Detailed error message"
  }
}
```

## Installation and Setup

### Prerequisites
- Python 3.7+
- Chrome browser
- ChromeDriver (auto-installed by webdriver-manager)
- Required Python packages (see requirements.txt)

### Installation
```bash
# Install dependencies
pip install fastapi uvicorn selenium beautifulsoup4 webdriver-manager requests

# Start the API server
python scraper_api.py
```

### Dependencies
- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **Selenium**: Web automation
- **BeautifulSoup**: HTML parsing
- **webdriver-manager**: Chrome driver management

## Troubleshooting

### API Server Won't Start
1. Check if port 8000 is available
2. Ensure all dependencies are installed
3. Check Chrome and ChromeDriver installation

### Scraping Issues
1. Verify the target website is accessible
2. Check for anti-bot measures
3. Ensure the website allows scraping
4. Try increasing wait time for slow sites

### Memory Issues
1. Restart the API server periodically
2. Monitor system resources
3. Avoid scraping very large pages simultaneously

## Best Practices

1. **Respect Websites**: Check robots.txt and terms of service
2. **Rate Limiting**: Don't overwhelm target servers
3. **Error Handling**: Always check job status and handle errors
4. **Resource Management**: Monitor system resources
5. **Testing**: Test with simple sites before complex ones

## API Documentation

The API includes automatic documentation:
- **Swagger UI**: Available at `http://localhost:8000/docs`
- **ReDoc**: Available at `http://localhost:8000/redoc`
- **OpenAPI Schema**: Available at `http://localhost:8000/openapi.json`

## License

This project is part of the AEO-Maker suite and follows the same licensing terms.

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Verify the target website is accessible
3. Test with simpler websites first
4. Check the troubleshooting section above
5. Monitor system resources during scraping
