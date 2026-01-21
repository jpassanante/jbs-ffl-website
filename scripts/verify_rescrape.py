"""Verify re-scrape results"""
import json
from pathlib import Path

data_dir = Path(__file__).parent / "data"

# Check 2023 specifically
season_file = data_dir / "espn_season_2023.json"
if season_file.exists():
    with open(season_file, 'r') as f:
        data = json.load(f)
    
    matchups = data.get('matchups', [])
    weeks = sorted(set(m.get('week') for m in matchups))
    
    print("="*70)
    print("2023 Season Verification")
    print("="*70)
    print(f"All weeks found: {weeks}")
    print(f"Max week: {max(weeks) if weeks else 0}")
    print(f"Total matchups: {len(matchups)}")
    
    # Check playoff weeks (should be 15+ for 2021+)
    playoff_matchups = [m for m in matchups if m.get('week', 0) > 14]
    print(f"Playoff matchups (week 15+): {len(playoff_matchups)}")
    
    if playoff_matchups:
        playoff_weeks = sorted(set(m.get('week') for m in playoff_matchups))
        print(f"Playoff weeks: {playoff_weeks}")
        print("\nSample playoff matchups:")
        for m in playoff_matchups[:5]:
            print(f"  Week {m.get('week')}: {m.get('home_manager')} vs {m.get('away_manager')} ({m.get('home_score')} - {m.get('away_score')})")
    else:
        print("\n⚠️  No playoff matchups found! Re-scrape may not have worked.")
        print("   Week 14 matchups (should be regular season):")
        week14 = [m for m in matchups if m.get('week') == 14]
        for m in week14[:3]:
            print(f"     {m.get('home_manager')} vs {m.get('away_manager')}")

# Check a few other 2021+ seasons
print("\n" + "="*70)
print("Other 2021+ Seasons")
print("="*70)
for year in [2021, 2022, 2024, 2025]:
    season_file = data_dir / f"espn_season_{year}.json"
    if season_file.exists():
        with open(season_file, 'r') as f:
            data = json.load(f)
        matchups = data.get('matchups', [])
        weeks = sorted(set(m.get('week') for m in matchups))
        playoff = [m for m in matchups if m.get('week', 0) > 14]
        print(f"{year}: Max week {max(weeks) if weeks else 0}, Playoff matchups: {len(playoff)}")
