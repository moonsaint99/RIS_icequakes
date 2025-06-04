"""On-the-fly processing of seismic data."""

from __future__ import annotations

import obspy as op

from .sta_inv import get_sta_inv_offline


def process_otf(
    tr: op.Trace, fs: float = 50.0, pre_filt: list[float] | None = None
) -> op.Trace:
    """Apply basic preprocessing to ``tr``."""

    if pre_filt is None:
        pre_filt = [4, 5, 20, 22]

    sta = tr.meta.station
    net = tr.meta.network
    tr.interpolate(sampling_rate=fs, method="lanczos", a=20)
    tr.detrend("demean")
    tr.detrend("linear")
    tr.taper(max_percentage=0.00010, max_length=5.0)
    inv = get_sta_inv_offline(sta, net)
    tr.remove_response(inventory=inv, pre_filt=pre_filt, output="VEL")
    return tr
