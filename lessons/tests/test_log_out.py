from django import forms
from django.test import TestCase
from django.urls import reverse

from lessons.forms import LogInForm
from lessons.models import User


class LogOutViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('log_out')
        User.objects.create_user(email='a@bc.com', password='MyPassword!1')
        self.client.login(email='a@bc.com', password='MyPassword!1')

    def test_url(self):
        self.assertEqual(self.url, '/log_out')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_successful_log_out(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self._is_logged_in())

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()
