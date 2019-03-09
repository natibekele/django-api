import tempfile
import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from PIL import Image

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe,Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

# /api/recipe/recipes
RECIPES_URL = reverse('recipe:recipe-list')

def image_upload_url(recipe_id):
    """Return the image upload url"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

# /api/reciep/recipies/1/
def detail_url(recipe_id):
    """Return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_recipe(user,**params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user,**defaults)

def sample_tag(user,name='Main Course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user,name='OJ'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user,name=name)

class PublicRecipeApiTest(TestCase):
    """Test unauthenticated recipe API success"""

    def setUp(self):
        self.client = APIClient()


    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='yoyoyo@ttt.com',
            password='password'
        )
        self.client.force_authenticate(self.user)

    
    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)
    

    def test_retrieve_recipes_for_authenticated_user(self):
        """Test only retrieving users recipes"""
        user2 = get_user_model().objects.create_user(
            email='hh@333.com',
            password='hhh'
        )
        sample_recipe(user=self.user)
        sample_recipe(user=user2)
        recipes = Recipe.objects.all().filter(user=self.user)
        res = self.client.get(RECIPES_URL)

        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    
    def test_view_recipe_detail(self):
        """Test viewming a recipe detail"""
        recipe=sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serialzer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serialzer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    
    def test_create_recipe(self):
        """Test creating a basic recipe"""
        payload= {
            'title': 'Choc cream cake',
            'time_minutes': 5,
            'price': 5.00
            }

        res=self.client.post(RECIPES_URL,payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
    
    def test_create_recipe_with_tag(self):
        """Test creating a recipe with a tag"""
        tag1= sample_tag(user=self.user, name='Vegan')
        tag2= sample_tag(user=self.user, name='Hot')
        payload= {
            'title': 'Icecream',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 20,
            'price': 6.00
        }
        res= self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1,tags)
        self.assertIn(tag2,tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='salt')
        ingredient2 = sample_ingredient(user=self.user, name='pepper')

        payload = {
            'title': 'white chicken',
            'ingredients': [ingredient1.id,ingredient2.id],
            'time_minutes': 25,
            'price': 15
        }
        res= self.client.post(RECIPES_URL,payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)


    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe= sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name = 'Curry')

        payload = {
            'title': 'new title',
            'tags': [new_tag.id]
        }
        url = detail_url(recipe.id)
        self.client.patch(url,payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    
    def test_full_update_recipe(self):
        """Test updating the recipe with an update"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        payload = {
            'title' : 'Spicy Bachata',
            'time_minutes': 50,
            'price': 25
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        ingredients = recipe.ingredients.all()
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(len(tags), 0)
        self.assertEqual(len(ingredients),0)


class RecipeImageTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'dcfeyjoo@dd.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(self.user)
    
    def tearDown(self):
        self.recipe.image.delete()
    
    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10,10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    
    def test_upload_image_failed(self):
        """Test uploading recipe image bad request"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url,{'image': 'noimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


