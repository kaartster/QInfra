# QInfra — QGIS-plugin voor Nederlandse infra (v0.1.0)

QInfra is een kleine, praktische QGIS-plugin voor het snel laden en exporteren van PDOK luchtfoto's binnen Nederland. De plugin werkt standaard in RD New (EPSG:28992) en is gericht op een eenvoudige workflow: laad landelijke WMTS-luchtfoto, teken een projectgebied en exporteer een georeferende PNG + PGW.

Belangrijk: deze README is in het Nederlands om de workflow en gebruik eenvoudig te maken.

## Kernfunctionaliteit
- Laad PDOK Actueel_orthoHR via WMTS (tileMatrixSet=EPSG:28992).
- Teken een rechthoek als "Projectgebied (RD)" — opgeslagen als memory-layer in het project.
- Exporteer het projectgebied als PNG (lossless) met een bijbehorende PGW (worldfile) voor georeferentie in EPSG:28992.
- Vooruitblik van pixelgrootte en bestandsomvang in de download-dialog.

## Snelle workflow
1. Klik "Luchtfoto" — de landelijke PDOK WMTS-laag wordt toegevoegd (RD New wordt ingesteld als project-CRS).
2. Klik "Projectgebied" — teken een rechthoek in de kaart; dit maakt de laag "Projectgebied (RD)".
3. Klik "Download" — vink "Luchtfoto" aan, schuif de resolutie (rechts = hogere resolutie / kleinere m/px), klik "Download" en kies een bestandsnaam. Je krijgt een PNG + PGW. De WMTS-laag wordt standaard verborgen nadat de export is voltooid.

## Installatie (handmatig)
1. Download en pak de release uit (bijv. `QInfra-v0.2.7.zip`).
2. Plaats de map `QInfra/` in je QGIS user-plugins folder:
   - Windows: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
3. Herstart QGIS of schakel de plugin in: Plugins → Manage and Install Plugins → Installed → QInfra → Enable.

## Bekende beperkingen
- BGT en BRK zijn placeholders voor nu; download/visualisatie komt in toekomstige versies.
- Export heeft een veiligheidsgrens (standaard ca. 12000×12000 px) om te voorkomen dat QGIS/OS geheugenproblemen krijgt.
- Export is PNG (lossless). PGW worldfile wordt aangemaakt voor RD New.

## Ontwikkeling en style
- Standaard-CRS is EPSG:28992; alle geometrieën en worldfiles zijn in RD New.
- Code is Python 3 / PyQGIS. Bestanden zijn bewust simpel gehouden (geen qrc resources).
- Zie de repository voor verdere taken: BGT/BRK downloads, filename-patterns, append-mode voor projectgebieden, etc.

## Licentie & auteurs
- Auteurs: Kaartster BV
- Licentie: MIT (bestand `QInfra/LICENSE`)
