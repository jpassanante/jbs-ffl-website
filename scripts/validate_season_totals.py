"""
Validate that game counts match expected games per season
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def validate_season_totals():
    """Check if filtered games match expected counts per season"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print("Error: espn_all_seasons.json not found")
        return
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    print("="*70)
    print("Validating Season Totals")
    print("="*70)
    
    # Count games per season after filtering by matchup_period_id
    games_per_season = {}
    games_per_week = defaultdict(int)
    
    for season_str, data in all_data.items():
        season = int(season_str)
        matchups = data.get('matchups', [])
        
        # Group by week
        matchups_by_week = defaultdict(list)
        for matchup in matchups:
            week = matchup.get('week', 0)
            if week > 0:
                matchups_by_week[week].append(matchup)
        
        # Count games after filtering by matchup_period_id
        season_games = 0
        for week, week_matchups in matchups_by_week.items():
            # Filter by matchup_period_id == week
            filtered = [m for m in week_matchups if m.get('matchup_period_id') == week]
            season_games += len(filtered)
            games_per_week[week] += len(filtered)
        
        games_per_season[season] = season_games
        
        # Expected: 13 weeks (pre-2021) or 14 weeks (2021+) × 5 games = 65-70 games
        expected_weeks = 14 if season >= 2021 else 13
        expected_games = expected_weeks * 5
        
        status = "✓" if season_games == expected_games else "⚠"
        print(f"{status} {season}: {season_games} games (expected {expected_games} for {expected_weeks} weeks)")
    
    print(f"\n" + "="*70)
    print("Summary:")
    print("="*70)
    
    total_games = sum(games_per_season.values())
    avg_per_season = total_games / len(games_per_season) if games_per_season else 0
    
    print(f"\nTotal games across all seasons: {total_games}")
    print(f"Average games per season: {avg_per_season:.1f}")
    print(f"Expected: 65-70 games per season (13-14 weeks × 5 games)")
    
    # Check games per week
    print(f"\nGames per week (across all seasons):")
    for week in sorted(games_per_week.keys()):
        count = games_per_week[week]
        expected = len(games_per_season) * 5  # 5 games per week per season
        status = "✓" if count == expected else "⚠"
        print(f"  Week {week:2d}: {count:4d} games (expected ~{expected})")

if __name__ == "__main__":
    validate_season_totals()
