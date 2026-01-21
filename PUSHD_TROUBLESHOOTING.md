# Troubleshooting pushd in PowerShell

## The Issue

If `pushd` isn't showing a drive letter change, it might be because PowerShell handles it differently, or there's a network issue.

## Try This Instead

### Option 1: Check if pushd worked (it might have, just looks different)

After running `pushd`, check your current location:

```powershell
pwd
```

or

```powershell
Get-Location
```

If it shows a drive letter path (like `Z:\`), then `pushd` worked! The prompt might just not show it the same way.

### Option 2: Use pushd in CMD instead

PowerShell's `pushd` might work differently. Try using Command Prompt:

1. **Open Command Prompt** (not PowerShell):
   - Press `Windows Key + R`
   - Type `cmd`
   - Press Enter

2. **In CMD, run:**
   ```
   pushd "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
   ```

3. **You should see:**
   ```
   Z:\>
   ```

4. **Then run:**
   ```
   npm run dev
   ```

### Option 3: Map the drive manually first

If `pushd` isn't working, map the drive manually:

1. **In PowerShell, run:**
   ```powershell
   net use Z: "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
   ```

2. **Then navigate:**
   ```powershell
   cd Z:\fantasy-football
   ```

3. **Verify:**
   ```powershell
   dir
   ```
   (You should see the app folder)

4. **Run:**
   ```powershell
   npm run dev
   ```

### Option 4: Check what pushd actually did

After running `pushd`, try:

```powershell
Get-PSDrive
```

This shows all drives. Look for a new drive letter (like Z:). If you see one, `pushd` worked and you can just `cd` to that drive.

## Quick Test

Run this to see where you are:

```powershell
pushd "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
pwd
dir
```

If `pwd` shows a drive letter path and `dir` shows your files, you're good! Just run `npm run dev`.

## Recommendation

If `pushd` isn't working in PowerShell, I'd recommend **Option 2** (using CMD) or **Option 3** (manually mapping with `net use`). Both should work reliably.
