# How to Get ESPN Cookies for Authentication

Your league requires authentication. Follow these steps to get your cookies:

## Step-by-Step Instructions

### 1. Log into ESPN Fantasy Football
- Go to https://fantasy.espn.com/football
- Log in with your ESPN account
- Navigate to your league (League ID: 420782)

### 2. Open Developer Tools
- **Chrome/Edge**: Press `F12` or right-click → "Inspect"
- **Firefox**: Press `F12` or right-click → "Inspect Element"

### 3. Find the Cookies
- Click on the **Application** tab (Chrome) or **Storage** tab (Firefox)
- In the left sidebar, expand **Cookies**
- Click on `https://fantasy.espn.com`

### 4. Copy the Cookie Values
You need two cookies:
- **`SWID`** - Copy the entire value (it will look like `{A1B2C3D4-...}`)
- **`espn_s2`** - Copy the entire value (it's a long string)

### 5. Create cookies.txt File
- In the `scripts/` folder, create a new file named `cookies.txt`
- Paste your cookies in this exact format (replace with your actual values):
  ```
  SWID={A1B2C3D4-E5F6-7890-ABCD-EF1234567890}; espn_s2=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1e2f3g4h5i6j7k8l9m0n1o2p3q4r5s6t7u8v9w0x1y2z3a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9a0b1c2d3e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3y4z5
  ```

### 6. Save and Run
- Save the `cookies.txt` file
- Run the scraper: `python scrape_espn_data.py`
- The script will automatically read the cookies from the file

## Example cookies.txt Format

```
SWID={12345678-1234-1234-1234-123456789ABC}; espn_s2=ABC123DEF456GHI789JKL012MNO345PQR678STU901VWX234YZ567ABC890DEF123GHI456JKL789MNO012PQR345STU678VWX901YZ234ABC567DEF890GHI123JKL456MNO789PQR012STU345VWX678YZ901
```

## Security Note

⚠️ **Important**: Your cookies are like passwords. Don't share them or commit them to version control!
- The `cookies.txt` file is already in `.gitignore` (if you're using git)
- Never share your cookies with others
- If your cookies are compromised, you can regenerate them by logging out and back in

## Troubleshooting

**"Authentication required" error still appears:**
- Make sure the cookies.txt file is in the `scripts/` folder
- Check that the format is exactly: `SWID={value}; espn_s2={value}`
- Make sure there are no extra spaces or line breaks
- Try logging out and back into ESPN, then get fresh cookies

**Cookies expired:**
- Cookies can expire after some time
- Just get new cookies following the steps above
- Replace the old values in cookies.txt
