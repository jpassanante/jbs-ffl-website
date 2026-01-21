"""
Analyze Week 1 matchups to understand the data structure
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def analyze_week1():
    """Analyze Week 1 matchups for 2009"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    season_2009 = all_data.get('2009', {})
    matchups = season_2009.get('matchups', [])
    
    # Filter to week 1
    week1_matchups = [m for m in matchups if m.get('week') == 1]
    
    print(f"Total Week 1 matchups: {len(week1_matchups)}")
    print(f"Expected: 5 games (10 teams ÷ 2)")
    
    # Group by team pairs
    pairs = defaultdict(list)
    for m in week1_matchups:
        home_id = m.get('home_team_id')
        away_id = m.get('away_team_id')
        if home_id and away_id:
            pair = tuple(sorted([home_id, away_id]))
            pairs[pair].append(m)
    
    print(f"\nUnique team pairs in Week 1: {len(pairs)}")
    print(f"Expected: 5 pairs")
    
    # Check for pairs with multiple entries
    print(f"\nPairs with multiple entries:")
    for pair, matchups_list in pairs.items():
        if len(matchups_list) > 1:
            print(f"  Pair {pair}: {len(matchups_list)} entries")
            for i, m in enumerate(matchups_list[:3], 1):
                print(f"    {i}. Home: {m.get('home_manager')} ({m.get('home_score')}) vs Away: {m.get('away_manager')} ({m.get('away_score')})")
    
    # Check scores - real games should have non-zero scores
    zero_score_games = [m for m in week1_matchups if m.get('home_score', 0) == 0 and m.get('away_score', 0) == 0]
    print(f"\nGames with 0-0 scores: {len(zero_score_games)}")
    
    # Check for realistic scores (fantasy games typically 80-200 points)
    realistic_games = [m for m in week1_matchups if m.get('home_score', 0) > 50 and m.get('away_score', 0) > 50]
    print(f"Games with realistic scores (>50 each): {len(realistic_games)}")
    
    # Show all unique pairs and their scores
    print(f"\nAll unique pairs in Week 1:")
    for pair in sorted(pairs.keys()):
        matchups_list = pairs[pair]
        if len(matchups_list) == 1:
            m = matchups_list[0]
            print(f"  {pair}: {m.get('home_manager')} ({m.get('home_score')}) vs {m.get('away_manager')} ({m.get('away_score')})")
        else:
            print(f"  {pair}: {len(matchups_list)} entries (duplicates?)")

if __name__ == "__main__":
    analyze_week1()
