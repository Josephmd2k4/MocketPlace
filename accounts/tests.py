from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AccountTests(TestCase):

    def test_user_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'testuser',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        })
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())



    
    def test_profile_access_authenticated(self):
        user = User.objects.create_user(
            username='testuser2',
            password='Password456!',
            first_name='Test',
            last_name='User'
        )
        self.client.login(username='testuser2', password='Password456!')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')

    
    def test_profile_access_unauthenticated(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, '/accounts/login/?next=/accounts/profile/')  # update path if needed
