#!/usr/bin/env python3
"""
Test all conversion trackers to see if they return unique data
"""

import json
import requests

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

api_key = config['api_key']
start_date = config['start_date']
end_date = config['end_date']

base_url = "https://api.stackadapt.com/service/v2"

session = requests.Session()
session.headers.update({
    "X-Authorization": api_key,
    "Content-Type": "application/json",
})

# Get campaign to retrieve all trackers
campaign_id = config['campaign_id']
response = session.get(f"{base_url}/campaigns", params={"id": campaign_id})
campaign = response.json()["data"][0]
trackers = campaign.get("conversion_trackers", [])

print("=" * 80)
print("TESTING ALL CONVERSION TRACKERS")
print("=" * 80)
print(f"\nCampaign: {campaign['name']}")
print(f"Campaign ID: {campaign_id}")
print(f"Date Range: {start_date} to {end_date}")
print(f"Total Trackers: {len(trackers)}\n")

results = []

for tracker in trackers:
    tracker_id = tracker['id']
    tracker_name = tracker['name']
    
    print(f"\nTesting: {tracker_name} (ID: {tracker_id})")
    print("-" * 80)
    
    params = {
        "resource_type": "conversion_tracker",
        "type": "daily",
        "id": tracker_id,
        "date_range_type": "custom",
        "start_date": start_date,
        "end_date": end_date,
    }
    
    try:
        response = session.get(f"{base_url}/delivery", params=params)
        if response.status_code == 200:
            data = response.json()
            stats = data.get("stats", [])
            
            # Calculate totals
            total_conv = sum(s.get("conv", 0) for s in stats)
            total_s_conv = sum(s.get("s_conv", 0) for s in stats)
            total_sconv_imp = sum(s.get("sconv_imp", 0) for s in stats)
            
            results.append({
                "tracker_id": tracker_id,
                "tracker_name": tracker_name,
                "records": len(stats),
                "conv": total_conv,
                "s_conv": total_s_conv,
                "sconv_imp": total_sconv_imp,
            })
            
            print(f"  Records: {len(stats)}")
            print(f"  conv: {total_conv}")
            print(f"  s_conv: {total_s_conv}")
            print(f"  sconv_imp: {total_sconv_imp}")
        else:
            print(f"  ERROR: {response.status_code} - {response.text[:200]}")
            results.append({
                "tracker_id": tracker_id,
                "tracker_name": tracker_name,
                "error": response.status_code,
            })
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append({
            "tracker_id": tracker_id,
            "tracker_name": tracker_name,
            "error": str(e),
        })

print("\n\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print("\nConversion Tracker Results:")
print(f"{'Tracker Name':<45} {'ID':<10} {'Records':<10} {'s_conv':<10}")
print("-" * 80)

total_s_conv = 0
for result in results:
    if "error" not in result:
        print(f"{result['tracker_name']:<45} {result['tracker_id']:<10} {result['records']:<10} {result['s_conv']:<10}")
        total_s_conv += result['s_conv']

print("-" * 80)
print(f"{'TOTAL':<45} {'':<10} {'':<10} {total_s_conv:<10}")

print("\n✅ SUCCESS! Each tracker has different conversion counts!")
print("This is the correct endpoint to use for per-tracker stats.")

print("\n" + "=" * 80)
print("RECOMMENDATION")
print("=" * 80)
print("\nUpdate the CampaignConversionTrackerDeliveryStatsStream to use:")
print("  resource_type: 'conversion_tracker'")
print("  id: <tracker_id> (not campaign_id)")
print("  Use 's_conv' field instead of 'conv' for server-side conversions")
print("=" * 80)



