from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.views.generic import DetailView, ListView
from plotly import graph_objects as go
from plotly.offline import plot

from .models import Voter


class VoterFilterMixin:
    request: HttpRequest

    def apply_filters(self, qs: QuerySet[Voter]) -> QuerySet[Voter]:
        party = self.request.GET.get("party")
        min_year = self.request.GET.get("min_year")
        max_year = self.request.GET.get("max_year")
        score = self.request.GET.get("score")

        if party:
            qs = qs.filter(party_affiliation=party)
        if min_year:
            qs = qs.filter(date_of_birth__year__gte=min_year)
        if max_year:
            qs = qs.filter(date_of_birth__year__lte=max_year)
        if score:
            qs = qs.filter(voter_score=score)

        for election in ["v20state", "v21town", "v21primary", "v22general", "v23town"]:
            if self.request.GET.get(election):
                qs = qs.filter(**{election: True})

        return qs

    def add_filter_context(self, context: dict) -> None:
        query = self.request.GET

        context["selected_party"] = query.get("party", "")
        context["selected_min_year"] = query.get("min_year", "")
        context["selected_max_year"] = query.get("max_year", "")
        context["selected_score"] = query.get("score", "")

        for election in ["v20state", "v21town", "v21primary", "v22general", "v23town"]:
            context[f"selected_{election}"] = bool(query.get(election))

        context["party_choices"] = (
            Voter.objects.order_by("party_affiliation")  # type: ignore[attr-defined]
            .values_list("party_affiliation", flat=True)
            .distinct()
        )
        context["score_choices"] = (
            Voter.objects.order_by("voter_score")  # type: ignore[attr-defined]
            .values_list("voter_score", flat=True)
            .distinct()
        )
        years = (
            Voter.objects.exclude(date_of_birth__isnull=True)  # type: ignore[attr-defined]
            .dates("date_of_birth", "year")
            .order_by("date_of_birth")
        )
        context["year_choices"] = [d.year for d in years]
        query_items = query.copy()
        query_items.pop("page", None)
        context["query_string"] = query_items.urlencode()


class VoterListView(VoterFilterMixin, ListView):
    model = Voter
    template_name = "voter_analytics/voter_list.html"
    context_object_name = "voters"
    paginate_by = 100

    def get_queryset(self) -> QuerySet[Voter]:
        qs: QuerySet[Voter] = super().get_queryset().order_by("last_name", "first_name")
        return self.apply_filters(qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_filter_context(context)
        return context


class VoterDetailView(DetailView):
    model = Voter
    template_name = "voter_analytics/voter_detail.html"
    context_object_name = "voter"


class VoterGraphsView(VoterFilterMixin, ListView):
    model = Voter
    template_name = "voter_analytics/graphs.html"
    context_object_name = "voters"

    def get_queryset(self) -> QuerySet[Voter]:
        qs: QuerySet[Voter] = super().get_queryset()
        return self.apply_filters(qs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_filter_context(context)
        qs = context["voters"]

        birth_data = (
            qs.exclude(date_of_birth__isnull=True)
            .values("date_of_birth__year")
            .annotate(total=Count("id"))
            .order_by("date_of_birth__year")
        )
        birth_years = [row["date_of_birth__year"] for row in birth_data]
        birth_counts = [row["total"] for row in birth_data]
        birth_fig = go.Figure(
            data=[go.Bar(x=birth_years, y=birth_counts)],
            layout=go.Layout(title="Voters by Year of Birth", xaxis_title="Year", yaxis_title="Count"),
        )

        party_data = (
            qs.values("party_affiliation")
            .annotate(total=Count("id"))
            .order_by("party_affiliation")
        )
        party_labels = [row["party_affiliation"] for row in party_data]
        party_counts = [row["total"] for row in party_data]
        party_fig = go.Figure(
            data=[go.Pie(labels=party_labels, values=party_counts)],
            layout=go.Layout(title="Voters by Party Affiliation"),
        )

        election_labels = [
            "2020 State",
            "2021 Town",
            "2021 Primary",
            "2022 General",
            "2023 Town",
        ]
        election_counts = [
            qs.filter(v20state=True).count(),
            qs.filter(v21town=True).count(),
            qs.filter(v21primary=True).count(),
            qs.filter(v22general=True).count(),
            qs.filter(v23town=True).count(),
        ]
        election_fig = go.Figure(
            data=[go.Bar(x=election_labels, y=election_counts)],
            layout=go.Layout(title="Voter Participation by Election", xaxis_title="Election", yaxis_title="Count"),
        )

        context["birth_chart"] = plot(birth_fig, output_type="div", include_plotlyjs=False)
        context["party_chart"] = plot(party_fig, output_type="div", include_plotlyjs=False)
        context["election_chart"] = plot(election_fig, output_type="div", include_plotlyjs=False)
        return context
