"""Stackadapt tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_stackadapt import streams


class TapStackadapt(Tap):
    """Stackadapt tap class."""

    name = "tap-stackadapt"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType(nullable=False),
            required=True,
            secret=True,  # Flag config as protected.
            title="API Key",
            description="The API key to authenticate against StackAdapt API",
        ),
        th.Property(
            "start_date",
            th.DateTimeType(nullable=True),
            description="The earliest record date to sync",
        ),
        th.Property(
            "api_url",
            th.StringType(nullable=False),
            title="API URL",
            default="https://api.stackadapt.com",
            description="The url for the StackAdapt API service",
        ),
        th.Property(
            "chunk_days",
            th.IntegerType(nullable=False),
            title="Chunk Days",
            default=1,
            description="Number of days to chunk device stats queries (default: 1 for daily granularity)",
        ),
        th.Property(
            "lookback_days",
            th.IntegerType(nullable=False),
            title="Lookback Days",
            default=30,
            description="Number of days to look back from current date if no start_date is provided",
        ),
        th.Property(
            "user_agent",
            th.StringType(nullable=True),
            description=(
                "A custom User-Agent header to send with each request. Default is "
                "'<tap_name>/<tap_version>'"
            ),
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.StackadaptStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.CampaignsStream(self),
            streams.AdvertisersStream(self),
            streams.CampaignDeviceStatsStream(self),
            streams.CampaignDeliveryStatsStream(self),
            streams.CampaignConversionTrackerDeliveryStatsStream(self),
        ]


if __name__ == "__main__":
    TapStackadapt.cli()
