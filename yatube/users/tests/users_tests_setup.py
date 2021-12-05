from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersTestsSetup(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()

        self.auth_client.force_login(self.user)
