"""
Diagnostic script to understand why head-to-head numbers are so high
"""
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

def load_all_seasons():
    """Load all scraped season data"""
    all_seasons_file = DATA_DIR / "espn_all_seasons.json"
    if not all_seasons_file.exists():
        print(f"Error: {all_seasons_file} not found")
        return {}
    
    with open(all_seasons_file, 'r') as f:
        all_data = json.load(f)
    
    return {int(k): v for k, v in all_data.items()}

def diagnose_head_to_head():
    """Diagnose head-to-head calculation issues"""
    print("=" * 70)
    print("Diagnosing Head-to-Head Records")
    print("=" * 70)
    
    espn_data = load_all_seasons()
    
    # Track statistics
    total_matchups = 0
    matchups_by_season = defaultdict(int)
    unique_pairs = set()
    pair_counts = defaultdict(int)
    
    # Sample a specific pair to trace
    sample_pair = ("John", "Matt")
    sample_matchups = []
    
    for season, data in espn_data.items():
        matchups = data.get('matchups', [])
        matchups_by_season[season] = len(matchups)
        total_matchups += len(matchups)
        
        for matchup in matchups:
            home_mgr = matchup.get('home_manager', '')
            away_mgr = matchup.get('away_manager', '')
            home_id = matchup.get('home_team_id')
            away_id = matchup.get('away_team_id')
            
            # Skip invalid matchups
            if home_id is None or away_id is None:
                continue
            if not home_mgr or not away_mgr:
                continue
            if 'Team None' in home_mgr or 'Team None' in away_mgr:
                continue
            
            # Simple name extraction (just use first part before any processing)
            home_first = home_mgr.split()[0] if ' ' in home_mgr else home_mgr
            away_first = away_mgr.split()[0] if ' ' in away_mgr else away_mgr
            
            # Try to match common names
            name_map = {
                'benhkline': 'Ben', 'Ben': 'Ben',
                'plazaroff': 'Peter', 'PLazaroff': 'Peter', 'Peter': 'Peter',
                'lannybenson13': 'Lanny', 'Lanny': 'Lanny',
                'jpassana': 'Joey', 'Joey': 'Joey',
                'tybear612': 'Tyler', 'TyBear612': 'Tyler', 'Tyler': 'Tyler',
                'vchapli1': 'Vernon', 'Vernon': 'Vernon',
                'johnnyhubes123': 'John', 'John': 'John',
                'mendy1399': 'Matt', 'Matt': 'Matt',
                'ugadogs34': 'Ted', 'UGAdogs34': 'Ted', 'Ted': 'Ted',
                'jayd3456': 'Jason', 'Jason': 'Jason',
                'tyfredstl': 'Ty', 'Ty': 'Ty',
            }
            
            home_first = name_map.get(home_first, home_first)
            away_first = name_map.get(away_first, away_first)
            
            if home_first == away_first:
                continue
            
            # Create sorted pair
            pair = tuple(sorted([home_first, away_first]))
            unique_pairs.add(pair)
            pair_counts[pair] += 1
            
            # Track sample pair
            if pair == sample_pair or pair == tuple(reversed(sample_pair)):
                sample_matchups.append({
                    'season': season,
                    'week': matchup.get('week', 0),
                    'home': home_first,
                    'away': away_first,
                    'home_score': matchup.get('home_score', 0),
                    'away_score': matchup.get('away_score', 0),
                })
    
    print(f"\nTotal matchups across all seasons: {total_matchups}")
    print(f"Unique manager pairs: {len(unique_pairs)}")
    
    print(f"\nMatchups by season:")
    for season in sorted(matchups_by_season.keys()):
        print(f"  {season}: {matchups_by_season[season]} matchups")
    
    print(f"\nMost common pairs (top 10):")
    sorted_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for (mgr1, mgr2), count in sorted_pairs:
        print(f"  {mgr1} vs {mgr2}: {count} matchups")
    
    print(f"\nSample: {sample_pair[0]} vs {sample_pair[1]}")
    print(f"  Total matchups found: {pair_counts.get(sample_pair, 0)}")
    print(f"  Sample matchups (first 10):")
    for i, m in enumerate(sample_matchups[:10], 1):
        print(f"    {i}. Season {m['season']}, Week {m['week']}: {m['home']} ({m['home_score']}) vs {m['away']} ({m['away_score']})")
    
    # Calculate expected vs actual
    print(f"\n\nExpected calculations:")
    print(f"  27 seasons × ~65 matchups/season (5 matchups/week × 13 weeks) = ~1,755 total matchups")
    print(f"  With 10 managers, each pair should play ~{1755 / 45:.1f} times on average")
    print(f"  (45 = number of unique pairs in 10-team league: 10×9/2)")
    
    print("\n" + "=" * 70)
    print("Diagnosis Complete")
    print("=" * 70)

if __name__ == "__main__":
    diagnose_head_to_head()
