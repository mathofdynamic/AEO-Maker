#!/usr/bin/env python3
"""
Simple Standalone Sitemap Test

This script tests the sitemap generation directly without requiring the API server.
It demonstrates how to use the SitemapGenerator class directly.

Author: AEO-Maker
Date: 2025-01-04
"""

import sys
import os
import json
from datetime import datetime

# Add the parent directory to the path so we can import the sitemap_api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the SitemapGenerator class directly
from sitemap_api import SitemapGenerator

def test_sitemap_generation():
    """Test the SitemapGenerator directly"""
    print("🧪 SIMPLE SITEMAP TEST")
    print("=" * 50)
    
    # Test configuration
    test_url = "https://droplinked.com"
    max_depth = 3
    
    print(f"🌐 Testing URL: {test_url}")
    print(f"📊 Max Depth: {max_depth}")
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Create generator instance
        print("\n🚀 Creating SitemapGenerator...")
        generator = SitemapGenerator(test_url, max_depth)
        
        # Generate sitemap
        print("🔄 Starting sitemap generation...")
        sitemap = generator.generate_sitemap()
        
        # Create results data
        result_data = {
            'test_info': {
                'url': test_url,
                'max_depth': max_depth,
                'test_time': datetime.now().isoformat(),
                'test_type': 'standalone_direct'
            },
            'job_id': generator.job_id,
            'status': generator.status,
            'url': generator.base_url,
            'logs': generator.logs,
            'discovered_urls_count': len(generator.visited_urls),
            'total_links_found': len(generator.all_found_urls),
            'url_relationships': len(generator.url_children),
            'sitemap': sitemap,
            'start_time': generator.start_time.isoformat() if generator.start_time else None,
            'end_time': generator.end_time.isoformat() if generator.end_time else None,
            'duration_seconds': (generator.end_time - generator.start_time).total_seconds() if generator.end_time and generator.start_time else None
        }
        
        # Save results
        results_dir = "test_results"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"standalone_test_{timestamp}.json"
        filepath = os.path.join(results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Sitemap generation completed!")
        print(f"💾 Results saved to: {filepath}")
        
        # Display results summary
        print(f"\n📊 RESULTS SUMMARY")
        print("-" * 30)
        print(f"🔍 Discovered URLs: {len(generator.visited_urls)}")
        print(f"🔗 Total Links Found: {len(generator.all_found_urls)}")
        print(f"🌳 URL Relationships: {len(generator.url_children)}")
        print(f"⏱️  Duration: {result_data['duration_seconds']:.2f} seconds")
        
        # Show sitemap structure
        print(f"\n🏗️  SITEMAP STRUCTURE")
        print("-" * 30)
        if sitemap:
            for domain, pages in sitemap.items():
                print(f"🌐 Domain: {domain}")
                print(f"📄 Total Pages: {len(pages)}")
                
                # Count pages with children
                pages_with_children = 0
                total_children = 0
                
                for page, children in pages.items():
                    if isinstance(children, dict) and children:
                        pages_with_children += 1
                        total_children += len(children)
                        print(f"  📁 {page}: {len(children)} children")
                    elif isinstance(children, list) and children:
                        pages_with_children += 1
                        total_children += len(children)
                        print(f"  📄 {page}: {len(children)} descendants")
                
                print(f"📊 Pages with children: {pages_with_children}")
                print(f"👶 Total children/descendants: {total_children}")
        
        # Show some example URLs
        print(f"\n🔗 EXAMPLE DISCOVERED URLS")
        print("-" * 30)
        for i, url in enumerate(list(generator.visited_urls)[:10], 1):
            print(f"{i:2d}. {url}")
        
        if len(generator.visited_urls) > 10:
            print(f"    ... and {len(generator.visited_urls) - 10} more URLs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 Starting Simple Sitemap Test")
    print("This test runs the SitemapGenerator directly without the API server")
    print()
    
    success = test_sitemap_generation()
    
    if success:
        print(f"\n🎉 Test completed successfully!")
        print(f"📁 Check the 'test_results' directory for the JSON file")
    else:
        print(f"\n❌ Test failed!")
    
    print(f"\n📖 For more information, see README.md")

if __name__ == "__main__":
    main()
