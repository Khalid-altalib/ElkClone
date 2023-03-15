from django import forms
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import login, logout
from lessons.forms import ApproveForm, RequestForm
from lessons.models import Request, User, Invoice, Child
import datetime as dt
from django.test.client import RequestFactory
from decimal import Decimal


class ApproveFormTestCase(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(first_name='A', last_name='B', email='admin@bc.com',
                                                password='Password123', is_staff=True)
        self.form_input = {
            'number_of_lessons': 10,
            'interval': 1,
            'duration': 60,
            'lesson_content': "Singing",
            'teacher': self.teacher,
            'class_Day': 'MONDAY',
            'class_Time': dt.time(8),
            'start_Date': dt.date(2021, 1, 1)
        }

    def test_form_contains_required_fields(self):
        form = ApproveForm()
        self.assertIn('number_of_lessons', form.fields)
        self.assertIn('interval', form.fields)
        self.assertIn('duration', form.fields)
        self.assertIn('lesson_content', form.fields)
        self.assertIn('teacher', form.fields)
        self.assertIn('class_Day', form.fields)
        self.assertIn('class_Time', form.fields)
        self.assertIn('start_Date', form.fields)

    def test_form_accepts_valid_input(self):
        form = ApproveForm(data=self.form_input)
        # pdb.set_trace()
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_number_of_lessons(self):
        self.form_input['number_of_lessons'] = None
        form = ApproveForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_interval(self):
        self.form_input['interval'] = None
        form = ApproveForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_duration(self):
        self.form_input['duration'] = None
        form = ApproveForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_lesson_content(self):
        self.form_input['lesson_content'] = ''
        form = ApproveForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_teacher_can_be_blank(self):
        self.form_input['teacher'] = ''
        form = ApproveForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_rejects_blank_class_day(self):
        self.form_input['class_Day'] = ''
        form = ApproveForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_class_time(self):
        self.form_input['class_Time'] = ''
        form = ApproveForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_class_date(self):
        self.form_input['start_Date'] = ''
        form = ApproveForm(data=self.form_input)
        self.assertFalse(form.is_valid())


class ApproveRequestViewTestCase(TestCase):
    def setUp(self):

        self.teacher = User.objects.create_user(first_name='Pinky', last_name='Dinky', email='admin@bcmail.com',
                                                password='Password123', is_staff=True)
        self.student1 = User.objects.create_user(email='test2@example.com', password='password123')
        self.student2 = User.objects.create_user(email='student2@example.com', password='password123')
        self.child = Child.objects.create(name="Small Human", parent=self.student2)
        self.request1 = Request.objects.create(user=self.student1, availability="MONDAYAM, TUESDAYPM",
                                               number_of_lessons=10, interval=1, duration=60, lesson_content="Piano",
                                               teacher=self.teacher, isApproved=True)
        self.request2 = Request.objects.create(user=self.student2, availability="MONDAYAM, TUESDAYPM", child=self.child,
                                               number_of_lessons=20, interval=2, duration=45, lesson_content="Ukelele",
                                               teacher=None)

        self.request3 = Request.objects.create(user=self.student2, availability="MONDAYAM, TUESDAYPM",
                                               number_of_lessons=20, interval=2, duration=45, lesson_content="Ukelele",
                                               teacher=None)

        self.form_input1 = {
            'number_of_lessons': 20,
            'interval': 1,
            'duration': 60,
            'lesson_content': "Singing",
            'teacher': 1,
            'class_Day': "MONDAY",
            'class_Time': dt.time(8),
            'start_Date': dt.date(2021, 1, 1)
        }

        inv_num = str(self.request1.user.id).zfill(4) + '-001'  # First invoice for this user
        self.invoice1 = Invoice.objects.create(request=self.request1,
                                               amount_to_be_paid=self.request1.get_total_amount_payable(),
                                               invoice_number=inv_num)
        self.request1.invoice = self.invoice1
        self.requestId1 = self.request1.request_id
        self.requestId2 = self.request2.request_id
        self.requestId3 = self.request3.request_id
        self.url1 = reverse('approve', kwargs={'requestId': self.requestId1})
        self.url2 = reverse('approve', kwargs={'requestId': self.requestId2})
        self.url3 = reverse('approve', kwargs={'requestId': self.requestId3})

    def test_get(self):
        self.client.login(email="admin@bcmail.com", password="Password123")
        response = self.client.get(self.url1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'approve_request.html')
        form = response.context['form']
        self.assertIsInstance(form, ApproveForm)
        self.client.logout()

    def test_unauthorised_access(self):
        self.client.login(email="test2@example.com", password="password123")
        response = self.client.get(self.url1, follow=True)
        response_url = reverse('user_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'user_home.html')
        self.client.logout()

    def test_valid_edit(self):
        self.client.login(email="admin@bcmail.com", password="Password123")
        beforeCost = Request.objects.get(pk=self.requestId1).get_total_amount_payable()
        print(Request.objects.get(pk=self.requestId1).invoice)
        self.assertEqual(beforeCost, 6000)
        response = self.client.post(self.url1, self.form_input1, follow=True)
        print(Request.objects.get(pk=self.requestId1).invoice)
        afterCost = Request.objects.get(pk=self.requestId1).get_total_amount_payable()
        self.assertEqual(afterCost, 12000)
        self.assertEqual(beforeCost * 2, afterCost)
        response_url = reverse('admin_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_home.html')
        self.client.logout()

    def test_valid_post(self):
        self.client.login(email="admin@bcmail.com", password="Password123")
        beforeInvoiceValue = Request.objects.get(request_id=self.requestId2).invoice
        self.assertIsNone(beforeInvoiceValue)
        response = self.client.post(self.url2, self.form_input1, follow=True)
        afterInvoiceValue = response.context['invoices'].last()

        self.assertIsNotNone(afterInvoiceValue)
        self.assertEqual(afterInvoiceValue.amount_to_be_paid, self.request2.get_total_amount_payable())
        self.assertEqual(afterInvoiceValue.invoice_number, str(self.request2.user.id).zfill(4) + '-001')
        response_url = reverse('admin_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_home.html')

        response = self.client.post(self.url3, self.form_input1, follow=True)
        afterInvoiceValue = response.context['invoices'].last()

        self.assertIsNotNone(afterInvoiceValue)
        self.assertEqual(afterInvoiceValue.amount_to_be_paid, self.request3.get_total_amount_payable())
        self.assertEqual(afterInvoiceValue.invoice_number, str(self.request3.user.id).zfill(4) + '-002')
        response_url = reverse('admin_home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_home.html')
        self.client.logout()

