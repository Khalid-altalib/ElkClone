from django import forms
from django.test import TestCase
from django.urls import reverse

from lessons.forms import LogInForm
from lessons.models import User


class DirectorViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('director_home')
        User.objects.create_user(email='a@bc.com', password='MyPassword!1')
        User.objects.create_superuser(email='director@bc.com', password='MyPassword!1')

    def test_url(self):
        self.assertEqual(self.url, '/director/')

    def test_get_logged_out(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url+"?next="+self.url, status_code=302, target_status_code=200)

    def test_get_logged_in_insufficient_perms(self):
        self.client.login(email='a@bc.com', password='MyPassword!1')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url+"?next="+self.url, status_code=302, target_status_code=302)

    def test_get(self):
        self.client.login(email='director@bc.com', password='MyPassword!1')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'director_home.html')
        self.assertIsInstance(response.context['users'], list)
        self.assertNotEqual(response.context['requests'], None)
        self.assertNotEqual(response.context['approved'], None)

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()
