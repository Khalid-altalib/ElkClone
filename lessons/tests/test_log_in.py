from django import forms
from django.test import TestCase
from django.urls import reverse

from lessons.forms import LogInForm
from lessons.models import User


class LogInFormTestCase(TestCase):
    def setUp(self):
        self.form_input = {'email': 'a@bc.com', 'password': 'MyPassword!1'}

    def test_form_contains_required_fields(self):
        form = LogInForm()
        self.assertIn('email', form.fields)
        self.assertIn('password', form.fields)
        self.assertIsInstance(form.fields['password'].widget, forms.PasswordInput)

    def test_form_accepts_valid_input(self):
        form = LogInForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_email(self):
        self.form_input['email'] = ''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_password(self):
        self.form_input['password'] = ''
        form = LogInForm(data=self.form_input)
        self.assertFalse(form.is_valid())


class LogInViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('log_in')
        self.form_input = {'email': 'a@bc.com', 'password': 'MyPassword!1'}
        User.objects.create_user(email='a@bc.com', password='MyPassword!1')
        User.objects.create_user(email='admin@bc.com', password='MyPassword!1', is_staff=True)
        User.objects.create_superuser(email='director@bc.com', password='MyPassword!1')

    def test_url(self):
        self.assertEqual(self.url, '/log_in')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertIsInstance(form, LogInForm)

    def test_unsuccessful_log_in(self):
        self.form_input['email'] = 'invalid email'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertIsInstance(form, LogInForm)
        self.assertFalse(self._is_logged_in())

    def test_successful_log_in(self):
        form_input = {'email': 'a@bc.com', 'password': 'MyPassword!1'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('user_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_home.html')

    def test_successful_admin_log_in(self):
        form_input = {'email': 'admin@bc.com', 'password': 'MyPassword!1'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('admin_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_home.html')

    def test_successful_director_log_in(self):
        form_input = {'email': 'director@bc.com', 'password': 'MyPassword!1'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('director_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'director_home.html')

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()
