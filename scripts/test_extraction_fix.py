"""Test the improved playoff extraction logic"""
import json
from pathlib import Path
from compare_championships import extract_playoff_results, extract_first_name

# Test 2023 specifically
data_file = Path(__file__).parent / "data" / "espn_season_2023.json"
with open(data_file, 'r') as f:
    data = json.load(f)

espn_data = {2023: data}
results = extract_playoff_results(espn_data, 2023)

print("="*70)
print("2023 Playoff Results (After Fix)")
print("="*70)
print(f"Champion: {results.get('champion')} -> {extract_first_name(results.get('champion', '')) if results.get('champion') else 'None'}")
print(f"Runner-up: {results.get('runnerUp')} -> {extract_first_name(results.get('runnerUp', '')) if results.get('runnerUp') else 'None'}")
print(f"Third Place: {results.get('thirdPlace')} -> {extract_first_name(results.get('thirdPlace', '')) if results.get('thirdPlace') else 'None'}")

print("\n" + "="*70)
print("Expected (from champions.js)")
print("="*70)
print("Champion: Tyler (TyBear612)")
print("Runner-up: Ted (UGAdogs34)")
print("Third Place: Matt (mendy1399)")

# Check if it matches
champ_match = extract_first_name(results.get('champion', '')) == 'Tyler'
runner_match = extract_first_name(results.get('runnerUp', '')) == 'Ted'
third_match = extract_first_name(results.get('thirdPlace', '')) == 'Matt'

print("\n" + "="*70)
print("Match Results")
print("="*70)
print(f"Champion match: {'✓' if champ_match else '✗'}")
print(f"Runner-up match: {'✓' if runner_match else '✗'}")
print(f"Third place match: {'✓' if third_match else '✗'}")
if champ_match and runner_match and third_match:
    print("\n🎉 All results match!")

# Write to file for verification
with open('test_extraction_output.txt', 'w') as f:
    f.write("2023 Results:\n")
    f.write(f"Champion: {results.get('champion')} -> {extract_first_name(results.get('champion', '')) if results.get('champion') else 'None'}\n")
    f.write(f"Runner-up: {results.get('runnerUp')} -> {extract_first_name(results.get('runnerUp', '')) if results.get('runnerUp') else 'None'}\n")
    f.write(f"Third: {results.get('thirdPlace')} -> {extract_first_name(results.get('thirdPlace', '')) if results.get('thirdPlace') else 'None'}\n")
    f.write(f"\nMatches: Champ={champ_match}, Runner={runner_match}, Third={third_match}\n")
