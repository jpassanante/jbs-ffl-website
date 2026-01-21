"""
Diagnostic script to check how many unique team pairs per week have winner_id set
This will help identify if ESPN returns all 45 pairs with winner_id, or if there's a pattern
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def diagnose_winner_id():
    """Check winner_id patterns across all seasons"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print(f"Error: {all_seasons_file} not found")
        return
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    # Convert string keys to int
    espn_data = {int(k): v for k, v in all_data.items()}
    
    print("="*70)
    print("Diagnosing winner_id Patterns")
    print("="*70)
    
    # Track stats per week
    weekly_stats = defaultdict(lambda: {'with_winner': 0, 'without_winner': 0, 'unique_pairs_with_winner': set()})
    
    for season, data in espn_data.items():
        matchups = data.get('matchups', [])
        
        for matchup in matchups:
            home_id = matchup.get('home_team_id')
            away_id = matchup.get('away_team_id')
            winner_id = matchup.get('winner_id')
            week = matchup.get('week', 0)
            
            # Skip invalid matchups
            if home_id is None or away_id is None:
                continue
            
            home_score = matchup.get('home_score', 0)
            away_score = matchup.get('away_score', 0)
            
            # Skip 0-0 games
            if home_score == 0 and away_score == 0:
                continue
            
            week_key = (season, week)
            team_pair = tuple(sorted([home_id, away_id]))
            
            if winner_id:
                weekly_stats[week_key]['with_winner'] += 1
                weekly_stats[week_key]['unique_pairs_with_winner'].add(team_pair)
            else:
                weekly_stats[week_key]['without_winner'] += 1
    
    # Analyze results
    print(f"\nAnalyzed {len(weekly_stats)} week/season combinations")
    print(f"\nUnique pairs with winner_id per week:")
    
    pair_counts = []
    for week_key, stats in sorted(weekly_stats.items()):
        season, week = week_key
        unique_count = len(stats['unique_pairs_with_winner'])
        pair_counts.append(unique_count)
        
        if unique_count > 5:
            print(f"  {season} Week {week:2d}: {unique_count:2d} unique pairs with winner_id (expected 5)")
    
    if pair_counts:
        print(f"\nSummary:")
        print(f"  Min unique pairs with winner_id: {min(pair_counts)}")
        print(f"  Max unique pairs with winner_id: {max(pair_counts)}")
        print(f"  Avg unique pairs with winner_id: {sum(pair_counts) / len(pair_counts):.1f}")
        print(f"  Expected: 5 pairs per week (10-team league)")
        
        over_5 = sum(1 for c in pair_counts if c > 5)
        exactly_5 = sum(1 for c in pair_counts if c == 5)
        under_5 = sum(1 for c in pair_counts if c < 5)
        
        print(f"\nDistribution:")
        print(f"  Weeks with exactly 5 pairs: {exactly_5} ({exactly_5/len(pair_counts)*100:.1f}%)")
        print(f"  Weeks with more than 5 pairs: {over_5} ({over_5/len(pair_counts)*100:.1f}%)")
        print(f"  Weeks with fewer than 5 pairs: {under_5} ({under_5/len(pair_counts)*100:.1f}%)")
    
    # Show example week with many pairs
    print(f"\nExample: Week with most unique pairs (showing first 10):")
    max_week = max(weekly_stats.items(), key=lambda x: len(x[1]['unique_pairs_with_winner']))
    week_key, stats = max_week
    season, week = week_key
    print(f"  {season} Week {week}: {len(stats['unique_pairs_with_winner'])} unique pairs")
    
    # Show a few example pairs
    for i, pair in enumerate(sorted(stats['unique_pairs_with_winner'])[:10], 1):
        print(f"    {i}. Team {pair[0]} vs Team {pair[1]}")
    
    print("\n" + "="*70)
    print("Conclusion:")
    if max(pair_counts) > 5:
        print("  ESPN is returning MORE than 5 unique pairs with winner_id per week.")
        print("  We need to identify which 5 are the actual scheduled games.")
        print("  Recommendation: Use the 2025 schedule validation to find patterns.")
    elif max(pair_counts) == 5:
        print("  ESPN returns exactly 5 unique pairs with winner_id per week.")
        print("  Using winner_id filter should work correctly!")
    else:
        print("  ESPN returns fewer than 5 unique pairs with winner_id per week.")
        print("  Some games may be missing winner_id, or data is incomplete.")

if __name__ == "__main__":
    diagnose_winner_id()
