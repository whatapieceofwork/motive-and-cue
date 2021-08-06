import unittest
from app.models import AnonymousUser, User, Role, Permission

class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u = User(email="lisa@example.com", username="lisa", password="cat")
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(email="brianna@example.com", username="brianna", password="cat")
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(email="joseph@example.com", username="joe", password="cat")
        self.assertTrue(u.check_password("cat"))
        self.assertFalse(u.check_password("dog"))

    def test_password_salts_are_random(self):
        u = User(email="john@example.com", username="john", password="cat")
        u2 = User(email="jane@example.com", username="jane", password="ferretflassasdsdsdasd")
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_user_role(self):
        u = User(email="eliza@example.com", username="eliza", password="cat")
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.SUGGEST_EDIT))
        self.assertFalse(u.can(Permission.APPROVE_EDIT))
        self.assertFalse(u.can(Permission.ADD))
        self.assertFalse(u.can(Permission.ADMIN))
        
    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.SUGGEST_EDIT))
        self.assertFalse(u.can(Permission.APPROVE_EDIT))
        self.assertFalse(u.can(Permission.ADD))
        self.assertFalse(u.can(Permission.ADMIN))