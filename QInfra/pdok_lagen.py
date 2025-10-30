
from qgis.core import (
    QgsProject, QgsRasterLayer, QgsCoordinateReferenceSystem, QgsRectangle,
    QgsVectorLayer, QgsFeature, QgsGeometry, QgsSymbol, QgsSimpleFillSymbolLayer, QgsWkbTypes
)
from qgis.PyQt.QtCore import QCoreApplication, QSize
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.core import QgsMapSettings, QgsMapRendererParallelJob

LAYER_NAAM_PROJECTGEBIED = "Projectgebied (RD)"

def tr(t):
    return QCoreApplication.translate("QInfra", t)

PDOK_WMTS_LUCHTFOTO = "https://service.pdok.nl/hwh/luchtfotorgb/wmts/v1_0?"

def zorg_voor_project_crs_rdnew():
    rd = QgsCoordinateReferenceSystem("EPSG:28992")
    if QgsProject.instance().crs() != rd:
        QgsProject.instance().setCrs(rd)

def voeg_pdok_luchtfoto_wmts_toe(laagnaam="Luchtfoto (PDOK, WMTS)"):
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

def _vind_luchtfoto_layer():
    for lyr in QgsProject.instance().mapLayers().values():
        if isinstance(lyr, QgsRasterLayer) and lyr.providerType() == "wms" and "luchtfoto" in lyr.name().lower():
            return lyr
    return None

def exporteer_luchtfoto_bbox(rect_rd: QgsRectangle, resolutie_m=0.25):
    zorg_voor_project_crs_rdnew()
    from qgis.utils import iface
    luchtfoto = _vind_luchtfoto_layer()
    if luchtfoto is None:
        luchtfoto = voeg_pdok_luchtfoto_wmts_toe()

    width_m = rect_rd.width()
    height_m = rect_rd.height()
    px_w = max(1, int(round(width_m / resolutie_m)))
    px_h = max(1, int(round(height_m / resolutie_m)))

    path, _ = QFileDialog.getSaveFileName(iface.mainWindow(), tr("Opslaan als"), "luchtfoto.png", "PNG (*.png)")
    if not path:
        return None

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

def maak_of_update_projectgebied_layer(rect_rd: QgsRectangle, naam=LAYER_NAAM_PROJECTGEBIED) -> QgsVectorLayer:
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

def lees_projectgebied_rect(naam=LAYER_NAAM_PROJECTGEBIED):
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
