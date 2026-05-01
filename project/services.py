"""External API helpers for project app."""

from __future__ import annotations

import json
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


def search_musicbrainz_artists(query: str, limit: int = 8) -> list[dict]:
    """Search MusicBrainz for artists and return a small normalized payload."""
    if not query.strip():
        return []

    url = (
        "https://musicbrainz.org/ws/2/artist/"
        f"?query={quote_plus(query)}&fmt=json&limit={limit}"
    )
    req = Request(
        url,
        headers={
            # MusicBrainz requests a descriptive user-agent.
            "User-Agent": "CS412-MusicProject/1.0 (student project demo)",
            "Accept": "application/json",
        },
    )
    with urlopen(req, timeout=8) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    artists = []
    for item in payload.get("artists", []):
        artists.append(
            {
                "name": item.get("name", ""),
                "country": item.get("country", "Unknown"),
                "type": item.get("type", "Unknown"),
                "score": item.get("score", 0),
                "mbid": item.get("id", ""),
            }
        )
    return artists


def fetch_artist_release_groups(artist_mbid: str, limit: int = 8, release_type: str = "album") -> list[dict]:
    """Fetch release-groups for an artist and map likely cover-art URLs.

    ``release_type`` is passed to MusicBrainz (e.g. ``album``). Use ``""`` to omit
    the type filter and return more release kinds (still capped by ``limit``).
    """
    if not artist_mbid:
        return []

    type_q = f"&type={quote_plus(release_type)}" if release_type.strip() else ""
    url = (
        "https://musicbrainz.org/ws/2/release-group"
        f"?artist={quote_plus(artist_mbid)}&fmt=json&limit={min(limit, 100)}{type_q}"
    )
    req = Request(
        url,
        headers={
            "User-Agent": "CS412-MusicProject/1.0 (student project demo)",
            "Accept": "application/json",
        },
    )
    with urlopen(req, timeout=8) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    results = []
    for rg in payload.get("release-groups", []):
        rg_mbid = rg.get("id", "")
        first_date = rg.get("first-release-date", "")
        year = 0
        if first_date and len(first_date) >= 4 and first_date[:4].isdigit():
            year = int(first_date[:4])
        results.append(
            {
                "title": rg.get("title", "Untitled Album"),
                "year_released": year or 2000,
                "rg_mbid": rg_mbid,
                "external_cover_url": f"https://coverartarchive.org/release-group/{rg_mbid}/front-250"
                if rg_mbid
                else "",
            }
        )
    return results


def fetch_release_group_tracks(release_group_mbid: str, limit_releases: int = 5) -> list[str]:
    """Fetch track titles for a release-group using release->recordings include."""
    if not release_group_mbid:
        return []

    url = (
        "https://musicbrainz.org/ws/2/release"
        f"?release-group={quote_plus(release_group_mbid)}&fmt=json&inc=recordings&limit={limit_releases}"
    )
    req = Request(
        url,
        headers={
            "User-Agent": "CS412-MusicProject/1.0 (student project demo)",
            "Accept": "application/json",
        },
    )
    with urlopen(req, timeout=8) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    tracks: list[str] = []
    releases = payload.get("releases", [])
    for release in releases:
        media = release.get("media", [])
        for disc in media:
            for track in disc.get("tracks", []):
                title = (track.get("title") or "").strip()
                if title and title not in tracks:
                    tracks.append(title)
    return tracks


def fetch_tracks_by_album_search(title: str, artist_name: str, limit: int = 3) -> list[str]:
    """Fallback: search releases by title+artist and extract track names."""
    if not title.strip():
        return []
    query = f'release:"{title}"'
    if artist_name.strip():
        query += f' AND artist:"{artist_name}"'
    url = (
        "https://musicbrainz.org/ws/2/release/"
        f"?query={quote_plus(query)}&fmt=json&inc=recordings&limit={limit}"
    )
    req = Request(
        url,
        headers={
            "User-Agent": "CS412-MusicProject/1.0 (student project demo)",
            "Accept": "application/json",
        },
    )
    with urlopen(req, timeout=8) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    tracks: list[str] = []
    for release in payload.get("releases", []):
        for disc in release.get("media", []):
            for track in disc.get("tracks", []):
                name = (track.get("title") or "").strip()
                if name and name not in tracks:
                    tracks.append(name)
    return tracks


def fetch_tracks_from_itunes(title: str, artist_name: str) -> list[str]:
    """Fallback source for track names when MusicBrainz has sparse release data."""
    if not title.strip():
        return []
    term = f"{artist_name} {title}".strip()
    url = (
        "https://itunes.apple.com/search"
        f"?term={quote_plus(term)}&entity=song&limit=200"
    )
    req = Request(
        url,
        headers={
            "User-Agent": "CS412-MusicProject/1.0 (student project demo)",
            "Accept": "application/json",
        },
    )
    with urlopen(req, timeout=8) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    tracks: list[str] = []
    seen = set()
    title_lower = title.lower().strip()
    for item in payload.get("results", []):
        collection = (item.get("collectionName") or "").lower().strip()
        # Keep songs that plausibly belong to the same album.
        if title_lower and title_lower not in collection:
            continue
        track = (item.get("trackName") or "").strip()
        if track and track not in seen:
            seen.add(track)
            tracks.append(track)
    return tracks


def find_release_group_mbid(title: str, artist_name: str) -> str:
    """Best-effort lookup for a release-group MBID by album title + artist."""
    if not title.strip():
        return ""
    query = f'releasegroup:"{title}"'
    if artist_name.strip():
        query += f' AND artist:"{artist_name}"'
    url = (
        "https://musicbrainz.org/ws/2/release-group/"
        f"?query={quote_plus(query)}&fmt=json&limit=1"
    )
    req = Request(
        url,
        headers={
            "User-Agent": "CS412-MusicProject/1.0 (student project demo)",
            "Accept": "application/json",
        },
    )
    with urlopen(req, timeout=8) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    hits = payload.get("release-groups", [])
    if not hits:
        return ""
    return hits[0].get("id", "")
