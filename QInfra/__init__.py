# __init__.py
# QInfra - Minimal QGIS plugin bootstrap

def classFactory(iface):  # QGIS calls this to get your plugin
    from .qinfra_plugin import QInfraPlugin
    return QInfraPlugin(iface)
