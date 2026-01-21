"""
Quick verification script to check scraped data accuracy
Shows summary statistics and sample data for review
"""
import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent / "data"

def verify_season(season: int):
    """Verify a single season's data"""
    season_file = DATA_DIR / f"espn_season_{season}.json"
    
    if not season_file.exists():
        print(f"❌ Season {season} file not found")
        return None
    
    with open(season_file, 'r') as f:
        data = json.load(f)
    
    print(f"\n{'='*70}")
    print(f"Season {season} Verification")
    print(f"{'='*70}")
    
    # Check teams
    teams = data.get('teams', {})
    print(f"\n✓ Teams: {len(teams)} teams found")
    print("  Managers:")
    for manager, team_info in list(teams.items())[:5]:
        print(f"    - {manager}: {team_info.get('team_name', 'Unknown')}")
    if len(teams) > 5:
        print(f"    ... and {len(teams) - 5} more")
    
    # Check matchups
    matchups = data.get('matchups', [])
    print(f"\n✓ Matchups: {len(matchups)} total")
    
    # Group by week
    by_week = defaultdict(int)
    playoff_count = 0
    for m in matchups:
        week = m.get('week', 0)
        by_week[week] += 1
        if m.get('is_playoff', False):
            playoff_count += 1
    
    print(f"  Regular season matchups: {len(matchups) - playoff_count}")
    print(f"  Playoff matchups: {playoff_count} (should be 0)")
    
    weeks = sorted(by_week.keys())
    print(f"  Weeks found: {weeks}")
    print(f"  Weeks 1-{max(weeks) if weeks else 0}: {len(weeks)} weeks")
    
    # Expected weeks based on season
    if season >= 2021:
        expected_weeks = 14
    else:
        expected_weeks = 13
    
    if len(weeks) == expected_weeks and max(weeks) == expected_weeks:
        print(f"  ✓ Correct number of weeks ({expected_weeks})")
    else:
        print(f"  ⚠ Expected {expected_weeks} weeks, found {len(weeks)}")
    
    # Show sample matchups
    print(f"\n  Sample matchups (Week 1):")
    week1_matchups = [m for m in matchups if m.get('week') == 1][:3]
    for m in week1_matchups:
        print(f"    {m.get('home_manager')} ({m.get('home_score')}) vs {m.get('away_manager')} ({m.get('away_score')})")
    
    # Check standings
    standings = data.get('standings', [])
    print(f"\n✓ Standings: {len(standings)} teams")
    if standings:
        print("  Top 3:")
        for i, team in enumerate(standings[:3], 1):
            print(f"    {i}. {team.get('manager')}: {team.get('wins')}-{team.get('losses')} ({team.get('points_for', 0):.2f} pts)")
    
    # Check for any issues
    issues = []
    if playoff_count > 0:
        issues.append(f"Found {playoff_count} playoff matchups (should be 0)")
    if len(weeks) != expected_weeks:
        issues.append(f"Wrong number of weeks: {len(weeks)} vs expected {expected_weeks}")
    if len(teams) == 0:
        issues.append("No teams found")
    if len(matchups) == 0:
        issues.append("No matchups found")
    if len(standings) == 0:
        issues.append("No standings found")
    
    if issues:
        print(f"\n⚠ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print(f"\n✓ All checks passed!")
        return True

def main():
    """Verify all scraped seasons"""
    print("="*70)
    print("ESPN Data Verification")
    print("="*70)
    
    # Check if all_seasons file exists
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print("\n❌ espn_all_seasons.json not found")
        print("   Run the scraper first: python scrape_espn_data.py")
        return
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    seasons = sorted([int(k) for k in all_data.keys()])
    print(f"\nFound {len(seasons)} seasons: {seasons[0]}-{seasons[-1]}")
    
    # Verify a few sample seasons
    print("\n" + "="*70)
    print("Verifying Sample Seasons")
    print("="*70)
    
    # Check oldest, newest, and a middle one
    sample_seasons = [seasons[0], seasons[len(seasons)//2], seasons[-1]]
    
    all_good = True
    for season in sample_seasons:
        result = verify_season(season)
        if result is False:
            all_good = False
    
    # Summary
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print(f"Total seasons scraped: {len(seasons)}")
    print(f"Sample seasons verified: {len(sample_seasons)}")
    
    if all_good:
        print("\n✓ All sample seasons look good!")
        print("\nYou can now use this data for:")
        print("  - Building head-to-head records")
        print("  - Calculating all-time statistics")
        print("  - Displaying weekly matchup history")
    else:
        print("\n⚠ Some issues found in sample seasons")
        print("   Review the output above for details")
    
    print("\nTo verify a specific season:")
    print("  python verify_scrape.py 2023")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Verify specific season
        try:
            season = int(sys.argv[1])
            verify_season(season)
        except ValueError:
            print("Invalid season. Usage: python verify_scrape.py [season]")
    else:
        # Verify all seasons
        main()
