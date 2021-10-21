# This script regularily updates the overview-files for the firmware-selector by pulling
# the snapshot images from the buildbor-dir. It gets called by a cronjob.

REALPATH_SCRIPT=$(realpath "$0")
SCRIPT_DIR=$(dirname "$REALPATH_SCRIPT")
cd $SCRIPT_DIR

for DIR in $(ls /usr/local/src/www/htdocs/buildbot/unstable/ | grep snapshot); do
  ./get_profiles_local.py "https://firmware.berlin.freifunk.net/unstable/$DIR/" /usr/local/src/www/htdocs/buildbot/unstable/$DIR/
done
