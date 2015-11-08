# rws2gpx

Rijkswaterstaat drijvende markeringen naar CSV converteren

1. Download `yymmdd_DNZ_002a_markeringen_drijvend.csv` van http://www.vaarweginformatie.nl/fdd/main/infra/downloads
2. Converteer: `python rws2gpx.py <bestandsnaam.csv>`

Schrijft verschillende `.gpx`-bestanden naar `output/`. Deze bestanden kunnen dan vervolgens in OpenCPN worden ingeladen.

# TODO:
 - [*] debug html-pagina om gebruikte ton/topteken combinaties te laten zien [Pagina hier](http://jieter.github.io/rws2gpx/debug/).
 - [*] Check of icons bestaan en sorteer boeien met missende icons in de debug pagina.
 - [*] Toptekens
 - [*] Lichten
 - [ ] Fix/maak tonnen (is nu geen User Icon voor wat klopt):
    - [ ] Spar Rood/wit
    - [ ] Spar Rood/groen
    - [ ] Spar Groen/rood
    - [ ] Bol Rood/wit
    - [ ] Bol Rood/groen
 - [ ] Missende topmarks:
    - [ ] Bol, rood/groen
    - [ ] Cilinder boven bol, rood

 - [ ] Beschrijving (`<desc></desc>`) [see @nohals's version](https://github.com/nohal/OpenCPNScripts/blob/master/rws_buoys2gpx.sh#L46)
 - [ ] Maak output van lichten/toptekens/descriptions configureerbaar
 - [ ] Export to GeoJSON
 - [ ] Composed images with buoy, top mark and light
 - [ ] Add (calculated) bounds to gpx.

## Toevoegen aan OpenCPN

De laag kan worden toegevoegd als 'Tijdelijke laag' (Temporary layer), of als een vast beschikbare laag. Kopieer de bestanden daarvoor naar een nieuw te maken submap van de configuratiedirectory met de naam `layers`. Op linux dus `mkdir -p ~/.opencpn/layers && cp output/* ~/.opencpn/layers/`.

### UserIcons:

Zonder icons wordt de `.gpx` weergegeven als ronde punten met een stip in het midden. Om mooie boeiplaatjes te krijgen zijn UserIcons nodig, meegeleverd in `UserIcons.zip`.

Pak de zip uit in de configuratiedirectory van OpenCPN. De locatie van deze map staat in het 'about' venster in OpenCPN (icoon met vraagteken in taakbalk). Voor linux is dat: `~/.opencpn/`

Zie ook [OpenCPN manual over user icons](http://opencpn.org/ocpn/user_icons)

# Attribution:

- [@nohal](https://github.com/nohal/OpenCPNScripts/blob/master/rws_buoys2gpx-osmicons.sh), rooiedirk for the [shell script version](https://github.com/nohal/OpenCPNScripts/blob/master/rws_buoys2gpx-osmicons.sh).
- OpenSeaMap for `UserIcons.zip`

# links
- [GPX schema documentation](http://www.topografix.com/GPX/1/1/)
