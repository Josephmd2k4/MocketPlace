
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from . models import Message
from accounts.models import User

class MessagingModelTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")

    def test_message_creation(self):
        message = Message.objects.create(sender=self.user1, receiver=self.user2, content="Hey!")
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, "Hey!")
        self.assertFalse(message.read)

    def test_message_str_representation(self):
        message = Message.objects.create(sender=self.user1, receiver=self.user2, content="Hello, world!")
        expected_str = f"{self.user1} to {self.user2} at {message.timestamp}"
        self.assertEqual(str(message), expected_str)

    def test_message_read_status(self):
        message = Message.objects.create(sender=self.user1, receiver=self.user2, content="Hey!", read=False)
        message.read = True
        message.save()
        self.assertTrue(Message.objects.get(id=message.id).read)
