# rws2gpx

Rijkswaterstaat drijvende markeringen naar CSV converteren

1. Download `yymmdd_DNZ_002a_markeringen_drijvend.csv` van http://www.vaarweginformatie.nl/fdd/main/infra/downloads
2. Converteer: `python rws2gpx.py <bestandsnaam.csv>`

Schrijft verschillende `.gpx`-bestanden naar `output/`. Deze bestanden kunnen dan vervolgens in OpenCPN worden ingeladen.

# TODO:
 - [ ] Toptekens
 - [ ] Lichten
 - [ ] Beschrijving (`<desc></desc>`) [see @nohals's version](https://github.com/nohal/OpenCPNScripts/blob/master/rws_buoys2gpx.sh#L46)
 - [ ] Export to GeoJSON

# UserIcons:

Zie ook [OpenCPN manual over user icons](http://opencpn.org/ocpn/user_icons)

Pak het zip-bestand uit in de configuratiedirectory van OpenCPN. De locatie van deze map staat in het 'about' venster in OpenCPN (vraagteken in taakbalk). Voor linux is dat: `~/.opencpn/`


# Attribution:

- [@nohal](https://github.com/nohal/OpenCPNScripts/blob/master/rws_buoys2gpx-osmicons.sh), rooiedirk for the [shell script version](https://github.com/nohal/OpenCPNScripts/blob/master/rws_buoys2gpx-osmicons.sh).
- OpenSeaMap for `UserIcons.zip`
