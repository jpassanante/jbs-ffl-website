"""
Calculate Power Rankings for a season using ESPN scraped data
Replaces manual data entry with automated calculation

Power Rankings formula:
- Record: Rank by cumulative wins (higher rank = more wins = better)
- Points: Rank by cumulative total points (higher rank = more points = better)
- Breakdown: Rank by cumulative theoretical wins (higher rank = more theoretical wins = better)
- Total: Sum of Record + Points + Breakdown (higher is better)

Usage:
    python calculate_power_rankings.py <season>    # Process single season
    python calculate_power_rankings.py --all        # Process all available seasons
    python calculate_power_rankings.py -a           # Process all available seasons

Output:
    For each season, generates:
    - power_rankings_YYYY.csv (detailed data)
    - power_rankings_YYYY_summary.csv (weekly summary format)
"""
import json
import csv
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

def get_valid_regular_season_matchups(week_matchups: List[Dict], week: int, has_matchup_type: bool) -> List[Dict]:
    """Get valid regular season matchups for a week (same logic as process_data.py)"""
    # Strategy 1: Filter by matchup_period_id == week
    valid_matchups = []
    for matchup in week_matchups:
        matchup_period_id = matchup.get('matchup_period_id')
        is_playoff = matchup.get('is_playoff', False)
        
        if matchup_period_id == week and not is_playoff:
            valid_matchups.append(matchup)
    
    if valid_matchups:
        # Use first occurrence pattern
        seen_pairs = set()
        first_occurrence = []
        
        for matchup in valid_matchups:
            home_id = matchup.get('home_team_id')
            away_id = matchup.get('away_team_id')
            home_score = matchup.get('home_score', 0)
            away_score = matchup.get('away_score', 0)
            winner_id = matchup.get('winner_id')
            
            if home_id is None or away_id is None:
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
                first_occurrence.append(matchup)
        
        return first_occurrence
    
    return []

def calculate_rank_with_ties(values: List[Tuple[float, str]], total_teams: int) -> Dict[str, float]:
    """
    Calculate ranks with proper tie handling
    Returns dict mapping manager -> rank (HIGHER is better, like Matt's system)
    Ties get average rank (e.g., two teams tied for 8th/9th = both get 8.5)
    In Matt's system: rank 10 = best, rank 1 = worst
    """
    # Sort by value descending (higher value = better = higher rank)
    sorted_values = sorted(values, key=lambda x: x[0], reverse=True)
    
    ranks = {}
    i = 0
    while i < len(sorted_values):
        value = sorted_values[i][0]
        # Find all items with same value
        tie_group = []
        j = i
        while j < len(sorted_values) and sorted_values[j][0] == value:
            tie_group.append(sorted_values[j][1])  # manager name
            j += 1
        
        # Calculate average rank for this group
        # In Matt's system: best performer gets highest rank (total_teams)
        # Worst performer gets rank 1
        rank_start = total_teams - j + 1  # Invert: best (index 0) gets rank total_teams
        rank_end = total_teams - i  # Worst in tie group
        avg_rank = (rank_start + rank_end) / 2.0
        
        # Assign average rank to all in tie group
        for manager in tie_group:
            ranks[manager] = avg_rank
        
        i = j
    
    return ranks

def calculate_power_rankings(season: int) -> List[Dict]:
    """
    Calculate power rankings for a season, week by week
    Returns list of week data with rankings
    """
    # Load ESPN data
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print(f"Error: {all_seasons_file} not found")
        return []
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    season_data = all_data.get(str(season))
    if not season_data:
        print(f"Error: Season {season} not found in data")
        return []
    
    matchups = season_data.get('matchups', [])
    has_matchup_type = any(m.get('matchup_type') is not None for m in matchups[:10])
    
    # Group matchups by week
    matchups_by_week = defaultdict(list)
    for matchup in matchups:
        week = matchup.get('week', 0)
        if week > 0:
            matchups_by_week[week].append(matchup)
    
    # Track cumulative stats
    wins = defaultdict(int)
    losses = defaultdict(int)
    ties = defaultdict(int)
    total_points = defaultdict(float)
    
    # Track weekly scores for theoretical record calculation
    weekly_scores = defaultdict(dict)  # week -> manager -> score
    
    power_rankings = []
    
    # Process each week
    for week in sorted(matchups_by_week.keys()):
        week_matchups = matchups_by_week[week]
        valid_matchups = get_valid_regular_season_matchups(week_matchups, week, has_matchup_type)
        
        # Get all managers and their scores for this week
        week_scores = {}  # manager -> score
        
        for matchup in valid_matchups:
            home_mgr = matchup.get('home_manager', '')
            away_mgr = matchup.get('away_manager', '')
            home_score = matchup.get('home_score', 0)
            away_score = matchup.get('away_score', 0)
            winner_id = matchup.get('winner_id')
            
            if not home_mgr or not away_mgr:
                continue
            if 'Team None' in home_mgr or 'Team None' in away_mgr:
                continue
            
            home_first = extract_first_name(home_mgr)
            away_first = extract_first_name(away_mgr)
            
            # Store weekly scores
            week_scores[home_first] = home_score
            week_scores[away_first] = away_score
            weekly_scores[week][home_first] = home_score
            weekly_scores[week][away_first] = away_score
            
            # Update cumulative points
            total_points[home_first] += home_score
            total_points[away_first] += away_score
            
            # Update record
            is_tie = (home_score == away_score and home_score > 0)
            if is_tie:
                ties[home_first] += 1
                ties[away_first] += 1
            elif winner_id:
                if winner_id == matchup.get('home_team_id'):
                    wins[home_first] += 1
                    losses[away_first] += 1
                else:
                    wins[away_first] += 1
                    losses[home_first] += 1
        
        # Calculate theoretical record for this week
        # For each manager, compare their score against all other managers' scores
        theoretical_wins = defaultdict(int)
        theoretical_losses = defaultdict(int)
        theoretical_ties = defaultdict(int)
        
        managers_this_week = list(week_scores.keys())
        for manager in managers_this_week:
            manager_score = week_scores[manager]
            for opponent in managers_this_week:
                if manager == opponent:
                    continue
                opponent_score = week_scores[opponent]
                if manager_score > opponent_score:
                    theoretical_wins[manager] += 1
                elif manager_score < opponent_score:
                    theoretical_losses[manager] += 1
                else:
                    theoretical_ties[manager] += 1
        
        # Calculate cumulative theoretical record up to this week
        cum_theoretical_wins = defaultdict(int)
        cum_theoretical_losses = defaultdict(int)
        cum_theoretical_ties = defaultdict(int)
        
        for w in range(1, week + 1):
            if w in weekly_scores:
                week_mgrs = list(weekly_scores[w].keys())
                for manager in week_mgrs:
                    manager_score = weekly_scores[w][manager]
                    for opponent in week_mgrs:
                        if manager == opponent:
                            continue
                        opponent_score = weekly_scores[w][opponent]
                        if manager_score > opponent_score:
                            cum_theoretical_wins[manager] += 1
                        elif manager_score < opponent_score:
                            cum_theoretical_losses[manager] += 1
                        else:
                            cum_theoretical_ties[manager] += 1
        
        # Get all managers who have played
        all_managers = set()
        all_managers.update(wins.keys())
        all_managers.update(losses.keys())
        all_managers.update(total_points.keys())
        
        if not all_managers:
            continue
        
        # Calculate rankings
        # 1. Record ranking (by cumulative wins, not win percentage)
        # Matt ranks by total wins, where more wins = higher rank = better
        record_values = [(wins[manager], manager) for manager in all_managers]
        
        num_teams = len(all_managers)
        
        record_ranks = calculate_rank_with_ties(record_values, num_teams)
        
        # 2. Points ranking (by total points)
        points_values = [(total_points[manager], manager) for manager in all_managers]
        points_ranks = calculate_rank_with_ties(points_values, num_teams)
        
        # 3. Breakdown ranking (by cumulative theoretical wins, not percentage)
        # Matt ranks by total theoretical wins, not win percentage
        breakdown_values = [(cum_theoretical_wins[manager], manager) for manager in all_managers]
        breakdown_ranks = calculate_rank_with_ties(breakdown_values, num_teams)
        
        # Calculate totals and create week ranking
        week_rankings = []
        for manager in all_managers:
            # Default to worst rank (1) if not found
            record_rank = record_ranks.get(manager, 1)
            points_rank = points_ranks.get(manager, 1)
            breakdown_rank = breakdown_ranks.get(manager, 1)
            total_rank = record_rank + points_rank + breakdown_rank
            
            week_rankings.append({
                'week': week,
                'manager': manager,
                'record_rank': record_rank,
                'points_rank': points_rank,
                'breakdown_rank': breakdown_rank,
                'total_rank': total_rank,
                'wins': wins[manager],
                'losses': losses[manager],
                'ties': ties[manager],
                'total_points': total_points[manager],
                'theoretical_wins': cum_theoretical_wins[manager],
                'theoretical_losses': cum_theoretical_losses[manager],
                'theoretical_ties': cum_theoretical_ties[manager],
            })
        
        # Sort by total rank (higher is better in Matt's system)
        week_rankings.sort(key=lambda x: x['total_rank'], reverse=True)
        
        power_rankings.extend(week_rankings)
    
    return power_rankings

def export_to_csv(rankings: List[Dict], season: int, output_file: Path):
    """Export power rankings to CSV format"""
    if not rankings:
        print("No rankings to export")
        return
    
    # Group by week
    by_week = defaultdict(list)
    for ranking in rankings:
        by_week[ranking['week']].append(ranking)
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(['Week', 'Manager', 'Record Rank', 'Points Rank', 'Breakdown Rank', 
                        'Total Rank', 'Wins', 'Losses', 'Ties', 'Total Points',
                        'Theoretical Wins', 'Theoretical Losses', 'Theoretical Ties'])
        
        # Write data by week
        for week in sorted(by_week.keys()):
            week_data = by_week[week]
            for ranking in week_data:
                writer.writerow([
                    ranking['week'],
                    ranking['manager'],
                    ranking['record_rank'],
                    ranking['points_rank'],
                    ranking['breakdown_rank'],
                    ranking['total_rank'],
                    ranking['wins'],
                    ranking['losses'],
                    ranking['ties'],
                    f"{ranking['total_points']:.2f}",
                    ranking['theoretical_wins'],
                    ranking['theoretical_losses'],
                    ranking['theoretical_ties'],
                ])
    
    print(f"Exported power rankings to {output_file}")

def export_weekly_summary(rankings: List[Dict], season: int, output_file: Path):
    """Export weekly summary in format similar to Google Sheets"""
    if not rankings:
        print("No rankings to export")
        return
    
    # Group by week
    by_week = defaultdict(list)
    for ranking in rankings:
        by_week[ranking['week']].append(ranking)
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        for week in sorted(by_week.keys()):
            week_data = sorted(by_week[week], key=lambda x: x['total_rank'], reverse=True)
            
            # Write week header
            writer.writerow([f'Week {week}'])
            writer.writerow(['Traditional Ranking', 'Record', 'Points', 'Breakdown', 'Total'])
            
            # Write rankings
            for ranking in week_data:
                writer.writerow([
                    ranking['manager'],
                    ranking['record_rank'],
                    ranking['points_rank'],
                    ranking['breakdown_rank'],
                    ranking['total_rank'],
                ])
            
            writer.writerow([])  # Empty row between weeks
    
    print(f"Exported weekly summary to {output_file}")

def get_available_seasons() -> List[int]:
    """Get list of all available seasons from the scraped data"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print(f"Error: {all_seasons_file} not found")
        return []
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    # Get all season years and sort them
    seasons = sorted([int(k) for k in all_data.keys()])
    return seasons

def process_single_season(season: int) -> bool:
    """Process power rankings for a single season"""
    print(f"\n{'='*60}")
    print(f"Calculating power rankings for {season}...")
    print(f"{'='*60}")
    
    rankings = calculate_power_rankings(season)
    
    if not rankings:
        print(f"⚠ No rankings calculated for {season}. Skipping.")
        return False
    
    # Export to CSV
    csv_file = OUTPUT_DIR / f"power_rankings_{season}.csv"
    export_to_csv(rankings, season, csv_file)
    
    # Export weekly summary
    summary_file = OUTPUT_DIR / f"power_rankings_{season}_summary.csv"
    export_weekly_summary(rankings, season, summary_file)
    
    weeks = len(set(r['week'] for r in rankings))
    print(f"✓ Completed {season}: {weeks} weeks, {len(rankings)} total rankings")
    return True

def process_all_seasons():
    """Process power rankings for all available seasons"""
    seasons = get_available_seasons()
    
    if not seasons:
        print("No seasons found in data. Make sure espn_all_seasons.json exists.")
        return
    
    print(f"\n{'='*60}")
    print(f"Generating Power Rankings for All Seasons")
    print(f"Found {len(seasons)} seasons: {min(seasons)}-{max(seasons)}")
    print(f"{'='*60}\n")
    
    successful = 0
    failed = 0
    
    for season in seasons:
        if process_single_season(season):
            successful += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Batch Processing Complete!")
    print(f"✓ Successful: {successful} seasons")
    if failed > 0:
        print(f"⚠ Failed: {failed} seasons")
    print(f"{'='*60}")

def main():
    import sys
    
    # Check for --all flag or if no argument provided
    if len(sys.argv) < 2 or '--all' in sys.argv or '-a' in sys.argv:
        process_all_seasons()
        return
    
    # Single season mode
    try:
        season = int(sys.argv[1])
        process_single_season(season)
    except ValueError:
        print("Error: Season must be a number")
        print("Usage: python calculate_power_rankings.py <season>")
        print("       python calculate_power_rankings.py --all  (process all seasons)")
        print("Example: python calculate_power_rankings.py 2024")
        sys.exit(1)

if __name__ == "__main__":
    main()
