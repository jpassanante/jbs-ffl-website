# Fix: Next.js Can't Find App Directory (UNC Path Issue)

## The Problem

Next.js is having trouble with the UNC (network) path. Even though you're in the right folder, Next.js internally uses CMD.EXE which doesn't support UNC paths, so it defaults to the Windows directory and can't find your `app` folder.

## Solution: Use `pushd` to Map the Drive

The easiest fix is to use `pushd` to temporarily map your network folder to a drive letter.

### Steps:

1. **Stop the current server** (if it's still running):
   - Press `Ctrl + C` in your PowerShell window

2. **Use pushd to map the drive:**
   ```powershell
   pushd "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
   ```
   
   You should see something like:
   ```
   Z:\>
   ```
   (The drive letter might be different - that's fine!)

3. **Verify you can see the app folder:**
   ```powershell
   dir
   ```
   You should see the `app` folder in the list.

4. **Now run the dev server:**
   ```powershell
   npm run dev
   ```

5. **It should work now!** You should see:
   ```
   ▲ Next.js 14.2.35
   - Local:        http://localhost:3000
   ✓ Ready in X.Xs
   ```

## Alternative: Map Drive Permanently

If you want to avoid using `pushd` every time, you can map the network drive permanently:

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

8. **Now you can use:**
   ```powershell
   cd Z:\fantasy-football
   npm run dev
   ```
   (Use whatever drive letter you chose)

## Why This Happens

Next.js uses some internal processes that rely on CMD.EXE, which doesn't support UNC paths. By mapping the network drive to a drive letter (like Z:), everything works normally.

## Quick Reference

**Using pushd (temporary):**
```powershell
pushd "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
npm run dev
# When done, you can use: popd
```

**Using mapped drive (permanent):**
```powershell
cd Z:\fantasy-football
npm run dev
```

Good luck! 🚀
