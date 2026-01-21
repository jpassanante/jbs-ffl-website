"""
Quick Data Review - Simple version
Shows key stats from scraped ESPN data
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

print("=" * 70)
print("ESPN Fantasy Football Data - Quick Review")
print("=" * 70)

# Load combined data
all_seasons_file = DATA_DIR / "espn_all_seasons.json"
if not all_seasons_file.exists():
    print(f"Error: {all_seasons_file} not found")
    exit(1)

with open(all_seasons_file, 'r') as f:
    all_data = json.load(f)

seasons = sorted([int(s) for s in all_data.keys()])
print(f"\n✓ Found {len(seasons)} seasons: {min(seasons)} - {max(seasons)}")

# Quick stats
total_teams = 0
total_matchups = 0
seasons_with_playoffs = 0
issues = []

for season in seasons:
    data = all_data[str(season)]
    
    teams = data.get('teams', {})
    matchups = data.get('matchups', [])
    standings = data.get('standings', [])
    playoffs = data.get('playoff_results', {})
    
    total_teams += len(teams)
    total_matchups += len(matchups)
    if playoffs:
        seasons_with_playoffs += 1
    
    # Check for issues
    if not teams:
        issues.append(f"Season {season}: No teams")
    if not matchups:
        issues.append(f"Season {season}: No matchups")
    if not standings:
        issues.append(f"Season {season}: No standings")

print(f"\nOverall Statistics:")
print(f"  Total teams (across all seasons): {total_teams}")
print(f"  Total matchups: {total_matchups}")
print(f"  Seasons with playoff data: {seasons_with_playoffs}/{len(seasons)}")

# Per-season summary
print(f"\nPer-Season Summary:")
for season in seasons:
    data = all_data[str(season)]
    teams = data.get('teams', {})
    matchups = data.get('matchups', [])
    standings = data.get('standings', [])
    
    managers = list(teams.keys())[:3]  # First 3 managers
    managers_str = ', '.join(managers)
    if len(teams) > 3:
        managers_str += f" (+{len(teams)-3} more)"
    
    reg_season = sum(1 for m in matchups if not m.get('is_playoff', False))
    playoff = sum(1 for m in matchups if m.get('is_playoff', False))
    
    champ = standings[0].get('manager', '?') if standings else '?'
    
    print(f"  {season}: {len(teams)} teams, {reg_season} reg + {playoff} playoff matchups, Champ: {champ}")

# Issues
if issues:
    print(f"\n⚠ Issues Found ({len(issues)}):")
    for issue in issues[:10]:  # Show first 10
        print(f"  - {issue}")
    if len(issues) > 10:
        print(f"  ... and {len(issues) - 10} more")
else:
    print(f"\n✓ No major issues found!")

print("\n" + "=" * 70)
print("To review a specific season in detail, run:")
print("  python review_data.py --season 2024")
print("=" * 70)
