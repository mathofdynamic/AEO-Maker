# LLM.txt Generator - Professional Website Analysis Tool

A comprehensive web application that generates LLM.txt files for every page of a website to improve AEO (AI Engine Optimization). This professional tool combines advanced web crawling, content extraction, visual analysis, and AI-powered content generation in a beautiful, real-time web interface.

## 🚀 Features

### Core Functionality
- **🌐 Automatic Sitemap Discovery**: Intelligent website crawling with hierarchical sitemap generation
- **📝 Advanced Content Extraction**: Enhanced text scraping optimized for Client-Side Rendered (CSR) websites
- **📸 Visual Analysis**: Full-page screenshot capture with lazy-loading support
- **🤖 AI-Powered Generation**: Creates comprehensive LLM.txt files using advanced AI models
- **💾 Database Storage**: SQLite database for persistent storage of results

### Professional Web Interface
- **🎨 Modern UI/UX**: Beautiful, responsive design with smooth animations
- **⚡ Real-time Updates**: WebSocket-powered live progress tracking and logging
- **📊 Interactive Dashboard**: Professional data visualization and result management
- **🔄 Live Progress Tracking**: Step-by-step progress with visual indicators
- **📋 Comprehensive Logging**: Real-time log display with different severity levels
- **💼 Export Functionality**: Download results as JSON or individual LLM.txt files

### Technical Excellence
- **🛡️ Robust Error Handling**: Comprehensive error management and user feedback
- **🔧 Service Integration**: Seamless integration of multiple specialized APIs
- **📱 Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **♿ Accessibility**: Built with accessibility best practices
- **🧪 Comprehensive Testing**: Complete test suite with detailed result logging

## 🏗️ Architecture

The system consists of four main components:

1. **Sitemap API** (`Sitemap_Service/sitemap_api.py`) - Port 5000
   - Discovers and maps website structure
   - Generates hierarchical sitemap
   - Uses Selenium for JavaScript-rendered content
   - **Testing**: `Sitemap_test_files/test_sitemap.py`

2. **Scraper API** (`Text_Scrapper_Service/scraper_api.py`) - Port 8000
   - Extracts text content from web pages
   - Enhanced for Client-Side Rendered (CSR) websites
   - Handles dynamic content loading and scrolling
   - **Testing**: `Text_scrapper_test_files/test_scraper.py`

3. **Screenshot API** (`Screenshot_Service/screenshot_api.py`) - Port 5002
   - Captures full-page screenshots
   - Waits for dynamic content to load
   - Uses Chrome DevTools Protocol for high-quality captures
   - **Testing**: `Screenshot_test_files/test_screenshot.py`

4. **LLM.txt Generator Web App** (`app.py`) - Port 5001
   - Professional web interface with real-time updates
   - Orchestrates all three APIs seamlessly
   - Generates LLM.txt content using AI models
   - Database storage and export functionality
   - WebSocket-powered real-time communication

## 📋 Prerequisites

- Python 3.8+
- Chrome/Chromium browser
- OpenAI API key
- Internet connection

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd AEO-Maker
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp env_template.txt .env
   # Edit .env and add your OpenAI API key
   ```

4. **Install Chrome/Chromium** (if not already installed):
   - **macOS**: `brew install --cask google-chrome`
   - **Ubuntu/Debian**: `sudo apt install chromium-browser`
   - **Windows**: Download from [Chrome website](https://www.google.com/chrome/)

## 🚀 Quick Start

### **One-Command Startup (Recommended)**

The application now automatically starts all required services! Just run:

**On macOS/Linux:**
```bash
python3 app.py
```

**On Windows:**
```batch
start_app.bat
```

That's it! The application will:
- ✅ Automatically start all required services
- ✅ Check service health
- ✅ Launch the web interface
- ✅ Be ready to use immediately

### **Manual Setup (Alternative)**

If you prefer manual control over services:

**Step 1: Start Required Services**

Start each service in separate terminals:

```bash
# Terminal 1 - Sitemap API
cd Sitemap_Service
python sitemap_api.py

# Terminal 2 - Scraper API  
cd Text_Scrapper_Service
python scraper_api.py

# Terminal 3 - Screenshot API
cd Screenshot_Service
python screenshot_api.py
```

**Step 2: Start Main Application**

```bash
# Terminal 4 - LLM.txt Generator Web App
python app.py
```

### Step 3: Access Web Interface

Open your browser and navigate to: **http://localhost:5001**

### Step 4: Test the Application

Run the comprehensive test suite:

```bash
python test_app.py
```

## 🧪 Testing

Each service includes comprehensive testing capabilities:

### Running Individual Service Tests

```bash
# Test Sitemap API
cd Sitemap_Service/Sitemap_test_files
python test_sitemap.py

# Test Scraper API (enhanced for CSR websites)
cd Text_Scrapper_Service/Text_scrapper_test_files
python test_scraper.py

# Test Screenshot API
cd Screenshot_Service/Screenshot_test_files
python test_screenshot.py
```

### Test Results

- **JSON Results**: All tests save detailed results in `test_results/` folders
- **Screenshots**: Screenshot tests save PNG files in `Screenshot_Service/screenshots/`
- **Standalone Testing**: Tests work without running API servers
- **CSR Support**: Scraper tests are optimized for Client-Side Rendered websites

## 🌐 Usage

### Web Interface (Recommended)

1. **Access the Application**: Navigate to `http://localhost:5001`
2. **Enter Website URL**: Input the website you want to analyze
3. **Start Analysis**: Click "Start Analysis" to begin the process
4. **Monitor Progress**: Watch real-time progress with step-by-step updates
5. **View Logs**: Expand the logs section to see detailed processing information
6. **Review Results**: Browse the generated LLM.txt files in the results table
7. **Export Data**: Download individual files or export all results as JSON

### Key Features of the Web Interface

- **🎨 Professional Design**: Modern, clean interface with smooth animations
- **⚡ Real-time Updates**: Live progress tracking via WebSocket connections
- **📊 Interactive Results**: Sortable, searchable table of generated content
- **📋 Detailed Logging**: Real-time log display with different severity levels
- **💾 Export Options**: Multiple export formats for easy integration
- **📱 Responsive**: Works perfectly on all devices

### API Usage

#### Start LLM.txt Generation Job

```bash
curl -X POST http://localhost:5001/api/start-job \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Response:
```json
{
  "job_id": "uuid-string",
  "status": "started",
  "message": "LLM.txt generation started"
}
```

#### Check Job Status and Results

```bash
curl http://localhost:5001/api/job-status/<job_id>
```

Response:
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "progress": 100,
  "url": "https://example.com",
  "logs": [...],
  "results": [...],
  "start_time": "2025-01-04T10:00:00",
  "end_time": "2025-01-04T10:05:00"
}
```

#### Export Results

```bash
curl http://localhost:5001/api/export-results/<job_id> -o results.json
```

## 📁 Project Structure

```
LLM.txt Generator/
├── README.md                          # Main documentation
├── requirements.txt                   # Python dependencies
├── app.py                            # Main web application
├── test_app.py                       # Comprehensive test suite
├── llm_generator.db                  # SQLite database (created on first run)
├── templates/
│   └── index.html                    # Professional web interface
├── static/
│   ├── css/
│   │   └── styles.css               # Professional styling with animations
│   └── js/
│       └── app.js                   # Frontend application logic
├── Media/                           # Project assets
├── Sitemap_Service/
│   ├── sitemap_api.py              # Sitemap generation API
│   └── Sitemap_test_files/
│       ├── test_sitemap.py         # Standalone sitemap tests
│       ├── README.md               # Sitemap API documentation
│       └── test_results/           # Test result JSON files
├── Text_Scrapper_Service/
│   ├── scraper_api.py              # Text extraction API (CSR optimized)
│   └── Text_scrapper_test_files/
│       ├── test_scraper.py         # Standalone scraper tests
│       ├── README.md               # Scraper API documentation
│       └── test_results/           # Test result JSON files
└── Screenshot_Service/
    ├── screenshot_api.py           # Screenshot capture API
    ├── screenshots/                # Generated screenshots
    │   └── YYYYMMDD/              # Date-organized folders
    └── Screenshot_test_files/
        ├── test_screenshot.py      # Standalone screenshot tests
        ├── README.md               # Screenshot API documentation
        └── test_results/           # Test result JSON files
```

## 📁 Output and Results

### Database Storage

All results are stored in a SQLite database (`llm_generator.db`) with the following structure:

- **Jobs Table**: Stores job information, status, and metadata
- **Results Table**: Stores individual page results with URLs and generated LLM.txt content

### Generated Content Structure

Each LLM.txt file contains:

```
# LLM.txt for https://example.com/page

## Page Information
- URL: https://example.com/page
- Title: Page Title
- Generated: 2025-01-04 10:30:45

## Content Summary
Comprehensive summary of the page content...

## Key Content Elements
- Main navigation items
- Primary content sections
- Call-to-action elements

## Page Structure
- Total text elements: 150
- Primary content focus: Business services
- Content type: Commercial website

## Keywords and Topics
Based on the extracted content, covering topics related to:
business, services, solutions, contact, about

## Technical Details
- Screenshot available: Yes
- Content extraction method: Automated web scraping
- Processing timestamp: 2025-01-04T10:30:45

## AI-Friendly Summary
Optimized content summary for AI systems and search engines...
```

### Export Options

- **Individual Downloads**: Download specific LLM.txt files from the web interface
- **JSON Export**: Complete job results in structured JSON format
- **Database Access**: Direct SQLite database access for advanced users

## ⚙️ Configuration

### ChatGPT Integration Setup

1. **Get OpenAI API Key**:
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create an account and generate an API key
   - Copy the API key

2. **Configure Environment**:
   ```bash
   # Copy the template
   cp env_template.txt .env
   
   # Edit .env file with your API key
   nano .env
   ```

3. **Environment Variables**:
   ```env
   # OpenAI API Configuration
   OPENAI_API_KEY=your-actual-openai-api-key-here
   
   # GPT-5 Nano with Responses API (multimodal: text + image analysis)
   OPENAI_MODEL=gpt-5-nano-2025-08-07
   
   # Response Length
   MAX_TOKENS=2000
   ```

### GPT-5 Nano Features

- **Multimodal Analysis**: Analyzes both text content and visual screenshots
- **Responses API**: Uses the new OpenAI Responses API format
- **Advanced Vision**: Can analyze webpage layouts, design, and visual elements
- **Enhanced SEO**: Provides comprehensive content analysis for better optimization

### Fallback Mode

If no OpenAI API key is configured, the application will use an enhanced template-based LLM.txt generation that still provides comprehensive content analysis.

## 🔧 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**:
   - Ensure Chrome/Chromium is installed
   - Check if Chrome is in your PATH
   - Try updating Chrome to the latest version

2. **Port Conflicts**:
   - Check if ports 5000, 5001, 5002, or 8000 are already in use
   - Modify port numbers in the respective API files if needed

3. **OpenAI API Errors**:
   - Verify your API key is correct
   - Check your OpenAI account balance
   - Ensure you have access to GPT-4 Vision

4. **Memory Issues**:
   - Large websites may require more memory
   - Consider reducing `max_depth` in sitemap generation
   - Process websites in smaller batches

### Debug Mode

Enable debug mode by setting `debug=True` in the Flask apps:

```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📊 Performance

- **Small websites** (< 50 pages): 5-15 minutes
- **Medium websites** (50-200 pages): 15-60 minutes  
- **Large websites** (> 200 pages): 1+ hours

Performance depends on:
- Website complexity and loading times
- OpenAI API response times
- Network speed and stability
- Available system resources

## 🔒 Security Considerations

- Keep your OpenAI API key secure
- Don't commit `.env` files to version control
- Consider rate limiting for production use
- Monitor API usage and costs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in the web interface
3. Open an issue on GitHub
4. Check the service health endpoints

## 🔮 Future Enhancements

- [ ] Support for multiple AI providers
- [ ] Batch processing capabilities
- [ ] Content quality scoring
- [ ] SEO optimization suggestions
- [ ] Integration with CMS platforms
- [ ] Advanced content analysis
- [ ] Multi-language support
