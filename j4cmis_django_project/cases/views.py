from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from . import models


def _scope_to_region(queryset, request, region_field="region"):
    """NFR-06: Regional Coordinators see only their own region's data;
    National Coordinators and System Admins see everything."""
    profile = getattr(request.user, "profile", None)
    if profile and profile.role == models.UserProfile.Role.REGIONAL_COORDINATOR and profile.region:
        return queryset.filter(**{region_field: profile.region})
    return queryset


@login_required
def dashboard(request):
    cases = models.Case.objects.select_related("child")
    cases = _scope_to_region(cases, request)

    context = {
        "total_cases": cases.count(),
        "open_cases": cases.exclude(status=models.Case.Status.CLOSED).count(),
        "incomplete_cases": cases.filter(incomplete_data_flag=True).count(),
        "total_children": models.Child.objects.count(),
        "cases_by_category": cases.values("case_category").annotate(n=Count("id")).order_by("-n"),
        "recent_cases": cases.order_by("-reg_datetime")[:10],
        "incomplete_records": cases.filter(incomplete_data_flag=True).order_by("-updated_at")[:10],
        "upcoming_hearings": models.CourtProceeding.objects.select_related("case")
            .filter(hearing_date__isnull=False, case__in=cases).order_by("hearing_date")[:10],
    }
    return render(request, "cases/dashboard.html", context)
