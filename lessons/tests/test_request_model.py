from django.test import TestCase
from django.core.exceptions import ValidationError
from lessons.models import Request, User, Child
import datetime as dt
from decimal import Decimal

class RequestModelTestCase(TestCase):
    """Tests of the Request Model"""

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.teacher = User.objects.create_user(email='teacher@example.com', password='password123', is_staff=True)
        self.child = Child.objects.create(name="Small Human", parent=self.user)
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

    def test_request_is_valid(self):
        self._assert_request_is_valid()

    def test_get_amount_payable(self):
        self.assertEquals(self.request.get_total_amount_payable(), 4500.0)

    def test_type_get_amount_payable(self):
        self.assertIsInstance(self.request.get_total_amount_payable(), Decimal)
        # self.assertEquals(self.request.get_total_amount_payable(), 4500.0)

    def test_user_is_same_as_user_entered(self):
        self.assertEquals(self.request.user, self.user)

    def test_default_isApproved_is_false(self):
        self.assertEquals(self.request.isApproved, False)

    def test_availability_cannot_be_more_than_200_characters(self):
        self.request.availability = "x" * 201
        self._assert_request_is_invalid()

    def test_availability_must_be_listed_in_choices(self):
        self.request.availability = "Not in choices"
        self._assert_request_is_invalid()

    def test_number_of_lessons_cannot_be_more_than_50(self):
        self.request.number_of_lessons = 51
        self._assert_request_is_invalid()

    def test_number_of_lessons_cannot_be_less_than_1(self):
        self.request.number_of_lessons = 0
        self._assert_request_is_invalid()

    def test_interval_cannot_be_more_than_5(self):
        self.request.interval = 5
        self._assert_request_is_invalid()

    def test_interval_cannot_be_less_than_1(self):
        self.request.interval = 0
        self._assert_request_is_invalid()

    def test_duration_cannot_be_more_than_180(self):
        self.request.duration = 181
        self._assert_request_is_invalid()

    def test_duration_cannot_be_less_than_30(self):
        self.request.duration = 29
        self._assert_request_is_invalid()

    def test_lesson_content_cannot_be_more_than_50_characters(self):
        self.request.lesson_content = "x" * 51
        self._assert_request_is_invalid()

    def test_lesson_content_can_be_50_characters(self):
        self.request.lesson_content = "x" * 50
        self._assert_request_is_valid()

    def test_teacher_can_be_blank(self):
        self.request.teacher = None
        self._assert_request_is_valid()

    def test_teacher_must_be_valid(self):
        self.request.teacher = self.user
        self._assert_request_is_invalid()

    def _assert_request_is_valid(self):
        try:
            self.request.full_clean()
        except ValidationError:
            self.fail('user should be valid')

    def _assert_request_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.request.full_clean()

    def test_default_day_is_monday(self):
        self.assertEquals(self.request.class_Day, 'MONDAY')

    def test_default_time_is_8(self):
        self.assertEquals(self.request.class_Time, dt.time(8))

    def test_default_Start_Date(self):
        self.assertEquals(self.request.start_Date, dt.date(2021, 1, 1))

    def test_child_can_be_added(self):
        self.request.child = self.child
        self._assert_request_is_valid()

    def test_child_cannot_be_someone_elses(self):
        user_2 = User.objects.create_user(email='test2@example.com', password='password123')
        child_2 = Child.objects.create(name="Another Kid", parent=user_2)
        self.request.child = child_2
        self._assert_request_is_invalid()
