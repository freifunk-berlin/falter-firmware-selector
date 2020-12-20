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
    print("fetching data from " + sys.argv[1])
except:
    print("Usage:\n\t./get_profiles_from [URL]\n\nPlease give an URL to the buildbot-dir.")
    print("Example:\n\t./get_profiles_from http://buildbot.berlin.freifunk.net/buildbot/unstable/2020-12-19/")
    exit(1)

image_types = find_subdirs(sys.argv[1], "\"(\w*\/)\"")
#print(image_types)

profiles_root = sys.argv[1].split(sep='/')[-2]
try:
    os.mkdir(profiles_root)
except:
    shutil.rmtree(profiles_root)
    os.mkdir(profiles_root)

for itype in image_types:
    link = sys.argv[1] + itype
    
    # write stuff into own directory
    try:
        os.mkdir(itype)
    except:
        shutil.rmtree(itype)
        os.mkdir(itype)

    os.mkdir(itype+"www/")
    os.system("touch "+itype+"www/config.js")
    
    command = "./misc/collect.py  --image-url '"+link+"{target}' "+link+" "+itype+"www/"
    os.system(command)

    src_dir = [f.path for f in os.scandir(itype+"www/data/") if f.is_dir()][0]
    dirs_to_move = [f.path for f in os.scandir(src_dir)]

    
    # move dirs to first hirachy-step
    for fd in dirs_to_move:
        shutil.move(fd, itype)
    shutil.rmtree(itype+"www/")

    shutil.move(itype, profiles_root)

