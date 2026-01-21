# Data Review Tools

After scraping ESPN data, use these tools to review and validate your data.

## Quick Review

Get a quick summary of all seasons:

```bash
python quick_review.py
```

This shows:
- Total number of seasons found
- Overall statistics (teams, matchups, playoffs)
- Per-season summary (teams, matchups, champions)
- Any issues found

## Detailed Review

### Review All Seasons

```bash
python review_data.py
```

Shows comprehensive summary with validation for all seasons.

### Review Specific Season

```bash
python review_data.py --season 2024
```

Shows detailed information for a specific season:
- Team details with records
- Final standings
- Sample matchups
- Validation issues

## Manual Review

You can also manually inspect the JSON files:

```bash
# View a specific season file
cat data/espn_season_2024.json | python -m json.tool | less

# Or open in a text editor
notepad data/espn_season_2024.json
```

## What to Check

When reviewing the data, verify:

1. **Teams**: Each season should have 10 teams with manager names
2. **Matchups**: Should have regular season + playoff matchups
3. **Standings**: Should match ESPN's final regular season standings
4. **Playoffs**: Should have playoff bracket/results for completed seasons
5. **Manager Names**: Should be consistent (not "Team 1", "Team 2", etc.)

## Common Issues

- **Missing manager names**: If you see "Team 1", "Team 2", etc., the team-to-manager mapping failed
- **Empty matchups**: Season might not have been fully scraped
- **Missing playoffs**: Playoff data might not be available for that season
