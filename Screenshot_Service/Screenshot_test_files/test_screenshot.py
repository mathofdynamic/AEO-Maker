#!/usr/bin/env python3
"""
Screenshot API Test

This script tests the screenshot functionality and saves results to JSON files.
It demonstrates how to use the screenshot_api.py service to capture full-page screenshots.

Author: AEO-Maker
Date: 2025-01-04
"""

import sys
import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any

def test_screenshot_api():
    """Test the screenshot API functionality"""
    print("🧪 SCREENSHOT API TEST")
    print("=" * 50)
    
    # Test configuration
    test_urls = [
        "https://droplinked.com",
        "https://example.com",
        "https://httpbin.org"
    ]
    
    base_url = "http://localhost:5002"
    
    print(f"🌐 Testing URLs: {test_urls}")
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create results directory (ensure it's in the test directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, "test_results")
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"📁 Created results directory: {results_dir}")
    
    all_results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{'='*60}")
        print(f"🧪 TEST {i}/{len(test_urls)}: {url}")
        print(f"{'='*60}")
        
        try:
            # Test 1: Check if API is running
            print("🔍 Checking if API server is running...")
            try:
                response = requests.get(f"{base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ API server is running")
                else:
                    print(f"❌ API server returned status {response.status_code}")
                    continue
            except requests.exceptions.RequestException as e:
                print(f"❌ Cannot connect to API server: {e}")
                print("💡 Make sure to start the screenshot API server first:")
                print("   cd Screenshot_Service")
                print("   python screenshot_api.py")
                continue
            
            # Test 2: Take screenshot
            print(f"📸 Taking screenshot of: {url}")
            start_time = time.time()
            
            screenshot_request = {"url": url}
            
            response = requests.post(
                f"{base_url}/screenshot",
                json=screenshot_request,
                headers={'Content-Type': 'application/json'},
                timeout=60  # Screenshots can take longer
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                screenshot_data = response.json()
                
                if screenshot_data.get('success'):
                    print(f"✅ Screenshot completed in {duration:.2f} seconds")
                    
                    # Create result data
                    result_data = {
                        'test_info': {
                            'url': url,
                            'test_time': datetime.now().isoformat(),
                            'test_type': 'screenshot_api',
                            'test_number': i
                        },
                        'url': url,
                        'status': 'completed',
                        'result': screenshot_data,
                        'screenshot_path': screenshot_data.get('file_path', ''),
                        'screenshot_width': screenshot_data.get('width', 0),
                        'screenshot_height': screenshot_data.get('height', 0),
                        'duration_seconds': duration
                    }
                    
                    all_results.append(result_data)
                    
                    # Save individual result
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"screenshot_test_{i}_{timestamp}.json"
                    filepath = os.path.join(results_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(result_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"💾 Results saved to: {filepath}")
                    print(f"📸 Screenshot saved to: {screenshot_data.get('file_path', 'N/A')}")
                    print(f"📐 Dimensions: {screenshot_data.get('width', 0)}x{screenshot_data.get('height', 0)}")
                    
                else:
                    print(f"❌ Screenshot failed: {screenshot_data.get('error', 'Unknown error')}")
                    
                    # Create error result
                    error_result = {
                        'test_info': {
                            'url': url,
                            'test_time': datetime.now().isoformat(),
                            'test_type': 'screenshot_api',
                            'test_number': i
                        },
                        'url': url,
                        'status': 'failed',
                        'result': {
                            'error': screenshot_data.get('error', 'Unknown error')
                        },
                        'screenshot_path': '',
                        'screenshot_width': 0,
                        'screenshot_height': 0,
                        'duration_seconds': duration
                    }
                    
                    all_results.append(error_result)
            else:
                print(f"❌ API request failed with status {response.status_code}: {response.text}")
                
                # Create error result
                error_result = {
                    'test_info': {
                        'url': url,
                        'test_time': datetime.now().isoformat(),
                        'test_type': 'screenshot_api',
                        'test_number': i
                    },
                    'url': url,
                    'status': 'failed',
                    'result': {
                        'error': f"API request failed: {response.status_code}"
                    },
                    'screenshot_path': '',
                    'screenshot_width': 0,
                    'screenshot_height': 0,
                    'duration_seconds': duration
                }
                
                all_results.append(error_result)
            
        except Exception as e:
            print(f"❌ Error during screenshot test: {e}")
            import traceback
            traceback.print_exc()
            
            # Create error result
            error_result = {
                'test_info': {
                    'url': url,
                    'test_time': datetime.now().isoformat(),
                    'test_type': 'screenshot_api',
                    'test_number': i
                },
                'url': url,
                'status': 'failed',
                'result': {
                    'error': str(e)
                },
                'screenshot_path': '',
                'screenshot_width': 0,
                'screenshot_height': 0,
                'duration_seconds': 0
            }
            
            all_results.append(error_result)
    
    # Save combined results
    if all_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_filename = f"screenshot_combined_results_{timestamp}.json"
        combined_filepath = os.path.join(results_dir, combined_filename)
        
        combined_data = {
            'test_summary': {
                'total_tests': len(test_urls),
                'successful_tests': len([r for r in all_results if r['status'] == 'completed']),
                'failed_tests': len([r for r in all_results if r['status'] == 'failed']),
                'test_time': datetime.now().isoformat(),
                'test_type': 'screenshot_api_combined'
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
        if successful > 0:
            total_width = sum(result['screenshot_width'] for result in all_results if result['status'] == 'completed')
            total_height = sum(result['screenshot_height'] for result in all_results if result['status'] == 'completed')
            avg_width = total_width / successful
            avg_height = total_height / successful
            print(f"📐 Average screenshot dimensions: {avg_width:.0f}x{avg_height:.0f}")
            
            # Show screenshot paths
            print(f"📸 Screenshots saved to:")
            for result in all_results:
                if result['status'] == 'completed' and result['screenshot_path']:
                    print(f"  - {result['screenshot_path']}")
    
    return len([r for r in all_results if r['status'] == 'completed']) > 0

def main():
    """Main function"""
    print("🚀 Starting Screenshot API Test")
    print("This test requires the screenshot API server to be running")
    print("💡 To start the server: cd Screenshot_Service && python screenshot_api.py")
    print()
    
    success = test_screenshot_api()
    
    if success:
        print(f"\n🎉 Test completed successfully!")
        print(f"📁 Check the 'test_results' directory for the JSON files")
        print(f"📸 Check the 'screenshots' directory for the captured images")
    else:
        print(f"\n❌ Test failed!")
        print("💡 Make sure the screenshot API server is running on http://localhost:5002")
    
    print(f"\n📖 For more information, see README.md")

if __name__ == "__main__":
    main()
