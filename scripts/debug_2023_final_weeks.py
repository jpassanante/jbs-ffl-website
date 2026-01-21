"""Debug the final playoff weeks for 2023"""
import json
from pathlib import Path
from collections import defaultdict

data_file = Path(__file__).parent / "data" / "espn_season_2023.json"
with open(data_file, 'r') as f:
    data = json.load(f)

matchups = data.get('matchups', [])

# Get playoff weeks 16 and 17
week16 = [m for m in matchups if m.get('week') == 16 and m.get('is_playoff')]
week17 = [m for m in matchups if m.get('week') == 17 and m.get('is_playoff')]

print("="*70)
print("Week 16 (Semifinals?)")
print("="*70)
print(f"Total games: {len(week16)}")

# Group by unique matchup
matchup_pairs = defaultdict(list)
for m in week16:
    home = m.get('home_manager')
    away = m.get('away_manager')
    key = tuple(sorted([home, away]))
    matchup_pairs[key].append(m)

print(f"Unique matchups: {len(matchup_pairs)}")
for key, games in list(matchup_pairs.items())[:5]:
    print(f"  {key[0]} vs {key[1]}: {len(games)} game(s)")

# Show actual games
print("\nActual games in week 16:")
for i, m in enumerate(week16[:10], 1):
    print(f"  {i}. {m.get('home_manager')} ({m.get('home_score')}) vs {m.get('away_manager')} ({m.get('away_score')})")
    print(f"     Winner: {m.get('winner_manager')}")

print("\n" + "="*70)
print("Week 17 (Championship + Third Place?)")
print("="*70)
print(f"Total games: {len(week17)}")

# Group by unique matchup
matchup_pairs = defaultdict(list)
for m in week17:
    home = m.get('home_manager')
    away = m.get('away_manager')
    key = tuple(sorted([home, away]))
    matchup_pairs[key].append(m)

print(f"Unique matchups: {len(matchup_pairs)}")
for key, games in matchup_pairs.items():
    print(f"  {key[0]} vs {key[1]}: {len(games)} game(s)")

# Show actual games
print("\nActual games in week 17:")
for i, m in enumerate(week17, 1):
    print(f"  {i}. {m.get('home_manager')} ({m.get('home_score')}) vs {m.get('away_manager')} ({m.get('away_score')})")
    print(f"     Winner: {m.get('winner_manager')}")

# Expected: Tyler (TyBear612) vs Ted (UGAdogs34) in championship
# Expected: Matt (mendy1399) in third place game
print("\n" + "="*70)
print("Looking for expected teams:")
print("="*70)
print("Championship should be: TyBear612 vs UGAdogs34")
print("Third place should involve: mendy1399")

champ_candidates = [m for m in week17 if 'TyBear612' in [m.get('home_manager'), m.get('away_manager')] 
                    and 'UGAdogs34' in [m.get('home_manager'), m.get('away_manager')]]
third_candidates = [m for m in week17 if 'mendy1399' in [m.get('home_manager'), m.get('away_manager')]]

print(f"\nChampionship candidates (TyBear612 vs UGAdogs34): {len(champ_candidates)}")
for m in champ_candidates:
    print(f"  {m.get('home_manager')} ({m.get('home_score')}) vs {m.get('away_manager')} ({m.get('away_score')})")

print(f"\nThird place candidates (involving mendy1399): {len(third_candidates)}")
for m in third_candidates:
    print(f"  {m.get('home_manager')} ({m.get('home_score')}) vs {m.get('away_manager')} ({m.get('away_score')})")
