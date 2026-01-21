import json
from collections import defaultdict
from pathlib import Path

data_file = Path(__file__).parent / "data" / "espn_season_2023.json"
with open(data_file, 'r') as f:
    data = json.load(f)

matchups = data.get('matchups', [])
week_counts = defaultdict(int)
for m in matchups:
    week = m.get('week', 0)
    week_counts[week] += 1

print('Week counts (last 5 weeks):')
for week in sorted(week_counts.keys())[-5:]:
    count = week_counts[week]
    playoff_count = len([m for m in matchups if m.get('week') == week and m.get('is_playoff')])
    print(f'  Week {week}: {count} total matchups, {playoff_count} marked as playoff')

# Show week 14 matchups
week14 = [m for m in matchups if m.get('week') == 14]
print(f'\nWeek 14 has {len(week14)} matchups:')
for m in week14:
    print(f"  {m.get('home_manager')} vs {m.get('away_manager')}: {m.get('home_score')} - {m.get('away_score')} (is_playoff: {m.get('is_playoff')})")
