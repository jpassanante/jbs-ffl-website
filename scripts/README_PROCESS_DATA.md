# Process ESPN Data for Website

This script processes the scraped ESPN regular season data to generate JavaScript data files for the Next.js website.

## Usage

```bash
cd fantasy-football/scripts
python process_data.py
```

## What It Does

1. **Loads scraped ESPN data** from `data/espn_all_seasons.json`
2. **Calculates head-to-head records** between all manager pairs
3. **Calculates all-time statistics**:
   - Highest single game score
   - Most points in a season
   - Best regular season record
   - Most points all-time
   - Most championships (from champions.js)
4. **Generates JavaScript data files**:
   - `../data/headToHead.js` - Head-to-head records
   - `../data/allTimeRecords.js` - All-time records

## Output Files

### `headToHead.js`
Exports an array of head-to-head records:
```javascript
export const headToHeadRecords = [
  {
    manager1: "Ted",
    manager2: "Joey",
    manager1Wins: 15,
    manager2Wins: 12,
    record: "15-12",
  },
  // ...
];
```

### `allTimeRecords.js`
Exports an array of all-time records:
```javascript
export const allTimeRecords = [
  {
    category: "Most Championships",
    record: "5 Championships",
    holder: "Ted",
    details: "1999, 2001, 2004, 2020, 2024",
  },
  // ...
];
```

## After Running

Once you run the script, the Next.js pages will automatically use the real data:
- `/all-time-records` - Shows calculated all-time records
- `/head-to-head` - Shows head-to-head records between all managers

## Troubleshooting

If you get import errors in Next.js:
- Make sure the data files were generated in `fantasy-football/data/`
- Check that the files export the correct constants
- Restart the Next.js dev server after generating files
