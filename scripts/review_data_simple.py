"""
Simple data review - check scraped data accuracy
"""
import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent / "data"

# Load all seasons
all_seasons_file = DATA_DIR / "espn_all_seasons.json"
if not all_seasons_file.exists():
    print("❌ espn_all_seasons.json not found")
    exit(1)

with open(all_seasons_file, 'r') as f:
    all_data = json.load(f)

seasons = sorted([int(k) for k in all_data.keys()])

print("="*70)
print("ESPN Data Review - Regular Season Only")
print("="*70)
print(f"\nFound {len(seasons)} seasons: {seasons[0]}-{seasons[-1]}")

# Review each season
print("\n" + "="*70)
print("Season-by-Season Review")
print("="*70)

all_good = True
for season in seasons:
    data = all_data[str(season)]
    
    teams = data.get('teams', {})
    matchups = data.get('matchups', [])
    standings = data.get('standings', [])
    
    # Check weeks
    weeks = sorted(set(m.get('week', 0) for m in matchups))
    max_week = max(weeks) if weeks else 0
    
    # Expected weeks
    if season >= 2021:
        expected_weeks = 14
    else:
        expected_weeks = 13
    
    # Check for playoff matchups
    playoff_matchups = [m for m in matchups if m.get('is_playoff', False)]
    
    # Status
    status = "✓"
    issues = []
    if len(weeks) != expected_weeks or max_week != expected_weeks:
        status = "⚠"
        issues.append(f"Weeks: {len(weeks)} (expected {expected_weeks})")
    if playoff_matchups:
        status = "⚠"
        issues.append(f"Found {len(playoff_matchups)} playoff matchups")
    if not teams:
        status = "❌"
        issues.append("No teams")
    if not matchups:
        status = "❌"
        issues.append("No matchups")
    if not standings:
        status = "⚠"
        issues.append("No standings")
    
    if issues:
        all_good = False
    
    # Print summary
    reg_season_count = len(matchups) - len(playoff_matchups)
    print(f"\n{status} {season}: {len(teams)} teams, {reg_season_count} matchups, Weeks 1-{max_week}")
    if issues:
        for issue in issues:
            print(f"    ⚠ {issue}")
    
    # Show top team
    if standings:
        top = standings[0]
        print(f"    Top: {top.get('manager')} ({top.get('wins')}-{top.get('losses')}, {top.get('points_for', 0):.2f} pts)")

# Overall summary
print("\n" + "="*70)
print("Summary")
print("="*70)

total_matchups = sum(len(data.get('matchups', [])) for data in all_data.values())
total_teams = sum(len(data.get('teams', {})) for data in all_data.values())

print(f"Total seasons: {len(seasons)}")
print(f"Total matchups: {total_matchups}")
print(f"Total team entries: {total_teams}")

if all_good:
    print("\n✓ All seasons look good!")
    print("\nData is ready to use for:")
    print("  - Head-to-head records")
    print("  - All-time statistics")
    print("  - Weekly matchup history")
else:
    print("\n⚠ Some issues found - review above for details")

print("\n" + "="*70)
print("To review a specific season in detail:")
print("  python review_data.py --season 2023")
print("="*70)
