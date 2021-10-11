for FILE in $(ls www/); do ln -s -T "www/$FILE" "$FILE"; done
