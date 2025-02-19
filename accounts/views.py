from django.contrib.auth import login
from django.contrib.auth.views import LoginView as DefaultLoginView
from django.shortcuts import redirect, render

from accounts.forms import RegistrationForm


class LoginView(DefaultLoginView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().get(request, *args, **kwargs)


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})
