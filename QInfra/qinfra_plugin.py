from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsRectangle,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsProject,
    QgsWkbTypes,
    QgsRasterLayer,
)
from qgis.gui import QgsMapTool, QgsRubberBand
import os

from .pdok_lagen import (
    voeg_pdok_luchtfoto_wmts_toe,
    exporteer_luchtfoto_bbox,
    zorg_voor_project_crs_rdnew,
    maak_of_update_projectgebied_layer,
    lees_projectgebied_rect,
)
from .download_dialog import DownloadDialog

class RechthoekTool(QgsMapTool):
    """Interactive map tool to draw a rectangle and pass it to a callback."""
    def __init__(self, canvas, callback):
        super().__init__(canvas)
        self.canvas = canvas
        self.callback = callback
        self.rb = QgsRubberBand(canvas, QgsWkbTypes.PolygonGeometry)
        self.rb.setColor(QColor(30, 144, 255, 80))
        self.rb.setFillColor(QColor(30, 144, 255, 40))
        self.rb.setWidth(2)
        self.start = None
        self.dragging = False

    def canvasPressEvent(self, e):
        self.start = self.toMapCoordinates(e.pos())
        self.dragging = True

    def canvasMoveEvent(self, e):
        if not self.dragging:
            return
        cur = self.toMapCoordinates(e.pos())
        rect = QgsRectangle(self.start, cur)
        self._draw_rect(rect)

    def canvasReleaseEvent(self, e):
        if not self.dragging:
            return
        self.dragging = False
        cur = self.toMapCoordinates(e.pos())
        rect = QgsRectangle(self.start, cur)
        self._draw_rect(rect)
        self.callback(rect)
        self.rb.reset(QgsWkbTypes.PolygonGeometry)

    def _draw_rect(self, rect: QgsRectangle) -> None:
        from qgis.core import QgsGeometry, QgsPointXY
        pts = [
            QgsPointXY(rect.xMinimum(), rect.yMaximum()),
            QgsPointXY(rect.xMaximum(), rect.yMaximum()),
            QgsPointXY(rect.xMaximum(), rect.yMinimum()),
            QgsPointXY(rect.xMinimum(), rect.yMinimum()),
            QgsPointXY(rect.xMinimum(), rect.yMaximum()),
        ]
        self.rb.reset(QgsWkbTypes.PolygonGeometry)
        self.rb.addGeometry(QgsGeometry.fromPolygonXY([pts]), None)

class QInfraPlugin:
    """Main plugin class providing toolbar actions and dialog handling."""
    def __init__(self, iface):
        self.iface = iface
        self.toolbar = iface.addToolBar("QInfra")
        self.actions = []
        self.rect_tool = None

    def tr(self, text: str) -> str:
        return QCoreApplication.translate("QInfra", text)

    def initGui(self):
        base = os.path.dirname(__file__)
        icon_lucht = QIcon(os.path.join(base, "icons", "luchtfoto.svg"))
        icon_dl = QIcon(os.path.join(base, "icons", "download.svg"))
        icon_rect = QIcon(os.path.join(base, "icons", "rect.svg"))

        a1 = QAction(icon_lucht, self.tr("Luchtfoto"), self.iface.mainWindow())
        a1.setToolTip(self.tr("Luchtfoto"))
        a1.triggered.connect(self.laad_luchtfoto)
        self.iface.addPluginToMenu("QInfra", a1)
        self.toolbar.addAction(a1)
        self.actions.append(a1)

        a2 = QAction(icon_rect, self.tr("Projectgebied"), self.iface.mainWindow())
        a2.setToolTip(self.tr("Teken rechthoek en maak laag 'Projectgebied (RD)'") )
        a2.triggered.connect(self.start_projectgebied_tekenen)
        self.iface.addPluginToMenu("QInfra", a2)
        self.toolbar.addAction(a2)
        self.actions.append(a2)

        a3 = QAction(icon_dl, self.tr("Download"), self.iface.mainWindow())
        a3.setToolTip(self.tr("Kies wat je wilt downloaden voor het projectgebied"))
        a3.triggered.connect(self.open_download_dialog)
        self.iface.addPluginToMenu("QInfra", a3)
        self.toolbar.addAction(a3)
        self.actions.append(a3)

    def unload(self):
        for a in self.actions:
            self.iface.removePluginMenu("QInfra", a)
            self.toolbar.removeAction(a)
        del self.toolbar

    def laad_luchtfoto(self):
        try:
            voeg_pdok_luchtfoto_wmts_toe()
        except Exception as e:
            QMessageBox.critical(self.iface.mainWindow(), "QInfra", str(e))

    def start_projectgebied_tekenen(self):
        zorg_voor_project_crs_rdnew()
        canvas = self.iface.mapCanvas()
        proj = QgsProject.instance()
        rd = QgsCoordinateReferenceSystem("EPSG:28992")

        def on_rect(rect_map):
            if proj.crs() != rd:
                ct = QgsCoordinateTransform(proj.crs(), rd, proj)
                rect_rd = ct.transform(rect_map)
            else:
                rect_rd = rect_map
            maak_of_update_projectgebied_layer(rect_rd)
            canvas.unsetMapTool(self.rect_tool)

        self.rect_tool = RechthoekTool(canvas, on_rect)
        canvas.setMapTool(self.rect_tool)

    def open_download_dialog(self):
        rect_rd = lees_projectgebied_rect()
        if not rect_rd:
            QMessageBox.information(
                self.iface.mainWindow(),
                "QInfra",
                self.tr("Geen projectgebied gevonden. Teken eerst een 'Projectgebied'."),
            )
            return

        def schatter(res_m):
            px_w = max(1, int(round(rect_rd.width() / res_m)))
            px_h = max(1, int(round(rect_rd.height() / res_m)))
            est_mb = (px_w * px_h * 4) / (1024 * 1024)
            return px_w, px_h, est_mb

        dlg = DownloadDialog(self.iface.mainWindow(), schatting_functie=schatter, init_res=0.25)
        if not dlg.exec_():
            return

        keuzes = dlg.keuzes()
        res = dlg.gekozen_resolutie()

        MAX_W = 12000
        MAX_H = 12000
        if keuzes.get("luchtfoto", False):
            px_w, px_h, est_mb = schatter(res)
            if px_w > MAX_W or px_h > MAX_H:
                QMessageBox.warning(
                    self.iface.mainWindow(),
                    "QInfra",
                    self.tr(f"Luchtfoto te groot ({px_w}×{px_h} px). Verklein gebied of kies grovere resolutie."),
                )
                return

        if keuzes.get("luchtfoto", False):
            try:
                result = exporteer_luchtfoto_bbox(rect_rd, resolutie_m=res)
                if result:
                    path, pgw, w, h = result
                    rl = QgsRasterLayer(path, os.path.basename(path))
                    if rl.isValid():
                        QgsProject.instance().addMapLayer(rl)
                    # hide WMTS layers after download (default)
                    root = QgsProject.instance().layerTreeRoot()
                    for lyr in QgsProject.instance().mapLayers().values():
                        if isinstance(lyr, QgsRasterLayer) and lyr.providerType() == "wms" and "luchtfoto" in lyr.name().lower():
                            node = root.findLayer(lyr.id())
                            if node:
                                node.setItemVisibilityChecked(False)
                    QMessageBox.information(
                        self.iface.mainWindow(),
                        "QInfra",
                        self.tr(f"Luchtfoto opgeslagen. {w}×{h} px (PNG+PGW). WMTS verborgen."),
                    )
            except Exception as e:
                QMessageBox.critical(self.iface.mainWindow(), "QInfra", f"Luchtfoto: {str(e)}")

        if keuzes.get("bgt", False) or keuzes.get("brk", False):
            QMessageBox.information(
                self.iface.mainWindow(),
                "QInfra",
                self.tr("BGT/BRK-download komt binnenkort. Luchtfoto is gedownload indien aangevinkt."),
            )
