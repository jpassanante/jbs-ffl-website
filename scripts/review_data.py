"""
ESPN Fantasy Football Data Review Script
Quickly review and validate scraped ESPN data

Usage:
    python review_data.py
    python review_data.py --season 2024  # Review specific season
    python review_data.py --summary     # Just show summary
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

DATA_DIR = Path(__file__).parent / "data"


def load_season_data(season: int) -> Dict:
    """Load data for a specific season"""
    filepath = DATA_DIR / f"espn_season_{season}.json"
    if not filepath.exists():
        return None
    with open(filepath, 'r') as f:
        return json.load(f)


def load_all_seasons() -> Dict:
    """Load combined data file"""
    filepath = DATA_DIR / "espn_all_seasons.json"
    if not filepath.exists():
        return None
    with open(filepath, 'r') as f:
        return json.load(f)


def get_season_summary(season_data: Dict) -> Dict:
    """Get summary statistics for a season"""
    if not season_data:
        return None
    
    summary = {
        'season': season_data.get('season'),
        'teams_count': len(season_data.get('teams', {})),
        'matchups_count': len(season_data.get('matchups', [])),
        'standings_count': len(season_data.get('standings', [])),
        'has_playoffs': bool(season_data.get('playoff_results', {})),
    }
    
    # Get team names
    teams = season_data.get('teams', {})
    summary['team_managers'] = list(teams.keys()) if teams else []
    
    # Get regular season vs playoff matchups
    matchups = season_data.get('matchups', [])
    summary['regular_season_matchups'] = sum(1 for m in matchups if not m.get('is_playoff', False))
    summary['playoff_matchups'] = sum(1 for m in matchups if m.get('is_playoff', False))
    
    # Get standings info
    standings = season_data.get('standings', [])
    if standings:
        summary['regular_season_champ'] = standings[0].get('manager', 'Unknown') if standings else None
        summary['most_points'] = max(standings, key=lambda x: x.get('points_for', 0)).get('manager', 'Unknown') if standings else None
    
    # Get playoff results
    playoff = season_data.get('playoff_results', {})
    if playoff:
        summary['playoff_data_keys'] = list(playoff.keys())
    
    return summary


def print_season_summary(summary: Dict):
    """Print formatted summary for a season"""
    if not summary:
        print("  No data available")
        return
    
    print(f"\n  Season {summary['season']}:")
    print(f"    Teams: {summary['teams_count']}")
    print(f"    Managers: {', '.join(summary['team_managers'][:5])}{'...' if len(summary['team_managers']) > 5 else ''}")
    print(f"    Matchups: {summary['matchups_count']} total ({summary['regular_season_matchups']} regular, {summary['playoff_matchups']} playoff)")
    print(f"    Standings: {summary['standings_count']} teams")
    if summary.get('regular_season_champ'):
        print(f"    Regular Season Champ: {summary['regular_season_champ']}")
    if summary.get('most_points'):
        print(f"    Most Points: {summary['most_points']}")
    if summary.get('has_playoffs'):
        print(f"    Playoff Data: Available")
        if summary.get('playoff_data_keys'):
            print(f"      Keys: {', '.join(summary['playoff_data_keys'][:5])}")


def validate_season(season_data: Dict) -> List[str]:
    """Validate season data and return list of issues"""
    issues = []
    
    if not season_data:
        issues.append("No data file found")
        return issues
    
    season = season_data.get('season')
    
    # Check teams
    teams = season_data.get('teams', {})
    if not teams:
        issues.append("No teams data")
    else:
        for manager, team_info in teams.items():
            if not team_info.get('id'):
                issues.append(f"Team '{manager}' missing ID")
            if not team_info.get('name'):
                issues.append(f"Team '{manager}' missing name")
    
    # Check matchups
    matchups = season_data.get('matchups', [])
    if not matchups:
        issues.append("No matchups data")
    else:
        # Check for missing manager names
        missing_managers = set()
        for matchup in matchups:
            if matchup.get('home_manager', '').startswith('Team '):
                missing_managers.add(matchup.get('home_manager'))
            if matchup.get('away_manager', '').startswith('Team '):
                missing_managers.add(matchup.get('away_manager'))
        if missing_managers:
            issues.append(f"Matchups with missing manager names: {len(missing_managers)} instances")
    
    # Check standings
    standings = season_data.get('standings', [])
    if not standings:
        issues.append("No standings data")
    
    return issues


def print_all_seasons_summary():
    """Print summary for all seasons"""
    print("=" * 70)
    print("ESPN Fantasy Football Data Review - All Seasons Summary")
    print("=" * 70)
    
    all_data = load_all_seasons()
    if not all_data:
        print("Error: Could not load espn_all_seasons.json")
        return
    
    seasons = sorted(all_data.keys())
    print(f"\nFound {len(seasons)} seasons: {min(seasons)} - {max(seasons)}")
    
    # Overall stats
    total_teams = 0
    total_matchups = 0
    seasons_with_playoffs = 0
    
    for season in seasons:
        season_data = all_data[season]
        summary = get_season_summary(season_data)
        if summary:
            total_teams += summary['teams_count']
            total_matchups += summary['matchups_count']
            if summary['has_playoffs']:
                seasons_with_playoffs += 1
    
    print(f"\nOverall Statistics:")
    print(f"  Total teams across all seasons: {total_teams}")
    print(f"  Total matchups: {total_matchups}")
    print(f"  Seasons with playoff data: {seasons_with_playoffs}/{len(seasons)}")
    
    # Print per-season summaries
    print(f"\nPer-Season Details:")
    for season in seasons:
        season_data = all_data[season]
        summary = get_season_summary(season_data)
        print_season_summary(summary)
    
    # Validation
    print(f"\n" + "=" * 70)
    print("Data Validation")
    print("=" * 70)
    
    all_issues = {}
    for season in seasons:
        season_data = all_data[season]
        issues = validate_season(season_data)
        if issues:
            all_issues[season] = issues
    
    if all_issues:
        print(f"\n⚠ Found issues in {len(all_issues)} season(s):")
        for season, issues in all_issues.items():
            print(f"\n  Season {season}:")
            for issue in issues:
                print(f"    - {issue}")
    else:
        print("\n✓ No issues found - all seasons look good!")


def review_single_season(season: int):
    """Review a single season in detail"""
    print("=" * 70)
    print(f"ESPN Fantasy Football Data Review - Season {season}")
    print("=" * 70)
    
    season_data = load_season_data(season)
    if not season_data:
        print(f"Error: Could not load data for season {season}")
        return
    
    # Summary
    summary = get_season_summary(season_data)
    print_season_summary(summary)
    
    # Detailed team info
    teams = season_data.get('teams', {})
    if teams:
        print(f"\n  Teams ({len(teams)}):")
        for manager, team_info in teams.items():
            print(f"    - {manager}: {team_info.get('name', 'N/A')} (ID: {team_info.get('id')})")
            print(f"      Record: {team_info.get('wins', 0)}-{team_info.get('losses', 0)}-{team_info.get('ties', 0)}")
    
    # Standings
    standings = season_data.get('standings', [])
    if standings:
        print(f"\n  Final Standings:")
        for i, team in enumerate(standings[:5], 1):  # Top 5
            print(f"    {i}. {team.get('manager', 'Unknown')}: {team.get('wins', 0)}-{team.get('losses', 0)} "
                  f"({team.get('points_for', 0):.2f} pts)")
    
    # Sample matchups
    matchups = season_data.get('matchups', [])
    if matchups:
        print(f"\n  Sample Matchups (first 3):")
        for matchup in matchups[:3]:
            week = matchup.get('week', '?')
            home = matchup.get('home_manager', 'Unknown')
            away = matchup.get('away_manager', 'Unknown')
            home_score = matchup.get('home_score', 0)
            away_score = matchup.get('away_score', 0)
            playoff = " (Playoff)" if matchup.get('is_playoff') else ""
            print(f"    Week {week}{playoff}: {home} ({home_score:.2f}) vs {away} ({away_score:.2f})")
    
    # Validation
    issues = validate_season(season_data)
    if issues:
        print(f"\n  ⚠ Issues Found:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print(f"\n  ✓ No issues found")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Review ESPN Fantasy Football scraped data')
    parser.add_argument('--season', type=int, help='Review specific season')
    parser.add_argument('--summary', action='store_true', help='Show only summary')
    args = parser.parse_args()
    
    if args.season:
        review_single_season(args.season)
    else:
        print_all_seasons_summary()


if __name__ == "__main__":
    main()
