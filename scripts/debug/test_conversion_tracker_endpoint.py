#!/usr/bin/env python3
"""
Test the conversion_tracker resource_type endpoint approach
"""

import json
import requests

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

api_key = config['api_key']
campaign_id = config['campaign_id']
start_date = config['start_date']
end_date = config['end_date']

base_url = "https://api.stackadapt.com/service/v2"

session = requests.Session()
session.headers.update({
    "X-Authorization": api_key,
    "Content-Type": "application/json",
})

print("=" * 80)
print("TESTING CONVERSION TRACKER RESOURCE TYPE")
print("=" * 80)

# Test 1: Get conversion tracker stats grouped by campaign
print("\n1. CONVERSION TRACKER STATS (grouped by campaign)")
print("-" * 80)

params = {
    "resource_type": "conversion_tracker",
    "type": "daily",
    "date_range_type": "custom",
    "start_date": start_date,
    "end_date": end_date,
    "group_by_resource": "campaign"
}

url = f"{base_url}/delivery"
print(f"URL: {url}")
print(f"Params: {json.dumps(params, indent=2)}")

try:
    response = session.get(url, params=params)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nResponse structure:")
        print(json.dumps(data, indent=2)[:1000])  # First 1000 chars
        
        stats = data.get("stats", [])
        print(f"\n\nTotal stats records: {len(stats)}")
        
        if stats:
            print("\nFirst record:")
            print(json.dumps(stats[0], indent=2))
    else:
        print(f"\nError response: {response.text[:500]}")
        
except Exception as e:
    print(f"\nError: {e}")

# Test 2: Try with specific conversion tracker ID
print("\n\n2. SPECIFIC CONVERSION TRACKER STATS")
print("-" * 80)

tracker_id = 147422  # First tracker from your campaign

params2 = {
    "resource_type": "conversion_tracker",
    "type": "daily",
    "id": tracker_id,
    "date_range_type": "custom",
    "start_date": start_date,
    "end_date": end_date,
}

print(f"URL: {url}")
print(f"Params: {json.dumps(params2, indent=2)}")

try:
    response = session.get(url, params=params2)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n" + "="*80)
        print("FULL RAW JSON RESPONSE")
        print("="*80)
        print(json.dumps(data, indent=2, default=str))
        print("="*80)
        
        stats = data.get("stats", [])
        print(f"\nTotal stats records: {len(stats)}")
        
        if stats:
            print("\nFirst record:")
            print(json.dumps(stats[0], indent=2))
            
            # Calculate totals
            total_conv = sum(s.get("conv", 0) for s in stats)
            total_s_conv = sum(s.get("s_conv", 0) for s in stats)
            print(f"\nTotal conversions for tracker {tracker_id}:")
            print(f"  conv: {total_conv}")
            print(f"  s_conv: {total_s_conv}")
    else:
        print(f"\nError response: {response.text[:500]}")
        
except Exception as e:
    print(f"\nError: {e}")

# Test 3: Try with campaign filter
print("\n\n3. CONVERSION TRACKER STATS FILTERED BY CAMPAIGN")
print("-" * 80)

params3 = {
    "resource_type": "conversion_tracker",
    "type": "daily",
    "id": tracker_id,
    "date_range_type": "custom",
    "start_date": start_date,
    "end_date": end_date,
    "campaign_id": campaign_id,
}

print(f"URL: {url}")
print(f"Params: {json.dumps(params3, indent=2)}")

try:
    response = session.get(url, params=params3)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n" + "="*80)
        print("FULL RAW JSON RESPONSE (with campaign_id filter)")
        print("="*80)
        print(json.dumps(data, indent=2, default=str))
        print("="*80)
        
        stats = data.get("stats", [])
        print(f"\nTotal stats records: {len(stats)}")
        
        if stats:
            print("\nFirst record:")
            print(json.dumps(stats[0], indent=2))
            
            # Calculate totals
            total_conv = sum(s.get("conv", 0) for s in stats)
            total_s_conv = sum(s.get("s_conv", 0) for s in stats)
            print(f"\nTotal conversions for tracker {tracker_id} + campaign {campaign_id}:")
            print(f"  conv: {total_conv}")
            print(f"  s_conv: {total_s_conv}")
    else:
        print(f"\nError response: {response.text[:500]}")
        
except Exception as e:
    print(f"\nError: {e}")

print("\n" + "=" * 80)


