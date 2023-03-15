from django import forms
from django.test import TestCase
from django.urls import reverse

from lessons.forms import LogInForm, EditUserForm, EditChildForm
from lessons.models import User, Child


class EditChildFormTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='a@bc.com', password='MyPassword!1')
        self.child = Child.objects.create(name='A Junior', parent=self.user)
        self.form_input = {'name': 'X Æ A-12'}

    def test_form_contains_required_fields(self):
        form = EditChildForm(instance=self.user)
        self.assertIn('name', form.fields)

    def test_form_accepts_valid_input(self):
        form = EditChildForm(instance=self.child, data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_name(self):
        self.form_input['name'] = ''
        form = EditChildForm(instance=self.child, data=self.form_input)
        self.assertFalse(form.is_valid())


class EditChildViewTestCase(TestCase):
    def setUp(self):
        self.form_input = {'name': 'Aaa Bb'}
        self.user_1 = User.objects.create_user(email='a@bc.com', password='MyPassword!1')
        self.user_2 = User.objects.create_user(email='b@bc.com', password='MyPassword!1')
        self.user_3 = User.objects.create_superuser(email='admin@bc.com', password='MyPassword!1')
        self.child = Child.objects.create(name='A B', parent=self.user_1)
        self.url = reverse('edit_child', kwargs={'child_id': self.child.id})

    def test_url(self):
        self.assertEqual(self.url, '/edit_child/' + str(self.child.id) + '/')

    def test_get_logged_out(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url + "?next=" + self.url, status_code=302, target_status_code=200)

    def test_get_logged_in_insufficient_perms(self):
        self.client.login(email='b@bc.com', password='MyPassword!1')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = reverse('user_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_get_logged_in(self):
        self.client.login(email='a@bc.com', password='MyPassword!1')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_child.html')
        form = response.context['form']
        self.assertIsInstance(form, EditChildForm)
        self.assertEqual(form.instance, self.child)

    def test_get_logged_in_superuser(self):
        self.client.login(email='admin@bc.com', password='MyPassword!1')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_child.html')
        form = response.context['form']
        self.assertIsInstance(form, EditChildForm)
        self.assertEqual(form.instance, self.child)

    def test_unsuccessful_submit(self):
        self.client.login(email='a@bc.com', password='MyPassword!1')
        self.form_input['name'] = ''
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_child.html')
        form = response.context['form']
        self.assertIsInstance(form, EditChildForm)

    def test_successful_submit(self):
        self.client.login(email='a@bc.com', password='MyPassword!1')
        form_input = {'name': 'X Æ A-12'}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)


class DeleteChildViewTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create_user(email='a@bc.com', password='MyPassword!1')
        self.user_2 = User.objects.create_user(email='b@bc.com', password='MyPassword!1')
        self.user_3 = User.objects.create_superuser(email='admin@bc.com', password='MyPassword!1')
        self.child = Child.objects.create(name='A B', parent=self.user_1)
        self.url = reverse('delete_child', kwargs={'child_id': self.child.id})

    def test_delete_child(self):
        self.client.login(email='a@bc.com', password='MyPassword!1')
        before_count = Child.objects.count()
        response = self.client.get(self.url, follow=True)
        after_count = Child.objects.count()
        self.assertEqual(after_count, before_count - 1)
        response_url = reverse('user_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_delete_child_superuser(self):
        self.client.login(email='admin@bc.com', password='MyPassword!1')
        before_count = Child.objects.count()
        response = self.client.get(self.url, follow=True)
        after_count = Child.objects.count()
        self.assertEqual(after_count, before_count - 1)
        response_url = reverse('director_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)

    def test_delete_child_logged_out(self):
        before_count = Child.objects.count()
        response = self.client.get(self.url)
        after_count = Child.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('log_in')
        self.assertRedirects(response, response_url + "?next=" + self.url, status_code=302, target_status_code=200)

    def test_delete_user_insufficient_perms(self):
        self.client.login(email='b@bc.com', password='MyPassword!1')
        before_count = Child.objects.count()
        response = self.client.get(self.url)
        after_count = Child.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('user_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
