"""Test 2023 extraction in detail"""
import json
from pathlib import Path
from compare_championships import extract_playoff_results, extract_first_name

data_file = Path(__file__).parent / "data" / "espn_season_2023.json"
with open(data_file, 'r') as f:
    data = json.load(f)

espn_data = {2023: data}
results = extract_playoff_results(espn_data, 2023)

print("="*70)
print("2023 Extraction Results")
print("="*70)
print(f"Champion: {results.get('champion')} -> {extract_first_name(results.get('champion', '')) if results.get('champion') else 'None'}")
print(f"Runner-up: {results.get('runnerUp')} -> {extract_first_name(results.get('runnerUp', '')) if results.get('runnerUp') else 'None'}")
print(f"Third: {results.get('thirdPlace')} -> {extract_first_name(results.get('thirdPlace', '')) if results.get('thirdPlace') else 'None'}")

print("\n" + "="*70)
print("Expected")
print("="*70)
print("Champion: Tyler (TyBear612)")
print("Runner-up: Ted (UGAdogs34)")
print("Third: Matt (mendy1399)")

# Now let's manually check week 16 and 17
matchups = data.get('matchups', [])
week16 = [m for m in matchups if m.get('week') == 16 and m.get('is_playoff')]
week17 = [m for m in matchups if m.get('week') == 17 and m.get('is_playoff')]

print("\n" + "="*70)
print("Week 16 Analysis (Semifinals)")
print("="*70)

# Deduplicate week 16
week16_deduped = {}
for m in week16:
    key = tuple(sorted([m.get('home_manager'), m.get('away_manager')]))
    total = m.get('home_score', 0) + m.get('away_score', 0)
    if key not in week16_deduped or total > (week16_deduped[key].get('home_score', 0) + week16_deduped[key].get('away_score', 0)):
        week16_deduped[key] = m

print(f"Total games: {len(week16)}, Unique matchups: {len(week16_deduped)}")
print("\nUnique games:")
for key, game in week16_deduped.items():
    home = game.get('home_manager')
    away = game.get('away_manager')
    home_score = game.get('home_score', 0)
    away_score = game.get('away_score', 0)
    winner = game.get('winner_manager')
    print(f"  {home} ({home_score}) vs {away} ({away_score}) -> Winner: {winner}")

# Find semifinal winners
semifinal_winners = set()
semifinal_losers = set()
for game in week16_deduped.values():
    home_score = game.get('home_score', 0)
    away_score = game.get('away_score', 0)
    if home_score > away_score:
        semifinal_winners.add(game.get('home_manager'))
        semifinal_losers.add(game.get('away_manager'))
    elif away_score > home_score:
        semifinal_winners.add(game.get('away_manager'))
        semifinal_losers.add(game.get('home_manager'))

print(f"\nSemifinal winners: {semifinal_winners}")
print(f"Semifinal losers: {semifinal_losers}")

print("\n" + "="*70)
print("Week 17 Analysis (Championship + Third Place)")
print("="*70)

# Deduplicate week 17
week17_deduped = {}
for m in week17:
    key = tuple(sorted([m.get('home_manager'), m.get('away_manager')]))
    total = m.get('home_score', 0) + m.get('away_score', 0)
    if key not in week17_deduped or total > (week17_deduped[key].get('home_score', 0) + week17_deduped[key].get('away_score', 0)):
        week17_deduped[key] = m

print(f"Total games: {len(week17)}, Unique matchups: {len(week17_deduped)}")
print("\nUnique games:")
for key, game in week17_deduped.items():
    home = game.get('home_manager')
    away = game.get('away_manager')
    home_score = game.get('home_score', 0)
    away_score = game.get('away_score', 0)
    winner = game.get('winner_manager')
    print(f"  {home} ({home_score}) vs {away} ({away_score}) -> Winner: {winner}")

# Find championship game (between semifinal winners)
champ_game = None
third_game = None
for game in week17_deduped.values():
    home = game.get('home_manager')
    away = game.get('away_manager')
    if home in semifinal_winners and away in semifinal_winners:
        champ_game = game
    elif home in semifinal_losers and away in semifinal_losers:
        third_game = game

print(f"\nChampionship game (between semifinal winners):")
if champ_game:
    home = champ_game.get('home_manager')
    away = champ_game.get('away_manager')
    home_score = champ_game.get('home_score', 0)
    away_score = champ_game.get('away_score', 0)
    winner = champ_game.get('winner_manager')
    print(f"  {home} ({home_score}) vs {away} ({away_score}) -> Winner: {winner}")
    print(f"  Expected: TyBear612 vs UGAdogs34, Winner: TyBear612")
else:
    print("  NOT FOUND!")

print(f"\nThird place game (between semifinal losers):")
if third_game:
    home = third_game.get('home_manager')
    away = third_game.get('away_manager')
    home_score = third_game.get('home_score', 0)
    away_score = third_game.get('away_score', 0)
    winner = third_game.get('winner_manager')
    print(f"  {home} ({home_score}) vs {away} ({away_score}) -> Winner: {winner}")
    print(f"  Expected: Should involve mendy1399")
else:
    print("  NOT FOUND!")
