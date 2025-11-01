#!/usr/bin/env python3
"""
Simple test script to validate PDOK WMTS URLs and layer names.
Run this outside of QGIS to test our service configurations.
"""

import requests
import xml.etree.ElementTree as ET

# Copy the service configuration for testing
PDOK_SERVICES = {
    "luchtfoto": {
        "url": "https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0?",
        "layer": "Actueel_orthoHR", 
        "name": "Luchtfoto (PDOK, WMTS)",
        "format": "image/jpeg",
        "description": "Actuele luchtfoto's van Nederland"
    },
    "bgt": {
        "url": "https://service.pdok.nl/lv/bgt/wmts/v1_0?",
        "layers": {
            "standaard": "standaardvisualisatie",
            "achtergrond": "achtergrondvisualisatie", 
            "icoon": "icoonvisualisatie",
            "omtrek": "omtrekgerichtevisualisatie",
            "pastel": "pastelvisualisatie"
        },
        "default_layer": "standaardvisualisatie",
        "name": "BGT (PDOK, WMTS)",
        "format": "image/png",
        "description": "Basisregistratie Grootschalige Topografie"
    },
    "brk": {
        "url": "https://service.pdok.nl/kadaster/kadastralekaart/wmts/v5_0?",
        "layers": {
            "standaard": "kadastralekaart",
            "kwaliteit": "kadastralekaart_kwaliteit"
        },
        "default_layer": "kadastralekaart", 
        "name": "Kadastrale kaart (PDOK, WMTS)",
        "format": "image/png",
        "description": "Kadastrale percelen en grenzen"
    }
}

def test_wmts_service(service_key):
    """Test if a WMTS service responds and has expected layers."""
    service = PDOK_SERVICES[service_key]
    url = service['url'] + "request=GetCapabilities&service=WMTS"
    
    print(f"\nTesting {service_key} service:")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Define namespaces
        namespaces = {
            'wmts': 'http://www.opengis.net/wmts/1.0',
            'ows': 'http://www.opengis.net/ows/1.1'
        }
        
        # Find all layers
        layers = root.findall('.//wmts:Layer', namespaces)
        print(f"✅ Found {len(layers)} layers")
        
        # List actual layer identifiers
        layer_ids = []
        for layer in layers:
            identifier = layer.find('ows:Identifier', namespaces)
            if identifier is not None:
                layer_ids.append(identifier.text)
                print(f"   - {identifier.text}")
        
        # Check if our configured layers exist
        if 'layers' in service:
            expected_layers = service['layers'].values()
        else:
            expected_layers = [service['layer']]
            
        missing_layers = []
        for expected in expected_layers:
            if expected not in layer_ids:
                missing_layers.append(expected)
        
        if missing_layers:
            print(f"⚠️ Missing expected layers: {missing_layers}")
        else:
            print(f"✅ All expected layers found")
            
        return len(missing_layers) == 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing PDOK WMTS Services")
    print("=" * 50)
    
    for service_key in PDOK_SERVICES.keys():
        success = test_wmts_service(service_key)
        if not success:
            print(f"❌ {service_key} service test FAILED")
        else:
            print(f"✅ {service_key} service test PASSED")