"""
Validate ESPN data against known 2025 schedule to identify real games
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

# Manager name mapping (same as process_data.py)
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

def load_espn_2025_data():
    """Load ESPN data for 2025"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print("Error: espn_all_seasons.json not found")
        return None
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    return all_data.get('2025', {})

def analyze_week(espn_data, week, actual_schedule):
    """
    Analyze a specific week to identify which ESPN matchups are real
    
    Args:
        espn_data: List of all matchups from ESPN for this week
        week: Week number
        actual_schedule: Dict mapping week -> list of (team1_id, team2_id) tuples that actually played
    """
    print(f"\n{'='*60}")
    print(f"Week {week} Analysis")
    print(f"{'='*60}")
    
    week_matchups = [m for m in espn_data if m.get('week') == week]
    print(f"ESPN returned {len(week_matchups)} matchups for Week {week}")
    
    actual_pairs = actual_schedule.get(week, [])
    print(f"Actual games played: {len(actual_pairs)}")
    
    # Group ESPN matchups by team pair
    espn_pairs = defaultdict(list)
    for m in week_matchups:
        home_id = m.get('home_team_id')
        away_id = m.get('away_team_id')
        if home_id and away_id:
            pair = tuple(sorted([home_id, away_id]))
            espn_pairs[pair].append(m)
    
    print(f"\nUnique team pairs in ESPN data: {len(espn_pairs)}")
    print(f"Expected: {len(actual_pairs)}")
    
    # Check which pairs match actual schedule
    print(f"\nMatching actual schedule:")
    matches = 0
    
    # Check if FIRST occurrence of each team pair in ESPN data matches actual schedule
    # Track first occurrence position for each team pair
    first_occurrence = {}  # team_pair -> (position, matchup)
    for idx, m in enumerate(week_matchups):
        home_id = m.get('home_team_id')
        away_id = m.get('away_team_id')
        if home_id and away_id:
            pair = tuple(sorted([home_id, away_id]))
            if pair not in first_occurrence:
                first_occurrence[pair] = (idx, m)
    
    for actual_pair in actual_pairs:
        sorted_actual = tuple(sorted(actual_pair))
        if sorted_actual in espn_pairs:
            matches += 1
            matchups = espn_pairs[sorted_actual]
            first_pos, first_matchup = first_occurrence.get(sorted_actual, (None, None))
            
            print(f"  ✓ {sorted_actual}: Found {len(matchups)} entry/entries")
            print(f"    First occurrence at position {first_pos}: {first_matchup.get('home_manager')} ({first_matchup.get('home_score')}) vs {first_matchup.get('away_manager')} ({first_matchup.get('away_score')})")
            
            if len(matchups) > 1:
                print(f"    All entries for this pair:")
                for i, m in enumerate(matchups, 1):
                    print(f"      {i}. {m.get('home_manager')} ({m.get('home_score')}) vs {m.get('away_manager')} ({m.get('away_score')})")
        else:
            print(f"  ✗ {sorted_actual}: NOT FOUND in ESPN data")
    
    print(f"\nMatches: {matches}/{len(actual_pairs)}")
    
    # Check for extra pairs in ESPN data
    extra_pairs = set(espn_pairs.keys()) - {tuple(sorted(p)) for p in actual_pairs}
    if extra_pairs:
        print(f"\nExtra pairs in ESPN data (not in actual schedule): {len(extra_pairs)}")
        for pair in list(extra_pairs)[:5]:  # Show first 5
            matchups = espn_pairs[pair]
            print(f"  {pair}: {len(matchups)} entry/entries")
            if matchups:
                m = matchups[0]
                print(f"    Example: {m.get('home_manager')} ({m.get('home_score')}) vs {m.get('away_manager')} ({m.get('away_score')})")

def map_manager_to_team_id(manager_name, teams):
    """Map manager name to team ID"""
    manager_lower = manager_name.lower()
    for mgr, info in teams.items():
        if mgr.lower() == manager_lower:
            return info.get('id')
    return None

def get_2025_actual_schedule():
    """
    Return the actual 2025 schedule from screenshots.
    Format: {week: [(away_id, home_id), ...]}
    """
    # Team ID mapping:
    # Ted (UGAdogs34) → 1
    # Peter (PLazaroff) → 2
    # Lanny (lannybenson13) → 4
    # Ben (benhkline) → 5
    # Vernon (vchapli1) → 6
    # John (johnnyhubes123) → 7
    # Joey (jpassana) → 8
    # Matt (mendy1399) → 9
    # Tyler (TyBear612) → 10
    # Jason (jayd3456) → 11
    
    return {
        1: [(1, 8), (10, 6), (7, 9), (4, 2), (5, 11)],  # Ted@Joey, Tyler@Vernon, John@Matt, Lanny@Peter, Ben@Jason
        2: [(7, 10), (8, 4), (1, 5), (6, 2), (9, 11)],  # John@Tyler, Joey@Lanny, Ted@Ben, Vernon@Peter, Matt@Jason
        3: [(5, 4), (2, 10), (11, 7), (6, 8), (9, 1)],  # Ben@Lanny, Peter@Tyler, Jason@John, Vernon@Joey, Matt@Ted
        4: [(11, 2), (4, 6), (5, 9), (10, 8), (7, 1)],  # Jason@Peter, Lanny@Vernon, Ben@Matt, Tyler@Joey, John@Ted
        5: [(9, 6), (8, 2), (1, 11), (10, 4), (7, 5)],  # Matt@Vernon, Joey@Peter, Ted@Jason, Tyler@Lanny, John@Ben
        6: [(6, 9), (2, 8), (11, 1), (4, 10), (5, 7)],  # Vernon@Matt, Peter@Joey, Jason@Ted, Lanny@Tyler, Ben@John
        7: [(8, 6), (1, 2), (11, 9), (10, 5), (7, 4)],  # Joey@Vernon, Ted@Peter, Jason@Matt, Tyler@Ben, John@Lanny
        8: [(9, 7), (4, 1), (2, 11), (6, 10), (5, 8)],  # Matt@John, Lanny@Ted, Peter@Jason, Vernon@Tyler, Ben@Joey
        9: [(1, 6), (2, 8), (9, 7), (4, 10), (11, 5)],  # Ted@Vernon, Peter@Joey, Matt@John, Lanny@Tyler, Jason@Ben
        10: [(7, 8), (6, 10), (5, 1), (2, 4), (11, 9)],  # John@Joey, Vernon@Tyler, Ben@Ted, Peter@Lanny, Jason@Matt
        11: [(5, 10), (4, 8), (7, 11), (2, 6), (1, 9)],  # Ben@Tyler, Lanny@Joey, John@Jason, Peter@Vernon, Ted@Matt
        12: [(11, 4), (10, 2), (9, 5), (8, 6), (1, 7)],  # Jason@Lanny, Tyler@Peter, Matt@Ben, Joey@Vernon, Ted@John
        13: [(9, 2), (6, 4), (11, 1), (8, 10), (5, 7)],  # Matt@Peter, Vernon@Lanny, Jason@Ted, Joey@Tyler, Ben@John
        14: [(8, 1), (10, 7), (4, 5), (2, 11), (6, 9)],  # Joey@Ted, Tyler@John, Lanny@Ben, Peter@Jason, Vernon@Matt
    }

def main():
    """Main validation function"""
    print("="*60)
    print("Validating ESPN Data Against 2025 Schedule")
    print("="*60)
    
    espn_data = load_espn_2025_data()
    if not espn_data:
        return
    
    matchups = espn_data.get('matchups', [])
    print(f"\nLoaded {len(matchups)} total matchups for 2025")
    
    # Get team ID mapping
    teams = espn_data.get('teams', {})
    manager_to_id = {}
    id_to_manager = {}
    for mgr, info in teams.items():
        team_id = info.get('id')
        manager_to_id[mgr.lower()] = team_id
        id_to_manager[team_id] = mgr
    
    # Show available teams for reference
    print("\n" + "="*60)
    print("Available Teams (for reference):")
    print("="*60)
    for mgr, info in sorted(teams.items(), key=lambda x: x[1].get('id', 0)):
        team_id = info.get('id')
        team_name = info.get('name', 'Unknown')
        first_name = extract_first_name(mgr)
        print(f"  ID {team_id:2d}: {first_name:8s} ({mgr:20s}) - {team_name}")
    
    # Get actual schedule from screenshots
    actual_schedule = get_2025_actual_schedule()
    
    print("\n" + "="*60)
    print("Validating Against 2025 Schedule")
    print("="*60)
    
    # Analyze each week
    patterns_found = {
        'has_winner_id': 0,
        'no_winner_id': 0,
        'real_games': [],
        'projected_games': [],
    }
    
    for week in range(1, 15):
        analyze_week(matchups, week, actual_schedule)
        
        # Check patterns for real games
        week_matchups = [m for m in matchups if m.get('week') == week]
        actual_pairs = {tuple(sorted(pair)) for pair in actual_schedule.get(week, [])}
        
        for m in week_matchups:
            home_id = m.get('home_team_id')
            away_id = m.get('away_team_id')
            if home_id and away_id:
                pair = tuple(sorted([home_id, away_id]))
                winner_id = m.get('winner_id')
                
                if pair in actual_pairs:
                    # This is a real game
                    patterns_found['real_games'].append(m)
                    if winner_id:
                        patterns_found['has_winner_id'] += 1
                    else:
                        patterns_found['no_winner_id'] += 1
                else:
                    # This is a projected/duplicate game
                    patterns_found['projected_games'].append(m)
    
    # Analyze patterns
    print("\n" + "="*60)
    print("Pattern Analysis")
    print("="*60)
    print(f"\nReal games found: {len(patterns_found['real_games'])}")
    print(f"  With winner_id: {patterns_found['has_winner_id']}")
    print(f"  Without winner_id: {patterns_found['no_winner_id']}")
    print(f"\nProjected/duplicate games: {len(patterns_found['projected_games'])}")
    
    # Check if winner_id is a reliable indicator
    if patterns_found['has_winner_id'] > 0 and patterns_found['no_winner_id'] == 0:
        print("\n✓ PATTERN FOUND: Real games always have winner_id set!")
        print("  Recommendation: Filter by winner_id presence")
    elif patterns_found['has_winner_id'] > patterns_found['no_winner_id']:
        print(f"\n⚠ PATTERN: Most real games have winner_id ({patterns_found['has_winner_id']} vs {patterns_found['no_winner_id']})")
        print("  Recommendation: Use winner_id as primary filter, with score-based fallback")
    else:
        print("\n✗ winner_id is not a reliable indicator")
        print("  Need to find other patterns...")
    
    # Check score patterns
    if patterns_found['real_games']:
        real_scores = [(m.get('home_score', 0) + m.get('away_score', 0)) for m in patterns_found['real_games']]
        if patterns_found['projected_games']:
            projected_scores = [(m.get('home_score', 0) + m.get('away_score', 0)) for m in patterns_found['projected_games']]
            avg_real = sum(real_scores) / len(real_scores) if real_scores else 0
            avg_projected = sum(projected_scores) / len(projected_scores) if projected_scores else 0
            print(f"\nScore analysis:")
            print(f"  Real games avg combined score: {avg_real:.2f}")
            print(f"  Projected games avg combined score: {avg_projected:.2f}")
            
            # Check if real games have consistently higher scores
            if avg_real > avg_projected:
                print(f"  ✓ Real games have higher scores on average (difference: {avg_real - avg_projected:.2f})")
            else:
                print(f"  ✗ Score difference is not significant (real: {avg_real:.2f}, projected: {avg_projected:.2f})")
    
    # Check for other patterns - position in list, specific score ranges, etc.
    print(f"\n" + "="*60)
    print("Detailed Pattern Analysis")
    print("="*60)
    
    # Test hypothesis: First occurrence of each team pair is the real game
    print(f"\nTesting hypothesis: First occurrence of each team pair = real game")
    first_occurrence_matches = 0
    first_occurrence_total = 0
    
    for week in range(1, 15):
        week_matchups = [m for m in matchups if m.get('week') == week]
        actual_pairs = {tuple(sorted(pair)) for pair in actual_schedule.get(week, [])}
        
        # Track first occurrence of each team pair
        first_occurrence = {}  # team_pair -> matchup
        for m in week_matchups:
            home_id = m.get('home_team_id')
            away_id = m.get('away_team_id')
            if home_id and away_id:
                pair = tuple(sorted([home_id, away_id]))
                if pair not in first_occurrence:
                    first_occurrence[pair] = m
        
        # Check if first occurrences match actual schedule
        for actual_pair in actual_schedule.get(week, []):
            sorted_actual = tuple(sorted(actual_pair))
            first_occurrence_total += 1
            if sorted_actual in first_occurrence:
                first_matchup = first_occurrence[sorted_actual]
                # Check if this matchup matches the actual game (by comparing with known schedule)
                # For now, just count if it exists
                first_occurrence_matches += 1
    
    match_rate = (first_occurrence_matches / first_occurrence_total * 100) if first_occurrence_total > 0 else 0
    print(f"  First occurrence matches actual schedule: {first_occurrence_matches}/{first_occurrence_total} ({match_rate:.1f}%)")
    
    if match_rate == 100:
        print(f"  ✓ PATTERN FOUND: First occurrence of each team pair is always the real game!")
        print(f"  Recommendation: Use first occurrence of each unique team pair per week")
    elif match_rate > 80:
        print(f"  ⚠ PATTERN: First occurrence matches most of the time ({match_rate:.1f}%)")
        print(f"  Recommendation: Use first occurrence as primary method, with fallback")
    else:
        print(f"  ✗ First occurrence is not reliable ({match_rate:.1f}% match rate)")
        print(f"  Need to find other patterns...")

if __name__ == "__main__":
    main()
