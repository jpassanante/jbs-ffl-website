"""Diagnose playoff data structure"""
import json
from collections import Counter
from pathlib import Path

data_file = Path(__file__).parent / "data" / "espn_season_2023.json"
with open(data_file, 'r') as f:
    data = json.load(f)

matchups = data.get('matchups', [])
print(f"Total matchups: {len(matchups)}")

# Count by week
week_counts = Counter(m.get('week') for m in matchups)
print(f"\nMatchups per week:")
for week in sorted(week_counts.keys())[-5:]:
    count = week_counts[week]
    playoff_count = len([m for m in matchups if m.get('week') == week and m.get('is_playoff')])
    print(f"  Week {week}: {count} total, {playoff_count} marked as playoff")

# Check playoff flag
playoff_marked = [m for m in matchups if m.get('is_playoff')]
print(f"\nTotal matchups marked as playoff: {len(playoff_marked)}")
if playoff_marked:
    playoff_weeks = sorted(set(m.get('week') for m in playoff_marked))
    print(f"Playoff weeks: {playoff_weeks}")
    
    # Show sample playoff matchups
    print(f"\nSample playoff matchups:")
    for m in playoff_marked[:5]:
        print(f"  Week {m.get('week')}: {m.get('home_manager')} vs {m.get('away_manager')}")
