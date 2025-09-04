# AEO Maker

An automated system that generates LLM.txt files for website pages to improve AEO (AI Engine Optimization). This tool integrates three APIs to crawl websites, extract content, and generate AI-optimized content descriptions.

## 🚀 Features

- **Automatic Sitemap Discovery**: Uses `sitemap_api.py` to crawl and discover all pages of a website
- **Content Extraction**: Uses `scraper_api.py` to extract text content from each page (enhanced for CSR websites)
- **Visual Analysis**: Uses `screenshot_api.py` to capture full-page screenshots for visual context
- **AI-Powered Generation**: Integrates with OpenAI GPT-5 Nano (vision) to generate comprehensive LLM.txt files
- **Web Interface**: User-friendly web interface for easy operation
- **REST API**: Full API access for integration with other systems
- **Comprehensive Testing**: Each service includes standalone test scripts with JSON result logging

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

4. **AEO Maker** (`aeo_maker.py`) - Port 5001
   - Orchestrates all three APIs
   - Generates LLM.txt content using OpenAI
   - Provides web interface and REST API

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

### Option 1: Use the startup script (Recommended)

```bash
python start_services.py
```

This will start all four services automatically.

### Option 2: Start services manually

Start each service in separate terminals:

```bash
# Terminal 1 - Sitemap API
python sitemap_api.py

# Terminal 2 - Scraper API  
python scraper_api.py

# Terminal 3 - Screenshot API
python screenshot_api.py

# Terminal 4 - AEO Maker
python aeo_maker.py
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

### Web Interface

1. Open your browser and go to `http://localhost:5001`
2. Enter the website URL you want to process
3. Click "Generate LLM.txt Files"
4. Monitor the progress in real-time
5. Download generated files from the `llm_files/` directory

### API Usage

#### Start LLM.txt Generation

```bash
curl -X POST http://localhost:5001/generate-llm \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

#### Check Job Status

```bash
curl http://localhost:5001/status/<job_id>
```

#### List All Jobs

```bash
curl http://localhost:5001/jobs
```

## 📁 Project Structure

```
AEO-Maker/
├── README.md
├── requirements.txt
├── Media/
├── Sitemap_Service/
│   ├── sitemap_api.py
│   └── Sitemap_test_files/
│       ├── test_sitemap.py
│       ├── README.md
│       └── test_results/
├── Text_Scrapper_Service/
│   ├── scraper_api.py
│   └── Text_scrapper_test_files/
│       ├── test_scraper.py
│       ├── README.md
│       └── test_results/
├── Screenshot_Service/
│   ├── screenshot_api.py
│   ├── screenshots/
│   └── Screenshot_test_files/
│       ├── test_screenshot.py
│       ├── README.md
│       └── test_results/
└── aeo_maker.py
```

## 📁 Output

Generated LLM.txt files are saved in the `llm_files/` directory with the following structure:

```
llm_files/
├── llm_example.com_homepage.txt
├── llm_example.com_about.txt
├── llm_example.com_services.txt
└── ...
```

Each file contains:
- Page URL and generation timestamp
- AI-generated content summary
- Key topics and themes
- Important keywords
- Content structure analysis
- Call-to-action elements

## ⚙️ Configuration

Edit the `.env` file to customize:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# API Service URLs
SITEMAP_API_URL=http://localhost:5000
SCRAPER_API_URL=http://localhost:8000
SCREENSHOT_API_URL=http://localhost:5002

# LLM Generator Configuration
LLM_GENERATOR_PORT=5001
MAX_CONCURRENT_PAGES=5
OPENAI_MODEL=gpt-5-nano-2025-08-07
```

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
