/**
 * Django dev server origin (no trailing slash). Used for resolving relative media paths.
 * - Physical device: point this at your machine's LAN IP, e.g. http://192.168.1.5:8000
 */
export const DJANGO_ORIGIN = 'http://127.0.0.1:8000';

/**
 * mini_insta is mounted at `/mini_insta/` in django_project/urls.py — API lives under this prefix.
 */
export const MINI_INSTA_API_BASE = `${DJANGO_ORIGIN}/mini_insta`;
