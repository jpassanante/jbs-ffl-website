"""Check 2023 playoff structure"""
import json
from pathlib import Path

data_file = Path(__file__).parent / "data" / "espn_season_2023.json"
with open(data_file, 'r') as f:
    data = json.load(f)

matchups = data.get('matchups', [])
weeks = sorted(set(m.get('week') for m in matchups))

output = []
output.append(f"All weeks in 2023: {weeks}")
output.append(f"Max week: {max(weeks)}")

# Check week 14
week14 = [m for m in matchups if m.get('week') == 14]
output.append(f"\nWeek 14: {len(week14)} matchups")
output.append("All week 14 games:")
for m in week14:
    output.append(f"  {m.get('home_manager')} ({m.get('home_score')}) vs {m.get('away_manager')} ({m.get('away_score')})")

# Check standings
standings = data.get('standings', [])
output.append(f"\nTop 4 in standings:")
for i, team in enumerate(standings[:4]):
    output.append(f"  {i+1}. {team.get('manager')} ({team.get('wins')}-{team.get('losses')}) - {team.get('points_for')}")

# According to champions.js, 2023 should be:
# Champion: Tyler (TyBear612)
# Runner-up: Ted (UGAdogs34)  
# Third: Matt (mendy1399)
output.append("\nExpected (from champions.js):")
output.append("  Champion: Tyler (TyBear612)")
output.append("  Runner-up: Ted (UGAdogs34)")
output.append("  Third: Matt (mendy1399)")

# Write to file
with open(Path(__file__).parent / "check_2023_output.txt", 'w') as f:
    f.write('\n'.join(output))

print('\n'.join(output))
