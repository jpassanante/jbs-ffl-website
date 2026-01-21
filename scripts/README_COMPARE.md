# Championship Data Comparison

This script compares your existing `champions.js` file with the scraped ESPN data to validate championship results.

## Usage

```bash
python compare_championships.py
```

## What It Does

1. **Loads Data**:
   - Parses `champions.js` to extract championship history
   - Loads ESPN scraped data from `data/espn_all_seasons.json`

2. **Extracts Playoff Results**:
   - Champion (playoff winner)
   - Runner-up (playoff loser)
   - Third place
   - Regular season champion (first in standings)
   - Regular season most points

3. **Maps Manager Names**:
   - ESPN uses display names (e.g., "benhkline", "PLazaroff")
   - champions.js uses first names (e.g., "Ben", "Peter")
   - Script attempts to map automatically, but may need manual adjustment

4. **Compares Results**:
   - Shows matches (✓)
   - Shows discrepancies (⚠)
   - Identifies missing data

## Manager Name Mapping

The script includes a basic mapping function, but you may need to update it if names don't match correctly. Edit the `extract_first_name()` function in the script to add custom mappings:

```python
name_mappings = {
    'benhkline': 'Ben',
    'plazaroff': 'Peter',
    'lannybenson13': 'Lanny',
    # Add your custom mappings here
}
```

## Understanding the Output

- **✓ Perfect matches**: All championship fields match between champions.js and ESPN data
- **⚠ Discrepancies**: Fields that don't match (could be data errors or name mapping issues)
- **Manager Name Mapping**: Shows how ESPN display names are mapped to first names

## Common Issues

1. **Name Mismatches**: ESPN display names may not map correctly to first names
   - Solution: Update the `name_mappings` dictionary in the script

2. **Missing Playoff Data**: Some seasons may not have playoff matchups in ESPN
   - This is normal for incomplete seasons or if ESPN doesn't have the data

3. **Different Playoff Structures**: Playoff formats may have changed over the years
   - The script tries to handle this, but may need adjustment for specific seasons

## Next Steps

After running the comparison:
1. Review discrepancies carefully
2. Update manager name mappings if needed
3. Verify any data errors in either champions.js or ESPN data
4. Update champions.js with any missing information from ESPN data
