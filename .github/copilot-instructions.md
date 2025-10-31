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

## Testing & Debugging
- Test with various project area sizes to verify memory limits
- Verify EPSG:28992 coordinate transformations
- Check PGW worldfile accuracy in external GIS software
- Validate WMTS layer loading with PDOK service availability