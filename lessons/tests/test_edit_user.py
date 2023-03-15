from django import forms
from django.test import TestCase
from django.urls import reverse

from lessons.forms import LogInForm, EditUserForm
from lessons.models import User


class EditUserFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='a@bc.com', password='MyPassword!1')
        self.form_input = {'email': 'a@bc.com', 'first_name': 'changed name'}

    def test_form_contains_required_fields(self):
        form = EditUserForm(instance=self.user)
        self.assertIn('email', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('is_staff', form.fields)
        self.assertIn('is_superuser', form.fields)

    def test_form_accepts_valid_input(self):
        form = EditUserForm(instance=self.user, data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_email(self):
        self.form_input['email'] = ''
        form = EditUserForm(instance=self.user, data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_staff_fields_are_enabled_for_non_superuser(self):
        form = EditUserForm(instance=self.user, data=self.form_input)
        self.assertFalse(form.fields['is_staff'].disabled)
        self.assertFalse(form.fields['is_superuser'].disabled)

    def test_staff_fields_are_disabled_for_superuser(self):
        form = EditUserForm(instance=User.objects.create_superuser(email='superuser@bc.com', password='MyPassword!1'),
                            data=self.form_input)
        self.assertTrue(form.fields['is_staff'].disabled)
        self.assertTrue(form.fields['is_superuser'].disabled)


class EditUserViewTestCase(TestCase):
    def setUp(self):
        self.form_input = {'email': 'a@bc.com'}
        self.user_1 = User.objects.create_user(email='a@bc.com', password='MyPassword!1')
        self.user_2 = User.objects.create_superuser(email='admin@bc.com', password='MyPassword!1')
        self.url = reverse('edit_user', kwargs={'user_id': self.user_1.id})

    def test_url(self):
        self.assertEqual(self.url, '/edit_user/' + str(self.user_1.id) + '/')

    def test_get_logged_out(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url + "?next=" + self.url, status_code=302, target_status_code=200)

    def test_get_logged_in_insufficient_perms(self):
        self.client.login(email='a@bc.com', password='MyPassword!1')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url + "?next=" + self.url, status_code=302, target_status_code=302)

    def test_get_logged_in(self):
        self.client.login(email='admin@bc.com', password='MyPassword!1')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_user.html')
        form = response.context['form']
        self.assertIsInstance(form, EditUserForm)
        self.assertEqual(form.instance, self.user_1)

    def test_unsuccessful_submit(self):
        self.client.login(email='admin@bc.com', password='MyPassword!1')
        self.form_input['email'] = 'invalid email'
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_user.html')
        form = response.context['form']
        self.assertIsInstance(form, EditUserForm)

    def test_successful_submit(self):
        self.client.login(email='admin@bc.com', password='MyPassword!1')
        form_input = {'email': 'a@bc.com'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)


class DeleteUserViewTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(email='a@bc.com', password='MyPassword!1')
        self.user_2 = User.objects.create_superuser(email='admin@bc.com', password='MyPassword!1')
        self.url = reverse('delete_user', kwargs={'user_id': self.user_1.id})

    def test_delete_user(self):
        self.client.login(email='admin@bc.com', password='MyPassword!1')
        before_count = User.objects.count()
        response = self.client.get(self.url, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count - 1)
        response_url = reverse('director_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_delete_user_logged_out(self):
        before_count = User.objects.count()
        response = self.client.get(self.url)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url + "?next=" + self.url, status_code=302, target_status_code=200)

    def test_delete_user_insufficient_perms(self):
        self.client.login(email='a@bc.com', password='MyPassword!1')
        before_count = User.objects.count()
        response = self.client.get(self.url)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url + "?next=" + self.url, status_code=302, target_status_code=302)
