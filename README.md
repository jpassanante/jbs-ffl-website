# Fantasy Football League Website

A simple Next.js website for managing your fantasy football league.

## Features

- **Home Page**: Welcome page with navigation to all sections
- **Standings**: View current league standings
- **Teams**: Browse all teams in the league
- **Schedule**: View weekly matchups and scores

## Getting Started

First, install the dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Building for Production

To create a static export (since this is a static site):

```bash
npm run build
```

This will create an `out` directory with all the static files ready to deploy.

## Customization

All the data (standings, teams, schedule) is currently hardcoded in the page components. You can:

1. Edit the data directly in each page component (`app/standings/page.tsx`, `app/teams/page.tsx`, `app/schedule/page.tsx`)
2. Replace with your own data structure
3. Add more pages as needed

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Static Site Generation (no database needed)
