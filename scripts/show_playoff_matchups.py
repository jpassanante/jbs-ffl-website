"""
Show playoff matchups for manual verification
Helps identify which games are championship, runner-up, third place
"""
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def extract_first_name(display_name: str) -> str:
    """Extract first name from ESPN display name"""
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
        'jayd3456': 'Jason',
        'tyfredstl': 'Ty',
    }
    return name_mappings.get(display_name.lower(), display_name)

def show_playoff_matchups(season: int):
    """Show playoff matchups for a specific season"""
    season_file = DATA_DIR / f"espn_season_{season}.json"
    if not season_file.exists():
        print(f"Season {season} data not found")
        return
    
    with open(season_file, 'r') as f:
        data = json.load(f)
    
    matchups = data.get('matchups', [])
    
    # Determine regular season length based on NFL expansion in 2021
    # Pre-2021: 13 week regular season, playoffs start week 14
    # 2021+: 14 week regular season, playoffs start week 15
    if season >= 2021:
        regular_season_weeks = 14
    else:
        regular_season_weeks = 13
    
    # Identify playoff weeks
    # First, try to use the is_playoff flag
    playoff_matchups = [m for m in matchups if m.get('is_playoff', False)]
    
    # If none marked, identify by week number (playoffs start after regular season)
    if not playoff_matchups:
        playoff_matchups = [m for m in matchups if m.get('week', 0) > regular_season_weeks]
    
    # If still no matchups, try to identify by matchup count (fallback)
    if not playoff_matchups:
        week_counts = defaultdict(int)
        for m in matchups:
            week = m.get('week', 0)
            week_counts[week] += 1
        
        # Find weeks with 4 or fewer matchups (playoff rounds)
        # Regular season typically has 5 matchups (10 teams = 5 games)
        playoff_weeks = [w for w, count in week_counts.items() 
                        if count <= 4 and w > regular_season_weeks]
        
        if playoff_weeks:
            playoff_matchups = [m for m in matchups if m.get('week', 0) in playoff_weeks]
    
    if not playoff_matchups:
        print(f"\n{'='*70}")
        print(f"Season {season}: No playoff matchups found")
        print(f"{'='*70}")
        return
    
    # Group by week
    by_week = defaultdict(list)
    for m in playoff_matchups:
        week = m.get('week', 0)
        by_week[week].append(m)
    
    print(f"\n{'='*70}")
    print(f"Season {season} - Playoff Matchups")
    print(f"{'='*70}")
    
    for week in sorted(by_week.keys()):
        games = by_week[week]
        print(f"\nWeek {week} ({len(games)} game{'s' if len(games) != 1 else ''}):")
        print("-" * 70)
        
        for i, game in enumerate(games, 1):
            home_mgr = game.get('home_manager', 'Unknown')
            away_mgr = game.get('away_manager', 'Unknown')
            home_score = game.get('home_score', 0)
            away_score = game.get('away_score', 0)
            
            home_first = extract_first_name(home_mgr)
            away_first = extract_first_name(away_mgr)
            
            winner = home_first if home_score > away_score else away_first if away_score > home_score else "Tie"
            
            print(f"  Game {i}: {home_first:10} ({home_score:6.2f}) vs {away_first:10} ({away_score:6.2f})")
            print(f"           Winner: {winner}")
            print(f"           [ESPN: {home_mgr} vs {away_mgr}]")
    
    # Try to identify championship game
    print(f"\n{'='*70}")
    print("Championship Analysis")
    print(f"{'='*70}")
    
    if by_week:
        final_week = max(by_week.keys())
        final_games = by_week[final_week]
        
        print(f"\nFinal Week: {final_week} ({len(final_games)} game{'s' if len(final_games) != 1 else ''})")
        
        if len(final_games) == 1:
            # Only one game = championship
            game = final_games[0]
            home_mgr = game.get('home_manager', 'Unknown')
            away_mgr = game.get('away_manager', 'Unknown')
            home_score = game.get('home_score', 0)
            away_score = game.get('away_score', 0)
            
            if home_score > away_score:
                champ = extract_first_name(home_mgr)
                runner_up = extract_first_name(away_mgr)
            else:
                champ = extract_first_name(away_mgr)
                runner_up = extract_first_name(home_mgr)
            
            print(f"  Champion: {champ}")
            print(f"  Runner-up: {runner_up}")
            print(f"  (No third place game found)")
            
        elif len(final_games) == 2:
            # Two games: likely championship and third place
            # Championship is typically the one with higher combined score
            game1 = final_games[0]
            game2 = final_games[1]
            
            total1 = game1.get('home_score', 0) + game1.get('away_score', 0)
            total2 = game2.get('home_score', 0) + game2.get('away_score', 0)
            
            if total1 >= total2:
                champ_game = game1
                third_game = game2
            else:
                champ_game = game2
                third_game = game1
            
            # Championship
            home_mgr = champ_game.get('home_manager', 'Unknown')
            away_mgr = champ_game.get('away_manager', 'Unknown')
            home_score = champ_game.get('home_score', 0)
            away_score = champ_game.get('away_score', 0)
            
            if home_score > away_score:
                champ = extract_first_name(home_mgr)
                runner_up = extract_first_name(away_mgr)
            else:
                champ = extract_first_name(away_mgr)
                runner_up = extract_first_name(home_mgr)
            
            # Third place
            home_mgr = third_game.get('home_manager', 'Unknown')
            away_mgr = third_game.get('away_manager', 'Unknown')
            home_score = third_game.get('home_score', 0)
            away_score = third_game.get('away_score', 0)
            
            if home_score > away_score:
                third = extract_first_name(home_mgr)
            else:
                third = extract_first_name(away_mgr)
            
            print(f"  Champion: {champ}")
            print(f"  Runner-up: {runner_up}")
            print(f"  Third Place: {third}")
            
        else:
            # Multiple games - show all
            print(f"  Multiple games in final week - need manual identification")
            for game in final_games:
                home_mgr = game.get('home_manager', 'Unknown')
                away_mgr = game.get('away_manager', 'Unknown')
                home_score = game.get('home_score', 0)
                away_score = game.get('away_score', 0)
                total = home_score + away_score
                
                home_first = extract_first_name(home_mgr)
                away_first = extract_first_name(away_mgr)
                
                print(f"    {home_first} vs {away_first}: {home_score:.2f} - {away_score:.2f} (Total: {total:.2f})")

def main():
    """Show playoff matchups for all seasons or a specific season"""
    import sys
    
    # Force output to be flushed
    import sys
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
    
    if len(sys.argv) > 1:
        # Show specific season
        try:
            season = int(sys.argv[1])
            show_playoff_matchups(season)
            sys.stdout.flush()
        except ValueError:
            print("Invalid season. Usage: python show_playoff_matchups.py [season]")
            sys.stdout.flush()
    else:
        # Show all seasons
        all_seasons_file = DATA_DIR / "espn_all_seasons.json"
        if not all_seasons_file.exists():
            print("No ESPN data found")
            sys.stdout.flush()
            return
        
        with open(all_seasons_file, 'r') as f:
            all_data = json.load(f)
        
        seasons = sorted([int(k) for k in all_data.keys() if int(k) >= 2009])
        
        for season in seasons:
            show_playoff_matchups(season)
            print("\n" + "="*70 + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
