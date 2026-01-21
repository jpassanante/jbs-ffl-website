# Fix: UNC Path Error in Command Prompt

You're getting this error because your project is on a network drive (`\\rbfil21\...`), and Windows Command Prompt (CMD) can't use network paths directly.

## Solution 1: Use PowerShell Instead (Easiest! ⭐)

PowerShell supports UNC paths, so this is the easiest solution.

### Steps:

1. **Open PowerShell instead of Command Prompt:**
   - Press `Windows Key + X`
   - Click "Windows PowerShell" or "Terminal"
   - OR press `Windows Key + R`, type `powershell`, press Enter

2. **Navigate to your folder:**
   ```
   cd "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
   ```

3. **Verify you're in the right place:**
   ```
   dir
   ```
   (You should see package.json)

4. **Now run npm install:**
   ```
   npm install
   ```

**That's it!** PowerShell works just like Command Prompt, but it supports network paths.

---

## Solution 2: Use `pushd` Command (Works in CMD)

The `pushd` command automatically maps a UNC path to a temporary drive letter.

### Steps:

1. **Open Command Prompt** (keep using CMD if you prefer)

2. **Use pushd instead of cd:**
   ```
   pushd "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
   ```

3. **You'll see something like:**
   ```
   Z:\> 
   ```
   (It automatically mapped the network path to drive Z:)

4. **Verify you're in the right place:**
   ```
   dir
   ```
   (You should see package.json)

5. **Run npm install:**
   ```
   npm install
   ```

6. **When you're done, you can go back:**
   ```
   popd
   ```
   (This unmaps the temporary drive)

**Note:** The drive letter (Z:) might be different - that's fine!

---

## Solution 3: Map Network Drive Permanently

This maps your network folder to a drive letter (like D: or E:) so you can use it like a regular drive.

### Steps:

1. **Open File Explorer** (Windows Key + E)

2. **In the address bar, type:**
   ```
   \\rbfil21\Users$\jpassanante\Documents\vibe-lab
   ```
   Press Enter

3. **Right-click on the `fantasy-football` folder**

4. **Select "Map network drive..."**

5. **Choose a drive letter** (like Z: or Y:)

6. **Check "Reconnect at sign-in"** if you want it to stay mapped

7. **Click "Finish"**

8. **Now in Command Prompt, you can use:**
   ```
   cd Z:\fantasy-football
   ```
   (Use whatever drive letter you chose)

---

## Which Solution Should You Use?

- **Solution 1 (PowerShell)** - ⭐ **Recommended!** Easiest, no extra steps
- **Solution 2 (pushd)** - Good if you want to stick with CMD
- **Solution 3 (Map Drive)** - Good if you'll be working with this folder often

---

## Quick Reference

**Using PowerShell (Solution 1):**
```powershell
cd "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
npm install
```

**Using CMD with pushd (Solution 2):**
```cmd
pushd "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
npm install
```

**Using mapped drive (Solution 3):**
```cmd
cd Z:\fantasy-football
npm install
```

---

## After This Works

Once you get past the UNC path issue and `npm install` completes, you can continue with the rest of the guide!

Good luck! 🚀
