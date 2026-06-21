"""Refresh World Cup data from football-data.org.

Required repository secret: FOOTBALL_API_KEY
The token is sent as the X-Auth-Token request header.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

FIXTURES_FILE = Path('src/fixtures.js')
STATUS_FILE = Path('src/liveStatus.js')
API_URLS = [
    'https://api.football-data.org/v4/competitions/WC/matches?season=2026',
    'https://api.football-data.org/v4/competitions/WC/matches',
]

ALIASES = {
    'USA': 'United States',
    'United States of America': 'United States',
    'Korea Republic': 'South Korea',
    'Republic of Korea': 'South Korea',
    'Czech Republic': 'Czechia',
    'Côte d’Ivoire': 'Ivory Coast',
    "Côte d'Ivoire": 'Ivory Coast',
    'DR Congo': 'DR Congo',
    'Congo DR': 'DR Congo',
    'Cape Verde Islands': 'Cape Verde',
    'Curaçao': 'Curacao',
}

GROUPS = {
    'A': ['Mexico','South Africa','South Korea','Czechia'],
    'B': ['Canada','Bosnia and Herzegovina','Qatar','Switzerland'],
    'C': ['Brazil','Morocco','Haiti','Scotland'],
    'D': ['United States','Paraguay','Australia','Turkey'],
    'E': ['Germany','Curacao','Ivory Coast','Ecuador'],
    'F': ['Netherlands','Japan','Sweden','Tunisia'],
    'G': ['Belgium','Egypt','Iran','New Zealand'],
    'H': ['Spain','Cape Verde','Saudi Arabia','Uruguay'],
    'I': ['France','Senegal','Iraq','Norway'],
    'J': ['Argentina','Algeria','Austria','Jordan'],
    'K': ['Portugal','DR Congo','Uzbekistan','Colombia'],
    'L': ['England','Croatia','Ghana','Panama'],
}


def clean_team(name: str) -> str:
    return ALIASES.get(name, name)


def group_label(home: str, away: str, api_group: str | None = None) -> str:
    if api_group:
        label = api_group.replace('_', ' ').title()
        if label.startswith('Group'):
            return label
    for letter, teams in GROUPS.items():
        if home in teams and away in teams:
            return f'Group {letter}'
    return 'World Cup'


def status_label(status: str) -> str:
    return 'Complete' if status in {'FINISHED', 'AWARDED'} else 'Scheduled'


def fetch_json(api_key: str) -> dict:
    last_error: Exception | None = None
    for url in API_URLS:
        req = urllib.request.Request(url, headers={'X-Auth-Token': api_key})
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                headers = dict(response.headers.items())
                useful_headers = {k: v for k, v in headers.items() if k.lower().startswith('x-') or k.lower() == 'retry-after'}
                print('football-data response headers:', useful_headers)
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as exc:
            useful_headers = {k: v for k, v in exc.headers.items() if k.lower().startswith('x-') or k.lower() == 'retry-after'}
            print(f'{url} returned HTTP {exc.code}; headers: {useful_headers}')
            if exc.code == 429:
                retry_after = int(exc.headers.get('Retry-After', '60'))
                print(f'Rate limited. Sleeping {retry_after} seconds before ending safely.')
                time.sleep(min(retry_after, 60))
                sys.exit(0)
            last_error = exc
        except Exception as exc:
            last_error = exc
            print(f'{url} failed: {exc}')
    raise RuntimeError(f'Unable to fetch World Cup data: {last_error}')


def convert(payload: dict) -> list[dict]:
    converted = []
    for idx, match in enumerate(payload.get('matches', [])):
        home = clean_team(match.get('homeTeam', {}).get('name') or '')
        away = clean_team(match.get('awayTeam', {}).get('name') or '')
        utc_date = match.get('utcDate') or ''
        if not home or not away:
            continue
        score = match.get('score', {})
        full_time = score.get('fullTime') or {}
        home_score = full_time.get('home')
        away_score = full_time.get('away')
        converted.append({
            'id': match.get('id', idx),
            'date': utc_date[:10],
            'utcDate': utc_date,
            'group': group_label(home, away, match.get('group')),
            'home': home,
            'away': away,
            'homeScore': home_score,
            'awayScore': away_score,
            'status': status_label(match.get('status', '')),
        })
    return [m for m in converted if m['home'] and m['away'] and m['date']]


def write_fixtures(fixtures: list[dict]) -> None:
    rows = json.dumps(fixtures, ensure_ascii=False, indent=2)
    FIXTURES_FILE.write_text(f'export const fixtures = {rows};\n', encoding='utf-8')


def write_status(enabled: bool, source: str, message: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    content = (
        'export const liveStatus = '\
        + json.dumps({
            'enabled': enabled,
            'source': source,
            'lastUpdated': now,
            'message': message,
        }, ensure_ascii=False, indent=2)
        + ';\n'
    )
    STATUS_FILE.write_text(content, encoding='utf-8')


def main() -> None:
    api_key = os.environ.get('FOOTBALL_API_KEY')
    if not api_key:
        print('FOOTBALL_API_KEY is not set. Keeping existing fixture data.')
        write_status(False, 'Sample data', 'API key is not configured.')
        return

    try:
        payload = fetch_json(api_key)
        fixtures = convert(payload)
        if not fixtures:
            write_status(False, 'football-data.org', 'API returned no World Cup fixtures yet; keeping existing fixture data.')
            print('No fixtures returned. Existing fixture data kept.')
            return
        write_fixtures(fixtures)
        write_status(True, 'football-data.org', f'Refreshed {len(fixtures)} matches from football-data.org.')
        print(f'Updated {len(fixtures)} fixtures.')
    except Exception as exc:
        print(exc)
        write_status(False, 'football-data.org', f'Last update failed: {exc}')


if __name__ == '__main__':
    main()
