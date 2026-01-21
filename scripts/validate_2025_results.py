"""
Validate 2025 head-to-head results against known schedule
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def get_2025_actual_schedule():
    """Return the actual 2025 schedule"""
    return {
        1: [(1, 8), (10, 6), (7, 9), (4, 2), (5, 11)],
        2: [(7, 10), (8, 4), (1, 5), (6, 2), (9, 11)],
        3: [(5, 4), (2, 10), (11, 7), (6, 8), (9, 1)],
        4: [(11, 2), (4, 6), (5, 9), (10, 8), (7, 1)],
        5: [(9, 6), (8, 2), (1, 11), (10, 4), (7, 5)],
        6: [(1, 10), (4, 7), (2, 5), (6, 11), (8, 9)],
        7: [(1, 4), (2, 7), (5, 6), (8, 11), (9, 10)],
        8: [(1, 2), (6, 7), (5, 8), (10, 11), (4, 9)],
        9: [(1, 6), (2, 8), (9, 7), (4, 10), (11, 5)],
        10: [(7, 8), (6, 10), (5, 1), (2, 4), (11, 9)],
        11: [(5, 10), (4, 8), (7, 11), (2, 6), (1, 9)],
        12: [(11, 4), (10, 2), (9, 5), (8, 6), (1, 7)],
        13: [(9, 2), (6, 4), (11, 1), (8, 10), (5, 7)],
        14: [(8, 1), (10, 7), (4, 5), (2, 11), (6, 9)],
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

def validate_2025():
    """Validate 2025 results against known schedule"""
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
    
    print("="*70)
    print("Validating 2025 Results")
    print("="*70)
    
    # Get team ID to manager mapping
    teams = season_2025.get('teams', {})
    team_id_to_manager = {}
    for mgr, info in teams.items():
        team_id = info.get('id')
        if team_id:
            team_id_to_manager[team_id] = extract_first_name(mgr)
    
    # Process 2025 matchups with the same logic as process_data.py
    h2h_2025 = defaultdict(lambda: defaultdict(int))
    games_by_week = defaultdict(list)
    
    # Group by week
    matchups_by_week = defaultdict(list)
    for matchup in matchups:
        week = matchup.get('week', 0)
        if week > 0:
            matchups_by_week[week].append(matchup)
    
    # Process each week
    for week in range(1, 15):
        week_matchups = matchups_by_week.get(week, [])
        actual_pairs = {tuple(sorted(pair)) for pair in actual_schedule.get(week, [])}
        
        # Store original for fallback (same as process_data.py)
        original_week_matchups = week_matchups.copy()
        
        # Filter by matchup_period_id == week (same as process_data.py)
        has_matchup_period_id = any(m.get('matchup_period_id') is not None for m in week_matchups[:5])
        
        if has_matchup_period_id:
            filtered_matchups = []
            for matchup in week_matchups:
                matchup_period_id = matchup.get('matchup_period_id')
                if matchup_period_id == week:
                    filtered_matchups.append(matchup)
            
            # Validate filtered results (same as process_data.py)
            if filtered_matchups:
                valid_filtered = []
                for matchup in filtered_matchups:
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
                    
                    valid_filtered.append(matchup)
                
                # Check if we have exactly 5 games and each team appears once
                if len(valid_filtered) == 5:
                    team_counts = {}
                    for matchup in valid_filtered:
                        home_id = matchup.get('home_team_id')
                        away_id = matchup.get('away_team_id')
                        team_counts[home_id] = team_counts.get(home_id, 0) + 1
                        team_counts[away_id] = team_counts.get(away_id, 0) + 1
                    
                    all_appear_once = all(count == 1 for count in team_counts.values())
                    
                    if all_appear_once:
                        week_matchups = filtered_matchups
                    else:
                        week_matchups = original_week_matchups
                else:
                    week_matchups = original_week_matchups
            else:
                week_matchups = original_week_matchups
        
        # Apply other filters (same as process_data.py)
        valid_matchups = []
        for matchup in week_matchups:
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
            
            valid_matchups.append(matchup)
        
        # Get first occurrence of each team pair
        first_occurrence = {}
        seen_pairs = set()
        
        for matchup in valid_matchups:
            home_id = matchup.get('home_team_id')
            away_id = matchup.get('away_team_id')
            team_pair = tuple(sorted([home_id, away_id]))
            
            if team_pair not in seen_pairs:
                seen_pairs.add(team_pair)
                first_occurrence[team_pair] = matchup
        
        # Select 5 games ensuring each team appears exactly once
        selected_games = []
        used_teams = set()
        
        for team_pair, matchup in first_occurrence.items():
            if len(selected_games) >= 5:
                break
            
            home_id = matchup.get('home_team_id')
            away_id = matchup.get('away_team_id')
            
            if home_id not in used_teams and away_id not in used_teams:
                selected_games.append((team_pair, matchup))
                used_teams.add(home_id)
                used_teams.add(away_id)
        
        if len(selected_games) < 5:
            selected_games = list(first_occurrence.items())[:5]
        
        # Record results
        for team_pair, matchup in selected_games:
            home_id = matchup.get('home_team_id')
            away_id = matchup.get('away_team_id')
            home_score = matchup.get('home_score', 0)
            away_score = matchup.get('away_score', 0)
            
            home_mgr = team_id_to_manager.get(home_id, f"Team {home_id}")
            away_mgr = team_id_to_manager.get(away_id, f"Team {away_id}")
            
            home_first = extract_first_name(matchup.get('home_manager', home_mgr))
            away_first = extract_first_name(matchup.get('away_manager', away_mgr))
            
            if home_first == away_first:
                continue
            
            pair_key = tuple(sorted([home_first, away_first]))
            
            if home_score > away_score:
                h2h_2025[pair_key][home_first] += 1
            elif away_score > home_score:
                h2h_2025[pair_key][away_first] += 1
            
            # Store for week-by-week validation
            games_by_week[week].append({
                'pair': team_pair,
                'home': home_first,
                'away': away_first,
                'home_score': home_score,
                'away_score': away_score,
                'winner': home_first if home_score > away_score else away_first
            })
    
    # Validate week by week
    print("\n" + "="*70)
    print("Week-by-Week Validation")
    print("="*70)
    
    total_correct = 0
    total_expected = 0
    
    for week in range(1, 15):
        actual_pairs = {tuple(sorted(pair)) for pair in actual_schedule.get(week, [])}
        found_pairs = {g['pair'] for g in games_by_week.get(week, [])}
        
        matches = len(actual_pairs & found_pairs)
        missing = actual_pairs - found_pairs
        extra = found_pairs - actual_pairs
        
        total_expected += len(actual_pairs)
        total_correct += matches
        
        status = "✓" if matches == len(actual_pairs) and len(extra) == 0 else "⚠"
        print(f"\n{status} Week {week}: {matches}/{len(actual_pairs)} correct games")
        
        if missing:
            print(f"  Missing: {missing}")
        if extra:
            print(f"  Extra: {extra}")
        
        # Show the games that were found
        if games_by_week.get(week):
            print(f"  Found games:")
            for game in games_by_week[week]:
                print(f"    {game['away']} @ {game['home']}: {game['away_score']:.2f}-{game['home_score']:.2f} ({game['winner']} wins)")
    
    print(f"\n" + "="*70)
    print("Summary:")
    print("="*70)
    print(f"Total correct games: {total_correct}/{total_expected} ({total_correct/total_expected*100:.1f}%)")
    
    if total_correct == total_expected:
        print("✓✓✓ PERFECT! All 2025 games match the known schedule!")
    else:
        print(f"⚠ {total_expected - total_correct} games don't match")
    
    # Show 2025 head-to-head summary
    print(f"\n" + "="*70)
    print("2025 Head-to-Head Summary:")
    print("="*70)
    
    h2h_list = []
    for (mgr1, mgr2), records in h2h_2025.items():
        wins1 = records.get(mgr1, 0)
        wins2 = records.get(mgr2, 0)
        if wins1 + wins2 > 0:
            h2h_list.append({
                'manager1': mgr1,
                'manager2': mgr2,
                'wins1': wins1,
                'wins2': wins2,
                'total': wins1 + wins2
            })
    
    h2h_list.sort(key=lambda x: x['total'], reverse=True)
    
    print(f"\nTotal unique matchups in 2025: {len(h2h_list)}")
    print(f"Expected: ~45 unique pairs (10 teams = 45 possible pairs)")
    
    print(f"\nTop matchups by games played:")
    for h2h in h2h_list[:10]:
        print(f"  {h2h['manager1']} vs {h2h['manager2']}: {h2h['wins1']}-{h2h['wins2']} ({h2h['total']} games)")

if __name__ == "__main__":
    validate_2025()
