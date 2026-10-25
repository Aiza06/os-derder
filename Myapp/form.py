from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Story, StoryRating


class StoryForm(forms.ModelForm):
    """Form for creating and editing stories."""
    
    class Meta:
        model = Story
        fields = [
            "title",
            "author_name",
            "genre",
            "description",
            "chapter",
            "date_published",
            "status",
            "rating",
            "cover_image",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter story title",
                    "autocomplete": "off",
                }
            ),
            "author_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter author name",
                    "autocomplete": "off",
                }
            ),
            "genre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Fantasy, Romance, Mystery...",
                    "autocomplete": "off",
                    "list": "genres-list",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Write a detailed description of your story...",
                }
            ),
            "chapter": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "Current chapter",
                }
            ),
            "date_published": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "rating": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "max": 5,
                    "step": "0.1",
                    "placeholder": "0.0 - 5.0",
                }
            ),
            "cover_image": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }
        labels = {
            "title": "Story Title",
            "author_name": "Author Name",
            "genre": "Genre",
            "description": "Description",
            "chapter": "Current Chapter",
            "date_published": "Publication Date",
            "status": "Story Status",
            "rating": "Rating (0.0 - 5.0)",
            "cover_image": "Cover Image",
        }
    
    def clean_title(self):
        """Validate title is not empty."""
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError("Story title cannot be empty.")
        if len(title) < 3:
            raise ValidationError("Story title must be at least 3 characters long.")
        return title
    
    def clean_author_name(self):
        """Validate author name."""
        author = self.cleaned_data.get('author_name', '').strip()
        if not author:
            raise ValidationError("Author name cannot be empty.")
        return author
    
    def clean_genre(self):
        """Validate genre."""
        genre = self.cleaned_data.get('genre', '').strip()
        if not genre:
            raise ValidationError("Genre cannot be empty.")
        return genre
    
    def clean_description(self):
        """Validate description."""
        description = self.cleaned_data.get('description', '').strip()
        if not description:
            raise ValidationError("Description cannot be empty.")
        if len(description) < 10:
            raise ValidationError("Description must be at least 10 characters long.")
        return description
    
    def clean_rating(self):
        """Validate rating is between 0 and 5."""
        rating = self.cleaned_data.get('rating')
        if rating is not None and (rating < 0 or rating > 5):
            raise ValidationError("Rating must be between 0.0 and 5.0")
        return rating
    
    def clean_cover_image(self):
        """Validate cover image file."""
        cover_image = self.cleaned_data.get('cover_image')
        if cover_image:
            # Check file size (max 5MB)
            if cover_image.size > 5 * 1024 * 1024:
                raise ValidationError("Image file size must not exceed 5MB.")
            
            # Check file format
            allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if cover_image.content_type not in allowed_formats:
                raise ValidationError(
                    "Only JPG, PNG, GIF, and WebP images are allowed."
                )
        return cover_image


class StoryRatingForm(forms.ModelForm):
    """Form for rating stories."""
    
    class Meta:
        model = StoryRating
        fields = ['score', 'review']
        widgets = {
            "score": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "max": 5,
                    "step": "0.5",
                    "placeholder": "0.0",
                }
            ),
            "review": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Write your review (optional)...",
                }
            ),
        }
        labels = {
            "score": "Rating",
            "review": "Your Review",
        }
    
    def clean_score(self):
        """Validate score."""
        score = self.cleaned_data.get('score')
        if score is None:
            raise ValidationError("Please provide a rating.")
        if score < 0 or score > 5:
            raise ValidationError("Rating must be between 0 and 5 stars.")
        return score


class SearchForm(forms.Form):
    """Form for searching and filtering stories."""
    
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search stories, authors, genres...",
                "autocomplete": "off",
            }
        ),
        label="Search",
    )
    genre = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Filter by genre",
                "autocomplete": "off",
            }
        ),
        label="Genre",
    )
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Status'),
            ('Ongoing', 'Ongoing'),
            ('Completed', 'Completed'),
            ('Draft', 'Draft'),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
        label="Status",
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('-date_published', 'Newest First'),
            ('date_published', 'Oldest First'),
            ('-rating', 'Highest Rated'),
            ('-views_count', 'Most Viewed'),
            ('title', 'Title A-Z'),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
        label="Sort By",
    )


class LoginForm(AuthenticationForm):
    """Username and password sign-in form."""

    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your username",
                "autocomplete": "username",
                "autofocus": True,
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your password",
                "autocomplete": "current-password",
            }
        ),
    )

    error_messages = {
        "invalid_login": (
            "That username and password did not match. "
            "Please check both and try again."
        ),
        "inactive": "This account has been disabled.",
    }


class RegisterForm(UserCreationForm):
    """Create a new Novera reader account."""

    first_name = forms.CharField(
        label="First name",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First name",
                "autocomplete": "given-name",
                "autofocus": True,
            }
        ),
    )

    last_name = forms.CharField(
        label="Last name",
        max_length=150,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last name (optional)",
                "autocomplete": "family-name",
            }
        ),
    )

    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Choose a username",
                "autocomplete": "username",
            }
        ),
        help_text="Letters, digits and @/./+/-/_ only.",
    )

    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "you@example.com",
                "autocomplete": "email",
            }
        ),
        help_text="Used to recognise your account. We never share it.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email")
        field_order = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Create a password",
                "autocomplete": "new-password",
            }
        )
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Repeat your password",
                "autocomplete": "new-password",
            }
        )

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("That username is already taken.")

        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                "An account with this email address already exists."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data.get("last_name", "").strip()
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user