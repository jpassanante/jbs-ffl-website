"""
Verify if the first 5 unique team pairs encountered (in order) are always the actual scheduled games
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

# Manager name mapping
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

def get_2025_actual_schedule():
    """Return the actual 2025 schedule"""
    return {
        1: [(1, 8), (10, 6), (7, 9), (4, 2), (5, 11)],
        2: [(7, 10), (8, 4), (1, 5), (6, 2), (9, 11)],
        3: [(5, 4), (2, 10), (11, 7), (6, 8), (9, 1)],
        4: [(11, 2), (4, 6), (5, 9), (10, 8), (7, 1)],
        5: [(9, 6), (8, 2), (1, 11), (10, 4), (7, 5)],
        6: [(6, 9), (2, 8), (11, 1), (4, 10), (5, 7)],
        7: [(8, 6), (1, 2), (11, 9), (10, 5), (7, 4)],
        8: [(9, 7), (4, 1), (2, 11), (6, 10), (5, 8)],
        9: [(1, 6), (2, 8), (9, 7), (4, 10), (11, 5)],
        10: [(7, 8), (6, 10), (5, 1), (2, 4), (11, 9)],
        11: [(5, 10), (4, 8), (7, 11), (2, 6), (1, 9)],
        12: [(11, 4), (10, 2), (9, 5), (8, 6), (1, 7)],
        13: [(9, 2), (6, 4), (11, 1), (8, 10), (5, 7)],
        14: [(8, 1), (10, 7), (4, 5), (2, 11), (6, 9)],
    }

def verify_first_5_pattern():
    """Check if first 5 unique pairs = actual games"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print("Error: espn_all_seasons.json not found")
        return
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    season_2025 = all_data.get('2025', {})
    matchups = season_2025.get('matchups', [])
    actual_schedule = get_2025_actual_schedule()
    
    print("="*70)
    print("Verifying: Are first 5 unique pairs = actual scheduled games?")
    print("="*70)
    
    matches = 0
    total = 0
    
    for week in range(1, 15):
        week_matchups = [m for m in matchups if m.get('week') == week]
        actual_pairs = {tuple(sorted(pair)) for pair in actual_schedule.get(week, [])}
        
        # Get first 5 unique pairs encountered (in order)
        first_5_pairs = []
        seen_pairs = set()
        
        for matchup in week_matchups:
            home_id = matchup.get('home_team_id')
            away_id = matchup.get('away_team_id')
            winner_id = matchup.get('winner_id')
            
            if home_id is None or away_id is None:
                continue
            if not winner_id:
                continue
            
            team_pair = tuple(sorted([home_id, away_id]))
            
            if team_pair not in seen_pairs:
                seen_pairs.add(team_pair)
                first_5_pairs.append(team_pair)
                
                if len(first_5_pairs) >= 5:
                    break
        
        # Check if these 5 pairs match actual schedule
        first_5_set = set(first_5_pairs)
        match_count = len(first_5_set & actual_pairs)
        
        total += 5
        matches += match_count
        
        if match_count < 5:
            print(f"Week {week}: Only {match_count}/5 match")
            print(f"  First 5 pairs: {first_5_pairs}")
            print(f"  Actual pairs: {sorted(actual_pairs)}")
            print(f"  Missing: {sorted(actual_pairs - first_5_set)}")
    
    match_rate = (matches / total * 100) if total > 0 else 0
    print(f"\n{'='*70}")
    print(f"Result: {matches}/{total} pairs match ({match_rate:.1f}%)")
    
    if match_rate == 100:
        print("✓ First 5 unique pairs are always the actual games!")
        print("  Recommendation: Use first 5 unique pairs per week")
    else:
        print("✗ First 5 unique pairs do NOT always match actual games")
        print("  Need a different approach...")

if __name__ == "__main__":
    verify_first_5_pattern()
