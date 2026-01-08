# Step 7: Video Demonstration Guide

**Time Required:** 6-8 hours (3-4 recording, 3-4 editing)  
**Who:** Person 3 (lead), all appear  
**Goal:** Create professional 12-15 minute demonstration video

## Overview

The video must demonstrate:
1. Application overview
2. All 4 vulnerabilities being exploited
3. Tool usage (Burp Suite, sqlmap)
4. Monitoring system
5. Patched version blocking attacks
6. Code differences

## Part A: Pre-Production Planning

### 1. Script Creation

**File:** `testing_results/VIDEO_SCRIPT.md`

```markdown
# Video Script - CS437 Task 5 Demonstration

## Timing: 14 minutes total

### SCENE 1: Introduction (0:00 - 1:00)
**Visual:** Team on camera or title slide
**Audio:**
"Hello, we are Team [X] presenting our CS 437 assignment on SCADA security. 
We developed a Remote Valve Management System for a city water reservoir with 
intentional security vulnerabilities. Today we'll demonstrate how these 
vulnerabilities are exploited and how we patched them.

Our team members are [Name 1], [Name 2], and [Name 3]. We implemented 4 critical 
vulnerabilities: three file upload vulnerabilities based on CWE-434, and one 
SQL injection vulnerability with role-based behavior.

Let's start with an overview of the application."

**Notes:** Keep introduction brief. Show team professionalism.

---

### SCENE 2: Application Tour (1:00 - 2:30)
**Visual:** Screen recording of application
**Audio:**
"This is the Remote Valve Management System. [Login as admin]

The dashboard shows 150 valves across the water distribution network. Each 
valve displays its current state, open percentage, location, and status.

[Click on a valve] We can control valves, issue commands like open, close, or 
adjust percentage.

[Go to Valves page] Here we can search and filter valves.

[Go to Upload page] The upload section has three scenarios - we'll exploit 
these shortly.

[Go to Logs] System logs show all commands and events.

[Go to Monitoring] The monitoring dashboard tracks security events - you'll 
see this fill up as we demonstrate attacks.

Now let's exploit the first vulnerability."

**Notes:** Quick tour, don't linger. Set the stage for attacks.

---

### SCENE 3: Vulnerability 1 - Upload Scenario 1 (2:30 - 4:30)
**Visual:** Split screen - Burp Suite + Browser
**Audio:**
"Vulnerability #1: Unrestricted file upload with no validation.

[Open Burp Suite] I've configured Firefox to proxy through Burp Suite.

[Navigate to Scenario 1] This endpoint is supposed to accept firmware files, 
but let's try uploading a malicious PHP file.

[Select shell.php] Here's our payload - a PHP webshell that executes system 
commands.

[Enable intercept] Burp intercepts the request. Notice the filename is 
'shell.php' and the content contains PHP code. There's no validation happening.

[Forward] The server accepts it without question.

[Show file on disk - terminal] The file is now on the server with its original name.

[Check monitoring] The attack is logged but was allowed.

Now let's test the patched version.

[Switch to localhost:5001] Same upload attempt...

[Enable intercept] Same malicious file...

[Forward] This time: 'Invalid file type. Only .bin and .conf allowed.'

[Show monitoring] The attack was logged and BLOCKED. The patch works.

[Show code comparison] The fix uses whitelist validation, magic byte 
verification, and secure random filenames."

**Notes:** This is the template - repeat similar flow for scenarios 2 and 3.

---

### SCENE 4: Vulnerability 2 - Upload Scenario 2 (4:30 - 6:00)
**Visual:** Burp Suite + Browser
**Audio:**
"Vulnerability #2: Weak protection with bypassable checks.

This endpoint has TWO protection mechanisms - but both can be bypassed.

First bypass: Size limit. [Show large file] This file is 10MB, over the 5MB limit.

[Intercept with Burp] Notice Content-Length header says 10485760 bytes.

[Modify to 1024] Change Content-Length to 1024. The server trusts this header.

[Forward] Bypassed! The 10MB file was accepted.

Second bypass: Extension blacklist. [Show JSP file] The blacklist only blocks 
.exe, .sh, .bat, .php - but .jsp is allowed!

[Upload JSP] Success! The blacklist is incomplete.

[Test on patched] Both bypasses fail on the patched version.

[Show code] The patch uses real size validation and whitelist instead of blacklist."

---

### SCENE 5: Vulnerability 3 - Upload Scenario 3 (6:00 - 7:30)
**Visual:** Browser + Terminal
**Audio:**
"Vulnerability #3: Encrypted file scanning bypass - a pipeline design flaw.

This endpoint encrypts files before storage. The problem? Scanning happens on 
the encrypted data, which is useless.

[Upload malicious file] File uploaded and encrypted.

[Show encrypted file in terminal] It's encrypted with AES-256 - the scan can't 
read the malicious content.

[Trigger decryption] Now we decrypt it via the decrypt endpoint.

[Show decrypted file] The malicious payload is extracted - no re-scan happened!

This is a real-world vulnerability pattern in OT systems that encrypt data 
before analysis.

[Test patched version] The patch implements decrypt-then-scan. After decryption, 
the file is scanned again and blocked.

[Show code] The fix adds scanning after decryption, closing the pipeline gap."

---

### SCENE 6: Vulnerability 4 - SQL Injection (7:30 - 11:00)
**Visual:** Burp Suite + Terminal (sqlmap)
**Audio:**
"Vulnerability #4: Role-based SQL injection - the most interesting one.

This vulnerability only affects admin users, not operators. It demonstrates 
how vulnerabilities can be missed during testing with limited privileges.

First, let's test as an operator.

[Login as operator1, go to search] Simple valve search.

[Intercept with Burp, inject payload] UNION SELECT to extract user table.

[Forward] Nothing. The results show valves, not users. Operators are safe - 
the code uses parameterized queries for them.

Now watch what happens as admin.

[Logout, login as admin] Same search page.

[Intercept, inject same payload] UNION SELECT from users table.

[Forward] Boom! User data extracted: admin, operator1, operator2, viewer1, 
emails, password hashes.

The admin account uses raw SQL with string interpolation. It's vulnerable.

Let's automate this with sqlmap.

[Terminal - sqlmap command] Testing as admin...

[Show output] sqlmap finds the vulnerability: 'Generic UNION query injectable'

[Enumerate databases] Database: valves

[Dump tables] 5 tables found.

[Dump users table] Complete data exfiltration: all usernames, hashes, emails.

[Show CSV output] sqlmap saved everything to CSV.

Now test the patched version.

[sqlmap on patched] Testing with maximum level and risk...

[Show output] 'Parameter does not seem to be injectable.' The patch works!

[Test patched as admin in browser] Injection fails - safe results returned.

[Show code comparison] The fix: parameterized queries for ALL users, regardless 
of role. Plus input validation and attack detection.

This demonstrates why privilege-based code paths are dangerous."

**Notes:** This is the longest section - SQL injection is the most complex vulnerability.

---

### SCENE 7: Monitoring Dashboard Deep Dive (11:00 - 12:00)
**Visual:** Monitoring dashboard (both versions)
**Audio:**
"Let's examine the monitoring system we built.

[Show vulnerable version monitoring] All our attacks are logged here:
- File upload attempts: 12 attacks
- SQL injection: 8 attacks
- Total: 20 security events

Each entry shows:
- Timestamp
- Attack type classification
- User and IP address
- Full request payload
- Outcome: ALLOWED (on vulnerable version)

[Show patched version monitoring] Same attacks on patched version:
- All 20 attacks logged
- Classification identical
- But outcome: BLOCKED

[Show detailed view] Clicking an attack shows full details: HTTP method, 
endpoint, parameters, user agent.

This monitoring system provides visibility into attacks on both versions and 
proves our patches are effective."

---

### SCENE 8: Code Walkthrough (12:00 - 13:00)
**Visual:** Code editor, side-by-side comparison
**Audio:**
"Let's look at the code changes.

[Show vulnerable upload code] Vulnerable version: No validation, filename 
preserved, direct save.

[Show patched upload code] Patched version: Whitelist check, magic byte 
verification, random filenames.

[Show vulnerable SQL code] Vulnerable: f-string interpolation for admin, 
parameterized for operator.

[Show patched SQL code] Patched: Parameterized for everyone, plus input 
validation and detection.

The patches follow security best practices:
- Whitelist over blacklist
- Defense in depth
- Input validation
- Secure by default
- Comprehensive logging"

---

### SCENE 9: Conclusion (13:00 - 14:00)
**Visual:** Team or conclusion slide
**Audio:**
"In summary:

We built a SCADA valve management system with 4 real-world vulnerabilities:
- Three file upload vulnerabilities with different weakness patterns
- One role-based SQL injection that demonstrates testing gaps

We successfully exploited all vulnerabilities using industry tools:
- Burp Suite for manual testing and interception
- sqlmap for automated SQL injection
- Complete data exfiltration achieved

We implemented comprehensive patches:
- 100% of attacks blocked on patched version
- No false positives in testing
- Functionality preserved

Our monitoring system:
- Logged 100% of attacks
- Accurate classification
- Provides visibility for incident response

This project demonstrates that securing OT systems requires:
- Defense in depth
- Input validation
- Secure coding practices
- Comprehensive monitoring

These principles apply to real SCADA systems protecting critical infrastructure.

Thank you for watching. We're ready for questions."

---

## B-Roll Shots Needed
1. Terminal commands running
2. File system showing uploaded files
3. Code editor showing vulnerabilities
4. Database viewer showing extracted data
5. Monitoring dashboard updating in real-time
6. Docker containers starting

## Graphics Needed
1. Title slide with team names
2. "Vulnerability #1" through "#4" title cards
3. "Patched Version" transition slides
4. Architecture diagram
5. Conclusion summary slide
```

### 2. Storyboard

Create a simple storyboard in PowerPoint or similar:

**Slide 1: Introduction**
- Team photo or names
- Project title
- Task number

**Slide 2: Application Tour**
- Screenshot of dashboard
- Key features list

**Slides 3-6: Each Vulnerability**
- Split screen layout
- Tool on left, app on right

**Slide 7: Monitoring**
- Dashboard screenshot
- Statistics

**Slide 8: Code**
- Side-by-side comparison

**Slide 9: Conclusion**
- Summary points
- Team names

## Part B: Equipment and Software Setup

### Recording Software Options

**Option 1: OBS Studio (Recommended - Free)**

**Installation:**
```bash
brew install --cask obs
```

**Configuration:**
1. Open OBS Studio
2. Settings → Output
   - Recording Format: MP4
   - Encoder: x264
   - Quality: High (CRF 18-23)
3. Settings → Video
   - Base Resolution: 1920x1080
   - Output Resolution: 1920x1080
   - FPS: 30
4. Settings → Audio
   - Sample Rate: 48kHz
   - Channels: Stereo

**Scene Setup:**
1. Create scene: "Full Screen"
   - Source: Display Capture
2. Create scene: "Browser + Burp"
   - Source 1: Window Capture (Browser) - Left 60%
   - Source 2: Window Capture (Burp) - Right 40%
3. Create scene: "Terminal + Browser"
   - Source 1: Window Capture (Terminal) - Bottom 40%
   - Source 2: Window Capture (Browser) - Top 60%
4. Create scene: "Webcam"
   - Source: Video Capture Device (for intro/conclusion)

**Option 2: QuickTime (macOS - Simple)**
1. Open QuickTime Player
2. File → New Screen Recording
3. Options → Show Mouse Clicks
4. Record full screen

**Option 3: Loom (Easy, Cloud-based)**
- Install from: https://www.loom.com
- Good for quick recordings
- Auto-uploads to cloud

### Audio Equipment

**Best:** External USB microphone (Blue Yeti, Audio-Technica AT2020)  
**Good:** Laptop built-in microphone in quiet room  
**Avoid:** Recording in noisy environment

**Audio Test:**
```bash
# Record 10 seconds to test
# Say: "Testing, one two three, this is the audio test"
# Playback and verify clarity
```

### Test Recording Checklist

Before full recording:
- [ ] OBS configured correctly
- [ ] Microphone working
- [ ] System audio captured (if needed)
- [ ] Screen resolution 1920x1080
- [ ] Applications in correct windows
- [ ] Notification Center disabled (Do Not Disturb)
- [ ] Desktop clean (close unnecessary apps)
- [ ] Browser zoom at 100%
- [ ] Dark mode ON (easier to see code)

## Part C: Recording Process

### Preparation Day Before

**1. Rehearse Script**
- Read through entire script 3 times
- Time each section
- Adjust if too long/short
- Mark breathing points

**2. Prepare Applications**
- Start Docker containers
- Login to both versions (keep sessions)
- Open Burp Suite, configure proxy
- Open Firefox
- Prepare terminal with sqlmap
- Have test files ready
- Clear browser cache
- Reset databases to clean state

**3. Clean Up Desktop**
```bash
# Close all unnecessary apps
# Hide desktop icons temporarily
defaults write com.apple.finder CreateDesktop false
killall Finder

# Re-enable after recording:
defaults write com.apple.finder CreateDesktop true
killall Finder
```

**4. Disable Notifications**
- System Preferences → Notifications
- Enable "Do Not Disturb"
- Or: Hold Option key, click menu bar clock

### Recording Day

**Morning Setup (30 min):**
1. Restart computer (clean state)
2. Start Docker containers
3. Verify both apps running
4. Configure OBS scenes
5. Test microphone
6. Record 30-second test
7. Review test recording

**Recording Session (3-4 hours):**

**Take 1: Introduction (Webcam)**
- Position camera at eye level
- Good lighting (face camera)
- Plain background
- Professional appearance
- 2-3 takes until perfect

**Take 2: Application Tour**
- Record 3 times
- Pick best take
- Aim for smooth mouse movement
- Clear, steady narration

**Takes 3-6: Each Vulnerability**
- Record each vulnerability separately
- 2-3 takes per vulnerability
- OK to pause and restart
- Focus on clarity over speed

**Take 7: Monitoring & Code**
- Screen recording
- Can speed up in editing

**Take 8: Conclusion (Webcam)**
- Return to webcam
- Professional closing
- Thank viewers

**Recording Tips:**
- Speak slowly and clearly
- Pause between sections (easy to cut)
- If you make mistake, pause, repeat from last sentence
- Don't say "um" or filler words
- Smile - it shows in your voice!
- Breathe normally

### What To Record

**For Each Vulnerability:**

1. **Setup Shot** (5 seconds)
   - Title card: "Vulnerability #X: [Name]"
   
2. **Explanation** (20-30 seconds)
   - What it is
   - Why it's vulnerable
   
3. **Exploitation** (60-90 seconds)
   - Tool setup
   - Attack execution
   - Success verification
   
4. **Monitoring** (15 seconds)
   - Show attack logged
   
5. **Patched Test** (30-45 seconds)
   - Same attack on patched
   - Show it's blocked
   
6. **Code Comparison** (30 seconds)
   - Vulnerable vs patched
   - Highlight fix

## Part D: Video Editing

### Editing Software Options

**Option 1: DaVinci Resolve (Free, Professional)**

**Installation:**
```bash
# Download from: https://www.blackmagicdesign.com/products/davinciresolve/
```

**Basic Editing:**
1. Import all video clips
2. Drag clips to timeline
3. Cut unnecessary parts (press B for blade tool)
4. Add transitions between clips
5. Add title cards
6. Add background music (optional, low volume)
7. Color correction if needed
8. Export as MP4

**Option 2: iMovie (macOS - Simple)**
1. Import clips
2. Drag to timeline
3. Add titles
4. Add transitions
5. Export as 1080p

**Option 3: Online Editors**
- Kapwing.com
- Clipchamp.com
- Good for simple edits

### Editing Workflow

**Step 1: Organize Clips (30 min)**
```
01_intro_take2.mov
02_tour_take1.mov
03_vuln1_take3.mov
04_vuln1_patched_take1.mov
05_vuln2_take2.mov
...
```

**Step 2: Assembly (1 hour)**
- Import all to timeline
- Arrange in order
- No cutting yet, just sequence

**Step 3: Cutting (1.5 hours)**
- Remove long pauses
- Remove mistakes
- Remove "um" sounds
- Keep total time 12-15 minutes

**Step 4: Annotations (1 hour)**

**Add text overlays:**
- Vulnerability names
- Key points
- Code highlights
- Terminal commands

**Example annotations:**
```
[When showing Burp request]
Text overlay: "Malicious PHP file - no validation"
Arrow pointing to filename

[When SQL injection succeeds]
Text overlay: "User data exfiltrated!"
Highlight the usernames

[When patched blocks]
Text overlay: "BLOCKED ✓"
Red circle around error message
```

**Tools for annotations:**
- DaVinci Resolve: Fusion page
- Screenflow (macOS): Built-in annotations
- After importing to editor, add shapes/text

**Step 5: Transitions (30 min)**
- Between scenes: Simple fade (1 second)
- Between vulnerabilities: 2-second fade
- Don't overuse fancy transitions

**Step 6: Title Cards (30 min)**

**Create in PowerPoint/Keynote:**

**Title Card 1: Opening**
```
CS 437 - Operational Technology Security
Assignment: SCADA Security

Task 5: Remote Valve Management System

Team:
[Name 1]
[Name 2]
[Name 3]
```

**Title Cards 2-5: Vulnerabilities**
```
Vulnerability #1
CWE-434: Unrestricted File Upload
No Protection
```

**Title Card 6: Monitoring**
```
Monitoring System
Attack Detection & Logging
```

**Title Card 7: Conclusion**
```
Thank You

Questions?

[Team Names]
[Date]
```

Export as PNG, import to video editor.

**Step 7: Audio Enhancement (30 min)**

**In DaVinci Resolve:**
1. Go to Fairlight tab
2. Select audio track
3. Add effects:
   - Noise Reduction (if background noise)
   - Normalize Audio (even volume)
   - EQ (boost voice frequencies 80-200 Hz cut, 2-5 kHz boost)
4. Target: -14 to -10 dB

**Background Music (Optional):**
- Only in intro/conclusion
- Royalty-free from: YouTube Audio Library, Free Music Archive
- Volume: -30 to -25 dB (very quiet, don't overpower voice)
- Fade in/out

**Step 8: Color Correction (15 min)**
- Optional but makes it look professional
- Slightly increase contrast
- Slightly increase saturation
- Make code more readable

**Step 9: Final Review (30 min)**
- Watch entire video
- Check audio sync
- Check for cuts/errors
- Verify all annotations visible
- Check text readable
- Verify total time 12-15 min

**Step 10: Export (15 min)**

**Settings:**
- Format: MP4
- Codec: H.264
- Resolution: 1920x1080
- Frame Rate: 30 fps
- Bitrate: 8-10 Mbps (good quality)
- Audio: AAC, 192 kbps

**File size target:** 500MB - 2GB

## Part E: Quality Checklist

**Content:**
- [ ] All 4 vulnerabilities demonstrated
- [ ] Burp Suite shown
- [ ] sqlmap shown
- [ ] Monitoring dashboard shown
- [ ] Patched version shown for each
- [ ] Code comparison included
- [ ] Introduction and conclusion present

**Technical Quality:**
- [ ] 1920x1080 resolution
- [ ] Audio clear, no background noise
- [ ] No long pauses or dead air
- [ ] Mouse movements smooth
- [ ] Text visible and readable
- [ ] Video length 12-15 minutes

**Professional Quality:**
- [ ] Title cards present
- [ ] Annotations helpful
- [ ] Transitions smooth
- [ ] Consistent pacing
- [ ] No "um" or filler words
- [ ] Confident narration

**Functionality:**
- [ ] Opens in VLC/QuickTime
- [ ] File size reasonable (<3GB)
- [ ] Uploaded successfully
- [ ] Playable on various devices

## Part F: Distribution

### Upload Options

**Option 1: YouTube (Unlisted)**
1. Create Google account if needed
2. YouTube Studio → Create → Upload Video
3. Drag video file
4. Title: "CS437 Task 5 - Remote Valve Management System Security Demo - Team [X]"
5. Description:
```
CS 437 Assignment - SCADA Security Demonstration
Task 5: Remote Valve Management System

This video demonstrates:
- 4 security vulnerabilities in a SCADA system
- Exploitation using Burp Suite and sqlmap
- Comprehensive security patches
- Monitoring system effectiveness

Team Members:
- [Name 1]
- [Name 2]
- [Name 3]

Sabancı University - 2025
```
6. Visibility: **Unlisted** (not public, only link access)
7. Not made for kids: No
8. Save

**Option 2: Google Drive**
1. Upload video file
2. Right-click → Share
3. Anyone with link can view
4. Copy link

**Option 3: OneDrive / Dropbox**
- Same process as Google Drive

### Verify Upload

1. Open link in incognito/private window
2. Verify video plays
3. Test on different browser
4. Check on mobile device

## Part G: Troubleshooting

**"Video file too large to upload (>5GB)":**
- Re-export with lower bitrate (5-6 Mbps)
- Use Handbrake to compress:
```bash
brew install handbrake
# Use H.264 preset, RF 23
```

**"Audio out of sync":**
- In editor, manually adjust audio track
- Shift by frames until synced
- Or re-record audio separately (voiceover)

**"Video choppy during screen recording":**
- Close all unnecessary apps during recording
- Lower OBS base resolution to 1280x720
- Use hardware encoding (if available)

**"Can't capture Burp Suite window":**
- Use Display Capture instead of Window Capture
- Or record in full screen mode

**"Background noise in audio":**
- Record in quiet room
- Use noise reduction in DaVinci Resolve
- Or re-record voiceover

**"Title cards don't look professional":**
- Use Canva.com (free templates)
- Keep it simple: white text on dark background
- Use consistent font (Helvetica, Arial)

## Part H: Backup and Archive

**Save multiple versions:**
```bash
testing_results/video/
├── raw_recordings/
│   ├── 01_intro.mov
│   ├── 02_tour.mov
│   └── ...
├── edited/
│   ├── project_file.fcpx (Final Cut)
│   ├── project_file.prproj (Premiere)
│   └── project_file.drp (Resolve)
├── exports/
│   ├── CS437_Task5_TeamX_FINAL_v1.mp4
│   ├── CS437_Task5_TeamX_FINAL_v2.mp4
│   └── CS437_Task5_TeamX_FINAL.mp4  ← Submit this one
└── screenshots_from_video/
    └── (stills for report if needed)
```

**Backup to:**
- External hard drive
- Cloud storage
- Keep for at least 1 year

## Part I: Timeline

**Day 1: Preparation**
- Write script (3 hours)
- Rehearse (2 hours)
- Setup equipment (1 hour)

**Day 2: Recording**
- Morning setup (30 min)
- Record all scenes (4 hours)
- Review footage (30 min)

**Day 3: Editing**
- Import and organize (1 hour)
- Assembly edit (1 hour)
- Fine cutting (2 hours)
- Annotations (1 hour)

**Day 4: Finishing**
- Title cards (1 hour)
- Audio enhancement (1 hour)
- Color correction (30 min)
- Final review (1 hour)
- Export and upload (1 hour)

**Total: ~20 hours** (but can rush in 2-3 days if needed)

## Summary Checklist

- [ ] Script written
- [ ] Storyboard created
- [ ] OBS configured
- [ ] Test recording successful
- [ ] Desktop prepared
- [ ] All scenes recorded
- [ ] Clips imported to editor
- [ ] Video assembled
- [ ] Annotations added
- [ ] Title cards created
- [ ] Audio enhanced
- [ ] Video exported
- [ ] Uploaded and link obtained
- [ ] Playback verified

## Next Steps

**Once video is complete:**
→ **08_FINAL_SUBMISSION.md**

**Estimated time for next step:** 2-3 hours
