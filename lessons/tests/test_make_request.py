from django import forms
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import login, logout
from lessons.forms import RequestForm
from lessons.models import Request, User


class RequestFormTestCase(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(email='teacher@example.com', password='password123', is_staff=True)
        self.form_input = {
            'availability': ["MONDAYAM", "TUESDAYPM"],
            'number_of_lessons': 10,
            'interval': 1,
            'duration': 60,
            'lesson_content': "Singing",
            'teacher': self.teacher
        }

    def test_form_contains_required_fields(self):
        form = RequestForm()
        self.assertIn('availability', form.fields)
        self.assertIn('number_of_lessons', form.fields)
        self.assertIn('interval', form.fields)
        self.assertIn('duration', form.fields)
        self.assertIn('lesson_content', form.fields)
        self.assertIn('teacher', form.fields)

    def test_form_accepts_valid_input(self):
        form = RequestForm(data=self.form_input)
        # pdb.set_trace()
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_availability(self):
        self.form_input['availability'] = ''
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_number_of_lessons(self):
        self.form_input['number_of_lessons'] = None
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_interval(self):
        self.form_input['interval'] = None
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_duration(self):
        self.form_input['duration'] = None
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_lesson_content(self):
        self.form_input['lesson_content'] = ''
        form = RequestForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_teacher_can_be_blank(self):
        self.form_input['teacher'] = ''
        form = RequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())


class MakeFormViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('make_request')
        User.objects.create_user(email='test@example.com', password='password123')
        self.form_input = {
            'availability': ["MONDAYAM", "TUESDAYPM"],
            'number_of_lessons': 10,
            'interval': 1,
            'duration': 60,
            'lesson_content': "Singing"
        }

    def test_url(self):
        self.assertEqual(self.url, '/make_request/')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'make_request.html')
        form = response.context['form']
        self.assertIsInstance(form, RequestForm)

    def test_unsuccessful_request(self):
        self.client.login(email="test@example.com", password="password123")
        self.form_input['number_of_lessons'] = ''
        before_count = Request.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'make_request.html')
        form = response.context['form']
        self.assertIsInstance(form, RequestForm)

    def test_successful_request(self):
        self.client.login(email="test@example.com", password="password123")
        before_count = Request.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count + 1)
        response_url = reverse('user_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_home.html')
        request = Request.objects.latest("submission_date")
        self.assertEqual(request.availability, ["MONDAYAM", "TUESDAYPM"])
        self.assertEqual(request.number_of_lessons, 10)
        self.assertEqual(request.interval, 1)
        self.assertEqual(request.duration, 60)
        self.assertEqual(request.lesson_content, "Singing")
        self.assertEqual(request.teacher, None)
