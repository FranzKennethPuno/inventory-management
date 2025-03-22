from rest_framework import serializers
from .models import PantryItem, Recipe, CommunityPost, Comment
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from inventory.models import Recipe, RecipeIngredient
from .models import UserPreferences

class PantryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PantryItem
        fields = '__all__'

class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ["ingredient_name", "quantity", "unit"]

from rest_framework import serializers
from inventory.models import Recipe, RecipeIngredient

class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ["ingredient_name", "quantity", "unit"]

class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ["ingredient_name", "quantity", "unit"]



class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'instructions', 'calories', 'fat', 'protein', 'carbs', 'cuisines',
                  'dietary_restrictions']

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients", [])  # Extract ingredients list
        recipe = Recipe.objects.create(**validated_data)  # Create the recipe

        # Save each ingredient linked to the recipe
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient)

        return recipe


class CommunityPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityPost
        fields = ['id', 'user', 'title', 'content', 'hashtags', 'likes', 'created_at']
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'comment', 'created_at']
        read_only_fields = ['post', 'user', 'created_at']  # Ensure post & user are auto-assigned


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        refresh = RefreshToken.for_user(user)  # Generate tokens

        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }

class MissingIngredientSerializer(serializers.Serializer):
    ingredient_name = serializers.CharField(max_length=255)
    quantity_needed = serializers.FloatField()
    unit = serializers.CharField(max_length=50)
    quantity_in_pantry = serializers.FloatField()

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = ['dietary_restrictions', 'favorite_cuisines']