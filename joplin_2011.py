# Title: joplin_2011.py
# Description: Downloading and plotting NEXRAD scans from the May 22, 2011 Joplin, MO tornado.
# Author: Joseph Cheatham
# Last Updated: 5/10/2026
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

print("--Tornado Tracer--")

# Connect and query AWS
print("Connecting to AWS...")
conn = nexradaws.NexradAwsInterface()
start = datetime(2011, 5, 22, 22, 30, tzinfo=pytz.UTC)
end   = datetime(2011, 5, 22, 23, 15, tzinfo=pytz.UTC)
scans = conn.get_avail_scans_in_range(start, end, 'KSGF')
print(f"Found {len(scans)} scans in window.")

total_scans = len(scans)
templocation = tempfile.mkdtemp()

for i in range(total_scans):
    print(f"\n[Scan {i+1}/{total_scans}]")
    target_scan = scans[i]

    # Download
    results = conn.download(target_scan, templocation)
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

    # Plot
    print(f"Plotting {time_str_title}...")
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
    plt.title(f'KSGF Velocity - {time_str_title}')

    os.makedirs('plots', exist_ok=True)
    plt.tight_layout()
    plt.savefig(f'plots/KSGF_{time_str_file}.png', dpi=150)
    plt.close()
    print(f"Saved plots/KSGF_{time_str_file}.png")

print("\nDone. Have a nice day!")