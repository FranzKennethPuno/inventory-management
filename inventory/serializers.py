# inventory/serializers.py
from rest_framework import serializers
from .models import PantryItem, Recipe, MealPlan, UserPreference, InventoryHistory, CommunityPost, Comment

class PantryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PantryItem
        fields = '__all__'

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'

class MealPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlan
        fields = '__all__'

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = '__all__'

class InventoryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryHistory
        fields = '__all__'

class CommunityPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityPost
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

##LOGIN AND REGISTER##
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        user = authenticate(username=data["username"], password=data["password"])
        if user:
            refresh = RefreshToken.for_user(user)
            return {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        raise serializers.ValidationError("Invalid credentials")

##CREATE A RECIPE##
from rest_framework import serializers
from .models import Recipe
import ast

class RecipeSerializer(serializers.ModelSerializer):
    # Convert the string to a proper list on retrieval
    ingredients = serializers.SerializerMethodField()
    steps = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        # Safely convert the string to a list if it was saved as a string
        if isinstance(obj.ingredients, str):
            return ast.literal_eval(obj.ingredients)
        return obj.ingredients

    def get_steps(self, obj):
        # Safely convert the string to a list if it was saved as a string
        if isinstance(obj.steps, str):
            return ast.literal_eval(obj.steps)
        return obj.steps
