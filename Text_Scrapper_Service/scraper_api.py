import time
import uuid
import os
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Asynchronous Web Scraper API",
    description="An API to scrape text from client-side rendered websites. "
                "Submit a URL to start a job and use the job ID to check the status and retrieve the results.",
    version="1.0.0",
)

# --- In-Memory Job Storage ---
# A simple dictionary to act as a database for job statuses and results.
# For a production environment, you would replace this with a proper database like Redis, PostgreSQL, or MongoDB.
jobs: Dict[str, Dict[str, Any]] = {}

# --- Pydantic Models for API Data Validation ---
class ScrapeRequest(BaseModel):
    url: str = Field(..., example="https://droplinked.com", description="The URL of the website to scrape.")

class Job(BaseModel):
    job_id: str = Field(..., example="f47ac10b-58cc-4372-a567-0e02b2c3d479", description="Unique identifier for the scraping job.")
    status: str = Field(..., example="pending", description="Current status of the job (pending, in_progress, completed, failed).")
    result: Optional[Dict[str, Any]] = Field(None, example={"url": "https://droplinked.com", "text_content": ["Droplinked", "Features", "Solutions"]}, description="The result of the scrape, available when the job is completed.")


# --- Core Scraping Logic ---
def scrape_website_text(url: str) -> List[str]:
    """
    The core scraping function. Navigates to a URL, waits for JS rendering,
    and extracts all text content into a list of strings. This is a blocking I/O-bound operation.
    Enhanced for CSR (Client-Side Rendered) websites.
    """
    print(f"Starting scrape for: {url}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Use system Chrome directly instead of downloading ChromeDriver
    # This avoids location-based download restrictions
    service = Service()  # Let Selenium find Chrome automatically
    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"Navigating to: {url}")
        driver.get(url)
        
        # Wait for initial page load
        print("Waiting for initial page load...")
        time.sleep(1)  # Reduced from 2 to 1
        
        # Scroll to load lazy content (optimized)
        print("Scrolling to load dynamic content...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        for i in range(1):  # Reduced from 2 to 1 scroll
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)  # Reduced from 1 to 0.5
            
            # Scroll back up
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.3)  # Reduced from 0.5 to 0.3
            
            # Check if page height changed (new content loaded)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Wait for any remaining dynamic content (reduced)
        print("Waiting for final content to load...")
        time.sleep(0.5)  # Reduced from 1 to 0.5
        
        # Get the final page source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "noscript"]):
            script.decompose()
        
        # Extract all text content
        all_text_list = []
        for text in soup.stripped_strings:
            # Filter out very short or empty strings
            if text and len(text.strip()) > 1:
                all_text_list.append(text.strip())
        
        print(f"Extracted {len(all_text_list)} text items from {url}")
        return all_text_list
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        raise
    finally:
        if driver:
            driver.quit()

def run_scraping_task(job_id: str, url: str):
    """
    A wrapper function for the background task. It updates the job status
    before and after running the actual scraping logic.
    """
    try:
        # Update status to 'in_progress'
        jobs[job_id]["status"] = "in_progress"
        print(f"Job {job_id} is in progress.")

        # Run the actual scraping
        scraped_text = scrape_website_text(url)

        # On success, update status and store the result in the required JSON format
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = {"url": url, "text_content": scraped_text}
        print(f"Job {job_id} completed successfully.")

    except Exception as e:
        # On failure, update status and store the error message
        print(f"Job {job_id} failed: {e}")
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["result"] = {"error": str(e)}

# --- API Endpoints ---
@app.post("/scrape", response_model=Job, status_code=202)
async def start_scraping_job(scrape_request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Accepts a URL and starts a new scraping job in the background.
    Returns a job ID immediately so the client doesn't have to wait.
    """
    job_id = str(uuid.uuid4())
    # Create the job entry with a 'pending' status
    jobs[job_id] = {"status": "pending", "result": None}

    # Add the long-running task to be executed in the background
    background_tasks.add_task(run_scraping_task, job_id, scrape_request.url)

    # Return the initial job status
    return {"job_id": job_id, "status": "pending", "result": None}


@app.get("/health")
async def health_check():
    """
    Health check endpoint for the scraper service.
    """
    return {"status": "healthy", "service": "scraper_api", "timestamp": datetime.now().isoformat()}


@app.get("/jobs/{job_id}", response_model=Job)
async def get_job_status(job_id: str):
    """
    Retrieves the status and result of a scraping job using its job ID.
    """
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Construct the full Job object to return
    return {"job_id": job_id, "status": job["status"], "result": job.get("result")}

# --- Main entry point for direct execution ---
if __name__ == "__main__":
    import uvicorn
    import os
    import sys

    print("Starting Web Scraper API server...")
    # This allows you to run the API directly with `python scraper_api.py`
    # The `reload=True` flag enables auto-reloading for development.
    
    # Get the name of the current file without the .py extension
    # This makes the script runnable even if you rename the file
    module_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    
    uvicorn.run(f"{module_name}:app", host="0.0.0.0", port=8000, reload=True)


