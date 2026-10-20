# -*- coding: utf-8 -*-
"""Durgaj_OSF_HeatWatchMiami.ipynb

Original file is located at
    https://colab.research.google.com/drive/1SQhJeJZRQIwK0aSGBQFml-zyLOVRGmMD

**Objective:** Replicate temperature maps seen in summary report of [Miami Heat Watch project](https://osf.io/2dtg7/overview). 
Note that plots display *traverse data* collected on June 27, 2020 only. 
Three figures should be produced representing different times of day: 1) morning (6-7 am) 2) afternoon (3-4 pm) 3) evening (7-8 pm)

# Install necessary packages
!pip install -q geopandas matplotlib contextily shapely

"""# Morning Temperature Distribution"""

# Import modules
import os
import zipfile
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np

# Extract data from whole zip file
zip_path = '2dtg7-osfstorage-archive.zip'
extract_dir = 'extracted_data'
os.makedirs(extract_dir, exist_ok=True)

# Unzip main archive
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# Extract nested zip files
zipped_files_found = True
while zipped_files_found:
    zipped_files_found = False
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.zip'):
                nested_zip_path = os.path.join(root, file)
                target_extract_to = os.path.join(root, file[:-4])
                if not os.path.exists(target_extract_to):
                    with zipfile.ZipFile(nested_zip_path, 'r') as nested_ref:
                        nested_ref.extractall(target_extract_to)
                    zipped_files_found = True

# Specifically target the June 27th morning traverse shapefile
selected_shapefile = None
for root, dirs, files in os.walk(extract_dir):
    for file in files:
        if file.endswith('.shp') and '06-27_traverses' in root and 'am_trav' in file:
            selected_shapefile = os.path.join(root, file)
            break
    if selected_shapefile:
        break

if not selected_shapefile:
    # Fallback search if path changes
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.shp') and 'am_trav' in file:
                selected_shapefile = os.path.join(root, file)
                break
        if selected_shapefile:
            break

if not selected_shapefile:
    raise FileNotFoundError("Could not find the June 27th morning traverse shapefile.")

# Load the correct shapefile into a GeoDataFrame
gdf = gpd.read_file(selected_shapefile)

# Sort chronologically
if 'time' in gdf.columns:
    gdf = gdf.sort_values(by='time')

# Search for boundary shapefile to plot 'Model Boundary'
boundary_shapefile = None
for root, dirs, files in os.walk(extract_dir):
    for file in files:
        if file.endswith('.shp') and ('boundary' in file.lower() or 'model' in file.lower() or 'area' in file.lower()):
            boundary_shapefile = os.path.join(root, file)
            break
    if boundary_shapefile:
        break

# Ensure coordinate reference system (CRS) is Web Mercator (EPSG:3857) for the basemap
if gdf.crs != "EPSG:3857":
    gdf = gdf.to_crs(epsg=3857)

# Create the Geospatial Plot 
fig, ax = plt.subplots(1, 1, figsize=(11, 13))

# Explicitly get limits of the data like reference
bounds = gdf.total_bounds
ax.set_xlim(bounds[0] - 200, bounds[2] + 200)
ax.set_ylim(bounds[1] - 200, bounds[3] + 200)

# Exact classification bins from the reference legend
custom_bins = [76.10, 76.82, 77.54, 78.26, 78.98, 80.06, 81.50, 82.58, 83.12]
max_val = gdf['t_f'].max() # max temp from data to cap bins
all_bin_edges = custom_bins + [max_val]
descending_labels = [f"≤ {val:.2f} °F" for val in reversed(all_bin_edges)]

# Print to verify labels look correct
#print("Generated Labels:", descending_labels)

# Plot
gdf.plot(
    column='t_f',
    cmap='coolwarm',      
    scheme='UserDefined',
    classification_kwds={'bins': custom_bins},
    markersize=35,        
    edgecolor='none',      
    legend=True,
    legend_kwds={
        'loc': 'upper left',
        'bbox_to_anchor': (0.05, 0.90),
        'facecolor': 'white',
        'edgecolor': 'darkgray',
        'framealpha': 0.95
    },
    ax=ax,
    zorder=3
)

# Plot the Model Boundary if found
if boundary_shapefile:
    boundary_gdf = gpd.read_file(boundary_shapefile)
    if boundary_gdf.crs != "EPSG:3857":
        boundary_gdf = boundary_gdf.to_crs(epsg=3857)
    boundary_gdf.boundary.plot(ax=ax, color='black', linestyle='--', linewidth=1.5, zorder=2, label='Model Boundary')

# Set desaturated basemap style
ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, zoom=13, alpha=0.45, zorder=1)

# Force grayscale
for child in ax.get_children():
    if isinstance(child, plt.matplotlib.image.AxesImage):
        arr = child.get_array()
        if arr is not None and len(arr.shape) == 3:
            # Apply standard luminosity grayscale formula
            gray = 0.2989 * arr[:, :, 0] + 0.5870 * arr[:, :, 1] + 0.1140 * arr[:, :, 2]
            # Re-tile back to RGB space but desaturated
            for i in range(3):
                arr[:, :, i] = gray
            child.set_data(arr)

# Legend
legend = ax.get_legend()
if legend:
    handles = legend.legend_handles
    reversed_handles=list(handles[::-1]) # reverses to align high temps with warm colors

    # If the boundary was plotted
    if boundary_shapefile:
        from matplotlib.lines import Line2D
        boundary_handle = Line2D([0], [0], color='black', linestyle='--', linewidth=1.5)
        descending_labels = list(descending_labels) + ['Model Boundary']

    ax.legend(
        reversed_handles,
        descending_labels,
        title='Temperature',
        loc='upper left',
        bbox_to_anchor=(0.05, 0.90),
        facecolor='white',
        edgecolor='darkgray',
        framealpha=0.95
    )

# Matching plot format to reference
ax.set_axis_off()
plt.title("Morning Traverse Points\n(6 - 7 am)", fontsize=16, fontweight='bold', pad=25, color='#2c7bb6')
plt.tight_layout()
plt.show()

"""# Afternoon Temperature Distribution"""

# Import modules
import os
import zipfile
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np

# Extract data from whole zip file
zip_path = '2dtg7-osfstorage-archive.zip'
extract_dir = 'extracted_data'
os.makedirs(extract_dir, exist_ok=True)

# Unzip main archive
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# Extract nested zip files
zipped_files_found = True
while zipped_files_found:
    zipped_files_found = False
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.zip'):
                nested_zip_path = os.path.join(root, file)
                target_extract_to = os.path.join(root, file[:-4])
                if not os.path.exists(target_extract_to):
                    with zipfile.ZipFile(nested_zip_path, 'r') as nested_ref:
                        nested_ref.extractall(target_extract_to)
                    zipped_files_found = True

# Specifically target the June 27th afternoon traverse shapefile
selected_shapefile = None
for root, dirs, files in os.walk(extract_dir):
    for file in files:
        if file.endswith('.shp') and '06-27_traverses' in root and 'af_trav' in file:
            selected_shapefile = os.path.join(root, file)
            break
    if selected_shapefile:
        break

if not selected_shapefile:
    # Fallback search if path changes
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.shp') and 'af_trav' in file:
                selected_shapefile = os.path.join(root, file)
                break
        if selected_shapefile:
            break

if not selected_shapefile:
    raise FileNotFoundError("Could not find the June 27th morning traverse shapefile.")

# Load the correct shapefile into a GeoDataFrame
gdf = gpd.read_file(selected_shapefile)

# Sort chronologically
if 'time' in gdf.columns:
    gdf = gdf.sort_values(by='time')

# Search for boundary shapefile to plot 'Model Boundary'
boundary_shapefile = None
for root, dirs, files in os.walk(extract_dir):
    for file in files:
        if file.endswith('.shp') and ('boundary' in file.lower() or 'model' in file.lower() or 'area' in file.lower()):
            boundary_shapefile = os.path.join(root, file)
            break
    if boundary_shapefile:
        break

# Ensure coordinate reference system (CRS) is Web Mercator (EPSG:3857) for the basemap
if gdf.crs != "EPSG:3857":
    gdf = gdf.to_crs(epsg=3857)

# Create the Geospatial Plot 
fig, ax = plt.subplots(1, 1, figsize=(11, 13))

# Explicitly get limits of the data like reference
bounds = gdf.total_bounds
ax.set_xlim(bounds[0] - 200, bounds[2] + 200)
ax.set_ylim(bounds[1] - 200, bounds[3] + 200)

# Exact classification bins from the reference legend
custom_bins = [84.20, 87.26, 87.98, 88.70, 89.24, 89.78, 90.50, 91.22, 92.12]

max_val = gdf['t_f'].max() # max temp from data to cap bins
all_bin_edges = custom_bins + [max_val]
descending_labels = [f"≤ {val:.2f} °F" for val in reversed(all_bin_edges)]

# Print to verify labels look correct
#print("Generated Labels:", descending_labels)

# Plot
gdf.plot(
    column='t_f',
    cmap='coolwarm',      
    scheme='UserDefined',
    classification_kwds={'bins': custom_bins},
    markersize=35,        
    edgecolor='none',      
    legend=True,
    legend_kwds={
        'loc': 'upper left',
        'bbox_to_anchor': (0.05, 0.90),
        'facecolor': 'white',
        'edgecolor': 'darkgray',
        'framealpha': 0.95
    },
    ax=ax,
    zorder=3
)

# Plot the Model Boundary if found
if boundary_shapefile:
    boundary_gdf = gpd.read_file(boundary_shapefile)
    if boundary_gdf.crs != "EPSG:3857":
        boundary_gdf = boundary_gdf.to_crs(epsg=3857)
    boundary_gdf.boundary.plot(ax=ax, color='black', linestyle='--', linewidth=1.5, zorder=2, label='Model Boundary')

# Set desaturated basemap style
ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, zoom=13, alpha=0.45, zorder=1)

# Force grayscale 
for child in ax.get_children():
    if isinstance(child, plt.matplotlib.image.AxesImage):
        arr = child.get_array()
        if arr is not None and len(arr.shape) == 3:
            # Apply standard luminosity grayscale formula
            gray = 0.2989 * arr[:, :, 0] + 0.5870 * arr[:, :, 1] + 0.1140 * arr[:, :, 2]
            # Re-tile back to RGB space but desaturated
            for i in range(3):
                arr[:, :, i] = gray
            child.set_data(arr)

# Legend
legend = ax.get_legend()
if legend:
    handles = legend.legend_handles
    reversed_handles=list(handles[::-1]) # reverses to align high temps with warm colors

    # If the boundary was plotted
    if boundary_shapefile:
        from matplotlib.lines import Line2D
        boundary_handle = Line2D([0], [0], color='black', linestyle='--', linewidth=1.5)
        descending_labels = list(descending_labels) + ['Model Boundary']

    ax.legend(
        reversed_handles,
        descending_labels,
        title='Temperature',
        loc='upper left',
        bbox_to_anchor=(0.05, 0.90),
        facecolor='white',
        edgecolor='darkgray',
        framealpha=0.95)

# Matching plot format to reference
ax.set_axis_off()
plt.title("Afternoon Traverse Points\n(3 - 4 pm)", fontsize=16, fontweight='bold', pad=25, color='#2c7bb6')
plt.tight_layout()
plt.show()

"""# Evening Temperature Distribution"""

# Import modules
import os
import zipfile
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np

# Extract data from whole zip file
zip_path = '2dtg7-osfstorage-archive.zip'
extract_dir = 'extracted_data'
os.makedirs(extract_dir, exist_ok=True)

# Unzip main archive
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# Extract nested zip files
zipped_files_found = True
while zipped_files_found:
    zipped_files_found = False
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.zip'):
                nested_zip_path = os.path.join(root, file)
                target_extract_to = os.path.join(root, file[:-4])
                if not os.path.exists(target_extract_to):
                    with zipfile.ZipFile(nested_zip_path, 'r') as nested_ref:
                        nested_ref.extractall(target_extract_to)
                    zipped_files_found = True

# Specifically target the June 27th evening traverse shapefile
selected_shapefile = None
for root, dirs, files in os.walk(extract_dir):
    for file in files:
        if file.endswith('.shp') and '06-27_traverses' in root and 'pm_trav' in file:
            selected_shapefile = os.path.join(root, file)
            break
    if selected_shapefile:
        break

if not selected_shapefile:
    # Fallback search if path changes
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.shp') and 'pm_trav' in file:
                selected_shapefile = os.path.join(root, file)
                break
        if selected_shapefile:
            break

if not selected_shapefile:
    raise FileNotFoundError("Could not find the June 27th morning traverse shapefile.")

# Load the correct shapefile into a GeoDataFrame
gdf = gpd.read_file(selected_shapefile)

# Sort chronologically
if 'time' in gdf.columns:
    gdf = gdf.sort_values(by='time')

# Search for boundary shapefile to plot 'Model Boundary'
boundary_shapefile = None
for root, dirs, files in os.walk(extract_dir):
    for file in files:
        if file.endswith('.shp') and ('boundary' in file.lower() or 'model' in file.lower() or 'area' in file.lower()):
            boundary_shapefile = os.path.join(root, file)
            break
    if boundary_shapefile:
        break

# Ensure coordinate reference system (CRS) is Web Mercator (EPSG:3857) for the basemap
if gdf.crs != "EPSG:3857":
    gdf = gdf.to_crs(epsg=3857)

# Create the Geospatial Plot 
fig, ax = plt.subplots(1, 1, figsize=(11, 13))

# Explicitly get limits of the data like reference
bounds = gdf.total_bounds
ax.set_xlim(bounds[0] - 200, bounds[2] + 200)
ax.set_ylim(bounds[1] - 200, bounds[3] + 200)

# Exact classification bins from the reference legend
custom_bins = [82.76, 83.48, 84.20, 84.92, 85.46, 85.82, 86.36, 86.90, 87.62]

max_val = gdf['t_f'].max() # max temp from data to cap bins
all_bin_edges = custom_bins + [max_val]
descending_labels = [f"≤ {val:.2f} °F" for val in reversed(all_bin_edges)]

# Print to verify labels look correct
#print("Generated Labels:", descending_labels)

# Plot
gdf.plot(
    column='t_f',
    cmap='coolwarm',      
    scheme='UserDefined',
    classification_kwds={'bins': custom_bins},
    markersize=35,         
    edgecolor='none',      
    legend=True,
    legend_kwds={
        'loc': 'upper left',
        'bbox_to_anchor': (0.05, 0.90),
        'facecolor': 'white',
        'edgecolor': 'darkgray',
        'framealpha': 0.95
    },
    ax=ax,
    zorder=3
)

# Plot the Model Boundary if found
if boundary_shapefile:
    boundary_gdf = gpd.read_file(boundary_shapefile)
    if boundary_gdf.crs != "EPSG:3857":
        boundary_gdf = boundary_gdf.to_crs(epsg=3857)
    boundary_gdf.boundary.plot(ax=ax, color='black', linestyle='--', linewidth=1.5, zorder=2, label='Model Boundary')

# Set desaturated basemap style
ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, zoom=13, alpha=0.45, zorder=1)

# Force grayscale 
for child in ax.get_children():
    if isinstance(child, plt.matplotlib.image.AxesImage):
        arr = child.get_array()
        if arr is not None and len(arr.shape) == 3:
            # Apply standard luminosity grayscale formula
            gray = 0.2989 * arr[:, :, 0] + 0.5870 * arr[:, :, 1] + 0.1140 * arr[:, :, 2]
            # Re-tile back to RGB space but desaturated
            for i in range(3):
                arr[:, :, i] = gray
            child.set_data(arr)

# Legend
legend = ax.get_legend()
if legend:
    handles = legend.legend_handles
    reversed_handles=list(handles[::-1]) # reverses to align high temps with warm colors

    # If the boundary was plotted
    if boundary_shapefile:
        from matplotlib.lines import Line2D
        boundary_handle = Line2D([0], [0], color='black', linestyle='--', linewidth=1.5)
        descending_labels = list(descending_labels) + ['Model Boundary']

    ax.legend(
        reversed_handles,
        descending_labels,
        title='Temperature',
        loc='upper left',
        bbox_to_anchor=(0.05, 0.90),
        facecolor='white',
        edgecolor='darkgray',
        framealpha=0.95)

# Matching plot format to reference
ax.set_axis_off()
plt.title("Evening Traverse Points\n(7 - 8 pm)", fontsize=16, fontweight='bold', pad=25, color='#2c7bb6')
plt.tight_layout()
plt.show()
