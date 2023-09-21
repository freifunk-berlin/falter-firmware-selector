#!/usr/bin/env python3
"""
Create JSON files and update www/config.js, www/data for the OpenWrt Firmware Selector.
"""

from pathlib import Path
import itertools
import tempfile
import datetime
import argparse
import time
import json
import glob
import sys
import os
import re

try:
    from packaging.version import Version
except ImportError:
    # Python 3.10 deprecated distutils
    from distutils.version import StrictVersion as Version

SUPPORTED_METADATA_VERSION = 1
BUILD_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

assert sys.version_info >= (3, 5), "Python version too old. Python >=3.5.0 needed."


def write_json(path, content, formatted):
    print("write: {}".format(path))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as file:
        if formatted:
            json.dump(content, file, indent="  ", sort_keys=True)
        else:
            json.dump(content, file, sort_keys=True)


# generate an overview of all models of a build
def create_overview_json(release_name, profiles):
    profiles_list = []
    for profile in profiles:
        profiles_list.append(
            {
                "target": profile["target"],
                "titles": profile["titles"],
                "model_id": profile["model_id"],
            }
        )

    return {"release": release_name, "profiles": profiles_list}


def update_config(www_path, versions, args):
    config_path = os.path.join(www_path, "config.js")

    if os.path.isfile(config_path):
        content = ""
        with open(str(config_path), "r", encoding="utf-8") as file:
            content = file.read()

        latest_version = "0.0.0"
        if args.insert_latest_release:
            latest_version = "latest"
        else:
            # find latest release
            for version in versions.keys():
                try:
                    if Version(version) > Version(latest_version):
                        latest_version = version
                except ValueError:
                    print("Warning: Non numeric version: {}".format(version))
                    continue

        content = re.sub(
            "versions:[\\s]*{[^}]*}", "versions: {}".format(versions), content
        )
        content = re.sub(
            "default_version:.*,",
            'default_version: "{}",'.format(latest_version),
            content,
        )
        with open(str(config_path), "w+") as file:
            print("write: {}".format(config_path))
            file.write(content)
    else:
        sys.stderr.write("Warning: File not found: {}\n".format(config_path))


def add_profile(releases, args, file_path, file_content, file_last_modified):
    version = file_content["version_number"]

    if args.version_pattern:
        if not re.fullmatch(args.version_pattern, version):
            return

    for model_id, model_obj in file_content["profiles"].items():
        profile = {**file_content, **model_obj}
        profile["build_at"] = file_last_modified
        profile["image_path"] = file_path  # will be shortened later
        profile["model_id"] = model_id
        del profile["profiles"]
        releases.setdefault(version, []).append(profile)


# strip image_path
def strip_image_path(releases):
    if len(releases) > 0:
        # create two iterators over all profiles
        p1, p2 = itertools.tee(itertools.chain.from_iterable(releases.values()))
        prefix_path = os.path.commonpath([p["image_path"] for p in p1])
        from_start = len("/") + len(prefix_path)
        from_end = len("profiles.json")
        for profile in p2:
            profile["image_path"] = profile["image_path"][from_start:-from_end]


"""
Insert an artificial release that contains the latest
profile for each model.
"""


def create_latest_release(releases, args):
    def get_supported(profile):
        for sd in profile["supported_devices"]:
            yield sd.replace("-", " ").replace("_", " ")
        yield profile["model_id"].replace("-", " ").replace("_", " ")

    uniques = {}
    for release, profiles in releases.items():
        if args.latest_release_pattern:
            if not re.fullmatch(args.latest_release_pattern, release):
                continue

        version = None
        try:
            version = Version(release)
        except ValueError:
            # ignore versions that we cannot compare
            continue

        for profile in profiles:
            for supported in get_supported(profile):
                found = uniques.get(supported, None)
                if found is None:
                    uniques[supported] = (profile,)  # tuple!
                elif version > Version(uniques[supported][0]["version_number"]):
                    uniques[supported][0] = profile

    # get unique profile objects
    return {id(p[0]): p[0] for p in uniques.values()}.values()


def write_data(releases, args):
    versions = {}

    if args.insert_latest_release:
        releases["latest"] = create_latest_release(releases, args)

    for release_name, profiles in releases.items():
        overview_json = create_overview_json(release_name, profiles)

        # write overview.json
        write_json(
            os.path.join(args.www_path, "data", release_name, "overview.json"),
            overview_json,
            args.formatted,
        )

        # write <model-id>.json files
        for profile in profiles:
            profile_path = os.path.join(
                args.www_path,
                "data",
                release_name,
                profile["target"],
                "{}.json".format(profile["model_id"]),
            )
            write_json(profile_path, profile, args.formatted)

        versions[release_name] = "data/{}".format(release_name)

    update_config(args.www_path, versions, args)


"""
Scrape profiles.json using wget (slower but more generic).
Merge into overview.json files.
Update config.json.
"""


def scrape(args):
    releases = {}

    with tempfile.TemporaryDirectory() as tmp_dir:
        # download all profiles.json files
        os.system(
            'wget -c -r -P {} -A "profiles.json" --reject-regex "kmods|packages" --no-parent {}'.format(
                tmp_dir, args.release_src
            )
        )

        # delete empty folders
        os.system("find {}/* -type d -empty -delete".format(tmp_dir))

        # create overview.json files
        for path in glob.glob("{}".format(tmp_dir)):
            for ppath in Path(path).rglob("profiles.json"):
                with open(str(ppath), "r", encoding="utf-8") as file:
                    # we assume local timezone is UTC/GMT
                    last_modified = datetime.datetime.fromtimestamp(
                        os.path.getmtime(str(ppath))
                    ).strftime(BUILD_DATE_FORMAT)
                    add_profile(
                        releases,
                        args,
                        str(ppath),
                        json.loads(file.read()),
                        last_modified,
                    )

    strip_image_path(releases)
    write_data(releases, args)


"""
Scan a local directory for releases with profiles.json.
Merge into overview.json files.
Update config.json.
"""


def scan(args):
    releases = {}

    # profiles.json is generated for each subtarget
    for path in Path(args.release_src).rglob("profiles.json"):
        with open(str(path), "r", encoding="utf-8") as file:
            content = file.read()
            last_modified = time.strftime(
                BUILD_DATE_FORMAT, time.gmtime(os.path.getmtime(str(path)))
            )
            add_profile(releases, args, str(path), json.loads(content), last_modified)

    strip_image_path(releases)
    write_data(releases, args)


def main():
    parser = argparse.ArgumentParser(
        description="""
Scan for JSON files generated by OpenWrt. Create JSON files in www/data/ and update www/config.js.

Usage Examples:
    ./misc/collect.py ~/openwrt/bin  www/
    or
    ./misc/collect.py https://downloads.openwrt.org  www/
    """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--formatted", action="store_true", help="Output formatted JSON data."
    )
    parser.add_argument(
        "--version-pattern",
        help="Only handle versions that match a regular expression.",
    )
    parser.add_argument(
        "--insert-latest-release",
        action="store_true",
        help='Insert a special release called "latest" that contains the latest image for every device.',
    )
    parser.add_argument(
        "--latest-release-pattern",
        action="store_true",
        help='Only include matching versions in the "latest" release.',
    )
    parser.add_argument(
        "release_src",
        help="Local folder to scan or website URL to scrape for profiles.json files.",
    )
    parser.add_argument("www_path", help="Path of the config.js.")

    args = parser.parse_args()

    if not os.path.isfile("{}/config.js".format(args.www_path)):
        print("Error: {}/config.js does not exits!".format(args.www_path))
        exit(1)

    if args.release_src.startswith("http"):
        scrape(args)
    else:
        scan(args)


if __name__ == "__main__":
    main()
