"""
Inspect raw ESPN API response to identify fields that distinguish scheduled vs projected games
This script will make a direct API call to see the full structure
"""
import json
import requests
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def inspect_raw_api_response():
    """Make a direct API call to inspect the raw structure"""
    # Load cookies from environment variable or file (same as scraper)
    import os
    cookies_str = os.environ.get('ESPN_COOKIES')
    
    # Fallback to cookies.txt file (same as scraper)
    if not cookies_str:
        cookies_file = SCRIPT_DIR / "cookies.txt"
        if cookies_file.exists():
            with open(cookies_file, 'r') as f:
                cookies_str = f.read().strip()
    
    if not cookies_str:
        print("Error: No cookies found.")
        print("Please either:")
        print("  1. Set ESPN_COOKIES environment variable, or")
        print("  2. Create a cookies.txt file in the scripts directory")
        print("You can get cookies from your browser's developer tools when logged into ESPN.")
        return
    
    # League ID and season
    LEAGUE_ID = 420782
    season = 2025
    week = 1
    
    # Construct URL
    url = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{season}/segments/0/leagues/{LEAGUE_ID}?view=mMatchup&view=mMatchupScore&scoringPeriodId={week}"
    
    print("="*70)
    print("Inspecting Raw ESPN API Response")
    print("="*70)
    print(f"\nURL: {url}")
    print(f"Season: {season}, Week: {week}")
    
    try:
        # Use cookie string directly in headers (same as scraper)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://fantasy.espn.com/',
            'Origin': 'https://fantasy.espn.com',
            'Cookie': cookies_str
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Navigate to schedule/matchups
        schedule = data.get('schedule', [])
        if not schedule:
            # Try alternative structure
            schedule_obj = data.get('schedule', {})
            if isinstance(schedule_obj, dict):
                matchups_by_period = schedule_obj.get('matchupsByMatchupPeriod', {})
                if matchups_by_period:
                    schedule = matchups_by_period.get(str(week), [])
        
        if not schedule:
            print("\n❌ No schedule data found in response")
            print("\nAvailable top-level keys:", list(data.keys())[:20])
            return
        
        print(f"\n✓ Found {len(schedule)} matchups in schedule")
        
        # Inspect first few matchups
        print("\n" + "="*70)
        print("Sample Matchup Structure (First 3 Matchups)")
        print("="*70)
        
        for i, matchup in enumerate(schedule[:3]):
            print(f"\n--- Matchup {i+1} ---")
            print(json.dumps(matchup, indent=2))
            
            # Highlight key fields
            print(f"\nKey Fields:")
            print(f"  - id: {matchup.get('id')}")
            print(f"  - matchupPeriodId: {matchup.get('matchupPeriodId')}")
            print(f"  - matchupType: {matchup.get('matchupType')}")
            print(f"  - playoffTierType: {matchup.get('playoffTierType')}")
            print(f"  - isBye: {matchup.get('isBye')}")
            print(f"  - winner: {matchup.get('winner')}")
            print(f"  - home.teamId: {matchup.get('home', {}).get('teamId')}")
            print(f"  - away.teamId: {matchup.get('away', {}).get('teamId')}")
            print(f"  - home.totalPoints: {matchup.get('home', {}).get('totalPoints')}")
            print(f"  - away.totalPoints: {matchup.get('away', {}).get('totalPoints')}")
        
        # Analyze all matchups for patterns
        print("\n" + "="*70)
        print("Analysis: Identifying Scheduled vs Projected Games")
        print("="*70)
        
        matchup_types = {}
        for matchup in schedule:
            mtype = matchup.get('matchupType')
            if mtype not in matchup_types:
                matchup_types[mtype] = []
            matchup_types[mtype].append(matchup)
        
        print(f"\nMatchup Types Found: {list(matchup_types.keys())}")
        for mtype, matchups in matchup_types.items():
            print(f"\n  {mtype}: {len(matchups)} matchups")
            if matchups:
                sample = matchups[0]
                home_id = sample.get('home', {}).get('teamId')
                away_id = sample.get('away', {}).get('teamId')
                home_score = sample.get('home', {}).get('totalPoints', 0)
                away_score = sample.get('away', {}).get('totalPoints', 0)
                winner = sample.get('winner')
                print(f"    Sample: Team {home_id} ({home_score}) vs Team {away_id} ({away_score}), winner: {winner}")
        
        # Compare actual scheduled games vs projected games using 2025 schedule
        print("\n" + "="*70)
        print("Comparing Actual Scheduled Games vs Projected Games")
        print("="*70)
        
        from validate_with_2025_schedule import get_2025_actual_schedule
        actual_schedule = get_2025_actual_schedule()
        week_1_actual = {tuple(sorted(pair)) for pair in actual_schedule.get(1, [])}
        
        actual_games = []
        projected_games = []
        
        for matchup in schedule:
            home_id = matchup.get('home', {}).get('teamId')
            away_id = matchup.get('away', {}).get('teamId')
            if home_id and away_id:
                pair = tuple(sorted([home_id, away_id]))
                if pair in week_1_actual:
                    actual_games.append(matchup)
                else:
                    projected_games.append(matchup)
        
        print(f"\nActual scheduled games: {len(actual_games)}")
        print(f"Projected/duplicate games: {len(projected_games)}")
        
        if actual_games and projected_games:
            print("\nComparing fields between actual and projected games:")
            actual_sample = actual_games[0]
            projected_sample = projected_games[0]
            
            all_fields = set(actual_sample.keys()) | set(projected_sample.keys())
            
            print("\nFields that differ between actual and projected:")
            for field in sorted(all_fields):
                actual_val = actual_sample.get(field)
                projected_val = projected_sample.get(field)
                if actual_val != projected_val:
                    print(f"  {field}:")
                    print(f"    Actual: {actual_val}")
                    print(f"    Projected: {projected_val}")
            
            # Check for numeric patterns
            print("\nNumeric field patterns:")
            numeric_fields = ['id', 'matchupPeriodId', 'playoffTierType']
            for field in numeric_fields:
                if field in actual_sample or field in projected_sample:
                    actual_vals = [m.get(field) for m in actual_games[:5]]
                    projected_vals = [m.get(field) for m in projected_games[:10]]
                    print(f"  {field}:")
                    print(f"    Actual range: {min(actual_vals)} - {max(actual_vals)}" if actual_vals else "    Actual: None")
                    print(f"    Projected range: {min(projected_vals)} - {max(projected_vals)}" if projected_vals else "    Projected: None")
        
        # Compare actual scheduled games vs projected games using 2025 schedule
        print("\n" + "="*70)
        print("Comparing Actual Scheduled Games vs Projected Games")
        print("="*70)
        
        # Get 2025 actual schedule
        def get_2025_actual_schedule():
            return {
                1: [(1, 8), (10, 6), (7, 9), (4, 2), (5, 11)],
            }
        
        actual_schedule = get_2025_actual_schedule()
        week_1_actual = {tuple(sorted(pair)) for pair in actual_schedule.get(1, [])}
        
        actual_games = []
        projected_games = []
        
        for matchup in schedule:
            home_id = matchup.get('home', {}).get('teamId')
            away_id = matchup.get('away', {}).get('teamId')
            if home_id and away_id:
                pair = tuple(sorted([home_id, away_id]))
                if pair in week_1_actual:
                    actual_games.append(matchup)
                else:
                    projected_games.append(matchup)
        
        print(f"\nActual scheduled games: {len(actual_games)}")
        print(f"Projected/duplicate games: {len(projected_games)}")
        
        if actual_games and projected_games:
            print("\nComparing fields between actual and projected games:")
            actual_sample = actual_games[0]
            projected_sample = projected_games[0]
            
            all_fields = set(actual_sample.keys()) | set(projected_sample.keys())
            
            print("\nFields that differ between actual and projected:")
            differing_fields = []
            for field in sorted(all_fields):
                actual_val = actual_sample.get(field)
                projected_val = projected_sample.get(field)
                if actual_val != projected_val:
                    differing_fields.append(field)
                    print(f"  {field}:")
                    print(f"    Actual: {actual_val}")
                    print(f"    Projected: {projected_val}")
            
            if not differing_fields:
                print("  (No obvious differences in top-level fields)")
            
            # Check for patterns across all actual vs projected games
            print("\nPattern analysis across all games:")
            
            # Check matchupPeriodId
            actual_periods = [m.get('matchupPeriodId') for m in actual_games]
            projected_periods = [m.get('matchupPeriodId') for m in projected_games[:20]]
            if actual_periods and projected_periods:
                print(f"  matchupPeriodId:")
                print(f"    Actual: {set(actual_periods)}")
                print(f"    Projected (first 20): {set(projected_periods)}")
            
            # Check id field
            actual_ids = [m.get('id') for m in actual_games]
            projected_ids = [m.get('id') for m in projected_games[:20]]
            if actual_ids and projected_ids:
                print(f"  id:")
                print(f"    Actual range: {min(actual_ids)} - {max(actual_ids)}")
                print(f"    Projected range (first 20): {min(projected_ids)} - {max(projected_ids)}")
            
            # Check home/away team structure
            print(f"\n  home/away structure:")
            actual_home = actual_games[0].get('home', {})
            projected_home = projected_games[0].get('home', {})
            home_fields = set(actual_home.keys()) | set(projected_home.keys())
            print(f"    Home team fields: {sorted(home_fields)}")
            for field in sorted(home_fields):
                if actual_home.get(field) != projected_home.get(field):
                    print(f"      {field} differs: actual={actual_home.get(field)}, projected={projected_home.get(field)}")
        
        # Check for other distinguishing fields
        print("\n" + "="*70)
        print("All Fields in Matchup Objects")
        print("="*70)
        
        all_fields = set()
        for matchup in schedule[:10]:  # Check first 10
            all_fields.update(matchup.keys())
        
        print(f"\nAll top-level fields found:")
        for field in sorted(all_fields):
            print(f"  - {field}")
        
        # Save raw response for further analysis
        output_file = DATA_DIR / "raw_api_response_week1.json"
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n✓ Saved raw API response to {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_raw_api_response()
