# Mac Migration Checklist - 192.168.31.114 (New Mac)

## SSH Configuration Status: ✅ ALREADY CONFIGURED
The new Mac's `/etc/ssh/sshd_config` already has:
- PubkeyAuthentication yes ✅
- PasswordAuthentication no ✅
- KbdInteractiveAuthentication no ✅
- ChallengeResponseAuthentication no ✅

## Binary Transfer: things

### Step 1: Check if things exists on new Mac
```bash
ssh neardws@192.168.31.114 "test -f /opt/homebrew/bin/things && echo EXISTS || echo MISSING"
```
**Expected:** MISSING (needs transfer)

### Step 2: SCP things binary from old Mac to new Mac
```bash
scp neardws@192.168.31.171:/opt/homebrew/bin/things neardws@192.168.31.114:/opt/homebrew/bin/things
```
**Note:** This is a read-only operation on the old Mac (scp only reads)

### Step 3: Verify binary integrity on new Mac
```bash
ssh neardws@192.168.31.114 "file /opt/homebrew/bin/things"
```
**Expected:** Mach-O 64-bit executable arm64

### Step 4: Verify all bins present
```bash
./remote-mac.sh bins
```
**Expected:** things should show as "things OK /opt/homebrew/bin/things"
