import glob, os
from concurrent.futures import ProcessPoolExecutor
import obspy as op

# ---------- helpers ----------------------------------------------------------
def _init_pool(user_func, user_kwargs):
    global _FUNC, _KWARGS
    _FUNC   = user_func
    _KWARGS = user_kwargs

def _worker(trace_path):
    tr = op.read(trace_path)[0]     # load inside worker
    _FUNC(tr, **_KWARGS)

# ---------- core API ---------------------------------------------------------
def get_all_traces(data_dir='outputs/raw_data_cache'):
    return glob.glob(os.path.join(data_dir, '**', '*Z.mseed'), recursive=True)

def get_incomplete_traces(data_dir='outputs/raw_data_cache', result_dir='outputs/stalta_detections/'):
    all_traces = get_all_traces(data_dir)
    incomplete_traces = []
    for trace_path in all_traces:
        sta = os.path.basename(os.path.dirname(trace_path)).split('_')[1]
        date  = os.path.basename(os.path.dirname(os.path.dirname(trace_path)))
        out_file = os.path.join(result_dir, f"{date}/{sta}.csv")
        if not os.path.exists(out_file):
            incomplete_traces.append(trace_path)
    return incomplete_traces

def iterate_serial(func, data_dir='outputs/raw_data_cache', **kwargs):
    for p in get_all_traces(data_dir):
        func(op.read(p)[0], **kwargs)

def iterate_parallel(func, data_dir='outputs/raw_data_cache', **kwargs):
    paths = get_all_traces(data_dir)
    with ProcessPoolExecutor(
            max_workers=os.cpu_count(),
            initializer=_init_pool,
            initargs=(func, kwargs)) as ex:
        # force evaluation; chunks of 16 keeps fork/exec overhead low
        list(ex.map(_worker, paths, chunksize=16))

def iterate_all(func, mode='serial', **kwargs):
    if mode == 'parallel':
        iterate_parallel(func, **kwargs)
    elif mode == 'serial':
        iterate_serial(func, **kwargs)
    else:
        raise ValueError("mode must be 'serial' or 'parallel'")

# ---------- example ----------------------------------------------------------
def demo(trace, scale=1.0):
    trace.data *= scale           # stand-in for real work

if __name__ == "__main__":        # required on spawn-based OSes
    iterate_all(demo, mode='parallel', scale=2.0)