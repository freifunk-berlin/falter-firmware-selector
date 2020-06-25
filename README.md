# Yet Another Firmware Selector

A simple OpenWrt firmware selector using autocompletion. Uses plain
HTML/CSS/JavaScript. Checkout the [Demo](https://mwarning.github.io/yet-another-firmware-selector/www/).

![image](misc/screenshot.png)


## Run

* Checkput the repository and change to the project directory
* Start webserver (e.g. `python3 -m http.server`)
* Go to `http://localhost:8000/www/` in your web browser

Configure with [config.js](www/config.js).

## Attended Sysupgrade Support

This firmware selector can speak to a [ASU server](https://github.com/aparcar/asu) to build custom images. To enable the feature, the `asu_url` option in the config.js needs to be set.

## Update Database

The `overview.json` files are based on JSON files created by OpenWrt
(master): `Global build settings  ---> [*] Create JSON info files per build
image`.

A [Python script](misc/collect.py) is included to merge the JSON files:
`./collect.py bin/ --url
'https://downloads.openwrt.org/releases/{version}/targets/{target}' >
overview.json`.

For the OpenWrt 18.06 and 19.07 releases, you need to patch OpenWrt to output JSON files for collect.py (commit [openwrt/openwrt@881ed09](https://github.com/openwrt/openwrt/commit/881ed09ee6e23f6c224184bb7493253c4624fb9f)).

## Similar Projects

- [Gluon Firmware Selector](https://github.com/freifunk-darmstadt/gluon-firmware-selector): Original source of this project for images generated by [Gluon](https://github.com/freifunk-gluon/), now with pictures.
- [Freifunk Hennef Firmware Downloader](https://github.com/Freifunk-Hennef/ffhef-fw-dl): Similar to the project above, but PHP based.
- [LibreMesh Chef](https://github.com/libremesh/chef/): Allows to select configurations.
- [GSoC Firmware Selector](https://github.com/sudhanshu16/openwrt-firmware-selector/): Result of the GSoC
- [FFB Firmware Selector](https://github.com/freifunk-bielefeld/firmware-selector): Build for Freifunk Bielefeld
