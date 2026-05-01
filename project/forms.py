"""Forms used by the project app for validation and filtering."""

import re

from django import forms

from .models import Album, Listener, Review


class ReviewForm(forms.ModelForm):
    """Create/update review with server-side rating validation."""

    manual_track_title = forms.CharField(
        required=False,
        max_length=200,
        label="Or type song name",
        widget=forms.TextInput(attrs={"placeholder": "If not listed above"}),
    )

    class Meta:
        model = Review
        fields = ["album", "listener", "review_target", "track_title", "rating", "review_text"]
        widgets = {
            "review_text": forms.Textarea(
                attrs={
                    "rows": 3,
                    "maxlength": 250,
                    "placeholder": "What did you like or not like?",
                    "class": "form-full",
                }
            ),
        }

    field_order = [
        "album",
        "listener",
        "review_target",
        "track_title",
        "manual_track_title",
        "rating",
        "review_text",
    ]

    def __init__(self, *args, track_titles=None, **kwargs):
        """Build a song dropdown from ``track_titles`` plus any existing review title."""
        track_titles = track_titles or []
        super().__init__(*args, **kwargs)
        choices: list[tuple[str, str]] = [("", "— Select a song —")]
        seen: set[str] = set()
        for raw in track_titles:
            t = (raw or "").strip()
            if t and t not in seen:
                choices.append((t, t))
                seen.add(t)
        inst_title = (getattr(self.instance, "track_title", None) or "").strip()
        if inst_title and inst_title not in seen:
            choices.append((inst_title, inst_title))
            seen.add(inst_title)
        self.fields["track_title"].widget = forms.Select(choices=choices)
        self.fields["track_title"].required = False
        self.fields["track_title"].label = "Song (for song review)"

    def clean_rating(self):
        rating = self.cleaned_data["rating"]
        if rating < 1 or rating > 10:
            raise forms.ValidationError("Rating must be between 1 and 10.")
        return rating

    def clean(self):
        cleaned = super().clean()
        target = cleaned.get("review_target")
        track = (cleaned.get("track_title") or "").strip()
        manual = (cleaned.get("manual_track_title") or "").strip()
        if target == "album":
            cleaned["track_title"] = ""
            return cleaned
        final = track or manual
        if not final:
            self.add_error("track_title", "Pick a song from the list or type a title for song reviews.")
        else:
            cleaned["track_title"] = final
        return cleaned


class AlbumFilterForm(forms.Form):
    """Simple filter controls for album list pages."""

    genre = forms.CharField(required=False, max_length=100)
    year = forms.IntegerField(required=False, min_value=1900, max_value=2100)

    def filter_queryset(self, queryset):
        """Apply validated query-parameter filters to an album queryset."""
        if not self.is_valid():
            return queryset

        genre = self.cleaned_data.get("genre")
        year = self.cleaned_data.get("year")
        if genre:
            queryset = queryset.filter(genre__icontains=genre)
        if year:
            queryset = queryset.filter(year_released=year)
        return queryset


class ArtistLookupForm(forms.Form):
    """Search field for external MusicBrainz artist lookup."""

    query = forms.CharField(max_length=100, required=True, label="Artist name")


class ListenerProfileForm(forms.ModelForm):
    """Edit listener profile fields shown on profile page."""

    class Meta:
        model = Listener
        fields = ["username", "first_name", "last_name", "email", "profile_image_url", "bio"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
            "profile_image_url": forms.URLInput(
                attrs={
                    "class": "form-full",
                    "size": 72,
                    "placeholder": "https://example.com/your-picture.jpg",
                }
            ),
        }
        help_texts = {
            "profile_image_url": (
                "Use a direct image link (often ends in .jpg or .png). "
                "If it does not load, try “Open image in new tab” on the site and paste that URL."
            ),
        }

    def clean_profile_image_url(self):
        raw = (self.cleaned_data.get("profile_image_url") or "").strip()
        if not raw:
            return ""
        if raw.startswith("//"):
            raw = "https:" + raw
        elif not re.match(r"^https?://", raw, re.IGNORECASE):
            raw = "https://" + raw.lstrip("/")
        return raw
