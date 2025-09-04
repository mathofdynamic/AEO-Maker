# Screenshot API Documentation

## Overview

The Screenshot API is a powerful Flask-based service that captures full-page screenshots of websites using Selenium WebDriver and Chrome DevTools Protocol. It's specifically designed to handle Client-Side Rendered (CSR) websites by waiting for complete page loads and triggering lazy-loaded content through progressive scrolling.

## Features

- 📸 **Full-Page Screenshots**: Captures entire webpage content, not just viewport
- 🌐 **CSR Support**: Handles JavaScript-heavy websites with proper waiting and scrolling
- 🚀 **Chrome DevTools Protocol**: Uses CDP for high-quality, full-page captures
- 📁 **Organized Storage**: Saves screenshots in dated directories for easy management
- ⏱️ **Smart Waiting**: Waits for DOM ready state and triggers lazy content
- 🔄 **Progressive Scrolling**: Scrolls through page to load all dynamic content
- 📐 **Flexible Dimensions**: Automatically adjusts to page size

## How It Works

### 1. Request Processing

The API follows a simple request-response pattern:

1. **URL Validation**: Validates and normalizes the input URL
2. **Page Loading**: Loads the page with headless Chrome
3. **DOM Ready Wait**: Waits for `document.readyState === 'complete'`
4. **Progressive Scroll**: Scrolls through page to trigger lazy content
5. **Screenshot Capture**: Captures full-page screenshot via Chrome DevTools
6. **File Storage**: Saves screenshot with timestamped filename

### 2. Screenshot Process

The core screenshot logic:

1. **Chrome Setup**: Initializes headless Chrome with optimized options
2. **Page Navigation**: Loads the target URL with timeout handling
3. **DOM Ready Check**: Waits for complete page load state
4. **Progressive Scrolling**: Scrolls in steps to trigger lazy-loaded content
5. **Dimension Calculation**: Determines full page width and height
6. **CDP Capture**: Uses Chrome DevTools Protocol for full-page screenshot
7. **File Saving**: Saves PNG file with organized naming

### 3. CSR Handling

- **DOM Ready Wait**: Ensures JavaScript has finished executing
- **Progressive Scroll**: Triggers lazy-loaded content by scrolling
- **Height Detection**: Monitors page height changes during scrolling
- **Content Loading**: Ensures all dynamic content is loaded before capture

## API Endpoints

### 1. Health Check
**GET** `/health`

Simple health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "screenshot_api"
}
```

### 2. Take Screenshot
**POST** `/screenshot`

Captures a full-page screenshot of the specified URL.

**Request Body:**
```json
{
  "url": "https://example.com"
}
```

**Response (Success):**
```json
{
  "success": true,
  "url": "https://example.com",
  "file_path": "screenshots/20250104/example.com_20250104_123456.png",
  "width": 1366,
  "height": 2048
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Timed out waiting for page to load."
}
```

## Usage Examples

### Basic Usage

```python
import requests

# Take a screenshot
response = requests.post('http://localhost:5002/screenshot', 
                        json={'url': 'https://example.com'})

if response.status_code == 200:
    data = response.json()
    if data['success']:
        print(f"Screenshot saved to: {data['file_path']}")
        print(f"Dimensions: {data['width']}x{data['height']}")
    else:
        print(f"Error: {data['error']}")
```

### Using the Test Script

The included `test_screenshot.py` script provides a complete testing framework:

```bash
# Start the API server first
cd Screenshot_Service
python screenshot_api.py

# In another terminal, run the test
cd Screenshot_test_files
python test_screenshot.py
```

The script will:
1. Check if the API server is running
2. Test multiple URLs
3. Capture screenshots
4. Save results to JSON files
5. Provide detailed analysis

## Configuration

### Chrome Options
- **Headless Mode**: Chrome runs without GUI
- **Window Size**: Default 1366x900 viewport
- **GPU Disabled**: Optimized for server environments
- **Logging Disabled**: Clean output without Chrome logs

### Scrolling Settings
- **Scroll Step**: 1200 pixels per scroll step
- **Scroll Pause**: 0.6 seconds between scrolls
- **Max Attempts**: 30 scroll attempts maximum
- **Height Detection**: Monitors page height changes

### Timeouts
- **Page Load**: 30 seconds maximum wait time
- **API Request**: 60 seconds for screenshot operations
- **DOM Ready**: Waits for complete document state

## Output Format

### Screenshot Files
- **Format**: PNG images
- **Naming**: `{domain}_{timestamp}.png`
- **Organization**: Stored in `screenshots/YYYYMMDD/` directories
- **Dimensions**: Full page width and height

### JSON Response Structure
```json
{
  "success": true,
  "url": "https://example.com",
  "file_path": "screenshots/20250104/example.com_20250104_123456.png",
  "width": 1366,
  "height": 2048
}
```

## Performance Considerations

### Screenshot Speed
- **Typical Speed**: 10-30 seconds per screenshot
- **CSR Heavy Sites**: May take longer due to scrolling and waiting
- **Large Pages**: More content = longer processing time

### Resource Usage
- **Memory**: Chrome WebDriver uses significant memory
- **CPU**: Browser rendering and screenshot capture
- **Storage**: PNG files can be large (1-10MB per screenshot)

### Scalability
- **Single Threaded**: Flask handles one request at a time
- **Memory Management**: Chrome instances are cleaned up after each request
- **File Storage**: Screenshots accumulate over time

## Error Handling

### Common Issues
1. **Chrome Driver Not Found**: Install Chrome and ChromeDriver
2. **Page Load Timeouts**: Some sites may be slow to load
3. **Memory Issues**: Large pages may cause memory problems
4. **File System Errors**: Check write permissions for screenshots directory

### Error Responses
```json
{
  "success": false,
  "error": "Detailed error message"
}
```

## Installation and Setup

### Prerequisites
- Python 3.7+
- Chrome browser
- ChromeDriver (auto-managed by Selenium)
- Required Python packages

### Installation
```bash
# Install dependencies
pip install flask selenium requests

# Start the API server
python screenshot_api.py
```

### Dependencies
- **Flask**: Web framework for API endpoints
- **Selenium**: Web automation and Chrome control
- **Requests**: HTTP client for testing

## File Organization

### Screenshot Storage
```
Screenshot_Service/
├── screenshot_api.py
├── screenshots/
│   └── 20250104/
│       ├── example.com_20250104_123456.png
│       └── droplinked.com_20250104_123500.png
└── Screenshot_test_files/
    ├── test_screenshot.py
    ├── README.md
    └── test_results/
        ├── screenshot_combined_results_20250104_123456.json
        ├── screenshot_test_1_20250104_123456.json
        └── screenshot_test_2_20250104_123500.json
```

## Advanced Features

### CSR Optimization
- **DOM Ready Detection**: Waits for complete JavaScript execution
- **Progressive Scrolling**: Triggers lazy-loaded content
- **Height Monitoring**: Detects when no more content loads
- **Return to Top**: Ensures screenshot starts from page top

### Chrome DevTools Protocol
- **Full-Page Capture**: Captures entire page, not just viewport
- **Surface Rendering**: Avoids viewport-only screenshots
- **Dimension Override**: Emulates full page size for capture
- **High Quality**: PNG format with full resolution

### File Management
- **Timestamped Names**: Prevents filename conflicts
- **Dated Directories**: Organizes screenshots by date
- **Safe Filenames**: Converts URLs to filesystem-safe names
- **Path Tracking**: Returns full file paths in responses

## Troubleshooting

### API Server Won't Start
1. Check if port 5002 is available
2. Ensure all dependencies are installed
3. Check Chrome and ChromeDriver installation

### Screenshot Issues
1. Verify the target website is accessible
2. Check for anti-bot measures
3. Ensure the website allows screenshots
4. Try increasing timeout values

### Memory Issues
1. Restart the API server periodically
2. Monitor system resources
3. Avoid capturing very large pages simultaneously

## Best Practices

1. **Respect Websites**: Check robots.txt and terms of service
2. **Rate Limiting**: Don't overwhelm target servers
3. **Error Handling**: Always check success status in responses
4. **Resource Management**: Monitor system resources
5. **Testing**: Test with simple sites before complex ones

## API Documentation

The API includes basic documentation:
- **Health Check**: Available at `http://localhost:5002/health`
- **Screenshot Endpoint**: Available at `http://localhost:5002/screenshot`

## License

This project is part of the AEO-Maker suite and follows the same licensing terms.

## Support

For issues and questions:
1. Check the API health endpoint
2. Verify the target website is accessible
3. Test with simpler websites first
4. Check the troubleshooting section above
5. Monitor system resources during screenshot capture
