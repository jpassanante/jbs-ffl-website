"""Analyze 2023 playoff structure to understand the data"""
import json
from pathlib import Path
from collections import defaultdict

data_file = Path(__file__).parent / "data" / "espn_season_2023.json"
with open(data_file, 'r') as f:
    data = json.load(f)

matchups = data.get('matchups', [])

# Get playoff weeks
playoff_matchups = [m for m in matchups if m.get('is_playoff', False)]
print(f"Total playoff matchups: {len(playoff_matchups)}")

# Group by week
by_week = defaultdict(list)
for m in playoff_matchups:
    week = m.get('week', 0)
    by_week[week].append(m)

print("\nPlayoff weeks and game counts:")
for week in sorted(by_week.keys()):
    games = by_week[week]
    print(f"  Week {week}: {len(games)} games")
    
    # Show unique teams playing
    teams = set()
    for g in games:
        teams.add(g.get('home_manager'))
        teams.add(g.get('away_manager'))
    print(f"    Unique teams: {len(teams)}")
    
    # Show sample games
    print(f"    Sample games:")
    for g in games[:3]:
        print(f"      {g.get('home_manager')} vs {g.get('away_manager')}: {g.get('home_score')} - {g.get('away_score')}")

# Check for duplicates (same teams playing multiple times in same week)
print("\nChecking for duplicate matchups in same week:")
for week in sorted(by_week.keys()):
    games = by_week[week]
    matchups_set = set()
    duplicates = []
    for g in games:
        home = g.get('home_manager')
        away = g.get('away_manager')
        matchup_key = tuple(sorted([home, away]))
        if matchup_key in matchups_set:
            duplicates.append(g)
        else:
            matchups_set.add(matchup_key)
    
    if duplicates:
        print(f"  Week {week}: {len(duplicates)} duplicate matchups found")
        for d in duplicates[:3]:
            print(f"    {d.get('home_manager')} vs {d.get('away_manager')}")

# Expected for 2023 (from champions.js):
# Champion: Tyler (TyBear612)
# Runner-up: Ted (UGAdogs34)
# Third: Matt (mendy1399)
print("\n" + "="*70)
print("Expected Results (from champions.js):")
print("  Champion: Tyler (TyBear612)")
print("  Runner-up: Ted (UGAdogs34)")
print("  Third: Matt (mendy1399)")
print("="*70)

# Find games involving these teams in final weeks
final_weeks = sorted(by_week.keys())[-2:] if len(by_week) >= 2 else sorted(by_week.keys())
print(f"\nGames in final weeks {final_weeks}:")
for week in final_weeks:
    games = by_week[week]
    print(f"\nWeek {week}:")
    for g in games:
        home = g.get('home_manager')
        away = g.get('away_manager')
        # Check if involves expected teams
        if any(t in [home, away] for t in ['TyBear612', 'UGAdogs34', 'mendy1399']):
            print(f"  {home} vs {away}: {g.get('home_score')} - {g.get('away_score')}")
