"""
ESPN Fantasy Football Data Scraper
Scrapes historical data from ESPN Fantasy Football League

Usage:
    python scrape_espn_data.py

Output:
    Creates JSON files with league data in the data/ directory
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# League Configuration
LEAGUE_ID = 420782
BASE_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons"
HISTORY_BASE_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/leagueHistory"

# ESPN API endpoints
def get_seasons_url():
    """Get URL for available seasons"""
    return f"{BASE_URL}"

def get_league_url(season: int, views: List[str] = None):
    """Get URL for league data for a specific season"""
    # ESPN uses different endpoints for pre-2018 seasons
    if season < 2018:
        # Historical endpoint for pre-2018
        base_url = f"{HISTORY_BASE_URL}/{LEAGUE_ID}?seasonId={season}"
        if views:
            view_params = "&".join([f"view={v}" for v in views])
            return f"{base_url}&{view_params}"
        return base_url
    else:
        # Standard endpoint for 2018+
        base_url = f"{BASE_URL}/{season}/segments/0/leagues/{LEAGUE_ID}"
        if views:
            view_params = "&".join([f"view={v}" for v in views])
            return f"{base_url}?{view_params}"
        return base_url

def get_league_settings_url(season: int):
    """Get URL for league settings"""
    return f"{BASE_URL}/{season}/segments/0/leagues/{LEAGUE_ID}?view=mSettings"

def get_matchup_url(season: int, matchup_period: int):
    """Get URL for matchup data"""
    if season < 2018:
        return f"{HISTORY_BASE_URL}/{LEAGUE_ID}?seasonId={season}&scoringPeriodId={matchup_period}&view=mMatchup"
    else:
        return f"{BASE_URL}/{season}/segments/0/leagues/{LEAGUE_ID}?scoringPeriodId={matchup_period}&view=mMatchup"

def get_standings_url(season: int):
    """Get URL for standings"""
    if season < 2018:
        return f"{HISTORY_BASE_URL}/{LEAGUE_ID}?seasonId={season}&view=mStandings"
    else:
        return f"{BASE_URL}/{season}/segments/0/leagues/{LEAGUE_ID}?view=mStandings"

def get_playoff_url(season: int):
    """Get URL for playoff bracket"""
    if season < 2018:
        return f"{HISTORY_BASE_URL}/{LEAGUE_ID}?seasonId={season}&view=mPlayoffBracket"
    else:
        return f"{BASE_URL}/{season}/segments/0/leagues/{LEAGUE_ID}?view=mPlayoffBracket"


class ESPNFantasyScraper:
    def __init__(self, league_id: int, cookies: Optional[str] = None):
        self.league_id = league_id
        self.session = requests.Session()
        # Set headers to mimic a browser request
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://fantasy.espn.com/',
            'Origin': 'https://fantasy.espn.com',
        })
        # Add cookies if provided
        if cookies:
            self.session.headers.update({
                'Cookie': cookies
            })
            print("✓ Cookies added for authentication")
    
    def _check_response(self, response, url: str) -> Optional[Dict]:
        """Check if response is valid JSON and return parsed data"""
        if response.status_code != 200:
            return None
        
        # Check content type
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/json' not in content_type:
            # Likely HTML (login page or error)
            preview = response.text[:200].replace('\n', ' ')
            if 'login' in preview.lower() or 'sign in' in preview.lower() or 'access denied' in preview.lower():
                return {'_error': 'authentication_required', '_preview': preview}
            return {'_error': 'not_json', '_preview': preview, '_content_type': content_type}
        
        # Try to parse JSON
        try:
            data = response.json()
            # Check for error messages in the JSON response
            if isinstance(data, dict):
                if 'error' in data or 'message' in data:
                    error_msg = data.get('error') or data.get('message', 'Unknown error')
                    return {'_error': 'api_error', '_message': error_msg}
            return data
        except json.JSONDecodeError as e:
            preview = response.text[:200].replace('\n', ' ')
            return {'_error': 'json_parse_error', '_message': str(e), '_preview': preview}
    
    def get_available_seasons(self) -> List[int]:
        """Get list of available seasons for the league"""
        print("Fetching available seasons...")
        print("Note: League started using ESPN in 2009 (1999-2008 were on CBS Sportsline)")
        try:
            # League started using ESPN in 2009
            # Check from 2009 to current year
            seasons = []
            auth_error_shown = False
            debug_info = []
            
            for year in range(2009, datetime.now().year + 1):
                try:
                    # Try with basic views to check if season exists
                    url = get_league_url(year, ['mTeam'])
                    response = self.session.get(url, timeout=10)
                    data = self._check_response(response, url)
                    
                    if data is None:
                        # Non-200 status code (likely 404 for missing seasons)
                        if response.status_code == 404:
                            debug_info.append(f"  {year}: Not found (404) - season may not exist in ESPN")
                        elif response.status_code == 403:
                            debug_info.append(f"  {year}: Forbidden (403) - may need different authentication")
                        else:
                            debug_info.append(f"  {year}: Status {response.status_code}")
                        continue
                    elif '_error' in data:
                        # Error in response
                        if data['_error'] == 'authentication_required' and not auth_error_shown:
                            print(f"\n⚠ Authentication required! ESPN is returning a login page.")
                            print("   The league appears to be private. You need to add cookies.")
                            print("   See README_SCRAPER.md for instructions on how to get your cookies.")
                            auth_error_shown = True
                        debug_info.append(f"  {year}: {data['_error']}")
                        continue
                    else:
                        # Handle both dict and list responses
                        # Historical endpoint returns a list, modern returns a dict
                        league_data = None
                        if isinstance(data, list):
                            # Historical endpoint - get first item
                            if len(data) > 0 and isinstance(data[0], dict):
                                league_data = data[0]
                        elif isinstance(data, dict):
                            league_data = data
                        
                        if league_data:
                            # Check for league ID
                            if 'id' in league_data:
                                if league_data['id'] == self.league_id:
                                    seasons.append(year)
                                    print(f"  ✓ Found season: {year}")
                                else:
                                    debug_info.append(f"  {year}: Wrong league ID (got {league_data.get('id')}, expected {self.league_id})")
                            elif 'teams' in league_data or 'members' in league_data:
                                # Has teams/members but no ID - might still be valid
                                seasons.append(year)
                                print(f"  ✓ Found season: {year} (no ID field, but has teams/members)")
                            else:
                                debug_info.append(f"  {year}: Response missing 'id' field (keys: {list(league_data.keys())[:5]})")
                        else:
                            debug_info.append(f"  {year}: Empty or invalid response structure")
                except Exception as e:
                    # Network or other error
                    debug_info.append(f"  {year}: Exception - {str(e)[:50]}")
                    continue
                time.sleep(0.5)  # Be nice to ESPN's servers
            
            # Show debug info for missing seasons (especially historical ones)
            if debug_info:
                print(f"\n⚠ {len(debug_info)} seasons not found:")
                for info in debug_info:
                    print(info)
                print("")
            
            return sorted(seasons)
        except Exception as e:
            print(f"Error fetching seasons: {e}")
            return []
    
    def get_league_info(self, season: int, views: List[str] = None) -> Optional[Dict]:
        """Get basic league information for a season"""
        try:
            # Default views to get basic league data
            if views is None:
                views = ['mTeam', 'mSettings', 'mStandings']
            
            url = get_league_url(season, views)
            response = self.session.get(url, timeout=10)
            data = self._check_response(response, url)
            
            if data is None or '_error' in data:
                return None
            
            # Historical endpoint (pre-2018) returns a list, modern endpoint returns a dict
            if isinstance(data, list):
                # Get first item from list (should only be one league)
                if len(data) > 0 and isinstance(data[0], dict):
                    return data[0]
                return None
            
            # Modern endpoint returns dict directly
            return data
        except Exception as e:
            print(f"Error fetching league info for {season}: {e}")
            return None
    
    def get_teams(self, season: int) -> Dict[str, Dict]:
        """Get team information mapped by manager name"""
        league_data = self.get_league_info(season)
        if not league_data:
            return {}
        
        teams = {}
        try:
            # Get teams from league data
            teams_list = league_data.get('teams', [])
            if not isinstance(teams_list, list):
                print(f"  Warning: 'teams' is not a list for {season}")
                return {}
            
            # Get members mapping (member ID to member info)
            members_dict = {}
            for member in league_data.get('members', []):
                if isinstance(member, dict):
                    member_id = member.get('id', '')
                    members_dict[member_id] = member
            
            for team in teams_list:
                if not isinstance(team, dict):
                    continue
                
                # Get manager name - ESPN stores this in different places
                manager_name = None
                team_id = team.get('id')
                
                # Try to get owner from team.owners
                owners = team.get('owners', [])
                if owners and isinstance(owners, list) and len(owners) > 0:
                    owner_id = owners[0]
                    # owner_id might be a string (member ID) or a dict
                    if isinstance(owner_id, str):
                        # Look up member by ID
                        member = members_dict.get(owner_id)
                        if member and isinstance(member, dict):
                            manager_name = member.get('displayName') or member.get('firstName', 'Unknown')
                    elif isinstance(owner_id, dict):
                        manager_name = owner_id.get('displayName') or owner_id.get('firstName', 'Unknown')
                
                # Fallback to team name if no owner found
                if not manager_name:
                    manager_name = team.get('name', f"Team {team_id}")
                
                # Get record safely
                record = team.get('record', {})
                if isinstance(record, dict):
                    overall = record.get('overall', {})
                    if isinstance(overall, dict):
                        wins = overall.get('wins', 0)
                        losses = overall.get('losses', 0)
                        ties = overall.get('ties', 0)
                    else:
                        wins = losses = ties = 0
                else:
                    wins = losses = ties = 0
                
                teams[manager_name] = {
                    'id': team_id,
                    'name': team.get('name', ''),
                    'manager': manager_name,
                    'abbrev': team.get('abbrev', ''),
                    'wins': wins,
                    'losses': losses,
                    'ties': ties,
                }
        except Exception as e:
            print(f"Error parsing teams for {season}: {e}")
            import traceback
            traceback.print_exc()
        
        return teams
    
    def get_matchups(self, season: int) -> List[Dict]:
        """Get all matchups for a season (regular season and playoffs)"""
        league_data = self.get_league_info(season)
        if not league_data:
            return []
        
        # Create team ID to manager mapping
        team_id_to_manager = {}
        teams_data = self.get_teams(season)
        for manager, team_info in teams_data.items():
            team_id_to_manager[team_info['id']] = {
                'manager': manager,
                'team_name': team_info['name']
            }
        
        matchups = []
        try:
            settings = league_data.get('settings', {})
            schedule_settings = settings.get('scheduleSettings', {})
            
            # Get regular season weeks from settings
            regular_season_weeks = schedule_settings.get('matchupPeriodCount', 13)
            
            # NFL expanded regular season from 16 to 17 games in 2021
            # This means fantasy regular season went from 13 to 14 weeks
            # If the setting doesn't reflect this, override based on season
            if season >= 2021:
                # 2021+: Regular season is 14 weeks, playoffs start week 15
                regular_season_weeks = 14
            else:
                # Pre-2021: Regular season is 13 weeks, playoffs start week 14
                regular_season_weeks = 13
            
            # Only fetch regular season weeks (no playoffs)
            # Fetch matchups for each period (regular season only)
            print(f"    Fetching regular season periods 1-{regular_season_weeks}")
            
            for period in range(1, regular_season_weeks + 1):
                try:
                    url = get_matchup_url(season, period)
                    response = self.session.get(url, timeout=10)
                    matchup_response = self._check_response(response, url)
                    
                    if matchup_response and '_error' not in matchup_response:
                        # Handle both list (historical) and dict (modern) responses
                        matchup_data = matchup_response
                        if isinstance(matchup_response, list):
                            if len(matchup_response) > 0 and isinstance(matchup_response[0], dict):
                                matchup_data = matchup_response[0]
                            else:
                                continue
                        
                        if not isinstance(matchup_data, dict):
                            continue
                        
                        # ESPN API structure: schedule can be a list or in schedule.matchupsByMatchupPeriod
                        schedule_list = matchup_data.get('schedule', [])
                        if not schedule_list and 'schedule' in matchup_data:
                            # Try alternative structure: schedule.matchupsByMatchupPeriod[period]
                            schedule_obj = matchup_data.get('schedule', {})
                            if isinstance(schedule_obj, dict):
                                matchups_by_period = schedule_obj.get('matchupsByMatchupPeriod', {})
                                if matchups_by_period:
                                    schedule_list = matchups_by_period.get(str(period), [])
                        
                        if not schedule_list:
                            # No matchups found for this period (might be a bye week or no games)
                            continue
                            
                        for matchup in schedule_list:
                            home_team = matchup.get('home', {})
                            away_team = matchup.get('away', {})
                            
                            # Get team IDs
                            home_team_id = home_team.get('teamId')
                            away_team_id = away_team.get('teamId')
                            
                            # Get scores
                            home_score = home_team.get('totalPoints', 0)
                            away_score = away_team.get('totalPoints', 0)
                            
                            # Get manager names from mapping
                            home_manager = team_id_to_manager.get(home_team_id, {}).get('manager', f"Team {home_team_id}")
                            away_manager = team_id_to_manager.get(away_team_id, {}).get('manager', f"Team {away_team_id}")
                            
                            home_team_name = team_id_to_manager.get(home_team_id, {}).get('team_name', f"Team {home_team_id}")
                            away_team_name = team_id_to_manager.get(away_team_id, {}).get('team_name', f"Team {away_team_id}")
                            
                            # Capture additional fields to distinguish scheduled vs projected games
                            matchup_type = matchup.get('matchupType')  # e.g., 'SCHEDULED', 'PROJECTED', etc.
                            matchup_id = matchup.get('id')
                            matchup_period_id = matchup.get('matchupPeriodId')  # Critical: distinguishes scheduled vs projected
                            playoff_tier_type = matchup.get('playoffTierType')
                            is_bye = matchup.get('isBye', False)
                            winner = matchup.get('winner')  # ESPN's winner field (may differ from our calculation)
                            
                            # All matchups are regular season (we're not fetching playoffs)
                            matchups.append({
                                'week': period,
                                'is_playoff': False,
                                'home_team_id': home_team_id,
                                'away_team_id': away_team_id,
                                'home_manager': home_manager,
                                'away_manager': away_manager,
                                'home_team_name': home_team_name,
                                'away_team_name': away_team_name,
                                'home_score': home_score,
                                'away_score': away_score,
                                'winner_id': home_team_id if home_score > away_score else away_team_id if away_score > home_score else None,
                                'winner_manager': home_manager if home_score > away_score else away_manager if away_score > home_score else None,
                                # Additional fields for filtering
                                'matchup_type': matchup_type,
                                'matchup_id': matchup_id,
                                'matchup_period_id': matchup_period_id,  # Key field for filtering scheduled games
                                'playoff_tier_type': playoff_tier_type,
                                'is_bye': is_bye,
                                'winner_espn': winner,
                            })
                    
                    time.sleep(0.5)  # Rate limiting
                except Exception as e:
                    print(f"  Error fetching matchups for week {period}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error getting matchups for {season}: {e}")
        
        return matchups
    
    def get_standings(self, season: int) -> List[Dict]:
        """Get regular season standings"""
        league_data = self.get_league_info(season)
        if not league_data:
            return []
        
        # Get team info for manager mapping
        teams_data = self.get_teams(season)
        
        standings = []
        try:
            teams_list = league_data.get('teams', [])
            if not isinstance(teams_list, list):
                return []
            
            for team in teams_list:
                if not isinstance(team, dict):
                    continue
                    
                team_id = team.get('id')
                
                # Get record safely
                record = team.get('record', {})
                if isinstance(record, dict):
                    overall = record.get('overall', {})
                    if isinstance(overall, dict):
                        wins = overall.get('wins', 0)
                        losses = overall.get('losses', 0)
                        ties = overall.get('ties', 0)
                        win_percentage = overall.get('percentage', 0)
                    else:
                        wins = losses = ties = win_percentage = 0
                else:
                    wins = losses = ties = win_percentage = 0
                
                # Find manager for this team
                manager = None
                for mgr_name, team_info in teams_data.items():
                    if team_info.get('id') == team_id:
                        manager = mgr_name
                        break
                
                standings.append({
                    'team_id': team_id,
                    'team_name': team.get('name', ''),
                    'manager': manager or f"Team {team_id}",
                    'wins': wins,
                    'losses': losses,
                    'ties': ties,
                    'points_for': team.get('points', 0),
                    'points_against': team.get('pointsAgainst', 0),
                    'win_percentage': win_percentage,
                })
            
            # Sort by wins (descending), then points
            standings.sort(key=lambda x: (x['wins'], x['points_for']), reverse=True)
            
        except Exception as e:
            print(f"Error getting standings for {season}: {e}")
            import traceback
            traceback.print_exc()
        
        return standings
    
    def get_playoff_results(self, season: int) -> Dict:
        """Get playoff bracket and results"""
        league_data = self.get_league_info(season)
        if not league_data:
            return {}
        
        playoff_data = {}
        try:
            # Try to get playoff bracket
            url = get_playoff_url(season)
            response = self.session.get(url, timeout=10)
            bracket_response = self._check_response(response, url)
            
            if bracket_response and '_error' not in bracket_response:
                # Handle both list (historical) and dict (modern) responses
                bracket_data = bracket_response
                if isinstance(bracket_response, list):
                    if len(bracket_response) > 0 and isinstance(bracket_response[0], dict):
                        bracket_data = bracket_response[0]
                    else:
                        return {}
                
                if isinstance(bracket_data, dict):
                    playoff_data = bracket_data.get('playoffBracket', {})
        except Exception as e:
            print(f"Error getting playoff results for {season}: {e}")
        
        return playoff_data
    
    def scrape_all_seasons(self) -> Dict[int, Dict]:
        """Scrape data for all available seasons"""
        seasons = self.get_available_seasons()
        
        if not seasons:
            print("No seasons found. You may need to check the league ID or ESPN may require authentication.")
            return {}
        
        all_data = {}
        
        for season in seasons:
            print(f"\nScraping season {season}...")
            season_data = {
                'season': season,
                'teams': {},
                'matchups': [],
                'standings': [],
                'playoff_results': {},
            }
            
            # Get teams
            print("  Fetching teams...")
            season_data['teams'] = self.get_teams(season)
            
            # Get matchups
            print("  Fetching matchups...")
            season_data['matchups'] = self.get_matchups(season)
            
            # Get standings
            print("  Fetching standings...")
            season_data['standings'] = self.get_standings(season)
            
            # Skip playoff results - focusing on regular season data only
            season_data['playoff_results'] = {}
            
            all_data[season] = season_data
            
            # Save individual season file
            filename = f"data/espn_season_{season}.json"
            with open(filename, 'w') as f:
                json.dump(season_data, f, indent=2)
            print(f"  Saved to {filename}")
            
            time.sleep(1)  # Rate limiting between seasons
        
        return all_data


def test_single_season(season: int = 2024):
    """Test function to diagnose issues with a single season"""
    import os
    cookies = os.environ.get('ESPN_COOKIES')
    if not cookies and os.path.exists('cookies.txt'):
        with open('cookies.txt', 'r') as f:
            cookies = f.read().strip()
    
    scraper = ESPNFantasyScraper(LEAGUE_ID, cookies=cookies)
    
    print(f"\nTesting season {season}...")
    url = get_league_url(season, ['mTeam', 'mSettings'])
    print(f"URL: {url}")
    
    response = scraper.session.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
    print(f"Response length: {len(response.text)} characters")
    print(f"\nFirst 500 characters of response:")
    print("-" * 60)
    print(response.text[:500])
    print("-" * 60)
    
    data = scraper._check_response(response, url)
    if data and '_error' not in data:
        print(f"\n✓ Successfully parsed JSON!")
        # Historical endpoint returns a list, modern endpoint returns a dict
        if isinstance(data, list):
            print(f"Response is a list with {len(data)} item(s)")
            if len(data) > 0:
                data = data[0]  # Get first item
                print(f"Using first item from list")
        if isinstance(data, dict):
            print(f"Keys in response: {list(data.keys())[:10]}")
            if 'id' in data:
                print(f"League ID in response: {data['id']}")
            if 'teams' in data:
                print(f"Number of teams: {len(data.get('teams', []))}")
    elif data and '_error' in data:
        print(f"\n✗ Error: {data['_error']}")
        if '_message' in data:
            print(f"  Message: {data['_message']}")


def main():
    """Main function to run the scraper"""
    import sys
    import os
    
    # Check for test mode
    if '--test' in sys.argv or '-t' in sys.argv:
        # Test a historical season (2010) and a modern season (2024)
        test_season = 2010
        if len(sys.argv) > 2:
            try:
                test_season = int(sys.argv[2])
            except ValueError:
                pass
        test_single_season(test_season)
        return
    
    print("=" * 60)
    print("ESPN Fantasy Football Data Scraper")
    print(f"League ID: {LEAGUE_ID}")
    print("Scraping seasons: 2009-2025 (ESPN era)")
    print("Note: 1999-2008 seasons were on CBS Sportsline (not included)")
    print("Focus: Regular season data only (no playoffs)")
    print("=" * 60)
    
    # Check for cookies in environment variable or config
    cookies = os.environ.get('ESPN_COOKIES')
    
    # You can also create a cookies.txt file with your cookies
    if not cookies and os.path.exists('cookies.txt'):
        with open('cookies.txt', 'r') as f:
            cookies = f.read().strip()
    
    scraper = ESPNFantasyScraper(LEAGUE_ID, cookies=cookies)
    
    # Create data directory if it doesn't exist
    import os
    os.makedirs('data', exist_ok=True)
    
    # Scrape all seasons
    all_data = scraper.scrape_all_seasons()
    
    # Save combined data
    if all_data:
        combined_filename = "data/espn_all_seasons.json"
        with open(combined_filename, 'w') as f:
            json.dump(all_data, f, indent=2)
        print(f"\n✓ Combined data saved to {combined_filename}")
        print(f"✓ Scraped {len(all_data)} seasons")
    else:
        print("\n✗ No data was scraped. Please check:")
        print("  1. League ID is correct (420782)")
        print("  2. League is publicly accessible")
        print("  3. You may need to add authentication (cookies) if league is private")
        print("  4. Try accessing the league URL in your browser:")
        print(f"     https://fantasy.espn.com/football/league?leagueId={LEAGUE_ID}")
        print("\nIf you can access it in your browser, you may need to:")
        print("  - Copy your ESPN cookies and add them to the script")
        print("  - Or provide your league URL for testing")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and (sys.argv[1] == '--help' or sys.argv[1] == '-h'):
        print("ESPN Fantasy Football Data Scraper")
        print("\nUsage:")
        print("  python scrape_espn_data.py        - Run the scraper")
        print("  python scrape_espn_data.py --test - Test mode (diagnose issues with a single season)")
        print("\nFor authentication, create a cookies.txt file in this directory.")
        print("See HOW_TO_GET_COOKIES.md for detailed instructions.")
    else:
        main()
