"""Helper functions for retrieving station metadata."""

from __future__ import annotations

from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.core.inventory import Inventory, read_inventory


def get_sta_inv_online(sta: str, net: str = "XH") -> Inventory:
    """Download station metadata from IRIS."""

    client = Client("IRIS")
    return client.get_stations(
        network=net,
        station=sta,
        starttime=UTCDateTime(2014, 11, 28),
        endtime=UTCDateTime(2014, 12, 15),
        level="response",
    )


def get_sta_inv_offline(sta: str, net: str = "XH") -> Inventory:
    """Load cached station metadata from disk."""

    return read_inventory(
        f"outputs/stations/{net}.{sta}.xml", format="STATIONXML", level="response"
    )
