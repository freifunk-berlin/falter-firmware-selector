#!/usr/bin/python3

# usage: give file with duplicate links as $1. Copy file into verison-folder.

#for targets: bcm53xx, brcm47xx, 
# LIST=$(find . -type f | grep bcm53)
# for FILE in $LIST; do ./deduplicate.py $FILE ;done

import json
import sys
import os

dataset = {}

with open(sys.argv[1], "r") as f:
    data = f.read()
    dataset = json.loads(data)
    f.close()

reduced_linkset = dataset["images"][-1]

dataset["images"] = [reduced_linkset]

#print(dataset)

with open(sys.argv[1], "w") as f:
    f.write(json.dumps(dataset))
    f.close()
