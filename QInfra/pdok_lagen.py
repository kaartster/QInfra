from qgis.core import (
    QgsProject,
    QgsRasterLayer,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsSymbol,
    QgsSimpleFillSymbolLayer,
    QgsWkbTypes,
    QgsMapSettings,
    QgsMapRendererParallelJob,
)
from qgis.PyQt.QtCore import QCoreApplication, QSize
from qgis.PyQt.QtWidgets import QFileDialog
import os

LAYER_NAAM_PROJECTGEBIED = "Projectgebied (RD)"
PDOK_WMTS_LUCHTFOTO = "https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0?"

def tr(text: str) -> str:
    return QCoreApplication.translate("QInfra", text)

def zorg_voor_project_crs_rdnew() -> None:
    """Set project CRS to EPSG:28992 if it is different."""
    rd = QgsCoordinateReferenceSystem("EPSG:28992")
    if QgsProject.instance().crs() != rd:
        QgsProject.instance().setCrs(rd)

def voeg_pdok_luchtfoto_wmts_toe(laagnaam: str = "Luchtfoto (PDOK, WMTS)") -> QgsRasterLayer:
    """Add PDOK WMTS luchtfoto layer to the project and set canvas extent."""
    zorg_voor_project_crs_rdnew()
    uri = (
        f"url={PDOK_WMTS_LUCHTFOTO}"
        f"&service=WMTS&request=GetCapabilities"
        f"&layers=Actueel_orthoHR"
        f"&tileMatrixSet=EPSG:28992"
        f"&format=image/jpeg"
        f"&styles=default"
    )
    rl = QgsRasterLayer(uri, laagnaam, "wms")
    if not rl.isValid():
        raise RuntimeError(tr("Kon Luchtfoto (WMTS) niet laden."))
    QgsProject.instance().addMapLayer(rl)
    ext = rl.extent()
    if not ext.isEmpty():
        from qgis.utils import iface
        iface.mapCanvas().setExtent(ext)
        iface.mapCanvas().refresh()
    return rl

def _vind_luchtfoto_layer() -> QgsRasterLayer | None:
    """Return the first raster WMS layer whose name contains 'luchtfoto' (case-insensitive)."""
    for lyr in QgsProject.instance().mapLayers().values():
        if isinstance(lyr, QgsRasterLayer) and lyr.providerType() == "wms" and "luchtfoto" in lyr.name().lower():
            return lyr
    return None

def exporteer_luchtfoto_bbox(rect_rd: QgsRectangle, resolutie_m: float = 0.25, out_path: str | None = None):
    """
    Export the WMTS layer for the given rect to a PNG + PGW.
    If out_path is provided it is used; otherwise a save dialog is shown.
    Returns (path, pgw_path, px_w, px_h) or None if cancelled.
    """
    zorg_voor_project_crs_rdnew()
    from qgis.utils import iface

    luchtfoto = _vind_luchtfoto_layer() or voeg_pdok_luchtfoto_wmts_toe()

    width_m = rect_rd.width()
    height_m = rect_rd.height()
    px_w = max(1, int(round(width_m / resolutie_m)))
    px_h = max(1, int(round(height_m / resolutie_m)))

    if out_path:
        path = out_path
    else:
        default_name = "luchtfoto.png"
        path, _ = QFileDialog.getSaveFileName(iface.mainWindow(), tr("Opslaan als"), default_name, "PNG (*.png)")
        if not path:
            return None

    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

    ms = QgsMapSettings()
    ms.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:28992"))
    ms.setExtent(rect_rd)
    ms.setOutputSize(QSize(px_w, px_h))
    ms.setLayers([luchtfoto])

    job = QgsMapRendererParallelJob(ms)
    job.start()
    job.waitForFinished()
    img = job.renderedImage()
    img.save(path, "PNG")

    pgw_path = path[:-4] + ".pgw" if path.lower().endswith(".png") else path + ".pgw"
    pixel_size_x = rect_rd.width() / px_w
    pixel_size_y = -rect_rd.height() / px_h
    ulx = rect_rd.xMinimum() + (pixel_size_x / 2.0)
    uly = rect_rd.yMaximum() + (pixel_size_y / 2.0)
    with open(pgw_path, "w", encoding="utf-8") as wf:
        wf.write(f"{pixel_size_x}\n0.0\n0.0\n{pixel_size_y}\n{ulx}\n{uly}\n")

    return path, pgw_path, px_w, px_h

def maak_of_update_projectgebied_layer(rect_rd: QgsRectangle, naam: str = LAYER_NAAM_PROJECTGEBIED) -> QgsVectorLayer:
    """Create or replace the project-area memory layer with a single rectangular feature."""
    for lyr in QgsProject.instance().mapLayersByName(naam):
        QgsProject.instance().removeMapLayer(lyr.id())

    vl = QgsVectorLayer("Polygon?crs=EPSG:28992", naam, "memory")
    pr = vl.dataProvider()
    feat = QgsFeature()
    feat.setGeometry(QgsGeometry.fromRect(rect_rd))
    pr.addFeatures([feat])
    vl.updateExtents()

    sym = QgsSymbol.defaultSymbol(vl.geometryType())
    fill = QgsSimpleFillSymbolLayer()
    c = fill.color(); c.setAlpha(0)
    fill.setColor(c)
    sc = fill.strokeColor(); sc.setAlpha(255)
    fill.setStrokeColor(sc)
    fill.setStrokeWidth(1.2)
    sym.changeSymbolLayer(0, fill)
    vl.setRenderer(vl.renderer().__class__(sym))

    QgsProject.instance().addMapLayer(vl, True)
    return vl

def lees_projectgebied_rect(naam: str = LAYER_NAAM_PROJECTGEBIED) -> QgsRectangle | None:
    """Return the combined extent of all polygon features in the project-area layer, or None."""
    lagen = QgsProject.instance().mapLayersByName(naam)
    if not lagen:
        return None
    vl = lagen[0]
    if vl.wkbType() not in (QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon):
        return None
    extent = None
    for f in vl.getFeatures():
        g = f.geometry()
        if g is None or g.isEmpty():
            continue
        r = g.boundingBox()
        extent = r if extent is None else extent.combineExtentWith(r)
    return extent
