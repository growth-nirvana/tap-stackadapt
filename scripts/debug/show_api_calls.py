#!/usr/bin/env python3
"""
Show the exact API calls being made for conversion tracker debugging
"""

import json
import sys
from urllib.parse import urlencode

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

campaign_id = config['campaign_id']
start_date = config['start_date']
end_date = config['end_date']

base_url = "https://api.stackadapt.com/service/v2"

print("=" * 80)
print("API CALLS BEING MADE")
print("=" * 80)

print("\n1. CAMPAIGN STATS (NO CONVERSION TRACKER FILTER)")
print("-" * 80)
params1 = {
    "resource_type": "campaign",
    "type": "daily",
    "id": campaign_id,
    "date_range_type": "custom",
    "start_date": start_date,
    "end_date": end_date,
    "page": 1,
}
url1 = f"{base_url}/delivery?{urlencode(params1)}"
print(f"\nFull URL:")
print(url1)
print(f"\nBreakdown:")
print(f"  Base URL: {base_url}/delivery")
print(f"  Parameters:")
for key, value in params1.items():
    print(f"    {key}: {value}")

print("\n\n2. INDIVIDUAL CONVERSION TRACKER STATS")
print("-" * 80)

# Example with a tracker ID
tracker_id = 147422  # First tracker from your campaign
params2 = {
    "resource_type": "campaign",
    "type": "daily",
    "id": campaign_id,
    "date_range_type": "custom",
    "start_date": start_date,
    "end_date": end_date,
    "page": 1,
    "conversion_tracker_id": tracker_id,  # THIS IS THE KEY PARAMETER
}
url2 = f"{base_url}/delivery?{urlencode(params2)}"
print(f"\nFull URL:")
print(url2)
print(f"\nBreakdown:")
print(f"  Base URL: {base_url}/delivery")
print(f"  Parameters:")
for key, value in params2.items():
    print(f"    {key}: {value}")

print("\n\n" + "=" * 80)
print("KEY DIFFERENCE")
print("=" * 80)
print("\nWithout tracker filter:")
print("  ❌ NO conversion_tracker_id parameter")
print("  → Should return ALL conversions for the campaign")
print("\nWith tracker filter:")
print("  ✅ conversion_tracker_id = 147422")
print("  → Should return ONLY conversions for tracker 147422")
print("  → But it's returning ALL conversions instead!")

print("\n\n" + "=" * 80)
print("HEADERS SENT")
print("=" * 80)
print(f"\nX-Authorization: {config['api_key'][:10]}...{config['api_key'][-10:]}")
print("Content-Type: application/json")

print("\n\n" + "=" * 80)
print("CURL COMMANDS")
print("=" * 80)

print("\n# Campaign stats (no filter):")
print(f"curl -X GET '{url1}' \\")
print(f"  -H 'X-Authorization: {config['api_key']}' \\")
print(f"  -H 'Content-Type: application/json'")

print("\n# Tracker-specific stats (with filter):")
print(f"curl -X GET '{url2}' \\")
print(f"  -H 'X-Authorization: {config['api_key']}' \\")
print(f"  -H 'Content-Type: application/json'")

print("\n" + "=" * 80)



