"""Tap for Stackadapt."""

from tap_stackadapt.streams import (
    CampaignsStream,
    AdvertisersStream,
    CampaignDeviceStatsStream,
)

__all__ = [
    "CampaignsStream",
    "AdvertisersStream", 
    "CampaignDeviceStatsStream",
]
