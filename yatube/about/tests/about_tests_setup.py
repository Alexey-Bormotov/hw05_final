from django.test import Client, TestCase


class AboutTestsSetup(TestCase):
    def setUp(self):
        self.guest_client = Client()
