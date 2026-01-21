"""
Quick data check - verify scraped data looks correct
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

print("="*70)
print("Checking Scraped Data")
print("="*70)

# Check if files exist
all_seasons_file = DATA_DIR / "espn_all_seasons.json"
if not all_seasons_file.exists():
    print("\n❌ espn_all_seasons.json not found")
    print("   Run the scraper first: python scrape_espn_data.py")
    exit(1)

with open(all_seasons_file, 'r') as f:
    all_data = json.load(f)

seasons = sorted([int(k) for k in all_data.keys()])
print(f"\n✓ Found {len(seasons)} seasons: {seasons[0]}-{seasons[-1]}")

# Check a few sample seasons
print("\n" + "="*70)
print("Sample Season Checks")
print("="*70)

sample_seasons = [seasons[0], seasons[len(seasons)//2], seasons[-1]]

for season in sample_seasons:
    data = all_data[str(season)]
    
    teams = data.get('teams', {})
    matchups = data.get('matchups', [])
    standings = data.get('standings', [])
    
    # Check weeks
    weeks = sorted(set(m.get('week', 0) for m in matchups))
    max_week = max(weeks) if weeks else 0
    
    # Expected
    expected = 14 if season >= 2021 else 13
    
    # Check for playoffs
    playoff_count = sum(1 for m in matchups if m.get('is_playoff', False))
    
    print(f"\n{season}:")
    print(f"  Teams: {len(teams)}")
    print(f"  Matchups: {len(matchups)}")
    print(f"  Weeks: {weeks[0]}-{max_week} ({len(weeks)} weeks)")
    print(f"  Expected: {expected} weeks")
    print(f"  Playoff matchups: {playoff_count} (should be 0)")
    
    if len(weeks) == expected and max_week == expected and playoff_count == 0:
        print(f"  ✓ Looks good!")
    else:
        print(f"  ⚠ Issues:")
        if len(weeks) != expected:
            print(f"     - Wrong number of weeks")
        if playoff_count > 0:
            print(f"     - Found {playoff_count} playoff matchups")
    
    # Show sample matchup
    if matchups:
        sample = matchups[0]
        print(f"  Sample: Week {sample.get('week')}, {sample.get('home_manager')} vs {sample.get('away_manager')}")

print("\n" + "="*70)
print("Overall Statistics")
print("="*70)

total_matchups = 0
total_playoff = 0
for season in seasons:
    data = all_data[str(season)]
    matchups = data.get('matchups', [])
    total_matchups += len(matchups)
    total_playoff += sum(1 for m in matchups if m.get('is_playoff', False))

print(f"Total matchups: {total_matchups}")
print(f"Playoff matchups: {total_playoff} (should be 0)")
print(f"Regular season matchups: {total_matchups - total_playoff}")

if total_playoff == 0:
    print("\n✓ All matchups are regular season - looks perfect!")
else:
    print(f"\n⚠ Found {total_playoff} playoff matchups (should be 0)")

print("\n" + "="*70)
print("Data appears ready to use!")
print("="*70)
