from django.urls import path
from .views import (
    PantryItemListCreateView, PantryItemDetailView, RecipeListCreateView,
    RecipeDetailView, RecipeSuggestionsView, CommunityPostListCreateView,
    CommentListCreateView, RegisterView, filter_pantry_items, LowStockItemsView,
    ExpiringSoonNotificationView, PantryItemUpdateView, PantryItemDeleteView,
    LikePostView, TrendingPostsView, RecentlyAddedItemsView, UnusedItemsView,
    MissingIngredientsView, RecipeNutritionView, UserPreferencesView, MealPlanGenerateView,
    ScanItemView, PantryItemHistoryView, CategorizedItemsView, PantryItemUpdateView,
    FrequentlyUsedItemsView

)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('inventory/items/', PantryItemListCreateView.as_view(), name='pantry-list'),
    path('inventory/items/filter/', filter_pantry_items, name='filter_pantry_items'),
    path('inventory/items/<int:pk>/remove/', PantryItemDeleteView.as_view(), name='remove_pantry_item'),
    path('inventory/items/low-stock/', LowStockItemsView.as_view(), name='low_stock_items'),
    path('inventory/items/recently-added/', RecentlyAddedItemsView.as_view(), name='recently_added_items'),
    path('inventory/items/unused/', UnusedItemsView.as_view(), name='unused-items'),
    path('recipes/<int:recipe_id>/missing-ingredients/', MissingIngredientsView.as_view(), name='missing-ingredients'),
    path('inventory/notifications/', ExpiringSoonNotificationView.as_view(), name='expiring_notifications'),
    path('inventory/items/<int:pk>/update/', PantryItemUpdateView.as_view(), name='update_pantry_item'),
    path('inventory/items/<int:pk>/', PantryItemDetailView.as_view(), name='pantry-detail'),
    path("inventory/items/categorized/", CategorizedItemsView.as_view(), name="categorized-items"),
    path("inventory/users/<int:user_id>/history/", PantryItemHistoryView.as_view(), name="user-history"),
    path("inventory/items/frequently-used/", FrequentlyUsedItemsView.as_view(), name="frequently-used-items"),
    path('scan/', ScanItemView.as_view(), name='scan_item'),
    path('recipes/', RecipeListCreateView.as_view(), name='recipe-list'),
    path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('recipes/<int:recipe_id>/nutrition/', RecipeNutritionView.as_view(), name='recipe_nutrition'),
    path('recipes/suggest/', RecipeSuggestionsView.as_view(), name='recipe-suggest'),
    path('inventory/meal-plans/generate/<int:user_id>/', MealPlanGenerateView.as_view(), name='generate_meal_plan'),
    path('community/posts/', CommunityPostListCreateView.as_view(), name='post-list'),
    path('community/posts/<int:post_id>/like/', LikePostView.as_view(), name='like_post'),
    path('community/posts/<int:postId>/comments/', CommentListCreateView.as_view(), name='comment-list'),
    path("community/posts/trending/", TrendingPostsView.as_view(), name="trending_posts"),
    path('users/<int:user_id>/preferences/', UserPreferencesView.as_view(), name='user-preferences'),
]
