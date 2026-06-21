# World Cup 2026 Dashboard

A clickable World Cup dashboard for browsing groups and seeing each team's played and upcoming fixtures.

## Features

- Groups A–L
- Click any team to see their match timeline
- Search teams
- Filter by group
- Favourite teams
- Dark mode
- Mobile-friendly layout
- GitHub Pages deployment workflow
- Scheduled data update workflow scaffold

## Local development

```bash
npm install
npm run dev
```

## Deployment

This repo includes `.github/workflows/deploy.yml` for GitHub Pages.

In GitHub, go to **Settings → Pages → Build and deployment** and set the source to **GitHub Actions**.

## Live data updates

The scheduled workflow runs hourly. To connect live football data:

1. Get an API key from a football data provider.
2. Add it as a repository secret named `FOOTBALL_API_KEY`.
3. Complete the provider mapping inside `scripts/update_data.py` so it rewrites `src/fixtures.js`.

The app expects fixtures in this format:

```js
{ id, date, group, home, away, homeScore, awayScore, status }
```
