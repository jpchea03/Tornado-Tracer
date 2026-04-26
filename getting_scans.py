# Title: getting_scans.py
# Description: Figuring out how to get and process NEXRAD scans
# Author: Joseph Cheatham

import cartopy
import fsspec
from datetime import datetime as dt
import pyart
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

fs = fsspec.filesystem("s3", anon=True)

# -* KPAH on 4/26/2026 (no tornado) *-
print("**KPAH on 4/26/2026 (no tornado)**")
# Build glob for radar site and time window
site = "KPAH"
date = "2026/04/26"
files = fs.glob(f"s3://unidata-nexrad-level2/{date}/{site}/{site}*_V06")

# Create radar object for first file in list
radar = pyart.io.read_nexrad_archive(f"s3://{files[0]}")
print(" Data obtained: ", radar)

# Dealiasing
vel_corrected = pyart.correct.dealias_region_based(radar)
radar.add_field("dealiased_velocity", vel_corrected, replace_existing=True)

# Plot radial velocity for KPAH on 4/26/2026
print(" Plotting...")
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection=ccrs.PlateCarree())

display = pyart.graph.RadarMapDisplay(radar)
display.plot_ppi_map(
    "dealiased_velocity",
    sweep=1,              
    vmin=-30, vmax=30,  
    colorbar_label="Radial Velocity (m/s)",
    ax=ax,
)
ax.add_feature(cartopy.feature.STATES, linewidth=0.5)
counties = cartopy.feature.NaturalEarthFeature(
    category="cultural",
    name="admin_2_counties",
    scale="10m",
    facecolor="none",
    edgecolor="gray"
)
ax.add_feature(counties, linewidth=0.3, alpha=0.5)

plt.title("KPAH-4/26/2026")
plt.tight_layout()
plt.savefig("plots/KPAH-4-26-2026.png", dpi=150)
print(" Plot saved as: plots/KPAH-4-26-2026.png")



# -* KPAH on 5/27/2024 EF-3 tornado near Dawson Springs KY *-
print("\n**KPAH on 5/27/2024 EF-3 tornado near Dawson Springs KY**")
site = "KPAH"
date_tornado = "2024/05/27"
files_tornado = fs.glob(f"s3://unidata-nexrad-level2/{date_tornado}/{site}/{site}*_V06")

# Tornado was active 00:01-01:15 UTC, peak ~00:30-01:00 UTC
# KPAH20240527_004739_V06 = ~47 min in, tornado near peak through Caldwell/Hopkins
file_tornado = [f for f in files_tornado if "KPAH20240527_004739" in f][0]
radar_tornado = pyart.io.read_nexrad_archive(f"s3://{file_tornado}")
print(" Data obtained: ", radar_tornado)
vel_tornado = pyart.correct.dealias_region_based(radar_tornado)
radar_tornado.add_field("dealiased_velocity", vel_tornado, replace_existing=True)

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection=ccrs.PlateCarree())
display = pyart.graph.RadarMapDisplay(radar_tornado)
display.plot_ppi_map(
    "dealiased_velocity",
    sweep=1,
    vmin=-30, vmax=30,
    colorbar_label="Radial Velocity (m/s)",
    ax=ax,
)
ax.add_feature(cartopy.feature.STATES, linewidth=0.5)
counties = cartopy.feature.NaturalEarthFeature(
    category="cultural",
    name="admin_2_counties",
    scale="10m",
    facecolor="none",
    edgecolor="gray"
)
ax.add_feature(counties, linewidth=0.3, alpha=0.5)
plt.title("KPAH - 2024-05-27 00:47 UTC\nEF-3 Tornado: Lyon → Caldwell → Hopkins Co.")
plt.tight_layout()
plt.savefig("plots/KPAH-2024-05-27-tornado.png", dpi=150)
print(" Plot saved as: plots/KPAH-2024-05-27-tornado.png")