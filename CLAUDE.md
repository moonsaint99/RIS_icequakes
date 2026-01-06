# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RIS Icequakes is a Python package for processing seismic data from Ross Ice Shelf stations to detect, locate, and cluster icequakes. The workflow follows a pipeline: download raw data → preprocess → detect events → associate arrivals → locate sources.

## Development Commands

```bash
# Install package in development mode
pip install -e .

# Run Jupyter notebooks (primary development interface)
jupyter notebook

# Package uses uv for dependency management
uv sync  # Install dependencies from lock file
```

No formal test suite or linting configuration exists yet.

## Architecture

### Data Processing Pipeline

```
FDSN servers → bulk_dl.py → raw miniSEED files
                    ↓
              otf.py (preprocess: interpolate to 50Hz, detrend, remove response, bandpass 4-22Hz)
                    ↓
              stalta.py (STA/LTA detection, 2s/60s windows)
                    ↓
              envelope.py (convert detections to Rayleigh wave arrivals)
                    ↓
              assoc.py (cluster arrivals within 64s travel-time window)
                    ↓
              locator_rayleigh.py (source location - stub)
```

### Package Structure

- **ris_icequakes/download/**: Data acquisition from FDSN (IRIS, SCEDC, etc.) for XH network stations (DR05-DR14, RS04-RS05)
- **ris_icequakes/detection/**: STA/LTA trigger algorithm with serial/parallel batch processing via `iterator.py`
- **ris_icequakes/association/**: Sliding-window clustering requiring minimum 3 picks from 3 unique stations
- **ris_icequakes/location/**: Placeholder for Rayleigh arrival inversion

### Key Output Directories

- `outputs/raw_data_cache/` - Downloaded miniSEED data
- `outputs/stalta_detections/` - Detection CSV files
- `outputs/rayleigh_times/` - Arrival time estimates
- `outputs/stations/` - StationXML metadata

## Jupyter Notebook Workflows

- `data_download.ipynb` - Bulk data retrieval workflow
- `detect.ipynb` - STA/LTA detection demonstration
- `network_triggering.ipynb` - Multi-station correlation analysis
- `associate.ipynb`, `tides.ipynb` - Placeholders for future workflows

## Key Dependencies

- **ObsPy 1.4.1**: Core seismic data processing
- **pandas 2.2.3**: Data manipulation
- **torch, mlx, pymetal**: ML frameworks (available but not yet utilized in core modules)

## Code Conventions

- Uses `from __future__ import annotations` for forward reference type hints
- Functions designed for reusability with sensible defaults
- Google/NumPy style docstrings
