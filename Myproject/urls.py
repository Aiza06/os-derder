
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from Myapp import views
from Myapp import auth_views


urlpatterns = [
    path(
        "admin/",
        admin.site.urls
    ),

    # Authentication
    path(
        "accounts/login/",
        auth_views.login_view,
        name="login"
    ),

    path(
        "accounts/register/",
        auth_views.register_view,
        name="register"
    ),

    # Friendly alias for the same registration page.
    path(
        "accounts/signup/",
        auth_views.register_view,
        name="signup"
    ),

    path(
        "accounts/logout/",
        auth_views.logout_view,
        name="logout"
    ),

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "story/add/",
        views.story_create,
        name="story_create"
    ),

    path(
        "story/<int:pk>/",
        views.story_detail,
        name="story_detail"
    ),

    path(
        "story/<int:pk>/edit/",
        views.story_edit,
        name="story_edit"
    ),

    # Delete confirmation page
    path(
        "story/<int:pk>/confirm-delete/",
        views.story_confirm_delete,
        name="story_confirm_delete"
    ),

    # Actual permanent deletion
    path(
        "story/<int:pk>/delete/",
        views.story_delete,
        name="story_delete"
    ),

    path(
        "story/<int:pk>/rate/",
        views.add_rating,
        name="add_rating"
    ),
]


# Serve uploaded media during development.
if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
