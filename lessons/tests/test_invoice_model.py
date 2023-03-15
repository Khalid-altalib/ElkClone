from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models import Request, Invoice, User
import datetime as dt
from decimal import Decimal


class InvoiceModelTestCase(TestCase):
    """Tests of the Invoice Model"""

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='Password123')
        self.teacher = User.objects.create_user(email='teacher@example.com', password='password123', is_staff=True)
        self.request = Request.objects.create(
            user=self.user,
            availability="MONDAYAM",
            number_of_lessons=10,
            interval=1,
            duration=45,
            lesson_content="Singing",
            teacher=self.teacher,
            class_Day='MONDAY',
            class_Time=dt.time(8),
            start_Date=dt.date(2021, 1, 1),
        )
        self.request.clean()
        self.invoice = Invoice.objects.create(
            invoice_number="1234-001",
            request=self.request,
            created_date=dt.date(2021, 1, 1),
            amount_to_be_paid=Decimal('120.55'),

        )

    def generateInvoice2(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='Password123')
        self.teacher = User.objects.create_user(email='teacher@example.com', password='password123', is_staff=True)
        self.request = Request.objects.create(
            user=self.user,
            availability="MONDAYAM",
            number_of_lessons=10,
            interval=1,
            duration=45,
            lesson_content="Singing",
            teacher=self.teacher,
            class_Day='MONDAY',
            class_Time=dt.time(8),
            start_Date=dt.date(2021, 1, 1),
        )
        self.request.clean()
        self.invoice = Invoice.objects.create(
            invoice_number="1234-001",
            request=self.request,
            created_date=dt.date(2021, 1, 1),
            amount_to_be_paid=Decimal('120.55'),

        )


    def test_valid_invoice(self):
        self._assert_invoice_is_valid()

    def _assert_invoice_is_valid(self):
        try:
            self.invoice.full_clean()
        except ValidationError:
            self.fail('Invoice should be valid, but is not')

    def _assert_invoice_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.invoice.full_clean()

    """Tests for Invoice Number"""

    def test_invoice_number_must_contain_dash_symbol(self):
        self.invoice.invoice_number = '12345678'
        self._assert_invoice_is_invalid()

    def test_invoice_number_must_not_contain_more_than_one_dash(self):
        self.invoice.invoice_number = '12-45-45'
        self._assert_invoice_is_invalid()

    def test_invoice_number_must_contain_only_digits(self):
        self.invoice.invoice_number = 'abcd-801'
        self._assert_invoice_is_invalid()

    def test_invoice_number_must_be_unique(self):
        second_invoice = self._create_second_invoice()
        self.invoice.invoice_number = second_invoice.invoice_number
        self._assert_invoice_is_invalid()

    def test_invoice_number_must_not_be_blank(self):
        self.invoice.invoice_number = ''
        self._assert_invoice_is_invalid()

    def test_invoice_number_can_be_8_characters_long(self):
        self.invoice.invoice_number = '1234-567'
        self._assert_invoice_is_valid()

    def test_invoice_number_cannot_be_over_9_characters(self):
        self.invoice.invoice_number = '121323435-13224325'
        self._assert_invoice_is_invalid()

    """Tests for Created date"""

    def test_created_date_should_be_in_the_past(self):
        pass
        # TODO: Figure it out 

    def test_created_date_must_not_be_blank(self):
        self.invoice.created_date = ''
        self._assert_invoice_is_invalid()

    """Tests for Amount To be Paid"""

    def test_amount_must_not_be_blank(self):
        self.invoice.amount_to_be_paid = ''
        self._assert_invoice_is_invalid()

    def test_amount_must_be_decimal_instance(self):
        self.invoice.amount_to_be_paid = 123.45
        self._assert_invoice_is_invalid()

    def test_amount_can_have_2_decimals(self):
        self.invoice.amount_to_be_paid = Decimal('123.45')
        self._assert_invoice_is_valid()

    def test_amount_cannot_have_3_or_more_decimals(self):
        self.invoice.amount_to_be_paid = Decimal('123.456')
        self._assert_invoice_is_invalid()

    def test_amount_can_have_12_digits(self):
        self.invoice.amount_to_be_paid = Decimal('1234567890.12')
        self._assert_invoice_is_valid()

    def test_amount_cannot_be_over_13_or_more_digits(self):
        self.invoice.amount_to_be_paid = Decimal('01234567890123456789.12')
        self._assert_invoice_is_invalid()

    """Tests for Status"""
    def test_status_can_only_be_active_or_closed(self):
        self.invoice.status = "Pending"
        self._assert_invoice_is_invalid()

    def test_status_is_case_sensitive(self):
        self.invoice.status = "Closed"
        self._assert_invoice_is_invalid()

    def test_status_default_to_be_active(self):
        self.assertEqual(self.invoice.status, "ACTIVE")

    def _create_second_invoice(self):
        self.teacher = User.objects.create_user(email='teacher2@example.com', password='password123', is_staff=True)
        self.request2 = Request.objects.create(
            user=self.user,
            availability="MONDAYPM, THURSDAYPM",
            number_of_lessons=6,
            interval=1,
            duration=60,
            lesson_content="Dancing",
            teacher=self.teacher,
            class_Day='MONDAY',
            class_Time=dt.time(8),
            start_Date=dt.date(2021, 1, 1),
        )
        invoice2 = Invoice.objects.create(
            invoice_number="2938-094",
            request=self.request2,
            created_date=dt.date(2021, 9, 9),
            amount_to_be_paid=Decimal('901.90'),
        )
        return invoice2
