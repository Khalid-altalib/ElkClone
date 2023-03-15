from django import forms
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse

from lessons.forms import LogInForm, SignUpForm
from lessons.models import User


class SignUpFormTestCase(TestCase):
    def setUp(self):
        self.form_input = {'email': 'a@bc.com', 'first_name': 'Anthony', 'last_name': 'Crowley',
                           'password': 'MyPassword!1', 'password_confirmation': 'MyPassword!1'}

    def test_form_contains_required_fields(self):
        form = SignUpForm()
        self.assertIn('email', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('password', form.fields)
        self.assertIn('password_confirmation', form.fields)
        self.assertIsInstance(form.fields['password'].widget, forms.PasswordInput)
        self.assertIsInstance(form.fields['password_confirmation'].widget, forms.PasswordInput)

    def test_form_accepts_valid_input(self):
        form = SignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_email(self):
        self.form_input['email'] = ''
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_password(self):
        self.form_input['password'] = ''
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_non_matching_passwords(self):
        self.form_input['password'] = 'MyPassword!2'
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_first_name_can_be_blank(self):
        self.form_input['first_name'] = ''
        form = SignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_last_name_can_be_blank(self):
        self.form_input['last_name'] = ''
        form = SignUpForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_password_cannot_be_under_8_chars(self):
        self.form_input['password'] = 'a' * 7
        self.form_input['password_confirmation'] = 'a' * 7
        form = SignUpForm(data=self.form_input)
        self.assertFalse(form.is_valid())


class SignUpViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'first_name': 'Adam',
            'last_name': 'Adamson',
            'email': 'a@aa.com',
            'password': 'MyNameIsAdam!1',
            'password_confirmation': 'MyNameIsAdam!1',
        }

    def test_url(self):
        self.assertEqual(self.url, '/sign_up')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertIsInstance(form, SignUpForm)

    def test_unsuccessful_sign_up(self):
        self.form_input['email'] = 'invalid email'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertIsInstance(form, SignUpForm)

    def test_successful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('user_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_home.html')
        user = User.objects.get(email='a@aa.com')
        self.assertEqual(user.first_name, 'Adam')
        self.assertEqual(user.last_name, 'Adamson')
        self.assertEqual(user.email, 'a@aa.com')
        is_password_correct = check_password('MyNameIsAdam!1', user.password)
        self.assertTrue(is_password_correct)
