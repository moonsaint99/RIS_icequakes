"""Scripts for bulk waveform downloads."""

from __future__ import annotations

import os

import obspy
from obspy.clients.fdsn.mass_downloader import (
    MassDownloader,
    RectangularDomain,
    Restrictions,
)


def download_data(download_path: str = "raw_data_cache") -> None:
    """Download waveform data in daily chunks."""
    domain = RectangularDomain(
        minlatitude=-90, maxlatitude=-70, minlongitude=-180, maxlongitude=180
    )

    restrictions = Restrictions(
        starttime=obspy.UTCDateTime(2014, 11, 28),
        # endtime=obspy.UTCDateTime(2014,12,15),
        endtime=obspy.UTCDateTime(2016, 11, 1),
        chunklength_in_sec=86400,
        network="XH",
        station="DR05,DR06,DR07,DR08,DR09,DR10,DR11,DR12,DR13,DR14,RS04,RS05",
        channel="HH*",
        location="",
        reject_channels_with_gaps=False,
        minimum_length=0.0,
    )

    # Create a helper function to name the filepath for the downloaded data
    def mseed_pathname(network, station, location, channel, starttime, endtime):
        date = starttime.strftime("%Y%m%d")
        return os.path.join(
            download_path, f"{date}/{network}_{station}/{channel}.mseed"
        )

    # Create a helper function to name the downloaded data appropriately
    def get_mseed_storage(network, station, location, channel, starttime, endtime):
        filename = mseed_pathname(
            network, station, location, channel, starttime, endtime
        )
        # Check if the file already exists
        if os.path.exists(filename):
            return True
        else:
            return filename

    mdl = MassDownloader(providers=["IRIS", "SCEDC", "NCEDC", "RESIF", "GFZ"])
    mdl.download(
        domain,
        restrictions,
        mseed_storage=get_mseed_storage,
        stationxml_storage="stations",
        download_chunk_size_in_mb=200,
        threads_per_client=6,
    )
