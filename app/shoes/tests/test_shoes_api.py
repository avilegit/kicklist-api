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

    def test_create_basic_shoe(self):
        """Test creating a basic shoe"""

        payload = {
            'title' : 'UltraBoosts 2019',
            'brand' : 'Adidas',
            'price' : 150
        }

        res = self.client.post(SHOES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        shoe = Shoes.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(shoe, key))

    def test_create_shoe_with_tags(self):
        """Test creating a shoe with tags"""
        tag1 = sample_tag(user=self.user, name='hightops')
        tag2 = sample_tag(user=self.user, name='lowtops')
        payload = {
            'title' : 'lowtop-hightop hybrid',
            'tags' : [tag1.id, tag2.id],
            'brand' : 'weird brand',
            'price' : '4000'
        }

        res = self.client.post(SHOES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        shoe = Shoes.objects.get(id=res.data['id'])
        tags = shoe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_show_with_characteristics(self):
        """Test creating shoe with characteristics"""

        char1 = sample_characteristic(user =self.user, name='teal')
        char2 = sample_characteristic(user=self.user, name='gum bottom')

        payload = {
            'title' : 'NMD 250',
            'characteristics' : [char1.id, char2.id],
            'brand' : 'Adidas',
            'price' : '160'
        }

        res = self.client.post(SHOES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        shoe = Shoes.objects.get(id=res.data['id'])
        characteristics = shoe.characteristics.all()

        self.assertEqual(characteristics.count(), 2)
        self.assertIn(char1, characteristics)
        self.assertIn(char2, characteristics)

    def test_partial_update_shoe(self):
        """Test udpating a shoe with PATCH"""

        shoe = sample_shoe(user=self.user)
        shoe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='designer')

        payload = {
            'title' : 'Skechers 500',
            'tags'  : [new_tag.id],
        }

        url = detail_url(shoe.id)
        self.client.patch(url, payload)

        shoe.refresh_from_db()
        self.assertEqual(shoe.title, payload['title'])
        tags = shoe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """test updating a recipe with PUT"""

        shoe = sample_shoe(user=self.user)
        shoe.tags.add(sample_tag(user=self.user))

        payload = {
            'title' : 'LunarEpics',
            'brand' : 'Nike',
            'price' : 130
        }

        url = detail_url(shoe.id)
        self.client.put(url, payload)

        shoe.refresh_from_db()
        self.assertEqual(shoe.title, payload['title'])
        self.assertEqual(shoe.brand, payload['brand'])
        self.assertEqual(shoe.price, payload['price'])
        tags = shoe.tags.all()
        self.assertEqual(len(tags), 0)
        self.assertEqual(shoe.brand, payload['brand'])


