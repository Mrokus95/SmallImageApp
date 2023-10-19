from django.contrib.auth import get_user_model

User = get_user_model()


def change_password_to_default():
    test_user = User.objects.get(username="TestUser")
    if test_user:

        test_user.set_password("TestPassword")
        test_user.save()

