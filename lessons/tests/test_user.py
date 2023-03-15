from django.core.exceptions import ValidationError
from django.test import TestCase

from lessons.models import User


class UserModelTestCase(TestCase):
    """Tests of the User model"""

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123')

    def test_user_is_valid(self):
        self._assert_user_is_valid()

    def test_default_balance_is_zero(self):
        self.assertEquals(self.user.balance, 0)

    def test_email_must_be_unique(self):
        otherUser = User.objects.create_user(email='test2@example.com', password='password123')
        self.user.email = otherUser.email
        self._assert_user_is_invalid()

    def test_email_must_contain_at(self):
        self.user.email = 'a'
        self._assert_user_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.user.email = 'a@b@c.com'
        self._assert_user_is_invalid()

    def test_first_name_need_not_be_unique(self):
        otherUser = User.objects.create_user(email='test2@example.com', password='password123', first_name='First',
                                             last_name='Last')
        self.user.first_name = otherUser.first_name
        self._assert_user_is_valid()

    def test_last_name_need_not_be_unique(self):
        otherUser = User.objects.create_user(email='test2@example.com', password='password123', first_name='First',
                                             last_name='Last')
        self.user.last_name = otherUser.last_name
        self._assert_user_is_valid()

    def test_first_name_cannot_be_over_50_chars(self):
        self.user.first_name = 'a' * 51
        self._assert_user_is_invalid()

    def test_first_name_can_be_50_chars(self):
        self.user.first_name = 'a' * 50
        self._assert_user_is_valid()

    def test_last_name_cannot_be_over_50_chars(self):
        self.user.last_name = 'a' * 51
        self._assert_user_is_invalid()

    def test_last_name_can_be_50_chars(self):
        self.user.last_name = 'a' * 50
        self._assert_user_is_valid()

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
            self.fail('user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()
