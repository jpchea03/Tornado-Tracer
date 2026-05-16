# Title: pipeline.py
# Description: A pipeline for downloading, processing, and plotting NEXRAD data.
# Author: Joseph Cheatham

import nexradaws
import pyart
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature
import numpy as np
import os
import tempfile
import pytz
from datetime import datetime, timedelta
import shutil

# Connect and query AWS
def connect_and_query(start, end, radar_id):
    print("Connecting to AWS...")
    conn = nexradaws.NexradAwsInterface()
    scans = conn.get_avail_scans_in_range(start, end, radar_id)
    print(f"Found {len(scans)} scans in window.")
    templocation  = tempfile.mkdtemp()
    return conn, scans, templocation

# Download and process a scan
def process_scan(scan, conn, templocation, radar_id):
    # Download
    results = conn.download(scan, templocation)
    localfile = results.success[0]
    print(f"Downloaded: {localfile.filepath}")

    # Read
    radar = pyart.io.read_nexrad_archive(localfile.filepath)
    print(f"Loaded {radar.nsweeps} sweeps.")
    print(f"Real data points: {np.sum(~np.ma.getmaskarray(radar.fields['velocity']['data']))}")

    # Gate coordinates
    radar.init_gate_longitude_latitude()
    sweep_slice = radar.get_slice(1)
    gate_lons_s0 = radar.gate_longitude['data'][sweep_slice]
    gate_lats_s0 = radar.gate_latitude['data'][sweep_slice]

    # Extract velocity
    vel_ma = radar.fields['velocity']['data'][sweep_slice]
    vel_s0 = np.where(np.ma.getmaskarray(vel_ma), np.nan, vel_ma.data.astype(float))
    print(f"Non-nan velocity points: {np.sum(~np.isnan(vel_s0))}")

    # Parse scan time
    time_units = radar.time['units']
    base_time_str = time_units.split('since ')[1].rstrip('Z').replace('T', ' ')
    base_time = datetime.strptime(base_time_str, '%Y-%m-%d %H:%M:%S')
    scan_time = base_time + timedelta(seconds=float(radar.time['data'][0]))
    time_str_file  = scan_time.strftime('%Y%m%d_%H%M%S')
    time_str_title = scan_time.strftime('%Y-%m-%d %H:%M:%S UTC')

    # Return processed data
    return {
        'gate_lons_s0': gate_lons_s0,
        'gate_lats_s0': gate_lats_s0,
        'vel_s0': vel_s0,
        'time_str_title': time_str_title,
        'time_str_file': time_str_file,
        'radar_id': radar_id
    }

# Plot the scan
def plot_scan(gate_lons_s0, gate_lats_s0, vel_s0, time_str_title, time_str_file, radar_id):
    fig = plt.figure(figsize=(12, 9))
    ax = plt.subplot(111, projection=ccrs.PlateCarree())
    ax.set_extent([-95.2, -93.8, 36.7, 37.7], crs=ccrs.PlateCarree())

    mesh = ax.pcolormesh(
        gate_lons_s0, gate_lats_s0, vel_s0,
        cmap='RdBu_r', vmin=-33.5, vmax=33.5,
        transform=ccrs.PlateCarree(),
        shading='auto'
    )

    plt.colorbar(mesh, ax=ax, label='Radial Velocity (m/s)')
    ax.add_feature(cfeature.STATES, linewidth=0.8)
    counties = NaturalEarthFeature(
        category='cultural', name='admin_2_counties',
        scale='10m', facecolor='none'
    )
    ax.add_feature(counties, linewidth=0.3, alpha=0.5)
    ax.gridlines(draw_labels=True, linewidth=0.3, alpha=0.5)
    plt.title(f'{radar_id} Velocity - {time_str_title}')

    os.makedirs('plots', exist_ok=True)
    plt.tight_layout()
    plt.savefig(f'plots/{radar_id}_{time_str_file}.png', dpi=150)
    plt.close()
    print(f"Saved plots/{radar_id}_{time_str_file}.png")

# Download, process, and plot all scans in the window
def run_pipeline(start, end, radar_id):
    print("-Tornado Tracer-")
    conn, scans, templocation = connect_and_query(start, end, radar_id)
    for i in range(len(scans)):
        target_scan = scans[i]
        print(f"\n[Scan {i+1}/{len(scans)}]")
        data = process_scan(target_scan, conn, templocation, radar_id)
        plot_scan(**data)
    shutil.rmtree(templocation)
    print("\nCleaned up temporary files.")
    print("Done. Have a nice day!")
        