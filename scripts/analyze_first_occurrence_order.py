"""
Analyze if actual games appear first in the list of first occurrences
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

def analyze_first_occurrence_order():
    """Check if actual games appear first in first occurrence list"""
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
    print("Analyzing First Occurrence Order for 2025")
    print("="*70)
    
    total_matches = 0
    total_weeks = 0
    
    for week in range(1, 15):
        week_matchups = [m for m in matchups if m.get('week') == week]
        actual_pairs = {tuple(sorted(pair)) for pair in actual_schedule.get(week, [])}
        
        # Get first occurrences (same logic as process_data.py)
        first_occurrence = {}  # team_pair -> matchup
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
                first_occurrence[team_pair] = matchup
        
        # Get order of first occurrences (by position in original list)
        first_occurrence_list = []
        seen_in_order = set()
        for matchup in week_matchups:
            home_id = matchup.get('home_team_id')
            away_id = matchup.get('away_team_id')
            winner_id = matchup.get('winner_id')
            
            if home_id is None or away_id is None or not winner_id:
                continue
            
            team_pair = tuple(sorted([home_id, away_id]))
            
            if team_pair not in seen_in_order and team_pair in first_occurrence:
                seen_in_order.add(team_pair)
                first_occurrence_list.append((team_pair, matchup))
        
        # Check if first 5 are actual games
        first_5_pairs = [pair for pair, _ in first_occurrence_list[:5]]
        actual_in_first_5 = len(set(first_5_pairs) & actual_pairs)
        
        total_weeks += 1
        total_matches += actual_in_first_5
        
        if actual_in_first_5 < 5:
            print(f"\nWeek {week}: Only {actual_in_first_5}/5 actual games in first 5")
            print(f"  First 5 pairs: {first_5_pairs}")
            print(f"  Actual pairs: {sorted(actual_pairs)}")
            missing = sorted(actual_pairs - set(first_5_pairs))
            if missing:
                print(f"  Missing: {missing}")
        else:
            print(f"Week {week}: ✓ All 5 actual games in first 5")
    
    match_rate = (total_matches / (total_weeks * 5) * 100) if total_weeks > 0 else 0
    print(f"\n{'='*70}")
    print(f"Summary: {total_matches}/{total_weeks * 5} actual games found in first 5 ({match_rate:.1f}%)")
    
    if match_rate == 100:
        print("✓ First 5 first occurrences are always the actual games!")
        print("  Recommendation: Use first 5 first occurrences per week")
    else:
        print("✗ First 5 first occurrences do NOT always match actual games")

if __name__ == "__main__":
    analyze_first_occurrence_order()
