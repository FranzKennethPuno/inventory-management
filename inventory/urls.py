# inventory/urls.py
from django.urls import path, include
from django.urls import path
from .views import UserDetailView
from .views import LogoutView
from .views import RegisterView, LoginView, ProfileView
from .views import check_expiration
from .views import CreateRecipeView
from .views import RecipeListCreateView, RecipeDetailView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import (
    PantryItemViewSet, RecipeViewSet, NotificationView, BarcodeScanView, RecipeUsageView,
    MealPlanViewSet, UserPreferenceViewSet, AnalyticsView, UsageAnalyticsView, CommunityPostViewSet,
    HealthCheckView  # <-- Import the new view
)

router = DefaultRouter()
router.register(r'inventory/items', PantryItemViewSet, basename='pantryitem')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'inventory/meal-plans', MealPlanViewSet, basename='mealplan')
router.register(r'inventory/community/posts', CommunityPostViewSet, basename='communitypost')

urlpatterns = [
    path('', include(router.urls)),
    path('inventory/notifications/', NotificationView.as_view(), name='notifications'),
    path('inventory/scan/', BarcodeScanView.as_view(), name='barcode-scan'),
    path('inventory/recipes/used/', RecipeUsageView.as_view(), name='recipe-usage'),
    path('inventory/analytics/spending/', AnalyticsView.as_view(), name='analytics-spending'),
    path('inventory/analytics/usage/', UsageAnalyticsView.as_view(), name='analytics-usage'),
    # User preferences and history endpoints:
    path('inventory/users/<int:user_id>/preferences/', UserPreferenceViewSet.as_view({'get': 'retrieve_preferences'}), name='user-preferences'),
    path('inventory/users/<int:user_id>/history/', UserPreferenceViewSet.as_view({'get': 'list_history'}), name='user-history'),
    # New health-check endpoint:
    path('inventory/health-check/', HealthCheckView.as_view(), name='health-check'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', UserDetailView.as_view(), name='user-detail'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('items/<int:item_id>/check-expiration/', check_expiration, name='check-expiration'),
    path('create/', CreateRecipeView.as_view(), name='create-recipe'),
    path('recipes/', RecipeListCreateView.as_view(), name='recipe-list'),
    path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),

]
