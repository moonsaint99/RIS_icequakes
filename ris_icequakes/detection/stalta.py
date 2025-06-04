"""Utilities for STA/LTA based event detection."""

from __future__ import annotations

import os
from typing import Iterable

import numpy as np
import obspy as op
from obspy.signal.trigger import classic_sta_lta, trigger_onset

from ..download.otf import process_otf


def detect_stalta(
    tr: op.Trace,
    *,
    output_dir: str = "outputs/stalta_detections/",
    fs: float = 50.0,
    pre_filt: Iterable[float] | None = None,
) -> np.ndarray:
    """Run the STA/LTA detector on a single trace.

    Parameters
    ----------
    tr:
        Input trace.
    output_dir:
        Base directory where detection CSV files are written.
    fs:
        Desired sampling rate after interpolation.
    pre_filt:
        Frequency band for deconvolution. If ``None`` a default band is used.

    Returns
    -------
    ndarray
        Array of onset indices written to ``output_dir``.
    """

    if pre_filt is None:
        pre_filt = [4, 5, 20, 22]

    date = tr.stats.starttime.strftime("%Y%m%d")
    sta = tr.stats.station
    out_file = os.path.join(output_dir, f"{date}/{sta}.csv")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    tr = process_otf(tr, fs=fs, pre_filt=pre_filt)
    try:
        cft = classic_sta_lta(
            tr.data,
            int(2 * tr.stats.sampling_rate),
            int(60 * tr.stats.sampling_rate),
        )
    except ValueError as exc:
        print(f"Error processing {tr.id}: {exc}")
        return np.empty((0, 2), dtype=int)

    onsets = trigger_onset(cft, 11, 8, 10)
    np.savetxt(out_file, onsets, delimiter=",")
    return onsets


def detect_stalta_from_trace_path(trace_path: str) -> np.ndarray:
    """Convenience wrapper to run :func:`detect_stalta` on a file path."""
    tr = op.read(trace_path)[0]
    return detect_stalta(tr)
