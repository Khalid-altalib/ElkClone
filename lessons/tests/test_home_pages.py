from django import forms
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import login, logout
from lessons.models import Request, User
import datetime as dt


class userHomeViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('user_home')
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.user2 = User.objects.create_user(email='test2@example.com', password='password123')
        self.teacher = User.objects.create_user(email='admin@example.com', password='password123', is_staff=True)

        # User creates a request
        self.request = Request.objects.create(
            user=self.user,
            availability="MONDAYAM, TUESDAYPM",
            number_of_lessons=10,
            interval=1,
            duration=45,
            lesson_content="Singing",
            teacher=self.teacher,
            class_Day='MONDAY',
            class_Time=dt.time(8),
            start_Date=dt.date(2021, 1, 1),
        )

        # Second user creates a request
        self.request2 = Request.objects.create(
            user=self.user2,
            availability="MONDAYPM, TUESDAYPM",
            number_of_lessons=10,
            interval=1,
            duration=45,
            lesson_content="Singing",
            teacher=self.teacher,
            class_Day='MONDAY',
            class_Time=dt.time(8),
            start_Date=dt.date(2021, 1, 1),
        )

        self.approved = Request.objects.create(
            user=self.user,
            availability="MONDAYAM, TUESDAYPM",
            number_of_lessons=10,
            interval=1,
            duration=45,
            lesson_content="Dancing",
            teacher=self.teacher,
            class_Day='MONDAY',
            class_Time=dt.time(8),
            start_Date=dt.date(2021, 1, 1),
            isApproved=True
        )

        # Retreives the home page response
        self.client.login(email="test@example.com", password="password123")
        self.response = self.client.get(self.url)
        self.client.logout()

        self.client.login(email="test2@example.com", password="password123")
        self.response2 = self.client.get(self.url)

    def test_url(self):
        self.assertEqual(self.url, '/home/')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_home.html')

    def test_display_pending_reqeusts(self):
        pendingRequest = self.response.context['pending']
        self.assertEquals(len(pendingRequest), 1)
        self.assertEquals(pendingRequest[0].lesson_content, "Singing")

    def test_display_message_when_there_is_no_requests(self):
        approvedRequest = self.response2.context['approved']
        self.assertEquals(len(approvedRequest), 0)
        self.assertContains(self.response2, '<td colspan="4">There are currently requests that have been approved</td>')

    def test_display_approved_requests(self):
        approvedRequest = self.response.context['approved']
        self.assertEquals(len(approvedRequest), 1)
        self.assertEquals(approvedRequest[0].lesson_content, "Dancing")

    def test_does_not_display_other_users_requests(self):
        pendingRequest = self.response.context['pending']
        self.assertNotIn("Monday PM", pendingRequest[0].availability)


class adminHomeViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('admin_home')  # get the url for the admin home page
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.teacher = User.objects.create_user(email='teacher@example.com', password='password123', is_staff=True)
        User.objects.create_user(email='admin@example.com', password='password123', is_staff=True)

        # User creates a request
        self.request = Request.objects.create(
            user=self.user,
            availability="MONDAYAM, TUESDAYPM",
            number_of_lessons=10,
            interval=1,
            duration=45,
            lesson_content="Singing",
            teacher=self.teacher,
            class_Day='MONDAY',
            class_Time=dt.time(8),
            start_Date=dt.date(2021, 1, 1),
        )

        self.approved = Request.objects.create(
            user=self.user,
            availability="MONDAYAM, TUESDAYPM",
            number_of_lessons=10,
            interval=1,
            duration=45,
            lesson_content="Dancing",
            teacher=self.teacher,
            class_Day='MONDAY',
            class_Time=dt.time(8),
            start_Date=dt.date(2021, 1, 1),
            isApproved=True
        )

        # Retreives the home page response
        self.client.login(email="admin@example.com", password="password123")
        self.response = self.client.get(self.url)
        self.client.logout()

    def test_url(self):
        self.assertEqual(self.url, '/administrator/')

    def test_get(self):
        self.client.login(email="admin@example.com", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_home.html')
        self.client.logout()

    def test_display_pending_requests(self):
        pendingRequest = self.response.context['requests']
        self.assertEquals(len(pendingRequest), 1)
        self.assertEquals(pendingRequest[0].lesson_content, "Singing")

    def test_display_approved_requests(self):
        approvedRequest = self.response.context['approved']
        self.assertEquals(len(approvedRequest), 1)
        self.assertEquals(approvedRequest[0].lesson_content, "Dancing")

    def test_does_not_display_other_users_requests(self):
        pendingRequest = self.response.context['requests']
        self.assertNotIn("Monday PM", pendingRequest[0].availability)

    def test_cannot_be_accessed_by_user(self):
        self.client.login(email="test@example.com", password="password123")
        response = self.client.get(self.url)
        response_url = '/log_in?next=/administrator/'
        self.assertRedirects(response, response_url, status_code=302, target_status_code=302)
