# Step 2: Install Dependencies - Detailed Guide

This guide will walk you through installing dependencies step-by-step with lots of detail and troubleshooting help.

---

## Before You Start: Verify You're Ready

### Check 1: Are you in the right folder?

1. Look at your Command Prompt/Terminal window
2. You should see something like:
   ```
   C:\Users\jpassanante\Documents\vibe-lab\fantasy-football>
   ```
   or
   ```
   \\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football>
   ```

3. **If you're NOT in the fantasy-football folder:**
   - **If using PowerShell:** Type this command and press Enter:
     ```
     cd "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
     ```
   - **If using Command Prompt and you get a UNC path error:** Use `pushd` instead:
     ```
     pushd "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
     ```
   - See `FIX_UNC_PATH.md` for more help with network paths
   - Press Enter
   - You should now be in the right place

### Check 2: Can you see the package.json file?

1. Type this command:
   ```
   dir
   ```
   (On Mac/Linux, use `ls` instead)

2. You should see a file called `package.json` in the list
   - If you don't see it, you're in the wrong folder
   - Go back to Check 1 and navigate to the correct folder

---

## The Actual Installation

### Step 1: Type the command

1. Make sure your cursor is at the end of the command prompt line
2. Type exactly this (don't include the quotes):
   ```
   npm install
   ```

3. Press Enter

### Step 2: What you'll see (and what it means)

**Immediately after pressing Enter, you might see:**

```
npm WARN deprecated some-package@1.0.0: This package is deprecated
```

**This is normal!** It's just a warning, not an error. Keep going.

**Then you'll see lots of text scrolling:**

```
added 1 package, and audited 500 packages in 15s
found 0 vulnerabilities
```

**What's happening:**
- `added 1 package` = npm is downloading and installing packages
- The number will keep going up (1, 2, 3, 10, 50, 100...)
- `audited 500 packages` = npm is checking for security issues
- This is GOOD! It means it's working

**The scrolling text might look like:**
```
npm http fetch GET 200 https://registry.npmjs.org/react 123ms
npm http fetch GET 200 https://registry.npmjs.org/next 145ms
npm timing stage:loadTrees Completed in 1234ms
```

**This is also normal!** It's showing you what it's downloading. You don't need to read it.

### Step 3: Wait for it to finish

**How long will it take?**
- First time: 2-5 minutes (sometimes longer on slow internet)
- It depends on your internet speed
- Be patient! Don't close the window

**What you'll see when it's done:**

```
added 500 packages, and audited 500 packages in 2m

found 0 vulnerabilities
```

**Success! ✅** This means everything installed correctly!

---

## Common Problems and Solutions

### Problem 1: "npm is not recognized"

**Error message:**
```
'npm' is not recognized as an internal or external command,
operable program or batch file.
```

**What this means:**
- Node.js isn't installed, OR
- Node.js is installed but not in your system PATH

**How to fix it:**

1. **First, check if Node.js is installed:**
   - Type: `node --version`
   - Press Enter
   - If you see a version number (like `v20.10.0`), Node.js IS installed
   - If you see an error, Node.js is NOT installed

2. **If Node.js is NOT installed:**
   - Go to https://nodejs.org/
   - Download the "LTS" version (it's the big green button)
   - Run the installer
   - **Important:** During installation, make sure "Add to PATH" is checked
   - Restart your Command Prompt/Terminal after installing
   - Try `npm install` again

3. **If Node.js IS installed but npm still doesn't work:**
   - Close your Command Prompt/Terminal
   - Open a NEW Command Prompt/Terminal
   - Try again
   - If it still doesn't work, you may need to reinstall Node.js with "Add to PATH" checked

### Problem 2: "Cannot find module" or "package.json not found"

**Error message:**
```
npm ERR! code ENOENT
npm ERR! syscall open
npm ERR! path C:\...\package.json
npm ERR! errno -4058
npm ERR! enoent Could not read package.json
```

**What this means:**
- You're not in the fantasy-football folder
- OR the package.json file doesn't exist

**How to fix it:**

1. Check what folder you're in:
   ```
   cd
   ```
   (This shows your current location)

2. Navigate to the correct folder:
   ```
   cd "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
   ```

3. Verify you're in the right place:
   ```
   dir
   ```
   (You should see package.json)

4. Try `npm install` again

### Problem 3: "Permission denied" or "Access denied"

**Error message:**
```
npm ERR! code EACCES
npm ERR! syscall access
```

**What this means:**
- Windows/Mac is blocking npm from writing files
- Usually happens if you're in a protected folder

**How to fix it:**

1. **On Windows:**
   - Right-click on Command Prompt
   - Select "Run as administrator"
   - Navigate to your folder again
   - Try `npm install` again

2. **On Mac:**
   - You might need to use `sudo` (not recommended for beginners)
   - Or move your project to a folder you own (like Documents)

### Problem 4: "Network timeout" or "Connection error"

**Error message:**
```
npm ERR! network timeout
npm ERR! code ETIMEDOUT
```

**What this means:**
- Your internet connection is slow or unstable
- OR npm's servers are busy

**How to fix it:**

1. **Check your internet connection:**
   - Try opening a website in your browser
   - If websites don't load, fix your internet first

2. **Wait and try again:**
   - Sometimes npm's servers are just busy
   - Wait 5 minutes and try again

3. **Use a different registry (advanced):**
   - If this keeps happening, you might need to configure npm to use a different server
   - This is more advanced - ask for help if needed

### Problem 5: Installation seems stuck

**What you see:**
- The command ran, but nothing is happening
- No text is scrolling
- It's been more than 5 minutes

**How to fix it:**

1. **Wait a bit longer:**
   - Sometimes it takes a while to start
   - Give it 2-3 more minutes

2. **Check if it's actually working:**
   - Look for a blinking cursor
   - If the cursor is blinking, it's still working (just slowly)
   - Be patient!

3. **If it's truly stuck:**
   - Press `Ctrl + C` to stop it
   - Check your internet connection
   - Try again

---

## After Installation: Verify It Worked

### Check 1: Look for the node_modules folder

1. Type this command:
   ```
   dir
   ```

2. You should see a folder called `node_modules`
   - This folder contains all the downloaded packages
   - It might be very large (hundreds of MB)
   - **If you see this folder, installation worked! ✅**

### Check 2: Check the package-lock.json file

1. Type `dir` again (or `ls` on Mac)

2. You should see a file called `package-lock.json`
   - This file was created during installation
   - It lists all the exact versions of packages installed
   - **If you see this file, installation worked! ✅**

---

## Visual Guide: What Success Looks Like

**Before installation:**
```
C:\...\fantasy-football> npm install
```

**During installation (lots of scrolling text):**
```
npm http fetch GET 200 https://registry.npmjs.org/react 123ms
npm http fetch GET 200 https://registry.npmjs.org/next 145ms
npm timing stage:loadTrees Completed in 1234ms
... (more lines scrolling) ...
```

**After installation (success!):**
```
added 500 packages, and audited 500 packages in 2m

found 0 vulnerabilities
```

**Your prompt is back:**
```
C:\...\fantasy-football> _
```
(The underscore is your blinking cursor, ready for the next command)

---

## Next Steps

Once `npm install` completes successfully:

1. ✅ You should see "found 0 vulnerabilities" (or a low number)
2. ✅ You should see a `node_modules` folder
3. ✅ You're ready for Step 3: Start the Development Server

**Move on to Step 3 when you see:**
```
added XXX packages, and audited XXX packages in Xm
found 0 vulnerabilities
```

---

## Still Having Problems?

If you're still stuck after trying these solutions:

1. **Copy the exact error message** you're seeing
2. **Note what step you were on** when the error happened
3. **Check:**
   - Are you in the fantasy-football folder? (type `cd` to check)
   - Is Node.js installed? (type `node --version` to check)
   - Is your internet working? (try opening a website)

4. **Ask for help** with:
   - The exact error message
   - What you've already tried
   - Your operating system (Windows/Mac)

Good luck! 🚀
