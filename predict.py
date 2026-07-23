import numpy as np
from scipy.ndimage import label, maximum_filter

def compute_shear(vel_s0, gate_lons_s0, gate_lats_s0):
    """
    Compute azimuthal shear at each gate (delta_v / delta_distance).
    Returns a 2D array of shear values, same shape as vel_s0.
    """
    ...

def find_couplet_candidates(shear, vel_s0, gate_lons_s0, gate_lats_s0, 
                             shear_threshold=0.01, min_delta_v=20.0):
    """
    Identify candidate TVS regions.
    shear_threshold: minimum shear (m/s/m) to flag a gate
    min_delta_v: minimum velocity difference (m/s) across the couplet
    Returns list of candidate dicts with location and raw metrics.
    """
    ...

def score_candidate(candidate):
    """
    Compute a 0–1 confidence score from:
    - Peak shear magnitude
    - Couplet delta-V
    - Spatial compactness (area of flagged region)
    Returns float confidence.
    """
    ...

def predict(gate_lons_s0, gate_lats_s0, vel_s0):
    """
    Main entry point. Accepts the same fields returned by pipeline.py.
    Returns:
        {
            'lat': float,
            'lon': float,
            'confidence': float (0.0 – 1.0),
            'delta_v': float (m/s),
            'peak_shear': float (m/s/m)
        }
        or None if no credible signature found.
    """
    ...