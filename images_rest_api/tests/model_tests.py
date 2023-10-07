from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import AccountType, ThumbnailSize


# Create your tests here.
class CustomUserTests(TestCase):
    def setUp(self) -> None:
        thumbs = ThumbnailSize.objects.create(size=200)
        account_type = AccountType.objects.create(name="TestAccountType")
        account_type.thumbs.set([thumbs])

    def test_new_superuser(self):
        db = get_user_model()
        superuser = db.objects.create_superuser(
            "testuser", "testuser@email.com", "strongpassword", 1
        )
        self.assertEqual(superuser.username, "testuser")
        self.assertEqual(superuser.email, "testuser@email.com")
        self.assertNotEqual(superuser.password, "strongpassword")
        self.assertEqual(superuser.account_type.id, 1)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_active)
        self.assertEqual(superuser.__str__(), "testuser")

        with self.assertRaises(ValueError):
            superuser = db.objects.create_superuser(
                "testuser",
                "testuser@email.com",
                "strongpassword",
                1,
                is_superuser=False,
            )

        with self.assertRaises(ValueError):
            superuser = db.objects.create_superuser(
                "testuser", "testuser@email.com", "strongpassword", 1, is_staff=False
            )

        with self.assertRaises(ValueError):
            superuser = db.objects.create_superuser(
                "testuser", "testuser@email.com", "strongpassword", 1, is_active=False
            )

    def test_new_user(self):
        db = get_user_model()
        account_type = AccountType.objects.get(name="TestAccountType")

        user = db.objects.create_user(
            "testuser", "testuser@email.com", "strongpassword", account_type.id
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@email.com")
        self.assertNotEqual(user.password, "strongpassword")
        self.assertEqual(user.account_type.id, account_type.id)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertEqual(user.__str__(), "testuser")
