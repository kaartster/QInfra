#!/usr/bin/env python3
"""
Quick URL tester to find working PDOK WMTS endpoints.
Run this to test which URLs actually work.
"""

def test_url_simple(url, name):
    """Simple URL test - just check if we get a response"""
    import requests
    try:
        response = requests.get(f"{url}?request=GetCapabilities&service=WMTS", timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: {url} - WORKS")
            return True
        else:
            print(f"❌ {name}: {url} - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: {url} - ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Testing PDOK WMTS URLs")
    print("=" * 50)
    
    # Test URLs
    urls_to_test = [
        ("Luchtfoto (working)", "https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0"),
        ("BGT Original", "https://service.pdok.nl/lv/bgt/wmts/v1_0"),
        ("BGT Alt 1", "https://service.pdok.nl/bgt/wmts/v1_0"),
        ("BGT Alt 2", "https://geodata.nationaalgeoregister.nl/bgt/wmts"),
        ("BGT Alt 3", "https://service.pdok.nl/lv/bgt/wmts"),
        ("BRK Original", "https://service.pdok.nl/kadaster/kadastralekaart/wmts/v5_0"),
        ("BRK Alt 1", "https://service.pdok.nl/kadaster/kadastralekaart/wmts"),
        ("BRK Alt 2", "https://geodata.nationaalgeoregister.nl/kadastralekaart/wmts"),
        ("BRK Alt 3", "https://service.pdok.nl/brk/wmts"),
    ]
    
    working_urls = []
    for name, url in urls_to_test:
        if test_url_simple(url, name):
            working_urls.append((name, url))
    
    print("\n" + "=" * 50)
    print("WORKING URLs:")
    for name, url in working_urls:
        print(f"  {name}: {url}")