
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class StoryQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status="Completed")

    def ongoing(self):
        return self.filter(status="Ongoing")

    def recent(self):
        return self.order_by("-date_published", "-id")

    def top_rated(self):
        return self.order_by("-rating", "-views_count")

    def with_stats(self):
        return self.annotate(
            average_rating=models.Avg("ratings__score"),
            total_views=models.Count("views"),
        )


class StoryManager(models.Manager):
    def get_queryset(self):
        return StoryQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

    def ongoing(self):
        return self.get_queryset().ongoing()

    def recent(self):
        return self.get_queryset().recent()

    def top_rated(self):
        return self.get_queryset().top_rated()

    def with_stats(self):
        return self.get_queryset().with_stats()


class Story(models.Model):
    """Model representing a story/book."""

    STATUS_CHOICES = [
        ("Ongoing", "Ongoing"),
        ("Completed", "Completed"),
        ("Draft", "Draft"),
    ]

    title = models.CharField(
        max_length=200,
        help_text="Title of the story",
    )

    author_name = models.CharField(
        max_length=200,
        help_text="Author's name",
    )

    genre = models.CharField(
        max_length=100,
        help_text="Story genre",
    )

    description = models.TextField(
        help_text="Brief description of the story",
    )

    chapter = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Current chapter number",
    )

    date_published = models.DateField(
        help_text="Publication date",
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="Draft",
        help_text="Current status of the story",
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0),
        ],
        help_text="Average rating (0.0 - 5.0)",
    )

    cover_image = models.ImageField(
        upload_to="covers/",
        blank=True,
        null=True,
        help_text="Cover image for the story",
    )

    views_count = models.IntegerField(
        default=0,
        help_text="Number of times this story has been viewed",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the story was created",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the story was last updated",
    )

    objects = StoryManager()

    class Meta:
        ordering = ["-date_published", "-id"]
        indexes = [
            models.Index(
                fields=["status", "-date_published"]
            ),
            models.Index(
                fields=["genre"]
            ),
            models.Index(
                fields=["-rating"]
            ),
        ]
        verbose_name_plural = "Stories"

    def __str__(self):
        return self.title

    def increment_views(self):
        """Increment the view count."""
        self.views_count += 1
        self.save(update_fields=["views_count"])

    @property
    def is_published(self):
        return self.status == "Completed"

    @property
    def is_ongoing(self):
        return self.status == "Ongoing"

    def get_status_display_color(self):
        colors = {
            "Ongoing": "primary",
            "Completed": "success",
            "Draft": "secondary",
        }
        return colors.get(self.status, "secondary")

    def delete(self, *args, **kwargs):
        """
        Permanently delete the story and its uploaded cover image.
        Related StoryRating and StoryView records are also deleted
        because their ForeignKeys use on_delete=models.CASCADE.
        """

        # Save the image name before deleting the database record.
        image_name = self.cover_image.name if self.cover_image else None

        # Delete the Story from the database.
        result = super().delete(*args, **kwargs)

        # Delete the actual image file from media/covers/.
        if image_name:
            try:
                self.cover_image.storage.delete(image_name)
            except Exception:
                # Database deletion should not fail because of
                # a missing/unavailable image file.
                pass

        return result


class StoryView(models.Model):
    """Track story views for analytics."""

    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name="views",
    )

    viewed_at = models.DateTimeField(
        auto_now_add=True
    )

    user_agent = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-viewed_at"]
        indexes = [
            models.Index(
                fields=["story", "-viewed_at"]
            ),
        ]

    def __str__(self):
        return f"{self.story.title} - {self.viewed_at}"


class StoryRating(models.Model):
    """User ratings for stories."""

    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name="ratings",
    )

    score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0),
        ],
    )

    review = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["story"]
            ),
        ]

    def __str__(self):
        return f"{self.story.title} - {self.score}/5"

