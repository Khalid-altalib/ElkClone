from django import forms
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse

from lessons.forms import LogInForm, SignUpForm, RegisterChildForm
from lessons.models import User, Child


class RegisterChildFormTestCase(TestCase):
    def setUp(self):
        self.form_input = {'name': 'A Child'}
        self.user = User.objects.create_user(
            first_name='First',
            last_name='Last',
            email='a@bc.com',
            password='Password123'
        )

    def test_form_contains_required_fields(self):
        form = RegisterChildForm()
        self.assertIn('name', form.fields)

    def test_form_accepts_valid_input(self):
        form = RegisterChildForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_name(self):
        self.form_input['name'] = ''
        form = RegisterChildForm(data=self.form_input)
        self.assertFalse(form.is_valid())


class RegisterChildViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('register_child')
        self.form_input = {
            'name': 'James Bond'
        }
        self.user = User.objects.create_user(
            first_name='Ian',
            last_name='Fleming',
            email='a@bc.com',
            password='Password123'
        )

    def test_url(self):
        self.assertEqual(self.url, '/register_child/')

    def test_get(self):
        self.client.login(email='a@bc.com', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_child.html')
        form = response.context['form']
        self.assertIsInstance(form, RegisterChildForm)

    def test_unsuccessful_registration(self):
        self.client.login(email='a@bc.com', password='Password123')
        self.form_input['name'] = ''
        before_count = Child.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Child.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register_child.html')
        form = response.context['form']
        self.assertIsInstance(form, RegisterChildForm)

    def test_successful_registration(self):
        self.client.login(email='a@bc.com', password='Password123')
        before_count = Child.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Child.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('user_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_home.html')
        child = Child.objects.get(name='James Bond', parent=self.user)
        self.assertNotEqual(child, None)
