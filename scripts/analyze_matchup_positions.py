"""
Analyze the position/order of actual scheduled games within ESPN's matchup list for each week
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

def analyze_positions():
    """Analyze where actual games appear in ESPN's matchup list"""
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
    print("Analyzing Position of Actual Games in ESPN Matchup List")
    print("="*70)
    
    all_positions = []
    
    for week in range(1, 15):
        week_matchups = [m for m in matchups if m.get('week') == week]
        actual_pairs = {tuple(sorted(pair)) for pair in actual_schedule.get(week, [])}
        
        # Track first occurrence position for each actual pair
        first_occurrence_positions = {}
        seen_pairs = set()
        
        for idx, matchup in enumerate(week_matchups):
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
                if team_pair in actual_pairs:
                    first_occurrence_positions[team_pair] = idx
        
        positions = sorted(first_occurrence_positions.values())
        all_positions.extend(positions)
        
        print(f"\nWeek {week}:")
        print(f"  Actual games at positions: {positions}")
        print(f"  Range: {min(positions)} to {max(positions)}")
        print(f"  Total matchups for week: {len(week_matchups)}")
    
    print(f"\n{'='*70}")
    print(f"Summary:")
    print(f"  Total actual games: {len(all_positions)}")
    print(f"  Position range: {min(all_positions)} to {max(all_positions)}")
    print(f"  Average position: {sum(all_positions) / len(all_positions):.1f}")
    print(f"  Median position: {sorted(all_positions)[len(all_positions)//2]}")
    
    # Check if actual games are always in first N positions
    max_position = max(all_positions)
    print(f"\n  Maximum position of actual game: {max_position}")
    print(f"  If we take first {max_position + 1} matchups per week, we'd capture all actual games")
    
    # Check distribution
    position_counts = defaultdict(int)
    for pos in all_positions:
        position_counts[pos] += 1
    
    print(f"\n  Position distribution (first 20 positions):")
    for pos in sorted(position_counts.keys())[:20]:
        print(f"    Position {pos}: {position_counts[pos]} actual games")

if __name__ == "__main__":
    analyze_positions()
