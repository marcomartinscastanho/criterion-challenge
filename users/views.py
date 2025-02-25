import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from users.forms import PickOrderCriteriaForm, ProfileForm, SessionTimesForm
from users.models import UserPreference
from users.utils import get_days_of_week, get_user_watched_films, get_user_watchlist_films, get_watched_chart_data


@login_required
def profile(request: HttpRequest):
    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return render(
                request, "user/profile/profile.html", {"form": form, "success": "Profile updated successfully!"}
            )
    form = ProfileForm(instance=user)
    # in case of a GET
    return render(request, "user/profile/profile.html", {"form": form})


@login_required
def film_stats(request: HttpRequest):
    user = request.user
    if request.method == "POST":
        get_user_watched_films(user)
        get_user_watchlist_films(user)
        chart_data = get_watched_chart_data(user)
        return render(
            request,
            "user/stats/stats.html",
            {"success": "Watchlisted films updated!", "chart_data": json.dumps(chart_data)},
        )
    else:
        # GET
        chart_data = get_watched_chart_data(user)
        return render(request, "user/stats/stats.html", {"chart_data": json.dumps(chart_data)})


@login_required
def preferences(request):
    user_prefs, _ = UserPreference.objects.get_or_create(user=request.user)
    pick_order_form = PickOrderCriteriaForm(instance=user_prefs)
    session_times_form = SessionTimesForm(instance=user_prefs)
    return render(
        request,
        "user/preferences/preferences.html",
        {
            "pick_order_form": pick_order_form,
            "session_times_form": session_times_form,
            "days_of_week": get_days_of_week(),
        },
    )


@login_required
def update_pick_order_criteria(request):
    user_prefs = request.user.preferences
    if request.method == "POST":
        form = PickOrderCriteriaForm(request.POST, instance=user_prefs)
        if form.is_valid():
            form.save()
            messages.success(request, "Pick order criteria updated successfully.")
    return redirect("preferences")


@login_required
def update_session_times(request):
    user_prefs = request.user.preferences
    # unchecked chatgpt code...
    if request.method == "POST":
        session_times_data = {}
        for key, value in request.POST.items():
            if key.startswith("session_times"):
                parts = key.split("[")
                day_num = parts[1][:-1]  # Extract day number
                field = parts[2][:-1]  # Extract field (start/end)
                if day_num not in session_times_data:
                    session_times_data[day_num] = {}
                session_times_data[day_num][field] = int(value)
        user_prefs.session_times = session_times_data
        user_prefs.save()
        messages.success(request, "Session times updated successfully.")
    return redirect("preferences")


# FIXME: give this a better name
@login_required
@require_http_methods(["PATCH"])
def update_filter_preferences(request: HttpRequest):
    user = request.user
    data = json.loads(request.body)
    filter_not_watched = data.get("filter_not_watched")
    filter_watchlisted = data.get("filter_watchlisted")
    filter_with_sessions = data.get("filter_with_sessions")
    UserPreference.objects.get_or_create(user=user)
    if filter_not_watched is not None:
        UserPreference.objects.filter(user=user).update(filter_not_watched=filter_not_watched)
    if filter_watchlisted is not None:
        UserPreference.objects.filter(user=user).update(filter_watchlisted=filter_watchlisted)
    if filter_with_sessions is not None:
        UserPreference.objects.filter(user=user).update(filter_with_sessions=filter_with_sessions)
    return JsonResponse({"success": True})
