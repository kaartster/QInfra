def classFactory(iface):
    from .qinfra_plugin import QInfraPlugin
    return QInfraPlugin(iface)
