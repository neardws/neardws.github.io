#!/bin/bash
ssh neardws@192.168.31.114 "sqlite3 ~/Pictures/Photos\ Library.photoslibrary/database/Photos.sqlite \"SELECT ZTITLE FROM ZGENERICALBUM WHERE ZTITLE IS NOT NULL AND ZTRASHEDSTATE=0\""
