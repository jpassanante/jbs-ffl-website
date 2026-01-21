"""
Verify head-to-head counts after deduplication
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def load_all_seasons():
    """Load all scraped season data"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print(f"Error: {all_seasons_file} not found")
        return {}
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    return {int(k): v for k, v in all_data.items()}

def verify_counts():
    """Verify head-to-head counts"""
    print("=" * 70)
    print("Verifying Head-to-Head Counts After Deduplication")
    print("=" * 70)
    
    espn_data = load_all_seasons()
    
    # Track unique matchups by team ID
    seen_matchups = set()
    unique_matchups_by_season = defaultdict(int)
    manager_games = defaultdict(int)
    
    MANAGER_MAPPING = {
        'benhkline': 'Ben',
        'plazaroff': 'Peter',
        'lannybenson13': 'Lanny',
        'jpassana': 'Joey',
        'tybear612': 'Tyler',
        'vchapli1': 'Vernon',
        'johnnyhubes123': 'John',
        'mendy1399': 'Matt',
        'ugadogs34': 'Ted',
        'jayd3456': 'Jason',
        'tyfredstl': 'Ty',
    }
    
    def extract_first_name(display_name: str) -> str:
        return MANAGER_MAPPING.get(display_name.lower(), display_name)
    
    for season, data in espn_data.items():
        matchups = data.get('matchups', [])
        
        for matchup in matchups:
            home_id = matchup.get('home_team_id')
            away_id = matchup.get('away_team_id')
            home_mgr = matchup.get('home_manager')
            away_mgr = matchup.get('away_manager')
            week = matchup.get('week', 0)
            
            # Skip invalid matchups
            if home_id is None or away_id is None:
                continue
            if not home_mgr or not away_mgr:
                continue
            if 'Team None' in home_mgr or 'Team None' in away_mgr:
                continue
            
            # Create unique key
            matchup_key = (season, week, tuple(sorted([home_id, away_id])))
            
            # Count unique matchups
            if matchup_key not in seen_matchups:
                seen_matchups.add(matchup_key)
                unique_matchups_by_season[season] += 1
                
                # Count games per manager
                home_first = extract_first_name(home_mgr)
                away_first = extract_first_name(away_mgr)
                if home_first != away_first:
                    manager_games[home_first] += 1
                    manager_games[away_first] += 1
    
    print(f"\nTotal unique matchups (after deduplication): {len(seen_matchups)}")
    print(f"Expected: ~1,755 matchups (27 seasons × ~65 per season)")
    
    print(f"\nUnique matchups by season:")
    for season in sorted(unique_matchups_by_season.keys()):
        count = unique_matchups_by_season[season]
        expected = 65 if season < 2021 else 70  # 13 weeks × 5 games or 14 weeks × 5 games
        print(f"  {season}: {count} unique matchups (expected ~{expected})")
    
    print(f"\nTotal games per manager (should be ~351-378 over 27 seasons):")
    for manager in sorted(manager_games.keys()):
        games = manager_games[manager]
        print(f"  {manager}: {games} games")
    
    # Calculate expected
    total_expected = sum(65 if s < 2021 else 70 for s in unique_matchups_by_season.keys())
    print(f"\n\nExpected total unique matchups: ~{total_expected}")
    print(f"Actual total unique matchups: {len(seen_matchups)}")
    print(f"Difference: {len(seen_matchups) - total_expected}")
    
    print("\n" + "=" * 70)
    print("Verification Complete")
    print("=" * 70)

if __name__ == "__main__":
    verify_counts()
