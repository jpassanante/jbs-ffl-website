"""Test if the 2023 fix works"""
import json
from pathlib import Path
from compare_championships import extract_playoff_results, extract_first_name

# Load 2023 data
data_file = Path(__file__).parent / "data" / "espn_season_2023.json"
with open(data_file, 'r') as f:
    data = json.load(f)

espn_data = {2023: data}

# Extract playoff results
results = extract_playoff_results(espn_data, 2023)

print("="*70)
print("2023 Playoff Results (Extracted)")
print("="*70)
print(f"Champion: {results.get('champion')} -> {extract_first_name(results.get('champion', '')) if results.get('champion') else 'None'}")
print(f"Runner-up: {results.get('runnerUp')} -> {extract_first_name(results.get('runnerUp', '')) if results.get('runnerUp') else 'None'}")
print(f"Third Place: {results.get('thirdPlace')} -> {extract_first_name(results.get('thirdPlace', '')) if results.get('thirdPlace') else 'None'}")
print(f"Regular Season Champ: {results.get('regularSeasonChamp')} -> {extract_first_name(results.get('regularSeasonChamp', '')) if results.get('regularSeasonChamp') else 'None'}")
print(f"Most Points: {results.get('regularSeasonMostPoints')} -> {extract_first_name(results.get('regularSeasonMostPoints', '')) if results.get('regularSeasonMostPoints') else 'None'}")

print("\n" + "="*70)
print("Expected (from champions.js)")
print("="*70)
print("Champion: Tyler (TyBear612)")
print("Runner-up: Ted (UGAdogs34)")
print("Third Place: Matt (mendy1399)")
print("Regular Season Champ: Tyler (TyBear612)")
print("Most Points: Joey (jpassana)")

# Check what weeks we're finding
matchups = data.get('matchups', [])
playoff_matchups = [m for m in matchups if m.get('week', 0) > 14]  # 2021+ so playoffs start week 15
print(f"\nPlayoff matchups found: {len(playoff_matchups)}")
if playoff_matchups:
    weeks = sorted(set(m.get('week') for m in playoff_matchups))
    print(f"Playoff weeks: {weeks}")
