# rws2gpx

Rijkswaterstaat drijvende markeringen naar CSV converteren

1. Download `yymmdd_DNZ_002a_markeringen_drijvend.csv`
2. Converteer: `python rws2gpx.py <bestandsnaam.csv>`

Schrijft verschillende `.gpx`-bestanden naar `output/`. Deze bestanden kunnen dan vervolgens in OpenCPN worden ingeladen.

# UserIcons:

Zie ook [OpenCPN manual over user icons](http://opencpn.org/ocpn/user_icons)

Pak het zip-bestand uit in de configuratiedirectory van OpenCPN. De locatie van deze map staat in het 'about' venster in OpenCPN (vraagteken in taakbalk). Voor linux is dat: `~/.opencpn/`


# Attribution:

nohal, rooiedirk

shell script version: https://github.com/nohal/OpenCPNScripts/blob/master/rws_buoys2gpx-osmicons.sh
