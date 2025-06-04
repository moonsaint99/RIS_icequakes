"""Utilities to iterate over raw data and apply detection functions."""

from __future__ import annotations

import glob
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Callable

import obspy as op


# ---------- helpers ----------------------------------------------------------
def _init_pool(user_func: Callable[[op.Trace], None], user_kwargs: dict) -> None:
    """Initialize global variables for the worker pool."""

    global _FUNC, _KWARGS
    _FUNC = user_func
    _KWARGS = user_kwargs


def _worker(trace_path: str) -> None:
    """Worker function executed in subprocesses."""

    tr = op.read(trace_path)[0]  # load inside worker
    _FUNC(tr, **_KWARGS)


# ---------- core API ---------------------------------------------------------
def get_all_traces(data_dir: str = "outputs/raw_data_cache") -> list[str]:
    """Return a list of all vertical component traces."""

    return glob.glob(os.path.join(data_dir, "**", "*Z.mseed"), recursive=True)


def get_incomplete_traces(
    data_dir: str = "outputs/raw_data_cache",
    result_dir: str = "outputs/stalta_detections/",
) -> list[str]:
    """Return traces lacking detection results."""

    all_traces = get_all_traces(data_dir)
    incomplete_traces: list[str] = []
    for trace_path in all_traces:
        sta = os.path.basename(os.path.dirname(trace_path)).split("_")[1]
        date = os.path.basename(os.path.dirname(os.path.dirname(trace_path)))
        out_file = os.path.join(result_dir, f"{date}/{sta}.csv")
        if not os.path.exists(out_file):
            incomplete_traces.append(trace_path)
    return incomplete_traces


def iterate_serial(
    func: Callable[[op.Trace], None], data_dir: str = "outputs/raw_data_cache", **kwargs
) -> None:
    """Apply ``func`` to every trace sequentially."""

    for p in get_all_traces(data_dir):
        func(op.read(p)[0], **kwargs)


def iterate_parallel(
    func: Callable[[op.Trace], None], data_dir: str = "outputs/raw_data_cache", **kwargs
) -> None:
    """Apply ``func`` to every trace in parallel."""

    paths = get_all_traces(data_dir)
    with ProcessPoolExecutor(
        max_workers=os.cpu_count(), initializer=_init_pool, initargs=(func, kwargs)
    ) as ex:
        # force evaluation; chunks of 16 keeps fork/exec overhead low
        list(ex.map(_worker, paths, chunksize=16))


def iterate_all(
    func: Callable[[op.Trace], None], mode: str = "serial", **kwargs
) -> None:
    """Convenience wrapper to dispatch to serial or parallel iterators."""

    if mode == "parallel":
        iterate_parallel(func, **kwargs)
    elif mode == "serial":
        iterate_serial(func, **kwargs)
    else:
        raise ValueError("mode must be 'serial' or 'parallel'")


# ---------- example ----------------------------------------------------------
def demo(trace: op.Trace, scale: float = 1.0) -> None:
    """Example processing function used in the module demo."""

    trace.data *= scale  # stand-in for real work


if __name__ == "__main__":  # required on spawn-based OSes
    iterate_all(demo, mode="parallel", scale=2.0)
