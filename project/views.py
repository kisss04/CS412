"""Views for the music-review project app.

This module uses generic class-based views for readable, maintainable pages:
- List/detail pages for each model
- Create/update/delete interactions for reviews
- Dashboard stats and top-rated albums for richer UX
"""

from django.contrib import messages
from django.db.models import Avg
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import AlbumFilterForm, ArtistLookupForm, ListenerProfileForm, ReviewForm
from .models import Album, Artist, Listener, Review, ReviewLike
from .services import (
    fetch_artist_release_groups,
    fetch_tracks_by_album_search,
    fetch_tracks_from_itunes,
    fetch_release_group_tracks,
    find_release_group_mbid,
    search_musicbrainz_artists,
)

def _current_listener(request):
    listener_id = request.session.get("listener_id")
    if not listener_id:
        return None
    return Listener.objects.filter(pk=listener_id).first()


def _backfill_album_covers(albums: list[Album], limit: int = 8) -> None:
    """Best-effort MusicBrainz cover URLs for albums missing art (capped per request)."""
    n = 0
    for album in albums:
        if n >= limit:
            break
        if album.cover_image or not album.external_cover_is_placeholder():
            continue
        try:
            mbid = (album.musicbrainz_release_group_mbid or "").strip() or find_release_group_mbid(
                str(album.title), str(album.artist.name)
            )
            if not mbid:
                continue
            album.musicbrainz_release_group_mbid = mbid
            album.external_cover_url = (
                f"https://coverartarchive.org/release-group/{mbid}/front-250"
            )
            album.save(update_fields=["musicbrainz_release_group_mbid", "external_cover_url"])
            n += 1
        except Exception:
            continue


class ProjectHomeView(TemplateView):
    """Discover page with top-rated albums and recent reviews."""

    template_name = "project/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_reviews"] = Review.objects.select_related(
            "album", "listener"
        ).order_by("-date_posted")[:5]
        rated_albums = list(
            Album.objects.annotate(avg_rating=Avg("reviews__rating"))
            .filter(avg_rating__isnull=False)
            .select_related("artist")
            .order_by("-avg_rating", "-year_released")
        )

        # Fill with additional albums to improve variety on Discover.
        top_albums = []
        used_artist_ids = set()
        for album in rated_albums:
            if album.artist_id in used_artist_ids:
                continue
            top_albums.append(album)
            used_artist_ids.add(album.artist_id)
            if len(top_albums) >= 12:
                break

        if len(top_albums) < 12:
            used_ids = {a.id for a in top_albums}
            filler = Album.objects.select_related("artist").exclude(id__in=used_ids).order_by(
                "-id"
            )
            for album in filler:
                if album.artist_id in used_artist_ids and len(top_albums) < 8:
                    continue
                top_albums.append(album)
                used_artist_ids.add(album.artist_id)
                if len(top_albums) >= 12:
                    break
        _backfill_album_covers(top_albums)
        context["top_albums"] = top_albums
        return context


class ArtistListView(ListView):
    """List all artists."""

    model = Artist
    template_name = "project/artist_list.html"
    context_object_name = "artists"


class ArtistDetailView(DetailView):
    """Show one artist, every stored album, and a long MusicBrainz discography list."""

    model = Artist
    template_name = "project/artist_detail.html"
    context_object_name = "artist"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artist = self.object
        albums = list(
            Album.objects.filter(artist=artist)
            .select_related("artist")
            .order_by("-year_released", "title")
        )
        context["albums"] = albums
        local_by_title = {a.title.strip().lower(): a for a in albums}

        mb_discography: list[dict] = []
        mbid_match = ""
        try:
            hits = search_musicbrainz_artists(str(artist.name), limit=8)
        except Exception:
            hits = []
        target = str(artist.name).strip().lower()
        for h in hits:
            if (h.get("name") or "").strip().lower() == target:
                mbid_match = (h.get("mbid") or "").strip()
                break
        if not mbid_match and hits:
            mbid_match = (hits[0].get("mbid") or "").strip()

        if mbid_match:
            try:
                # No ``type=`` filter so singles/EPs appear too; cap at MusicBrainz browse limit.
                mb_discography = fetch_artist_release_groups(
                    mbid_match, limit=100, release_type=""
                )
            except Exception:
                mb_discography = []
        mb_discography.sort(
            key=lambda r: (-(r.get("year_released") or 0), (r.get("title") or "").lower())
        )
        for row in mb_discography:
            key = (row.get("title") or "").strip().lower()
            row["local_album"] = local_by_title.get(key)

        context["mb_discography"] = mb_discography
        context["mbid_match"] = mbid_match
        return context


class AlbumListView(ListView):
    """List albums with optional filter form (genre/year)."""

    model = Album
    template_name = "project/album_list.html"
    context_object_name = "albums"

    def get_queryset(self):
        queryset = Album.objects.select_related("artist").all().order_by("-year_released")
        self.filter_form = AlbumFilterForm(self.request.GET)
        return self.filter_form.filter_queryset(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        return context


class AlbumDetailView(DetailView):
    """Show one album, cover art, and its reviews."""

    model = Album
    template_name = "project/album_detail.html"
    context_object_name = "album"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["listeners"] = Listener.objects.all().order_by("last_name", "first_name")
        return context


class ListenerListView(ListView):
    """List all listeners."""

    model = Listener
    template_name = "project/listener_list.html"
    context_object_name = "listeners"


class ListenerDetailView(DetailView):
    """Show one listener and reviews they have written."""

    model = Listener
    template_name = "project/listener_detail.html"
    context_object_name = "listener"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listener = self.object
        reviews = listener.reviews.select_related("album").all().order_by("-id")
        likes_received = ReviewLike.objects.filter(review__listener=listener).select_related(
            "listener", "review", "review__album"
        )
        likes_given = listener.liked_reviews.select_related("review", "review__listener", "review__album")
        context["reviews"] = reviews
        context["likes_received_count"] = likes_received.count()
        context["likes_given_count"] = likes_given.count()
        context["likes_received"] = likes_received[:20]
        context["likes_given"] = likes_given[:20]
        context["listeners"] = Listener.objects.all().order_by("last_name", "first_name")
        cur = _current_listener(self.request)
        context["is_own_profile"] = cur is not None and cur.pk == listener.pk
        return context


class ReviewListView(ListView):
    """List all reviews in reverse chronological order."""

    model = Review
    template_name = "project/review_list.html"
    context_object_name = "reviews"

    def get_queryset(self):
        return (
            Review.objects.select_related("album", "album__artist", "listener")
            .prefetch_related("likes")
            .order_by("-date_posted")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["listeners"] = Listener.objects.all().order_by("last_name", "first_name")
        seen: set[int] = set()
        page_albums: list[Album] = []
        for rev in context["reviews"]:
            if rev.album_id in seen:
                continue
            seen.add(rev.album_id)
            page_albums.append(rev.album)
        _backfill_album_covers(page_albums, limit=12)
        return context


class ReviewHubView(TemplateView):
    """Search albums, preview covers, and submit star-based reviews."""

    template_name = "project/review_hub.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        albums = Album.objects.select_related("artist").all().order_by("title")
        if query:
            albums = albums.filter(title__icontains=query) | albums.filter(
                artist__name__icontains=query
            )
        context["query"] = query
        context["albums"] = albums[:20]
        context["external_albums"] = []
        if query:
            seen_rg = set()
            external_albums = []
            try:
                artist_hits = search_musicbrainz_artists(query, limit=2)
                for artist in artist_hits:
                    for rg in fetch_artist_release_groups(artist["mbid"], limit=6):
                        rg_id = rg.get("rg_mbid")
                        if not rg_id or rg_id in seen_rg:
                            continue
                        seen_rg.add(rg_id)
                        external_albums.append(
                            {
                                "title": rg["title"],
                                "year_released": rg["year_released"],
                                "external_cover_url": rg["external_cover_url"],
                                "rg_mbid": rg_id,
                                "artist_name": artist["name"],
                                "artist_country": artist.get("country", "Unknown"),
                                "artist_mbid": artist["mbid"],
                            }
                        )
                context["external_albums"] = external_albums[:12]
            except Exception:
                context["external_albums"] = []
        context["recent_reviews"] = (
            Review.objects.select_related("album", "listener")
            .prefetch_related("likes")
            .order_by("-id")[:8]
        )
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action == "import_album":
            artist_name = (request.POST.get("artist_name") or "").strip()
            artist_country = (request.POST.get("artist_country") or "").strip() or "Unknown"
            album_title = (request.POST.get("album_title") or "").strip()
            rg_mbid = (request.POST.get("rg_mbid") or "").strip()
            cover_url = (request.POST.get("external_cover_url") or "").strip()
            year_raw = request.POST.get("year_released") or "2000"
            try:
                year_released = int(year_raw)
            except ValueError:
                year_released = 2000

            if not artist_name or not album_title:
                messages.error(request, "Missing imported album details.")
                return redirect("project:review_hub")
            artist, _ = Artist.objects.get_or_create(
                name=artist_name,
                defaults={
                    "genre": "Imported from MusicBrainz",
                    "origin_country": artist_country,
                    "bio": "Imported from MusicBrainz metadata.",
                },
            )
            album, _ = Album.objects.get_or_create(
                title=album_title,
                artist=artist,
                defaults={
                    "year_released": year_released,
                    "genre": "Imported",
                    "external_cover_url": cover_url,
                    "musicbrainz_release_group_mbid": rg_mbid,
                },
            )
            messages.success(request, f"Loaded {album.title} for review.")
            return redirect("project:review_compose", album_id=album.id)

        messages.error(request, "Choose an album first, then submit on the review page.")
        return redirect("project:review_hub")


def _review_tracks_for_album(album: Album) -> list[str]:
    """Get track list from MusicBrainz, with metadata fallback for non-imported albums."""
    mbid = album.musicbrainz_release_group_mbid
    if not mbid:
        mbid = find_release_group_mbid(album.title, album.artist.name)
        if mbid:
            album.musicbrainz_release_group_mbid = mbid
            if not album.external_cover_url:
                album.external_cover_url = (
                    f"https://coverartarchive.org/release-group/{mbid}/front-250"
                )
            album.save(update_fields=["musicbrainz_release_group_mbid", "external_cover_url"])
    tracks: list[str] = []
    if mbid:
        tracks = fetch_release_group_tracks(mbid)
    if not tracks:
        tracks = fetch_tracks_by_album_search(album.title, album.artist.name)
    if not tracks:
        tracks = fetch_tracks_from_itunes(album.title, album.artist.name)
    return tracks


def review_compose_view(request, album_id: int):
    """Dedicated page to review one album or one song."""
    album = Album.objects.select_related("artist").filter(pk=album_id).first()
    if not album:
        messages.error(request, "Album not found.")
        return redirect("project:review_hub")

    try:
        tracks = _review_tracks_for_album(album)
    except Exception:
        tracks = []

    current = _current_listener(request)
    if not current:
        messages.info(request, "Please sign in before posting a review.")
        return redirect(f"{reverse_lazy('project:sign_in')}?next={request.path}")
    if request.method == "POST":
        review_text = (request.POST.get("review_text") or "").strip()
        rating_raw = request.POST.get("rating")
        review_target = (request.POST.get("review_target") or "album").strip()
        track_title = (request.POST.get("track_title") or "").strip()
        manual_track_title = (request.POST.get("manual_track_title") or "").strip()
        try:
            stars = int(rating_raw or "0")
        except ValueError:
            stars = 0
        if stars < 1 or stars > 10:
            messages.error(request, "Please pick a star rating from 1 to 10.")
            return redirect("project:review_compose", album_id=album.id)
        if not review_text:
            messages.error(request, "Please add a short review.")
            return redirect("project:review_compose", album_id=album.id)
        if review_target == "song" and not track_title and not manual_track_title:
            messages.error(request, "Please choose a song when reviewing a song.")
            return redirect("project:review_compose", album_id=album.id)
        if review_target not in {"album", "song"}:
            review_target = "album"

        final_track_title = track_title or manual_track_title

        Review.objects.create(
            album=album,
            listener=current,
            review_target=review_target,
            track_title=final_track_title if review_target == "song" else "",
            rating=stars,
            review_text=review_text,
        )
        messages.success(request, "Review posted.")
        return redirect("project:review_list")

    return render(
        request,
        "project/review_compose.html",
        {"selected_album": album, "selected_tracks": tracks, "current_listener": current},
    )


class ReviewCreateView(CreateView):
    """Create a review via form input."""

    model = Review
    form_class = ReviewForm
    template_name = "project/review_form.html"
    success_url = reverse_lazy("project:review_hub")

    def _album_id_for_request(self):
        return self.request.GET.get("album") or (
            self.request.POST.get("album") if self.request.method == "POST" else None
        )

    def _review_album_for_context(self):
        album_id = self._album_id_for_request()
        if not album_id:
            return None
        return Album.objects.select_related("artist").filter(pk=album_id).first()

    def _track_titles_for_request(self) -> list[str]:
        album = self._review_album_for_context()
        if not album:
            return []
        try:
            return _review_tracks_for_album(album)
        except Exception:
            return []

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["track_titles"] = self._track_titles_for_request()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["review_album"] = self._review_album_for_context()
        context["current_listener"] = _current_listener(self.request)
        context["rating_stars"] = self._resolved_rating_stars_create()
        context["all_albums"] = Album.objects.select_related("artist").order_by("title")
        return context

    def _resolved_rating_stars_create(self) -> int:
        if self.request.method == "POST":
            try:
                r = int(self.request.POST.get("rating") or "0")
                if 1 <= r <= 10:
                    return r
            except ValueError:
                pass
        return 5

    def form_valid(self, form):
        messages.success(self.request, "Review submitted successfully.")
        return super().form_valid(form)


class ReviewUpdateView(UpdateView):
    """Edit an existing review."""

    model = Review
    form_class = ReviewForm
    template_name = "project/review_form.html"
    success_url = reverse_lazy("project:review_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        try:
            kwargs["track_titles"] = _review_tracks_for_album(self.object.album)
        except Exception:
            kwargs["track_titles"] = []
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["review_album"] = self.object.album
        context["current_listener"] = self.object.listener
        context["rating_stars"] = self._resolved_rating_stars_edit()
        context["all_albums"] = Album.objects.select_related("artist").order_by("title")
        return context

    def _resolved_rating_stars_edit(self) -> int:
        if self.request.method == "POST":
            try:
                r = int(self.request.POST.get("rating") or "0")
                if 1 <= r <= 10:
                    return r
            except ValueError:
                pass
        r = self.object.rating
        return max(1, min(10, int(r))) if r else 5

    def form_valid(self, form):
        messages.success(self.request, "Review updated successfully.")
        return super().form_valid(form)


class ReviewDeleteView(DeleteView):
    """Delete a review after confirmation."""

    model = Review
    template_name = "project/review_confirm_delete.html"
    success_url = reverse_lazy("project:review_list")

    def form_valid(self, form):
        messages.success(self.request, "Review deleted.")
        return super().form_valid(form)


def musicbrainz_lookup_view(request):
    """Function-based view for external artist search integration."""
    results = []
    error = ""
    imported_count = 0
    form = ArtistLookupForm(request.GET or None)
    if request.method == "POST":
        artist_name = (request.POST.get("artist_name") or "").strip()
        artist_country = (request.POST.get("artist_country") or "").strip() or "Unknown"
        artist_mbid = (request.POST.get("artist_mbid") or "").strip()
        if not artist_name or not artist_mbid:
            messages.error(request, "Missing artist information for import.")
            return redirect("project:musicbrainz_lookup")
        artist, _ = Artist.objects.get_or_create(
            name=artist_name,
            defaults={
                "genre": "Imported from MusicBrainz",
                "origin_country": artist_country,
                "bio": "Imported from MusicBrainz metadata.",
            },
        )
        try:
            release_groups = fetch_artist_release_groups(artist_mbid, limit=8)
            for item in release_groups:
                Album.objects.get_or_create(
                    title=item["title"],
                    artist=artist,
                    defaults={
                        "year_released": item["year_released"],
                        "genre": "Imported",
                        "external_cover_url": item["external_cover_url"],
                        "musicbrainz_release_group_mbid": item["rg_mbid"],
                    },
                )
                imported_count += 1
        except Exception:
            messages.error(request, "Could not import albums from MusicBrainz right now.")
            return redirect("project:musicbrainz_lookup")
        messages.success(request, f"Imported {imported_count} albums for {artist_name}.")
        return redirect("project:album_list")

    if request.GET and form.is_valid():
        query = form.cleaned_data["query"]
        try:
            results = search_musicbrainz_artists(query)
        except Exception:
            error = "Could not reach MusicBrainz right now. Please try again."

    return render(
        request,
        "project/musicbrainz_lookup.html",
        {"form": form, "results": results, "error": error},
    )


class ListenerProfileUpdateView(UpdateView):
    """Edit profile information for a listener."""

    model = Listener
    form_class = ListenerProfileForm
    template_name = "project/listener_profile_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cur = _current_listener(self.request)
        context["is_own_profile"] = cur is not None and cur.pk == self.object.pk
        return context

    def get_success_url(self):
        return reverse_lazy("project:listener_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Profile updated.")
        return super().form_valid(form)


def toggle_review_like_view(request, pk: int):
    """Toggle like/unlike on a review for a selected listener."""
    if request.method != "POST":
        return redirect("project:review_hub")

    next_url = request.POST.get("next") or reverse_lazy("project:review_hub")
    review = Review.objects.filter(pk=pk).first()
    if not review:
        messages.error(request, "Review not found.")
        return redirect(next_url)

    listener = _current_listener(request)
    if not listener:
        messages.info(request, "Please sign in to like reviews.")
        return redirect(f"{reverse_lazy('project:sign_in')}?next={next_url}")

    like, created = ReviewLike.objects.get_or_create(review=review, listener=listener)
    if created:
        messages.success(request, "Review liked.")
    else:
        like.delete()
        messages.info(request, "Like removed.")
    return redirect(next_url)


def sign_in_view(request):
    """Simple profile-based sign in for the project app."""
    next_url = request.GET.get("next") or request.POST.get("next") or reverse_lazy(
        "project:home"
    )
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        first_name = (request.POST.get("first_name") or "").strip() or "Music"
        last_name = (request.POST.get("last_name") or "").strip() or "Fan"
        email = (request.POST.get("email") or "").strip() or f"{username}@example.local"
        if not username:
            messages.error(request, "Username is required.")
            return render(request, "project/sign_in.html", {"next_url": next_url})
        listener, _ = Listener.objects.get_or_create(
            username=username,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
            },
        )
        request.session["listener_id"] = listener.id
        messages.success(request, f"Signed in as {listener.username}.")
        return redirect(next_url)
    return render(request, "project/sign_in.html", {"next_url": next_url})


def sign_out_view(request):
    """End the session listener and send the user to sign-in with a reminder."""
    if request.method != "POST":
        messages.info(request, "Use the Sign out button to log out.")
        return redirect("project:home")
    request.session.pop("listener_id", None)
    messages.info(
        request,
        "You’re signed out. Sign in again with your username to use your profile, post reviews, and give likes.",
    )
    return redirect("project:sign_in")


def my_profile_view(request):
    listener = _current_listener(request)
    if not listener:
        messages.info(request, "Sign in to access your profile.")
        return redirect(f"{reverse_lazy('project:sign_in')}?next={reverse_lazy('project:my_profile')}")
    return redirect("project:listener_detail", pk=listener.pk)


def delete_my_profile_view(request):
    """Show a confirmation page, then delete the signed-in listener and clear the session.

    Related ``Review`` and ``ReviewLike`` rows are removed via ``CASCADE``.
    """
    listener = _current_listener(request)
    if not listener:
        messages.info(request, "Sign in to delete your profile.")
        return redirect(f"{reverse_lazy('project:sign_in')}?next={reverse_lazy('project:my_profile_delete')}")
    if request.method == "POST":
        if request.POST.get("confirm") == "DELETE":
            listener.delete()
            request.session.pop("listener_id", None)
            messages.success(request, "Your profile has been deleted.")
            return redirect("project:home")
        messages.info(request, "Profile not deleted.")
        return redirect("project:my_profile")
    return render(
        request,
        "project/listener_delete_confirm.html",
        {"listener": listener},
    )
