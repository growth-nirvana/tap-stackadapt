#!/usr/bin/env python3
"""
Debug tool for StackAdapt Campaign Conversion Tracker Delivery Stats

This tool helps debug data accuracy issues by:
1. Fetching campaign details and conversion trackers
2. Making direct API calls to get delivery stats
3. Comparing stats with and without conversion tracker filtering
4. Showing raw API responses for inspection

Usage:
    # Using config.json:
    python debug_conversion_tracker_stats.py --config config.json
    
    # Or using command-line arguments:
    python debug_conversion_tracker_stats.py --campaign-id <ID> --api-key <KEY> [options]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests


class StackAdaptDebugger:
    """Debug helper for StackAdapt API calls."""

    def __init__(self, api_key: str):
        """Initialize the debugger with API credentials."""
        self.api_key = api_key
        self.base_url = "https://api.stackadapt.com/service/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "X-Authorization": api_key,
            "Content-Type": "application/json",
        })

    def get_campaign(self, campaign_id: int) -> dict[str, Any] | None:
        """Fetch campaign details."""
        print(f"\n{'='*80}")
        print(f"FETCHING CAMPAIGN DETAILS")
        print(f"{'='*80}")
        
        url = f"{self.base_url}/campaigns"
        params = {"id": campaign_id}
        
        print(f"\nRequest URL: {url}")
        print(f"Request Params: {json.dumps(params, indent=2)}")
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            campaigns = data.get("data", [])
            if campaigns:
                campaign = campaigns[0]
                print(f"\nCampaign Found:")
                print(f"  ID: {campaign.get('id')}")
                print(f"  Name: {campaign.get('name')}")
                print(f"  Status: {campaign.get('status', {}).get('code')}")
                
                trackers = campaign.get("conversion_trackers", [])
                print(f"\n  Conversion Trackers ({len(trackers)}):")
                for tracker in trackers:
                    print(f"    - ID: {tracker.get('id')}, Name: {tracker.get('name')}")
                
                return campaign
            else:
                print(f"\nERROR: Campaign {campaign_id} not found")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"\nERROR fetching campaign: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None

    def get_delivery_stats(
        self,
        campaign_id: int,
        start_date: str,
        end_date: str,
        conversion_tracker_id: int | None = None,
        page: int = 1,
    ) -> dict[str, Any]:
        """Fetch delivery stats for a campaign."""
        url = f"{self.base_url}/delivery"
        params = {
            "resource_type": "campaign",
            "type": "daily",
            "id": campaign_id,
            "date_range_type": "custom",
            "start_date": start_date,
            "end_date": end_date,
            "page": page,
        }
        
        if conversion_tracker_id:
            params["conversion_tracker_id"] = conversion_tracker_id
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"\nERROR fetching delivery stats: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return {}

    def compare_stats(
        self,
        campaign_id: int,
        start_date: str,
        end_date: str,
        conversion_trackers: list[dict],
    ) -> None:
        """Compare stats with and without conversion tracker filtering."""
        print(f"\n{'='*80}")
        print(f"COMPARING DELIVERY STATS")
        print(f"{'='*80}")
        print(f"Date Range: {start_date} to {end_date}")
        
        # Get stats without conversion tracker filter (all campaign stats)
        print(f"\n{'='*80}")
        print(f"1. CAMPAIGN STATS (NO CONVERSION TRACKER FILTER)")
        print(f"{'='*80}")
        
        campaign_stats = self.get_delivery_stats(campaign_id, start_date, end_date)
        self._print_stats_summary(campaign_stats, "Campaign (All Trackers)")
        
        # Get stats for each conversion tracker
        tracker_stats_list = []
        for tracker in conversion_trackers:
            tracker_id = tracker.get("id")
            tracker_name = tracker.get("name", "Unknown")
            
            print(f"\n{'='*80}")
            print(f"2. CONVERSION TRACKER: {tracker_name} (ID: {tracker_id})")
            print(f"{'='*80}")
            
            tracker_stats = self.get_delivery_stats(
                campaign_id,
                start_date,
                end_date,
                conversion_tracker_id=tracker_id,
            )
            tracker_stats_list.append({
                "tracker": tracker,
                "stats": tracker_stats,
            })
            self._print_stats_summary(tracker_stats, f"Tracker: {tracker_name}")
        
        # Compare totals
        print(f"\n{'='*80}")
        print(f"COMPARISON SUMMARY")
        print(f"{'='*80}")
        
        campaign_totals = self._calculate_totals(campaign_stats.get("stats", []))
        print(f"\nCampaign Totals (All Trackers):")
        self._print_totals(campaign_totals)
        
        for tracker_data in tracker_stats_list:
            tracker = tracker_data["tracker"]
            stats = tracker_data["stats"]
            tracker_name = tracker.get("name", "Unknown")
            
            tracker_totals = self._calculate_totals(stats.get("stats", []))
            print(f"\nTracker '{tracker_name}' Totals:")
            self._print_totals(tracker_totals)
        
        # Check for discrepancies
        print(f"\n{'='*80}")
        print(f"DISCREPANCY ANALYSIS")
        print(f"{'='*80}")
        
        # Sum all tracker stats
        all_tracker_totals = {"conv": 0, "conv_click": 0, "conv_imp_derived": 0}
        for tracker_data in tracker_stats_list:
            stats = tracker_data["stats"]
            totals = self._calculate_totals(stats.get("stats", []))
            for key in all_tracker_totals:
                all_tracker_totals[key] += totals.get(key, 0)
        
        print(f"\nSum of All Individual Trackers:")
        self._print_totals(all_tracker_totals)
        
        print(f"\nDifference (Campaign - Sum of Trackers):")
        for key in all_tracker_totals:
            diff = campaign_totals.get(key, 0) - all_tracker_totals.get(key, 0)
            print(f"  {key}: {diff}")
        
        # Show warning if there are discrepancies
        has_discrepancy = False
        for key in all_tracker_totals:
            if campaign_totals.get(key, 0) != all_tracker_totals.get(key, 0):
                has_discrepancy = True
                break
        
        if has_discrepancy:
            print(f"\n⚠️  WARNING: Discrepancies detected!")
            print(f"    Campaign totals don't match sum of individual tracker stats.")
            print(f"    This suggests the conversion_tracker_id filter may not be working correctly.")
        else:
            print(f"\n✓ No discrepancies found. Stats match expected values.")

    def _print_stats_summary(self, data: dict[str, Any], label: str) -> None:
        """Print a summary of stats data."""
        stats = data.get("stats", [])
        
        print(f"\nRequest URL: {self.base_url}/delivery")
        print(f"Stats Records Returned: {len(stats)}")
        
        if stats:
            print(f"\nFirst Record:")
            print(json.dumps(stats[0], indent=2, default=str))
            
            if len(stats) > 1:
                print(f"\nLast Record:")
                print(json.dumps(stats[-1], indent=2, default=str))
        else:
            print("\n⚠️  No stats data returned!")

    def _calculate_totals(self, stats: list[dict]) -> dict[str, float]:
        """Calculate totals across all stats records."""
        totals = {
            "imp": 0,
            "click": 0,
            "cost": 0.0,
            "conv": 0,
            "conv_click": 0,
            "conv_imp_derived": 0,
            "conv_rev": 0.0,
        }
        
        for record in stats:
            for key in totals:
                value = record.get(key, 0)
                if value is not None:
                    totals[key] += float(value) if isinstance(value, (int, float)) else 0
        
        return totals

    def _print_totals(self, totals: dict[str, float]) -> None:
        """Print totals in a formatted way."""
        for key, value in totals.items():
            if isinstance(value, float) and value != int(value):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {int(value)}")

    def export_raw_data(
        self,
        campaign_id: int,
        start_date: str,
        end_date: str,
        conversion_trackers: list[dict],
        output_file: str,
    ) -> None:
        """Export all raw API responses to a JSON file."""
        print(f"\n{'='*80}")
        print(f"EXPORTING RAW DATA")
        print(f"{'='*80}")
        
        export_data = {
            "campaign_id": campaign_id,
            "date_range": {"start": start_date, "end": end_date},
            "timestamp": datetime.now().isoformat(),
            "campaign_stats": {},
            "tracker_stats": [],
        }
        
        # Get campaign stats
        print(f"\nFetching campaign stats...")
        campaign_stats = self.get_delivery_stats(campaign_id, start_date, end_date)
        export_data["campaign_stats"] = campaign_stats
        
        # Get tracker stats
        for tracker in conversion_trackers:
            tracker_id = tracker.get("id")
            tracker_name = tracker.get("name", "Unknown")
            print(f"Fetching stats for tracker: {tracker_name} (ID: {tracker_id})...")
            
            tracker_stats = self.get_delivery_stats(
                campaign_id,
                start_date,
                end_date,
                conversion_tracker_id=tracker_id,
            )
            
            export_data["tracker_stats"].append({
                "tracker_id": tracker_id,
                "tracker_name": tracker_name,
                "stats": tracker_stats,
            })
        
        # Write to file
        with open(output_file, "w") as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"\n✓ Raw data exported to: {output_file}")


def load_config(config_path: str) -> dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in config file: {e}")
        sys.exit(1)


def main():
    """Main entry point for the debug tool."""
    parser = argparse.ArgumentParser(
        description="Debug StackAdapt Campaign Conversion Tracker Delivery Stats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using config file:
  python debug_conversion_tracker_stats.py --config config.json
  
  # Using command-line arguments:
  python debug_conversion_tracker_stats.py --campaign-id 12345 --api-key YOUR_KEY
  
  # Export raw data:
  python debug_conversion_tracker_stats.py --config config.json --export output.json
        """,
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to config.json file (contains api_key, campaign_id, etc.)",
    )
    parser.add_argument(
        "--campaign-id",
        type=int,
        help="Campaign ID to debug",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="StackAdapt API key (or set STACKADAPT_API_KEY env var)",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date (YYYY-MM-DD). Default: 7 days ago",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="End date (YYYY-MM-DD). Default: today",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        help="Number of days to look back (default: 7)",
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export raw data to JSON file",
    )
    
    args = parser.parse_args()
    
    # Load config from file if provided
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # Override config with command-line arguments
    campaign_id = args.campaign_id or config.get("campaign_id")
    api_key = args.api_key or config.get("api_key") or os.environ.get("STACKADAPT_API_KEY")
    lookback_days = args.lookback_days or config.get("lookback_days", 7)
    export_file = args.export or config.get("export_file")
    
    # Validation
    if not campaign_id:
        print("ERROR: Campaign ID required. Use --campaign-id or specify in config.json")
        print("Run with --help for usage examples")
        sys.exit(1)
    
    if not api_key:
        print("ERROR: API key required. Use --api-key, set STACKADAPT_API_KEY env var, or specify in config.json")
        sys.exit(1)
    
    # Set date range
    if args.start_date:
        start_date = args.start_date
    elif config.get("start_date"):
        start_date = config["start_date"]
    else:
        start_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    
    if args.end_date:
        end_date = args.end_date
    elif config.get("end_date"):
        end_date = config["end_date"]
    else:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    # Initialize debugger
    debugger = StackAdaptDebugger(api_key)
    
    # Fetch campaign details
    campaign = debugger.get_campaign(campaign_id)
    if not campaign:
        sys.exit(1)
    
    conversion_trackers = campaign.get("conversion_trackers", [])
    if not conversion_trackers:
        print("\n⚠️  WARNING: This campaign has no conversion trackers!")
        print("    The conversion tracker delivery stats stream will skip this campaign.")
        sys.exit(0)
    
    # Compare stats
    debugger.compare_stats(
        campaign_id,
        start_date,
        end_date,
        conversion_trackers,
    )
    
    # Export raw data if requested
    if export_file:
        debugger.export_raw_data(
            campaign_id,
            start_date,
            end_date,
            conversion_trackers,
            export_file,
        )
    
    print(f"\n{'='*80}")
    print("DEBUG COMPLETE")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

