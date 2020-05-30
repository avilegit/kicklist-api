from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Shoes, Tag, Characteristic

from shoes.serializers import ShoeSerializer, ShoeDetailSerializer

SHOES_URL = reverse('shoes:shoes-list')

# api/shoe/shoes
# api/shoe/shoes/id create this dynamically

def detail_url(shoe_id):
    """return shoe detail URL"""

    #router will create the detail url
    return reverse('shoes:shoes-detail', args=[shoe_id])

def sample_tag(user, name='street wear'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)

def sample_characteristic(user, name='suede'):
    """Create and return a sample characteristic"""
    return Characteristic.objects.create(user=user, name=name)

def sample_shoe(user, **params):
    """Create and return a sample shoe"""

    defaults = {
        'title' : 'Sample shoe',
        'brand' : 'Sample brand',
        'price' : 1.00
    }

    defaults.update(params) #update defauls if we add more params
    return Shoes.objects.create(user=user, **defaults)  #turn a dictionary into args

class PublicShoesApiTests(TestCase):
    """Test unauthenticated shoes API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication required"""
        res = self.client.get(SHOES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateShoesApiTests(TestCase):
    """Test authenticated shoes API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@testdomain.com',
            'testpass'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_shoes(self):
        """Test retrieving a list of shoes"""

        #access these by retrieving db objects
        sample_shoe(user=self.user)
        sample_shoe(user=self.user)

        res = self.client.get(SHOES_URL)
        shoes = Shoes.objects.all().order_by('id')

        serializer = ShoeSerializer(shoes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_shoes_limited_to_user(self):
        """Test retrieiving shoes for user"""

        user2=get_user_model().objects.create_user(
            'other@testdomain.com',
            'password'
        )

        sample_shoe(user=user2)
        sample_shoe(user=self.user)

        res = self.client.get(SHOES_URL)

        shoes = Shoes.objects.filter(user=self.user)
        serializer = ShoeSerializer(shoes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_shoe_detail(self):
        """Test viewing a shoe detail"""

        shoe = sample_shoe(user=self.user)
        shoe.tags.add(sample_tag(user=self.user))
        shoe.characteristics.add(sample_characteristic(user=self.user))

        url = detail_url(shoe.id)
        res = self.client.get(url)

        serializer = ShoeDetailSerializer(shoe)
        self.assertEqual(res.data, serializer.data)


