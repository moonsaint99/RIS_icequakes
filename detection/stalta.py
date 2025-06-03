import os, numpy as np, obspy as op
from download.otf import process_otf
from obspy.signal.trigger import classic_sta_lta, plot_trigger, trigger_onset

def detect_stalta(tr: op.Trace, output_dir="outputs/stalta_detections/"):
    date = tr.stats.starttime.strftime("%Y%m%d")
    sta  = tr.stats.station
    out_file = os.path.join(output_dir, f"{date}/{sta}.csv")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    tr = process_otf(tr, fs=50, pre_filt=[4, 5, 20, 22])
    try:
        cft = classic_sta_lta(tr.data,
                                int(2 * tr.stats.sampling_rate),
                                int(60 * tr.stats.sampling_rate))
    except ValueError as e:
        print(f"Error processing {tr.id}: {e}")
        return None
    # plot_trigger(tr, cft, 10, 8)
    onsets = trigger_onset(cft, 11, 8, 10)
    np.savetxt(out_file, onsets, delimiter=",")
    return onsets

def detect_stalta_fromtracepath(trace_path):
    tr = op.read(trace_path)[0]
    return detect_stalta(tr)

