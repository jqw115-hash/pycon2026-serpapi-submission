from __future__ import annotations

import os
from typing import Any

import serpapi
from dotenv import load_dotenv

load_dotenv()

INTEREST_QUERIES: dict[str, str] = {
    "Foodie": "best food markets street food local cuisine",
    "Culture": "museums galleries cultural landmarks temples",
    "Outdoors": "hiking parks nature trails scenic viewpoints",
    "Nightlife": "best bars nightlife rooftop clubs",
    "Shopping": "best shopping markets boutiques malls",
}

EMPTY_HIDDEN_GEMS: dict[str, list] = {"articles": []}

EMPTY_FAQ: dict[str, list] = {"faq": [], "related_searches": []}


def get_client() -> serpapi.Client:
    api_key = os.getenv("SERPAPI_KEY", "")
    if not api_key:
        raise ValueError("SERPAPI_KEY environment variable is not set")
    return serpapi.Client(api_key=api_key, timeout=30)


def _build_attractions_query(city: str, interests: list[str]) -> str:
    if not interests:
        return f"top things to do in {city}"
    terms = " ".join(
        INTEREST_QUERIES[i] for i in interests if i in INTEREST_QUERIES
    )
    return f"{terms} {city}" if terms else f"top things to do in {city}"


def _build_restaurants_query(city: str, interests: list[str]) -> str:
    if interests and "Foodie" in interests:
        return f"best local restaurants {city}"
    return f"best restaurants food markets in {city}"


def _make_maps_url(gps: dict[str, float]) -> str:
    lat = gps.get("latitude")
    lng = gps.get("longitude")
    if lat is not None and lng is not None:
        return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
    return ""


def _parse_place(place: dict[str, Any]) -> dict[str, Any]:
    gps = place.get("gps_coordinates", {})
    return {
        "title": place.get("title", ""),
        "rating": place.get("rating"),
        "reviews": place.get("reviews"),
        "type": place.get("type", ""),
        "address": place.get("address", ""),
        "thumbnail": place.get("thumbnail", ""),
        "gps": gps,
        "maps_url": _make_maps_url(gps),
        "place_id": place.get("place_id", ""),
        "description": place.get("description", ""),
        "price": place.get("price", ""),
        "website": place.get("website", ""),
        "phone": place.get("phone", ""),
        "open_state": place.get("open_state", ""),
        "operating_hours": place.get("operating_hours", {}),
        "service_options": place.get("service_options", {}),
    }


def _search_maps(client: serpapi.Client, query: str) -> list[dict[str, Any]]:
    try:
        results = client.search({
            "engine": "google_maps",
            "q": query,
            "type": "search",
        })
        return [_parse_place(p) for p in results.get("local_results", [])]
    except Exception:
        return []


def search_attractions(
    client: serpapi.Client, city: str, interests: list[str],
) -> list[dict[str, Any]]:
    return _search_maps(client, _build_attractions_query(city, interests))


def search_restaurants(
    client: serpapi.Client, city: str, interests: list[str],
) -> list[dict[str, Any]]:
    return _search_maps(client, _build_restaurants_query(city, interests))


def search_hidden_gems(
    client: serpapi.Client, city: str,
) -> dict[str, list]:
    try:
        results = client.search({
            "engine": "google",
            "q": (
                f"{city} hidden gems trending viral tiktok "
                "best neighborhoods day trips instagrammable"
            ),
        })
    except Exception:
        return dict(EMPTY_HIDDEN_GEMS)

    articles = [
        {
            "title": r.get("title", ""),
            "snippet": r.get("snippet", ""),
            "link": r.get("link", ""),
            "source": r.get("displayed_link", ""),
            "date": r.get("date", ""),
            "thumbnail": r.get("thumbnail", ""),
        }
        for r in results.get("organic_results", [])[:10]
    ]
    return {"articles": articles}


def search_travel_faq(
    client: serpapi.Client, city: str,
) -> dict[str, list]:
    try:
        results = client.search({
            "engine": "google",
            "q": f"{city} travel guide",
        })
    except Exception:
        return dict(EMPTY_FAQ)

    faq = [
        {
            "question": q.get("question", ""),
            "snippet": q.get("snippet", ""),
            "title": q.get("title", ""),
            "link": q.get("link", ""),
        }
        for q in results.get("related_questions", [])
    ]

    related = [
        {
            "query": s.get("query", ""),
            "link": s.get("link", ""),
        }
        for s in results.get("related_searches", [])
    ]

    return {"faq": faq, "related_searches": related}


def search_events(
    client: serpapi.Client, city: str,
) -> list[dict[str, Any]]:
    try:
        results = client.search({
            "engine": "google_events",
            "q": f"events in {city}",
        })
    except Exception:
        return []

    parsed = []
    for event in results.get("events_results", []):
        date_info = event.get("date") or {}
        venue_info = event.get("venue") or {}
        raw_address = event.get("address", "")
        address = (
            ", ".join(raw_address) if isinstance(raw_address, list)
            else raw_address
        )
        ticket_info = event.get("ticket_info") or []
        tickets = [
            {
                "source": t.get("source", ""),
                "link": t.get("link", ""),
                "link_type": t.get("link_type", ""),
            }
            for t in ticket_info
        ]

        location_map = event.get("event_location_map") or {}

        parsed.append({
            "title": event.get("title", ""),
            "date": date_info.get("start_date", "") if isinstance(date_info, dict) else "",
            "when": date_info.get("when", "") if isinstance(date_info, dict) else "",
            "address": address,
            "venue": venue_info.get("name", "") if isinstance(venue_info, dict) else str(venue_info),
            "venue_rating": venue_info.get("rating") if isinstance(venue_info, dict) else None,
            "venue_reviews": venue_info.get("reviews") if isinstance(venue_info, dict) else None,
            "description": event.get("description", ""),
            "link": event.get("link", ""),
            "thumbnail": event.get("thumbnail", ""),
            "tickets": tickets,
            "map_image": location_map.get("image", ""),
            "map_link": location_map.get("link", ""),
        })
    return parsed


def search_videos(
    client: serpapi.Client, city: str,
) -> list[dict[str, Any]]:
    try:
        results = client.search({
            "engine": "youtube",
            "search_query": f"{city} travel guide",
        })
    except Exception:
        return []

    parsed = []
    for video in results.get("video_results", [])[:12]:
        channel = video.get("channel") or {}
        thumbnail = video.get("thumbnail") or ""
        parsed.append({
            "title": video.get("title", ""),
            "link": video.get("link", ""),
            "channel": channel.get("name", "") if isinstance(channel, dict) else "",
            "views": video.get("views"),
            "length": video.get("length", ""),
            "published": video.get("published_date", ""),
            "thumbnail": (
                thumbnail.get("static", "") if isinstance(thumbnail, dict)
                else thumbnail
            ),
            "description": video.get("description", ""),
        })
    return parsed


def explore_destination(
    city: str, interests: list[str] | None = None,
) -> dict[str, Any]:
    client = get_client()
    interests = interests or []
    return {
        "attractions": search_attractions(client, city, interests),
        "restaurants": search_restaurants(client, city, interests),
        "hidden_gems": search_hidden_gems(client, city),
        "travel_faq": search_travel_faq(client, city),
        "events": search_events(client, city),
        "videos": search_videos(client, city),
    }
