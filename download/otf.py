# On-the-fly processing of seismic data
import obspy as op
from download.sta_inv import get_sta_inv_offline

def process_otf(tr=op.Trace, fs: float = 50., pre_filt: list = [4, 5, 20, 22]):
    sta = tr.meta.station
    net = tr.meta.network
    tr.interpolate(sampling_rate=fs, method='lanczos', a=20)
    tr.detrend('demean')
    tr.detrend('linear')
    tr.taper(max_percentage=0.00010, max_length=5.)
    inv = get_sta_inv_offline(sta, net)
    tr.remove_response(inventory=inv, pre_filt=pre_filt, output='VEL')
    return tr