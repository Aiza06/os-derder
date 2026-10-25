import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Story


class AuthenticationTests(TestCase):
    """Sign-up, sign-in and sign-out behaviour."""

    password = "NoveraTest!2026"

    def setUp(self):
        self.user = User.objects.create_user(
            username="reader",
            email="reader@example.com",
            password=self.password,
            first_name="Rae",
        )

    def test_library_requires_login(self):
        response = self.client.get(reverse("home"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('home')}",
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}",
        )

    def test_register_creates_an_account_and_signs_in(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "username": "ada",
                "email": "ada@example.com",
                "password1": self.password,
                "password2": self.password,
            },
        )

        self.assertRedirects(response, reverse("home"))

        account = User.objects.get(username="ada")
        self.assertEqual(account.first_name, "Ada")
        self.assertEqual(account.email, "ada@example.com")
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            account.pk,
        )

    def test_register_rejects_duplicate_username_and_email(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Another",
                "username": "reader",
                "email": "other@example.com",
                "password1": self.password,
                "password2": self.password,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already taken")

        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Another",
                "username": "another",
                "email": "reader@example.com",
                "password1": self.password,
                "password2": self.password,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {"username": "reader", "password": self.password},
        )

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {"username": "reader", "password": "not-the-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "did not match")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_honours_local_next_and_ignores_external_next(self):
        response = self.client.post(
            f"{reverse('login')}?next={reverse('dashboard')}",
            {"username": "reader", "password": self.password},
        )
        self.assertRedirects(response, reverse("dashboard"))

        self.client.post(reverse("logout"))

        response = self.client.post(
            reverse("login"),
            {
                "username": "reader",
                "password": self.password,
                "next": "https://evil.example.com/",
            },
        )
        self.assertEqual(response.url, reverse("home"))

    def test_logout_requires_post_and_ends_the_session(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_anonymous_reader_sees_sign_in_prompt_instead_of_rating_form(self):
        story = Story.objects.create(
            title="A Test Story",
            author_name="A Writer",
            genre="Fantasy",
            description="A small story used by the test suite.",
            date_published=datetime.date(2026, 1, 1),
        )

        response = self.client.get(reverse("story_detail", args=[story.pk]))
        self.assertContains(response, "Log in to leave a rating")
        self.assertNotContains(response, "Leave a rating")

        self.client.force_login(self.user)

        response = self.client.get(reverse("story_detail", args=[story.pk]))
        self.assertContains(response, "Leave a rating")
        self.assertNotContains(response, "Log in to leave a rating")
