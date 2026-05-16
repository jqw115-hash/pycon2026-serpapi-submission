from __future__ import annotations

from typing import Any

import streamlit as st

st.set_page_config(
    page_title="WanderLens",
    page_icon="🌍",
    layout="wide",
)

from search import explore_destination  # noqa: E402  (must follow set_page_config)

PRICE_TIER_LABELS: dict[str, str] = {
    "$": "Budget",
    "$$": "Mid-Range",
    "$$$": "Upscale",
    "$$$$": "Fine Dining",
}

PRICE_TIERS = list(PRICE_TIER_LABELS)


@st.cache_data(ttl=3600, show_spinner=False)
def cached_explore(
    city: str, interests_tuple: tuple[str, ...],
) -> dict[str, Any]:
    return explore_destination(city, list(interests_tuple))


# --- Custom CSS ---

st.markdown(
    """
    <style>
    .rating-stars { color: #FF6B35; font-weight: bold; }
    .price-tag   { color: #2E8B57; font-weight: bold; }
    .section-header {
        font-size: 0.9em;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Rendering helpers ---

def _star_rating_text(rating: float | None) -> str:
    if not rating:
        return ""
    full = int(rating)
    has_half = rating - full >= 0.5
    empty = 5 - full - int(has_half)
    return "★" * full + ("½" if has_half else "") + "☆" * empty + f" {rating}"


def _render_place_card(place: dict[str, Any], *, show_price: bool = False) -> None:
    col_img, col_info = st.columns([1, 3])
    with col_img:
        if place.get("thumbnail"):
            st.image(place["thumbnail"], width=140)

    with col_info:
        st.markdown(f"**{place['title']}**")

        parts: list[str] = []
        if place.get("rating"):
            parts.append(
                f"<span class='rating-stars'>{_star_rating_text(place['rating'])}</span>"
            )
        if place.get("reviews"):
            parts.append(f"({place['reviews']} reviews)")
        if show_price and place.get("price"):
            parts.append(f"<span class='price-tag'>{place['price']}</span>")
        if place.get("open_state"):
            open_text = place["open_state"]
            lower = open_text.lower()
            is_open = lower.startswith("open ") or lower == "open"
            dot = "🟢" if is_open else "🔴"
            parts.append(f"{dot} {open_text}")
        if parts:
            st.markdown(" ".join(parts), unsafe_allow_html=True)

        if place.get("type"):
            st.caption(place["type"])
        if place.get("address"):
            st.caption(f"📍 {place['address']}")
        if place.get("description"):
            st.caption(place["description"])

        links: list[str] = []
        if place.get("website"):
            links.append(f"[Website]({place['website']})")
        if place.get("maps_url"):
            links.append(f"[Google Maps]({place['maps_url']})")
        if place.get("phone"):
            links.append(f"📞 {place['phone']}")
        if links:
            st.markdown(" · ".join(links))

        if place.get("operating_hours"):
            with st.expander("Operating hours"):
                for day, hours in place["operating_hours"].items():
                    st.text(f"{day.capitalize():12s} {hours}")

    st.divider()


def _render_article_card(article: dict[str, Any]) -> None:
    col_img, col_info = st.columns([1, 3])
    with col_img:
        if article.get("thumbnail"):
            st.image(article["thumbnail"], width=140)

    with col_info:
        title = article.get("title", "")
        if article.get("link"):
            st.markdown(f"**[{title}]({article['link']})**")
        else:
            st.markdown(f"**{title}**")
        if article.get("snippet"):
            st.write(article["snippet"])

        meta = [
            v for v in (article.get("source"), article.get("date")) if v
        ]
        if meta:
            st.caption(" · ".join(meta))

    st.divider()


# --- Tab renderers ---

def render_attractions_tab(attractions: list[dict[str, Any]]) -> None:
    if not attractions:
        st.info("No attractions found for this destination. Try a different city name.")
        return
    st.markdown(f"Found **{len(attractions)}** places to visit")
    for place in attractions:
        _render_place_card(place)


def render_food_tab(restaurants: list[dict[str, Any]]) -> None:
    if not restaurants:
        st.info("No restaurants or food spots found. Try a different city name.")
        return

    by_price: dict[str, list[dict[str, Any]]] = {t: [] for t in PRICE_TIERS}
    by_price["Other"] = []

    for restaurant in restaurants:
        tier = restaurant.get("price", "")
        bucket = by_price[tier] if tier in by_price else by_price["Other"]
        bucket.append(restaurant)

    has_price_groups = any(by_price[t] for t in PRICE_TIERS)

    if has_price_groups:
        for tier in PRICE_TIERS:
            if not by_price[tier]:
                continue
            label = PRICE_TIER_LABELS[tier]
            st.markdown(
                f"<div class='section-header'>{tier} — {label}</div>",
                unsafe_allow_html=True,
            )
            for place in by_price[tier]:
                _render_place_card(place, show_price=True)

        if by_price["Other"]:
            st.markdown(
                "<div class='section-header'>More options</div>",
                unsafe_allow_html=True,
            )
            for place in by_price["Other"]:
                _render_place_card(place, show_price=True)
    else:
        st.markdown(f"Found **{len(restaurants)}** food spots")
        for place in restaurants:
            _render_place_card(place, show_price=True)


def render_hidden_gems_tab(hidden_gems: dict[str, list]) -> None:
    articles = hidden_gems.get("articles", [])
    if not articles:
        st.info("No hidden gems or travel guides found for this destination.")
        return

    st.markdown(f"**{len(articles)}** travel guides and insider tips")
    for article in articles:
        _render_article_card(article)


def _render_event_card(event: dict[str, Any]) -> None:
    col_img, col_info = st.columns([1, 3])
    with col_img:
        if event.get("thumbnail"):
            st.image(event["thumbnail"], width=140)

    with col_info:
        title = event.get("title", "")
        if event.get("link"):
            st.markdown(f"**[{title}]({event['link']})**")
        else:
            st.markdown(f"**{title}**")

        when = event.get("when") or event.get("date")
        if when:
            st.write(f"📅 {when}")

        venue_parts: list[str] = []
        if event.get("venue"):
            venue_parts.append(event["venue"])
        if event.get("venue_rating"):
            venue_parts.append(_star_rating_text(event["venue_rating"]))
        if venue_parts:
            st.write(f"📍 {' · '.join(venue_parts)}")

        if event.get("address"):
            st.caption(event["address"])
        if event.get("description"):
            st.caption(event["description"][:200])

        ticket_links = []
        for ticket in event.get("tickets", []):
            if not ticket.get("link"):
                continue
            label = ticket.get("link_type", "link").capitalize()
            source = ticket.get("source", "")
            display = f"{label} ({source})" if source else label
            ticket_links.append(f"[🎟️ {display}]({ticket['link']})")
        if ticket_links:
            st.markdown(" · ".join(ticket_links))

        if event.get("map_link"):
            st.markdown(f"[View on Map]({event['map_link']})")

    st.divider()


def render_events_tab(events: list[dict[str, Any]]) -> None:
    if not events:
        st.info("No upcoming events found. Try checking closer to your travel dates.")
        return

    st.markdown(f"**{len(events)}** upcoming events")
    for event in events:
        _render_event_card(event)


def render_videos_tab(videos: list[dict[str, Any]]) -> None:
    if not videos:
        st.info("No travel videos found for this destination.")
        return

    st.markdown(f"**{len(videos)}** travel videos")
    cols_per_row = 3
    for i in range(0, len(videos), cols_per_row):
        row = videos[i : i + cols_per_row]
        cols = st.columns(cols_per_row)
        for j, video in enumerate(row):
            with cols[j]:
                if video.get("thumbnail"):
                    st.image(video["thumbnail"], use_container_width=True)

                title = video.get("title", "")
                if video.get("link"):
                    st.markdown(f"**[{title}]({video['link']})**")
                else:
                    st.markdown(f"**{title}**")

                channel = video.get("channel")
                views = f"{video['views']} views" if video.get("views") else None
                length = video.get("length")
                meta = [v for v in (channel, views, length) if v]
                if meta:
                    st.caption(" · ".join(meta))


def render_faq_tab(travel_faq: dict[str, list]) -> None:
    faq = travel_faq.get("faq", [])
    related = travel_faq.get("related_searches", [])

    if not faq and not related:
        st.info("No frequently asked questions found for this destination.")
        return

    if faq:
        st.markdown("### Common Traveler Questions")
        for item in faq:
            with st.expander(item["question"]):
                if item.get("snippet"):
                    st.write(item["snippet"])
                if item.get("link"):
                    source_title = item.get("title", "Read more")
                    st.caption(f"Source: [{source_title}]({item['link']})")

    if related:
        st.markdown("---")
        st.markdown("### Explore More")
        cols = st.columns(3)
        for i, result in enumerate(related):
            with cols[i % 3]:
                st.markdown(f"🔍 {result['query']}")


# --- Sidebar ---

with st.sidebar:
    st.title("WanderLens")
    st.caption("Your AI-powered travel planner")
    st.markdown("---")

    city = st.text_input(
        "Where do you want to go?",
        placeholder="e.g. Seoul, South Korea",
    )

    interests = st.multiselect(
        "Travel interests (optional)",
        ["Foodie", "Culture", "Outdoors", "Nightlife", "Shopping"],
        help="Tailors search results to your interests",
    )

    search_clicked = st.button(
        "Explore Destination",
        type="primary",
        use_container_width=True,
        disabled=not city.strip(),
    )

    st.markdown("---")
    st.caption("Powered by [SerpApi](https://serpapi.com)")
    st.caption(
        "Uses 6 searches per query "
        "(Google Maps x2, Google Search x2, Events, YouTube)"
    )


# --- Main area ---

if not search_clicked:
    st.title("WanderLens")
    st.markdown("### Discover your next destination")
    st.markdown(
        "Enter a city in the sidebar to get a comprehensive travel plan with "
        "**attractions**, **restaurants & food markets**, **hidden gems**, "
        "**upcoming events**, **travel videos**, and a **traveler FAQ** — "
        "all powered by real-time search data."
    )
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Try these destinations:**")
        st.markdown("- Seoul, South Korea")
        st.markdown("- Tokyo, Japan")
        st.markdown("- Barcelona, Spain")
    with col2:
        st.markdown("**How it works:**")
        st.markdown("- Searches 6 engines simultaneously")
        st.markdown("- Adapts to your interests")
        st.markdown("- Finds hidden gems, not just tourist traps")
    with col3:
        st.markdown("**Powered by:**")
        st.markdown("- Google Maps for places & dining")
        st.markdown("- Google Events for activities")
        st.markdown("- YouTube for travel videos")
        st.markdown("- Google Search for insider tips")

else:
    destination = city.strip()
    if not destination:
        st.warning("Please enter a destination city.")
        st.stop()
    st.title(f"Exploring {destination}")
    if interests:
        st.caption(f"Focused on: {', '.join(interests)}")

    with st.spinner(f"Searching across 6 engines for the best of {destination}..."):
        try:
            data = cached_explore(destination, tuple(interests))
        except ValueError as exc:
            st.error(str(exc))
            st.stop()

    tabs = st.tabs([
        "📍 Attractions",
        "🍽️ Food & Dining",
        "💎 Hidden Gems",
        "🎉 Events",
        "🎬 Travel Videos",
        "❓ Traveler FAQ",
    ])

    with tabs[0]:
        render_attractions_tab(data["attractions"])
    with tabs[1]:
        render_food_tab(data["restaurants"])
    with tabs[2]:
        render_hidden_gems_tab(data["hidden_gems"])
    with tabs[3]:
        render_events_tab(data["events"])
    with tabs[4]:
        render_videos_tab(data["videos"])
    with tabs[5]:
        render_faq_tab(data["travel_faq"])
