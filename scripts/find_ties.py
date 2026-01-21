"""
Find tie games in the ESPN scraped data
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def find_ties():
    """Find all tie games in the scraped data"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print("Error: espn_all_seasons.json not found")
        return
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    print("="*70)
    print("Finding Tie Games in ESPN Data")
    print("="*70)
    
    ties_found = []
    
    for season_str, data in all_data.items():
        season = int(season_str)
        matchups = data.get('matchups', [])
        
        for matchup in matchups:
            home_id = matchup.get('home_team_id')
            away_id = matchup.get('away_team_id')
            home_score = matchup.get('home_score', 0)
            away_score = matchup.get('away_score', 0)
            winner_id = matchup.get('winner_id')
            week = matchup.get('week', 0)
            home_mgr = matchup.get('home_manager', '')
            away_mgr = matchup.get('away_manager', '')
            
            # Check for ties: scores are equal, both > 0, and winner_id is None
            # Also filter by matchup_period_id == week to only get actual scheduled ties (not duplicates)
            matchup_period_id = matchup.get('matchup_period_id')
            if (home_id is not None and away_id is not None and
                home_score == away_score and 
                home_score > 0 and
                winner_id is None and
                matchup_period_id == week):  # Only actual scheduled games
                
                ties_found.append({
                    'season': season,
                    'week': week,
                    'home_id': home_id,
                    'away_id': away_id,
                    'home_manager': home_mgr,
                    'away_manager': away_mgr,
                    'home_score': home_score,
                    'away_score': away_score,
                    'winner_id': winner_id,
                    'matchup_period_id': matchup_period_id,
                })
    
    print(f"\nTotal ties found: {len(ties_found)}")
    
    if ties_found:
        print("\nTie games:")
        for tie in ties_found:
            print(f"  {tie['season']} Week {tie['week']}: {tie['home_manager']} ({tie['home_score']}) vs {tie['away_manager']} ({tie['away_score']})")
            print(f"    Home ID: {tie['home_id']}, Away ID: {tie['away_id']}, Winner ID: {tie['winner_id']}")
            print(f"    Matchup Period ID: {tie['matchup_period_id']}")
    else:
        print("\nNo ties found in the data.")
        print("\nChecking for games with equal scores but winner_id set...")
        
        # Check for games with equal scores but winner_id is set (shouldn't happen for ties)
        equal_scores = []
        for season_str, data in all_data.items():
            season = int(season_str)
            matchups = data.get('matchups', [])
            
            for matchup in matchups:
                home_id = matchup.get('home_team_id')
                away_id = matchup.get('away_team_id')
                home_score = matchup.get('home_score', 0)
                away_score = matchup.get('away_score', 0)
                winner_id = matchup.get('winner_id')
                week = matchup.get('week', 0)
                
                if (home_id is not None and away_id is not None and
                    home_score == away_score and 
                    home_score > 0):
                    equal_scores.append({
                        'season': season,
                        'week': week,
                        'home_score': home_score,
                        'away_score': away_score,
                        'winner_id': winner_id,
                    })
        
        if equal_scores:
            print(f"\nFound {len(equal_scores)} games with equal scores:")
            for game in equal_scores[:10]:  # Show first 10
                print(f"  {game['season']} Week {game['week']}: Score {game['home_score']}, Winner ID: {game['winner_id']}")

if __name__ == "__main__":
    find_ties()
