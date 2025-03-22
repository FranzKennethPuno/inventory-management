from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PantryItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.FloatField()
    unit = models.CharField(max_length=50)
    expiration_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    barcode = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Barcode field
    category = models.CharField(
        max_length=100,
        choices=[
            ('Dairy', 'Dairy'),
            ('Meat', 'Meat'),
            ('Vegetables', 'Vegetables'),
            ('Grains', 'Grains'),
            ('Fruits', 'Fruits'),
            ('Others', 'Others')
        ],
        default='Others'
    )

    def update_usage(self):
        """Call this method when an item is used"""
        self.last_used_at = timezone.now()
        self.save()

class Recipe(models.Model):
    title = models.CharField(max_length=255)
    instructions = models.TextField()
    calories = models.FloatField(null=True, blank=True)
    fat = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    carbs = models.FloatField(null=True, blank=True)
    dietary_restrictions = models.CharField(max_length=255, blank=True, null=True)  # e.g., "Vegan, Gluten-Free"
    cuisines = models.CharField(max_length=255, blank=True, null=True)  # e.g., "Italian, Mexican"
    category = models.CharField(
        max_length=100,
        choices=[
            ('Dairy', 'Dairy'),
            ('Meat', 'Meat'),
            ('Vegetables', 'Vegetables'),
            ('Grains', 'Grains'),
            ('Fruits', 'Fruits'),
            ('Others', 'Others')
        ],
        default='Others'
    )
    def __str__(self):
        return self.title

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
    ingredient_name = models.CharField(max_length=255)
    quantity = models.FloatField()
    unit = models.CharField(max_length=50)

class NutritionInfo(models.Model):
    recipe = models.OneToOneField(Recipe, on_delete=models.CASCADE, related_name="nutrition_info")
    calories = models.IntegerField()
    protein = models.FloatField()
    fat = models.FloatField()
    carbs = models.FloatField()

from django.db import models
from django.contrib.auth.models import User

class CommunityPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Untitled Post")  # Set a default value
    content = models.TextField()
    hashtags = models.CharField(max_length=255, blank=True, default="")
    likes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dietary_restrictions = models.CharField(max_length=255, blank=True, null=True)  # For example, "Gluten-Free, Vegan"
    favorite_cuisines = models.CharField(max_length=255, blank=True, null=True)  # For example, "Italian, Mexican"

    def __str__(self):
        return f"{self.user.username}'s Preferences"

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PantryItemHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey("PantryItem", on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50)  # 'added', 'removed', 'updated'
    quantity_changed = models.FloatField()  # The change in quantity (positive or negative)
    action_date = models.DateTimeField(default=timezone.now)
    comment = models.TextField(blank=True, null=True)  # Optional comment field

    def __str__(self):
        item_name = self.item.name if self.item else "Unknown Item"
        return f"{self.user.username} {self.action} {item_name} ({self.quantity_changed})"




from django.db import models
from django.utils.timezone import now

class UsageLog(models.Model):
    item = models.ForeignKey("PantryItem", on_delete=models.CASCADE)
    quantity_used = models.PositiveIntegerField(default=0)  # Auto-fills new logs
    timestamp = models.DateTimeField(default=timezone.now)
