"""Tap for Stackadapt."""

import time

# Generate run_id as Unix timestamp at tap startup
RUN_ID = int(time.time())

from tap_stackadapt.streams import (
    CampaignsStream,
    AdvertisersStream,
    CampaignDeviceStatsStream,
    CampaignDeliveryStatsStream,
    CampaignConversionTrackerDeliveryStatsStream,
)

__all__ = [
    "CampaignsStream",
    "AdvertisersStream", 
    "CampaignDeviceStatsStream",
    "CampaignDeliveryStatsStream",
    "CampaignConversionTrackerDeliveryStatsStream",
]
