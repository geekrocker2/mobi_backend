from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from accounts.models import CustomUser, CheckIn, Interaction, FriendRequest, DirectMessage
from django.utils import timezone

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create two test users using the user model
        self.user1 = CustomUser.objects.create_user(
            username='newuser@example.com', 
            email='newuser@example.com', 
            password='newsecurepassword', 
            date_of_birth='2000-01-01'
        )
        self.user2 = CustomUser.objects.create_user(
            username='testuser2@example.com', 
            email='testuser2@example.com', 
            password='anotherpassword', 
            date_of_birth='2000-01-01'
        )
        # Make them friends
        self.user1.friends.add(self.user2)
        self.user2.friends.add(self.user1)

        # Obtain JWT tokens for both users by posting to the token endpoint
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'newuser@example.com',
            'password': 'newsecurepassword'
        }, format='json')
        self.token1 = response.data['access']

        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser2@example.com',
            'password': 'anotherpassword'
        }, format='json')
        self.token2 = response.data['access']

    def test_registration(self):
        """Test that a new user can register successfully."""
        url = reverse('register')
        data = {
            'email': 'testuser3@example.com',
            'password': 'thirdpassword',
            'mobile_number': '1112223333',
            'date_of_birth': '1990-01-01'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.data)

    def test_friend_request(self):
        """Test sending a friend request from user1 to user2."""
        # Remove friendship if it exists for this test
        self.user1.friends.remove(self.user2)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token1)
        url = reverse('send_friend_request')
        data = {'to_user_id': self.user2.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.data)


    def test_checkin_creation(self):
        """Test creating a check-in for user1."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token1)
        url = reverse('create_checkin')
        data = {
            'location_name': 'Test Location',
            'caption': 'Testing checkin',
            'rating': 4
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['location_name'], 'Test Location')

    def test_dm_send(self):
        """Test sending a direct message from user1 to user2."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token1)
        # Assuming you set the DM send endpoint as 'dms/' without a user_id for POST
        url = reverse('send_direct_message')
        data = {
            'receiver': self.user2.id,
            'message': 'Hello, this is a test DM'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'Hello, this is a test DM')

    def test_social_graph(self):
        """Test that social graph returns a closeness score for user2."""
        # Manually create an interaction (in-person) for testing
        from accounts.models import Interaction
        Interaction.objects.create(
            from_user=self.user1,
            to_user=self.user2,
            interaction_type='in_person',
            points=10
        )
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token1)
        url = reverse('social_graph')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.data
        # Check that at least one friend (user2) is present in the social graph data
        friend_ids = [entry['friend_id'] for entry in data]
        self.assertIn(self.user2.id, friend_ids)
