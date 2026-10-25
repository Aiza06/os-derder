from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .form import LoginForm, RegisterForm
from .models import Story


def _safe_redirect_target(request, fallback):
    """Return a local ``next`` URL, or the fallback route name."""
    candidate = request.POST.get("next") or request.GET.get("next")

    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate

    return fallback


def _display_name(user):
    return user.get_short_name() or user.get_full_name() or user.username


def login_view(request):
    """Sign an existing reader in."""
    if request.user.is_authenticated:
        return redirect("home")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            messages.success(
                request,
                f"Welcome back, {_display_name(user)}. Your shelf is ready.",
            )

            return redirect(_safe_redirect_target(request, "home"))

    return render(
        request,
        "Myapp/auth/login.html",
        {
            "form": form,
            "next": request.GET.get("next", ""),
            "story_preview": Story.objects.top_rated()[:3],
        },
    )


def register_view(request):
    """Create a new account and sign the reader in straight away."""
    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                f"Your account is ready, {_display_name(user)}. "
                "Add your first story to begin.",
            )

            return redirect(_safe_redirect_target(request, "home"))

    return render(
        request,
        "Myapp/auth/register.html",
        {
            "form": form,
            "next": request.GET.get("next", ""),
            "story_preview": Story.objects.top_rated()[:3],
        },
    )


@require_POST
def logout_view(request):
    """Sign the current reader out. Logging out is POST-only."""
    logout(request)
    messages.success(request, "You have been signed out. See you soon.")
    return redirect("login")
