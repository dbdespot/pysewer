# SPDX-FileCopyrightText: 2023 Helmholtz Centre for Environmental Research (UFZ)
# SPDX-License-Identifier: GPL-3.0-only

"""Stage benchmark datasets into work/benchmarks/ (scratch, never committed).

- reviewer_reduced: clip data/from_reviewer roads/buildings (EPSG:32631)
  to the cropped_dem extent
- wasweta: copy the Wasweta II share (UTM 36S) off the Nextcloud sync dir
  (never compute against a live sync mount)

Idempotent: existing staged files are kept.
"""

from pathlib import Path

import geopandas as gpd
import rasterio

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK = REPO_ROOT / "work" / "benchmarks"
WASWETA_SRC = Path("/Users/despot/Nextcloud/Shared with me/Wasweta_II_Test_Case")


def stage_reviewer_reduced():
    stage_reviewer(
        dem="cropped_dem.tif", suffix="reduced", label="reviewer_reduced"
    )


def stage_dem_nodata_fixed(src_path, out_path):
    """Copy a DEM clearing a bogus nodata tag. The reviewer rasters declare
    nodata=0.0, but the terrain legitimately spans -4..76 m, so sea-level
    cells (exactly 0) were treated as holes — the source of the
    'No Elevation Data' failures."""
    if out_path.exists():
        return out_path
    with rasterio.open(src_path) as src:
        meta = src.meta.copy()
        meta.update(nodata=None)
        with rasterio.open(out_path, "w", **meta) as dst:
            dst.write(src.read())
    return out_path


def valid_data_extent(dem_path, inner_buffer_m):
    """Polygon of the DEM extent, shrunk inward so that profile sampling
    near feature endpoints cannot step outside coverage."""
    from shapely.geometry import box

    with rasterio.open(dem_path) as src:
        return box(*src.bounds).buffer(-inner_buffer_m)


def stage_reviewer(dem, suffix, label):
    out = WORK / "reviewer"
    out.mkdir(parents=True, exist_ok=True)
    dem_path = stage_dem_nodata_fixed(
        REPO_ROOT / "data/from_reviewer" / dem, out / f"dem_{suffix}.tif"
    )
    roads_out = out / f"roads_{suffix}.gpkg"
    buildings_out = out / f"buildings_{suffix}.gpkg"
    if roads_out.exists() and buildings_out.exists():
        print(f"{label}: already staged")
        return
    # 3-cell inner buffer (~77 m at 25.6 m resolution): keeps every staged
    # feature well inside elevation coverage
    extent = valid_data_extent(dem_path, inner_buffer_m=77)
    roads = gpd.read_file(REPO_ROOT / "data/from_reviewer/roads.geojson")
    buildings = gpd.read_file(REPO_ROOT / "data/from_reviewer/buildings.geojson")
    gpd.clip(roads, extent).explode(index_parts=False).to_file(
        roads_out, driver="GPKG"
    )
    clipped_buildings = gpd.clip(buildings, extent)
    clipped_buildings = clipped_buildings[~clipped_buildings.geometry.is_empty]
    clipped_buildings.to_file(buildings_out, driver="GPKG")
    print(
        f"{label}: staged {len(gpd.read_file(roads_out))} roads, "
        f"{len(clipped_buildings)} buildings"
    )


def stage_wasweta():
    """The source DEM leaves its nodata border UNtagged: one line of 0.0
    cells in ~1,400 m terrain. Sampled silently, those cells fabricate a
    ~1,387 m elevation cliff (25 m/s design velocities on adjacent pipes).
    Declare nodata=0.0 on the staged copy (terrain minimum is 1,355 m, so
    0.0 is unambiguous) and clip features inside the valid-data footprint."""
    from shapely.geometry import box

    out = WORK / "wasweta"
    out.mkdir(parents=True, exist_ok=True)
    if (out / "dem_utm.tif").exists():
        print("wasweta: already staged")
        return
    if not WASWETA_SRC.exists():
        print(f"wasweta: source not found ({WASWETA_SRC}) — skipped")
        return
    with rasterio.open(WASWETA_SRC / "dem_utm.tif") as src:
        data = src.read()
        meta = src.meta.copy()
        meta.update(nodata=0.0)
        with rasterio.open(out / "dem_utm.tif", "w", **meta) as dst:
            dst.write(data)
        valid = data[0] != 0
        rows = valid.any(axis=1).nonzero()[0]
        cols = valid.any(axis=0).nonzero()[0]
        # 2-cell inner margin keeps profile sampling off the nodata border
        left, top = src.xy(rows[0] + 2, cols[0] + 2, offset="ul")
        right, bottom = src.xy(rows[-1] - 2, cols[-1] - 2, offset="lr")
    extent = box(left, bottom, right, top)
    for name in ("roads_utm", "buildings_utm"):
        gdf = gpd.read_file(WASWETA_SRC / f"{name}.shp")
        clipped = gpd.clip(gdf, extent).explode(index_parts=False)
        clipped = clipped[~clipped.geometry.is_empty]
        clipped.to_file(out / f"{name}.shp")
        print(f"wasweta: {name} {len(gdf)} -> {len(clipped)} features")
    print("wasweta: staged")


if __name__ == "__main__":
    stage_reviewer_reduced()
    stage_wasweta()
