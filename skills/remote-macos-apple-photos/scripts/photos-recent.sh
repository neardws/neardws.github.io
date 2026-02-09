#!/bin/bash
COUNT="${1:-10}"
ssh neardws@192.168.31.114 "sqlite3 ~/Pictures/Photos\ Library.photoslibrary/database/Photos.sqlite \"SELECT ZFILENAME, datetime(ZDATECREATED+978307200, 'unixepoch') FROM ZASSET WHERE ZTRASHEDSTATE=0 ORDER BY ZDATECREATED DESC LIMIT $COUNT\""
