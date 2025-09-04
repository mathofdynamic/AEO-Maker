#!/usr/bin/env python3
"""
Simple Scraper API Test

This script tests the text scraping functionality and saves results to JSON files.
It demonstrates how to use the scraper_api.py service to extract text from websites.

Author: AEO-Maker
Date: 2025-01-04
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, Any

# Add the parent directory to the path so we can import the scraper_api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the scraping function directly
from scraper_api import scrape_website_text

def test_scraper_api():
    """Test the scraper API functionality"""
    print("🧪 SIMPLE SCRAPER TEST")
    print("=" * 50)
    
    # Test configuration
    test_urls = [
        "https://droplinked.com",
        "https://example.com",
        "https://httpbin.org"
    ]
    
    print(f"🌐 Testing URLs: {test_urls}")
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create results directory
    results_dir = "test_results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"📁 Created results directory: {results_dir}")
    
    all_results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{'='*60}")
        print(f"🧪 TEST {i}/{len(test_urls)}: {url}")
        print(f"{'='*60}")
        
        try:
            print(f"🚀 Starting real scraping for: {url}")
            start_time = time.time()
            
            # Use the real scraping function
            scraped_text = scrape_website_text(url)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ Real scraping completed in {duration:.2f} seconds")
            
            # Create result data
            result_data = {
                'test_info': {
                    'url': url,
                    'test_time': datetime.now().isoformat(),
                    'test_type': 'real_scraper',
                    'test_number': i
                },
                'url': url,
                'status': 'completed',
                'result': {
                    'url': url,
                    'text_content': scraped_text
                },
                'scraped_text_count': len(scraped_text),
                'scraped_text_sample': scraped_text[:5],
                'duration_seconds': duration
            }
            
            all_results.append(result_data)
            
            # Save individual result
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraper_test_{i}_{timestamp}.json"
            filepath = os.path.join(results_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Results saved to: {filepath}")
            print(f"📊 Scraped {result_data['scraped_text_count']} text items")
            
            # Show sample text
            if result_data['scraped_text_sample']:
                print("📝 Sample text items:")
                for j, text in enumerate(result_data['scraped_text_sample'], 1):
                    print(f"  {j:2d}. {text}")
            
        except Exception as e:
            print(f"❌ Error during demo scraping: {e}")
            import traceback
            traceback.print_exc()
            
            # Create error result
            error_result = {
                'test_info': {
                    'url': url,
                    'test_time': datetime.now().isoformat(),
                    'test_type': 'real_scraper',
                    'test_number': i
                },
                'url': url,
                'status': 'failed',
                'result': {
                    'error': str(e)
                },
                'scraped_text_count': 0,
                'scraped_text_sample': [],
                'duration_seconds': 0
            }
            
            all_results.append(error_result)
    
    # Save combined results
    if all_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_filename = f"scraper_combined_results_{timestamp}.json"
        combined_filepath = os.path.join(results_dir, combined_filename)
        
        combined_data = {
            'test_summary': {
                'total_tests': len(test_urls),
                'successful_tests': len([r for r in all_results if r['status'] == 'completed']),
                'failed_tests': len([r for r in all_results if r['status'] == 'failed']),
                'test_time': datetime.now().isoformat(),
                'test_type': 'real_scraper_combined'
            },
            'results': all_results
        }
        
        with open(combined_filepath, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 TEST SUMMARY")
        print("-" * 30)
        successful = len([r for r in all_results if r['status'] == 'completed'])
        failed = len([r for r in all_results if r['status'] == 'failed'])
        print(f"✅ Successful tests: {successful}/{len(test_urls)}")
        print(f"❌ Failed tests: {failed}/{len(test_urls)}")
        print(f"💾 Combined results saved to: {combined_filepath}")
        
        # Show statistics
        total_text_items = sum(result['scraped_text_count'] for result in all_results if result['status'] == 'completed')
        print(f"📝 Total text items scraped: {total_text_items}")
        
        if successful > 0:
            avg_text_items = total_text_items / successful
            print(f"📊 Average text items per URL: {avg_text_items:.1f}")
    
    return len([r for r in all_results if r['status'] == 'completed']) > 0

def main():
    """Main function"""
    print("🚀 Starting Real Scraper Test")
    print("This test uses the actual scraper to extract text from websites")
    print("💡 Enhanced for CSR (Client-Side Rendered) websites")
    print()
    
    success = test_scraper_api()
    
    if success:
        print(f"\n🎉 Test completed successfully!")
        print(f"📁 Check the 'test_results' directory for the JSON files")
        print(f"💡 This extracted real text content from the websites")
    else:
        print(f"\n❌ Test failed!")
    
    print(f"\n📖 For more information, see README.md")

if __name__ == "__main__":
    main()
