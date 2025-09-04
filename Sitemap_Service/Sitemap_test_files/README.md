# Sitemap API Documentation

## Overview

The Sitemap API is a powerful web crawling service that generates hierarchical sitemaps for websites. It uses Selenium WebDriver to crawl websites and discover all linked pages, then organizes them into a tree-like JSON structure showing parent-child relationships.

## Features

- 🌐 **Deep Web Crawling**: Recursively crawls websites to discover all linked pages
- 🌳 **Hierarchical Structure**: Organizes URLs into a tree structure showing relationships
- 📊 **Comprehensive Discovery**: Finds pages through multiple methods (links, sitemaps, robots.txt)
- 🚀 **Asynchronous Processing**: Non-blocking API with job monitoring
- 📝 **Detailed Logging**: Complete logs of the crawling process
- 🎯 **Smart Blog Detection**: Special handling for blog sections with deeper crawling

## How It Works

### 1. Crawling Process

The sitemap generator uses a multi-step approach to discover all website URLs:

#### Step 1: Sitemap Discovery
- Checks for `sitemap.xml` files
- Parses `robots.txt` for sitemap references
- Extracts URLs from discovered sitemaps

#### Step 2: Recursive Crawling
- Starts from the base URL
- Uses Selenium WebDriver to load pages
- Extracts all links from each page
- Recursively follows links to discover new pages
- Special handling for blog sections (scrolls to load more content)

#### Step 3: Relationship Building
- Analyzes URL paths to determine parent-child relationships
- Builds hierarchical tree structure
- Groups related pages under their parent sections

### 2. URL Classification

The system classifies URLs into different categories:

- **Root Pages**: Main sections (e.g., `/about`, `/contact`)
- **Child Pages**: Direct children of root pages
- **Blog Posts**: Special handling for `/blogs/` sections
- **Deep Nested Pages**: Pages with multiple path segments

### 3. Hierarchy Building

The final sitemap is organized as a tree structure:

```json
{
  "domain.com": {
    "domain.com/page1": [],
    "domain.com/page2": {
      "domain.com/page2/subpage1": [],
      "domain.com/page2/subpage2": []
    },
    "domain.com/blogs": {
      "domain.com/blogs/post1": [],
      "domain.com/blogs/post2": []
    }
  }
}
```

## API Endpoints

### 1. Generate Sitemap
**POST** `/generate-sitemap`

Starts a new sitemap generation job.

**Request Body:**
```json
{
  "url": "https://example.com",
  "max_depth": 5
}
```

**Response:**
```json
{
  "job_id": "uuid-string",
  "status_url": "/status/uuid-string",
  "message": "Sitemap generation started"
}
```

### 2. Get Job Status
**GET** `/status/{job_id}`

Retrieves the current status and results of a sitemap generation job.

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "url": "https://example.com",
  "discovered_urls_count": 25,
  "total_links_found": 30,
  "url_relationships": 20,
  "sitemap": { ... },
  "logs": [ ... ],
  "start_time": "2025-01-04T10:00:00",
  "end_time": "2025-01-04T10:02:00",
  "duration_seconds": 120.5
}
```

### 3. List Jobs
**GET** `/jobs`

Lists all sitemap generation jobs.

### 4. Health Check
**GET** `/health`

Checks if the API server is running.

## Usage Examples

### Basic Usage

```python
import requests

# Start sitemap generation
response = requests.post('http://localhost:5000/generate-sitemap', 
                        json={'url': 'https://example.com', 'max_depth': 3})
job_data = response.json()
job_id = job_data['job_id']

# Monitor progress
while True:
    status_response = requests.get(f'http://localhost:5000/status/{job_id}')
    status_data = status_response.json()
    
    if status_data['status'] == 'completed':
        sitemap = status_data['sitemap']
        break
    elif status_data['status'] == 'error':
        print(f"Error: {status_data['error']}")
        break
    
    time.sleep(2)
```

### Using the Test Script

The included `test_sitemap_api.py` script provides a complete testing framework:

```bash
# Run the test script
python test_sitemap_api.py
```

The script will:
1. Check if the API server is running
2. Generate sitemaps for multiple test URLs
3. Save results to JSON files
4. Provide detailed analysis of the results

## Configuration

### Max Depth
Controls how deep the crawler goes into the website structure:
- `1`: Only direct children of the root page
- `3`: Up to 3 levels deep (recommended)
- `5`: Very deep crawling (may take longer)

### Special Handling

#### Blog Sections
The crawler has special handling for blog sections:
- Automatically scrolls to load more content
- Allows deeper nesting for blog posts
- Discovers individual blog post URLs

#### Sitemap Discovery
- Automatically checks for `sitemap.xml`
- Parses `robots.txt` for sitemap references
- Uses discovered URLs to enhance crawling

## Output Format

### Sitemap Structure
```json
{
  "domain.com": {
    "domain.com/page1": [],
    "domain.com/page2": {
      "domain.com/page2/subpage1": [],
      "domain.com/page2/subpage2": []
    }
  }
}
```

### Empty Arrays vs Objects
- **Empty Array `[]`**: Page has no children or descendants
- **Object `{}`**: Page has children (shows the hierarchical structure)

## Performance Considerations

### Crawling Speed
- Typical speed: 1-2 pages per second
- Blog sections may take longer due to scrolling
- Large websites may take several minutes

### Resource Usage
- Uses Chrome WebDriver (headless mode)
- Memory usage scales with website size
- CPU usage during active crawling

### Timeouts
- Page load timeout: 10 seconds
- Total job timeout: None (runs until completion)
- Connection timeout: 5 seconds

## Error Handling

### Common Issues
1. **Chrome Driver Not Found**: Install Chrome and ChromeDriver
2. **Network Timeouts**: Check internet connection
3. **Memory Issues**: Reduce max_depth for large websites
4. **Rate Limiting**: Some websites may block rapid requests

### Error Responses
```json
{
  "error": "Error message describing what went wrong",
  "status": "error"
}
```

## Installation and Setup

### Prerequisites
- Python 3.7+
- Chrome browser
- ChromeDriver
- Required Python packages (see requirements.txt)

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
python sitemap_api.py
```

### Dependencies
- Flask: Web framework
- Selenium: Web automation
- requests: HTTP client
- urllib: URL parsing

## Troubleshooting

### API Server Won't Start
1. Check if port 5000 is available
2. Ensure all dependencies are installed
3. Check Chrome and ChromeDriver installation

### Crawling Issues
1. Verify the target website is accessible
2. Check for JavaScript-heavy sites (may need longer timeouts)
3. Ensure the website allows crawling (check robots.txt)

### Memory Issues
1. Reduce max_depth parameter
2. Restart the API server periodically
3. Monitor system resources

## Best Practices

1. **Start Small**: Test with simple websites first
2. **Monitor Progress**: Use the status endpoint to track progress
3. **Handle Errors**: Always check for error responses
4. **Resource Management**: Don't run too many jobs simultaneously
5. **Respect Websites**: Be mindful of crawling frequency and server load

## License

This project is part of the AEO-Maker suite and follows the same licensing terms.

## Support

For issues and questions:
1. Check the logs in the API response
2. Verify the target website is accessible
3. Test with simpler websites first
4. Check the troubleshooting section above
