"""Envelope utilities used for Rayleigh-wave arrival estimation."""

import glob
import os.path
from typing import Iterable, Sequence

import numpy as np
import obspy as op
from obspy import UTCDateTime
from obspy.signal.filter import envelope

from ..download.otf import process_otf
import pandas as pd


def enveloper(tr: op.Trace, time: UTCDateTime) -> tuple[np.ndarray, op.Trace]:
    """Return the envelope of ``tr`` around ``time``."""

    t_beg = time - 10
    t_end = time + 30
    tr.trim(starttime=t_beg, endtime=t_end)
    return envelope(tr.data), tr


def envelope_max_time(env: Sequence[float], tr: op.Trace) -> float:
    """Return the relative time of the maximum in ``env``."""

    idx = int(np.argmax(env))
    return float(tr.times()[idx])


def pick_parser(pick_file: str, fs: float = 50.0) -> list[UTCDateTime]:
    """
    Parse a STA/LTA pick file into a list of ``UTCDateTime`` objects.
    """
    date = os.path.dirname(pick_file).split("/")[-1]
    # Turn YYYYMMDD string into a UTCDateTime object
    year = int(date[0:4])
    mon = int(date[4:6])
    day = int(date[6:8])
    date = UTCDateTime(year, mon, day)

    # Read the pick file
    df = pd.read_csv(pick_file, header=None, names=["onset_beg", "onset_end"])

    # Convert the time strings to UTCDateTime objects
    df["onset_beg_UTCDateTime"] = df["onset_beg"].apply(lambda x: date + x / fs)

    # turn the UTCDateTime column into a list to return
    picks = df["onset_beg_UTCDateTime"].tolist()
    return picks


def stalta_picks_to_rayleigh_times(
    date_path: str,
    fs: float = 50.0,
    pre_filt: Iterable[float] | None = None,
) -> None:
    """
    Convert STA/LTA pick files into Rayleigh-wave arrival time CSV files.
    """
    if pre_filt is None:
        pre_filt = [4, 5, 20, 22]
    date = os.path.basename(date_path)

    output_path = "outputs/rayleigh_times/"

    # Get the list of pick files in the date directory
    pick_files = glob.glob(date_path + "/*.csv")
    for pick_file in pick_files:  # each pick file corresponds to one station
        # Get the station name from the pick file
        sta = os.path.basename(pick_file).split(".")[0]
        # Get the picks from the pick file
        picks = pick_parser(pick_file, fs)
        # Get the stream for the station
        tr = op.read(f"outputs/raw_data_cache/{date}/XH_{sta}/HHZ.mseed")[0]
        tr = process_otf(tr, fs=fs, pre_filt=pre_filt)
        # Get the Rayleigh wave arrival times
        rayleigh_times = []
        for pick in picks:
            tr_working = tr.copy()
            envelope, tr_working = enveloper(tr_working, pick)
            time = envelope_max_time(envelope, tr_working)
            rayleigh_times.append(pick + time)
        # Write the Rayleigh wave arrival times to a CSV file
        output_file = os.path.join(output_path, f"{date}/{sta}.csv")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            for time in rayleigh_times:
                f.write(f"{time}\n")
    print(f"Rayleigh wave arrival times for {sta} written to {output_file}")


if __name__ == "__main__":
    stalta_picks_to_rayleigh_times()
