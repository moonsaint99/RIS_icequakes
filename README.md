# Ross Ice Shelf Icequakes

This repository collects small utilities used to download seismic data from Ross Ice Shelf stations, detect potential icequakes, convert detections to Rayleigh arrivals and cluster those arrivals into events.  Several Jupyter notebooks are included in the project root to illustrate an end-to-end workflow.

## Repository layout

```
ris_icequakes/ - core Python package
   __init__.py          package metadata
   association/         envelope picking and arrival clustering
      assoc.py          routines for grouping Rayleigh-wave picks by day
      envelope.py       utilities to convert STA/LTA picks to envelope maxima
   detection/           simple STA/LTA detection tools
      stalta.py         classic STA/LTA trigger on a trace
      iterator.py       iterate over cached data in serial or parallel
   download/            waveform download and preprocessing helpers
      bulk_dl.py        FDSN mass downloader script
      otf.py            basic on-the-fly preprocessing
      sta_inv.py        fetch or read station metadata
   location/            placeholder event location routines
      locator_rayleigh.py  skeleton for locating with Rayleigh arrivals

main.py      - minimal command line entry point
```

The notebooks demonstrate how to chain these modules together.  For example, `data_download.ipynb` shows how to retrieve raw data into `outputs/raw_data_cache/` while `detect.ipynb` converts those waveforms to STA/LTA detections.  `associate.ipynb` then clusters Rayleigh arrival times produced by `ris_icequakes/association/`.

## Package overview

### download
- **bulk_dl.py** – uses `obspy`'s `MassDownloader` to fetch miniSEED and station XML.  The helper functions name files so repeated runs skip previously downloaded data.
- **otf.py** – applies interpolation and instrument response removal as a convenience wrapper for preprocessing.
- **sta_inv.py** – loads cached station metadata or requests it from IRIS when needed.

### ris_icequakes.detection
- **stalta.py** – runs the classic STA/LTA algorithm on an `obspy.Trace`, writing onset indices to CSV for later processing.
- **iterator.py** – provides serial and parallel iterators over the cached waveform directory, suitable for applying any user supplied processing function.

### ris_icequakes.association
- **envelope.py** – converts STA/LTA onset files into envelope peaks surrounding each detection to estimate Rayleigh arrival times.
- **assoc.py** – groups arrival times within a fixed window using a sliding cluster algorithm and returns cluster lists for later location steps.

### ris_icequakes.location
- **locator_rayleigh.py** – stub routines for eventually inverting clustered Rayleigh arrivals for a source position.  Currently only defined for future expansion.

### Other files
- **main.py** – simple demo entry point printing a greeting.

## Getting started

The project requires Python 3.12 and depends largely on `obspy` and `pandas`.  Install the package locally using

```
pip install -e .
```

Refer to the notebooks for an example workflow using the packaged utilities.
