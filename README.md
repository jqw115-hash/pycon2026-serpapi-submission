# WanderLens

A travel planning app that searches across 6 SerpApi engines simultaneously to build a comprehensive destination guide. Enter any city and get attractions, restaurants, trending/viral spots, events, travel videos, and a traveler FAQ — all from real-time search data.

Built with [SerpApi](https://serpapi.com) Python SDK and [Streamlit](https://streamlit.io).

## What It Does

WanderLens takes a destination city and optional travel interests, then queries 6 SerpApi engines:

| Engine | What it finds |
|--------|--------------|
| Google Maps | Top attractions, landmarks, and points of interest |
| Google Maps | Restaurants, food markets, and street food stalls |
| Google Search | Hidden gems, TikTok/viral spots, trending neighborhoods, day trips |
| Google Search | Traveler FAQ (People Also Ask) and related search suggestions |
| Google Events | Upcoming events, festivals, and performances |
| YouTube | Travel vlogs and destination guides |

Results are organized into 6 tabs:

- **Attractions** — rated places with addresses and thumbnails
- **Food & Dining** — grouped by price tier ($, $$, $$$, $$$$)
- **Hidden Gems** — trending, viral, and instagrammable spots from travel blogs
- **Events** — upcoming local events with dates and venues
- **Travel Videos** — YouTube vlogs in a thumbnail grid
- **Traveler FAQ** — auto-generated from Google's "People Also Ask" + related searches

### Smart Query Adaptation

Select travel interests (Foodie, Culture, Outdoors, Nightlife, Shopping) and WanderLens tailors its search queries. A foodie gets street food markets and local cuisine spots; a culture enthusiast gets museums, galleries, and temples.

## Setup

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd wanderlens
```

### 2. Install dependencies

With uv (recommended):

```bash
uv sync
```

Or with pip:

```bash
pip install -r requirements.txt
```

### 3. Set your API key

Create a free SerpApi account at https://serpapi.com/users/sign_up (250 free searches).

```bash
cp .env.example .env
# Edit .env and replace with your actual key
```

### 4. Run the app

```bash
uv run streamlit run app.py
```

Or without uv:

```bash
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set `SERPAPI_KEY` in the app's Secrets management (Settings > Secrets):
   ```toml
   SERPAPI_KEY = "your_key_here"
   ```
5. Deploy

## Tech Stack

- **SerpApi** Python SDK — search engine API (Google Maps, Google Search, Google Events, YouTube)
- **Streamlit** — web UI framework
- **python-dotenv** — environment variable management
- **uv** — Python package management

## Search Budget

Each destination search uses 6 SerpApi calls. With the free tier (250 searches), you get ~40 destination lookups.
