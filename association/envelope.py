# In this file, we'll make a function that takes in a detection time,
# and it'll look at the seismogram 10 seconds before and 30 seconds
# after. It'll draw an envelope around the seismogram, and then find the
# maximum amplitude in that window. This will be the Rayleigh wave
# arrival time.
import os.path
import glob

import obspy as op
from obspy import UTCDateTime
from obspy.signal.filter import envelope
from download.otf import process_otf
import numpy as np
import pandas as pd

def enveloper(tr = op.Trace, time = UTCDateTime):
    """
    Given a stream and a time (in samples), this function will
    compute the envelope of the stream and find the maximum
    amplitude in a window around the time. The window is 10
    seconds before and 30 seconds after the time.
    :param st: Pre-filtered stream object containing the seismogram data.
    :param time: UTCDateTime of detection
    :return: Time in samples of the maximum amplitude in the envelope
    """
    t_beg = time - 10
    t_end = time + 30
    tr.trim(starttime=t_beg, endtime=t_end)
    return envelope(tr.data), tr

def envelope_max_time(envelope, tr = op.Trace):
    """
    Finds the time of the maximum in an envelope made using enveloper
    :param envelope: output from enveloper
    :param tr:  also output from enveloper
    :return: UTCDateTime of Rayleigh wave arrival time
    """
    idx = np.argmax(envelope)
    time = tr.times()[idx]
    return time

def pick_parser(pick_file: str = '/Users/rishi/seis/RIS_icequakes/outputs/stalta_detections/20150115/DR14.csv', fs = 50.):
    """
    Parses a pick file and returns the time of the pick as a list of UTCDateTime objects
    :param pick_file: path to the pick file
    :param fs: sampling frequency of the data
    :return: list of UTCDateTimes of the picks
    """
    date = os.path.dirname(pick_file).split('/')[-1]
    # Turn YYYYMMDD string into a UTCDateTime object
    year = int(date[0:4])
    mon = int(date[4:6])
    day = int(date[6:8])
    date = UTCDateTime(year, mon, day)

    # Read the pick file
    df = pd.read_csv(pick_file, header=None, names=['onset_beg', 'onset_end'])

    # Convert the time strings to UTCDateTime objects
    df['onset_beg_UTCDateTime'] = df['onset_beg'].apply(lambda x: date + x/fs)

    # turn the UTCDateTime column into a list to return
    picks = df['onset_beg_UTCDateTime'].tolist()
    return picks

def stalta_picks_to_rayleigh_times(date_path = '/Users/rishi/seis/RIS_icequakes/outputs/stalta_detections/20150115', fs = 50., pre_filt=None):
    """
    Given a date path, this function will read the pick files and produce a CSV of Rayleigh wave arrival times
    :param date_path: path to the date directory
    :param fs: sampling frequency of the data
    :return: list of UTCDateTime objects of the Rayleigh wave arrival times
    """
    if pre_filt is None:
        pre_filt = [4, 5, 20, 22]
    date = os.path.basename(date_path)

    output_path = 'outputs/rayleigh_times/'

    # Get the list of pick files in the date directory
    pick_files = glob.glob(date_path + '/*.csv')
    for pick_file in pick_files: # Each pick file is for a given station's picks for a given day
        # Get the station name from the pick file
        sta = os.path.basename(pick_file).split('.')[0]
        # Get the picks from the pick file
        picks = pick_parser(pick_file, fs)
        # Get the stream for the station
        tr = op.read(f'outputs/raw_data_cache/{date}/XH_{sta}/HHZ.mseed')[0]
        tr = process_otf(tr, fs=fs, pre_filt=pre_filt)
        # Get the Rayleigh wave arrival times
        rayleigh_times = []
        for pick in picks:
            tr_working = tr.copy()
            envelope, tr_working = enveloper(tr_working, pick)
            time = envelope_max_time(envelope, tr_working)
            rayleigh_times.append(pick+time)
        # Write the Rayleigh wave arrival times to a CSV file
        output_file = os.path.join(output_path, f'{date}/{sta}.csv')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            for time in rayleigh_times:
                f.write(f'{time}\n')
    print(f'Rayleigh wave arrival times for {sta} written to {output_file}')

stalta_picks_to_rayleigh_times()