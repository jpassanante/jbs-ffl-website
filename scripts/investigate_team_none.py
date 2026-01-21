"""
Diagnostic script to investigate "Team None" entries in head-to-head data
Analyzes matchups with null team IDs to understand the root cause
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def load_all_seasons():
    """Load all scraped season data"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print(f"Error: {all_seasons_file} not found")
        return {}
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    return {int(k): v for k, v in all_data.items()}

def analyze_null_team_ids():
    """Analyze matchups with null team IDs"""
    print("=" * 70)
    print("Investigating 'Team None' Entries")
    print("=" * 70)
    
    espn_data = load_all_seasons()
    
    # Track statistics
    null_home_count = 0
    null_away_count = 0
    null_both_count = 0
    null_by_season = defaultdict(int)
    null_by_week = defaultdict(int)
    null_matchups = []
    
    # Track team IDs that appear in matchups but not in teams data
    missing_team_ids = defaultdict(set)
    
    for season, data in espn_data.items():
        teams = data.get('teams', {})
        matchups = data.get('matchups', [])
        
        # Build set of valid team IDs for this season
        valid_team_ids = set()
        for manager, team_info in teams.items():
            team_id = team_info.get('id')
            if team_id:
                valid_team_ids.add(team_id)
        
        for matchup in matchups:
            home_id = matchup.get('home_team_id')
            away_id = matchup.get('away_team_id')
            home_mgr = matchup.get('home_manager', '')
            away_mgr = matchup.get('away_manager', '')
            week = matchup.get('week', 0)
            home_score = matchup.get('home_score', 0)
            away_score = matchup.get('away_score', 0)
            
            has_null = False
            
            # Check for null home team
            if home_id is None:
                null_home_count += 1
                has_null = True
                null_by_season[season] += 1
                null_by_week[(season, week)] += 1
                null_matchups.append({
                    'season': season,
                    'week': week,
                    'type': 'home_null',
                    'home_manager': home_mgr,
                    'away_manager': away_mgr,
                    'home_score': home_score,
                    'away_score': away_score,
                })
            
            # Check for null away team
            if away_id is None:
                null_away_count += 1
                has_null = True
                null_by_season[season] += 1
                null_by_week[(season, week)] += 1
                null_matchups.append({
                    'season': season,
                    'week': week,
                    'type': 'away_null',
                    'home_manager': home_mgr,
                    'away_manager': away_mgr,
                    'home_score': home_score,
                    'away_score': away_score,
                })
            
            # Check if both are null
            if home_id is None and away_id is None:
                null_both_count += 1
            
            # Check if team IDs exist in teams data
            if home_id and home_id not in valid_team_ids:
                missing_team_ids[season].add(home_id)
            if away_id and away_id not in valid_team_ids:
                missing_team_ids[season].add(away_id)
    
    # Print summary
    print(f"\nTotal matchups with null home_team_id: {null_home_count}")
    print(f"Total matchups with null away_team_id: {null_away_count}")
    print(f"Total matchups with both null: {null_both_count}")
    print(f"Total unique matchups with nulls: {len(null_matchups)}")
    
    print(f"\nNull matchups by season:")
    for season in sorted(null_by_season.keys()):
        print(f"  {season}: {null_by_season[season]} matchups")
    
    print(f"\nNull matchups by week (first 10):")
    for (season, week), count in sorted(null_by_week.items())[:10]:
        print(f"  Season {season}, Week {week}: {count} matchups")
    
    # Analyze the null matchups
    print(f"\nSample null matchups (first 10):")
    for i, matchup in enumerate(null_matchups[:10], 1):
        print(f"\n  {i}. Season {matchup['season']}, Week {matchup['week']}")
        print(f"     Type: {matchup['type']}")
        print(f"     Home: {matchup['home_manager']} ({matchup['home_score']})")
        print(f"     Away: {matchup['away_manager']} ({matchup['away_score']})")
    
    # Check for missing team IDs
    if missing_team_ids:
        print(f"\n⚠️  Team IDs in matchups but not in teams data:")
        for season, team_ids in missing_team_ids.items():
            print(f"  Season {season}: {sorted(team_ids)}")
    else:
        print(f"\n✓ All team IDs in matchups exist in teams data")
    
    # Check for "Team None" managers
    team_none_count = 0
    team_none_matchups = []
    for season, data in espn_data.items():
        matchups = data.get('matchups', [])
        for matchup in matchups:
            home_mgr = matchup.get('home_manager', '')
            away_mgr = matchup.get('away_manager', '')
            if 'Team None' in home_mgr or 'Team None' in away_mgr:
                team_none_count += 1
                team_none_matchups.append({
                    'season': season,
                    'week': matchup.get('week', 0),
                    'home_manager': home_mgr,
                    'away_manager': away_mgr,
                    'home_id': matchup.get('home_team_id'),
                    'away_id': matchup.get('away_team_id'),
                })
    
    print(f"\n\n'Team None' manager occurrences: {team_none_count}")
    print(f"Unique matchups with 'Team None': {len(team_none_matchups)}")
    
    if team_none_matchups:
        print(f"\nSample 'Team None' matchups (first 10):")
        for i, matchup in enumerate(team_none_matchups[:10], 1):
            print(f"\n  {i}. Season {matchup['season']}, Week {matchup['week']}")
            print(f"     Home: {matchup['home_manager']} (ID: {matchup['home_id']})")
            print(f"     Away: {matchup['away_manager']} (ID: {matchup['away_id']})")
    
    # Check scores for null matchups
    zero_score_count = 0
    for matchup in null_matchups:
        if matchup['home_score'] == 0 and matchup['away_score'] == 0:
            zero_score_count += 1
    
    print(f"\n\nNull matchups with 0-0 scores: {zero_score_count} / {len(null_matchups)}")
    print(f"Percentage: {zero_score_count / len(null_matchups) * 100:.1f}%")
    
    print("\n" + "=" * 70)
    print("Investigation Complete")
    print("=" * 70)

if __name__ == "__main__":
    analyze_null_team_ids()
