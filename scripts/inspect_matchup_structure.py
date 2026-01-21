"""
Inspect the raw ESPN matchup structure to find fields that indicate scheduled games
"""
import json
import requests
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def inspect_raw_espn_matchup(season: int = 2024, week: int = 1):
    """Inspect a raw ESPN API response to see all available fields"""
    
    # Try to load from existing data first
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if all_seasons_file.exists():
        with open(all_seasons_file, 'r') as f:
            all_data = json.load(f)
        
        season_data = all_data.get(str(season), {})
        matchups = season_data.get('matchups', [])
        
        week_matchups = [m for m in matchups if m.get('week') == week]
        
        if week_matchups:
            print(f"Found {len(week_matchups)} matchups for {season} Week {week} in saved data")
            print("\nSample matchup structure (from saved data):")
            print(json.dumps(week_matchups[0], indent=2))
            return
    
    # If no saved data, try to fetch directly (requires cookies)
    print("No saved data found. To inspect raw API response, you would need to:")
    print("1. Make a direct API call to ESPN")
    print("2. Inspect the raw 'schedule' array structure")
    print("\nThe scraper extracts these fields from each matchup:")
    print("  - home/away team objects with teamId, totalPoints")
    print("  - But the raw API may have additional fields like:")
    print("    * matchupType (scheduled vs projected)")
    print("    * matchupPeriodId")
    print("    * playoffTierType")
    print("    * winner (indicates completed game)")
    print("    * isBye")
    print("\nWe need to check the raw API response to see what's available.")

if __name__ == "__main__":
    inspect_raw_espn_matchup()
