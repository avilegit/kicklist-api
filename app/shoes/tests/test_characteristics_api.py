from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Characteristic

from shoes.serializers import CharacteristicsSerializer

CHARACTERISTICS_URL = reverse('shoes:characteristic-list')

class PublicCharacteristicsApiTests(TestCase):
    """Test the publically available characteristics API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(CHARACTERISTICS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateCharacteristicsApiTests(TestCase):
    """Test the private characteristics api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@testdomain.com',
            'testpass'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_characteristics_list(self):
        """test retrieving a list of characteristics"""

        Characteristic.objects.create(user=self.user, name = 'blue')
        Characteristic.objects.create(user=self.user, name = 'leather')

        res = self.client.get(CHARACTERISTICS_URL)

        characteristics = Characteristic.objects.all().order_by('-name')
        serializer = CharacteristicsSerializer(characteristics, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_characteristics_limited_to_user(self):
        """Test that characteristics for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'other@testdomain.com',
            'testpass'
        )

        Characteristic.objects.create(user=user2, name='canvas')
        characteristic = Characteristic.objects.create(user=self.user, name = 'mesh')

        res = self.client.get(CHARACTERISTICS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], characteristic.name)

    def test_create_characteristic_succesful(self):
        """Test create a new characteristic"""

        payload = {'name' : 'stripes'} 
        self.client.post(CHARACTERISTICS_URL, payload)

        exists = Characteristic.objects.filter(
            user = self.user,
            name = payload['name'], 
        ).exists()

        self.assertTrue(exists)

    def test_create_characteristic_invalid(self):
        """Test creating invalid characteristic"""

        payload = {'name' : ''}
        res = self.client.post(CHARACTERISTICS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)