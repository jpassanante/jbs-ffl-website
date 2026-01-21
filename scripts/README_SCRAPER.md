# ESPN Fantasy Football Data Scraper

This script scrapes historical data from your ESPN Fantasy Football league.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the scraper:**
   ```bash
   python scrape_espn_data.py
   ```

   **Test mode** (to diagnose issues):
   ```bash
   python scrape_espn_data.py --test
   ```
   This will test a single season (2024) and show detailed response information.

## What It Does

The script will:
- Find all available ESPN seasons for your league (2009-2025)
  - Note: 1999-2008 seasons were on CBS Sportsline and are not included
  - **Historical seasons (2009-2017)** use ESPN's `leagueHistory` endpoint
  - **Modern seasons (2018+)** use the standard API endpoint
  - Some older seasons may not be available if ESPN has purged the data
- For each season, extract **regular season data only**:
  - Team information (names, managers, records)
  - Weekly matchups (regular season weeks only)
    - Pre-2021: Weeks 1-13 (13-week regular season)
    - 2021+: Weeks 1-14 (14-week regular season, NFL expanded to 17 games)
  - Regular season standings (wins, losses, points for/against)
  - **Note:** Playoff data is not scraped. Championship results are maintained separately in `champions.js`
- Save data as JSON files in the `data/` directory

## Output Files

- `data/espn_season_YYYY.json` - Individual season data (regular season only)
- `data/espn_all_seasons.json` - Combined data for all seasons

### Data Structure

Each season file contains:
- `season`: Year (e.g., 2023)
- `teams`: Object mapping manager names to team information (id, name, etc.)
- `matchups`: Array of weekly matchups with:
  - `week`: Week number (1-13 for pre-2021, 1-14 for 2021+)
  - `is_playoff`: Always `false` (regular season only)
  - `home_manager` / `away_manager`: Manager names
  - `home_score` / `away_score`: Points scored
  - `winner_manager`: Winner of the matchup
- `standings`: Array of teams sorted by record, with:
  - `manager`: Manager name
  - `wins`, `losses`, `ties`: Record
  - `points_for`: Total points scored
  - `points_against`: Total points allowed
- `playoff_results`: Empty object (playoffs not scraped)

## Authentication

If your league is private (which it appears to be), you need to add authentication cookies.

### Option 1: Using cookies.txt file (Recommended)

1. **Get your ESPN cookies:**
   - Log into ESPN Fantasy Football in your browser
   - Open Developer Tools (F12)
   - Go to the **Application** tab (Chrome) or **Storage** tab (Firefox)
   - Click on **Cookies** in the left sidebar
   - Select `https://fantasy.espn.com`
   - Find the `SWID` and `espn_s2` cookies
   - Copy their values

2. **Create a cookies.txt file:**
   - In the `scripts/` folder, create a file named `cookies.txt`
   - Paste your cookies in this format:
     ```
     SWID={your-swid-value}; espn_s2={your-espn_s2-value}
     ```
   - The script will automatically read this file

### Option 2: Using environment variable

Set an environment variable:
```bash
# Windows PowerShell
$env:ESPN_COOKIES="SWID={value}; espn_s2={value}"

# Windows CMD
set ESPN_COOKIES=SWID={value}; espn_s2={value}

# Linux/Mac
export ESPN_COOKIES="SWID={value}; espn_s2={value}"
```

### Getting Cookie Values (Detailed Steps)

1. **Log into ESPN Fantasy Football** in your browser
2. **Open Developer Tools** (Press F12)
3. **Go to Application tab** (Chrome) or **Storage tab** (Firefox)
4. **Navigate to Cookies** → `https://fantasy.espn.com`
5. **Find these cookies:**
   - `SWID` - Copy the entire value (looks like: `{...}`)
   - `espn_s2` - Copy the entire value (long string)
6. **Create cookies.txt** with format:
   ```
   SWID={paste-swid-here}; espn_s2={paste-espn_s2-here}
   ```

## Troubleshooting

**"No seasons found" error:**
- Run in test mode first: `python scrape_espn_data.py --test`
- This will show you exactly what ESPN is returning
- Verify the league ID is correct (420782)
- Check if your cookies are valid (they may have expired)
- Make sure cookies.txt format is correct: `SWID={value}; espn_s2={value}`
- Try logging out and back into ESPN, then get fresh cookies

**Rate limiting:**
- The script includes delays between requests
- If you get blocked, increase the `time.sleep()` values

**Missing data:**
- 1999-2008 seasons were on CBS Sportsline and won't be scraped
- You'll need to manually enter data for those seasons (already done in `data/champions.js`)
- Some ESPN seasons (especially 2009-2017) may not be available if:
  - The league data was purged by ESPN
  - The league became inactive and wasn't renewed
  - ESPN's historical data access is restricted
- If a season returns 404 (Not Found), that season's data is likely no longer accessible via ESPN's API

## Next Steps

After running the scraper:
1. Review the JSON files to verify data accuracy
2. Use the regular season data for:
   - Building head-to-head records
   - Calculating all-time statistics
   - Displaying weekly matchup history
   - Showing regular season champions and most points (from standings)
3. Championship results (champion, runner-up, third place) are maintained separately in `data/champions.js` and are not scraped from ESPN
