# QInfra

Modular open-source QGIS plugin for infrastructure and cadastral mapping — fetch and visualize PDOK layers such as luchtfoto, BGT, and BRK.

Maintainer: **Kaartster.BV** <kaartster.bv@gamil>

## Install (dev)
1. Copy the `QInfra` folder into your QGIS plugins directory:
   - **Windows**: %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
   - **macOS**: ~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/
   - **Linux**: ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
2. (Optional) Compile Qt resources if you plan to use `:/qinfra/...` paths later:
   ```bash
   cd QInfra
   pyrcc5 resources.qrc -o resources_rc.py   # or pyrcc6
   ```
3. Launch QGIS → *Plugins* → *Manage and Install Plugins...* → *Installed* → enable **QInfra**.

## Usage (MVP skeleton)
- Click the **QInfra** toolbar button or use *Plugins → QInfra → Hello from QInfra*.
- A message box confirms the plugin is loaded.

## Contributing
PRs welcome. Please follow Ruff linting. Run tests with `pytest`.

## Links
- Repository: https://github.com/kaartster/QInfra
- Issues: https://github.com/kaartster/QInfra/issues

## License
GPLv3 © 2025 Kaartster.BV

![CI](https://github.com/kaartster/QInfra/actions/workflows/ci.yml/badge.svg)
