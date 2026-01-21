"""Quick script to check playoff data structure"""
import json
from pathlib import Path

data_file = Path(__file__).parent / "data" / "espn_season_2023.json"
with open(data_file, 'r') as f:
    data = json.load(f)

matchups = data.get('matchups', [])
weeks = sorted(set(m.get('week', 0) for m in matchups))
print(f"Weeks found: {weeks}")
print(f"Total matchups: {len(matchups)}")

playoff = [m for m in matchups if m.get('is_playoff')]
print(f"Playoff matchups (is_playoff=True): {len(playoff)}")

# Check last few weeks
for week in weeks[-3:]:
    week_matchups = [m for m in matchups if m.get('week') == week]
    print(f"\nWeek {week}: {len(week_matchups)} matchups")
    for m in week_matchups[:3]:
        print(f"  {m.get('home_manager')} vs {m.get('away_manager')}: {m.get('home_score')} - {m.get('away_score')}")
