# QInfra QGIS Plugin - AI Development Guide

## Project Overview
QInfra is a QGIS plugin for Dutch infrastructure work, focused on PDOK aerial photo downloads with RD New coordinate system (EPSG:28992). The plugin provides a simple workflow: load aerial photos → draw project areas → export georeferenced images.

## Architecture & Key Components

### Core Module Structure
- **`qinfra_plugin.py`**: Main plugin class with toolbar actions and interactive map tools
- **`pdok_lagen.py`**: PDOK WMTS layer management, project area handling, and PNG+PGW export logic  
- **`download_dialog.py`**: UI dialog for resolution selection and export options
- **`__init__.py`**: Plugin factory entry point
- **`metadata.txt`**: QGIS plugin configuration

### Coordinate System Convention
- **Everything operates in EPSG:28992 (RD New)** - this is hardcoded throughout
- `zorg_voor_project_crs_rdnew()` automatically sets project CRS if different
- All geometries, exports, and worldfiles use RD New coordinates

### Memory Layer Pattern
- Project areas stored as memory layers named `"Projectgebied (RD)"`
- Managed via `maak_of_update_projectgebied_layer()` - replaces existing layer each time
- Read back using `lees_projectgebied_rect()` for export operations

## Development Patterns

### QGIS Plugin Structure
```python
# Standard plugin initialization in __init__.py
def classFactory(iface):
    from .qinfra_plugin import QInfraPlugin
    return QInfraPlugin(iface)
```

### Interactive Map Tools
- `RechthoekTool` extends `QgsMapTool` for rectangle drawing
- Uses `QgsRubberBand` for visual feedback during drawing
- Callback pattern: `RechthoekTool(canvas, callback_function)`

### WMTS Layer Integration
```python
# PDOK WMTS URL pattern in pdok_lagen.py
PDOK_WMTS_LUCHTFOTO = "https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0?"
# Always use tileMatrixSet=EPSG:28992 for RD New
```

### Export Workflow
1. Find existing WMTS layer via `_vind_luchtfoto_layer()` 
2. Use `QgsMapRendererParallelJob` for raster rendering to specific pixel dimensions
3. Generate PGW worldfile with pixel center registration
4. Safety limits: 12000×12000 px maximum to prevent memory issues

### UI Conventions
- Dutch language throughout (matching target users)
- Toolbar icons from `icons/` directory (SVG format)  
- Resolution slider with inverted mapping (right = higher resolution/smaller m/px)
- File size estimation in dialog before export

## Key Implementation Details

### Layer Finding Pattern
```python
# Find layers by provider type and name pattern
for lyr in QgsProject.instance().mapLayers().values():
    if isinstance(lyr, QgsRasterLayer) and lyr.providerType() == "wms" and "luchtfoto" in lyr.name().lower():
        return lyr
```

### Error Handling
- Use `QMessageBox` for user-facing errors
- Validate layer loading with `rl.isValid()`
- Check for project areas before export operations

### Future Extensions
- BGT/BRK downloads are planned but currently disabled placeholders
- Plugin metadata marks as `experimental=True`
- Version follows semantic versioning (currently v0.1.0)

## Development Environment
- Python 3 with PyQGIS API
- No external dependencies beyond QGIS core
- No `.qrc` resource files (keeping simple file structure)
- MIT license from Kaartster BV

## Roadmap & Future Enhancements

### **Phase 1: Multi-Layer Export (Pre-QGIS Repository)**
**Vision**: Transform download functionality from single-layer to comprehensive multi-layer export with format-appropriate outputs
- **Auto-detect visible background layers**: Scan project for all loaded PDOK services (BRT, Luchtfoto, BGT, BRK)
- **Smart export by layer type**: 
  - Luchtfoto → PNG + PGW (highest available resolution: 8cm or 25cm)
  - BGT/BRK → WFS vector export (GeoJSON/GeoPackage for editability)
  - BRT → PNG + PGW (cartographic visualization)
- **Simplified UX**: Remove resolution slider, auto-select highest quality, size estimation + progress bar
- **Parallel processing**: Efficient simultaneous raster and vector exports with progress tracking
- **Intelligent file naming**: `ProjectName_Luchtfoto-8cm.png`, `ProjectName_BGT-standaard.gpkg`

**Implementation Strategy:**
- Extend `exporteer_luchtfoto_bbox()` for raster layers (PNG + PGW)
- Add new `exporteer_vector_wfs()` for BGT/BRK (WFS → GeoPackage/GeoJSON)
- Update `download_dialog.py` with progress bar and cancel functionality
- Implement automatic resolution detection and size estimation
- Add WFS service integration for vector data access

**User Workflow Enhancement:**
1. Load multiple background services (BRT + Luchtfoto + BGT)
2. Adjust layer visibility to achieve desired combination
3. Draw project area and click "Export All" 
4. Monitor progress with cancel option
5. Receive mixed outputs: raster PNGs for imagery + vector files for editable data

### **Phase 2: Extended PDOK Integration**
- AHN (height data) integration for terrain analysis
- NWB (road networks) for transportation planning
- Enhanced service discovery and metadata display

### **Phase 3: Advanced Export Features**
- Custom export formats (GeoTIFF, ECW)
- Multi-resolution batch exports
- Layer composition and styling preservation

## Testing & Debugging
- Test with various project area sizes to verify memory limits
- Verify EPSG:28992 coordinate transformations
- Check PGW worldfile accuracy in external GIS software
- Validate WMTS layer loading with PDOK service availability
- **Multi-layer testing**: Verify consistent export across different layer combinations
- **Performance testing**: Monitor memory usage during parallel layer rendering