"""
Diagnose why weeks 6-8 don't match the expected schedule
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def get_2025_actual_schedule():
    """Return the actual 2025 schedule"""
    return {
        6: [(6, 9), (2, 8), (11, 1), (4, 10), (5, 7)],
        7: [(8, 6), (1, 2), (11, 9), (10, 5), (7, 4)],
        8: [(9, 7), (4, 1), (2, 11), (6, 10), (5, 8)],
    }

# Manager name mapping
MANAGER_MAPPING = {
    'benhkline': 'Ben',
    'plazaroff': 'Peter',
    'lannybenson13': 'Lanny',
    'jpassana': 'Joey',
    'tybear612': 'Tyler',
    'vchapli1': 'Vernon',
    'johnnyhubes123': 'John',
    'mendy1399': 'Matt',
    'ugadogs34': 'Ted',
    'jayd3456': 'Jason',
    'tyfredstl': 'Ty',
}

def extract_first_name(display_name: str) -> str:
    """Extract first name from ESPN display name"""
    return MANAGER_MAPPING.get(display_name.lower(), display_name)

def diagnose_weeks_6_8():
    """Diagnose what's happening with weeks 6-8"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print("Error: espn_all_seasons.json not found")
        return
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    season_2025 = all_data.get('2025', {})
    if not season_2025:
        print("Error: 2025 season data not found")
        return
    
    matchups = season_2025.get('matchups', [])
    actual_schedule = get_2025_actual_schedule()
    
    # Get team ID to manager mapping
    teams = season_2025.get('teams', {})
    team_id_to_manager = {}
    for mgr, info in teams.items():
        team_id = info.get('id')
        if team_id:
            team_id_to_manager[team_id] = extract_first_name(mgr)
    
    print("="*70)
    print("Diagnosing Weeks 6-8")
    print("="*70)
    
    for week in [6, 7, 8]:
        print(f"\n{'='*70}")
        print(f"Week {week} Analysis")
        print(f"{'='*70}")
        
        # Get all matchups for this week
        week_matchups = [m for m in matchups if m.get('week') == week]
        print(f"\nTotal matchups in data for Week {week}: {len(week_matchups)}")
        
        # Filter by matchup_period_id == week
        filtered_by_period = [m for m in week_matchups if m.get('matchup_period_id') == week]
        print(f"Matchups with matchup_period_id == {week}: {len(filtered_by_period)}")
        
        # Show all matchup_period_id values for this week
        period_ids = defaultdict(int)
        for m in week_matchups:
            period_id = m.get('matchup_period_id')
            period_ids[period_id] += 1
        print(f"\nDistribution of matchup_period_id values:")
        for period_id, count in sorted(period_ids.items()):
            print(f"  Period {period_id}: {count} matchups")
        
        # Show the actual expected pairs
        expected_pairs = {tuple(sorted(pair)) for pair in actual_schedule.get(week, [])}
        print(f"\nExpected team pairs: {expected_pairs}")
        
        # Show what we found after filtering
        found_pairs = set()
        found_matchups = []
        
        for matchup in filtered_by_period:
            home_id = matchup.get('home_team_id')
            away_id = matchup.get('away_team_id')
            home_score = matchup.get('home_score', 0)
            away_score = matchup.get('away_score', 0)
            winner_id = matchup.get('winner_id')
            
            if home_id is None or away_id is None:
                continue
            if not winner_id:
                continue
            if home_score == 0 and away_score == 0:
                continue
            if home_score < 50 and away_score < 50:
                continue
            
            team_pair = tuple(sorted([home_id, away_id]))
            found_pairs.add(team_pair)
            
            home_mgr = team_id_to_manager.get(home_id, f"Team {home_id}")
            away_mgr = team_id_to_manager.get(away_id, f"Team {away_id}")
            
            found_matchups.append({
                'pair': team_pair,
                'home_id': home_id,
                'away_id': away_id,
                'home_mgr': extract_first_name(matchup.get('home_manager', home_mgr)),
                'away_mgr': extract_first_name(matchup.get('away_manager', away_mgr)),
                'home_score': home_score,
                'away_score': away_score,
                'matchup_period_id': matchup.get('matchup_period_id'),
                'matchup_id': matchup.get('matchup_id'),
            })
        
        print(f"\nFound {len(found_pairs)} unique team pairs after filtering:")
        for m in found_matchups:
            print(f"  {m['pair']}: {m['away_mgr']} @ {m['home_mgr']}: {m['away_score']:.2f}-{m['home_score']:.2f} (period_id={m['matchup_period_id']}, matchup_id={m['matchup_id']})")
        
        print(f"\nFound pairs: {found_pairs}")
        print(f"Expected pairs: {expected_pairs}")
        
        matches = expected_pairs & found_pairs
        missing = expected_pairs - found_pairs
        extra = found_pairs - expected_pairs
        
        print(f"\nMatches: {len(matches)}/{len(expected_pairs)}")
        if missing:
            print(f"Missing pairs: {missing}")
        if extra:
            print(f"Extra pairs: {extra}")
        
        # Check if the expected pairs exist in the raw data (before filtering)
        print(f"\nChecking if expected pairs exist in raw Week {week} data:")
        for expected_pair in expected_pairs:
            found_in_raw = False
            for matchup in week_matchups:
                home_id = matchup.get('home_team_id')
                away_id = matchup.get('away_team_id')
                if home_id and away_id:
                    pair = tuple(sorted([home_id, away_id]))
                    if pair == expected_pair:
                        found_in_raw = True
                        period_id = matchup.get('matchup_period_id')
                        print(f"  {expected_pair}: Found in raw data (matchup_period_id={period_id})")
                        break
            if not found_in_raw:
                print(f"  {expected_pair}: NOT FOUND in raw data")

if __name__ == "__main__":
    diagnose_weeks_6_8()
