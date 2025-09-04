import json
import os
import urllib.parse
import threading
import time
import uuid
from datetime import datetime
from typing import Set, Dict, List, Tuple
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

app = Flask(__name__)

# Global storage for crawl jobs
crawl_jobs = {}


class SitemapGenerator:
    def __init__(self, base_url: str, max_depth: int = 5, job_id: str = None):
        self.base_url = base_url
        self.max_depth = max_depth
        self.job_id = job_id or str(uuid.uuid4())
        self.visited_urls: Set[str] = set()
        self.all_found_urls: Set[str] = set()
        self.url_children: Dict[str, Set[str]] = {}  # Track parent-child relationships
        self.driver = None
        self.status = "initializing"
        self.logs = []
        self.sitemap_data = None
        self.error = None
        self.start_time = None
        self.end_time = None
        
    def log(self, message: str):
        """Add a log entry with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)  # Also print to console
        
    def update_status(self, status: str):
        """Update the current status"""
        self.status = status
        self.log(f"Status: {status}")
        
    def setup_driver(self):
        """Set up the Chrome driver with appropriate options for headless browsing"""
        self.log("Setting up Chrome driver...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.log("Chrome driver setup successful")
        except Exception as e:
            error_msg = f"Error setting up Chrome driver: {e}"
            self.log(error_msg)
            self.error = error_msg
            raise
            
    def get_page_links(self, url: str) -> Set[str]:
        """Extract all links from a page using Selenium"""
        if self.driver is None:
            self.setup_driver()

        try:
            self.log(f"Loading page: {url}")
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            self.driver.implicitly_wait(3)

            urls = set()
            
            # Get all links from the page
            try:
                all_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")
                self.log(f"Found {len(all_links)} links on page")
                
                for link in all_links:
                    href = link.get_attribute("href")
                    if href:
                        absolute_url = urllib.parse.urljoin(url, href)
                        if self.is_same_domain(absolute_url):
                            parsed_url = urllib.parse.urlparse(absolute_url)
                            clean_url = urllib.parse.urlunparse((
                                parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                                parsed_url.params, parsed_url.query, ''
                            ))

                            if (clean_url.startswith("http") and
                                clean_url != url and
                                not clean_url.endswith(('.jpg', '.png', '.gif', '.css', '.js', '.pdf', '.zip')) and
                                '#' not in clean_url):
                                urls.add(clean_url)
                
                # For blogs page, also try to find blog posts by scrolling and loading more content
                if 'blogs' in url:
                    self.log("Detected blogs page, attempting to load more content...")
                    try:
                        # Scroll down to load more content
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(2)
                        
                        # Look for more links after scrolling
                        more_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")
                        for link in more_links:
                            href = link.get_attribute("href")
                            if href:
                                absolute_url = urllib.parse.urljoin(url, href)
                                if self.is_same_domain(absolute_url):
                                    parsed_url = urllib.parse.urlparse(absolute_url)
                                    clean_url = urllib.parse.urlunparse((
                                        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                                        parsed_url.params, parsed_url.query, ''
                                    ))
                                    if (clean_url.startswith("http") and
                                        clean_url != url and
                                        not clean_url.endswith(('.jpg', '.png', '.gif', '.css', '.js', '.pdf', '.zip')) and
                                        '#' not in clean_url):
                                        urls.add(clean_url)
                        
                        self.log(f"After scrolling, found {len(urls)} total URLs")
                    except Exception as e:
                        self.log(f"Error during blog page scrolling: {e}")
                
                self.log(f"Extracted {len(urls)} valid same-domain URLs")
            except Exception as e:
                self.log(f"Error extracting links: {e}")

            return urls
        except TimeoutException:
            self.log(f"Timeout getting links from {url}")
            return set()
        except Exception as e:
            self.log(f"Error getting links from {url}: {str(e)[:50]}...")
            return set()
            
    def is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain as base_url"""
        try:
            base_domain = urllib.parse.urlparse(self.base_url).netloc
            url_domain = urllib.parse.urlparse(url).netloc
            return base_domain == url_domain
        except:
            return False

    def get_url_depth(self, url: str) -> int:
        """Get the depth of a URL based on its path segments"""
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.strip('/')
        if not path:
            return 0
        return len(path.split('/'))

    def is_child_of(self, parent_url: str, child_url: str) -> bool:
        """Check if child_url is a child of parent_url (allows deeper nesting)"""
        parent_parsed = urllib.parse.urlparse(parent_url)
        child_parsed = urllib.parse.urlparse(child_url)
        
        # Must be same domain
        if parent_parsed.netloc != child_parsed.netloc:
            return False
            
        parent_path = parent_parsed.path.rstrip('/')
        child_path = child_parsed.path.rstrip('/')
        
        # Root page case
        if parent_path == '':
            return child_path != '' and child_path.startswith('/')
        
        # Child path should start with parent path
        if not child_path.startswith(parent_path + '/'):
            return False
            
        # For blogs and similar sections, allow deeper nesting
        if 'blogs' in parent_path or 'blog' in parent_path:
            # Allow any depth for blog sections
            return True
        
        # For other sections, limit to one level deeper
        remaining_path = child_path[len(parent_path + '/'):]
        return '/' not in remaining_path

    def crawl_recursive(self, url: str, depth: int = 0) -> None:
        """Recursively crawl pages to build a complete hierarchy"""
        if depth > self.max_depth or url in self.visited_urls:
            return
            
        self.log(f"Crawling: {url} (depth: {depth})")
        self.visited_urls.add(url)
        
        # Get all links from current page
        links = self.get_page_links(url)
        self.all_found_urls.update(links)
        
        # Track children of current URL
        children = set()
        for link in links:
            if self.is_child_of(url, link):
                children.add(link)
        
        self.url_children[url] = children
        
        # For blogs page, crawl deeper to find blog posts
        if 'blogs' in url and depth < 3:  # Allow deeper crawling for blogs
            for link in links:
                if (self.is_same_domain(link) and 
                    '/blogs/' in link and 
                    link not in self.visited_urls):
                    self.crawl_recursive(link, depth + 1)
        
        # Recursively crawl children
        for child_url in children:
            if child_url not in self.visited_urls:
                self.crawl_recursive(child_url, depth + 1)

    def discover_sitemap_urls(self) -> Set[str]:
        """Discover URLs from sitemap.xml and robots.txt"""
        discovered_urls = set()
        
        try:
            # Try to find sitemap.xml
            sitemap_url = urllib.parse.urljoin(self.base_url, '/sitemap.xml')
            self.log(f"Checking for sitemap at: {sitemap_url}")
            
            try:
                self.driver.get(sitemap_url)
                time.sleep(2)
                
                # Look for URLs in sitemap
                sitemap_links = self.driver.find_elements(By.CSS_SELECTOR, "loc")
                for link in sitemap_links:
                    url_text = link.text.strip()
                    if url_text and self.is_same_domain(url_text):
                        discovered_urls.add(url_text)
                
                self.log(f"Found {len(discovered_urls)} URLs in sitemap.xml")
            except Exception as e:
                self.log(f"Sitemap.xml not found or error: {e}")
            
            # Try to find robots.txt
            robots_url = urllib.parse.urljoin(self.base_url, '/robots.txt')
            self.log(f"Checking for robots.txt at: {robots_url}")
            
            try:
                self.driver.get(robots_url)
                time.sleep(2)
                
                # Parse robots.txt for sitemap entries
                page_source = self.driver.page_source
                for line in page_source.split('\n'):
                    if line.strip().lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        if self.is_same_domain(sitemap_url):
                            discovered_urls.add(sitemap_url)
                
                self.log(f"Found sitemap references in robots.txt")
            except Exception as e:
                self.log(f"Robots.txt not found or error: {e}")
                
        except Exception as e:
            self.log(f"Error discovering sitemap URLs: {e}")
        
        return discovered_urls

    def crawl_site(self) -> None:
        """Main crawling method that discovers all URLs and their relationships"""
        self.update_status("starting_crawl")
        
        if self.driver is None:
            self.setup_driver()
            
        # Start with the base URL
        parsed = urllib.parse.urlparse(self.base_url)
        root_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, '', '', '', ''))
        
        self.log(f"Starting recursive crawl from: {root_url}")
        
        # Discover URLs from sitemaps first
        sitemap_urls = self.discover_sitemap_urls()
        self.all_found_urls.update(sitemap_urls)
        
        # Recursively crawl the site
        self.crawl_recursive(root_url, 0)
        
        # Also crawl the base URL if it's different from root
        if self.base_url != root_url:
            self.crawl_recursive(self.base_url, 0)
        
        self.log(f"Crawl complete. Discovered {len(self.visited_urls)} unique URLs")

    def build_hierarchical_sitemap(self) -> Dict:
        """Build hierarchical sitemap from discovered URLs and their relationships"""
        self.update_status("building_hierarchy")
        
        base_domain = urllib.parse.urlparse(self.base_url).netloc
        
        def build_tree_for_url(url: str) -> Dict:
            """Recursively build tree structure for a given URL"""
            tree = {}
            
            if url in self.url_children:
                children = sorted(list(self.url_children[url]))
                for child_url in children:
                    # Create key for child (domain + path)
                    parsed = urllib.parse.urlparse(child_url)
                    child_key = f"{parsed.netloc}{parsed.path}"
                    
                    # Check if child has its own children
                    if child_url in self.url_children and self.url_children[child_url]:
                        # Child has children, build subtree
                        tree[child_key] = build_tree_for_url(child_url)
                    else:
                        # Child is a leaf, find all its descendants
                        descendants = []
                        child_path = urllib.parse.urlparse(child_url).path
                        
                        # For blogs, include all discovered blog URLs
                        if 'blogs' in child_path:
                            for discovered_url in self.all_found_urls:
                                discovered_path = urllib.parse.urlparse(discovered_url).path
                                if (discovered_path.startswith(child_path + '/') and 
                                    discovered_url != child_url and
                                    '/blogs/' in discovered_path):
                                    parsed_desc = urllib.parse.urlparse(discovered_url)
                                    desc_key = f"{parsed_desc.netloc}{parsed_desc.path}"
                                    descendants.append(desc_key)
                        else:
                            # For other sections, only include direct descendants
                            for discovered_url in self.visited_urls:
                                discovered_path = urllib.parse.urlparse(discovered_url).path
                                if (discovered_path.startswith(child_path + '/') and 
                                    discovered_url != child_url):
                                    parsed_desc = urllib.parse.urlparse(discovered_url)
                                    desc_key = f"{parsed_desc.netloc}{parsed_desc.path}"
                                    descendants.append(desc_key)
                        
                        tree[child_key] = sorted(list(set(descendants)))
            
            return tree
        
        # Build the complete hierarchy
        self.log("Building hierarchical tree structure...")
        
        # Start with root domain
        root_url = urllib.parse.urlunparse((
            urllib.parse.urlparse(self.base_url).scheme,
            base_domain, '', '', '', ''
        ))
        
        hierarchy = {base_domain: build_tree_for_url(root_url)}
        
        self.log("Hierarchy building complete")
        return hierarchy

    def generate_sitemap(self) -> Dict:
        """Generate and return the sitemap in JSON format"""
        try:
            self.start_time = datetime.now()
            self.log(f"Starting sitemap generation for: {self.base_url}")
            
            self.crawl_site()
            hierarchical_sitemap = self.build_hierarchical_sitemap()
            
            self.update_status("completed")
            self.sitemap_data = hierarchical_sitemap
            self.end_time = datetime.now()
            
            duration = (self.end_time - self.start_time).total_seconds()
            self.log(f"Sitemap generation completed in {duration:.2f} seconds")
            
            return hierarchical_sitemap
            
        except Exception as e:
            error_msg = f"Error during sitemap generation: {str(e)}"
            self.log(error_msg)
            self.error = error_msg
            self.update_status("error")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                self.log("Chrome driver closed")


# API Routes

@app.route('/generate-sitemap', methods=['POST'])
def generate_sitemap():
    """Start a new sitemap generation job"""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        max_depth = data.get('max_depth', 5) # Changed default to 5
        
        # Validate URL
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.netloc:
                return jsonify({'error': 'Invalid URL format'}), 400
        except:
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Create new job
        job_id = str(uuid.uuid4())
        generator = SitemapGenerator(url, max_depth, job_id)
        crawl_jobs[job_id] = generator
        
        # Start crawling in background thread
        def crawl_worker():
            try:
                generator.generate_sitemap()
            except Exception as e:
                generator.log(f"Crawl failed: {str(e)}")
        
        thread = threading.Thread(target=crawl_worker)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status_url': f'/status/{job_id}',
            'message': 'Sitemap generation started'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get the status of a sitemap generation job"""
    if job_id not in crawl_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    generator = crawl_jobs[job_id]
    
    response = {
        'job_id': job_id,
        'status': generator.status,
        'url': generator.base_url,
        'logs': generator.logs,
        'discovered_urls_count': len(generator.visited_urls),
        'total_links_found': len(generator.all_found_urls),
        'url_relationships': len(generator.url_children)
    }
    
    if generator.start_time:
        response['start_time'] = generator.start_time.isoformat()
    
    if generator.end_time:
        response['end_time'] = generator.end_time.isoformat()
        response['duration_seconds'] = (generator.end_time - generator.start_time).total_seconds()
    
    if generator.error:
        response['error'] = generator.error
    
    if generator.sitemap_data:
        response['sitemap'] = generator.sitemap_data
    
    return jsonify(response)


@app.route('/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    jobs = []
    for job_id, generator in crawl_jobs.items():
        jobs.append({
            'job_id': job_id,
            'url': generator.base_url,
            'status': generator.status,
            'start_time': generator.start_time.isoformat() if generator.start_time else None
        })
    
    return jsonify({'jobs': jobs})


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


if __name__ == "__main__":
    print("Starting Sitemap Generator API...")
    print("Available endpoints:")
    print("  POST /generate-sitemap - Start new sitemap generation")
    print("  GET  /status/<job_id> - Get job status and live logs")
    print("  GET  /jobs - List all jobs")
    print("  GET  /health - Health check")
    
    app.run(debug=True, host='0.0.0.0', port=5000)