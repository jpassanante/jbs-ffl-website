"""
Check what matchup_type values are in the newly scraped data
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def check_matchup_types():
    """Check what matchup_type values exist in the data"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print("Error: espn_all_seasons.json not found")
        return
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    print("="*70)
    print("Checking matchup_type Values in Scraped Data")
    print("="*70)
    
    matchup_types = defaultdict(int)
    sample_matchups = []
    
    for season_str, data in all_data.items():
        matchups = data.get('matchups', [])
        for matchup in matchups[:50]:  # Check first 50 from each season
            mtype = matchup.get('matchup_type')
            matchup_types[mtype] += 1
            if len(sample_matchups) < 5 and mtype is not None:
                sample_matchups.append({
                    'season': season_str,
                    'week': matchup.get('week'),
                    'matchup_type': mtype,
                    'home_id': matchup.get('home_team_id'),
                    'away_id': matchup.get('away_team_id'),
                    'winner_id': matchup.get('winner_id'),
                })
    
    print(f"\nMatchup type distribution:")
    for mtype, count in sorted(matchup_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {mtype}: {count} matchups")
    
    print(f"\nSample matchups with matchup_type:")
    for i, m in enumerate(sample_matchups, 1):
        print(f"  {i}. Season {m['season']}, Week {m['week']}: type={m['matchup_type']}, "
              f"Teams {m['home_id']} vs {m['away_id']}, winner={m['winner_id']}")
    
    # Check if we have the field at all
    total_matchups = sum(len(data.get('matchups', [])) for data in all_data.values())
    matchups_with_type = sum(1 for data in all_data.values() 
                            for m in data.get('matchups', []) 
                            if m.get('matchup_type') is not None)
    
    print(f"\n{'='*70}")
    print(f"Summary:")
    print(f"  Total matchups: {total_matchups}")
    print(f"  Matchups with matchup_type: {matchups_with_type}")
    print(f"  Matchups without matchup_type: {total_matchups - matchups_with_type}")
    
    if matchups_with_type == 0:
        print("\n⚠ WARNING: No matchups have matchup_type field!")
        print("  The scraper may not be capturing this field correctly.")
    else:
        print(f"\n✓ Found matchup_type in {matchups_with_type}/{total_matchups} matchups")

if __name__ == "__main__":
    check_matchup_types()
