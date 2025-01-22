from time import sleep

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render

from criterionchallenge.constants import CURRENT_YEAR
from picks.models import Pick


@login_required
def picks(request: HttpRequest):
    user = request.user
    # if not user.challenge_complete:
    #     pass
    picks = Pick.objects.filter(user=user).filter(year=CURRENT_YEAR)

    sleep(1)
    return render(request, "picks.html", {"picks": picks})
