"""
Validate head-to-head totals to check if numbers are reasonable
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR.parent / "data"

def validate_totals():
    """Check if head-to-head totals are reasonable"""
    h2h_file = OUTPUT_DIR / "headToHead.js"
    if not h2h_file.exists():
        print("Error: headToHead.js not found")
        return
    
    # Parse the JS file (simple parsing)
    with open(h2h_file, 'r') as f:
        content = f.read()
    
    # Extract records using regex
    import re
    records = []
    pattern = r'manager1:\s*"([^"]+)",\s*manager2:\s*"([^"]+)",\s*manager1Wins:\s*(\d+),\s*manager2Wins:\s*(\d+)'
    for match in re.finditer(pattern, content):
        mgr1, mgr2, wins1, wins2 = match.groups()
        records.append({
            'manager1': mgr1,
            'manager2': mgr2,
            'wins1': int(wins1),
            'wins2': int(wins2),
            'total': int(wins1) + int(wins2)
        })
    
    # Calculate totals per manager
    manager_totals = defaultdict(lambda: {'wins': 0, 'losses': 0, 'games': 0})
    
    for record in records:
        mgr1 = record['manager1']
        mgr2 = record['manager2']
        wins1 = record['wins1']
        wins2 = record['wins2']
        total = record['total']
        
        manager_totals[mgr1]['wins'] += wins1
        manager_totals[mgr1]['losses'] += wins2
        manager_totals[mgr1]['games'] += total
        
        manager_totals[mgr2]['wins'] += wins2
        manager_totals[mgr2]['losses'] += wins1
        manager_totals[mgr2]['games'] += total
    
    print("="*70)
    print("Head-to-Head Totals Validation")
    print("="*70)
    
    print("\nTotal games per manager:")
    for manager in sorted(manager_totals.keys()):
        stats = manager_totals[manager]
        total_games = stats['games']
        win_pct = (stats['wins'] / total_games * 100) if total_games > 0 else 0
        print(f"  {manager:10s}: {stats['wins']:3d}-{stats['losses']:3d} ({total_games:3d} games, {win_pct:5.1f}%)")
    
    # Expected: ~351-378 games per manager over 27 seasons
    # (13-14 weeks per season × 27 seasons)
    print("\n" + "="*70)
    print("Analysis:")
    print("="*70)
    
    avg_games = sum(s['games'] for s in manager_totals.values()) / len(manager_totals) if manager_totals else 0
    print(f"\nAverage games per manager: {avg_games:.1f}")
    print(f"Expected range: 351-378 games (13-14 weeks × 27 seasons)")
    
    if avg_games < 300:
        print(f"\n⚠ WARNING: Average is lower than expected")
        print(f"  Possible reasons:")
        print(f"    - Some managers didn't play all seasons")
        print(f"    - League had fewer teams in some seasons")
        print(f"    - matchup_period_id filter may be too strict")
    elif avg_games > 400:
        print(f"\n⚠ WARNING: Average is higher than expected")
        print(f"  Possible reasons:")
        print(f"    - Still counting some projected/duplicate games")
        print(f"    - League had more teams in some seasons")
    else:
        print(f"\n✓ Average is within reasonable range")
    
    # Check individual matchup ranges
    print("\n" + "="*70)
    print("Individual Matchup Analysis:")
    print("="*70)
    
    matchup_totals = [r['total'] for r in records]
    if matchup_totals:
        print(f"\nMatchup totals range: {min(matchup_totals)} - {max(matchup_totals)} games")
        print(f"Expected: 27-54 games per pair (1-2 times per season × 27 seasons)")
        
        too_high = [r for r in records if r['total'] > 54]
        too_low = [r for r in records if r['total'] < 10]
        
        if too_high:
            print(f"\n⚠ {len(too_high)} matchups have >54 games (may be inflated):")
            for r in too_high[:5]:
                print(f"  {r['manager1']} vs {r['manager2']}: {r['total']} games")
        
        if too_low:
            print(f"\nℹ {len(too_low)} matchups have <10 games (may be managers who joined/left):")
            for r in too_low[:5]:
                print(f"  {r['manager1']} vs {r['manager2']}: {r['total']} games")

if __name__ == "__main__":
    validate_totals()
