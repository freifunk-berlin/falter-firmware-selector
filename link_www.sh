#!/bin/sh

# link every file in www-folder to this folder

for FILE in $(ls www/); do
	ln -s www/$FILE $FILE
done
