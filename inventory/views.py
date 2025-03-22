from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.db.models import Count
from .serializers import RecipeSerializer
from rest_framework import viewsets
from django.views import View
from django.http import JsonResponse
from .models import PantryItem, UsageLog  # Ensure UsageLog is imported
from .models import PantryItem, Recipe, CommunityPost, Comment
from .serializers import PantryItemSerializer, RecipeSerializer, CommunityPostSerializer, CommentSerializer
from rest_framework.generics import UpdateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.generics import ListAPIView
from django.db.models.functions import Lower
from django.utils import timezone
from datetime import timedelta, date
from django.db.models import Q
from django.db.models import Q
from inventory.services import get_recently_added_items
from django.db.models import Exists, OuterRef
from inventory.models import RecipeIngredient
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny
from inventory.services import filter_inventory_items
from inventory.services import get_expiring_items
from .serializers import MissingIngredientSerializer
from .models import UserPreferences
from .serializers import UserPreferencesSerializer
from django.contrib.auth.models import User



# Pantry Item Views
class PantryItemListCreateView(generics.ListCreateAPIView):
    queryset = PantryItem.objects.all()
    serializer_class = PantryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class PantryItemUpdateView(UpdateAPIView):
    queryset = PantryItem.objects.all()
    serializer_class = PantryItemSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()  # Get the PantryItem instance
        old_quantity = instance.quantity  # Store the old quantity before updating

        response = super().update(request, *args, **kwargs)  # Call the parent update method

        # Get the updated quantity
        new_quantity = self.get_object().quantity
        quantity_used = old_quantity - new_quantity

        # Only log if the item was actually used (quantity decreased)
        if quantity_used > 0:
            UsageLog.objects.create(item=instance, quantity_used=quantity_used)

        return response

class PantryItemDeleteView(DestroyAPIView):
    queryset = PantryItem.objects.all()
    permission_classes = [IsAuthenticated]


class PantryItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PantryItem.objects.all()
    serializer_class = PantryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class RecentlyAddedItemsView(APIView):
    def get(self, request):
        recent_items = get_recently_added_items()
        serializer = PantryItemSerializer(recent_items, many=True)
        return Response(serializer.data)

class UnusedItemsView(generics.ListAPIView):
    serializer_class = PantryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        # Get items that were either never used or not used in the last 30 days
        return PantryItem.objects.filter(
            user=self.request.user
        ).filter(
            Q(last_used_at__lte=thirty_days_ago) | Q(last_used_at__isnull=True)
        )


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import RecipeIngredient, PantryItem
from .serializers import MissingIngredientSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from inventory.models import RecipeIngredient, PantryItem
from inventory.serializers import MissingIngredientSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from inventory.models import RecipeIngredient, PantryItem
from inventory.serializers import MissingIngredientSerializer


class MissingIngredientsView(APIView):
    def get(self, request, recipe_id):
        print(f"Looking for missing ingredients for Recipe ID: {recipe_id}")

        # Fetch ingredients for the specified recipe
        recipe_ingredients = RecipeIngredient.objects.filter(recipe_id=recipe_id)

        # If no ingredients are found for the recipe
        if not recipe_ingredients:
            return Response({"message": "Recipe not found or no ingredients associated."},
                            status=status.HTTP_404_NOT_FOUND)

        # Get all pantry items and map them to a dictionary by name (lowercase to ignore case sensitivity)
        pantry_items = {item.name.lower(): item.quantity for item in PantryItem.objects.all()}
        print(f"Pantry Items: {pantry_items}")  # Debugging pantry items

        missing_ingredients = []

        # Check for missing ingredients
        for ingredient in recipe_ingredients:
            ingredient_name = ingredient.ingredient_name.lower()
            required_quantity = ingredient.quantity
            unit = ingredient.unit
            print(
                f"Checking {ingredient_name} - Required: {required_quantity}, Pantry: {pantry_items.get(ingredient_name, 0)}")  # Debug info

            # If ingredient is missing or has insufficient quantity
            if ingredient_name not in pantry_items or pantry_items[ingredient_name] < required_quantity:
                quantity_needed = required_quantity - pantry_items.get(ingredient_name, 0)
                missing_ingredients.append({
                    "ingredient_name": ingredient.ingredient_name,
                    "quantity_needed": quantity_needed,
                    "unit": unit,
                    "quantity_in_pantry": pantry_items.get(ingredient_name, 0)
                })

        # If no missing ingredients
        if not missing_ingredients:
            return Response({"message": "No missing ingredients for the specified recipe."}, status=status.HTTP_200_OK)

        return Response(MissingIngredientSerializer(missing_ingredients, many=True).data, status=status.HTTP_200_OK)


# Recipe Views
class RecipeListCreateView(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

class RecipeDetailView(generics.RetrieveAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

class RecipeSuggestionsView(APIView):
    def get(self, request):
        # Get the user's pantry items
        pantry_items = PantryItem.objects.filter(user=request.user).values_list("name", flat=True)
        available_ingredients = {name.lower() for name in pantry_items}

        # Get recipes with at least one matching ingredient
        ingredient_matches = RecipeIngredient.objects.annotate(
            lower_name=Lower("ingredient_name")
        ).filter(
            lower_name__in=available_ingredients
        ).values_list("recipe_id", flat=True)

        # Get matching recipes
        matching_recipes = Recipe.objects.filter(id__in=ingredient_matches).distinct()

        # Debugging
        print("Available Ingredients:", available_ingredients)
        print("Recipe IDs with Matching Ingredients:", list(ingredient_matches))
        print("Matching Recipes:", list(matching_recipes.values("id", "title")))

        return Response(RecipeSerializer(matching_recipes, many=True).data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Recipe.objects.all()

        dietary_restriction = self.request.query_params.get('dietary_restrictions', None)
        cuisine = self.request.query_params.get('cuisines', None)

        if dietary_restriction:
            queryset = queryset.filter(dietary_restrictions__icontains=dietary_restriction)
        if cuisine:
            queryset = queryset.filter(cuisines__icontains=cuisine)

        return queryset

class RecipeNutritionView(View):
    def get(self, request, recipe_id):
        try:
            # Fetch the recipe by ID
            recipe = Recipe.objects.get(id=recipe_id)
            # Prepare the nutrition data dictionary
            nutrition_data = {
                'calories': recipe.calories,
                'fat': recipe.fat,
                'protein': recipe.protein,
                'carbs': recipe.carbs,
            }
            # Return the nutrition data as JSON
            return JsonResponse(nutrition_data)
        except Recipe.DoesNotExist:
            # Return an error response if recipe not found
            return JsonResponse({'error': 'Recipe not found'}, status=404)



# Community Posts
class CommunityPostListCreateView(generics.ListCreateAPIView):
    queryset = CommunityPost.objects.all()
    serializer_class = CommunityPostSerializer
    permission_classes = [permissions.IsAuthenticated]

class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(post_id=self.kwargs["postId"])

    def perform_create(self, serializer):
        serializer.save(post_id=self.kwargs["postId"], user=self.request.user)

class TrendingPostsView(ListAPIView):
    serializer_class = CommunityPostSerializer

    def get_queryset(self):
        return CommunityPost.objects.order_by("-likes", "-created_at")[:10]  # Top 10 trending



class LikePostView(APIView):
    def post(self, request, post_id):
        try:
            post = CommunityPost.objects.get(id=post_id)
            post.likes += 1
            post.save()
            return Response({"message": "Post liked successfully", "likes": post.likes}, status=status.HTTP_200_OK)
        except CommunityPost.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

class RegisterView(APIView):
    permission_classes = [AllowAny]  # 👈 Make registration public

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user_data = serializer.save()
            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def filter_pantry_items(request):
    """
    API endpoint to filter pantry items based on query parameters.
    """
    name = request.GET.get('name')
    category = request.GET.get('category')
    min_stock = request.GET.get('min_stock')
    max_stock = request.GET.get('max_stock')
    expiring_soon = request.GET.get('expiring_soon')

    # Convert query parameters to appropriate data types
    min_stock = int(min_stock) if min_stock is not None else None
    max_stock = int(max_stock) if max_stock is not None else None
    expiring_soon = int(expiring_soon) if expiring_soon is not None else None

    # Get filtered pantry items
    filtered_items = filter_inventory_items(name, category, min_stock, max_stock, expiring_soon)

    # Serialize and return response
    serializer = PantryItemSerializer(filtered_items, many=True)
    return Response(serializer.data)

class LowStockItemsView(APIView):
    def get(self, request):
        low_stock_items = PantryItem.objects.filter(quantity__lte=5)
        serializer = PantryItemSerializer(low_stock_items, many=True)
        return Response(serializer.data)

from datetime import date, timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from inventory.models import PantryItem
from inventory.serializers import PantryItemSerializer

class ExpiringSoonNotificationView(APIView):
    def get(self, request):
        today = date.today()
        expiring_soon = PantryItem.objects.filter(expiration_date__lte=today + timedelta(days=7))

        if not expiring_soon.exists():
            return Response({"message": "No items expiring soon"}, status=200)

        serializer = PantryItemSerializer(expiring_soon, many=True)
        return Response({"expiring_soon": serializer.data}, status=200)


#USER

class UserPreferencesView(APIView):

    def get(self, request, user_id):
        try:
            # Retrieve user preferences based on user_id
            preferences = UserPreferences.objects.get(user_id=user_id)
            serializer = UserPreferencesSerializer(preferences)
            return Response(serializer.data)
        except UserPreferences.DoesNotExist:
            return Response({"error": "Preferences not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, user_id):
        # Check if the user already has preferences
        try:
            preferences = UserPreferences.objects.get(user_id=user_id)
            # Update the existing preferences
            serializer = UserPreferencesSerializer(preferences, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserPreferences.DoesNotExist:
            # If preferences do not exist, create new ones
            try:
                user = User.objects.get(id=user_id)
                new_preferences = UserPreferences(user=user, **request.data)
                new_preferences.save()
                serializer = UserPreferencesSerializer(new_preferences)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)



class MealPlanGenerateView(APIView):
    def get(self, request, user_id):
        # Fetch user and preferences
        user = get_object_or_404(User, id=user_id)
        preferences = get_object_or_404(UserPreferences, user=user)

        # Fetch all available pantry items for this user
        pantry_items = PantryItem.objects.filter(user=user)

        # Filter recipes based on dietary restrictions and favorite cuisines
        available_recipes = Recipe.objects.all()

        if preferences.dietary_restrictions:
            available_recipes = available_recipes.filter(dietary_restrictions__icontains=preferences.dietary_restrictions)

        if preferences.favorite_cuisines:
            available_recipes = available_recipes.filter(cuisines__icontains=preferences.favorite_cuisines)

        # Check if we have any available recipes after filtering
        if available_recipes.count() == 0:
            return Response({'error': 'No recipes found matching your preferences.'}, status=404)

        # Filter recipes based on available ingredients
        meal_plan = []
        for recipe in available_recipes:
            ingredients = recipe.ingredients.all()
            missing_ingredients = []

            for ingredient in ingredients:
                if not pantry_items.filter(ingredient=ingredient).exists():
                    missing_ingredients.append(ingredient)

            if not missing_ingredients:
                meal_plan.append(recipe)

        # Check if the meal_plan is empty (no recipes available)
        if not meal_plan:
            return Response({'error': 'No recipes available with your current pantry items.'}, status=404)

        # Generate the meal plan for 7 days
        weekly_plan = []
        start_date = date.today()
        for i in range(7):
            daily_recipe = meal_plan[i % len(meal_plan)]  # Rotate through the available recipes
            weekly_plan.append({
                'date': str(start_date + timedelta(days=i)),
                'recipe': RecipeSerializer(daily_recipe).data,
            })

        return Response({'meal_plan': weekly_plan}, status=200)


# views.py
import json
from django.http import JsonResponse
from django.views import View
from .models import PantryItem
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class ScanItemView(View):

    def post(self, request, *args, **kwargs):
        # Get the barcode from the request body (assuming JSON)
        try:
            data = json.loads(request.body)
            barcode = data.get('barcode')
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)

        if not barcode:
            return JsonResponse({"error": "Barcode is required."}, status=400)

        # Check if item with this barcode already exists
        try:
            item = PantryItem.objects.get(barcode=barcode)
            # Item exists, increment the quantity
            item.quantity += 1
            item.save()
            return JsonResponse({
                "message": f"Updated {item.name} quantity to {item.quantity}",
                "name": item.name,
                "quantity": item.quantity
            })

        except PantryItem.DoesNotExist:
            # Item doesn't exist, create a new one
            item = PantryItem.objects.create(
                barcode=barcode,
                name="New Item",  # Default name
                quantity=1,  # Default quantity
                category="General",  # Default category
                user=request.user  # Assuming the user is logged in
            )
            return JsonResponse({
                "message": f"Added {item.name} with barcode {item.barcode}",
                "name": item.name,
                "barcode": item.barcode,
                "quantity": item.quantity
            })

    def get(self, request, *args, **kwargs):
        return JsonResponse({"error": "Invalid method. Use POST."}, status=405)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from .models import PantryItemHistory, User

class PantryItemHistoryView(View):
    def get(self, request, user_id):  # Ensure this matches the URL pattern
        history_queryset = PantryItemHistory.objects.filter(user_id=user_id).order_by("-action_date")

        history_data = [
            {
                "action": entry.action,
                "quantity_changed": entry.quantity_changed,
                "item_name": entry.item.name if entry.item else "Deleted Item",
                "action_date": entry.action_date.strftime("%Y-%m-%d %H:%M:%S") if entry.action_date else "Unknown Date",
            }
            for entry in history_queryset
        ]

        return JsonResponse({"history": history_data}, safe=False)


from django.http import JsonResponse
from django.views import View
from inventory.models import PantryItem
from collections import defaultdict

class CategorizedItemsView(APIView):
    def get(self, request):
        categorized_items = {}

        for item in PantryItem.objects.all():
            category = item.category if item.category else "Uncategorized"

            if category not in categorized_items:
                categorized_items[category] = []

            categorized_items[category].append({
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "expiration_date": item.expiration_date,
                "barcode": item.barcode,
                "user": item.user.id
            })

        return Response(categorized_items, status=200)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from .models import UsageLog

class FrequentlyUsedItemsView(APIView):
    def get(self, request):
        frequently_used = (
            UsageLog.objects
            .values("item__name")
            .annotate(total_used=Sum("quantity_used"))
            .order_by("-total_used")
        )

        return Response(frequently_used, status=status.HTTP_200_OK)
