from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Shoes
from core.models import Characteristic

from shoes.serializers import TagSerializer

TAGS_URL = reverse('shoes:tag-list')

class PublicTagsApiTests(TestCase):
    """Test the publically available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@testdomain.com',
            'testpass'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
 
    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name="runners")
        Tag.objects.create(user=self.user, name="slides")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that the tags returned are for the authenticated user"""

        user2 = get_user_model().objects.create_user(
            'test2@testdomain.com',
            'testpass'
        )
        Tag.objects.create(user=user2, name='boots')
        tag = Tag.objects.create(user=self.user, name='designer')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def create_tag_successful(self):
        """Test creating a new tag"""

        payload = {'name' : 'Test tag'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user = self.user,
            name = payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_valid(self):
        """Creating a new tag with invalid payload"""
        payload = {'name' : ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_shoes(self):
        """Test filtering tags by those assigned to shoes"""

        tag1 = Tag.objects.create(user=self.user, name='Suede')
        tag2 = Tag.objects.create(user=self.user, name='Designer')

        shoe = Shoes.objects.create(
            title = 'Chuck Taylor All-Star',
            price = 60,
            brand = "Converse",
            user = self.user
        )

        shoe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only' : 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""

        tag = Tag.objects.create(user=self.user, name='streetwear')
        Tag.objects.create(user=self.user, name='basketball')

        shoe1 = Shoes.objects.create(
            title = 'Air Huarache',
            brand = 'Nike',
            price = 160,
            user = self.user
        )

        shoe1.tags.add(tag)

        shoe2 = Shoes.objects.create(
            title = 'Roche 1',
            brand = 'Nike',
            price = 140,
            user = self.user
        )
        
        shoe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only' : 1})
        self.assertEqual(len(res.data), 1)