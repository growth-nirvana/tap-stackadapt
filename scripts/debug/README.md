# StackAdapt Conversion Tracker Debug Tools

This directory contains tools to debug and analyze StackAdapt conversion tracker data accuracy issues.

## Tools Available

1. **`debug_old_stream_issue.py`** - Main debug tool (OLD STREAM ISSUE)
   - Fetches campaign details and conversion trackers
   - Makes direct API calls to compare campaign-level vs tracker-level stats
   - Identifies discrepancies in the old `CampaignConversionTrackerDeliveryStatsStream`
   - Exports raw data for analysis
   - **Purpose**: Prove the old stream has issues

2. **`test_conversion_tracker_endpoint.py`** - Endpoint testing tool (CORRECT ENDPOINT)
   - Tests the correct `resource_type=conversion_tracker` endpoint
   - Shows full raw JSON responses from the API
   - Validates per-tracker conversion data
   - Demonstrates the correct API usage for the new `ConversionTrackerStatsStream`
   - **Purpose**: Show the correct way to query tracker data

3. **`test_all_trackers.py`** - Bulk tracker validator
   - Tests all conversion trackers for a campaign
   - Verifies each tracker returns unique conversion counts
   - Shows summary totals for all trackers
   - **Purpose**: Confirm each tracker has unique data

4. **`show_api_calls.py`** - API call documentation
   - Shows the exact API calls being made
   - Demonstrates the difference between old and new approaches
   - Prints curl commands for manual testing
   - **Purpose**: Documentation and debugging reference

## Key Findings

### The Problem
The old `CampaignConversionTrackerDeliveryStatsStream` uses:
```
resource_type: "campaign"
conversion_tracker_id: <tracker_id>  # This parameter is IGNORED by API
```

**Result**: Every tracker query returns the same campaign totals → **inaccurate data**

### The Solution
The new `ConversionTrackerStatsStream` uses:
```
resource_type: "conversion_tracker"
id: <tracker_id>  # Query by tracker directly
```

**Result**: Each tracker returns unique conversion data → **accurate per-tracker stats**

## Setup

### 1. Create virtual environment

```bash
cd scripts/debug
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create config file

Copy the example config and fill in your details:

```bash
cp config.example.json config.json
```

Edit `config.json`:

```json
{
  "api_key": "your-stackadapt-api-key",
  "campaign_id": 12345,
  "start_date": "2024-10-01",
  "end_date": "2024-10-07",
  "lookback_days": 7,
  "export_file": "debug_output.json"
}
```

**Note:** Add `config.json` to `.gitignore` to avoid committing your API key!

## Usage

### Quick start with wrapper script

```bash
./run_debug.sh --config config.json
```

### Using config file (recommended)

```bash
# Activate venv first
source venv/bin/activate

# Test the old broken stream issue
python debug_old_stream_issue.py --config config.json

# Test the correct endpoint (with full raw responses)
python test_conversion_tracker_endpoint.py

# Test all trackers to verify unique data
python test_all_trackers.py

# Show API calls being made
python show_api_calls.py
```

### Using command-line arguments

```bash
python debug_old_stream_issue.py \
  --campaign-id 12345 \
  --api-key YOUR_API_KEY \
  --start-date 2024-10-01 \
  --end-date 2024-10-07
```

### Export raw data for further analysis

```bash
python debug_old_stream_issue.py --config config.json --export output.json
```

### Using environment variable for API key

```bash
export STACKADAPT_API_KEY="your-api-key"
python debug_old_stream_issue.py --campaign-id 12345
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `api_key` | StackAdapt API key | Required |
| `campaign_id` | Campaign ID to debug | Required |
| `start_date` | Start date (YYYY-MM-DD) | 7 days ago |
| `end_date` | End date (YYYY-MM-DD) | Today |
| `lookback_days` | Number of days to look back | 7 |
| `export_file` | Path to export raw JSON data | None |

## Understanding the Output

### Campaign Details
Shows the campaign name, status, and all associated conversion trackers.

### Stats Comparison (debug_old_stream_issue.py)
The tool fetches:
1. **Campaign stats (no filter)**: All delivery stats for the campaign
2. **Individual tracker stats**: Stats filtered by each conversion tracker ID

### Discrepancy Analysis
Compares:
- Campaign total conversions
- Sum of individual tracker conversions

**What to expect:**
- ❌ **Old endpoint**: All trackers return identical data (API bug)
- ✅ **New endpoint**: Each tracker returns unique conversion counts

### Key Metrics

The new `ConversionTrackerStatsStream` uses these fields:
- `s_conv`: Server-side conversions (primary metric)
- `sconv_imp`: Server-side impression conversions
- `conv`: Regular client-side conversions
- Note: `imp`, `click`, `cost` are typically 0 at tracker level (campaign-level metrics)

### Warning Signs

⚠️ **Discrepancies detected** - Old stream returns duplicate data
- Indicates the `conversion_tracker_id` filter is being ignored by API
- Solution: Use the new `ConversionTrackerStatsStream` instead

✓ **No discrepancies** - Stats match expected values
- Each tracker has unique conversion counts
- Use the new `ConversionTrackerStatsStream` for accurate data

## Troubleshooting

### "Campaign not found"
- Verify the campaign ID is correct
- Check that your API key has access to this campaign

### "No conversion trackers"
- This campaign has no conversion trackers configured
- Both `CampaignConversionTrackerDeliveryStatsStream` and `ConversionTrackerStatsStream` will skip this campaign

### "No stats data returned"
- Campaign may not have data for the selected date range
- Try a wider date range or different campaign
- Some trackers may have zero conversions for the date range

### Understanding s_conv vs conv
- `s_conv`: Server-side conversions (fires server-to-server) - more reliable
- `conv`: Client-side conversions (fires in browser) - can be blocked
- Most trackers use server-side conversions, so `s_conv` is the primary metric

## Example Output

### Running test_conversion_tracker_endpoint.py

```
================================================================================
TESTING CONVERSION TRACKER RESOURCE TYPE
================================================================================

2. SPECIFIC CONVERSION TRACKER STATS
--------------------------------------------------------------------------------
URL: https://api.stackadapt.com/service/v2/delivery
Params: {
  "resource_type": "conversion_tracker",
  "type": "daily",
  "id": 147422,
  "date_range_type": "custom",
  "start_date": "2025-09-16",
  "end_date": "2025-09-28"
}

Status Code: 200

================================================================================
FULL RAW JSON RESPONSE
================================================================================
{
  "stats": [
    {
      "date": "2025-09-28",
      "s_conv": 38,
      "sconv_imp": 38,
      "conv": 37,
      "tracker_conv": "SolidCore Landing Page Visits",
      "id": 147422
      ...
    }
  ]
}

Total stats records: 13

Total conversions for tracker 147422:
  conv: 37
  s_conv: 340
```

### Running test_all_trackers.py

```
================================================================================
SUMMARY
================================================================================

Tracker Name                                  ID         s_conv    
--------------------------------------------------------------------------------
SolidCore Landing Page Visits                 147422     340       
Solidcore Booked Class / Purchase             148822     0         
Solidcore Initate Booking Checkout            148276     19        
--------------------------------------------------------------------------------
TOTAL                                                               359       

✅ SUCCESS! Each tracker has different conversion counts!
This is the correct endpoint to use for per-tracker stats.
```

## Files Generated

- `debug_output.json` - Full raw data export from `debug_old_stream_issue.py`
- `tracker_raw_response.txt` - Full API response output from `test_conversion_tracker_endpoint.py`

**Note**: These are output files. You can safely delete them and regenerate by running the tools again.

