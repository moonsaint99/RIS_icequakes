"""Association routines for grouping Rayleigh-wave arrivals."""

from __future__ import annotations

import glob
import os
from typing import List

import pandas as pd
from ..download.sta_inv import get_sta_inv_offline


def assoc_day_rayleigh(date_path: str) -> List[List[List]]:
    """Cluster Rayleigh-wave arrival times recorded on a single day."""

    rayleigh_velocity = 1.55  # km/s, from Olinger et al., 2019

    sta_path_list = glob.glob(f"{date_path}/*.csv")
    sta_path_dict: dict[str, str] = {}
    sta_list: list[str] = []
    for sta_path in sta_path_list:
        sta = os.path.basename(sta_path).split(".")[0]
        sta_list.append(sta)
        sta_path_dict[sta] = sta_path

    rayleigh_arrival_list: list[list] = []

    for sta in sta_list:
        sta_path = sta_path_dict[sta]
        # Read the stationXML file to get the coordinates of the station
        inv = get_sta_inv_offline(sta)
        sta_coords = inv.get_coordinates(f"XH.{sta}..HHZ")

        # Each line in these CSV files is a UTCDateTime for when a Rayleigh wave arrived.
        with open(sta_path, "r") as f:
            for line in f:
                utc_time = line.strip()
                rayleigh_arrival_list.append(
                    [sta, utc_time, sta_coords["latitude"], sta_coords["longitude"]]
                )
    # Convert the list to a DataFrame
    df = pd.DataFrame(
        rayleigh_arrival_list, columns=["station", "utc_time", "latitude", "longitude"]
    )
    # De-duplicate the DataFrame
    df = df.drop_duplicates(subset=["station", "utc_time"])
    # Sort the DataFrame by time
    df["utc_time"] = pd.to_datetime(df["utc_time"])
    df = df.sort_values(by="utc_time")

    # Association using a simple sliding‑window cluster algorithm
    max_seismicity_range = 100  # km
    min_cluster_size = 3
    min_cluster_stations = 3
    window_sec = max_seismicity_range / rayleigh_velocity  # seconds

    df = df.reset_index(drop=True)
    clusters: list[list[list]] = []
    i = 0
    N = len(df)

    while i < N:
        j = i + 1
        t0 = df.at[i, "utc_time"]
        # grow window while picks fall within the fixed travel‑time window
        while j < N and (df.at[j, "utc_time"] - t0).total_seconds() <= window_sec:
            j += 1

        cluster_df = df.iloc[i:j]
        unique_stations = cluster_df["station"].nunique()

        if (
            len(cluster_df) >= min_cluster_size
            and unique_stations >= min_cluster_stations
        ):
            # convert to old pick format: [station, arrival_time, confidence, phase, date]
            date_str = os.path.basename(os.path.normpath(date_path))
            date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
            cluster = [
                [row.station, row.utc_time.to_pydatetime(), 1.0, "R", date_str]
                for row in cluster_df.itertuples()
            ]
            # If stations occur more than once, take the first occurrence
            seen_stations: set[str] = set()
            cluster = [
                pick
                for pick in cluster
                if pick[0] not in seen_stations and not seen_stations.add(pick[0])
            ]
            clusters.append(cluster)

        i = j

    return clusters


if __name__ == "__main__":
    print(assoc_day_rayleigh("outputs/rayleigh_times/20150615"))
