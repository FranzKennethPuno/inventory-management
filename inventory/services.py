from inventory.models import PantryItem
from django.utils.timezone import now
from datetime import timedelta


def filter_inventory_items(name=None, category=None, min_stock=None, max_stock=None, expiring_soon=None):
    """
    Filter pantry items based on various criteria.

    Parameters:
    - name: Search pantry items by name (partial match).
    - category: Filter by category (exact match).
    - min_stock: Minimum stock threshold.
    - max_stock: Maximum stock threshold.
    - expiring_soon: Number of days before expiration (e.g., 7 for items expiring in the next 7 days).

    Returns:
    - A queryset of filtered pantry items.
    """
    queryset = PantryItem.objects.all()

    if name:
        queryset = queryset.filter(name__icontains=name)  # Partial match for name
    if category:
        queryset = queryset.filter(category=category)
    if min_stock is not None:
        queryset = queryset.filter(quantity__gte=min_stock)
    if max_stock is not None:
        queryset = queryset.filter(quantity__lte=max_stock)
    if expiring_soon is not None:
        expiry_threshold = now().date() + timedelta(days=expiring_soon)
        queryset = queryset.filter(expiration_date__lte=expiry_threshold)

    return queryset

def get_expiring_items():
    """Retrieve items that will expire within 3 days."""
    three_days_from_now = now().date() + timedelta(days=3)
    return PantryItem.objects.filter(expiration_date__lte=three_days_from_now)

def get_recently_added_items(limit=10):
    """Retrieve the most recently added pantry items."""
    return PantryItem.objects.order_by('-created_at')[:limit]