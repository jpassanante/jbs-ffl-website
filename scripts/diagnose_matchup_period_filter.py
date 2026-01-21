"""
Diagnose how many games are being filtered out by matchup_period_id filter
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def diagnose_filter():
    """Check how matchup_period_id filter is working"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print("Error: espn_all_seasons.json not found")
        return
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    print("="*70)
    print("Diagnosing matchup_period_id Filter")
    print("="*70)
    
    total_matchups = 0
    total_with_period = 0
    total_matching_period = 0
    period_distribution = defaultdict(int)
    
    for season_str, data in all_data.items():
        matchups = data.get('matchups', [])
        
        for matchup in matchups:
            week = matchup.get('week', 0)
            if week == 0:
                continue
            
            total_matchups += 1
            matchup_period_id = matchup.get('matchup_period_id')
            
            if matchup_period_id is not None:
                total_with_period += 1
                period_distribution[matchup_period_id] += 1
                
                if matchup_period_id == week:
                    total_matching_period += 1
    
    print(f"\nTotal matchups processed: {total_matchups}")
    print(f"Matchups with matchup_period_id: {total_with_period} ({total_with_period/total_matchups*100:.1f}%)")
    print(f"Matchups where matchup_period_id == week: {total_matching_period} ({total_matching_period/total_matchups*100:.1f}%)")
    print(f"Matchups filtered out: {total_matchups - total_matching_period} ({(total_matchups - total_matching_period)/total_matchups*100:.1f}%)")
    
    print(f"\n" + "="*70)
    print("matchup_period_id Distribution:")
    print("="*70)
    
    # Show distribution for first few periods
    for period in sorted(period_distribution.keys())[:20]:
        print(f"  Period {period}: {period_distribution[period]} matchups")
    
    # Check if there's a pattern
    print(f"\n" + "="*70)
    print("Analysis:")
    print("="*70)
    
    if total_matching_period < total_matchups * 0.5:
        print(f"\n⚠ WARNING: Only {total_matching_period/total_matchups*100:.1f}% of matchups match period==week")
        print(f"  This suggests the filter may be too strict")
        print(f"  Recommendation: May need to use a different filtering strategy")
    else:
        print(f"\n✓ Filter is working: {total_matching_period/total_matchups*100:.1f}% of matchups match period==week")
    
    # Check a specific season/week to see the pattern
    print(f"\n" + "="*70)
    print("Sample: 2025 Week 1 Analysis")
    print("="*70)
    
    season_2025 = all_data.get('2025', {})
    week1_matchups = [m for m in season_2025.get('matchups', []) if m.get('week') == 1]
    
    print(f"\nTotal Week 1 matchups: {len(week1_matchups)}")
    
    period_counts = defaultdict(int)
    for m in week1_matchups:
        period = m.get('matchup_period_id')
        if period is not None:
            period_counts[period] += 1
    
    print(f"\nmatchup_period_id values for Week 1:")
    for period in sorted(period_counts.keys()):
        print(f"  Period {period}: {period_counts[period]} matchups")
    
    matching_week1 = [m for m in week1_matchups if m.get('matchup_period_id') == 1]
    print(f"\nMatchups with matchup_period_id == 1: {len(matching_week1)}")
    print(f"Expected: 5 (one per actual scheduled game)")

if __name__ == "__main__":
    diagnose_filter()
