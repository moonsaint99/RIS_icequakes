# In this file, we'll make a function that takes in a detection time,
# and it'll look at the seismogram 10 seconds before and 30 seconds
# after. It'll draw an envelope around the seismogram, and then find the
# maximum amplitude in that window. This will be the Rayleigh wave
# arrival time.
import obspy as op
from obspy import UTCDateTime
from obspy.signal.filter import envelope
from download.otf import process_otf
import numpy as np

def enveloper(st = op.Stream, time = UTCDateTime, fs = 50, pre_filt=None):
    """
    Given a stream and a time (in samples), this function will
    compute the envelope of the stream and find the maximum
    amplitude in a window around the time. The window is 10
    seconds before and 30 seconds after the time.
    :param st: Stream object containing the seismogram data.
    :param time: UTCDateTime of detection
    :return: Time in samples of the maximum amplitude in the envelope
    """
    if pre_filt is None:
        pre_filt = [4, 5, 20, 22]
    tr = st[0]
    t_beg = time - 10
    t_end = time + 30
    tr.trim(starttime=t_beg, endtime=t_end)
    tr = process_otf(tr, fs, pre_filt)
    return envelope(tr.data), tr

def envelope_max_time(envelope, tr = op.Trace):
    """
    Finds the time of the maximum in an envelope made using enveloper
    :param envelope: output from enveloper
    :param tr:  also output from enveloper
    :return: UTCDateTime of Rayleigh wave arrival time
    """
    idx = np.argmax(envelope)
    time = tr.times[idx]
    return time
