from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect, render

from common.templatetags.common_extras import more_than_a_month_ago
from users.models import User, UserWatched, UserWatchlist


@login_required
def home(request: HttpRequest):
    user = User.objects.get(pk=request.user.pk)
    if not user.date_of_birth:
        messages.warning(request, "You need to set your birth date. Go to Profile.")
    try:
        watched = UserWatched.objects.get(user=user)
        watchlist = UserWatchlist.objects.get(user=user)
        if not watched or not watchlist:
            messages.warning(request, "You need to refresh your film stats. Go to Profile > Stats.")
        if more_than_a_month_ago(watched.updated_at) or more_than_a_month_ago(watchlist.updated_at):
            messages.warning(request, "You haven't updated your film stats in a while...")
    except (UserWatched.DoesNotExist, UserWatchlist.DoesNotExist):
        messages.warning(request, "You need to refresh your film stats. Go to Profile > Stats.")
    if not messages.get_messages(request):
        return redirect("categories")
    return render(request, "home.html")
