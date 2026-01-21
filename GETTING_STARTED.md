# Getting Started Guide - For Beginners

Welcome! This guide will walk you through setting up your JBS FFL website step by step.

## What You Need First

Before we start, you need to have **Node.js** installed on your computer. Node.js is a program that lets you run JavaScript on your computer (not just in a web browser).

### Check if Node.js is Installed

1. Open your **Command Prompt** (Windows) or **Terminal** (Mac)
   - On Windows: Press `Windows Key + R`, type `cmd`, press Enter
   - On Mac: Press `Cmd + Space`, type `Terminal`, press Enter

2. Type this command and press Enter:
   ```
   node --version
   ```

3. If you see a version number (like `v20.10.0`), you're good! ✅
   - If you see an error, you need to install Node.js first
   - Go to https://nodejs.org/ and download the "LTS" version
   - Install it, then come back here

---

## Step 1: Navigate to Your Project Folder

You need to "go into" the project folder using the command line.

**⚠️ Important:** If your project is on a network drive (path starts with `\\`), see `FIX_UNC_PATH.md` for special instructions!

1. **Open PowerShell** (recommended) or Command Prompt
   - PowerShell: Press `Windows Key + X`, click "Windows PowerShell" or "Terminal"
   - Command Prompt: Press `Windows Key + R`, type `cmd`, press Enter

2. Navigate to your project:
   
   **If using PowerShell:**
   ```
   cd "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
   ```
   
   **If using Command Prompt (and you get a UNC path error):**
   ```
   pushd "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
   ```
   (See `FIX_UNC_PATH.md` for more details)
   
   **What this does:** `cd` or `pushd` moves you into the folder where your website files are.

3. Press Enter. You should now be "inside" the fantasy-football folder.

---

## Step 2: Install Dependencies

**What are "dependencies"?**
- Your website uses code libraries (like React, Next.js, Tailwind CSS) that other people wrote
- These libraries aren't included in your project files - they need to be downloaded
- `npm install` downloads all the libraries your project needs

**Need more help?** 
- 📋 See `STEP_2_QUICK_CHECKLIST.md` for a simple checklist
- 📖 See `STEP_2_DETAILED.md` for detailed explanations and troubleshooting

**How to do it:**

1. Make sure you're in the `fantasy-football` folder (from Step 1)

2. Type this command:
   ```
   npm install
   ```

3. Press Enter and wait. This might take 2-5 minutes.

4. You'll see lots of text scrolling by - that's normal! It's downloading packages.

5. When it's done, you'll see something like:
   ```
   added 500 packages in 2m
   ```

6. You should now see a new folder called `node_modules` in your project - that's where all the downloaded code lives.

**Troubleshooting:**
- If you see an error about "npm is not recognized", Node.js isn't installed correctly
- If it takes a very long time, that's normal - just wait!
- **For detailed troubleshooting, see `STEP_2_DETAILED.md`**

---

## Step 3: Start the Development Server

**What is a "development server"?**
- A development server is like a mini-website running on your computer
- It lets you see your website in your browser at `http://localhost:3000`
- When you make changes to your code, the website automatically updates!

**How to do it:**

1. Make sure you're still in the `fantasy-football` folder

2. Type this command:
   ```
   npm run dev
   ```

3. Press Enter

4. You should see output like this:
   ```
   ▲ Next.js 14.2.5
   - Local:        http://localhost:3000
   - Ready in 2.3s
   ```

5. **Keep this window open!** The server is now running. If you close it, your website will stop working.

---

## Step 4: View Your Website

1. Open your web browser (Chrome, Firefox, Edge, etc.)

2. In the address bar, type:
   ```
   http://localhost:3000
   ```

3. Press Enter

4. You should see your JBS FFL website! 🎉

5. Try clicking the navigation links:
   - Home
   - Trophy Room (you should see a rotating trophy!)
   - All-Time Records
   - Head-to-Head
   - Championship History

**What you're seeing:**
- This is your website running on your own computer
- Only you can see it (it's not on the internet yet)
- The address `localhost` means "this computer"

---

## Step 5: Make Changes to Your Website

Now let's update the sample data with your real league information!

### How to Edit Files

1. **Keep the server running** (the `npm run dev` window should still be open)

2. Open the `fantasy-football` folder in your code editor (VS Code, Cursor, etc.)

3. Find the file you want to edit. Here are the main ones:

   - **Home Page:** `app/page.tsx`
   - **Championship History:** `app/championship-history/page.tsx`
   - **All-Time Records:** `app/all-time-records/page.tsx`
   - **Head-to-Head:** `app/head-to-head/page.tsx`

4. **Edit the data:**
   - Look for arrays (lists) that start with `[` and contain data
   - Replace the sample data with your real data
   - Save the file (Ctrl+S or Cmd+S)

5. **See your changes:**
   - Go back to your browser at `http://localhost:3000`
   - The page should automatically refresh and show your changes!
   - If it doesn't refresh automatically, press F5 to refresh

### Example: Updating Championship History

Let's say you want to add your 2024 champion:

1. Open `app/championship-history/page.tsx`

2. Find the `championships` array (it starts around line 6)

3. You'll see entries like:
   ```typescript
   { year: 2024, champion: "Manager Name", runnerUp: "Manager Name", score: "145.2 - 132.8" },
   ```

4. Replace it with your real data:
   ```typescript
   { year: 2024, champion: "John Smith", runnerUp: "Jane Doe", score: "165.4 - 142.1" },
   ```

5. Save the file

6. Check your browser - the change should appear!

### Example: Updating All-Time Records

1. Open `app/all-time-records/page.tsx`

2. Find the `records` array

3. Update entries like:
   ```typescript
   {
     category: "Most Championships",
     record: "5 Championships",
     holder: "Manager Name",  // Change this!
     details: "1999, 2003, 2007, 2012, 2018",  // Change this!
   },
   ```

4. Save and see your changes!

---

## Step 6: Stop the Server

When you're done working:

1. Go back to the Command Prompt/Terminal window where `npm run dev` is running

2. Press `Ctrl + C` (or `Cmd + C` on Mac)

3. The server will stop

4. You can close that window

**To start it again later:** Just run `npm run dev` again from the `fantasy-football` folder!

---

## Common Questions

**Q: Do I need to run `npm install` every time?**
A: No! Only the first time, or when new dependencies are added.

**Q: Can I close the browser?**
A: Yes! The server keeps running. Just reopen `http://localhost:3000` when you want to see your site.

**Q: What if I see an error?**
A: 
- Check that you're in the right folder
- Make sure Node.js is installed
- Make sure you ran `npm install` first
- Read the error message - it usually tells you what's wrong

**Q: How do I put this on the internet?**
A: That's a later step! For now, you're just running it locally. When you're ready, you can use services like Vercel, Netlify, or GitHub Pages.

---

## Quick Reference

**Start working:**
```bash
cd "\\rbfil21\Users$\jpassanante\Documents\vibe-lab\fantasy-football"
npm run dev
```

**View website:**
Open browser to `http://localhost:3000`

**Stop server:**
Press `Ctrl + C` in the terminal

**Edit files:**
Open in your code editor, make changes, save

---

Good luck! 🏈
