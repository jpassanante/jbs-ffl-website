"""
Compare ESPN Scraped Data with champions.js
Validates championship results and identifies discrepancies

Usage:
    python compare_championships.py
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
CHAMPIONS_FILE = SCRIPT_DIR.parent / "data" / "champions.js"

# Manager name mapping: ESPN display name -> First name used in champions.js
# This will be built dynamically, but we can add known mappings
MANAGER_MAPPING = {
    # Add known mappings here if needed
    # "benhkline": "Ben",
    # "PLazaroff": "Peter",
    # etc.
}


def parse_champions_js() -> Dict[int, Dict]:
    """Parse champions.js file and extract championship data"""
    if not CHAMPIONS_FILE.exists():
        print(f"Error: {CHAMPIONS_FILE} not found")
        return {}
    
    with open(CHAMPIONS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the championships array using regex
    # Look for the array content between export const championships = [ and ];
    pattern = r'export\s+const\s+championships\s*=\s*\[(.*?)\];'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("Error: Could not parse champions.js file")
        return {}
    
    array_content = match.group(1)
    
    # Parse each championship object
    championships = {}
    
    # Find all championship objects
    obj_pattern = r'\{[^}]*year:\s*(\d+)[^}]*\}'
    for obj_match in re.finditer(obj_pattern, array_content, re.DOTALL):
        obj_str = obj_match.group(0)
        year_match = re.search(r'year:\s*(\d+)', obj_str)
        if not year_match:
            continue
        
        year = int(year_match.group(1))
        
        # Extract fields
        champ = re.search(r'champion:\s*"([^"]*)"', obj_str)
        runner_up = re.search(r'runnerUp:\s*"([^"]*)"', obj_str)
        third_place = re.search(r'thirdPlace:\s*"([^"]*)"', obj_str)
        reg_season_champ = re.search(r'regularSeasonChamp:\s*"([^"]*)"', obj_str)
        other_div_champ = re.search(r'otherDivisionChamp:\s*"([^"]*)"', obj_str)
        most_points = re.search(r'regularSeasonMostPoints:\s*"([^"]*)"', obj_str)
        
        championships[year] = {
            'champion': champ.group(1) if champ else None,
            'runnerUp': runner_up.group(1) if runner_up else None,
            'thirdPlace': third_place.group(1) if third_place else None,
            'regularSeasonChamp': reg_season_champ.group(1) if reg_season_champ else None,
            'otherDivisionChamp': other_div_champ.group(1) if other_div_champ else None,
            'regularSeasonMostPoints': most_points.group(1) if most_points else None,
        }
    
    return championships


def load_espn_data() -> Dict[int, Dict]:
    """Load ESPN scraped data"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print(f"Error: {all_seasons_file} not found")
        return {}
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    # Convert string keys to int
    return {int(k): v for k, v in all_data.items()}


def extract_first_name(display_name: str) -> str:
    """Extract first name from ESPN display name"""
    # Remove numbers and common suffixes
    name = display_name.lower()
    
    # Known mappings based on common patterns and user notes
    name_mappings = {
        'benhkline': 'Ben',
        'plazaroff': 'Peter',
        'lannybenson13': 'Lanny',
        'jpassana': 'Joey',
        'tybear612': 'Tyler',
        'vchapli1': 'Vernon',
        'johnnyhubes123': 'John',
        'mendy1399': 'Matt',
        'ugadogs34': 'Ted',
        'jayd3456': 'Jason',  # Based on user's note about Jason Dupont replacing Ty Fridrich
        'tyfredstl': 'Ty',  # Ty Fridrich (replaced by Jason Dupont)
        # Add more as discovered
    }
    
    if name in name_mappings:
        return name_mappings[name]
    
    # Try to extract first name from display name
    # Remove numbers
    name = re.sub(r'\d+', '', name)
    # Capitalize first letter
    if name:
        return name[0].upper() + name[1:] if len(name) > 1 else name.upper()
    
    return display_name


def build_manager_mapping(espn_data: Dict[int, Dict]) -> Dict[str, str]:
    """Build mapping from ESPN manager names to first names"""
    mapping = {}
    
    for season, data in espn_data.items():
        teams = data.get('teams', {})
        for manager, team_info in teams.items():
            if manager not in mapping:
                # Try to get first name from member data if available
                # For now, use extract_first_name
                first_name = extract_first_name(manager)
                mapping[manager] = first_name
    
    return mapping


def extract_playoff_results(espn_data: Dict, season: int, return_debug: bool = False) -> Dict:
    """Extract playoff results from ESPN data"""
    season_data = espn_data.get(season, {})
    if not season_data:
        return {}
    
    results = {
        'champion': None,
        'runnerUp': None,
        'thirdPlace': None,
        'regularSeasonChamp': None,
        'regularSeasonMostPoints': None,
    }
    
    # Get standings for regular season champ and most points
    standings = season_data.get('standings', [])
    if standings:
        results['regularSeasonChamp'] = standings[0].get('manager')
        # Most points
        most_points = max(standings, key=lambda x: x.get('points_for', 0))
        results['regularSeasonMostPoints'] = most_points.get('manager')
    
    # Try to get from playoff_results first
    playoff_data = season_data.get('playoff_results', {})
    if playoff_data and isinstance(playoff_data, dict):
        # ESPN playoff bracket structure varies, try common fields
        # This would need to be adjusted based on actual ESPN bracket structure
        pass
    
    # Fall back to extracting from playoff matchups
    matchups = season_data.get('matchups', [])
    
    # Determine regular season length based on NFL expansion in 2021
    # Pre-2021: 13 week regular season, playoffs start week 14
    # 2021+: 14 week regular season, playoffs start week 15
    if season >= 2021:
        regular_season_weeks = 14
    else:
        regular_season_weeks = 13
    
    # Get playoff matchups - use the is_playoff flag from scraper
    playoff_matchups = [m for m in matchups if m.get('is_playoff', False)]
    
    # If no matchups marked as playoff, identify by week number
    if not playoff_matchups:
        # Playoffs start after regular season weeks
        playoff_matchups = [m for m in matchups if m.get('week', 0) > regular_season_weeks]
    
    # If still no matchups, try to identify by matchup count (fallback)
    if not playoff_matchups:
        all_weeks = [m.get('week', 0) for m in matchups if m.get('week')]
        if all_weeks:
            max_week = max(all_weeks)
            
            # Count matchups per week to find playoff weeks
            week_counts = {}
            for m in matchups:
                week = m.get('week', 0)
                week_counts[week] = week_counts.get(week, 0) + 1
            
            # Regular season typically has 5 matchups per week (10 teams = 5 games)
            # Playoffs have fewer (2-4 games depending on round)
            # Weeks with 4 or fewer matchups are likely playoffs
            playoff_weeks = [w for w, count in week_counts.items() 
                           if count <= 4 and w > regular_season_weeks]
            
            if playoff_weeks:
                playoff_matchups = [m for m in matchups if m.get('week', 0) in playoff_weeks]
    
    if not playoff_matchups:
        return results
    
    # Find championship game by tracing the bracket
    if playoff_matchups:
        # First, deduplicate matchups by team pair and week
        # ESPN API sometimes returns duplicate matchups
        seen_matchups = {}
        unique_matchups = []
        for matchup in playoff_matchups:
            week = matchup.get('week', 0)
            home = matchup.get('home_manager')
            away = matchup.get('away_manager')
            # Create a unique key for this matchup
            key = (week, tuple(sorted([home, away])))
            
            if key not in seen_matchups:
                seen_matchups[key] = matchup
                unique_matchups.append(matchup)
            else:
                # If duplicate, keep the one with higher scores (more likely to be the real game)
                existing = seen_matchups[key]
                existing_total = existing.get('home_score', 0) + existing.get('away_score', 0)
                new_total = matchup.get('home_score', 0) + matchup.get('away_score', 0)
                if new_total > existing_total:
                    # Replace with the higher scoring version
                    idx = unique_matchups.index(existing)
                    unique_matchups[idx] = matchup
                    seen_matchups[key] = matchup
        
        # Group by week
        by_week = {}
        for matchup in unique_matchups:
            week = matchup.get('week', 0)
            if week not in by_week:
                by_week[week] = []
            by_week[week].append(matchup)
        
        if not by_week:
            return results
        
        # Filter out weeks with too many games (likely still has issues)
        # Normal playoff weeks should have 2-4 games max
        valid_weeks = {}
        for week, games in by_week.items():
            if len(games) <= 10:  # Reasonable threshold
                valid_weeks[week] = games
        
        if not valid_weeks:
            # Fallback to all weeks if filtering removed everything
            valid_weeks = by_week
        
        # Find the final week (championship week)
        champ_week = max(valid_weeks.keys())
        champ_week_games = valid_weeks[champ_week]
        
        # Deduplicate championship week games (keep highest scoring version of each matchup)
        champ_week_deduped = {}
        for game in champ_week_games:
            home = game.get('home_manager')
            away = game.get('away_manager')
            key = tuple(sorted([home, away]))
            total_score = game.get('home_score', 0) + game.get('away_score', 0)
            
            if key not in champ_week_deduped:
                champ_week_deduped[key] = game
            else:
                # Keep the one with higher total score
                existing_total = champ_week_deduped[key].get('home_score', 0) + champ_week_deduped[key].get('away_score', 0)
                if total_score > existing_total:
                    champ_week_deduped[key] = game
        
        champ_week_games = list(champ_week_deduped.values())
        
        # Debug: If we still have too many games after deduplication, something is wrong
        # For a 10-team league, championship week should have 1-2 games max
        if len(champ_week_games) > 5:
            # Too many games even after deduplication - might be different playoff structure
            # Try to filter by looking for games with reasonable scores (not 0-0 ties)
            champ_week_games = [g for g in champ_week_games 
                              if (g.get('home_score', 0) + g.get('away_score', 0)) > 50]
        
        # Try to identify semifinal winners from the previous week
        semifinal_winners = set()
        semifinal_losers = set()
        if champ_week > min(valid_weeks.keys()):
            # Look at the week before championship (should be semifinals)
            prev_week = champ_week - 1
            if prev_week in valid_weeks:
                prev_week_games = valid_weeks[prev_week]
                # Deduplicate previous week games too
                prev_week_deduped = {}
                for game in prev_week_games:
                    home = game.get('home_manager')
                    away = game.get('away_manager')
                    key = tuple(sorted([home, away]))
                    total_score = game.get('home_score', 0) + game.get('away_score', 0)
                    
                    if key not in prev_week_deduped:
                        prev_week_deduped[key] = game
                    else:
                        existing_total = prev_week_deduped[key].get('home_score', 0) + prev_week_deduped[key].get('away_score', 0)
                        if total_score > existing_total:
                            prev_week_deduped[key] = game
                
                # Filter previous week games too if too many
                prev_week_games_list = list(prev_week_deduped.values())
                if len(prev_week_games_list) > 5:
                    # Filter by reasonable scores
                    prev_week_games_list = [g for g in prev_week_games_list 
                                          if (g.get('home_score', 0) + g.get('away_score', 0)) > 50]
                
                # Find winners and losers of semifinal games
                # Semifinals should have 2 games (for 4-team playoff) or more
                for game in prev_week_games_list:
                    home_score = game.get('home_score', 0)
                    away_score = game.get('away_score', 0)
                    if home_score > away_score:
                        semifinal_winners.add(game.get('home_manager'))
                        semifinal_losers.add(game.get('away_manager'))
                    elif away_score > home_score:
                        semifinal_winners.add(game.get('away_manager'))
                        semifinal_losers.add(game.get('home_manager'))
        
        # If only 1 game in championship week, that's the championship
        if len(champ_week_games) == 1:
            champ_game = champ_week_games[0]
        elif len(champ_week_games) == 2:
            # Two games: championship and third place
            # If we found semifinal winners, use them to identify championship game
            if len(semifinal_winners) == 2:
                # Championship game should be between the two semifinal winners
                for game in champ_week_games:
                    home_mgr = game.get('home_manager')
                    away_mgr = game.get('away_manager')
                    if home_mgr in semifinal_winners and away_mgr in semifinal_winners:
                        champ_game = game
                        # The other game is third place
                        third_game = [g for g in champ_week_games if g != champ_game][0]
                        break
                else:
                    # Fallback: use highest combined score
                    champ_game = max(champ_week_games, key=lambda x: x.get('home_score', 0) + x.get('away_score', 0))
                    third_game = min(champ_week_games, key=lambda x: x.get('home_score', 0) + x.get('away_score', 0))
            else:
                # Fallback: championship is the one with higher combined score
                champ_game = max(champ_week_games, key=lambda x: x.get('home_score', 0) + x.get('away_score', 0))
                third_game = min(champ_week_games, key=lambda x: x.get('home_score', 0) + x.get('away_score', 0))
            
            # Set third place if we identified it
            if 'third_game' in locals():
                if third_game.get('home_score', 0) > third_game.get('away_score', 0):
                    results['thirdPlace'] = third_game.get('home_manager')
                else:
                    results['thirdPlace'] = third_game.get('away_manager')
        else:
            # Multiple games - try to find championship using semifinal winners
            if len(semifinal_winners) == 2:
                for game in champ_week_games:
                    home_mgr = game.get('home_manager')
                    away_mgr = game.get('away_manager')
                    if home_mgr in semifinal_winners and away_mgr in semifinal_winners:
                        champ_game = game
                        break
                else:
                    champ_game = max(champ_week_games, key=lambda x: x.get('home_score', 0) + x.get('away_score', 0))
            else:
                # Fallback: find the one with highest combined score
                champ_game = max(champ_week_games, key=lambda x: x.get('home_score', 0) + x.get('away_score', 0))
        
        # Set champion and runner-up
        if champ_game.get('home_score', 0) > champ_game.get('away_score', 0):
            results['champion'] = champ_game.get('home_manager')
            results['runnerUp'] = champ_game.get('away_manager')
        elif champ_game.get('away_score', 0) > champ_game.get('home_score', 0):
            results['champion'] = champ_game.get('away_manager')
            results['runnerUp'] = champ_game.get('home_manager')
        
        # If we didn't find third place yet, look for it in the final week
        if not results['thirdPlace'] and len(champ_week_games) >= 2:
            # First try to use semifinal losers to identify third place game
            if len(semifinal_losers) == 2:
                for game in champ_week_games:
                    if game == champ_game:
                        continue
                    home_mgr = game.get('home_manager')
                    away_mgr = game.get('away_manager')
                    # Third place game should be between the two semifinal losers
                    if home_mgr in semifinal_losers and away_mgr in semifinal_losers:
                        if game.get('home_score', 0) > game.get('away_score', 0):
                            results['thirdPlace'] = home_mgr
                        else:
                            results['thirdPlace'] = away_mgr
                        break
            
            # Fallback: look for any game with different teams than championship
            if not results['thirdPlace']:
                for game in champ_week_games:
                    if game == champ_game:
                        continue
                    home_mgr = game.get('home_manager')
                    away_mgr = game.get('away_manager')
                    # Make sure it's not the same teams as championship
                    if (home_mgr != results['champion'] and home_mgr != results['runnerUp'] and
                        away_mgr != results['champion'] and away_mgr != results['runnerUp']):
                        # This is likely the third place game
                        if game.get('home_score', 0) > game.get('away_score', 0):
                            results['thirdPlace'] = home_mgr
                        else:
                            results['thirdPlace'] = away_mgr
                        break
    
    return results


def extract_playoff_results_debug(espn_data: Dict, season: int) -> Tuple[Dict, Dict]:
    """Extract playoff results with debug info"""
    results, debug_info = extract_playoff_results(espn_data, season), {}
    season_data = espn_data.get(season, {})
    matchups = season_data.get('matchups', [])
    
    # Debug: show playoff weeks found
    playoff_matchups = [m for m in matchups if m.get('is_playoff', False)]
    all_weeks = sorted(set(m.get('week', 0) for m in matchups))
    
    if not playoff_matchups:
        # Try to identify by week
        max_week = max(all_weeks) if all_weeks else 0
        week14_count = len([m for m in matchups if m.get('week') == 14])
        week13_count = len([m for m in matchups if m.get('week') == 13])
        
        if max_week >= 14:
            if week14_count < week13_count * 0.8:
                regular_season_weeks = 13
            else:
                regular_season_weeks = 14 if max_week >= 15 else 13
        else:
            regular_season_weeks = max_week
        
        playoff_matchups = [m for m in matchups if m.get('week', 0) > regular_season_weeks]
    
    debug_info = {
        'all_weeks': all_weeks,
        'playoff_weeks': sorted(set(m.get('week') for m in playoff_matchups)),
        'playoff_matchup_count': len(playoff_matchups),
        'regular_season_weeks_estimated': regular_season_weeks if 'regular_season_weeks' in locals() else None,
    }
    
    return results, debug_info


def compare_season(season: int, champs_data: Dict, espn_data: Dict, manager_mapping: Dict[str, str]) -> Dict:
    """Compare championship data for a single season"""
    champs = champs_data.get(season, {})
    espn_results = extract_playoff_results(espn_data, season)
    
    # Get debug info - use the same logic as extract_playoff_results
    debug_info = {}
    season_data = espn_data.get(season, {})
    matchups = season_data.get('matchups', [])
    all_weeks = sorted(set(m.get('week', 0) for m in matchups if m.get('week')))
    
    # Count matchups marked as playoff
    playoff_marked = [m for m in matchups if m.get('is_playoff', False)]
    
    # If no marked, try to identify playoff weeks by matchup count
    playoff_weeks_found = []
    if not playoff_marked:
        week_counts = {}
        for m in matchups:
            week = m.get('week', 0)
            week_counts[week] = week_counts.get(week, 0) + 1
        
        # Find weeks with 4 or fewer matchups (playoff rounds)
        playoff_weeks_found = [w for w, count in week_counts.items() 
                              if count <= 4 and w > 10]
    
    debug_info = {
        'all_weeks': all_weeks,
        'playoff_marked_count': len(playoff_marked),
        'playoff_weeks_marked': sorted(set(m.get('week') for m in playoff_marked)) if playoff_marked else [],
        'playoff_weeks_detected': playoff_weeks_found,
    }
    
    if not champs and not espn_results:
        return {'status': 'no_data'}
    
    discrepancies = []
    matches = []
    
    # Compare each field
    fields = ['champion', 'runnerUp', 'thirdPlace', 'regularSeasonChamp', 'regularSeasonMostPoints']
    
    for field in fields:
        champs_value = champs.get(field)
        espn_value = espn_results.get(field)
        
        if espn_value:
            # Map ESPN name to first name
            espn_first_name = manager_mapping.get(espn_value, extract_first_name(espn_value))
        else:
            espn_first_name = None
        
        if champs_value and espn_first_name:
            # Normalize for comparison (case insensitive)
            if champs_value.lower() == espn_first_name.lower():
                matches.append(f"{field}: {champs_value}")
            else:
                discrepancies.append({
                    'field': field,
                    'champions_js': champs_value,
                    'espn': espn_value,
                    'espn_mapped': espn_first_name
                })
        elif champs_value and not espn_first_name:
            discrepancies.append({
                'field': field,
                'champions_js': champs_value,
                'espn': None,
                'espn_mapped': None,
                'note': 'Missing in ESPN data'
            })
        elif not champs_value and espn_first_name:
            discrepancies.append({
                'field': field,
                'champions_js': None,
                'espn': espn_value,
                'espn_mapped': espn_first_name,
                'note': 'Missing in champions.js'
            })
    
    return {
        'season': season,
        'matches': matches,
        'discrepancies': discrepancies,
        'has_data': bool(champs or espn_results),
        'debug_info': debug_info,
        'espn_results_raw': espn_results
    }


def main():
    """Main comparison function"""
    print("=" * 70)
    print("Championship Data Comparison")
    print("Comparing champions.js with ESPN scraped data")
    print("=" * 70)
    
    # Load data
    print("\nLoading data...")
    champs_data = parse_champions_js()
    espn_data = load_espn_data()
    
    print(f"  Loaded {len(champs_data)} seasons from champions.js")
    print(f"  Loaded {len(espn_data)} seasons from ESPN data")
    
    # Build manager mapping
    print("\nBuilding manager name mapping...")
    manager_mapping = build_manager_mapping(espn_data)
    print(f"  Mapped {len(manager_mapping)} manager names")
    
    # Compare seasons (2009-2025, ESPN era)
    print("\n" + "=" * 70)
    print("Comparison Results (ESPN Era: 2009-2025)")
    print("=" * 70)
    
    espn_seasons = sorted([s for s in espn_data.keys() if s >= 2009])
    all_matches = []
    all_discrepancies = []
    
    for season in espn_seasons:
        comparison = compare_season(season, champs_data, espn_data, manager_mapping)
        
        if not comparison.get('has_data'):
            continue
        
        if comparison['discrepancies']:
            all_discrepancies.append(comparison)
            print(f"\n⚠ Season {season} - DISCREPANCIES:")
            
            # Show debug info for playoff extraction
            if comparison.get('debug_info'):
                debug = comparison['debug_info']
                if debug.get('playoff_weeks_marked'):
                    print(f"  Playoff weeks (marked): {debug['playoff_weeks_marked']}")
                elif debug.get('playoff_weeks_detected'):
                    print(f"  Playoff weeks (detected by count): {debug['playoff_weeks_detected']}")
                if debug.get('playoff_marked_count', 0) > 0:
                    print(f"  Playoff matchups found: {debug['playoff_marked_count']}")
            
            for disc in comparison['discrepancies']:
                print(f"  {disc['field']}:")
                print(f"    champions.js: {disc['champions_js']}")
                print(f"    ESPN: {disc['espn']} -> {disc['espn_mapped']}")
                if 'note' in disc:
                    print(f"    Note: {disc['note']}")
        else:
            all_matches.append(comparison)
            print(f"✓ Season {season}: All fields match")
            if comparison['matches']:
                print(f"  Matched: {', '.join(comparison['matches'][:3])}")
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"  Seasons compared: {len(espn_seasons)}")
    print(f"  ✓ Perfect matches: {len(all_matches)}")
    print(f"  ⚠ With discrepancies: {len(all_discrepancies)}")
    
    # Show manager mapping for reference
    print("\n" + "=" * 70)
    print("Manager Name Mapping (ESPN -> First Name)")
    print("=" * 70)
    for espn_name, first_name in sorted(manager_mapping.items()):
        print(f"  {espn_name:20} -> {first_name}")
    
    print("\n" + "=" * 70)
    print("Note: Manager name mapping may need manual adjustment")
    print("If discrepancies are due to name mismatches, update MANAGER_MAPPING in the script")
    print("=" * 70)


if __name__ == "__main__":
    main()
