#!/bin/bash
# Search contacts by phone
PHONE="$1"
ssh neardws@192.168.31.114 "osascript -e 'tell application \"Contacts\"
  set matches to every person whose value of phones contains \"$PHONE\"
  repeat with p in matches
    log (name of p) & \" | \" & (value of phones of p)
  end repeat
end tell'" 2>&1
