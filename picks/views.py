import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from categories.models import Category
from common.constants import CURRENT_YEAR
from films.models import Film
from picks.models import Pick
from picks.utils import generate_picks
from users.models import User


@login_required
def complete_picks(request: HttpRequest):
    user: User = request.user
    Pick.objects.filter(user=user, year=CURRENT_YEAR, locked=False).delete()
    generate_picks(user)
    return redirect("/")


@login_required
@require_http_methods(["PATCH"])
def set_category_pick(request: HttpRequest):
    data = json.loads(request.body)
    category_id = data.get("category_id")
    film_id = data.get("film_id")
    try:
        category = Category.objects.get(pk=category_id)
    except Category.DoesNotExist:
        return JsonResponse({"success": False, "error": "Category not found"}, status=404)
    try:
        pick = Pick.objects.get(category=category, user=request.user)
        if film_id:
            try:
                film = Film.objects.get(pk=film_id)
            except Film.DoesNotExist:
                return JsonResponse({"success": False, "error": "Film not found"}, status=404)
            pick.film = film
        pick.save()
        return JsonResponse({"success": True})
    except Pick.DoesNotExist:
        try:
            film = Film.objects.get(pk=film_id)
        except Film.DoesNotExist:
            return JsonResponse({"success": False, "error": "Film not found"}, status=404)
        Pick.objects.create(category=category, user=request.user, year=CURRENT_YEAR, film=film)
    return JsonResponse({"success": True})


@login_required
@require_http_methods(["PATCH"])
def toggle_lock(request: HttpRequest):
    data = json.loads(request.body)
    pick_id = data.get("pick_id")
    try:
        pick = Pick.objects.get(pk=pick_id, user=request.user)
    except (Category.DoesNotExist, Pick.DoesNotExist):
        return JsonResponse({"success": False, "error": "Category/Pick not found"}, status=404)
    pick.locked = not pick.locked
    pick.save()
    return JsonResponse({"success": True})
