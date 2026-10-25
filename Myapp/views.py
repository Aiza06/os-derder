
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest

from .form import StoryForm, StoryRatingForm, SearchForm
from .models import Story, StoryView, StoryRating


def get_client_ip(request: HttpRequest) -> str:
    """Get the client's IP address."""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def get_featured_stories():
    """Return the three highest-rated stories."""
    return Story.objects.top_rated()[:3]


@login_required
def home(request):
    """Display the home page with stories, search and filters."""
    query = request.GET.get("q", "").strip()
    genre = request.GET.get("genre", "").strip()
    status = request.GET.get("status", "").strip()
    sort_by = request.GET.get("sort_by", "-date_published").strip()

    stories = Story.objects.all()

    if query:
        stories = stories.filter(
            Q(title__icontains=query)
            | Q(author_name__icontains=query)
            | Q(description__icontains=query)
            | Q(genre__icontains=query)
        )

    if genre:
        stories = stories.filter(genre__iexact=genre)

    if status:
        stories = stories.filter(status__iexact=status)

    valid_sorts = [
        "-date_published",
        "date_published",
        "-rating",
        "-views_count",
        "title",
    ]

    if sort_by in valid_sorts:
        stories = stories.order_by(sort_by)
    else:
        stories = stories.order_by("-date_published", "-id")

    paginator = Paginator(stories, 12)

    try:
        stories = paginator.page(request.GET.get("page", 1))
    except PageNotAnInteger:
        stories = paginator.page(1)
    except EmptyPage:
        stories = paginator.page(paginator.num_pages)

    genres = (
        Story.objects.values_list("genre", flat=True)
        .distinct()
        .order_by("genre")
    )

    context = {
        "stories": stories,
        "featured": get_featured_stories(),
        "genres": genres,
        "search_form": SearchForm(
            initial={
                "query": query,
                "genre": genre,
                "status": status,
                "sort_by": sort_by,
            }
        ),
        "query": query,
        "selected_genre": genre,
        "selected_status": status,
        "sort_by": sort_by,
    }

    return render(request, "Myapp/home.html", context)


def story_detail(request, pk):
    """Display a story's details and ratings."""
    story = get_object_or_404(Story, pk=pk)

    StoryView.objects.create(
        story=story,
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:200],
    )
    story.increment_views()

    ratings = story.ratings.all()[:5]
    avg_rating = ratings.aggregate(Avg("score"))["score__avg"] or 0

    related_stories = (
        Story.objects.filter(genre__iexact=story.genre)
        .exclude(pk=story.pk)
        .order_by("-rating")[:3]
    )

    context = {
        "story": story,
        "ratings": ratings,
        "avg_rating": avg_rating,
        "rating_form": StoryRatingForm() if request.user.is_authenticated else None,
        "related_stories": related_stories,
    }

    return render(request, "Myapp/story_detail.html", context)


@login_required
def story_create(request):
    """
    Create a story.

    The Home page uses the separate story form.
    The Dashboard submits its popup form to this same view.
    """
    if request.method == "POST":
        form = StoryForm(request.POST, request.FILES)

        if form.is_valid():
            story = form.save()

            messages.success(
                request,
                f'Story "{story.title}" was created successfully!',
            )

            if request.POST.get("next") == "dashboard":
                return redirect("dashboard")

            return redirect("story_detail", pk=story.pk)

        if request.POST.get("next") == "dashboard":
            # Store a useful error message before returning.
            messages.error(
                request,
                "The story could not be saved. Please check the required fields.",
            )
            return redirect("dashboard")

        messages.error(
            request,
            "Please correct the errors in the form.",
        )
    else:
        form = StoryForm()

    context = {
        "form": form,
        "page_title": "Add New Story",
        "action": "Create",
    }

    return render(request, "Myapp/story_form.html", context)


@login_required
def story_edit(request, pk):
    """Edit an existing story."""
    story = get_object_or_404(Story, pk=pk)

    if request.method == "POST":
        form = StoryForm(request.POST, request.FILES, instance=story)

        if form.is_valid():
            updated_story = form.save()
            messages.success(
                request,
                f'Story "{updated_story.title}" was updated successfully!',
            )
            return redirect("story_detail", pk=updated_story.pk)
    else:
        form = StoryForm(instance=story)

    context = {
        "form": form,
        "page_title": "Edit Story",
        "story": story,
        "action": "Edit",
    }

    return render(request, "Myapp/story_form.html", context)


@login_required
@require_http_methods(["POST"])
def story_delete(request, pk):
    """Permanently delete a story."""
    story = get_object_or_404(Story, pk=pk)
    title = story.title
    story.delete()

    messages.success(
        request,
        f'Story "{title}" was deleted successfully.',
    )

    return redirect("home")


@login_required
def story_confirm_delete(request, pk):
    """Show the story deletion confirmation page."""
    story = get_object_or_404(Story, pk=pk)
    return render(
        request,
        "Myapp/story_confirm_delete.html",
        {"story": story},
    )


@login_required
def add_rating(request, pk):
    """Add a rating to a story."""
    story = get_object_or_404(Story, pk=pk)

    if request.method != "POST":
        return redirect("story_detail", pk=pk)

    form = StoryRatingForm(request.POST)

    if form.is_valid():
        rating = form.save(commit=False)
        rating.story = story
        rating.save()
        messages.success(request, "Your rating has been added!")
    else:
        messages.error(request, "Please enter a valid rating.")

    return redirect("story_detail", pk=pk)


@login_required
def dashboard(request):
    """Display dashboard statistics and the Add Story popup form."""
    stories = Story.objects.all()

    total_stories = stories.count()
    ongoing_count = stories.filter(status="Ongoing").count()
    completed_count = stories.filter(status="Completed").count()
    draft_count = stories.filter(status="Draft").count()

    top_stories = (
        stories.annotate(rating_avg=Avg("ratings__score"))
        .order_by("-rating", "-views_count")[:5]
    )

    most_viewed = stories.order_by("-views_count")[:5]

    genre_stats = (
        stories.values("genre")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    total_views = sum(story.views_count for story in stories)
    avg_rating = stories.aggregate(Avg("rating"))["rating__avg"] or 0

    context = {
        "total_stories": total_stories,
        "ongoing_count": ongoing_count,
        "completed_count": completed_count,
        "draft_count": draft_count,
        "top_stories": top_stories,
        "most_viewed": most_viewed,
        "genre_stats": genre_stats,
        "total_views": total_views,
        "avg_rating": avg_rating,
        "form": StoryForm(),
    }

    return render(request, "Myapp/dashboard.html", context)