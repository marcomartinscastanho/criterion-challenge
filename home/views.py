from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as DefaultLoginView
from django.shortcuts import redirect, render


@login_required
def home(request):
    return render(request, "home.html")


@login_required
def test(request):  # XXX: remove
    return render(request, "test.html")


class LoginView(DefaultLoginView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().get(request, *args, **kwargs)
