import obspy as op
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.core.inventory import read_inventory

def get_sta_inv_online(sta: str, net: str = 'XH'):
    client = Client("IRIS")
    inv = client.get_stations(
        network = net,
        station = sta,
        starttime = UTCDateTime(2014,11,28),
        endtime = UTCDateTime(2014,12,15),
        level = 'response'
    )
    return inv

def get_sta_inv_offline(sta: str, net: str = 'XH'):
    inv = read_inventory(f'outputs/stations/{net}.{sta}.xml', format='STATIONXML', level='response')
    return inv