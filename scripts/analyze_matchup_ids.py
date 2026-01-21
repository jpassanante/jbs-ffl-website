"""
Analyze matchup_id patterns to see if we can identify scheduled games
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

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

def analyze_matchup_ids():
    """Analyze matchup_id patterns for 2025"""
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
    print("Analyzing matchup_id Patterns for 2025")
    print("="*70)
    
    for week in range(1, 15):
        week_matchups = [m for m in matchups if m.get('week') == week]
        actual_pairs = {tuple(sorted(pair)) for pair in actual_schedule.get(week, [])}
        
        # Get matchup_ids for actual games
        actual_ids = []
        projected_ids = []
        
        for matchup in week_matchups:
            home_id = matchup.get('home_team_id')
            away_id = matchup.get('away_team_id')
            matchup_id = matchup.get('matchup_id')
            winner_id = matchup.get('winner_id')
            
            if home_id is None or away_id is None or not winner_id:
                continue
            
            team_pair = tuple(sorted([home_id, away_id]))
            
            if team_pair in actual_pairs:
                actual_ids.append(matchup_id)
            else:
                projected_ids.append(matchup_id)
        
        if actual_ids:
            print(f"\nWeek {week}:")
            print(f"  Actual game matchup_ids: {sorted(actual_ids)}")
            print(f"  Projected game matchup_ids (first 10): {sorted(projected_ids)[:10]}")
            print(f"  Actual ID range: {min(actual_ids)} - {max(actual_ids)}")
            print(f"  Projected ID range: {min(projected_ids)} - {max(projected_ids)}" if projected_ids else "  No projected IDs")
            
            # Check if actual IDs are always lower
            if projected_ids and max(actual_ids) < min(projected_ids):
                print(f"  ✓ Actual games have lower IDs!")
            elif projected_ids and min(actual_ids) > max(projected_ids):
                print(f"  ✓ Actual games have higher IDs!")
            else:
                print(f"  ✗ No clear ID pattern")

if __name__ == "__main__":
    analyze_matchup_ids()
