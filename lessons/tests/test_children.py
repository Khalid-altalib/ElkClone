from django.core.exceptions import ValidationError
from django.test import TestCase

from lessons.models import User, Child


class ChildModelTestCase(TestCase):
    """Tests of the User model"""

    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='password123')
        self.child = Child.objects.create(name="Thing 1", parent=self.user)
        self.other_child = Child.objects.create(name="Thing 2", parent=self.user)

    def test_user_is_valid(self):
        self._assert_user_is_valid()

    def test_children_can_be_added(self):
        self._assert_child_is_valid(self.child)
        self._assert_user_is_valid()

    def test_child_name_must_be_unique_for_parent(self):
        self.other_child.name = "Thing 1"
        self._assert_child_is_invalid(self.other_child)

    def test_child_name_need_not_be_unique_with_different_parents(self):
        other_user = User.objects.create_user(email='test2@example.com', password='password123')
        self.other_child.parent = other_user
        self.other_child.name = "Thing 1"
        self._assert_child_is_valid(self.child)
        self._assert_child_is_valid(self.other_child)

    def test_child_name_must_not_be_blank(self):
        self.child.name = ""
        self._assert_child_is_invalid(self.child)

    def test_child_parent_must_not_be_blank(self):
        self.child.parent = None
        self._assert_child_is_invalid(self.child)

    def _assert_user_is_valid(self):
        try:
            self.user.full_clean()
        except ValidationError:
            self.fail('user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def _assert_child_is_valid(self, child):
        try:
            child.full_clean()
        except ValidationError:
            self.fail('user should be valid')

    def _assert_child_is_invalid(self, child):
        with self.assertRaises(ValidationError):
            child.full_clean()

