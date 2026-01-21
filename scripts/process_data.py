"""
Process scraped ESPN data into formats useful for the website
Calculates head-to-head records, all-time statistics, etc.
"""
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
OUTPUT_DIR = SCRIPT_DIR.parent / "data"

# Manager name mapping: ESPN display name -> First name
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

def load_all_seasons() -> Dict[int, Dict]:
    """Load all scraped season data"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print(f"Error: {all_seasons_file} not found")
        return {}
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    # Convert string keys to int
    return {int(k): v for k, v in all_data.items()}

def calculate_head_to_head(espn_data: Dict[int, Dict]) -> List[Dict]:
    """Calculate head-to-head records between all managers"""
    # Track wins and ties for each manager in each pair
    h2h_wins = defaultdict(lambda: defaultdict(int))
    h2h_ties = defaultdict(lambda: defaultdict(int))
    
    # Strategy: Use matchup_type field if available (from updated scraper),
    # otherwise fall back to first occurrence pattern (validated with 2025 schedule)
    
    for season, data in espn_data.items():
        matchups = data.get('matchups', [])
        
        # Check if we have matchup_type field (new data) or need to use fallback
        has_matchup_type = any(m.get('matchup_type') is not None for m in matchups[:10])
        
        # Group matchups by week
        matchups_by_week = defaultdict(list)
        for matchup in matchups:
            week = matchup.get('week', 0)
            if week > 0:
                matchups_by_week[week].append(matchup)
        
        # Process each week separately
        for week, week_matchups in matchups_by_week.items():
            # Store original week_matchups for fallback
            original_week_matchups = week_matchups.copy()
            
            # Strategy 1: Filter by matchup_period_id (most reliable - from raw API analysis)
            # Actual scheduled games for a week have matchupPeriodId == week
            # Projected games have different matchupPeriodId values
            # Check if we have this field in the data
            has_matchup_period_id = any(m.get('matchup_period_id') is not None for m in week_matchups[:5])
            
            if has_matchup_period_id:
                filtered_matchups = []
                for matchup in week_matchups:
                    matchup_period_id = matchup.get('matchup_period_id')
                    # If matchup_period_id matches the week, it's likely a scheduled game
                    if matchup_period_id == week:
                        filtered_matchups.append(matchup)
                
                # Validate filtered results: should have exactly 5 games, all with winner_id or ties
                # and each team should appear exactly once
                if filtered_matchups:
                    # Apply basic filters to get valid games
                    valid_filtered = []
                    for matchup in filtered_matchups:
                        home_id = matchup.get('home_team_id')
                        away_id = matchup.get('away_team_id')
                        home_score = matchup.get('home_score', 0)
                        away_score = matchup.get('away_score', 0)
                        winner_id = matchup.get('winner_id')
                        
                        if home_id is None or away_id is None:
                            continue
                        # Allow games with winner_id OR ties (home_score == away_score)
                        is_tie = (home_score == away_score and home_score > 0)
                        if not winner_id and not is_tie:
                            continue
                        if home_score == 0 and away_score == 0:
                            continue
                        if home_score < 50 and away_score < 50:
                            continue
                        
                        valid_filtered.append(matchup)
                    
                    # Check if we have exactly 5 games and each team appears once
                    if len(valid_filtered) == 5:
                        # Check that each team appears exactly once
                        team_counts = {}
                        for matchup in valid_filtered:
                            home_id = matchup.get('home_team_id')
                            away_id = matchup.get('away_team_id')
                            team_counts[home_id] = team_counts.get(home_id, 0) + 1
                            team_counts[away_id] = team_counts.get(away_id, 0) + 1
                        
                        # All teams should appear exactly once (10 teams, 5 games)
                        all_appear_once = all(count == 1 for count in team_counts.values())
                        
                        if all_appear_once:
                            # Validation passed - use filtered matchups
                            week_matchups = filtered_matchups
                        else:
                            # Validation failed - fall back to original
                            week_matchups = original_week_matchups
                    else:
                        # Not exactly 5 games - fall back to original
                        week_matchups = original_week_matchups
                else:
                    # No filtered matchups - fall back to original
                    week_matchups = original_week_matchups
            
            # Strategy 2: If we have matchup_type, filter by it (secondary filter)
            if has_matchup_type:
                # Filter to only scheduled matchups (not projected)
                scheduled_matchups = []
                for matchup in week_matchups:
                    matchup_type = matchup.get('matchup_type')
                    # ESPN uses 'SCHEDULED' or similar for actual games
                    # Projected games might be 'PROJECTED', None, or other values
                    if matchup_type and 'SCHEDULED' in str(matchup_type).upper():
                        scheduled_matchups.append(matchup)
                
                # If we found scheduled matchups, use them
                if scheduled_matchups:
                    week_matchups = scheduled_matchups
            
            # Strategy 3: Fallback - use first occurrence pattern
            # Track first occurrence of each unique team pair
            first_occurrence = {}  # team_pair -> matchup
            seen_pairs = set()
            
            # Process matchups in order - first occurrence is the real game
            for matchup in week_matchups:
                home_mgr = matchup.get('home_manager')
                away_mgr = matchup.get('away_manager')
                home_id = matchup.get('home_team_id')
                away_id = matchup.get('away_team_id')
                home_score = matchup.get('home_score', 0)
                away_score = matchup.get('away_score', 0)
                winner_id = matchup.get('winner_id')
                is_bye = matchup.get('is_bye', False)
                
                # Skip matchups with null team IDs (bye weeks, incomplete matchups)
                if home_id is None or away_id is None:
                    continue
                
                # Skip bye weeks
                if is_bye:
                    continue
                
                # Skip matchups with "Team None" managers (invalid matchups)
                if not home_mgr or not away_mgr:
                    continue
                if 'Team None' in home_mgr or 'Team None' in away_mgr:
                    continue
                
                # Skip games with 0-0 scores (not real games)
                if home_score == 0 and away_score == 0:
                    continue
                
                # Filter out unrealistic scores (both teams <50 points suggests placeholder/fake game)
                if home_score < 50 and away_score < 50:
                    continue
                
                # Only process games with winner_id (completed games) OR ties (home_score == away_score)
                # Ties have winner_id == None, so we need to check for ties separately
                is_tie = (home_score == away_score and home_score > 0)
                if not winner_id and not is_tie:
                    continue
                
                # Create unique key for this team pair
                team_pair = tuple(sorted([home_id, away_id]))
                
                # Track first occurrence of each team pair
                # This is the actual scheduled game (validated with 2025 schedule)
                if team_pair not in seen_pairs:
                    seen_pairs.add(team_pair)
                    first_occurrence[team_pair] = matchup
            
            # Process first occurrences - identify which 5 are the actual scheduled games
            # Strategy: Select 5 games such that each team appears exactly once
            # (10-team league = 5 matchups, so each team plays exactly once per week)
            
            # Get the order of first occurrences as they appear in week_matchups
            first_occurrence_ordered = []
            seen_in_order = set()
            
            for matchup in week_matchups:
                home_id = matchup.get('home_team_id')
                away_id = matchup.get('away_team_id')
                winner_id = matchup.get('winner_id')
                home_score = matchup.get('home_score', 0)
                away_score = matchup.get('away_score', 0)
                
                # Allow games with winner_id OR ties (home_score == away_score)
                is_tie = (home_score == away_score and home_score > 0)
                if home_id is None or away_id is None or (not winner_id and not is_tie):
                    continue
                
                team_pair = tuple(sorted([home_id, away_id]))
                
                # Only add if this is the first occurrence and we haven't seen it yet in order
                if team_pair in first_occurrence and team_pair not in seen_in_order:
                    seen_in_order.add(team_pair)
                    first_occurrence_ordered.append((team_pair, matchup))
            
            # Select 5 games ensuring each team appears exactly once
            selected_games = []
            used_teams = set()
            
            for team_pair, matchup in first_occurrence_ordered:
                if len(selected_games) >= 5:
                    break
                
                home_id = matchup.get('home_team_id')
                away_id = matchup.get('away_team_id')
                
                # Only add if neither team has been used yet
                if home_id not in used_teams and away_id not in used_teams:
                    selected_games.append((team_pair, matchup))
                    used_teams.add(home_id)
                    used_teams.add(away_id)
            
            # If we didn't get 5 games with the "each team once" constraint,
            # fall back to first 5 first occurrences
            if len(selected_games) < 5:
                selected_games = first_occurrence_ordered[:5]
            
            # Process selected games
            games_counted = 0
            for team_pair, matchup in selected_games:
                
                games_counted += 1
                
                home_mgr = matchup.get('home_manager')
                away_mgr = matchup.get('away_manager')
                home_score = matchup.get('home_score', 0)
                away_score = matchup.get('away_score', 0)
                
                # Convert to first names
                home_first = extract_first_name(home_mgr)
                away_first = extract_first_name(away_mgr)
                
                # Skip if same person (shouldn't happen, but just in case)
                if home_first == away_first:
                    continue
                
                # Create sorted key for pair (always same order)
                pair_key = tuple(sorted([home_first, away_first]))
                
                # Record the result
                if home_score > away_score:
                    h2h_wins[pair_key][home_first] += 1
                elif away_score > home_score:
                    h2h_wins[pair_key][away_first] += 1
                elif home_score == away_score:
                    # Ties: both managers get a tie
                    h2h_ties[pair_key][home_first] += 1
                    h2h_ties[pair_key][away_first] += 1
    
    # Convert to list format
    results = []
    # Get all unique pairs from both wins and ties
    all_pairs = set(h2h_wins.keys()) | set(h2h_ties.keys())
    
    for pair_key in all_pairs:
        wins_records = h2h_wins.get(pair_key, {})
        ties_records = h2h_ties.get(pair_key, {})
        
        mgr1, mgr2 = pair_key
        wins1 = wins_records.get(mgr1, 0)
        wins2 = wins_records.get(mgr2, 0)
        ties1 = ties_records.get(mgr1, 0)
        ties2 = ties_records.get(mgr2, 0)
        
        # Ties should be the same for both managers in a pair
        ties = max(ties1, ties2)
        
        if wins1 + wins2 + ties > 0:  # Only include if they've played
            # Format record string: "W-L" if no ties, "W-L-T" if ties exist
            if ties > 0:
                record_str = f"{wins1}-{wins2}-{ties}"
            else:
                record_str = f"{wins1}-{wins2}"
            
            results.append({
                'manager1': mgr1,
                'manager2': mgr2,
                'manager1Wins': wins1,
                'manager2Wins': wins2,
                'ties': ties,
                'record': record_str,
            })
    
    # Sort by total games played (most competitive matchups first)
    results.sort(key=lambda x: x['manager1Wins'] + x['manager2Wins'] + x.get('ties', 0), reverse=True)
    
    return results

def get_valid_regular_season_matchups(week_matchups: List[Dict], week: int, has_matchup_type: bool) -> List[Dict]:
    """Extract valid regular season matchups for a week using the same filtering logic as head-to-head"""
    original_week_matchups = week_matchups.copy()
    
    # Strategy 1: Filter by matchup_period_id
    has_matchup_period_id = any(m.get('matchup_period_id') is not None for m in week_matchups[:5])
    
    if has_matchup_period_id:
        filtered_matchups = []
        for matchup in week_matchups:
            matchup_period_id = matchup.get('matchup_period_id')
            if matchup_period_id == week:
                filtered_matchups.append(matchup)
        
        if filtered_matchups:
            valid_filtered = []
            for matchup in filtered_matchups:
                home_id = matchup.get('home_team_id')
                away_id = matchup.get('away_team_id')
                home_score = matchup.get('home_score', 0)
                away_score = matchup.get('away_score', 0)
                winner_id = matchup.get('winner_id')
                is_playoff = matchup.get('is_playoff', False)
                
                if home_id is None or away_id is None:
                    continue
                if is_playoff:
                    continue
                is_tie = (home_score == away_score and home_score > 0)
                if not winner_id and not is_tie:
                    continue
                if home_score == 0 and away_score == 0:
                    continue
                if home_score < 50 and away_score < 50:
                    continue
                
                valid_filtered.append(matchup)
            
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
    
    # Strategy 2: Filter by matchup_type if available
    if has_matchup_type:
        scheduled_matchups = []
        for matchup in week_matchups:
            matchup_type = matchup.get('matchup_type')
            if matchup_type and 'SCHEDULED' in str(matchup_type).upper():
                scheduled_matchups.append(matchup)
        if scheduled_matchups:
            week_matchups = scheduled_matchups
    
    # Strategy 3: First occurrence pattern
    first_occurrence = {}
    seen_pairs = set()
    
    for matchup in week_matchups:
        home_id = matchup.get('home_team_id')
        away_id = matchup.get('away_team_id')
        home_score = matchup.get('home_score', 0)
        away_score = matchup.get('away_score', 0)
        winner_id = matchup.get('winner_id')
        is_bye = matchup.get('is_bye', False)
        is_playoff = matchup.get('is_playoff', False)
        
        if home_id is None or away_id is None:
            continue
        if is_bye or is_playoff:
            continue
        if home_score == 0 and away_score == 0:
            continue
        if home_score < 50 and away_score < 50:
            continue
        is_tie = (home_score == away_score and home_score > 0)
        if not winner_id and not is_tie:
            continue
        
        team_pair = tuple(sorted([home_id, away_id]))
        if team_pair not in seen_pairs:
            seen_pairs.add(team_pair)
            first_occurrence[team_pair] = matchup
    
    # Get ordered first occurrences
    first_occurrence_ordered = []
    seen_in_order = set()
    
    for matchup in week_matchups:
        home_id = matchup.get('home_team_id')
        away_id = matchup.get('away_team_id')
        winner_id = matchup.get('winner_id')
        home_score = matchup.get('home_score', 0)
        away_score = matchup.get('away_score', 0)
        is_playoff = matchup.get('is_playoff', False)
        
        if is_playoff:
            continue
        is_tie = (home_score == away_score and home_score > 0)
        if home_id is None or away_id is None or (not winner_id and not is_tie):
            continue
        
        team_pair = tuple(sorted([home_id, away_id]))
        if team_pair in first_occurrence and team_pair not in seen_in_order:
            seen_in_order.add(team_pair)
            first_occurrence_ordered.append((team_pair, matchup))
    
    # Select 5 games ensuring each team appears exactly once
    selected_games = []
    used_teams = set()
    
    for team_pair, matchup in first_occurrence_ordered:
        if len(selected_games) >= 5:
            break
        home_id = matchup.get('home_team_id')
        away_id = matchup.get('away_team_id')
        if home_id not in used_teams and away_id not in used_teams:
            selected_games.append((team_pair, matchup))
            used_teams.add(home_id)
            used_teams.add(away_id)
    
    if len(selected_games) < 5:
        selected_games = first_occurrence_ordered[:5]
    
    # Return just the matchups
    return [matchup for _, matchup in selected_games]

def calculate_season_totals_from_matchups(espn_data: Dict[int, Dict]) -> Tuple[Dict[Tuple[int, str], float], Dict[str, int]]:
    """Calculate season point totals and total games played from regular season matchups only"""
    season_totals = defaultdict(float)  # (season, manager) -> total points
    total_games = defaultdict(int)  # manager -> total games played
    
    for season, data in espn_data.items():
        matchups = data.get('matchups', [])
        has_matchup_type = any(m.get('matchup_type') is not None for m in matchups[:10])
        
        # Group matchups by week
        matchups_by_week = defaultdict(list)
        for matchup in matchups:
            week = matchup.get('week', 0)
            if week > 0:
                matchups_by_week[week].append(matchup)
        
        # Process each week
        for week, week_matchups in matchups_by_week.items():
            valid_matchups = get_valid_regular_season_matchups(week_matchups, week, has_matchup_type)
            
            for matchup in valid_matchups:
                home_mgr = matchup.get('home_manager', '')
                away_mgr = matchup.get('away_manager', '')
                home_score = matchup.get('home_score', 0)
                away_score = matchup.get('away_score', 0)
                
                if not home_mgr or not away_mgr:
                    continue
                if 'Team None' in home_mgr or 'Team None' in away_mgr:
                    continue
                
                home_first = extract_first_name(home_mgr)
                away_first = extract_first_name(away_mgr)
                
                season_totals[(season, home_first)] += home_score
                season_totals[(season, away_first)] += away_score
                
                # Count games played (each matchup = 1 game per manager)
                total_games[home_first] += 1
                total_games[away_first] += 1
    
    return season_totals, total_games

def calculate_all_time_stats(espn_data: Dict[int, Dict]) -> Dict:
    """Calculate all-time statistics"""
    stats = {
        'all_single_games': [],  # List of all single game scores
        'all_season_totals': [],  # List of all season totals
        'all_season_records': [],  # List of all season records
        'most_points_all_time': defaultdict(float),
        'total_wins': defaultdict(int),
        'total_losses': defaultdict(int),
    }
    
    # Calculate season totals from regular season matchups only
    season_totals, total_games = calculate_season_totals_from_matchups(espn_data)
    
    for season, data in espn_data.items():
        matchups = data.get('matchups', [])
        standings = data.get('standings', [])
        
        # Use the same filtering logic as head-to-head to get valid regular season games
        has_matchup_type = any(m.get('matchup_type') is not None for m in matchups[:10])
        
        # Group matchups by week
        matchups_by_week = defaultdict(list)
        for matchup in matchups:
            week = matchup.get('week', 0)
            if week > 0:
                matchups_by_week[week].append(matchup)
        
        # Process each week to get valid games only
        seen_games = set()  # Track (season, week, manager, score) to deduplicate
        for week, week_matchups in matchups_by_week.items():
            valid_matchups = get_valid_regular_season_matchups(week_matchups, week, has_matchup_type)
            
            for matchup in valid_matchups:
                home_mgr = matchup.get('home_manager', '')
                away_mgr = matchup.get('away_manager', '')
                home_score = matchup.get('home_score', 0)
                away_score = matchup.get('away_score', 0)
                
                if not home_mgr or not away_mgr:
                    continue
                if 'Team None' in home_mgr or 'Team None' in away_mgr:
                    continue
                
                home_mgr_first = extract_first_name(home_mgr)
                away_mgr_first = extract_first_name(away_mgr)
                
                # Collect home score (deduplicate)
                if home_score > 0:
                    game_key = (season, week, home_mgr_first, home_score)
                    if game_key not in seen_games:
                        seen_games.add(game_key)
                        stats['all_single_games'].append({
                            'score': home_score,
                            'manager': home_mgr_first,
                            'week': week,
                            'season': season,
                        })
                
                # Collect away score (deduplicate)
                if away_score > 0:
                    game_key = (season, week, away_mgr_first, away_score)
                    if game_key not in seen_games:
                        seen_games.add(game_key)
                        stats['all_single_games'].append({
                            'score': away_score,
                            'manager': away_mgr_first,
                            'week': week,
                            'season': season,
                        })
        
        # Collect all season records from standings
        for team in standings:
            manager = extract_first_name(team.get('manager', ''))
            wins = team.get('wins', 0)
            losses = team.get('losses', 0)
            
            if wins + losses > 0:  # Only include valid records
                stats['all_season_records'].append({
                    'wins': wins,
                    'losses': losses,
                    'manager': manager,
                    'season': season,
                })
            
            # Accumulate all-time stats - use matchup-based totals for points
            # Use standings for wins/losses (still reliable)
            season_points = season_totals.get((season, manager), 0)
            stats['most_points_all_time'][manager] += season_points
            stats['total_wins'][manager] += wins
            stats['total_losses'][manager] += losses
    
    # Collect all season totals from matchup-based calculation
    for (s, manager), points in season_totals.items():
        if points > 0:
            stats['all_season_totals'].append({
                'points': points,
                'manager': manager,
                'season': s,
            })
    
    # Return season_totals and total_games for average calculation
    stats['season_totals'] = season_totals
    stats['total_games'] = total_games
    
    return stats

def generate_all_time_records(espn_data: Dict[int, Dict], champs_data: Dict) -> List[Dict]:
    """Generate all-time records list"""
    stats = calculate_all_time_stats(espn_data)
    season_totals = stats.get('season_totals', {})
    
    records = []
    
    # Highest Single Game Score - Top 5
    if stats['all_single_games']:
        # Sort by score descending
        sorted_games = sorted(stats['all_single_games'], key=lambda x: x['score'], reverse=True)
        top5_games = sorted_games[:5]
        
        top5_list = []
        for idx, game in enumerate(top5_games, 1):
            top5_list.append({
                'rank': idx,
                'holder': game['manager'],
                'record': f"{game['score']:.2f} points",
                'details': f"Week {game['week']}, {game['season']}",
            })
        
        records.append({
            'category': 'Highest Single Game Score',
            'top5': top5_list,
        })
    
    # Most Points in a Season - Top 5
    if stats['all_season_totals']:
        # Sort by points descending
        sorted_seasons = sorted(stats['all_season_totals'], key=lambda x: x['points'], reverse=True)
        top5_seasons = sorted_seasons[:5]
        
        top5_list = []
        for idx, season in enumerate(top5_seasons, 1):
            top5_list.append({
                'rank': idx,
                'holder': season['manager'],
                'record': f"{season['points']:.2f} points",
                'details': f"{season['season']} Season",
            })
        
        records.append({
            'category': 'Most Points in a Season',
            'top5': top5_list,
        })
    
    # Best Regular Season Record - Top 5
    if stats['all_season_records']:
        # Sort by win percentage (descending), then wins (descending)
        def record_sort_key(r):
            win_pct = r['wins'] / (r['wins'] + r['losses']) if (r['wins'] + r['losses']) > 0 else 0
            return (-win_pct, -r['wins'])  # Negative for descending
        
        sorted_records = sorted(stats['all_season_records'], key=record_sort_key)
        top5_records = sorted_records[:5]
        
        top5_list = []
        for idx, record in enumerate(top5_records, 1):
            top5_list.append({
                'rank': idx,
                'holder': record['manager'],
                'record': f"{record['wins']}-{record['losses']}",
                'details': f"{record['season']} Season",
            })
        
        records.append({
            'category': 'Best Regular Season Record',
            'top5': top5_list,
        })
    
    # Highest Average Points Per Game - Top 5
    if stats['most_points_all_time'] and stats.get('total_games'):
        total_games = stats['total_games']
        
        # Calculate average points per game for each manager
        averages = []
        for manager, total_points in stats['most_points_all_time'].items():
            games = total_games.get(manager, 0)
            if games > 0:
                avg = total_points / games
                averages.append({
                    'manager': manager,
                    'average': avg,
                    'games': games,
                })
        
        if averages:
            # Sort by average descending
            sorted_averages = sorted(averages, key=lambda x: x['average'], reverse=True)
            top5_averages = sorted_averages[:5]
            
            top5_list = []
            for idx, avg_data in enumerate(top5_averages, 1):
                top5_list.append({
                    'rank': idx,
                    'holder': avg_data['manager'],
                    'record': f"{avg_data['average']:.2f} points",
                    'details': f"Average across {avg_data['games']} game{'s' if avg_data['games'] != 1 else ''}",
                })
            
            records.append({
                'category': 'Highest Average Points Per Game',
                'top5': top5_list,
            })
    
    return records

def main():
    """Process data and generate output files"""
    print("="*70)
    print("Processing ESPN Data for Website")
    print("="*70)
    
    # Load data
    print("\nLoading data...")
    espn_data = load_all_seasons()
    if not espn_data:
        print("❌ No ESPN data found")
        return
    
    print(f"✓ Loaded {len(espn_data)} seasons")
    
    # Load championship data for context
    champs_file = OUTPUT_DIR / "champions.js"
    champs_data = {}
    if champs_file.exists():
        # Simple parsing - just get champion names by year
        with open(champs_file, 'r') as f:
            content = f.read()
            import re
            for match in re.finditer(r'year:\s*(\d+)[^}]*champion:\s*"([^"]*)"', content):
                year = int(match.group(1))
                champ = match.group(2)
                champs_data[year] = {'champion': champ}
    
    # Calculate head-to-head
    print("\nCalculating head-to-head records...")
    h2h_records = calculate_head_to_head(espn_data)
    print(f"✓ Found {len(h2h_records)} manager pairs")
    
    # Calculate all-time stats
    print("\nCalculating all-time statistics...")
    all_time_records = generate_all_time_records(espn_data, champs_data)
    print(f"✓ Generated {len(all_time_records)} records")
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Save head-to-head data
    h2h_file = OUTPUT_DIR / "headToHead.js"
    with open(h2h_file, 'w') as f:
        f.write("// JBS FFL Head-to-Head Records\n")
        f.write("// Generated from ESPN scraped data\n\n")
        f.write("export const headToHeadRecords = [\n")
        for record in h2h_records:
            f.write(f"  {{\n")
            f.write(f"    manager1: \"{record['manager1']}\",\n")
            f.write(f"    manager2: \"{record['manager2']}\",\n")
            f.write(f"    manager1Wins: {record['manager1Wins']},\n")
            f.write(f"    manager2Wins: {record['manager2Wins']},\n")
            f.write(f"    ties: {record.get('ties', 0)},\n")
            f.write(f"    record: \"{record['record']}\",\n")
            f.write(f"  }},\n")
        f.write("];\n")
    print(f"✓ Saved head-to-head data to {h2h_file}")
    
    # Save all-time records
    records_file = OUTPUT_DIR / "allTimeRecords.js"
    with open(records_file, 'w') as f:
        f.write("// JBS FFL All-Time Records\n")
        f.write("// Generated from ESPN scraped data\n\n")
        f.write("export const allTimeRecords = [\n")
        for record in all_time_records:
            f.write(f"  {{\n")
            f.write(f"    category: \"{record['category']}\",\n")
            if 'top5' in record:
                f.write(f"    top5: [\n")
                for entry in record['top5']:
                    f.write(f"      {{\n")
                    f.write(f"        rank: {entry['rank']},\n")
                    f.write(f"        holder: \"{entry['holder']}\",\n")
                    f.write(f"        record: \"{entry['record']}\",\n")
                    f.write(f"        details: \"{entry['details']}\",\n")
                    f.write(f"      }},\n")
                f.write(f"    ],\n")
            else:
                # Backward compatibility for single records
                f.write(f"    record: \"{record.get('record', '')}\",\n")
                f.write(f"    holder: \"{record.get('holder', '')}\",\n")
                f.write(f"    details: \"{record.get('details', '')}\",\n")
            f.write(f"  }},\n")
        f.write("];\n")
    print(f"✓ Saved all-time records to {records_file}")
    
    print("\n" + "="*70)
    print("✓ Data processing complete!")
    print("="*70)
    print(f"\nGenerated files:")
    print(f"  - {h2h_file}")
    print(f"  - {records_file}")
    print(f"\nNext steps:")
    print(f"  1. Update all-time-records/page.tsx to import allTimeRecords")
    print(f"  2. Update head-to-head/page.tsx to import headToHeadRecords")

if __name__ == "__main__":
    main()
