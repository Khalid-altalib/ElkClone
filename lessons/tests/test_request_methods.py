from django import forms
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import login, logout
from lessons.forms import EditRequestForm
from lessons.models import Request, User


class seeMoreViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.user2 = User.objects.create_user(email='test2@example.com', password='password123')
        self.teacher = User.objects.create_user(first_name="A", last_name="B", email='teacher@example.com', password='password123', is_staff=True)

        #User creates a request
        self.request = Request.objects.create(
            user=self.user,
            availability="MONDAYAM, TUESDAYPM",
            number_of_lessons=10,
            interval=1,
            duration=45,
            lesson_content="Singing",
            teacher=self.teacher,
        )
        requestId = self.request.request_id
        self.url = '/see_more/' + str(requestId)

        #Retreives the home page response
        self.client.login(email="test@example.com", password="password123")
        self.response = self.client.get(self.url)

    def test_get(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'see_more_request.html')

    def test_user_can_see_more(self):
        self.assertContains(self.response, "<td>Monday AM, Tuesday PM</td>")
        self.assertContains(self.response, "<td>10</td>")
        self.assertContains(self.response, "<td>1</td>")
        self.assertContains(self.response, "<td>45</td>")
        self.assertContains(self.response, "<td>Singing</td>")
        self.assertContains(self.response, "<td>A B</td>")
        self.assertContains(self.response, "<td>No</td>")

    def test_user_can_only_see_more_their_own_request(self):
        self.client.logout()
        self.client.login(email="test2@example.com", password="password123")
        response = self.client.get(self.url)
        response_url = reverse('user_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.client.logout()

class editViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.user2 = User.objects.create_user(email='test2@example.com', password='password123')

        #User creates a request
        self.request = Request.objects.create(
            user=self.user,
            availability="MONDAYAM, TUESDAYPM",
            number_of_lessons=10,
            interval=1,
            duration=45,
            lesson_content="Singing",
            teacher=None,
        )

        self.form_input = {
            'availability': ["TUESDAYAM"],
            'number_of_lessons': 10,
            'interval': 1,
            'duration': 60,
            'lesson_content': "Dancing"
        }

        requestId = self.request.request_id
        self.url = '/edit/' + str(requestId)

    def test_get(self):
        self.client.login(email="test@example.com", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'make_request.html')
        form = response.context['form']
        self.assertIsInstance(form, EditRequestForm)
        self.client.logout()

    def test_unsuccessful_edit_request(self):
        self.client.login(email="test@example.com", password="password123")
        self.form_input['number_of_lessons'] = ''
        before_count = Request.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'make_request.html')
        form = response.context['form']
        self.assertIsInstance(form, EditRequestForm)
        self.client.logout

    def test_successful_edit_request(self):
        self.client.login(email="test@example.com", password="password123")
        before_count = Request.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('user_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_home.html')

        request = Request.objects.latest("submission_date")
        self.assertEqual(request.availability, ["TUESDAYAM"])
        self.assertEqual(request.number_of_lessons, 10)
        self.assertEqual(request.interval, 1)
        self.assertEqual(request.duration, 60)
        self.assertEqual(request.lesson_content, "Dancing")
        self.assertEqual(request.teacher, None)
        self.client.logout()

    def test_user_can_only_see_more_their_own_request(self):
        self.client.logout()
        self.client.login(email="test2@example.com", password="password123")
        response = self.client.get(self.url)
        response_url = reverse('user_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.client.logout()

class deleteViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.user2 = User.objects.create_user(email='test2@example.com', password='password123')
        User.objects.create_user(email='admin@example.com', password='password123', is_staff=True)

        #User creates a request
        self.request = Request.objects.create(
            user=self.user,
            availability="MONDAYAM, TUESDAYPM",
            number_of_lessons=10,
            interval=1,
            duration=45,
            lesson_content="Singing",
            teacher=None
        )

        #Another user creates a request
        self.request2 = Request.objects.create(
            user=self.user,
            availability="MONDAYAM, TUESDAYPM",
            number_of_lessons=10,
            interval=1,
            duration=45,
            lesson_content="Singing",
            teacher=None,
            isApproved = True
        )

        #User creates another request
        self.request3 = Request.objects.create(
            user=self.user,
            availability="MONDAYAM, TUESDAYPM",
            number_of_lessons=10,
            interval=1,
            duration=45,
            lesson_content="Singing",
            teacher=None
        )

        self.url = f'/delete/{self.request.request_id}/'
        self.url2 = f'/delete/{self.request2.request_id}/'
        self.url3 =f'/delete/{self.request3.request_id}/'

    def test_request_is_deleted(self):
        self.client.login(email="test@example.com", password="password123")
        before_count = Request.objects.count()
        response = self.client.get(self.url3)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count - 1)
        response_url = reverse('user_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.client.logout()

    def test_cannot_delete_approved_requests(self):
        self.client.login(email="test2@example.com", password="password123")
        before_count = Request.objects.count()
        response = self.client.get(self.url2)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('user_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.client.logout()

    def test_user_can_only_delete_their_own_request(self):
        self.client.login(email="test2@example.com", password="password123")
        before_count = Request.objects.count()
        response = self.client.get(self.url)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('user_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.client.logout()

    def test_admin_can_delete_any_request(self):
        self.client.login(email="admin@example.com", password="password123")
        before_count = Request.objects.count()
        response = self.client.get(self.url)
        after_count = Request.objects.count()
        self.assertEqual(after_count, before_count - 1)
        response_url = reverse('admin_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.client.logout()
