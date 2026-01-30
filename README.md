# Graze

A modern web app for discovering high-protein dishes from nearby restaurants.

## Tech Stack

- **Vue 3** - Progressive JavaScript framework
- **Vite** - Build tool and dev server
- **Pinia** - State management
- **Vue Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Mapbox GL** - Interactive maps
- **GSAP** - Animation library

## Setup

1. Install dependencies:
```bash
yarn install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Add your environment variables to `.env`:
```
VITE_API_BASE_URL=your_api_url
VITE_MAPBOX_TOKEN=your_mapbox_token
```

## Development

Start the development server:
```bash
yarn dev
```

The app will be available at `http://localhost:5173`

## Build

Create a production build:
```bash
yarn build
```

Preview the production build:
```bash
yarn preview
```

## Features

- Search and filter dishes by macros (calories, protein, carbs, fat)
- Interactive map view of restaurant locations
- Geolocation support for nearby restaurants
- Light/dark mode with brown color scheme
- Responsive mobile design
