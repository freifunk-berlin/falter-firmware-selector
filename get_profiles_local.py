#! /usr/bin/python3

"""Fetch the profiles from buildbot-unstable-dir
and feed them into the firmware-selector """

import requests
import shutil
import time
import sys
import os
import re


def find_subdirs(url, regex):
    r = requests.get(url)
    subdirs = re.findall(regex, r.text)
    return subdirs

try:
    print("fetching data from " + sys.argv[2])
except:
    print("Usage:\n\t./get_profiles_from [URL]\n\nPlease give an URL to the buildbot-dir and where it is on the host.")
    print("Example:\n\t./get_profiles_from http://buildbot.berlin.freifunk.net/buildbot/unstable/1.2.2-snapshot/ /usr/local/src/www/htdocs/buildbot/unstable/1.2.2-snapshot")
    exit(1)

# image_types = ['backbone/', 'notunnel/', 'tunneldigger/']
image_types = find_subdirs(sys.argv[1], "\"(\w*\/)\"")

# profiles_root = "1.2.2-snapshot"
profiles_root = sys.argv[1].split(sep='/')[-2]

# create new dir for firmware-version. If already there, remove it and create new one
try:
    os.mkdir(profiles_root)
except:
    shutil.rmtree(profiles_root)
    os.mkdir(profiles_root)


for itype in image_types:
    link = sys.argv[1] + itype

    # write stuff into own directory per image-type. recreate, if already there
    try:
        os.mkdir(itype)
    except:
        shutil.rmtree(itype)
        os.mkdir(itype)

    # create www/ and config.js in that subdir to satisfy collect.py
    os.mkdir(itype+"www/")
    os.system("touch "+itype+"www/config.js")

    # call collect.py for individual firmware-type
    command = "./misc/collect.py  --image-url '{}{{target}}' {}{} {}www/".format(link, sys.argv[2], itype, itype)
    os.system(command)

    # src_dir = "backbone/www/data/21.02-SNAPSHOT"
    # dirs_to_move = ['backbone/www/data/21.02-SNAPSHOT/overview.json', 'backbone/www/data/21.02-SNAPSHOT/mpc85xx', ...]
    src_dir = [f.path for f in os.scandir(itype+"www/data/") if f.is_dir()][0]
    dirs_to_move = [f.path for f in os.scandir(src_dir)]

    # move target_dirs to first level within imagetyp-dir. i.e. 1.1.2/tunneldigger/overview.json vs. 1.1.2/tunneldigger/www/data/overview.json
    for fd in dirs_to_move:
        shutil.move(fd, itype)
    shutil.rmtree(itype+"www/")

    # remove obolete www-dir within version-dir
    shutil.move(itype, profiles_root)

# move version-dir (like 1.1.2/) to webservers www-directory. replace, if already there
try:
    shutil.move(profiles_root, "www/")
except:
    shutil.rmtree("www/" + profiles_root)
    shutil.move(profiles_root, "www/")
