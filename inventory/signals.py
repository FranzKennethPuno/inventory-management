from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PantryItem, PantryItemHistory

# Track when an item is added or updated
@receiver(post_save, sender=PantryItem)
def track_item_added_or_updated(sender, instance, created, **kwargs):
    action = 'added' if created else 'updated'
    quantity_changed = instance.quantity  # Track changes in quantity
    PantryItemHistory.objects.create(
        user=instance.user,
        item=instance,
        action=action,
        quantity_changed=quantity_changed,
    )

# Track when an item is removed
@receiver(post_delete, sender=PantryItem)
def track_item_removed(sender, instance, **kwargs):
    """Fix: Set item to None to prevent foreign key constraint failure."""
    PantryItemHistory.objects.create(
        user=instance.user,
        item=None,  # The item no longer exists, so set it to None
        action='removed',
        quantity_changed=-instance.quantity,  # Negative because it's removed
    )
