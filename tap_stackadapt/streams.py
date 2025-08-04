"""Stream type classes for tap-stackadapt."""

from __future__ import annotations

import typing as t
from datetime import datetime, timedelta
from importlib import resources

from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.pagination import BaseAPIPaginator

from tap_stackadapt import RUN_ID
from tap_stackadapt.client import StackadaptStream

# TODO: Delete this is if not using json files for schema definition
SCHEMAS_DIR = resources.files(__package__) / "schemas"


class StackAdaptPaginator(BaseAPIPaginator):
    """Paginator for StackAdapt API responses."""
    
    def __init__(self, start_value: int = 1):
        super().__init__(start_value)
        self._page = start_value
    
    def get_next(self, response):
        """Get the next page token from the response."""
        data = response.json()
        total_items = data.get("total_campaigns", data.get("total_advertisers", 0))
        current_page = data.get("page", 1)
        page_size = 100  # Assuming 100 items per page
        
        if (total_items / page_size) > current_page:
            return current_page + 1
        return None


class CampaignsStream(StackadaptStream):
    """Campaigns stream for StackAdapt."""

    name = "campaigns"
    path = "/campaigns"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None
    
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, description="Campaign ID"),
        th.Property("name", th.StringType, description="Campaign name"),
        th.Property("status", th.ObjectType(
            th.Property("code", th.StringType, description="Status code"),
            th.Property("description", th.StringType, description="Status description")
        ), description="Campaign status"),
        th.Property("created_at", th.DateTimeType, description="Creation timestamp"),
        th.Property("updated_at", th.DateTimeType, description="Last update timestamp"),
        th.Property("run_id", th.IntegerType, description="Extraction run ID"),
    ).to_dict()

    def get_new_paginator(self) -> BaseAPIPaginator:
        """Create a new pagination helper instance."""
        return StackAdaptPaginator()

    def parse_response(self, response):
        """Parse the response and return an iterator of result records."""
        try:
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            self.logger.error(f"Failed to parse response: {e}")
            self.logger.error(f"Response status: {response.status_code}")
            self.logger.error(f"Response headers: {response.headers}")
            self.logger.error(f"Response text: {response.text[:500]}")  # First 500 chars
            raise

    def post_process(
        self,
        row: dict,
        context: t.Any | None = None,  # noqa: ARG002
    ) -> dict | None:
        """Add run_id to each record."""
        row["run_id"] = RUN_ID
        return row


class AdvertisersStream(StackadaptStream):
    """Advertisers stream for StackAdapt."""

    name = "advertisers"
    path = "/advertisers"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None
    
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, description="Advertiser ID"),
        th.Property("name", th.StringType, description="Advertiser name"),
        th.Property("status", th.ObjectType(
            th.Property("code", th.StringType, description="Status code"),
            th.Property("description", th.StringType, description="Status description")
        ), description="Advertiser status"),
        th.Property("created_at", th.DateTimeType, description="Creation timestamp"),
        th.Property("updated_at", th.DateTimeType, description="Last update timestamp"),
        th.Property("run_id", th.IntegerType, description="Extraction run ID"),
    ).to_dict()

    def get_new_paginator(self) -> BaseAPIPaginator:
        """Create a new pagination helper instance."""
        return StackAdaptPaginator()

    def parse_response(self, response):
        """Parse the response and return an iterator of result records."""
        try:
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            self.logger.error(f"Failed to parse response: {e}")
            self.logger.error(f"Response status: {response.status_code}")
            self.logger.error(f"Response headers: {response.headers}")
            self.logger.error(f"Response text: {response.text[:500]}")  # First 500 chars
            raise

    def post_process(
        self,
        row: dict,
        context: t.Any | None = None,  # noqa: ARG002
    ) -> dict | None:
        """Add run_id to each record."""
        row["run_id"] = RUN_ID
        return row


class CampaignDeviceStatsStream(StackadaptStream):
    """Campaign device statistics stream for StackAdapt."""

    name = "campaign_device_stats"
    path = "/insights"
    primary_keys: t.ClassVar[list[str]] = ["campaign_id", "date", "devicetype"]
    replication_key = "date"  # Restore replication key since we're adding date
    
    schema = th.PropertiesList(
        # Primary keys
        th.Property("campaign_id", th.IntegerType, description="Campaign ID"),
        th.Property("date", th.DateType, description="Date of the statistics"),
        th.Property("devicetype", th.StringType, description="Device type"),
        
        # Campaign context
        th.Property("campaign", th.StringType, description="Campaign name"),
        th.Property("campaign_type", th.StringType, description="Campaign type"),
        th.Property("line_item", th.StringType, description="Line item name"),
        th.Property("sub_advertiser", th.StringType, description="Sub-advertiser"),
        th.Property("campaign_custom_fields", th.ArrayType(th.StringType()), description="Campaign custom fields"),
        
        # Basic metrics
        th.Property("imp", th.IntegerType, description="Impressions"),
        th.Property("click", th.IntegerType, description="Clicks"),
        th.Property("cost", th.NumberType, description="Cost"),
        th.Property("revenue", th.NumberType, description="Revenue"),
        
        # Conversion metrics
        th.Property("conv", th.IntegerType, description="Conversions"),
        th.Property("conv_click", th.IntegerType, description="Click-through conversions"),
        th.Property("conv_imp_derived", th.IntegerType, description="Impression-derived conversions"),
        th.Property("conv_rev", th.NumberType, description="Conversion revenue"),
        th.Property("conv_cookie", th.IntegerType, description="Cookie-based conversions"),
        th.Property("conv_ip", th.IntegerType, description="IP-based conversions"),
        th.Property("s_conv", th.IntegerType, description="Server-side conversions"),
        
        # Time metrics
        th.Property("conv_click_time_avg", th.NumberType, description="Average click-to-conversion time"),
        th.Property("conv_imp_time_avg", th.NumberType, description="Average impression-to-conversion time"),
        th.Property("time_on_site", th.IntegerType, description="Time on site"),
        th.Property("page_time", th.IntegerType, description="Page time"),
        th.Property("page_time_15_s", th.IntegerType, description="15-second page views"),
        th.Property("atos", th.NumberType, description="Average time on site"),
        
        # Engagement metrics
        th.Property("period_unique_ip", th.IntegerType, description="Period unique IPs"),
        th.Property("page_start", th.IntegerType, description="Page starts"),
        
        # View completion metrics
        th.Property("vcomp_0", th.IntegerType, description="0% view completions"),
        th.Property("vcomp_25", th.IntegerType, description="25% view completions"),
        th.Property("vcomp_50", th.IntegerType, description="50% view completions"),
        th.Property("vcomp_75", th.IntegerType, description="75% view completions"),
        th.Property("vcomp_95", th.IntegerType, description="95% view completions"),
        th.Property("vcomp_rate", th.NumberType, description="View completion rate"),
        th.Property("view_percent", th.NumberType, description="View percentage"),
        
        # Audio completion metrics
        th.Property("acomp_0", th.IntegerType, description="0% audio completions"),
        th.Property("acomp_25", th.IntegerType, description="25% audio completions"),
        th.Property("acomp_50", th.IntegerType, description="50% audio completions"),
        th.Property("acomp_75", th.IntegerType, description="75% audio completions"),
        th.Property("acomp_95", th.IntegerType, description="95% audio completions"),
        
        # Calculated metrics
        th.Property("ctr", th.NumberType, description="Click-through rate"),
        th.Property("cvr", th.NumberType, description="Conversion rate"),
        th.Property("click_cvr", th.NumberType, description="Click conversion rate"),
        th.Property("imp_cvr", th.NumberType, description="Impression conversion rate"),
        th.Property("ecpa", th.NumberType, description="Effective cost per acquisition"),
        th.Property("ecpc", th.NumberType, description="Effective cost per click"),
        th.Property("ecpe", th.NumberType, description="Effective cost per engagement"),
        th.Property("ecpm", th.NumberType, description="Effective cost per mille"),
        th.Property("ecpv", th.NumberType, description="Effective cost per view"),
        th.Property("engage_rate", th.NumberType, description="Engagement rate"),
        th.Property("run_id", th.IntegerType, description="Extraction run ID"),
    ).to_dict()

    def get_url_params(
        self,
        context: t.Any | None,
        next_page_token: t.Any | None,
    ) -> dict[str, t.Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params = {}
        
        if context and context.get("campaign_id") and context.get("start_date") and context.get("end_date"):
            params.update({
                "resource_type": "campaign",
                "type": "devices",
                "id": context["campaign_id"],
                "date_range_type": "custom",
                "start_date": context["start_date"],
                "end_date": context["end_date"]
            })
        
        return params

    def get_records(self, context: t.Any | None) -> t.Iterable[dict[str, t.Any]]:
        """Get records from the stream."""
        # First, get all campaigns
        campaigns_stream = CampaignsStream(self._tap)
        
        # Get chunk days from config (default to 1 for daily granularity)
        chunk_days = self.config.get("chunk_days", 1)
        
        # Get lookback days from config (default to 30 days)
        lookback_days = self.config.get("lookback_days", 30)
        
        # Get start date from config or use lookback window
        start_date_str = self.config.get("start_date")
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            # Convert to timezone-naive datetime
            if start_date.tzinfo:
                start_date = start_date.replace(tzinfo=None)
        else:
            # Use lookback window if no start_date provided
            start_date = datetime.now().replace(tzinfo=None) - timedelta(days=lookback_days)
        
        end_date = datetime.now().replace(tzinfo=None)
        
        # Generate date chunks
        current_date = start_date
        while current_date <= end_date:
            chunk_end_date = min(current_date + timedelta(days=chunk_days - 1), end_date)
            
            # For each campaign, fetch device stats for this date range
            for campaign in campaigns_stream.get_records(context):
                campaign_id = campaign.get("id")
                if not campaign_id:
                    continue
                
                # Create context for this campaign and date range
                campaign_context = {
                    "campaign_id": campaign_id,
                    "start_date": current_date.strftime("%Y-%m-%d"),
                    "end_date": chunk_end_date.strftime("%Y-%m-%d"),
                }
                
                # Fetch device stats for this campaign and date range
                try:
                    # Get authentication headers
                    auth_headers = self.authenticator.auth_headers or {}
                    
                    # Merge with other headers
                    headers = {**self.http_headers, **auth_headers}
                    
                    response = self.requests_session.get(
                        self.get_url(context=campaign_context),
                        headers=headers,
                        params=self.get_url_params(campaign_context, None),
                    )
                    response.raise_for_status()
                    
                    stats_data = response.json().get("stats", [])
                    
                    # Process each day's stats
                    for day_stats in stats_data:
                        # Add campaign context to each record
                        day_stats["campaign_id"] = campaign_id
                        day_stats["campaign"] = campaign.get("name", "")
                        
                        # Add the date from our query context since API doesn't provide it
                        day_stats["date"] = current_date.strftime("%Y-%m-%d")
                        
                        yield day_stats
                        
                except Exception as e:
                    self.logger.warning(f"Error fetching stats for campaign {campaign_id}: {e}")
                    continue
            
            # Move to next chunk
            current_date = chunk_end_date + timedelta(days=1)

    def post_process(
        self,
        row: dict,
        context: t.Any | None = None,  # noqa: ARG002
    ) -> dict | None:
        """Add run_id to each record."""
        row["run_id"] = RUN_ID
        return row
