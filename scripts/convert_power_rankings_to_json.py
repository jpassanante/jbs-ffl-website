"""
Convert Power Rankings CSV files to JSON format for website
Reads all power_rankings_YYYY.csv files and creates powerRankings.js
"""
import csv
import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
OUTPUT_DIR = SCRIPT_DIR.parent / "data"

def convert_csv_to_json():
    """Convert all power rankings CSV files to JSON format"""
    
    # Find all power rankings CSV files
    csv_files = sorted(DATA_DIR.glob("power_rankings_*.csv"))
    csv_files = [f for f in csv_files if not f.name.endswith("_summary.csv")]
    
    if not csv_files:
        print("No power rankings CSV files found")
        return
    
    power_rankings = {}
    
    for csv_file in csv_files:
        # Extract season from filename (e.g., power_rankings_2024.csv -> 2024)
        season = int(csv_file.stem.split("_")[-1])
        
        print(f"Processing {season}...")
        
        # Group data by week
        weeks_data = defaultdict(list)
        
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                week = int(row['Week'])
                weeks_data[week].append({
                    'manager': row['Manager'],
                    'recordRank': float(row['Record Rank']),
                    'pointsRank': float(row['Points Rank']),
                    'breakdownRank': float(row['Breakdown Rank']),
                    'totalRank': float(row['Total Rank']),
                    'wins': int(row['Wins']),
                    'losses': int(row['Losses']),
                    'ties': int(row['Ties']),
                    'totalPoints': float(row['Total Points']),
                    'theoreticalWins': int(row['Theoretical Wins']),
                    'theoreticalLosses': int(row['Theoretical Losses']),
                    'theoreticalTies': int(row['Theoretical Ties']),
                })
        
        # Convert to array format and sort by week
        weeks_array = []
        for week in sorted(weeks_data.keys()):
            # Sort managers by totalRank (descending - higher is better)
            managers = sorted(weeks_data[week], key=lambda x: x['totalRank'], reverse=True)
            weeks_array.append({
                'week': week,
                'managers': managers
            })
        
        # Get final week rankings
        final_week = max(weeks_data.keys()) if weeks_data else 0
        final_rankings = sorted(weeks_data[final_week], key=lambda x: x['totalRank'], reverse=True) if final_week > 0 else []
        
        power_rankings[season] = {
            'weeks': weeks_array,
            'finalWeek': final_week,
            'finalRankings': final_rankings
        }
    
    # Write to JavaScript file
    output_file = OUTPUT_DIR / "powerRankings.js"
    
    with open(output_file, 'w') as f:
        f.write("// JBS FFL Power Rankings Data\n")
        f.write("// Generated from CSV files - Do not edit manually\n\n")
        f.write("export const powerRankings = ")
        json.dump(power_rankings, f, indent=2)
        f.write(";\n")
    
    print(f"\n✓ Converted {len(power_rankings)} seasons to {output_file}")
    print(f"  Seasons: {min(power_rankings.keys())}-{max(power_rankings.keys())}")

if __name__ == "__main__":
    convert_csv_to_json()
