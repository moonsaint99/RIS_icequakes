import obspy as op
from obspy import UTCDateTime
from obspy.clients.fdsn import Client

def get_sta_inv(sta: str, net: str = 'XH'):
    client = Client("IRIS")
    inv = client.get_stations(
        network = net,
        station = sta,
        starttime = UTCDateTime(2014,11,28),
        endtime = UTCDateTime(2014,12,15),
        level = 'response'
    )
    return inv