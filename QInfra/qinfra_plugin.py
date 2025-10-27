# qinfra_plugin.py
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication
import os

class QInfraPlugin:
    def __init__(self, iface):
        """
        :param iface: An interface instance that will be passed to this class
                      which provides the hook by which you can manipulate the QGIS application.
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None
        self.menu_text = "QInfra"
        self.toolbar = self.iface.addToolBar("QInfra")
        self.toolbar.setObjectName("QInfraToolbar")

    def tr(self, message: str) -> str:
        """Qt translation wrapper (keeps us ready for i18n)."""
        return QCoreApplication.translate("QInfraPlugin", message)

    def initGui(self):
        """Create menu/toolbar items and connect signals."""
        icon_path = os.path.join(self.plugin_dir, "icons", "icon.svg")
        self.action = QAction(QIcon(icon_path), self.tr("Hello from QInfra"), self.iface.mainWindow())
        self.action.setObjectName("QInfraHelloAction")
        self.action.setWhatsThis(self.tr("Show a test message from QInfra"))
        self.action.triggered.connect(self.run)

        # Add to Plugins menu and to our dedicated toolbar
        self.iface.addPluginToMenu(self.menu_text, self.action)
        self.toolbar.addAction(self.action)

    def unload(self):
        """Remove menu/toolbar items when plugin is disabled."""
        if self.action:
            self.iface.removePluginMenu(self.menu_text, self.action)
            self.toolbar.removeAction(self.action)
        # Optionally remove the toolbar entirely
        del self.toolbar

    def run(self):
        """Slot for our action: minimal proof it works."""
        QMessageBox.information(self.iface.mainWindow(), self.tr("QInfra"), self.tr("QInfra plugin loaded!"))
