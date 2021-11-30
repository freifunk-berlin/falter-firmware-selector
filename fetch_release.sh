#!/bin/sh

VERSION="$1"

if [ "$VERSION" = "" ]; then
        printf " Usage:\n\tfetch_release.sh [VERSION]\n\nExample:\n\tfetch_release.sh 1.2.1\n\n"
        exit 1
fi

./get_profiles_local.py "https://firmware.berlin.freifunk.net/stable/$VERSION/" /usr/local/src/www/htdocs/buildbot/stable/$VERSION/
