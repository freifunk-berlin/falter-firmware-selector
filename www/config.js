/* manual config */

var config = {
  // Show help text for images
  show_help: true,

  // Image download URL (e.g. "https://downloads.openwrt.org")
  image_url: "https://firmware.berlin.freifunk.net/",

  // Insert snapshot versions (optional)
  //show_snapshots: true,

  // Path to were overview.json can be found
  versions: {
    //(versionsnummer|bleeding-edge) - (stable|snapshot|unstable|rc1) - (tunneldigger (standart)|notunnel)
    "1.2.3 - stable - tunneldigger (standard)": "1.2.3/tunneldigger/",
    "1.2.3 - stable - notunnel": "1.2.3/notunnel/",
    "1.4.0 - snapshot - tunneldigger (standard)": "1.4.0-snapshot/tunneldigger/",
    "1.4.0 - snapshot - notunnel": "1.4.0-snapshot/notunnel/",
    "1.4.0 - rc1 - tunneldigger (standard)": "1.4.0-rc1/tunneldigger/",
    "1.4.0 - rc1 - notunnel": "1.4.0-rc1/notunnel/",
    "1.4.0 - stable - tunneldigger (standard)": "1.4.0/tunneldigger/",
    "1.4.0 - stable - notunnel": "1.4.0/notunnel/",
    "bleeding-edge - unstable - tunneldigger (standard)": "snapshot/tunneldigger/",
    "bleeding-edge - unstable - notunnel": "snapshot/notunnel/"
  },

  // Pre-selected version (optional)
  default_version: "1.2.3 - stable - tunneldigger (standard)",

  // Image download URL (optional)
  //image_url: "https://downloads.openwrt.org/releases/{version}/{target}",

  // Info link URL (optional)
  info_url: "https://openwrt.org/start?do=search&id=toh&q={title} @toh",

  // Attended Sysupgrade Server support (optional)
  //asu_url: "https://sysupgrade.openwrt.org",
};
