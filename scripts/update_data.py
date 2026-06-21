"""Update World Cup fixture data.

This script is ready for live updates once you add a repository secret named
FOOTBALL_API_KEY. It currently keeps the checked-in sample data unchanged when
no key is available, so the scheduled workflow will not break.

Recommended source: API-Football or another provider that supports FIFA World Cup
fixtures, scores, and status.
"""
from __future__ import annotations

import os
from pathlib import Path

DATA_FILE = Path('src/fixtures.js')


def main() -> None:
    api_key = os.environ.get('FOOTBALL_API_KEY')
    if not api_key:
        print('FOOTBALL_API_KEY is not set. Keeping existing fixture data.')
        return

    # TODO: Replace this scaffold with the provider endpoint you choose.
    # The app only needs src/fixtures.js to export an array named `fixtures` with:
    # { id, date, group, home, away, homeScore, awayScore, status }
    print('FOOTBALL_API_KEY found. Add provider mapping here to refresh src/fixtures.js.')


if __name__ == '__main__':
    main()
