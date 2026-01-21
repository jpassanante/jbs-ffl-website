"""Test if we can fetch week 15 data for 2023"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scrape_espn_data import ESPNFantasyScraper, get_matchup_url, LEAGUE_ID

# Check for cookies
cookies = os.environ.get('ESPN_COOKIES')
if not cookies and os.path.exists('cookies.txt'):
    with open('cookies.txt', 'r') as f:
        cookies = f.read().strip()

if not cookies:
    print("⚠️  No cookies found. You may need authentication.")
    print("   Create a cookies.txt file or set ESPN_COOKIES environment variable")
    sys.exit(1)

scraper = ESPNFantasyScraper(LEAGUE_ID, cookies=cookies)

# Try to fetch week 15 for 2023
print("Testing week 15 fetch for 2023...")
url = get_matchup_url(2023, 15)
print(f"URL: {url}")

response = scraper.session.get(url, timeout=10)
result = scraper._check_response(response, url)

if result and '_error' not in result:
    print("✓ Successfully fetched week 15 data!")
    if isinstance(result, list):
        if len(result) > 0:
            result = result[0]
            print(f"Response was a list, using first item")
    if isinstance(result, dict):
        matchups = result.get('schedule', {}).get('matchupsByMatchupPeriod', {})
        if matchups:
            week15_matchups = matchups.get('15', [])
            print(f"Week 15 matchups found: {len(week15_matchups)}")
            if week15_matchups:
                print("\nSample matchup:")
                m = week15_matchups[0]
                print(f"  {m}")
        else:
            print("No matchups found in response")
            print(f"Keys in response: {list(result.keys())[:10]}")
else:
    print("✗ Failed to fetch week 15 data")
    if result and '_error' in result:
        print(f"Error: {result['_error']}")
