"""
Inspect raw ESPN API matchup object to see all available fields
This will help identify fields that distinguish real games from projections
"""
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def inspect_raw_matchup():
    """Inspect a raw matchup object from ESPN API"""
    # Try to find a raw API response file, or load from scraped data
    # and show what fields we're currently capturing vs what might be available
    
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print("Error: espn_all_seasons.json not found")
        return
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    # Get 2025 data
    season_2025 = all_data.get('2025', {})
    matchups = season_2025.get('matchups', [])
    
    if not matchups:
        print("No matchups found for 2025")
        return
    
    print("="*70)
    print("Inspecting Matchup Object Structure")
    print("="*70)
    
    # Show first matchup with all its fields
    print("\nSample matchup object (all fields we're currently capturing):")
    sample = matchups[0]
    print(json.dumps(sample, indent=2))
    
    print("\n" + "="*70)
    print("Note: This shows what we're CURRENTLY capturing.")
    print("The raw ESPN API response may have additional fields we're not storing.")
    print("\nTo see raw API fields, we would need to:")
    print("  1. Make a direct API call to ESPN")
    print("  2. Inspect the raw 'schedule' array items")
    print("\nPossible fields in raw API that might help:")
    print("  - matchupType (scheduled vs projected)")
    print("  - matchupPeriodId")
    print("  - id (unique matchup ID)")
    print("  - winner (different from winner_id?)")
    print("  - isBye")
    print("  - playoffTierType")
    print("  - Any field indicating 'completed' vs 'projected'")

if __name__ == "__main__":
    inspect_raw_matchup()
