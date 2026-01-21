# Investigation: "Team None" Entries in Head-to-Head Data

## Problem
The head-to-head data contained 10 entries with "Team None" as a manager name, which appeared in the generated `headToHead.js` file.

## Root Cause
In the scraped ESPN data (`espn_all_seasons.json`), some matchups have `null` values for `away_team_id` (or potentially `home_team_id`). 

When the scraper (`scrape_espn_data.py`) processes these matchups, it creates a fallback manager name:
```python
away_manager = team_id_to_manager.get(away_team_id, {}).get('manager', f"Team {away_team_id}")
```

When `away_team_id` is `None`, this becomes `"Team None"`.

## Characteristics of Null Matchups
Based on analysis of the data:
- **Scores**: All null matchups have `home_score: 0.0` and `away_score: 0`
- **Winners**: `winner_id` and `winner_manager` are `null`
- **Likely cause**: These appear to be **bye weeks** or **incomplete/cancelled matchups** where ESPN's API doesn't have complete data

## Example
```json
{
  "week": 1,
  "is_playoff": false,
  "home_team_id": 9,
  "away_team_id": null,
  "home_manager": "mendy1399",
  "away_manager": "Team None",
  "home_team_name": "Brees-y Ride To The Playoffs",
  "away_team_name": "Team None",
  "home_score": 0.0,
  "away_score": 0,
  "winner_id": null,
  "winner_manager": null
}
```

## Solution
Updated `process_data.py` to filter out invalid matchups in two places:

1. **In `calculate_head_to_head()` function** (lines 54-67):
   - Skip matchups where `home_team_id` or `away_team_id` is `None`
   - Skip matchups where manager names contain "Team None"

2. **In `calculate_all_time_stats()` function** (lines 117-130):
   - Same filtering applied when calculating highest single game scores

## Impact
- Invalid matchups (bye weeks, incomplete games) are now excluded from head-to-head calculations
- All-time statistics only count valid, completed matchups
- The "Team None" entries will no longer appear in the generated data files

## Next Steps
1. Re-run `process_data.py` to regenerate `headToHead.js` and `allTimeRecords.js` without "Team None" entries
2. Verify the generated files no longer contain "Team None" entries
3. The Next.js pages will automatically display the cleaned data

## Files Modified
- `fantasy-football/scripts/process_data.py` - Added filtering for null team IDs and "Team None" managers
