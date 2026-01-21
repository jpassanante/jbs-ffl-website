"""
Analyze the raw API response to find distinguishing fields
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def get_2025_actual_schedule():
    """Return the actual 2025 schedule for Week 1"""
    return {
        1: [(1, 8), (10, 6), (7, 9), (4, 2), (5, 11)],
    }

def analyze_raw_response():
    """Analyze the raw API response file"""
    raw_file = DATA_DIR / "raw_api_response_week1.json"
    if not raw_file.exists():
        print(f"Error: {raw_file} not found")
        print("Please run inspect_raw_api_structure.py first to generate it.")
        return
    
    print("="*70)
    print("Analyzing Raw ESPN API Response")
    print("="*70)
    
    print("\nLoading JSON file...")
    with open(raw_file, 'r') as f:
        data = json.load(f)
    
    # Get schedule
    schedule = data.get('schedule', [])
    if not schedule:
        schedule_obj = data.get('schedule', {})
        if isinstance(schedule_obj, dict):
            matchups_by_period = schedule_obj.get('matchupsByMatchupPeriod', {})
            if matchups_by_period:
                schedule = matchups_by_period.get('1', [])
    
    if not schedule:
        print("❌ No schedule found in response")
        return
    
    print(f"✓ Found {len(schedule)} matchups in schedule")
    
    # Get actual schedule
    actual_schedule = get_2025_actual_schedule()
    week_1_actual = {tuple(sorted(pair)) for pair in actual_schedule.get(1, [])}
    
    # Separate actual vs projected
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
    
    if not actual_games or not projected_games:
        print("❌ Need both actual and projected games to compare")
        return
    
    # Compare fields
    print("\n" + "="*70)
    print("Field Comparison: Actual vs Projected")
    print("="*70)
    
    actual_sample = actual_games[0]
    projected_sample = projected_games[0]
    
    all_fields = set(actual_sample.keys()) | set(projected_sample.keys())
    
    differing_fields = []
    for field in sorted(all_fields):
        actual_val = actual_sample.get(field)
        projected_val = projected_sample.get(field)
        if actual_val != projected_val:
            differing_fields.append(field)
            print(f"\n{field}:")
            print(f"  Actual: {actual_val}")
            print(f"  Projected: {projected_val}")
    
    if not differing_fields:
        print("\n(No obvious differences in top-level fields)")
    
    # Pattern analysis
    print("\n" + "="*70)
    print("Pattern Analysis")
    print("="*70)
    
    # matchupPeriodId - detailed analysis
    actual_periods = [m.get('matchupPeriodId') for m in actual_games]
    projected_periods = [m.get('matchupPeriodId') for m in projected_games[:20]]
    if actual_periods and projected_periods:
        print(f"\nmatchupPeriodId:")
        print(f"  Actual: {set(actual_periods)}")
        print(f"  Projected (first 20): {set(projected_periods)}")
        
        # Check if actual games for Week 1 have matchupPeriodId == 1
        actual_with_period_1 = [m for m in actual_games if m.get('matchupPeriodId') == 1]
        print(f"  Actual games with matchupPeriodId=1: {len(actual_with_period_1)}/{len(actual_games)}")
        
        # Check if we can filter by matchupPeriodId == week
        week = 1
        actual_matching_period = [m for m in actual_games if m.get('matchupPeriodId') == week]
        projected_matching_period = [m for m in projected_games if m.get('matchupPeriodId') == week]
        print(f"  Games with matchupPeriodId={week}:")
        print(f"    Actual: {len(actual_matching_period)}/{len(actual_games)}")
        print(f"    Projected: {len(projected_matching_period)}/{len(projected_games)}")
        
        if len(actual_matching_period) == len(actual_games) and len(projected_matching_period) == 0:
            print(f"  ✓✓✓ PERFECT! All actual games have matchupPeriodId={week}, no projected games do!")
            print(f"     Recommendation: Filter by matchupPeriodId == week")
        elif len(actual_matching_period) > 0 and len(projected_matching_period) < len(projected_games):
            print(f"  ✓ PARTIAL: Some actual games match, fewer projected games match")
            print(f"     May be useful as a filter")
    
    # id field
    actual_ids = [m.get('id') for m in actual_games]
    projected_ids = [m.get('id') for m in projected_games[:20]]
    if actual_ids and projected_ids:
        print(f"\nid:")
        print(f"  Actual range: {min(actual_ids)} - {max(actual_ids)}")
        print(f"  Projected range (first 20): {min(projected_ids)} - {max(projected_ids)}")
        if max(actual_ids) < min(projected_ids) or min(actual_ids) > max(projected_ids):
            print(f"  ✓ DISTINCT RANGES!")
    
    # Check all fields for patterns
    print("\n" + "="*70)
    print("Checking All Fields for Patterns")
    print("="*70)
    
    # Collect all values for each field
    field_patterns = {}
    for field in sorted(all_fields):
        actual_vals = [m.get(field) for m in actual_games]
        projected_vals = [m.get(field) for m in projected_games[:20]]
        
        # Filter out unhashable types (dict, list) for set operations
        actual_hashable = [v for v in actual_vals if isinstance(v, (int, float, str, bool, type(None)))]
        projected_hashable = [v for v in projected_vals if isinstance(v, (int, float, str, bool, type(None)))]
        
        if not actual_hashable or not projected_hashable:
            # Field contains complex types, skip set operations
            continue
        
        actual_set = set(actual_hashable)
        projected_set = set(projected_hashable)
        
        # Check if values are distinct
        if actual_set and projected_set and actual_set.isdisjoint(projected_set):
            field_patterns[field] = {
                'type': 'distinct_values',
                'actual': actual_set,
                'projected': projected_set
            }
            print(f"\n✓ {field}: DISTINCT VALUES")
            print(f"  Actual: {sorted(actual_set)}")
            print(f"  Projected (first 20): {sorted(list(projected_set))[:10]}")
        elif len(actual_set) == 1 and len(projected_set) == 1 and actual_set != projected_set:
            field_patterns[field] = {
                'type': 'single_distinct_value',
                'actual': list(actual_set)[0],
                'projected': list(projected_set)[0]
            }
            print(f"\n✓ {field}: SINGLE DISTINCT VALUE")
            print(f"  Actual: {list(actual_set)[0]}")
            print(f"  Projected: {list(projected_set)[0]}")
        
        # Also check for complex types (dict/list) - just report if they exist
        actual_complex = [v for v in actual_vals if isinstance(v, (dict, list))]
        projected_complex = [v for v in projected_vals if isinstance(v, (dict, list))]
        if actual_complex or projected_complex:
            print(f"\n  {field}: Contains complex types (dict/list) - {len(actual_complex)} actual, {len(projected_complex)} projected")
    
    # Check nested structures (home/away)
    print("\n" + "="*70)
    print("Checking Nested Structures (home/away)")
    print("="*70)
    
    actual_home = actual_games[0].get('home', {})
    projected_home = projected_games[0].get('home', {})
    home_fields = set(actual_home.keys()) | set(projected_home.keys())
    
    print(f"\nHome team fields: {sorted(home_fields)}")
    for field in sorted(home_fields):
        actual_val = actual_home.get(field)
        projected_val = projected_home.get(field)
        if actual_val != projected_val:
            print(f"  {field}:")
            print(f"    Actual: {actual_val}")
            print(f"    Projected: {projected_val}")
    
    # Summary
    print("\n" + "="*70)
    print("Summary & Recommendations")
    print("="*70)
    
    if field_patterns:
        print("\n✓ Found distinguishing fields:")
        for field, pattern in field_patterns.items():
            print(f"  - {field}: {pattern['type']}")
    else:
        print("\n⚠ No clear distinguishing fields found in top-level matchup fields")
        print("  May need to check nested structures or use a different approach")
    
    # List all available fields
    print("\n" + "="*70)
    print("All Available Fields in Matchup Objects")
    print("="*70)
    print(f"\n{', '.join(sorted(all_fields))}")

if __name__ == "__main__":
    analyze_raw_response()
